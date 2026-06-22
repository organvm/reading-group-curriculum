"""Tests for reading_group_curriculum data_export — curricula index and sample."""
import json
from pathlib import Path

from src.data_export import (
    load_seed_curricula,
    load_seed_readings,
    build_curricula_index,
    render_sample_curriculum,
    export_all,
)


def _write_seed_dir(tmp_path: Path) -> Path:
    seed_dir = tmp_path / "seed"
    seed_dir.mkdir()
    curricula = {
        "curricula": [
            {
                "title": "Foundations of Recursive Systems",
                "theme": "recursive-systems",
                "organ_focus": "ORGAN-I",
                "duration_weeks": 2,
                "description": "Study recursive systems.",
                "sessions": [
                    {
                        "week": 1,
                        "title": "Strange Loops",
                        "readings": ["reading-1", "reading-2"],
                        "questions": ["What makes a loop strange?"],
                        "activities": ["Map a feedback loop"],
                    },
                    {
                        "week": 2,
                        "title": "Self-Reference",
                        "readings": ["reading-3"],
                        "questions": ["Where does self-reference help?"],
                        "activities": ["Write a short reflection"],
                    },
                ],
            },
            {
                "title": "Building in Public",
                "theme": "building-in-public",
                "organ_focus": "ORGAN-V",
                "duration_weeks": 1,
                "description": "Study transparent development.",
                "sessions": [
                    {
                        "week": 1,
                        "title": "Public Process",
                        "readings": ["reading-4"],
                        "questions": [],
                        "activities": [],
                    }
                ],
            },
            {
                "title": "Theory to Product",
                "theme": "cross-organ",
                "organ_focus": "cross-organ",
                "duration_weeks": 1,
                "description": "Study cross-organ product movement.",
                "sessions": [
                    {
                        "week": 1,
                        "title": "Pipeline",
                        "readings": ["reading-5"],
                        "questions": [],
                        "activities": [],
                    }
                ],
            },
        ]
    }
    readings = {
        "entries": [
            {
                "key": f"reading-{i}",
                "title": f"Reading {i}",
                "author": "Author",
            }
            for i in range(1, 12)
        ]
    }
    (seed_dir / "curricula.json").write_text(json.dumps(curricula))
    (seed_dir / "reading_lists.json").write_text(json.dumps(readings))
    return seed_dir


def test_load_seed_curricula(tmp_path):
    """Loads curricula from a seed file."""
    seed_dir = _write_seed_dir(tmp_path)
    curricula = load_seed_curricula(seed_dir)
    assert len(curricula) >= 3
    assert curricula[0]["title"]


def test_load_seed_readings(tmp_path):
    """Loads reading entries from a seed file."""
    seed_dir = _write_seed_dir(tmp_path)
    readings = load_seed_readings(seed_dir)
    assert len(readings) > 10
    assert readings[0]["title"]


def test_load_seed_missing_dir(tmp_path):
    """Returns empty lists when seed dir doesn't have files."""
    assert load_seed_curricula(tmp_path) == []
    assert load_seed_readings(tmp_path) == []


def test_build_curricula_index(tmp_path):
    """Index has expected structure and counts."""
    seed_dir = _write_seed_dir(tmp_path)
    curricula = load_seed_curricula(seed_dir)
    readings = load_seed_readings(seed_dir)
    index = build_curricula_index(curricula, readings)
    assert index["curriculum_count"] >= 3
    assert index["total_sessions"] > 0
    assert index["total_weeks"] > 0
    assert len(index["themes"]) > 0
    assert index["reading_entry_count"] > 0
    for c in index["curricula"]:
        assert "title" in c
        assert "session_count" in c
        assert "theme" in c


def test_render_sample_curriculum(tmp_path):
    """Renders a curriculum to markdown with expected headings."""
    seed_dir = _write_seed_dir(tmp_path)
    curricula = load_seed_curricula(seed_dir)
    md = render_sample_curriculum(curricula[0])
    assert md.startswith("# ")
    assert "**Theme:**" in md
    assert "**Duration:**" in md
    assert "## Week" in md


def test_export_all_writes_files(tmp_path):
    """export_all writes both artifacts to the output directory."""
    seed_dir = _write_seed_dir(tmp_path)
    output_dir = tmp_path / "output"
    paths = export_all(seed_dir=seed_dir, output_dir=output_dir)
    assert len(paths) == 2

    index_path = output_dir / "curricula-index.json"
    assert index_path.exists()
    data = json.loads(index_path.read_text())
    assert data["curriculum_count"] >= 3

    md_path = output_dir / "sample-curriculum.md"
    assert md_path.exists()
    assert md_path.read_text().startswith("# ")
