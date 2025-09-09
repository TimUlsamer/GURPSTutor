import base64
import json
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="GURPS Adventure Builder", layout="wide")

ADVENTURE_DIR = Path(__file__).with_name("adventures")
ADVENTURE_DIR.mkdir(exist_ok=True)

TEMPLATE_PATH = Path(__file__).with_name("viewer_template.html")
HTML_TEMPLATE = TEMPLATE_PATH.read_text()

def render_html(data, pdf_b64, pdf_name):
    right_html = f'<h1>{data.get("title", "")} <span class="small">— GURPS Lite Quick-Links</span></h1>'
    right_html += '<p class="small">Tap any blue keyword to jump the PDF viewer on the left. Works on mobile & desktop.</p>'
    for sec in data.get("sections", []):
        tags_html = " ".join(f'<span class="pill">{t}</span>' for t in sec.get("tags", []))
        read_html = f'<div class="readaloud"><p>{sec.get("readaloud", "")}</p></div>' if sec.get("readaloud") else ""
        right_html += (
            f'<div class="panel" id="{sec.get("id", "")}">'
            f'<h2>{sec.get("id", "")}. {sec.get("title", "")} {tags_html}</h2>'
            f'{read_html}{sec.get("body", "")}'
            f"</div>"
        )
    html = HTML_TEMPLATE.replace("__RIGHT__", right_html)
    html = html.replace("__PDF_B64__", pdf_b64).replace("__PDF_NAME__", pdf_name)
    return html

st.sidebar.title("Menu")
mode = st.sidebar.radio("Mode", ["Browse", "Create/Edit"])

pdf_filename = st.sidebar.text_input("PDF file name (same folder):", value="GURPS 4e - Lite.pdf")
pdf_path = Path(pdf_filename)
if not pdf_path.exists():
    st.error(f"Cannot find **{pdf_filename}** in {Path('.').resolve()}")
    st.stop()
pdf_b64 = base64.b64encode(pdf_path.read_bytes()).decode("ascii")

if mode == "Browse":
    files = sorted(ADVENTURE_DIR.glob("*.json"))
    if not files:
        st.info("No adventures found.")
    else:
        names = [f.stem for f in files]
        choice = st.sidebar.selectbox("Adventure", names)
        data = json.loads((ADVENTURE_DIR / f"{choice}.json").read_text())
        html = render_html(data, pdf_b64, pdf_path.name)
        st.components.v1.html(html, height=900, scrolling=False)
        st.caption("Drag the vertical bar to resize the panels. Double-click (or double-tap) the bar to reset.")
else:
    files = sorted(ADVENTURE_DIR.glob("*.json"))
    names = [f.stem for f in files]
    choice = st.sidebar.selectbox("Adventure", ["<New>"] + names)
    if choice == "<New>":
        filename = st.sidebar.text_input("File name", value="new_adventure")
        data = {"title": "", "sections": []}
    else:
        filename = choice
        data = json.loads((ADVENTURE_DIR / f"{choice}.json").read_text())
    title = st.text_input("Title", value=data.get("title", ""))
    if "sections" not in st.session_state or st.session_state.get("file") != choice:
        sections = [
            {**sec, "tags": ", ".join(sec.get("tags", []))} for sec in data.get("sections", [])
        ]
        if not sections:
            sections = [{"id": "", "title": "", "tags": "", "readaloud": "", "body": ""}]
        st.session_state["sections"] = sections
    st.session_state["file"] = choice
    columns = ["id", "title", "tags", "readaloud", "body"]
    edited = st.data_editor(
        st.session_state["sections"],
        num_rows="dynamic",
        key="editor",
        column_order=columns,
        hide_index=True,
        column_config={
            "id": "ID",
            "title": "Title",
            "tags": "Tags (comma-separated)",
            "readaloud": "Read Aloud",
            "body": "Body HTML",
        },
    )

    def convert_rows(rows):
        out = []
        for row in rows:
            if not any(str(v).strip() for v in row.values()):
                continue
            tags = [t.strip() for t in row.get("tags", "").split(",") if t.strip()]
            out.append({**row, "tags": tags})
        return out

    if st.button("Save Adventure"):
        save_data = {"title": title, "sections": convert_rows(edited)}
        (ADVENTURE_DIR / f"{filename}.json").write_text(json.dumps(save_data, indent=2))
        st.success("Adventure saved.")
    if st.button("Preview"):
        preview_data = {"title": title, "sections": convert_rows(edited)}
        html = render_html(preview_data, pdf_b64, pdf_path.name)
        st.components.v1.html(html, height=900, scrolling=False)
        st.caption("Drag the vertical bar to resize the panels. Double-click (or double-tap) the bar to reset.")
