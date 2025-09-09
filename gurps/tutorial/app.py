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
        st.session_state["sections"] = data.get("sections", []) or [
            {"id": "", "title": "", "tags": [], "readaloud": "", "body": ""}
        ]
    st.session_state["file"] = choice

    sections = st.session_state["sections"]

    if st.button("Add Section"):
        sections.append({"id": "", "title": "", "tags": [], "readaloud": "", "body": ""})

    for idx, sec in enumerate(sections):
        with st.expander(f"Section {sec.get('id') or idx + 1}", expanded=True):
            sec["id"] = st.text_input("ID", value=sec.get("id", ""), key=f"id_{idx}")
            sec["title"] = st.text_input("Title", value=sec.get("title", ""), key=f"title_{idx}")
            tags_str = ", ".join(sec.get("tags", []))
            tags_input = st.text_input(
                "Tags (comma-separated)", value=tags_str, key=f"tags_{idx}"
            )
            sec["tags"] = [t.strip() for t in tags_input.split(",") if t.strip()]
            sec["readaloud"] = st.text_area(
                "Read Aloud", value=sec.get("readaloud", ""), key=f"ra_{idx}"
            )

            body_key = f"body_{idx}"
            if body_key not in st.session_state:
                st.session_state[body_key] = sec.get("body", "")
            st.text_area(
                "Body HTML", value=st.session_state[body_key], key=body_key, height=200
            )

            kw_cols = st.columns([2, 1, 1])
            kw_text = kw_cols[0].text_input("Keyword", key=f"kw_{idx}")
            kw_page = kw_cols[1].number_input(
                "PDF page", min_value=1, step=1, key=f"page_{idx}"
            )
            if kw_cols[2].button("Insert", key=f"ins_{idx}"):
                snippet = f'<span class="pdf" data-page="{int(kw_page)}">{kw_text}</span>'
                st.session_state[body_key] = (
                    st.session_state[body_key].rstrip() + " " + snippet
                ).strip()
                st.session_state[f"kw_{idx}"] = ""

            sec["body"] = st.session_state[body_key]

            if st.button("Delete Section", key=f"del_{idx}"):
                sections.pop(idx)
                st.experimental_rerun()

    def clean_sections(rows):
        out = []
        for row in rows:
            if not any(
                str(row.get(f, "")).strip()
                for f in ["id", "title", "readaloud", "body"]
            ) and not row.get("tags"):
                continue
            out.append(row)
        return out

    if st.button("Save Adventure"):
        save_data = {"title": title, "sections": clean_sections(sections)}
        (ADVENTURE_DIR / f"{filename}.json").write_text(json.dumps(save_data, indent=2))
        st.success("Adventure saved.")
    if st.button("Preview"):
        preview_data = {"title": title, "sections": clean_sections(sections)}
        html = render_html(preview_data, pdf_b64, pdf_path.name)
        st.components.v1.html(html, height=900, scrolling=False)
        st.caption(
            "Drag the vertical bar to resize the panels. Double-click (or double-tap) the bar to reset."
        )
