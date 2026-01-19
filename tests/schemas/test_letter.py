"""Tests for letter schemas."""

import pytest
from pydantic import ValidationError
from app.schemas.letter import (
    SchoolInfo, Person, KeyValueItem, Student,
    SuratTugasRequest, LembarPersetujuanRequest, LetterRequest, PDFResponse
)


class TestSchoolInfo:
    def test_school_info_with_all_fields(self):
        data = {
            "nama_sekolah": "SMK NEGERI 2 SINGOSARI",
            "alamat_jalan": "Jalan Perusahaan No. 20",
            "kelurahan": "Tunjungtirto",
            "kecamatan": "Singosari",
            "kab_kota": "Kab. Malang",
            "provinsi": "Jawa Timur",
            "kode_pos": "65153",
            "telepon": "(0341) 4345127",
            "email": "smkn2singosari@yahoo.co.id",
            "website": "www.smkn2singosari.sch.id",
            "logo_url": "https://example.com/logo.png"
        }
        school = SchoolInfo(**data)
        assert school.nama_sekolah == "SMK NEGERI 2 SINGOSARI"
        assert school.logo_url == "https://example.com/logo.png"

    def test_school_info_required_fields_only(self):
        data = {
            "nama_sekolah": "SMK Test",
            "alamat_jalan": "Jl. Test No. 1",
            "kab_kota": "Kab. Test",
            "provinsi": "Jawa Timur"
        }
        school = SchoolInfo(**data)
        assert school.kelurahan is None
        assert school.kode_pos is None

    def test_school_info_missing_required_field(self):
        data = {
            "nama_sekolah": "SMK Test",
            "alamat_jalan": "Jl. Test"
        }
        with pytest.raises(ValidationError):
            SchoolInfo(**data)


class TestPerson:
    def test_person_with_all_fields(self):
        data = {
            "nama": "SUMIJAH, S.Pd., M.Si.",
            "jabatan": "Kepala Sekolah",
            "nip": "19700210 199802 2 009",
            "pangkat": "Pembina Tk. I",
            "instansi": "SMK Negeri 2 Singosari"
        }
        person = Person(**data)
        assert person.nama == "SUMIJAH, S.Pd., M.Si."
        assert person.nip == "19700210 199802 2 009"

    def test_person_name_only(self):
        person = Person(nama="Budi Santoso")
        assert person.nama == "Budi Santoso"
        assert person.jabatan is None


class TestKeyValueItem:
    def test_key_value_item_default_separator(self):
        item = KeyValueItem(label="Keperluan", value="Test")
        assert item.label == "Keperluan"
        assert item.separator == ":"

    def test_key_value_item_custom_separator(self):
        item = KeyValueItem(label="Hari", value="Senin", separator=":")
        assert item.separator == ":"


class TestStudent:
    def test_student_valid(self):
        student = Student(nama="CHANDA ZULIA LESTARI")
        assert student.nama == "CHANDA ZULIA LESTARI"

    def test_student_missing_name(self):
        with pytest.raises(ValidationError):
            Student()


class TestSuratTugasRequest:
    def test_surat_tugas_valid(self):
        data = {
            "nomor_surat": "800/123/SMK.2/2024",
            "tanggal_surat": "1 Juli 2024",
            "perihal": "SURAT TUGAS",
            "school_info": {
                "nama_sekolah": "SMK Test",
                "alamat_jalan": "Jl. Test",
                "kab_kota": "Kab. Test",
                "provinsi": "Jawa Timur"
            },
            "penandatangan": {"nama": "Kepala Sekolah"},
            "assignees": [{"nama": "Guru 1"}, {"nama": "Guru 2"}],
            "details": [
                {"label": "Keperluan", "value": "Test"}
            ]
        }
        request = SuratTugasRequest(**data)
        assert len(request.assignees) == 2
        assert request.perihal == "SURAT TUGAS"

    def test_surat_tugas_empty_assignees(self):
        data = {
            "nomor_surat": "800/123/SMK.2/2024",
            "tanggal_surat": "1 Juli 2024",
            "school_info": {
                "nama_sekolah": "SMK Test",
                "alamat_jalan": "Jl. Test",
                "kab_kota": "Kab. Test",
                "provinsi": "Jawa Timur"
            },
            "penandatangan": {"nama": "Kepala Sekolah"},
            "assignees": [],
            "details": []
        }
        with pytest.raises(ValidationError):
            SuratTugasRequest(**data)


class TestLembarPersetujuanRequest:
    def test_lembar_persetujuan_valid(self):
        data = {
            "school_info": {
                "nama_sekolah": "SMK Test",
                "alamat_jalan": "Jl. Test",
                "kab_kota": "Kab. Test",
                "provinsi": "Jawa Timur"
            },
            "students": [{"nama": "Siswa 1"}, {"nama": "Siswa 2"}],
            "nama_perusahaan": "PT Test"
        }
        request = LembarPersetujuanRequest(**data)
        assert len(request.students) == 2
        assert request.nama_perusahaan == "PT Test"

    def test_lembar_persetujuan_empty_students(self):
        data = {
            "school_info": {
                "nama_sekolah": "SMK Test",
                "alamat_jalan": "Jl. Test",
                "kab_kota": "Kab. Test",
                "provinsi": "Jawa Timur"
            },
            "students": [],
            "nama_perusahaan": "PT Test"
        }
        with pytest.raises(ValidationError):
            LembarPersetujuanRequest(**data)


class TestPDFResponse:
    def test_pdf_response_valid(self):
        response = PDFResponse(
            filename="test.pdf",
            file_url="/api/v1/letters/download/test.pdf",
            file_size=12345
        )
        assert response.filename == "test.pdf"
        assert response.file_size == 12345
