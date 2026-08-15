"""
Model database SQLAlchemy untuk sistem RAB konstruksi.
Entitas: Proyek → BOQItem → AHSPItem, dan HSP (bank data harga satuan).
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class Proyek(Base):
    """
    Metadata proyek RAB. Setiap file Excel yang diupload menjadi 1 proyek.
    """
    __tablename__ = "proyek"

    id = Column(Integer, primary_key=True, index=True)
    nama_proyek = Column(String(500), nullable=False)
    lokasi = Column(String(255), nullable=False)      # Kabupaten/Kota/Provinsi
    tahun = Column(Integer, nullable=False)
    tanggal_upload = Column(DateTime, default=datetime.utcnow)
    deskripsi = Column(Text, nullable=True)
    nama_file_asli = Column(String(500), nullable=True)  # Nama file Excel asli
    ppn_persen = Column(Float, default=11.0)              # PPN dalam persen
    total_sebelum_ppn = Column(Float, default=0.0)
    total_ppn = Column(Float, default=0.0)
    total_dengan_ppn = Column(Float, default=0.0)
    is_generated = Column(Boolean, default=False)         # True jika dibuat dari fitur Generate

    boq_items = relationship(
        "BOQItem",
        back_populates="proyek",
        cascade="all, delete-orphan",
        order_by="BOQItem.id",
    )


class BOQItem(Base):
    """
    Item pekerjaan dalam Bill of Quantity (BOQ).
    Bisa berupa baris data atau baris divisi/header kelompok.
    """
    __tablename__ = "boq_items"

    id = Column(Integer, primary_key=True, index=True)
    proyek_id = Column(Integer, ForeignKey("proyek.id", ondelete="CASCADE"), nullable=False)
    nomor_urut = Column(String(50), nullable=True)         # "I", "1", "A.1", dst.
    divisi = Column(String(500), nullable=True)            # Nama kelompok/divisi pekerjaan
    is_divisi = Column(Boolean, default=False)             # True jika baris ini adalah header divisi
    uraian_pekerjaan = Column(String(1000), nullable=False)
    satuan = Column(String(100), nullable=True)
    volume = Column(Float, nullable=True, default=0.0)
    harga_satuan = Column(Float, nullable=True, default=0.0)
    jumlah = Column(Float, nullable=True, default=0.0)     # volume × harga_satuan

    proyek = relationship("Proyek", back_populates="boq_items")
    ahsp_items = relationship(
        "AHSPItem",
        back_populates="boq_item",
        cascade="all, delete-orphan",
    )


class AHSPItem(Base):
    """
    Rincian Analisa Harga Satuan Pekerjaan (AHSP).
    Komponen upah, bahan, dan alat untuk setiap item BOQ.
    """
    __tablename__ = "ahsp_items"

    id = Column(Integer, primary_key=True, index=True)
    boq_item_id = Column(Integer, ForeignKey("boq_items.id", ondelete="CASCADE"), nullable=False)
    komponen = Column(String(50), nullable=False)   # "UPAH", "BAHAN", "ALAT"
    uraian = Column(String(500), nullable=False)
    satuan = Column(String(100), nullable=True)
    koefisien = Column(Float, nullable=True, default=0.0)
    harga_satuan = Column(Float, nullable=True, default=0.0)
    jumlah = Column(Float, nullable=True, default=0.0)   # koefisien × harga_satuan

    boq_item = relationship("BOQItem", back_populates="ahsp_items")


class HSP(Base):
    """
    Bank Data Harga Satuan Pekerjaan (HSP).
    Dibuat otomatis saat RAB di-upload, digunakan untuk Generate RAB baru.
    Menyimpan harga satuan per jenis pekerjaan, lokasi, dan tahun.
    """
    __tablename__ = "hsp"

    id = Column(Integer, primary_key=True, index=True)
    proyek_id = Column(Integer, ForeignKey("proyek.id", ondelete="CASCADE"), nullable=False)
    boq_item_id = Column(Integer, ForeignKey("boq_items.id", ondelete="CASCADE"), nullable=True)
    lokasi = Column(String(255), nullable=False)
    tahun = Column(Integer, nullable=False)
    uraian_pekerjaan = Column(String(1000), nullable=False)
    satuan = Column(String(100), nullable=True)
    harga_satuan = Column(Float, nullable=False, default=0.0)
    divisi = Column(String(500), nullable=True)

    proyek = relationship("Proyek")
