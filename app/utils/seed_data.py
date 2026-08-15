"""
Data dummy untuk pengujian awal aplikasi.
Berisi 3 proyek RAB dari tahun 2022-2024 di lokasi berbeda.
"""
from datetime import datetime
from typing import Dict
from sqlalchemy.orm import Session
from app.models import Proyek, BOQItem, HSP
from app.utils.price_calculator import indeks_hsp_dari_proyek


DATA_DUMMY = [
    {
        "proyek": {
            "nama_proyek": "Pembangunan Gedung Kantor Desa Sukamaju",
            "lokasi": "Kabupaten Bogor, Jawa Barat",
            "tahun": 2022,
            "deskripsi": "Pembangunan gedung kantor desa 2 lantai, luas 200 m2",
            "ppn_persen": 11.0,
        },
        "items": [
            {"is_divisi": True, "uraian_pekerjaan": "I. PEKERJAAN PERSIAPAN", "nomor_urut": "I"},
            {"uraian_pekerjaan": "Pembersihan dan Perataan Lahan", "satuan": "m2", "volume": 250.0, "harga_satuan": 4500.0, "nomor_urut": "1", "divisi": "I. PEKERJAAN PERSIAPAN"},
            {"uraian_pekerjaan": "Pengukuran dan Pemasangan Bouwplank", "satuan": "m1", "volume": 60.0, "harga_satuan": 12000.0, "nomor_urut": "2", "divisi": "I. PEKERJAAN PERSIAPAN"},
            {"uraian_pekerjaan": "Pembuatan Direksi Keet dan Gudang Material", "satuan": "unit", "volume": 1.0, "harga_satuan": 4500000.0, "nomor_urut": "3", "divisi": "I. PEKERJAAN PERSIAPAN"},
            {"is_divisi": True, "uraian_pekerjaan": "II. PEKERJAAN TANAH", "nomor_urut": "II"},
            {"uraian_pekerjaan": "Galian Tanah untuk Pondasi", "satuan": "m3", "volume": 120.0, "harga_satuan": 42000.0, "nomor_urut": "4", "divisi": "II. PEKERJAAN TANAH"},
            {"uraian_pekerjaan": "Urugan Kembali Tanah Bekas Galian", "satuan": "m3", "volume": 60.0, "harga_satuan": 22000.0, "nomor_urut": "5", "divisi": "II. PEKERJAAN TANAH"},
            {"uraian_pekerjaan": "Urugan Pasir Bawah Pondasi", "satuan": "m3", "volume": 15.0, "harga_satuan": 180000.0, "nomor_urut": "6", "divisi": "II. PEKERJAAN TANAH"},
            {"is_divisi": True, "uraian_pekerjaan": "III. PEKERJAAN PONDASI", "nomor_urut": "III"},
            {"uraian_pekerjaan": "Pondasi Batu Kali Campuran 1:4", "satuan": "m3", "volume": 85.0, "harga_satuan": 820000.0, "nomor_urut": "7", "divisi": "III. PEKERJAAN PONDASI"},
            {"uraian_pekerjaan": "Sloof Beton Bertulang 15/20 K-175", "satuan": "m3", "volume": 10.5, "harga_satuan": 2400000.0, "nomor_urut": "8", "divisi": "III. PEKERJAAN PONDASI"},
            {"is_divisi": True, "uraian_pekerjaan": "IV. PEKERJAAN BETON", "nomor_urut": "IV"},
            {"uraian_pekerjaan": "Kolom Beton Bertulang 30/30 K-225", "satuan": "m3", "volume": 18.0, "harga_satuan": 3200000.0, "nomor_urut": "9", "divisi": "IV. PEKERJAAN BETON"},
            {"uraian_pekerjaan": "Balok Beton Bertulang 20/40 K-225", "satuan": "m3", "volume": 12.0, "harga_satuan": 3100000.0, "nomor_urut": "10", "divisi": "IV. PEKERJAAN BETON"},
            {"uraian_pekerjaan": "Pelat Lantai Beton Bertulang t=12cm K-225", "satuan": "m3", "volume": 24.0, "harga_satuan": 2800000.0, "nomor_urut": "11", "divisi": "IV. PEKERJAAN BETON"},
            {"is_divisi": True, "uraian_pekerjaan": "V. PEKERJAAN DINDING", "nomor_urut": "V"},
            {"uraian_pekerjaan": "Pasangan Bata Merah 1:4", "satuan": "m2", "volume": 350.0, "harga_satuan": 85000.0, "nomor_urut": "12", "divisi": "V. PEKERJAAN DINDING"},
            {"uraian_pekerjaan": "Plesteran Dinding Campuran 1:4", "satuan": "m2", "volume": 700.0, "harga_satuan": 35000.0, "nomor_urut": "13", "divisi": "V. PEKERJAAN DINDING"},
            {"uraian_pekerjaan": "Acian Dinding", "satuan": "m2", "volume": 700.0, "harga_satuan": 22000.0, "nomor_urut": "14", "divisi": "V. PEKERJAAN DINDING"},
            {"is_divisi": True, "uraian_pekerjaan": "VI. PEKERJAAN ATAP", "nomor_urut": "VI"},
            {"uraian_pekerjaan": "Rangka Atap Baja Ringan", "satuan": "m2", "volume": 120.0, "harga_satuan": 165000.0, "nomor_urut": "15", "divisi": "VI. PEKERJAAN ATAP"},
            {"uraian_pekerjaan": "Penutup Atap Genteng Metal Pasir", "satuan": "m2", "volume": 130.0, "harga_satuan": 85000.0, "nomor_urut": "16", "divisi": "VI. PEKERJAAN ATAP"},
            {"is_divisi": True, "uraian_pekerjaan": "VII. PEKERJAAN FINISHING", "nomor_urut": "VII"},
            {"uraian_pekerjaan": "Pengecatan Dinding Eksterior", "satuan": "m2", "volume": 350.0, "harga_satuan": 28000.0, "nomor_urut": "17", "divisi": "VII. PEKERJAAN FINISHING"},
            {"uraian_pekerjaan": "Pengecatan Dinding Interior", "satuan": "m2", "volume": 350.0, "harga_satuan": 22000.0, "nomor_urut": "18", "divisi": "VII. PEKERJAAN FINISHING"},
            {"uraian_pekerjaan": "Pemasangan Keramik Lantai 40x40", "satuan": "m2", "volume": 200.0, "harga_satuan": 125000.0, "nomor_urut": "19", "divisi": "VII. PEKERJAAN FINISHING"},
            {"uraian_pekerjaan": "Kusen Pintu dan Jendela Aluminium", "satuan": "unit", "volume": 8.0, "harga_satuan": 1500000.0, "nomor_urut": "20", "divisi": "VII. PEKERJAAN FINISHING"},
        ],
    },
    {
        "proyek": {
            "nama_proyek": "Rehabilitasi Jalan Desa RT.03 Kelurahan Merdeka",
            "lokasi": "Kota Bandung, Jawa Barat",
            "tahun": 2023,
            "deskripsi": "Rehabilitasi jalan beton panjang 500m lebar 3m",
            "ppn_persen": 11.0,
        },
        "items": [
            {"is_divisi": True, "uraian_pekerjaan": "I. PEKERJAAN PERSIAPAN", "nomor_urut": "I"},
            {"uraian_pekerjaan": "Pembersihan dan Perataan Lahan", "satuan": "m2", "volume": 1800.0, "harga_satuan": 3500.0, "nomor_urut": "1", "divisi": "I. PEKERJAAN PERSIAPAN"},
            {"uraian_pekerjaan": "Pengukuran dan Pemasangan Profil Jalan", "satuan": "m1", "volume": 500.0, "harga_satuan": 8500.0, "nomor_urut": "2", "divisi": "I. PEKERJAAN PERSIAPAN"},
            {"is_divisi": True, "uraian_pekerjaan": "II. PEKERJAAN TANAH", "nomor_urut": "II"},
            {"uraian_pekerjaan": "Galian Tanah", "satuan": "m3", "volume": 270.0, "harga_satuan": 48000.0, "nomor_urut": "3", "divisi": "II. PEKERJAAN TANAH"},
            {"uraian_pekerjaan": "Pemadatan Tanah Dasar", "satuan": "m2", "volume": 1800.0, "harga_satuan": 12000.0, "nomor_urut": "4", "divisi": "II. PEKERJAAN TANAH"},
            {"is_divisi": True, "uraian_pekerjaan": "III. PEKERJAAN LAPIS PONDASI", "nomor_urut": "III"},
            {"uraian_pekerjaan": "Lapis Pondasi Agregat Kelas A (LPA)", "satuan": "m3", "volume": 270.0, "harga_satuan": 320000.0, "nomor_urut": "5", "divisi": "III. PEKERJAAN LAPIS PONDASI"},
            {"uraian_pekerjaan": "Lapis Pondasi Agregat Kelas B (LPB)", "satuan": "m3", "volume": 180.0, "harga_satuan": 280000.0, "nomor_urut": "6", "divisi": "III. PEKERJAAN LAPIS PONDASI"},
            {"is_divisi": True, "uraian_pekerjaan": "IV. PEKERJAAN PERKERASAN BETON", "nomor_urut": "IV"},
            {"uraian_pekerjaan": "Perkerasan Beton K-300 tebal 20 cm", "satuan": "m3", "volume": 300.0, "harga_satuan": 1250000.0, "nomor_urut": "7", "divisi": "IV. PEKERJAAN PERKERASAN BETON"},
            {"uraian_pekerjaan": "Besi Tulangan Wiremesh M8", "satuan": "m2", "volume": 1500.0, "harga_satuan": 65000.0, "nomor_urut": "8", "divisi": "IV. PEKERJAAN PERKERASAN BETON"},
            {"uraian_pekerjaan": "Pemasangan Bekisting Tepi Jalan", "satuan": "m1", "volume": 1000.0, "harga_satuan": 22000.0, "nomor_urut": "9", "divisi": "IV. PEKERJAAN PERKERASAN BETON"},
            {"is_divisi": True, "uraian_pekerjaan": "V. PEKERJAAN DRAINASE", "nomor_urut": "V"},
            {"uraian_pekerjaan": "Galian Saluran Drainase", "satuan": "m3", "volume": 150.0, "harga_satuan": 55000.0, "nomor_urut": "10", "divisi": "V. PEKERJAAN DRAINASE"},
            {"uraian_pekerjaan": "Pasangan Batu Kali Saluran 1:4", "satuan": "m3", "volume": 60.0, "harga_satuan": 880000.0, "nomor_urut": "11", "divisi": "V. PEKERJAAN DRAINASE"},
            {"uraian_pekerjaan": "Plesteran Saluran Drainase", "satuan": "m2", "volume": 500.0, "harga_satuan": 38000.0, "nomor_urut": "12", "divisi": "V. PEKERJAAN DRAINASE"},
        ],
    },
    {
        "proyek": {
            "nama_proyek": "Pembangunan Saluran Irigasi Tersier Blok C",
            "lokasi": "Kabupaten Karawang, Jawa Barat",
            "tahun": 2024,
            "deskripsi": "Saluran irigasi tersier panjang 800m untuk areal sawah 45 ha",
            "ppn_persen": 11.0,
        },
        "items": [
            {"is_divisi": True, "uraian_pekerjaan": "I. PEKERJAAN PERSIAPAN", "nomor_urut": "I"},
            {"uraian_pekerjaan": "Pembersihan Lahan dan Semak Belukar", "satuan": "m2", "volume": 2400.0, "harga_satuan": 3800.0, "nomor_urut": "1", "divisi": "I. PEKERJAAN PERSIAPAN"},
            {"uraian_pekerjaan": "Pengukuran dan Pemasangan Profil", "satuan": "m1", "volume": 800.0, "harga_satuan": 9000.0, "nomor_urut": "2", "divisi": "I. PEKERJAAN PERSIAPAN"},
            {"is_divisi": True, "uraian_pekerjaan": "II. PEKERJAAN TANAH", "nomor_urut": "II"},
            {"uraian_pekerjaan": "Galian Tanah Saluran", "satuan": "m3", "volume": 960.0, "harga_satuan": 45000.0, "nomor_urut": "3", "divisi": "II. PEKERJAAN TANAH"},
            {"uraian_pekerjaan": "Urugan Tanah Kembali", "satuan": "m3", "volume": 200.0, "harga_satuan": 24000.0, "nomor_urut": "4", "divisi": "II. PEKERJAAN TANAH"},
            {"is_divisi": True, "uraian_pekerjaan": "III. PEKERJAAN PASANGAN BATU", "nomor_urut": "III"},
            {"uraian_pekerjaan": "Pasangan Batu Kali Campuran 1:4", "satuan": "m3", "volume": 480.0, "harga_satuan": 850000.0, "nomor_urut": "5", "divisi": "III. PEKERJAAN PASANGAN BATU"},
            {"uraian_pekerjaan": "Plesteran Campuran 1:3", "satuan": "m2", "volume": 1600.0, "harga_satuan": 42000.0, "nomor_urut": "6", "divisi": "III. PEKERJAAN PASANGAN BATU"},
            {"uraian_pekerjaan": "Acian Halus", "satuan": "m2", "volume": 1600.0, "harga_satuan": 25000.0, "nomor_urut": "7", "divisi": "III. PEKERJAAN PASANGAN BATU"},
            {"is_divisi": True, "uraian_pekerjaan": "IV. PEKERJAAN BANGUNAN PELENGKAP", "nomor_urut": "IV"},
            {"uraian_pekerjaan": "Box Tersier Beton Pracetak", "satuan": "unit", "volume": 8.0, "harga_satuan": 3500000.0, "nomor_urut": "8", "divisi": "IV. PEKERJAAN BANGUNAN PELENGKAP"},
            {"uraian_pekerjaan": "Pintu Air Romijn Lebar 0.5m", "satuan": "unit", "volume": 4.0, "harga_satuan": 5500000.0, "nomor_urut": "9", "divisi": "IV. PEKERJAAN BANGUNAN PELENGKAP"},
            {"uraian_pekerjaan": "Jembatan Pelayanan Beton lebar 1.5m", "satuan": "unit", "volume": 6.0, "harga_satuan": 8500000.0, "nomor_urut": "10", "divisi": "IV. PEKERJAAN BANGUNAN PELENGKAP"},
        ],
    },
]


