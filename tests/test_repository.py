"""Tests for CurriculumRepository — structure checks and mocked CRUD.

Tests repository methods with mocked SQLAlchemy sessions so no real
database is required. Live DB tests are gated behind DATABASE_URL.
"""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest

pytest.importorskip("sqlalchemy")
reading_models = pytest.importorskip("koinonia_db.models.reading")
repository = pytest.importorskip("src.repository")

CurriculumRepository = repository.CurriculumRepository
Curriculum = reading_models.Curriculum
ReadingSessionRow = reading_models.ReadingSessionRow
Entry = reading_models.Entry


# ── Structure Tests (no DB required) ───────────────────────────


def test_repository_has_add_curriculum():
    assert callable(getattr(CurriculumRepository, "add_curriculum"))


def test_repository_has_get_curriculum():
    assert callable(getattr(CurriculumRepository, "get_curriculum"))


def test_repository_has_list_curricula():
    assert callable(getattr(CurriculumRepository, "list_curricula"))


def test_repository_has_count_curricula():
    assert callable(getattr(CurriculumRepository, "count_curricula"))


def test_repository_has_add_session():
    assert callable(getattr(CurriculumRepository, "add_session"))


def test_repository_has_get_sessions():
    assert callable(getattr(CurriculumRepository, "get_sessions"))


def test_repository_has_add_entry():
    assert callable(getattr(CurriculumRepository, "add_entry"))


def test_repository_has_get_entry_by_title():
    assert callable(getattr(CurriculumRepository, "get_entry_by_title"))


def test_repository_has_count_entries():
    assert callable(getattr(CurriculumRepository, "count_entries"))


def test_repository_has_link_entry_to_session():
    assert callable(getattr(CurriculumRepository, "link_entry_to_session"))


def test_repository_has_add_discussion_question():
    assert callable(getattr(CurriculumRepository, "add_discussion_question"))


def test_repository_has_add_guide():
    assert callable(getattr(CurriculumRepository, "add_guide"))


# ── Mocked Unit Tests ──────────────────────────────────────────

@pytest.fixture
def repo():
    """Create a CurriculumRepository with mocked engine."""
    with patch("src.repository.create_engine"):
        return CurriculumRepository("postgresql+psycopg://test@localhost/test")


def _mock_session_ctx():
    """Return a mock Session context manager and its inner session."""
    session = MagicMock()
    ctx = MagicMock()
    ctx.__enter__ = MagicMock(return_value=session)
    ctx.__exit__ = MagicMock(return_value=False)
    return ctx, session


def test_add_curriculum_commits_and_returns_id(repo):
    ctx, session = _mock_session_ctx()
    with patch("src.repository.Session", return_value=ctx):
        def set_id(obj):
            obj.id = 42
        session.add.side_effect = set_id

        result = repo.add_curriculum("Test", "theme", "I", 8, "desc")
        assert result == 42
        session.commit.assert_called_once()


def test_get_curriculum_delegates_to_session_get(repo):
    ctx, session = _mock_session_ctx()
    mock_obj = MagicMock(spec=Curriculum)
    session.get.return_value = mock_obj
    with patch("src.repository.Session", return_value=ctx):
        result = repo.get_curriculum(1)
    assert result is mock_obj
    session.get.assert_called_once_with(Curriculum, 1)


def test_get_curriculum_returns_none_when_missing(repo):
    ctx, session = _mock_session_ctx()
    session.get.return_value = None
    with patch("src.repository.Session", return_value=ctx):
        result = repo.get_curriculum(999)
    assert result is None


def test_list_curricula_returns_list(repo):
    ctx, session = _mock_session_ctx()
    mock_rows = [MagicMock(spec=Curriculum), MagicMock(spec=Curriculum)]
    session.scalars.return_value = mock_rows
    with patch("src.repository.Session", return_value=ctx):
        result = repo.list_curricula()
    assert len(result) == 2


def test_count_curricula_returns_integer(repo):
    ctx, session = _mock_session_ctx()
    session.query.return_value.count.return_value = 5
    with patch("src.repository.Session", return_value=ctx):
        result = repo.count_curricula()
    assert result == 5


