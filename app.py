import json
import base64
from pathlib import Path
import streamlit as st

ADVENTURE_DIR = Path("adventures")


def load_adventures():
    adventures = {}
    if ADVENTURE_DIR.exists():
        for path in ADVENTURE_DIR.glob("*.json"):
            adventures[path.stem] = json.loads(path.read_text(encoding="utf-8"))
    return adventures


def pdf_viewer(pdf_path: Path):
    if not pdf_path.exists():
        st.warning(f"PDF '{pdf_path}' not found")
        return
    b64 = base64.b64encode(pdf_path.read_bytes()).decode("utf-8")
    pdf_display = f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="900" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


def show_adventure(data):
    left, right = st.columns(2)
    with left:
        pdf_viewer(Path(data.get("pdf", "")))
    with right:
        st.header(data.get("title", "Adventure"))
        for sec in data.get("sections", []):
            with st.expander(sec.get("title", "Section")):
                if sec.get("tags"):
                    tags = ", ".join(sec["tags"])
                    st.caption(tags)
                if sec.get("readaloud"):
                    st.markdown(f"**Read-Aloud:** {sec['readaloud']}")
                if sec.get("body"):
                    st.write(sec["body"])


def editor():
    name = st.text_input("Adventure name", st.session_state.get("adv_name", ""))
    pdf_file = st.text_input("PDF filename", st.session_state.get("pdf_file", "GURPS 4e - Lite.pdf"))
    sections = st.session_state.setdefault("sections", [])
    if st.button("Add section"):
        sections.append({"title": "", "tags": "", "readaloud": "", "body": ""})
    to_delete = []
    for idx, sec in enumerate(sections):
        with st.expander(f"Section {idx+1}", expanded=True):
            sec["title"] = st.text_input("Title", sec["title"], key=f"title_{idx}")
            sec["tags"] = st.text_input("Tags (comma separated)", sec["tags"], key=f"tags_{idx}")
            sec["readaloud"] = st.text_area("Read-aloud", sec["readaloud"], key=f"ra_{idx}")
            sec["body"] = st.text_area("Body", sec["body"], key=f"body_{idx}")
            if st.button("Delete", key=f"del_{idx}"):
                to_delete.append(idx)
    for idx in reversed(to_delete):
        sections.pop(idx)
    if st.button("Save adventure"):
        if not name:
            st.error("Please provide an adventure name")
        else:
            data = {
                "title": name,
                "pdf": pdf_file,
                "sections": [
                    {
                        "title": s["title"],
                        "tags": [t.strip() for t in s["tags"].split(",") if t.strip()],
                        "readaloud": s["readaloud"],
                        "body": s["body"],
                    }
                    for s in sections
                ],
            }
            ADVENTURE_DIR.mkdir(exist_ok=True)
            filename = name.lower().replace(" ", "_") + ".json"
            (ADVENTURE_DIR / filename).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            st.success(f"Saved to adventures/{filename}")
            st.session_state.adv_name = name
            st.session_state.pdf_file = pdf_file


st.sidebar.title("GURPS Adventure Manager")
mode = st.sidebar.selectbox("Mode", ["Browse Adventures", "Adventure Editor"])

if mode == "Browse Adventures":
    adventures = load_adventures()
    if not adventures:
        st.info("No adventures found. Create one in the editor.")
    else:
        choice = st.selectbox("Choose adventure", list(adventures.keys()))
        show_adventure(adventures[choice])
else:
    editor()
