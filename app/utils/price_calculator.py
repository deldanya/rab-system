"""
Kalkulasi harga dan pencarian HSP terbaik dari bank data historis.
"""
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from app.models import HSP, Proyek
import difflib


def hitung_total_rab(items: List[Dict], ppn_persen: float = 11.0) -> Dict:
    """
    Hitung subtotal, PPN, dan total dari daftar item BOQ.
    item: {volume, harga_satuan, jumlah, is_divisi}
    """
    subtotal = 0.0
    for item in items:
        if item.get("is_divisi"):
            continue
        jumlah = item.get("jumlah")
        if jumlah is None:
            vol = item.get("volume") or 0
            harga = item.get("harga_satuan") or 0
            jumlah = vol * harga
        subtotal += jumlah or 0

    ppn_nominal = subtotal * (ppn_persen / 100)
    total = subtotal + ppn_nominal

    return {
        "subtotal": subtotal,
        "ppn_persen": ppn_persen,
        "ppn_nominal": ppn_nominal,
        "total": total,
    }


def terapkan_eskalasi(harga: float, tahun_data: int, tahun_target: int,
                      eskalasi_persen: float = 5.0) -> float:
    """
    Eskalasi harga dari tahun_data ke tahun_target.
    Eskalasi majemuk per tahun (compound escalation).
    """
    selisih_tahun = tahun_target - tahun_data
    if selisih_tahun <= 0 or eskalasi_persen <= 0:
        return harga
    faktor = (1 + eskalasi_persen / 100) ** selisih_tahun
    return harga * faktor


def _kemiripan_teks(a: str, b: str) -> float:
    """Hitung kemiripan dua string (0.0 - 1.0)."""
    a = a.lower().strip()
    b = b.lower().strip()
    return difflib.SequenceMatcher(None, a, b).ratio()


def cari_hsp_terbaik(
    db: Session,
    uraian_pekerjaan: str,
    satuan: Optional[str],
    lokasi_target: str,
    tahun_target: int,
    eskalasi_persen: float = 0.0,
) -> Optional[Dict]:
    """
    Cari Harga Satuan Pekerjaan terbaik dari bank data historis.
    Prioritas: (1) lokasi sama + tahun paling dekat, (2) lokasi mengandung kata sama,
               (3) semua lokasi + tahun paling dekat.
    Kembalikan dict HSP terpilih beserta info sumbernya.
    """
    # Query semua HSP dengan uraian mirip
    kata_kunci = uraian_pekerjaan.lower().split()[:3]  # Ambil 3 kata pertama

    query = db.query(HSP, Proyek.nama_proyek).join(
        Proyek, HSP.proyek_id == Proyek.id
    ).filter(
        HSP.tahun <= tahun_target  # Hanya data historis atau tahun sama
    )

    # Filter kata kunci di uraian (cari yang mengandung minimal 1 kata kunci)
    if kata_kunci:
        kondisi = [func.lower(HSP.uraian_pekerjaan).contains(kw) for kw in kata_kunci]
        query = query.filter(or_(*kondisi))

    kandidat = query.all()

    if not kandidat:
        # Coba tanpa filter tahun jika tidak ada data
        query_alt = db.query(HSP, Proyek.nama_proyek).join(
            Proyek, HSP.proyek_id == Proyek.id
        )
        if kata_kunci:
            kondisi = [func.lower(HSP.uraian_pekerjaan).contains(kw) for kw in kata_kunci]
            query_alt = query_alt.filter(or_(*kondisi))
        kandidat = query_alt.all()

    if not kandidat:
        return None

    # Skor tiap kandidat
    def hitung_skor(hsp: HSP, nama_proyek: str) -> float:
        skor = 0.0

        # Kemiripan uraian (bobot tertinggi)
        kemiripan = _kemiripan_teks(uraian_pekerjaan, hsp.uraian_pekerjaan)
        skor += kemiripan * 10

        # Kesesuaian satuan
        if satuan and hsp.satuan:
            if satuan.lower().strip() == hsp.satuan.lower().strip():
                skor += 3
            elif satuan.lower()[:2] == hsp.satuan.lower()[:2]:
                skor += 1

        # Lokasi
        lokasi_t = lokasi_target.lower()
        lokasi_h = hsp.lokasi.lower()
        if lokasi_t == lokasi_h:
            skor += 5  # Exact match
        elif any(kata in lokasi_h for kata in lokasi_t.split()):
            skor += 2  # Partial match
        elif any(kata in lokasi_t for kata in lokasi_h.split()):
            skor += 1

        # Kedekatan tahun (lebih dekat = lebih baik)
        selisih = abs(tahun_target - hsp.tahun)
        skor += max(0, 5 - selisih)

        return skor

    # Sort by skor
    kandidat_dengan_skor = [
        (hsp, nama_proyek, hitung_skor(hsp, nama_proyek))
        for hsp, nama_proyek in kandidat
    ]
    kandidat_dengan_skor.sort(key=lambda x: x[2], reverse=True)

    terbaik_hsp, terbaik_nama_proyek, skor_terbaik = kandidat_dengan_skor[0]

    if skor_terbaik < 3:
        return None  # Terlalu tidak mirip

    harga_asli = terbaik_hsp.harga_satuan
    harga_eskalasi = terapkan_eskalasi(harga_asli, terbaik_hsp.tahun, tahun_target, eskalasi_persen)

    return {
        "hsp_id": terbaik_hsp.id,
        "lokasi_sumber": terbaik_hsp.lokasi,
        "tahun_sumber": terbaik_hsp.tahun,
        "nama_proyek_sumber": terbaik_nama_proyek,
        "uraian_sumber": terbaik_hsp.uraian_pekerjaan,
        "satuan_sumber": terbaik_hsp.satuan,
        "harga_asli": harga_asli,
        "harga_setelah_eskalasi": harga_eskalasi,
        "eskalasi_persen": eskalasi_persen,
        "selisih_tahun": tahun_target - terbaik_hsp.tahun,
        "skor_kemiripan": round(skor_terbaik, 2),
    }


def indeks_hsp_dari_proyek(db: Session, proyek_id: int) -> int:
    """
    Setelah upload RAB, buat/update entri HSP dari BOQ items proyek.
    Kembalikan jumlah HSP yang dibuat.
    """
    from app.models import BOQItem, HSP, Proyek

    proyek = db.query(Proyek).filter(Proyek.id == proyek_id).first()
    if not proyek:
        return 0

    # Hapus HSP lama dari proyek ini dulu
    db.query(HSP).filter(HSP.proyek_id == proyek_id).delete()

    items = db.query(BOQItem).filter(
        BOQItem.proyek_id == proyek_id,
        BOQItem.is_divisi == False,
        BOQItem.harga_satuan > 0,
        BOQItem.uraian_pekerjaan != None,
    ).all()

    jumlah_dibuat = 0
    for item in items:
        hsp = HSP(
            proyek_id=proyek_id,
            boq_item_id=item.id,
            lokasi=proyek.lokasi,
            tahun=proyek.tahun,
            uraian_pekerjaan=item.uraian_pekerjaan,
            satuan=item.satuan,
            harga_satuan=item.harga_satuan,
            divisi=item.divisi,
        )
        db.add(hsp)
        jumlah_dibuat += 1

    db.commit()
    return jumlah_dibuat
