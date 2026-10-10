"""Contract tests for the website's diagram topics.

Checks that docs/topics/*.json and docs/diagrams/*.svg agree with each
other. Standard library only.
"""
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

DOCS = Path(__file__).resolve().parent.parent / "docs"
TOPIC_FILES = sorted((DOCS / "topics").glob("*.json"))
SVG = "{http://www.w3.org/2000/svg}"
ID_RE = re.compile(r"^[a-z][a-z0-9-]*$")
FORBIDDEN_TAGS = {"script", "image", "foreignObject"}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def text_ok(value):
    return isinstance(value, str) and value.strip() != ""


def local(tag):
    return tag.split("}")[-1]


@pytest.mark.parametrize("path", TOPIC_FILES, ids=lambda p: p.stem)
def test_topic_shape(path):
    topic = load(path)
    assert topic["id"] == path.stem
    assert text_ok(topic["title"])
    assert topic["parts"], "topic has no parts"
    for part_id, part in topic["parts"].items():
        assert ID_RE.match(part_id), part_id
        assert text_ok(part["name"]), part_id
        assert text_ok(part["summary"]), part_id
        words = len(part["details"].split())
        assert 40 <= words <= 120, f"{part_id}: details has {words} words"
        assert 2 <= len(part["facts"]) <= 5, part_id
        assert all(text_ok(f) for f in part["facts"]), part_id
    assert topic["diagrams"], "topic has no diagrams"
    ids = [d["id"] for d in topic["diagrams"]]
    assert len(ids) == len(set(ids)), "duplicate diagram id"
    for d in topic["diagrams"]:
        assert ID_RE.match(d["id"]), d["id"]
        assert text_ok(d["title"]) and text_ok(d["intro"]), d["id"]
        assert d["svg"] == f"diagrams/{d['id']}.svg"
        assert d["parts"], d["id"]
        assert len(d["parts"]) == len(set(d["parts"])), d["id"]
        for part_id in d["parts"]:
            assert part_id in topic["parts"], f"{d['id']}: unknown part {part_id}"


@pytest.mark.parametrize("path", TOPIC_FILES, ids=lambda p: p.stem)
def test_no_unused_parts(path):
    topic = load(path)
    used = {p for d in topic["diagrams"] for p in d["parts"]}
    assert used == set(topic["parts"])


def nested_parts(el, inside=False):
    """Yield data-part ids that sit inside another data-part group."""
    here = el.get("data-part")
    if here and inside:
        yield here
    for child in el:
        yield from nested_parts(child, inside or bool(here))


@pytest.mark.parametrize("path", TOPIC_FILES, ids=lambda p: p.stem)
def test_diagram_svgs_follow_contract(path):
    topic = load(path)
    for d in topic["diagrams"]:
        svg_path = DOCS / d["svg"]
        assert svg_path.is_file(), d["svg"]
        root = ET.parse(svg_path).getroot()
        assert root.tag == SVG + "svg", d["svg"]
        assert root.get("viewBox"), f"{d['svg']}: missing viewBox"
        assert root.get("width") is None and root.get("height") is None, d["svg"]
        for el in root.iter():
            assert local(el.tag) not in FORBIDDEN_TAGS, f"{d['svg']}: <{local(el.tag)}>"
            for name, value in el.attrib.items():
                assert not local(name).startswith("on"), f"{d['svg']}: {name}"
                if local(name) == "href":
                    assert value.startswith("#"), f"{d['svg']}: external href"
        drawn = {el.get("data-part") for el in root.iter() if el.get("data-part")}
        assert drawn == set(d["parts"]), (
            f"{d['svg']}: only in drawing {sorted(drawn - set(d['parts']))}, "
            f"only in JSON {sorted(set(d['parts']) - drawn)}"
        )
        assert list(nested_parts(root)) == [], f"{d['svg']}: nested data-part"


def test_every_svg_file_is_used():
    used = {d["svg"] for p in TOPIC_FILES for d in load(p)["diagrams"]}
    on_disk = {f"diagrams/{p.name}" for p in (DOCS / "diagrams").glob("*.svg")}
    assert on_disk == used
