import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app
from app.api.v1.letters import pdf_storage


client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_pdf_storage():
    """Clear PDF storage before and after each test."""
    pdf_storage.clear()
    yield
    pdf_storage.clear()


def test_list_templates():
    """Test GET /api/v1/letters/templates - list available templates."""
    response = client.get("/api/v1/letters/templates")

    assert response.status_code == 200
    data = response.json()
    assert "templates" in data
    assert "count" in data
    assert data["count"] == 3
    assert "surat_dinas" in data["templates"]
    assert "surat_edaran" in data["templates"]
    assert "surat_pemberitahuan" in data["templates"]


def test_generate_letter_success():
    """Test POST /api/v1/letters/generate - successful PDF generation."""
    request_data = {
        "type": "surat_dinas",
        "data": {
            "nomor": "001/TEST/2024",
            "tanggal": "12 Januari 2024",
            "perihal": "Test Surat",
            "penerima": {
                "nama": "Budi Santoso",
                "jabatan": "Manager"
            },
            "isi": "Ini adalah isi surat untuk keperluan testing.",
            "penandatangan": {
                "nama": "Ahmad Direktur",
                "jabatan": "Direktur"
            }
        }
    }

    response = client.post("/api/v1/letters/generate", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "doc_id" in data["data"]
    assert "download_url" in data["data"]
    assert "filename" in data["data"]
    assert data["data"]["download_url"].startswith("/api/v1/letters/download/")


def test_generate_letter_invalid_template():
    """Test POST /api/v1/letters/generate - invalid template type returns 400."""
    request_data = {
        "type": "invalid_template",
        "data": {
            "nomor": "001/TEST/2024",
            "tanggal": "12 Januari 2024",
            "perihal": "Test Surat",
            "penerima": {
                "nama": "Budi Santoso",
                "jabatan": "Manager"
            },
            "isi": "Ini adalah isi surat untuk keperluan testing.",
            "penandatangan": {
                "nama": "Ahmad Direktur",
                "jabatan": "Direktur"
            }
        }
    }

    response = client.post("/api/v1/letters/generate", json=request_data)

    # Should fail validation at Pydantic level for invalid type
    # or at PDF generator level
    assert response.status_code in [400, 422]


def test_download_pdf_after_generation():
    """Test GET /api/v1/letters/download/{doc_id} - download generated PDF."""
    # First generate a PDF
    request_data = {
        "type": "surat_edaran",
        "data": {
            "nomor": "002/TEST/2024",
            "tanggal": "12 Januari 2024",
            "perihal": "Test Edaran",
            "penerima": {
                "nama": "Seluruh Staff",
                "jabatan": ""
            },
            "isi": "Ini adalah edaran untuk seluruh staff.",
            "penandatangan": {
                "nama": "Hrd Manager",
                "jabatan": "HRD Manager"
            }
        }
    }

    generate_response = client.post("/api/v1/letters/generate", json=request_data)
    assert generate_response.status_code == 200

    doc_id = generate_response.json()["data"]["doc_id"]

    # Now download the PDF
    download_response = client.get(f"/api/v1/letters/download/{doc_id}")

    assert download_response.status_code == 200
    assert download_response.headers["content-type"] == "application/pdf"


def test_download_pdf_invalid_id():
    """Test GET /api/v1/letters/download/{doc_id} - invalid ID returns 404."""
    fake_doc_id = "00000000-0000-0000-0000-000000000000"

    response = client.get(f"/api/v1/letters/download/{fake_doc_id}")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
