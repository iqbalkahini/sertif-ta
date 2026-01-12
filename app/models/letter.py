from pydantic import BaseModel
from typing import Literal


class Penerima(BaseModel):
    """Model for letter recipient (penerima surat)."""
    nama: str
    jabatan: str = ""


class Penandatangan(BaseModel):
    """Model for letter signatory (penandatangan surat)."""
    nama: str
    jabatan: str


class LetterData(BaseModel):
    """Core data model for letter content."""
    nomor: str
    tanggal: str
    perihal: str
    penerima: Penerima
    isi: str
    penandatangan: Penandatangan


class GenerateLetterRequest(BaseModel):
    """Request model for letter generation with type validation."""
    type: Literal["surat_dinas", "surat_edaran", "surat_pemberitahuan"]
    data: LetterData


class GenerateLetterResponse(BaseModel):
    """Response model for letter generation results."""
    success: bool
    message: str
    data: dict | None = None
