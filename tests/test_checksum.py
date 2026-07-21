"""
Tests for the checksum generation module.
"""

import tempfile
from pathlib import Path

import pytest

from src.ingestion.checksum import calculate_md5, calculate_sha256, compare_checksum

# ── Fixtures ───────────────────────────────────────────────────────


@pytest.fixture
def sample_file() -> Path:
    """Create a temporary file with known content."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("col1,col2\n1,test\n2,data\n")
        path = Path(f.name)
    yield path
    path.unlink(missing_ok=True)


@pytest.fixture
def empty_file() -> Path:
    """Create an empty temporary file."""
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        path = Path(f.name)
    yield path
    path.unlink(missing_ok=True)


@pytest.fixture
def large_file() -> Path:
    """Create a ~1 MB file for chunked reading tests."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        # Write ~100k lines (~1 MB)
        f.write("id,value\n")
        for i in range(100_000):
            f.write(f"{i},{i * 1.5}\n")
        path = Path(f.name)
    yield path
    path.unlink(missing_ok=True)


# ── SHA-256 Tests ──────────────────────────────────────────────────


class TestCalculateSha256:
    def test_returns_hex_string(self, sample_file: Path):
        """Should return a 64-character hex string."""
        checksum = calculate_sha256(sample_file)
        assert isinstance(checksum, str)
        assert len(checksum) == 64
        assert all(c in "0123456789abcdef" for c in checksum)

    def test_deterministic(self, sample_file: Path):
        """Same file content should always produce the same checksum."""
        c1 = calculate_sha256(sample_file)
        c2 = calculate_sha256(sample_file)
        assert c1 == c2

    def test_different_files_differ(self):
        """Different content -> different checksums."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f1:
            f1.write("content_a\n")
            p1 = Path(f1.name)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f2:
            f2.write("content_b\n")
            p2 = Path(f2.name)

        try:
            c1 = calculate_sha256(p1)
            c2 = calculate_sha256(p2)
            assert c1 != c2
        finally:
            p1.unlink(missing_ok=True)
            p2.unlink(missing_ok=True)

    def test_empty_file(self, empty_file: Path):
        """Empty file should still produce a valid checksum."""
        checksum = calculate_sha256(empty_file)
        assert isinstance(checksum, str)
        assert len(checksum) == 64

    def test_large_file_chunked(self, large_file: Path):
        """Large files should be processed via chunked reading."""
        checksum = calculate_sha256(large_file)
        assert isinstance(checksum, str)
        assert len(checksum) == 64


# ── MD5 Tests ──────────────────────────────────────────────────────


class TestCalculateMd5:
    def test_returns_hex_string(self, sample_file: Path):
        """MD5 should return a 32-character hex string."""
        checksum = calculate_md5(sample_file)
        assert isinstance(checksum, str)
        assert len(checksum) == 32

    def test_deterministic(self, sample_file: Path):
        """Same file -> same MD5."""
        c1 = calculate_md5(sample_file)
        c2 = calculate_md5(sample_file)
        assert c1 == c2


# ── Compare Checksum Tests ─────────────────────────────────────────


class TestCompareChecksum:
    def test_matching_checksum(self, sample_file: Path):
        """Should return True when checksum matches."""
        checksum = calculate_sha256(sample_file)
        assert compare_checksum(sample_file, checksum) is True

    def test_non_matching_checksum(self, sample_file: Path):
        """Should return False when checksum differs."""
        wrong_checksum = "a" * 64
        assert compare_checksum(sample_file, wrong_checksum) is False

    def test_md5_comparison(self, sample_file: Path):
        """Should work with MD5 algorithm too."""
        checksum = calculate_md5(sample_file)
        assert compare_checksum(sample_file, checksum, algorithm="md5") is True
