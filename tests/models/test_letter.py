import pytest
from app.models.letter import (
    Penerima,
    Penandatangan,
    LetterData,
    GenerateLetterRequest
)


def test_penerima_model():
    """Test Penerima model with all fields."""
    penerima = Penerima(nama="Budi Santoso", jabatan="Manager IT")
    assert penerima.nama == "Budi Santoso"
    assert penerima.jabatan == "Manager IT"


def test_penerima_jabatan_optional():
    """Test Penerima model with optional jabatan field."""
    penerima = Penerima(nama="Budi Santoso")
    assert penerima.jabatan == ""


def test_penandatangan_model():
    """Test Penandatangan model with all fields."""
    ttd = Penandatangan(nama="Ahmad Direktur", jabatan="Direktur Utama")
    assert ttd.nama == "Ahmad Direktur"
    assert ttd.jabatan == "Direktur Utama"


def test_letter_data_model():
    """Test LetterData model with nested models."""
    data = LetterData(
        nomor="123/IT/X/2025",
        tanggal="12 Januari 2025",
        perihal="Undangan Rapat",
        penerima={"nama": "Budi", "jabatan": "Manager"},
        isi="Isi surat...",
        penandatangan={"nama": "Direktur", "jabatan": "Direktur Utama"}
    )
    assert data.nomor == "123/IT/X/2025"
    assert data.penerima.nama == "Budi"


def test_generate_letter_request_valid_type():
    """Test GenerateLetterRequest with valid letter type."""
    request = GenerateLetterRequest(
        type="surat_dinas",
        data={
            "nomor": "001",
            "tanggal": "12 Januari 2025",
            "perihal": "Test",
            "penerima": {"nama": "Test"},
            "isi": "Test",
            "penandatangan": {"nama": "Test", "jabatan": "Test"}
        }
    )
    assert request.type == "surat_dinas"


def test_generate_letter_request_invalid_type():
    """Test GenerateLetterRequest with invalid letter type."""
    with pytest.raises(ValueError):
        GenerateLetterRequest(
            type="invalid_type",
            data={
                "nomor": "001",
                "tanggal": "12 Januari 2025",
                "perihal": "Test",
                "penerima": {"nama": "Test"},
                "isi": "Test",
                "penandatangan": {"nama": "Test", "jabatan": "Test"}
            }
        )
