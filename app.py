import base64
import json
import re
from pathlib import Path

import streamlit as st

ADVENTURE_DIR = Path("adventures")
ADVENTURE_DIR.mkdir(exist_ok=True)


def slugify(name: str) -> str:
    """Create a filesystem-friendly name."""
    return re.sub(r"[^a-zA-Z0-9_-]", "_", name).lower()


def list_adventures():
    return [p.stem for p in ADVENTURE_DIR.glob("*.json")]


def load_adventure(name: str) -> dict:
    with open(ADVENTURE_DIR / f"{name}.json", "r", encoding="utf-8") as fh:
        return json.load(fh)


def save_adventure(data: dict):
    filename = slugify(data["name"] or "adventure") + ".json"
    with open(ADVENTURE_DIR / filename, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def pdf_viewer(path: Path) -> str:
    b64 = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="800" type="application/pdf"></iframe>'


def view_page():
    adventures = list_adventures()
    if not adventures:
        st.info("No adventures found. Use the editor to create one.")
        return
    name = st.selectbox("Choose adventure", adventures)
    data = load_adventure(name)
    pdf_path = Path(data.get("pdf", ""))
    cols = st.columns([3, 2])
    with cols[0]:
        if pdf_path.exists():
            st.components.v1.html(pdf_viewer(pdf_path), height=800, scrolling=True)
        else:
            st.error(f"PDF '{pdf_path}' not found.")
    with cols[1]:
        st.header(data.get("name", "Adventure"))
        for sec in data.get("sections", []):
            with st.container():
                st.subheader(sec.get("title", "Section"))
                st.write(sec.get("content", ""))


def editor_page():
    st.header("Adventure Editor")
    existing = list_adventures()
    load_name = st.selectbox("Load adventure", ["<new>"] + existing)
    if load_name != "<new>":
        data = load_adventure(load_name)
    else:
        data = {"name": "", "pdf": "GURPS 4e - Lite.pdf", "sections": []}
    st.text_input("Adventure name", key="adv_name", value=data["name"])
    st.text_input("PDF file", key="adv_pdf", value=data["pdf"])
    if "sections" not in st.session_state:
        st.session_state.sections = data["sections"]
    cols = st.columns([3, 1])
    with cols[1]:
        if st.button("Add section"):
            st.session_state.sections.append({"title": "", "content": ""})
    for i, sec in enumerate(st.session_state.sections):
        with st.expander(f"Section {i+1}"):
            st.text_input("Title", key=f"title_{i}", value=sec.get("title", ""))
            st.text_area("Content", key=f"content_{i}", value=sec.get("content", ""), height=150)
            if st.button("Delete", key=f"del_{i}"):
                st.session_state.sections.pop(i)
                st.experimental_rerun()
    if st.button("Save adventure"):
        sections = []
        for i in range(len(st.session_state.sections)):
            sections.append({
                "title": st.session_state.get(f"title_{i}", ""),
                "content": st.session_state.get(f"content_{i}", ""),
            })
        adv = {
            "name": st.session_state.get("adv_name", ""),
            "pdf": st.session_state.get("adv_pdf", ""),
            "sections": sections,
        }
        save_adventure(adv)
        st.success("Adventure saved")


st.sidebar.title("Menu")
page = st.sidebar.radio("Go to", ["View", "Editor"])
if page == "View":
    view_page()
else:
    editor_page()
