"""Tests for file utility functions."""

from pathlib import Path

from src.utils.file_utils import (
    ensure_directory,
    get_file_extension,
    is_hidden_file,
    is_supported_format,
    is_temp_file,
)


class TestGetFileExtension:
    def test_returns_lowercase_ext(self):
        assert get_file_extension("data.CSV") == ".csv"
        assert get_file_extension("data.Parquet") == ".parquet"

    def test_no_extension(self):
        assert get_file_extension("README") == ""

    def test_dotted_filename(self):
        assert get_file_extension(".gitignore") == ""

    def test_multiple_dots(self):
        assert get_file_extension("archive.tar.gz") == ".gz"


class TestIsSupportedFormat:
    def test_csv_supported(self):
        assert is_supported_format("data.csv") is True

    def test_parquet_supported(self):
        assert is_supported_format("data.parquet") is True

    def test_pq_supported(self):
        assert is_supported_format("data.pq") is True

    def test_json_supported(self):
        assert is_supported_format("data.json") is True

    def test_txt_not_supported(self):
        assert is_supported_format("data.txt") is False

    def test_no_extension_not_supported(self):
        assert is_supported_format("Makefile") is False


class TestIsHiddenFile:
    def test_dot_prefix_is_hidden(self, tmp_path):
        file = tmp_path / ".hidden.csv"
        file.write_text("data")
        assert is_hidden_file(file) is True

    def test_normal_file_not_hidden(self, tmp_path):
        file = tmp_path / "visible.csv"
        file.write_text("data")
        assert is_hidden_file(file) is False

    def test_windows_hidden_attribute(self, tmp_path):
        """Test with stat FILE_ATTRIBUTE_HIDDEN (mock the st_file_attributes)."""
        import stat
        from unittest.mock import patch

        file = tmp_path / "win_hidden.csv"
        file.write_text("data")

        with patch.object(Path, "stat") as mock_stat:
            mock_stat.return_value.st_file_attributes = stat.FILE_ATTRIBUTE_HIDDEN
            assert is_hidden_file(file) is True


class TestIsTempFile:
    def test_tilde_prefix_is_temp(self):
        assert is_temp_file("~tempfile.csv") is True

    def test_dot_prefix_is_temp(self):
        assert is_temp_file(".swapfile.csv") is True

    def test_tmp_extension(self):
        assert is_temp_file("data.tmp") is True

    def test_temp_extension(self):
        assert is_temp_file("data.temp") is True

    def test_swp_extension(self):
        assert is_temp_file("data.swp") is True

    def test_bak_extension(self):
        assert is_temp_file("data.bak") is True

    def test_normal_file_not_temp(self):
        assert is_temp_file("data.csv") is False

    def test_normal_parquet_not_temp(self):
        assert is_temp_file("data.parquet") is False


class TestEnsureDirectory:
    def test_creates_directory(self, tmp_path):
        new_dir = tmp_path / "a" / "b" / "c"
        assert not new_dir.exists()

        result = ensure_directory(new_dir)
        assert new_dir.exists()
        assert result == new_dir

    def test_returns_path_for_existing_dir(self, tmp_path):
        existing = tmp_path / "existing"
        existing.mkdir(parents=True)

        result = ensure_directory(existing)
        assert result == existing
