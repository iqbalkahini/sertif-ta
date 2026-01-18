from typing import List, Optional, Dict, Any, Union, Annotated
from pydantic import BaseModel, Field

class SchoolInfo(BaseModel):
    nama_sekolah: str = Field(..., description="Nama lengkap sekolah", examples=["SMK NEGERI 2 SINGOSARI"])
    alamat_jalan: str = Field(..., description="Alamat jalan sekolah", examples=["Jalan Perusahaan No. 20"])
    kelurahan: str | None = Field(None, description="Kelurahan/Desa", examples=["Tunjungtirto"])
    kecamatan: str | None = Field(None, description="Kecamatan", examples=["Singosari"])
    kab_kota: str = Field(..., description="Kabupaten/Kota", examples=["Kab. Malang"])
    provinsi: str = Field(..., description="Provinsi", examples=["Jawa Timur"])
    kode_pos: str | None = Field(None, description="Kode pos", examples=["65153"])
    telepon: str | None = Field(None, description="Nomor telepon", examples=["(0341) 4345127"])
    email: str | None = Field(None, description="Alamat email", examples=["smkn2singosari@yahoo.co.id"])
    website: str | None = Field(None, description="Website sekolah", examples=["www.smkn2singosari.sch.id"])
    logo_url: str | None = Field(None, description="URL logo sekolah")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "nama_sekolah": "SMK NEGERI 2 SINGOSARI",
                    "alamat_jalan": "Jalan Perusahaan No. 20",
                    "kelurahan": "Tunjungtirto",
                    "kecamatan": "Singosari",
                    "kab_kota": "Kab. Malang",
                    "provinsi": "Jawa Timur",
                    "kode_pos": "65153",
                    "telepon": "(0341) 4345127",
                    "email": "smkn2singosari@yahoo.co.id",
                    "website": "www.smkn2singosari.sch.id"
                }
            ]
        }
    }

class Person(BaseModel):
    nama: str = Field(..., description="Nama lengkap", examples=["SUMIJAH, S.Pd., M.Si."])
    jabatan: str | None = Field(None, description="Jabatan/posisi", examples=["Kepala SMK Negeri 2 Singosari"])
    nip: str | None = Field(None, description="Nomor Induk Pegawai", examples=["19700210 199802 2 009"])
    pangkat: str | None = Field(None, description="Pangkat/golongan", examples=["Pembina Tk. I"])
    instansi: str | None = Field(None, description="Instansi/lembaga", examples=["SMK Negeri 2 Singosari"])

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "nama": "SUMIJAH, S.Pd., M.Si.",
                    "jabatan": "Kepala SMK Negeri 2 Singosari",
                    "nip": "19700210 199802 2 009",
                    "pangkat": "Pembina Tk. I",
                    "instansi": "SMK Negeri 2 Singosari"
                },
                {
                    "nama": "Inasni Dyah Rahmatika, S.Pd.",
                    "jabatan": "Guru",
                    "nip": "19850101 201001 2 005",
                    "instansi": "SMK Negeri 2 Singosari"
                },
                {
                    "nama": "Budi Santoso, S.Kom.",
                    "jabatan": "Guru Kejuruan",
                    "instansi": "SMK Negeri 2 Singosari"
                }
            ]
        }
    }

class KeyValueItem(BaseModel):
    label: str = Field(..., description="Label/key", examples=["Keperluan"])
    value: str = Field(..., description="Nilai/value", examples=["Pengantaran Siswa Praktik Kerja Lapangan (PKL)"])
    separator: str = Field(":", description="Pemisah antara label dan value", examples=[":"])

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"label": "Keperluan", "value": "Pengantaran Siswa Praktik Kerja Lapangan (PKL)", "separator": ":"},
                {"label": "Hari / Tanggal", "value": "Senin, 1 Juli 2024", "separator": ":"},
                {"label": "Waktu", "value": "08.00 – Selesai", "separator": ":"},
                {"label": "Tempat", "value": "BACAMALANG.COM", "separator": ":"},
                {"label": "Alamat", "value": "JL. MOROJANTEK NO. 87 B, PANGENTAN, KEC. SINGOSARI, KAB. MALANG", "separator": ":"}
            ]
        }
    }

# --- Specific Request Models ---

class SuratTugasRequest(BaseModel):
    """Strictly typed request for Surat Tugas generation."""
    nomor_surat: str
    tanggal_surat: str
    tempat_surat: str | None = None
    perihal: str = "SURAT TUGAS"

    school_info: SchoolInfo
    penandatangan: Person

    # Content specific to Surat Tugas
    assignees: List[Person]
    details: List[KeyValueItem]

    pembuka: str | None = None
    penutup: str | None = None

    model_config = {"json_schema_extra": {"examples": [{"nomor_surat": "800/123/SMK.2/2024", "tanggal_surat": "1 Juli 2024", "tempat_surat": "Singosari"}]}}

class LembarPersetujuanRequest(BaseModel):
    """Request schema for Lembar Persetujuan PKL."""
    school_info: SchoolInfo

    # Siswa details
    students: Annotated[List[Person], Field(min_length=1)]

    # DU/DI Info
    nama_perusahaan: str

    # Signature placeholder
    tempat_tanggal: str | None = None

    model_config = {"json_schema_extra": {"examples": [{"nama_perusahaan": "JTV MALANG", "tempat_tanggal": "Malang, 12 Januari 2026"}]}}


# --- Generic/Legacy Request Models ---

class LetterRequest(BaseModel):
    """Top level request to generate a letter (Generic)."""
    template_type: str = Field(..., description="Template name (e.g. surat_tugas)")
    nomor_surat: str
    perihal: str = "SURAT TUGAS"
    tanggal_surat: str
    tempat_surat: str | None = None

    school_info: SchoolInfo
    penandatangan: Person

    # Flexible content
    content: Dict[str, Any]

class PDFResponse(BaseModel):
    filename: str
    file_url: str
    file_size: int
    
