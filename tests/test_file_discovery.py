"""
Tests for the File Discovery service.
"""

import tempfile
from pathlib import Path

import pytest

from src.ingestion.file_discovery import FileDiscoverer

# Colourful test filenames
HIDDEN_FILE = ".hidden_file.csv"
TEMP_FILE = "~temp_file.csv"
SUPPORTED_CSV = "orders_2026_07_20.csv"
SUPPORTED_PARQUET = "orders_2026_07_20.parquet"
SUPPORTED_JSON = "orders_2026_07_20.json"
UNSUPPORTED_FILE = "readme.txt"


# ── Fixtures ───────────────────────────────────────────────────────


@pytest.fixture
def empty_tmp_dir() -> Path:
    """An empty temporary directory."""
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


@pytest.fixture
def mixed_tmp_dir() -> Path:
    """A directory with supported, unsupported, hidden, and temp files."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        # Supported files
        (tmp_path / SUPPORTED_CSV).write_text("col1,col2\n1,data\n")
        (tmp_path / SUPPORTED_PARQUET).write_text("dummy parquet")
        (tmp_path / SUPPORTED_JSON).write_text('{"key": "value"}')

        # Unsupported file
        (tmp_path / UNSUPPORTED_FILE).write_text("Some notes")

        # Hidden file (leading dot)
        (tmp_path / HIDDEN_FILE).write_text("hidden")

        # Temp file (leading tilde)
        (tmp_path / TEMP_FILE).write_text("temp")

        # Create a subdirectory (should be ignored)
        (tmp_path / "subdir").mkdir()

        yield tmp_path


@pytest.fixture
def discoverer(empty_tmp_dir: Path) -> FileDiscoverer:
    """A FileDiscoverer scoped to an empty directory."""
    return FileDiscoverer(base_path=empty_tmp_dir)


# ── Constructor ────────────────────────────────────────────────────


class TestFileDiscovererInit:
    def test_creates_directory_if_missing(self):
        """Should create the base directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmp:
            new_dir = Path(tmp) / "new_incremental"
            assert not new_dir.exists()

            discoverer = FileDiscoverer(base_path=new_dir)
            assert new_dir.exists()
            assert discoverer.base_path == new_dir

    def test_accepts_existing_directory(self, empty_tmp_dir: Path):
        """Should accept an already-existing directory."""
        discoverer = FileDiscoverer(base_path=empty_tmp_dir)
        assert discoverer.base_path == empty_tmp_dir


# ── discover_files ─────────────────────────────────────────────────


class TestDiscoverFiles:
    def test_empty_folder(self, discoverer: FileDiscoverer):
        """Empty folder should return an empty list."""
        files = discoverer.discover_files()
        assert files == []

    def test_ignores_hidden_files(self, mixed_tmp_dir: Path):
        """Should skip files starting with a dot."""
        discoverer = FileDiscoverer(base_path=mixed_tmp_dir)
        files = discoverer.discover_files()
        filenames = [f.name for f in files]
        assert HIDDEN_FILE not in filenames

    def test_ignores_temp_files(self, mixed_tmp_dir: Path):
        """Should skip files starting with a tilde."""
        discoverer = FileDiscoverer(base_path=mixed_tmp_dir)
        files = discoverer.discover_files()
        filenames = [f.name for f in files]
        assert TEMP_FILE not in filenames

    def test_ignores_unsupported_formats(self, mixed_tmp_dir: Path):
        """Should skip .txt and other unsupported extensions."""
        discoverer = FileDiscoverer(base_path=mixed_tmp_dir)
        files = discoverer.discover_files()
        filenames = [f.name for f in files]
        assert UNSUPPORTED_FILE not in filenames

    def test_includes_supported_formats(self, mixed_tmp_dir: Path):
        """Should include .csv, .parquet, .json files."""
        discoverer = FileDiscoverer(base_path=mixed_tmp_dir)
        files = discoverer.discover_files()
        filenames = [f.name for f in files]
        assert SUPPORTED_CSV in filenames
        assert SUPPORTED_PARQUET in filenames
        assert SUPPORTED_JSON in filenames

    def test_single_new_file(self, empty_tmp_dir: Path):
        """A single CSV should be discovered."""
        csv_file = empty_tmp_dir / "orders_2026_07_20.csv"
        csv_file.write_text("col1\nval1\n")

        discoverer = FileDiscoverer(base_path=empty_tmp_dir)
        files = discoverer.discover_files()
        assert len(files) == 1
        assert files[0].name == "orders_2026_07_20.csv"

    def test_multiple_new_files(self, empty_tmp_dir: Path):
        """Multiple supported files should all be discovered."""
        for name in ["a.csv", "b.csv", "c.json"]:
            (empty_tmp_dir / name).write_text("col1\nval\n")

        discoverer = FileDiscoverer(base_path=empty_tmp_dir)
        files = discoverer.discover_files(sort_by="name", reverse=False)
        assert len(files) == 3

    def test_not_a_directory_returns_empty(self):
        """If base_path is a file, returns an empty list."""
        with tempfile.NamedTemporaryFile(suffix=".csv") as f:
            discoverer = FileDiscoverer(base_path=Path(f.name))
            files = discoverer.discover_files()
            assert files == []


# ── Sorting ────────────────────────────────────────────────────────


class TestSortFiles:
    def test_sort_by_name(self, empty_tmp_dir: Path):
        """Sort files alphabetically by name."""
        for name in ["c.csv", "b.csv", "a.csv"]:
            (empty_tmp_dir / name).write_text("col1\nval\n")

        discoverer = FileDiscoverer(base_path=empty_tmp_dir)
        files = discoverer.discover_files(sort_by="name", reverse=False)
        assert [f.name for f in files] == ["a.csv", "b.csv", "c.csv"]

    def test_sort_by_name_reverse(self, empty_tmp_dir: Path):
        """Reverse alphabetical sort."""
        for name in ["a.csv", "b.csv", "c.csv"]:
            (empty_tmp_dir / name).write_text("col1\nval\n")

        discoverer = FileDiscoverer(base_path=empty_tmp_dir)
        files = discoverer.discover_files(sort_by="name", reverse=True)
        assert [f.name for f in files] == ["c.csv", "b.csv", "a.csv"]


# ── get_latest_file ────────────────────────────────────────────────


class TestGetLatestFile:
    def test_returns_none_when_empty(self, discoverer: FileDiscoverer):
        """Empty folder returns None."""
        assert discoverer.get_latest_file() is None

    def test_returns_file_when_present(self, empty_tmp_dir: Path):
        """Should return the single file when one exists."""
        latest = empty_tmp_dir / "latest.csv"
        latest.write_text("col1\nval\n")

        discoverer = FileDiscoverer(base_path=empty_tmp_dir)
        result = discoverer.get_latest_file()
        assert result is not None
        assert result.name == "latest.csv"


# ── validate_filename ──────────────────────────────────────────────


class TestValidateFilename:
    def test_valid_pattern(self):
        """Should accept filenames matching the expected convention."""
        assert FileDiscoverer.validate_filename("orders_2026_07_20.csv") is True
        assert FileDiscoverer.validate_filename("inventory_2026_07_21.parquet") is True
        assert FileDiscoverer.validate_filename("simple.json") is True

    def test_invalid_pattern(self):
        """Should reject filenames with spaces or special chars."""
        assert FileDiscoverer.validate_filename("orders 2026.csv") is False
        assert FileDiscoverer.validate_filename("../escape.csv") is False
