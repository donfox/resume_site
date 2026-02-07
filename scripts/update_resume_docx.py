import copy
import os
import tempfile
import xml.etree.ElementTree as ET
import zipfile


def insert_emrts_gap_note(docx_path: str) -> None:
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    note_text = (
        "Note: Gaps between EMRTS engagements are covered by contracts listed below."
    )

    with zipfile.ZipFile(docx_path) as docx:
        xml = docx.read("word/document.xml")

    root = ET.fromstring(xml)
    body = root.find("w:body", ns)
    if body is None:
        raise RuntimeError("Missing document body")

    target_phrase = "Projects included rapid prototyping and R&D with academic and professional collaborations."

    all_text = "".join(text.text for text in root.findall(".//w:t", ns) if text.text)
    note_already_present = note_text in all_text

    target_p = None
    for paragraph in body.findall("w:p", ns):
        texts = [text.text for text in paragraph.findall(".//w:t", ns) if text.text]
        if target_phrase in "".join(texts):
            target_p = paragraph
            break

    if target_p is None:
        raise RuntimeError("Target paragraph not found")

    if not note_already_present:
        new_p = ET.Element(f"{{{ns['w']}}}p")
        for child in list(target_p):
            if child.tag == f"{{{ns['w']}}}pPr":
                new_p.append(copy.deepcopy(child))
                break

        run = ET.SubElement(new_p, f"{{{ns['w']}}}r")
        text = ET.SubElement(run, f"{{{ns['w']}}}t")
        text.text = note_text

        children = list(body)
        idx = children.index(target_p)
        body.insert(idx + 1, new_p)

    new_xml = ET.tostring(root, encoding="utf-8", xml_declaration=True)

    with zipfile.ZipFile(docx_path) as docx:
        entries = [(info, docx.read(info.filename)) for info in docx.infolist()]

    fd, temp_path = tempfile.mkstemp(suffix=".docx")
    os.close(fd)
    try:
        with zipfile.ZipFile(temp_path, "w", compression=zipfile.ZIP_DEFLATED) as docx:
            for info, data in entries:
                if info.filename == "word/document.xml":
                    continue
                docx.writestr(info, data)
            docx.writestr("word/document.xml", new_xml)
        os.replace(temp_path, docx_path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


if __name__ == "__main__":
    insert_emrts_gap_note("static/files/Resume.v3.7.docx")
    print("Inserted note after EMRTS summary paragraph.")
