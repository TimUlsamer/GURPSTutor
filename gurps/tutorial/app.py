import base64
import json
import re
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="GURPS Adventure Builder", layout="wide")

ADVENTURE_DIR = Path(__file__).with_name("adventures")
ADVENTURE_DIR.mkdir(exist_ok=True)

TEMPLATE_PATH = Path(__file__).with_name("viewer_template.html")
HTML_TEMPLATE = TEMPLATE_PATH.read_text()


def apply_keywords(text, keywords):
    for kw in keywords:
        word = kw.get("keyword")
        page = kw.get("page")
        if word and page:
            pattern = re.escape(word)
            repl = f'<span class="pdf" data-page="{page}">{word} p.{page}</span>'
            text = re.sub(pattern, repl, text)
    return text


def render_html(data, pdf_b64, pdf_name):
    right_html = f'<h1>{data.get("title", "")} <span class="small">— GURPS Lite Quick-Links</span></h1>'
    right_html += '<p class="small">Tap any blue keyword to jump the PDF viewer on the left. Works on mobile & desktop.</p>'
    for sec in data.get("sections", []):
        tags_html = " ".join(f'<span class="pill">{t}</span>' for t in sec.get("tags", []))
        keywords = sec.get("keywords", [])
        read_text = apply_keywords(sec.get("readaloud", ""), keywords)
        read_html = f'<div class="readaloud"><p>{read_text}</p></div>' if read_text else ""
        body_html = apply_keywords(sec.get("body", ""), keywords)
        right_html += (
            f'<div class="panel" id="{sec.get("id", "")}">'
            f'<h2>{sec.get("id", "")}. {sec.get("title", "")} {tags_html}</h2>'
            f'{read_html}{body_html}'
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

    def empty_section():
        return {"id": "", "title": "", "tags": [], "readaloud": "", "body": "", "keywords": []}

    if "sections" not in st.session_state or st.session_state.get("file") != choice:
        sections = data.get("sections", [])
        if not sections:
            sections = [empty_section()]
        st.session_state["sections"] = sections
        st.session_state["file"] = choice

    for i, sec in enumerate(st.session_state["sections"]):
        with st.expander(f"Section {i + 1}: {sec.get('title', '') or '(untitled)'}", expanded=True):
            sec["id"] = st.text_input("ID", value=sec.get("id", ""), key=f"id_{i}")
            sec["title"] = st.text_input("Title", value=sec.get("title", ""), key=f"title_{i}")
            tags_str = st.text_input(
                "Tags (comma-separated)",
                value=", ".join(sec.get("tags", [])),
                key=f"tags_{i}",
            )
            sec["tags"] = [t.strip() for t in tags_str.split(",") if t.strip()]
            sec["readaloud"] = st.text_area("Read Aloud", value=sec.get("readaloud", ""), key=f"ra_{i}")
            sec["body"] = st.text_area("Body", value=sec.get("body", ""), key=f"body_{i}")
            kw_rows = st.data_editor(
                sec.get("keywords", []),
                num_rows="dynamic",
                hide_index=True,
                key=f"kw_{i}",
                column_config={"keyword": "Keyword", "page": "Page"},
            )
            sec["keywords"] = [kw for kw in kw_rows if kw.get("keyword") and kw.get("page")]
            if st.button("Delete Section", key=f"del_{i}"):
                del st.session_state["sections"][i]
                st.experimental_rerun()

    if st.button("Add Section"):
        st.session_state["sections"].append(empty_section())

    def clean_sections(sections):
        out = []
        for sec in sections:
            base = {k: sec.get(k, "") for k in ["id", "title", "readaloud", "body"]}
            if not any(str(v).strip() for v in base.values()) and not sec.get("tags") and not sec.get("keywords"):
                continue
            sec["tags"] = [t for t in sec.get("tags", []) if t]
            sec["keywords"] = [k for k in sec.get("keywords", []) if k.get("keyword") and k.get("page")]
            out.append(sec)
        return out

    if st.button("Save Adventure"):
        save_data = {"title": title, "sections": clean_sections(st.session_state["sections"])}
        (ADVENTURE_DIR / f"{filename}.json").write_text(json.dumps(save_data, indent=2))
        st.success("Adventure saved.")
    if st.button("Preview"):
        preview_data = {"title": title, "sections": clean_sections(st.session_state["sections"])}
        html = render_html(preview_data, pdf_b64, pdf_path.name)
        st.components.v1.html(html, height=900, scrolling=False)
        st.caption("Drag the vertical bar to resize the panels. Double-click (or double-tap) the bar to reset.")
