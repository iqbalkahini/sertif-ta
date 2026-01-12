import os
import tempfile
from pathlib import Path

import pytest

from app.services.pdf_generator import PDFGenerator
from app.models.letter import LetterData, Penerima, Penandatangan


class TestPDFGenerator:
    """Test suite for PDFGenerator service."""

    @pytest.fixture
    def sample_letter_data(self):
        """Create sample letter data for testing."""
        return LetterData(
            nomor="421/SMP-DINAS/2024/001",
            tanggal="12 Januari 2024",
            perihal="Undangan Rapat Koordinasi",
            penerima=Penerima(
                nama="Budi Santoso, S.Pd",
                jabatan="Kepala Sekolah SMP Negeri 1 Bandung"
            ),
            isi="Dengan ini kami mengundang Bapak/Ibu untuk menghadiri rapat koordinasi "
                "yang akan dilaksanakan pada hari Senin, 15 Januari 2024 pukul 09.00 WIB "
                "di Aula Dinas Pendidikan Kota Bandung. Mohon kehadirannya.",
            penandatangan=Penandatangan(
                nama="Dr. H. Ahmad Rizki, M.Pd",
                jabatan="Kepala Bidang SMP"
            )
        )

    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary output directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_generator_initialization(self, temp_output_dir):
        """Test that PDFGenerator initializes correctly."""
        generator = PDFGenerator(output_dir=temp_output_dir)

        assert generator.templates_dir is not None
        assert generator.output_dir == Path(temp_output_dir)
        assert generator.env is not None
        assert Path(temp_output_dir).exists()

    def test_generator_initialization_with_custom_templates_dir(self, temp_output_dir):
        """Test initialization with custom templates directory."""
        generator = PDFGenerator(
            templates_dir="app/templates",
            output_dir=temp_output_dir
        )

        assert generator.templates_dir == Path("app/templates")
        assert generator.output_dir == Path(temp_output_dir)

    def test_pdf_generation_returns_bytes(self, sample_letter_data, temp_output_dir):
        """Test that PDF generation returns bytes."""
        generator = PDFGenerator(output_dir=temp_output_dir)

        pdf_bytes = generator.generate(
            template_name="surat_dinas",
            data=sample_letter_data.model_dump()
        )

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        # PDF files start with %PDF
        assert pdf_bytes.startswith(b"%PDF")

    def test_pdf_generation_surat_edaran(self, sample_letter_data, temp_output_dir):
        """Test PDF generation for surat_edaran template."""
        generator = PDFGenerator(output_dir=temp_output_dir)

        pdf_bytes = generator.generate(
            template_name="surat_edaran",
            data=sample_letter_data.model_dump()
        )

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b"%PDF")

    def test_pdf_generation_surat_pemberitahuan(self, sample_letter_data, temp_output_dir):
        """Test PDF generation for surat_pemberitahuan template."""
        generator = PDFGenerator(output_dir=temp_output_dir)

        pdf_bytes = generator.generate(
            template_name="surat_pemberitahuan",
            data=sample_letter_data.model_dump()
        )

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b"%PDF")

    def test_invalid_template_raises_value_error(self, sample_letter_data, temp_output_dir):
        """Test that invalid template name raises ValueError."""
        generator = PDFGenerator(output_dir=temp_output_dir)

        with pytest.raises(ValueError) as exc_info:
            generator.generate(
                template_name="invalid_template",
                data=sample_letter_data.model_dump()
            )

        assert "is not supported" in str(exc_info.value)

    def test_unsupported_template_raises_value_error(self, sample_letter_data, temp_output_dir):
        """Test that unsupported template raises ValueError."""
        generator = PDFGenerator(output_dir=temp_output_dir)

        with pytest.raises(ValueError) as exc_info:
            generator.generate(
                template_name="surat_keputusan",
                data=sample_letter_data.model_dump()
            )

        assert "not supported" in str(exc_info.value)
        assert "surat_keputusan" in str(exc_info.value)

    def test_save_pdf_creates_file(self, sample_letter_data, temp_output_dir):
        """Test that save_pdf creates a file."""
        generator = PDFGenerator(output_dir=temp_output_dir)

        pdf_bytes = generator.generate(
            template_name="surat_dinas",
            data=sample_letter_data.model_dump()
        )

        file_path = generator.save_pdf(pdf_bytes, "test_surat")

        assert Path(file_path).exists()
        assert file_path.endswith("test_surat.pdf")

        # Verify file content
        with open(file_path, "rb") as f:
            saved_content = f.read()
            assert saved_content == pdf_bytes

    def test_save_pdf_with_pdf_extension(self, sample_letter_data, temp_output_dir):
        """Test save_pdf when filename already has .pdf extension."""
        generator = PDFGenerator(output_dir=temp_output_dir)

        pdf_bytes = generator.generate(
            template_name="surat_dinas",
            data=sample_letter_data.model_dump()
        )

        file_path = generator.save_pdf(pdf_bytes, "test_surat.pdf")

        assert Path(file_path).exists()
        assert file_path.endswith("test_surat.pdf")

    def test_save_pdf_creates_output_directory(self, sample_letter_data):
        """Test that save_pdf creates output directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            non_existent_dir = Path(tmpdir) / "nested" / "output" / "dir"
            generator = PDFGenerator(output_dir=str(non_existent_dir))

            pdf_bytes = generator.generate(
                template_name="surat_dinas",
                data=sample_letter_data.model_dump()
            )

            file_path = generator.save_pdf(pdf_bytes, "test_surat")

            assert non_existent_dir.exists()
            assert Path(file_path).exists()

    def test_pdf_generation_with_logo_path(self, sample_letter_data, temp_output_dir):
        """Test PDF generation with logo path."""
        generator = PDFGenerator(output_dir=temp_output_dir)

        # This will generate without logo since the file doesn't exist
        # but the validation should pass without error
        pdf_bytes = generator.generate(
            template_name="surat_dinas",
            data=sample_letter_data.model_dump(),
            logo_path="static/logo.png"
        )

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0

    def test_save_pdf_sanitizes_filename_path_traversal(self, sample_letter_data, temp_output_dir):
        """Test that save_pdf rejects path traversal attempts."""
        generator = PDFGenerator(output_dir=temp_output_dir)

        pdf_bytes = generator.generate(
            template_name="surat_dinas",
            data=sample_letter_data.model_dump()
        )

        # Try various path traversal attempts - all should raise ValueError
        malicious_filenames = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "../../malicious.pdf",
            "test/../../etc/passwd.pdf",
            "test\\..\\..\\etc\\passwd.pdf",
            "....//....//etc/passwd",  # Bypass attempt for replace("..", "")
            "./../file",
            "..file",
            "file/../../etc/passwd"
        ]

        for malicious_filename in malicious_filenames:
            with pytest.raises(ValueError) as exc_info:
                generator.save_pdf(pdf_bytes, malicious_filename)
            assert "Invalid filename" in str(exc_info.value) or "Path traversal" in str(exc_info.value)

    def test_save_pdf_invalid_characters(self, sample_letter_data, temp_output_dir):
        """Test that save_pdf rejects filenames with invalid characters."""
        generator = PDFGenerator(output_dir=temp_output_dir)

        pdf_bytes = generator.generate(
            template_name="surat_dinas",
            data=sample_letter_data.model_dump()
        )

        # Filenames with special characters should be rejected
        invalid_filenames = [
            "file@name.pdf",
            "file#name",
            "file$name",
            "file%name",
            "file&name",
            "file*name",
            "file|name",
            "file:name",
            "file<name>",
            "file>name",
            "file?name",
            'file"name'
        ]

        for invalid_filename in invalid_filenames:
            with pytest.raises(ValueError) as exc_info:
                generator.save_pdf(pdf_bytes, invalid_filename)
            assert "Invalid filename" in str(exc_info.value)

    def test_save_pdf_valid_filenames(self, sample_letter_data, temp_output_dir):
        """Test that save_pdf accepts valid filenames."""
        generator = PDFGenerator(output_dir=temp_output_dir)

        pdf_bytes = generator.generate(
            template_name="surat_dinas",
            data=sample_letter_data.model_dump()
        )

        # Valid filenames should work
        valid_filenames = [
            "test_surat",
            "test-surat",
            "test.surat",
            "test_surat 123",
            "Test Surat 2024.pdf",
            "surat-dinas-final.pdf"
        ]

        for valid_filename in valid_filenames:
            file_path = generator.save_pdf(pdf_bytes, valid_filename)
            assert Path(file_path).exists()
            # File should be in output directory
            assert Path(file_path).parent == Path(temp_output_dir)

    def test_save_pdf_size_limit(self, sample_letter_data, temp_output_dir):
        """Test that save_pdf rejects PDFs exceeding size limit."""
        generator = PDFGenerator(output_dir=temp_output_dir)

        # Create a PDF larger than MAX_PDF_SIZE (10MB)
        large_pdf = b"x" * (PDFGenerator.MAX_PDF_SIZE + 1)

        with pytest.raises(ValueError) as exc_info:
            generator.save_pdf(large_pdf, "test_surat")

        assert "exceeds maximum allowed size" in str(exc_info.value)

    def test_save_pdf_empty_filename(self, sample_letter_data, temp_output_dir):
        """Test that save_pdf raises ValueError for empty filename."""
        generator = PDFGenerator(output_dir=temp_output_dir)

        pdf_bytes = generator.generate(
            template_name="surat_dinas",
            data=sample_letter_data.model_dump()
        )

        # Empty filename should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            generator.save_pdf(pdf_bytes, "")

        assert "Invalid filename" in str(exc_info.value)

    def test_logo_path_validation_only_allows_static(self, sample_letter_data, temp_output_dir):
        """Test that logo path validation only allows app/static/ directory."""
        generator = PDFGenerator(output_dir=temp_output_dir)

        # These paths should be rejected (not in app/static/)
        malicious_paths = [
            "../../../etc/passwd",
            "/etc/passwd",
            "C:\\Windows\\System32\\config",
            "../../../../../../etc/passwd",
            "app/templates/base.html",
            "../templates/base.html",
        ]

        for logo_path in malicious_paths:
            # Should not raise error, but logo_path should not be in context
            # PDF should still generate without the logo
            pdf_bytes = generator.generate(
                template_name="surat_dinas",
                data=sample_letter_data.model_dump(),
                logo_path=logo_path
            )
            assert isinstance(pdf_bytes, bytes)
