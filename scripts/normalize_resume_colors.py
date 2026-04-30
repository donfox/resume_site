"""Normalize resume DOCX colors without changing content.

This script updates the Word source document so all non-hyperlink text uses a
single dark blue while hyperlinks use a brighter blue. It edits the DOCX XML
directly using lxml to preserve namespace prefixes and avoid Word corruption.
"""

from __future__ import annotations

import shutil
import tempfile
import zipfile
from pathlib import Path

from lxml import etree


DOCX_PATH = Path("static/files/Don Fox.docx")
BACKUP_PATH = Path("static/files/Don Fox.colors-backup.docx")

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}

DARK_BLUE = "001279"
BRIGHT_LINK_BLUE = "0563C1"


def qn(tag: str) -> str:
    prefix, local = tag.split(":", 1)
    if prefix != "w":
        raise ValueError(f"Unsupported namespace prefix: {prefix}")
    return f"{{{W_NS}}}{local}"


def ensure_child(parent: etree._Element, tag: str) -> etree._Element:
    child = parent.find(tag)
    if child is None:
        child = etree.SubElement(parent, tag)
    return child


def set_color(r_pr: etree._Element, value: str) -> None:
    color = ensure_child(r_pr, qn("w:color"))
    color.set(qn("w:val"), value)
    for attr in (qn("w:themeColor"), qn("w:themeShade"), qn("w:themeTint")):
        if attr in color.attrib:
            del color.attrib[attr]


def normalize_run(r_el: etree._Element, color_value: str) -> None:
    r_pr = ensure_child(r_el, qn("w:rPr"))
    set_color(r_pr, color_value)


def paragraph_has_text(p_el: etree._Element) -> bool:
    for text_el in p_el.findall(".//w:t", NS):
        if text_el.text and text_el.text.strip():
            return True
    return False


def normalize_document_xml(xml_bytes: bytes) -> bytes:
    root = etree.fromstring(xml_bytes)

    for hyperlink in root.findall(".//w:hyperlink", NS):
        for run in hyperlink.findall(".//w:r", NS):
            normalize_run(run, BRIGHT_LINK_BLUE)

    for paragraph in root.findall(".//w:p", NS):
        if not paragraph_has_text(paragraph):
            continue
        for run in paragraph.findall("./w:r", NS):
            normalize_run(run, DARK_BLUE)

    return etree.tostring(root, encoding="utf-8", xml_declaration=True)


def normalize_styles_xml(xml_bytes: bytes) -> bytes:
    root = etree.fromstring(xml_bytes)

    for style in root.findall("w:style", NS):
        style_id = style.get(qn("w:styleId"))
        if style_id == "Hyperlink":
            r_pr = ensure_child(style, qn("w:rPr"))
            set_color(r_pr, BRIGHT_LINK_BLUE)

    return etree.tostring(root, encoding="utf-8", xml_declaration=True)


def rewrite_docx(docx_path: Path) -> None:
    fd, tmp_name = tempfile.mkstemp(suffix=".docx")
    tmp_path = Path(tmp_name)
    tmp_path.unlink(missing_ok=True)

    try:
        with (
            zipfile.ZipFile(docx_path, "r") as src,
            zipfile.ZipFile(tmp_name, "w", compression=zipfile.ZIP_DEFLATED) as dst,
        ):
            for info in src.infolist():
                data = src.read(info.filename)
                if info.filename == "word/document.xml":
                    data = normalize_document_xml(data)
                elif info.filename == "word/styles.xml":
                    data = normalize_styles_xml(data)
                dst.writestr(info, data)

        shutil.move(tmp_name, docx_path)
    finally:
        tmp_path.unlink(missing_ok=True)


def main() -> None:
    if not DOCX_PATH.exists():
        raise FileNotFoundError(f"Not found: {DOCX_PATH}")

    shutil.copy2(DOCX_PATH, BACKUP_PATH)
    rewrite_docx(DOCX_PATH)
    print(f"Backup written to {BACKUP_PATH}")
    print(f"Normalized colors in {DOCX_PATH}")


if __name__ == "__main__":
    main()
