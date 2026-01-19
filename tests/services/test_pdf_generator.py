"""Tests for PDF generator service."""

import os
import pytest
from pathlib import Path
from app.services.pdf_generator import PDFGenerator
from app.schemas.letter import LetterRequest, SchoolInfo, Person


@pytest.fixture
def pdf_generator(tmp_path):
    """Create PDFGenerator with temporary output directory."""
    generator = PDFGenerator(output_dir=str(tmp_path))
    return generator


@pytest.fixture
def sample_letter_request():
    """Create a sample letter request."""
    return LetterRequest(
        template_type="surat_tugas",
        nomor_surat="800/123/SMK.2/2024",
        tanggal_surat="1 Juli 2024",
        perihal="SURAT TUGAS",
        tempat_surat="Singosari",
        school_info=SchoolInfo(
            nama_sekolah="SMK NEGERI 2 SINGOSARI",
            alamat_jalan="Jalan Perusahaan No. 20",
            kelurahan="Tunjungtirto",
            kecamatan="Singosari",
            kab_kota="Kab. Malang",
            provinsi="Jawa Timur",
            kode_pos="65153"
        ),
        penandatangan=Person(
            nama="SUMIJAH, S.Pd., M.Si.",
            jabatan="Kepala Sekolah",
            nip="19700210 199802 2 009"
        ),
        content={
            "assignees": [Person(nama="Guru Test")],
            "details": [{"label": "Keperluan", "value": "Test"}]
        }
    )


class TestPDFGenerator:
    def test_init_creates_output_dir(self, tmp_path):
        output_dir = tmp_path / "test_output"
        generator = PDFGenerator(output_dir=str(output_dir))
        assert output_dir.exists()

    def test_init_with_existing_output_dir(self, pdf_generator):
        assert pdf_generator.output_dir.exists()

    def test_generate_creates_pdf_file(self, pdf_generator, sample_letter_request):
        file_path = pdf_generator.generate(sample_letter_request)
        assert Path(file_path).exists()
        assert file_path.endswith(".pdf")

    def test_generate_with_custom_filename(self, pdf_generator, sample_letter_request):
        custom_name = "CUSTOM_TEST.pdf"
        file_path = pdf_generator.generate(sample_letter_request, custom_filename=custom_name)
        assert file_path.endswith(custom_name)

    def test_generate_custom_filename_without_extension(self, pdf_generator, sample_letter_request):
        file_path = pdf_generator.generate(sample_letter_request, custom_filename="test")
        assert file_path.endswith("test.pdf")

    def test_generate_default_filename_format(self, pdf_generator, sample_letter_request):
        file_path = pdf_generator.generate(sample_letter_request)
        filename = Path(file_path).name
        assert "surat_tugas" in filename
        assert ".pdf" in filename

    def test_generate_invalid_template_raises_error(self, pdf_generator, sample_letter_request):
        sample_letter_request.template_type = "nonexistent_template"
        with pytest.raises(ValueError, match="Template.*not found"):
            pdf_generator.generate(sample_letter_request)

    def test_generate_bytes(self, pdf_generator, sample_letter_request):
        pdf_bytes = pdf_generator.generate_bytes(sample_letter_request)
        assert pdf_bytes is not None
        assert len(pdf_bytes.getvalue()) > 0

    def test_generate_bytes_invalid_template(self, pdf_generator, sample_letter_request):
        sample_letter_request.template_type = "invalid"
        with pytest.raises(ValueError):
            pdf_generator.generate_bytes(sample_letter_request)
