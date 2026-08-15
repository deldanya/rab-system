"""
Router untuk Generate RAB baru dari bank data historis.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Proyek, BOQItem, HSP
from app.schemas import GenerateRABRequest, GenerateRABResponse
from app.utils.price_calculator import hitung_total_rab, indeks_hsp_dari_proyek, cari_hsp_terbaik

router = APIRouter(prefix="/api/generate", tags=["Generate RAB"])


@router.post("/rab")
def generate_rab(data: GenerateRABRequest, db: Session = Depends(get_db)):
    """
    Generate RAB baru berdasarkan daftar item dan spesifikasi proyek.
    Untuk setiap item, harga_satuan sudah ditetapkan oleh user (atau dari bank data).
    Hitung total, PPN, dan grand total secara otomatis.
    """
    if not data.items:
        raise HTTPException(status_code=400, detail="Daftar item pekerjaan tidak boleh kosong.")

    # Hitung jumlah untuk tiap item
    items_hasil = []
    for item in data.items:
        jumlah = item.volume * item.harga_satuan
        items_hasil.append({
            "nomor_urut": item.nomor_urut,
            "divisi": item.divisi,
            "is_divisi": False,
            "uraian_pekerjaan": item.uraian_pekerjaan,
            "satuan": item.satuan,
            "volume": item.volume,
            "harga_satuan": item.harga_satuan,
            "jumlah": jumlah,
        })

    # Hitung total keseluruhan
    total_info = hitung_total_rab(items_hasil, data.ppn_persen)

    # Simpan ke database jika diminta
    proyek_id = None
    if data.simpan_ke_database:
        proyek = Proyek(
            nama_proyek=data.nama_proyek,
            lokasi=data.lokasi,
            tahun=data.tahun,
            deskripsi=data.deskripsi,
            ppn_persen=data.ppn_persen,
            total_sebelum_ppn=total_info["subtotal"],
            total_ppn=total_info["ppn_nominal"],
            total_dengan_ppn=total_info["total"],
            is_generated=True,
        )
        db.add(proyek)
        db.flush()
        proyek_id = proyek.id

        for item in items_hasil:
            boq = BOQItem(
                proyek_id=proyek_id,
                nomor_urut=item.get("nomor_urut"),
                divisi=item.get("divisi"),
                is_divisi=False,
                uraian_pekerjaan=item["uraian_pekerjaan"],
                satuan=item["satuan"],
                volume=item["volume"],
                harga_satuan=item["harga_satuan"],
                jumlah=item["jumlah"],
            )
            db.add(boq)

        db.commit()
        indeks_hsp_dari_proyek(db, proyek_id)

    return {
        "proyek_id": proyek_id,
        "nama_proyek": data.nama_proyek,
        "lokasi": data.lokasi,
        "tahun": data.tahun,
        "items": items_hasil,
        "subtotal": total_info["subtotal"],
        "ppn_persen": total_info["ppn_persen"],
        "ppn_nominal": total_info["ppn_nominal"],
        "total": total_info["total"],
        "pesan": (
            f"RAB '{data.nama_proyek}' berhasil digenerate. "
            + (f"Disimpan dengan ID #{proyek_id}." if proyek_id else "Tidak disimpan ke database.")
        ),
    }


@router.post("/cari-harga-otomatis")
def cari_harga_otomatis(
    request: dict,
    db: Session = Depends(get_db),
):
    """
    Cari harga satuan terbaik dari bank data untuk satu item pekerjaan.
    Input: {uraian_pekerjaan, satuan, lokasi, tahun, eskalasi_persen}
    """
    uraian = request.get("uraian_pekerjaan", "")
    satuan = request.get("satuan")
    lokasi = request.get("lokasi", "")
    tahun = request.get("tahun", 2024)
    eskalasi = request.get("eskalasi_persen", 0.0)

    if not uraian:
        raise HTTPException(status_code=400, detail="uraian_pekerjaan tidak boleh kosong.")

    hasil = cari_hsp_terbaik(db, uraian, satuan, lokasi, tahun, eskalasi)

    if not hasil:
        return {
            "ditemukan": False,
            "pesan": (
                "Tidak ditemukan harga satuan yang sesuai di bank data. "
                "Isi harga satuan secara manual."
            ),
        }

    return {"ditemukan": True, **hasil}