def test_add_session_commits_and_returns_id(repo):
    ctx, session = _mock_session_ctx()
    with patch("src.repository.Session", return_value=ctx):
        def set_id(obj):
            obj.id = 7
        session.add.side_effect = set_id

        result = repo.add_session(curriculum_id=1, week=1, title="Week 1")
        assert result == 7
        session.commit.assert_called_once()


def test_get_sessions_returns_list(repo):
    ctx, session = _mock_session_ctx()
    mock_rows = [MagicMock(spec=ReadingSessionRow)]
    session.scalars.return_value = mock_rows
    with patch("src.repository.Session", return_value=ctx):
        result = repo.get_sessions(curriculum_id=1)
    assert len(result) == 1


def test_add_entry_commits_and_returns_id(repo):
    ctx, session = _mock_session_ctx()
    with patch("src.repository.Session", return_value=ctx):
        def set_id(obj):
            obj.id = 99
        session.add.side_effect = set_id

        result = repo.add_entry(title="Being and Time", author="Heidegger")
        assert result == 99
        session.commit.assert_called_once()


def test_get_entry_by_title_found(repo):
    ctx, session = _mock_session_ctx()
    mock_entry = MagicMock(spec=Entry)
    session.scalar.return_value = mock_entry
    with patch("src.repository.Session", return_value=ctx):
        result = repo.get_entry_by_title("Being and Time")
    assert result is mock_entry


def test_get_entry_by_title_not_found(repo):
    ctx, session = _mock_session_ctx()
    session.scalar.return_value = None
    with patch("src.repository.Session", return_value=ctx):
        result = repo.get_entry_by_title("Nonexistent")
    assert result is None


def test_count_entries_returns_integer(repo):
    ctx, session = _mock_session_ctx()
    session.query.return_value.count.return_value = 30
    with patch("src.repository.Session", return_value=ctx):
        result = repo.count_entries()
    assert result == 30


def test_link_entry_to_session_commits(repo):
    ctx, session = _mock_session_ctx()
    with patch("src.repository.Session", return_value=ctx):
        repo.link_entry_to_session(session_id=1, entry_id=5)
    session.add.assert_called_once()
    session.commit.assert_called_once()


def test_add_discussion_question_commits_and_returns_id(repo):
    ctx, session = _mock_session_ctx()
    with patch("src.repository.Session", return_value=ctx):
        def set_id(obj):
            obj.id = 15
        session.add.side_effect = set_id

        result = repo.add_discussion_question(
            session_id=1, question_text="What is the main argument?"
        )
        assert result == 15
        session.commit.assert_called_once()


def test_add_guide_commits_and_returns_id(repo):
    ctx, session = _mock_session_ctx()
    with patch("src.repository.Session", return_value=ctx):
        def set_id(obj):
            obj.id = 3
        session.add.side_effect = set_id

        result = repo.add_guide(
            session_id=1,
            opening_questions=["Q1?", "Q2?"],
            deep_dive_questions=["D1?"],
            activities=["A1"],
            closing_reflection="Reflect on X",
        )
        assert result == 3
        session.commit.assert_called_once()


# ── Live DB Tests (gated behind DATABASE_URL) ──────────────────

_skip_no_db = pytest.mark.skipif(
    not os.environ.get("DATABASE_URL"),
    reason="DATABASE_URL not set — skipping live DB tests",
)


@_skip_no_db
def test_live_instantiation():
    repo = CurriculumRepository(os.environ["DATABASE_URL"])
    assert repo is not None


@_skip_no_db
def test_live_count_curricula():
    repo = CurriculumRepository(os.environ["DATABASE_URL"])
    count = repo.count_curricula()
    assert isinstance(count, int)
    assert count >= 0


@_skip_no_db
def test_live_list_curricula():
    repo = CurriculumRepository(os.environ["DATABASE_URL"])
    curricula = repo.list_curricula()
    assert isinstance(curricula, list)


@_skip_no_db
def test_live_count_entries():
    repo = CurriculumRepository(os.environ["DATABASE_URL"])
    count = repo.count_entries()
    assert isinstance(count, int)
    assert count >= 0
