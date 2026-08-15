"""
Pydantic schemas untuk validasi data request/response FastAPI.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator


# ─── Proyek ───────────────────────────────────────────────────────────────────

class ProyekBase(BaseModel):
    nama_proyek: str = Field(..., min_length=1, max_length=500)
    lokasi: str = Field(..., min_length=1, max_length=255)
    tahun: int = Field(..., ge=2000, le=2100)
    deskripsi: Optional[str] = None
    ppn_persen: float = Field(default=11.0, ge=0, le=100)


class ProyekCreate(ProyekBase):
    pass


class ProyekUpdate(BaseModel):
    nama_proyek: Optional[str] = None
    lokasi: Optional[str] = None
    tahun: Optional[int] = None
    deskripsi: Optional[str] = None
    ppn_persen: Optional[float] = None


class ProyekResponse(ProyekBase):
    id: int
    tanggal_upload: datetime
    nama_file_asli: Optional[str] = None
    total_sebelum_ppn: float = 0.0
    total_ppn: float = 0.0
    total_dengan_ppn: float = 0.0
    is_generated: bool = False
    jumlah_item: Optional[int] = None

    class Config:
        from_attributes = True


# ─── BOQ Item ─────────────────────────────────────────────────────────────────

class BOQItemBase(BaseModel):
    nomor_urut: Optional[str] = None
    divisi: Optional[str] = None
    is_divisi: bool = False
    uraian_pekerjaan: str
    satuan: Optional[str] = None
    volume: Optional[float] = None
    harga_satuan: Optional[float] = None
    jumlah: Optional[float] = None


class BOQItemCreate(BOQItemBase):
    proyek_id: int


class BOQItemResponse(BOQItemBase):
    id: int
    proyek_id: int

    class Config:
        from_attributes = True


# ─── AHSP Item ────────────────────────────────────────────────────────────────

class AHSPItemBase(BaseModel):
    komponen: str  # UPAH / BAHAN / ALAT
    uraian: str
    satuan: Optional[str] = None
    koefisien: Optional[float] = None
    harga_satuan: Optional[float] = None
    jumlah: Optional[float] = None


class AHSPItemCreate(AHSPItemBase):
    boq_item_id: int


class AHSPItemResponse(AHSPItemBase):
    id: int
    boq_item_id: int

    class Config:
        from_attributes = True


# ─── HSP ──────────────────────────────────────────────────────────────────────

class HSPResponse(BaseModel):
    id: int
    proyek_id: int
    boq_item_id: Optional[int] = None
    lokasi: str
    tahun: int
    uraian_pekerjaan: str
    satuan: Optional[str] = None
    harga_satuan: float
    divisi: Optional[str] = None

    class Config:
        from_attributes = True


# ─── Upload & Preview ─────────────────────────────────────────────────────────

class PreviewItem(BaseModel):
    """Item BOQ hasil parsing Excel untuk preview sebelum disimpan."""
    nomor_urut: Optional[str] = None
    divisi: Optional[str] = None
    is_divisi: bool = False
    uraian_pekerjaan: str
    satuan: Optional[str] = None
    volume: Optional[float] = None
    harga_satuan: Optional[float] = None
    jumlah: Optional[float] = None
    peringatan: Optional[str] = None  # Pesan jika ada data mencurigakan


class UploadPreviewResponse(BaseModel):
    """Response preview setelah Excel diparsing."""
    nama_file: str
    total_baris: int
    total_item_valid: int
    total_divisi: int
    items: List[PreviewItem]
    metadata_terdeteksi: dict  # nama_proyek, lokasi, tahun jika ditemukan di Excel
    pesan: str


class KonfirmasiUpload(BaseModel):
    """Request konfirmasi untuk menyimpan hasil parsing ke database."""
    nama_proyek: str
    lokasi: str
    tahun: int
    deskripsi: Optional[str] = None
    ppn_persen: float = 11.0
    items: List[PreviewItem]
    nama_file: Optional[str] = None


# ─── Generate RAB ─────────────────────────────────────────────────────────────

class ItemGenerateRAB(BaseModel):
    """Satu item pekerjaan untuk Generate RAB baru."""
    uraian_pekerjaan: str
    satuan: str
    volume: float = Field(..., gt=0)
    harga_satuan: float = Field(..., ge=0)
    divisi: Optional[str] = None
    nomor_urut: Optional[str] = None


class GenerateRABRequest(BaseModel):
    """Request untuk membuat RAB baru dari bank data."""
    nama_proyek: str = Field(..., min_length=1)
    lokasi: str = Field(..., min_length=1)
    tahun: int = Field(..., ge=2000, le=2100)
    deskripsi: Optional[str] = None
    ppn_persen: float = Field(default=11.0, ge=0, le=100)
    items: List[ItemGenerateRAB]
    simpan_ke_database: bool = True


class GenerateRABResponse(BaseModel):
    """Response setelah RAB baru dibuat."""
    proyek_id: Optional[int] = None
    nama_proyek: str
    lokasi: str
    tahun: int
    items: List[dict]
    subtotal: float
    ppn_persen: float
    ppn_nominal: float
    total: float
    pesan: str


# ─── Pencarian ────────────────────────────────────────────────────────────────

class CariHSPRequest(BaseModel):
    """Filter untuk mencari harga satuan di bank data."""
    kata_kunci: Optional[str] = None
    lokasi: Optional[str] = None
    tahun_dari: Optional[int] = None
    tahun_sampai: Optional[int] = None
    divisi: Optional[str] = None
    limit: int = Field(default=50, ge=1, le=500)


class RiwayatHargaResponse(BaseModel):
    """Riwayat harga satuan suatu item antar tahun & lokasi."""
    uraian_pekerjaan: str
    satuan: Optional[str]
    riwayat: List[dict]  # [{tahun, lokasi, harga_satuan, nama_proyek}]
