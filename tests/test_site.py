"""Contract tests for the website's site map.

Checks that docs/site.json, docs/index.html and docs/topics/*.json agree
with each other. Standard library only.
"""
import json
import re
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs"
ID_RE = re.compile(r"^[a-z][a-z0-9-]*$")
COLOR_RE = re.compile(r"^#[0-9a-f]{6}$")
TABLE = "table"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def text_ok(value):
    return isinstance(value, str) and value.strip() != ""


def site():
    return load(DOCS / "site.json")


def topic_entries():
    return [t for s in site()["subjects"] for t in s["topics"]]


def test_site_has_title_and_subjects():
    data = site()
    assert text_ok(data["title"])
    assert data["subjects"], "site.json has no subjects"


def test_subjects_are_well_formed():
    subjects = site()["subjects"]
    ids = [s["id"] for s in subjects]
    assert len(ids) == len(set(ids)), "duplicate subject id"
    for s in subjects:
        assert ID_RE.match(s["id"]), s["id"]
        assert text_ok(s["title"]), s["id"]
        assert text_ok(s["blurb"]), s["id"]
        assert COLOR_RE.match(s["color"]), f"{s['id']}: colour {s['color']!r}"
        assert s["topics"], f"{s['id']}: no topics"
        for t in s["topics"]:
            assert ID_RE.match(t["id"]), t["id"]
            assert text_ok(t["title"]), t["id"]


def test_topic_ids_are_unique_and_not_reserved():
    ids = [t["id"] for t in topic_entries()]
    assert len(ids) == len(set(ids)), "duplicate topic id"
    assert "home" not in ids, "'home' is reserved"


def test_site_map_matches_topic_files():
    ids = [t["id"] for t in topic_entries()]
    assert ids.count(TABLE) == 1, "'table' must be listed exactly once"
    on_disk = {p.stem for p in (DOCS / "topics").glob("*.json")}
    assert set(ids) - {TABLE} == on_disk


def test_site_map_titles_match_topic_files():
    for t in topic_entries():
        if t["id"] == TABLE:
            continue
        topic = load(DOCS / "topics" / f"{t['id']}.json")
        assert t["title"] == topic["title"], t["id"]


def test_index_has_views_and_no_tabs():
    html = (DOCS / "index.html").read_text(encoding="utf-8")
    for element_id in ("home-view", "table-view", "topic-view", "topic-nav"):
        assert f'id="{element_id}"' in html, element_id
    assert "data-tab" not in html, "old tab buttons are still in index.html"


def test_index_loads_scripts_in_order():
    html = (DOCS / "index.html").read_text(encoding="utf-8")
    scripts = re.findall(r'<script src="([^"]+)"></script>', html)
    assert scripts == ["app.js", "topics.js", "site.js"]


def test_pulmonary_veins_text_matches_drawing():
    # The drawing shows one pair of veins; the text must not leave a
    # student counting two lines against "four".
    heart = load(DOCS / "topics" / "heart.json")
    assert "only the pair from one lung" in heart["parts"]["pulmonary-veins"]["details"].lower()