def seed_database(db: Session) -> Dict:
    """
    Isi database dengan data dummy. Hanya dijalankan jika database kosong.
    Kembalikan statistik data yang dimasukkan.
    """
    from app.models import Proyek

    # Cek apakah sudah ada data
    jumlah_proyek = db.query(Proyek).count()
    if jumlah_proyek > 0:
        return {"status": "skip", "pesan": "Database sudah memiliki data, seed dilewati."}

    total_proyek = 0
    total_item = 0

    for data in DATA_DUMMY:
        # Buat proyek
        proyek = Proyek(**data["proyek"])
        db.add(proyek)
        db.flush()  # Dapatkan ID proyek

        subtotal = 0.0
        # Buat BOQ items
        for item_data in data["items"]:
            item = BOQItem(proyek_id=proyek.id)
            item.is_divisi = item_data.get("is_divisi", False)
            item.uraian_pekerjaan = item_data["uraian_pekerjaan"]
            item.nomor_urut = item_data.get("nomor_urut")
            item.divisi = item_data.get("divisi")
            item.satuan = item_data.get("satuan")
            item.volume = item_data.get("volume")
            item.harga_satuan = item_data.get("harga_satuan")

            if not item.is_divisi and item.volume and item.harga_satuan:
                item.jumlah = item.volume * item.harga_satuan
                subtotal += item.jumlah

            db.add(item)

        # Update total proyek
        ppn = subtotal * (proyek.ppn_persen / 100)
        proyek.total_sebelum_ppn = subtotal
        proyek.total_ppn = ppn
        proyek.total_dengan_ppn = subtotal + ppn

        db.flush()
        total_proyek += 1
        total_item += len(data["items"])

    db.commit()

    # Buat indeks HSP dari semua proyek
    total_hsp = 0
    proyek_list = db.query(Proyek).all()
    for proyek in proyek_list:
        total_hsp += indeks_hsp_dari_proyek(db, proyek.id)

    return {
        "status": "ok",
        "total_proyek": total_proyek,
        "total_item": total_item,
        "total_hsp": total_hsp,
        "pesan": f"Berhasil menambahkan {total_proyek} proyek, {total_item} item BOQ, dan {total_hsp} data HSP.",
    }
