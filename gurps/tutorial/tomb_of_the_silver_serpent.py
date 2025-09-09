# app.py
# Streamlit app: PDF.js viewer + adventure with a draggable split pane.
# Put "GURPS 4e - Lite.pdf" in the same folder (or change name in the sidebar).

import base64
import json
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="The Tomb of the Silver Serpent — GURPS Lite Viewer", layout="wide")

# ----------- Menu & Simple Adventure Editor -----------
st.sidebar.title("Menü")
mode = st.sidebar.radio("Ansicht", ["Abenteuer ansehen", "Abenteuer erstellen"], index=0)

if mode == "Abenteuer erstellen":
    st.header("Abenteuer-Editor")
    st.caption("Erstelle oder verwalte deine eigenen Abenteuer-Kacheln.")

    if "tiles" not in st.session_state:
        st.session_state["tiles"] = []

    st.session_state["adv_title"] = st.text_input(
        "Titel des Abenteuers",
        value=st.session_state.get("adv_title", ""),
    )

    uploaded = st.file_uploader("Abenteuer aus JSON laden", type="json")
    if uploaded is not None:
        data = json.load(uploaded)
        st.session_state["adv_title"] = data.get("title", "")
        st.session_state["tiles"] = data.get("tiles", [])

    with st.form("tile_form"):
        t_title = st.text_input("Abschnittstitel")
        t_tags = st.text_input("Tags (Komma-getrennt)")
        t_readaloud = st.text_area("Vorlesetext")
        t_body = st.text_area("Beschreibung")
        add = st.form_submit_button("Kachel hinzufügen")

    if add and t_title:
        st.session_state["tiles"].append(
            {
                "title": t_title,
                "tags": [s.strip() for s in t_tags.split(",") if s.strip()],
                "readaloud": t_readaloud,
                "body": t_body,
            }
        )

    for i, tile in enumerate(st.session_state["tiles"]):
        st.subheader(f"{i + 1}. {tile['title']}")
        if tile["tags"]:
            st.markdown("Tags: " + ", ".join(tile["tags"]))
        if tile["readaloud"]:
            st.markdown("> " + tile["readaloud"].replace("\n", "\n> "))
        st.write(tile["body"])
        if st.button(f"Kachel löschen {i + 1}", key=f"del_{i}"):
            st.session_state["tiles"].pop(i)
            st.experimental_rerun()

    adventure_data = {
        "title": st.session_state.get("adv_title", ""),
        "tiles": st.session_state.get("tiles", []),
    }
    st.download_button(
        "Abenteuer speichern",
        data=json.dumps(adventure_data, ensure_ascii=False, indent=2),
        file_name="abenteuer.json",
        mime="application/json",
    )

    st.stop()

# ----------- Adventure Viewer -----------
st.sidebar.title("Settings")
pdf_filename = st.sidebar.text_input("PDF file name (same folder):", value="GURPS 4e - Lite.pdf")

pdf_path = Path(pdf_filename)
if not pdf_path.exists():
    st.error(
        f"Cannot find **{pdf_filename}** in {Path('.').resolve()}\n\n"
        "• Put the PDF in the same folder as `app.py`, or\n"
        "• Change the file name in the sidebar."
    )
    st.stop()

pdf_b64 = base64.b64encode(pdf_path.read_bytes()).decode("ascii")

html = """
<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<style>
  :root{
    --bg:#0e0f12; --panel:#151821; --ink:#e7ecf3; --muted:#b7c3d6; --accent:#79b8ff; --accent2:#a4f9c8;
    --pill:#1e2430; --pill-border:#2a3142; --link:#9ed0ff;
    --left:46%; --right:54%; /* initial split */
    --gutter:10px; /* splitter width */
  }
  html,body{background:var(--bg); color:var(--ink); margin:0; font-family:system-ui,-apple-system,Segoe UI,Roboto,Inter,Helvetica,Arial,sans-serif; line-height:1.55; height:100%}
  .wrap{
    display:grid;
    grid-template-columns: var(--left) var(--gutter) var(--right);
    grid-template-rows: 100%;
    gap:0;
    height:100vh; box-sizing:border-box; padding:10px;
  }
  .viewer{
    grid-column:1;
    position:sticky; top:0; height:calc(100vh - 20px);
    background:#0b0c10; border:1px solid #222839; border-radius:12px; overflow:auto; padding:8px
  }
  .right{
    grid-column:3;
    overflow:auto; padding-left:12px; padding-right:6px
  }
  .gutter{
    grid-column:2;
    cursor:col-resize;
    position:relative;
    display:flex; align-items:center; justify-content:center;
    touch-action:none; /* important for mobile dragging */
  }
  /* visual of the splitter */
  .bar{
    width:16px; height:70%;
    background:linear-gradient(180deg,#2a3142,#3b4560);
    border-radius:6px;
    box-shadow:0 0 0 1px #1d2330, inset 0 0 0 1px #4a5876;
  }
  .gutter.active .bar{ background:linear-gradient(180deg,#5b6a8d,#8aa2d1) }

  /* UI cosmetics */
  h1{font-size:1.45rem; margin:.2rem 0 .6rem}
  h2{font-size:1.18rem; margin:1rem 0 .4rem}
  h3{font-size:1.02rem; margin:.9rem 0 .25rem; color:var(--muted)}
  p{margin:.5rem 0}
  .panel{background:var(--panel); border:1px solid #222839; border-radius:14px; padding:12px 14px; margin:10px 0}
  .readaloud{border-left:4px solid var(--accent2); background:#182028; padding:10px 12px; border-radius:10px}
  .pill{display:inline-block; background:var(--pill); border:1px solid var(--pill-border); border-radius:999px; padding:.18rem .55rem; margin:.12rem .2rem; font-size:.86rem; color:var(--muted)}
  .pdf{color:var(--link); border-bottom:1px dotted #3b5b7c; cursor:pointer}
  .pdf:hover{text-decoration:underline}
  .small{font-size:.92rem; color:var(--muted)}
  .map{white-space:nowrap; overflow:auto}
  .kbd{font-family:ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; background:#212634; border:1px solid #2a3142; padding:.08rem .4rem; border-radius:6px}
  .toolbar{display:flex; gap:8px; align-items:center; flex-wrap:wrap; padding:6px 6px 8px; position:sticky; top:0; background:#0b0c10; z-index:2}
  .btn{appearance:none; border:1px solid #2a3142; background:#1a2030; color:#cfe2ff; padding:.34rem .6rem; border-radius:10px; cursor:pointer}
  input[type="number"]{width:5rem; background:#121620; border:1px solid #2a3142; color:#e6eefc; padding:.3rem .4rem; border-radius:8px}
  canvas{display:block; margin:0 auto; background:#0b0c10; border:1px solid #222839; border-radius:8px}
  .note{color:#a9bad6; font-size:.9rem}
</style>
</head>
<body>
<div class="wrap" id="splitWrap">
  <div class="viewer" id="viewer">
    <div class="toolbar">
      <button class="btn" id="prevBtn">◀ Prev</button>
      <button class="btn" id="nextBtn">Next ▶</button>
      <span class="small">Page</span>
      <input type="number" id="pageInput" min="1" value="1" />
      <span id="pageCount" class="small">/ ?</span>
      <span style="flex:1 1 auto"></span>
      <button class="btn" id="zoomOut">−</button>
      <span class="small">Zoom</span>
      <button class="btn" id="zoomIn">+</button>
      <button class="btn" id="fitWidth">Fit Width</button>
      <span class="note">File: <span class="kbd">__PDF_NAME__</span></span>
    </div>
    <canvas id="pdfCanvas"></canvas>
    <div id="pdfError" class="note" style="padding:8px 6px;"></div>
  </div>

  <div class="gutter" id="gutter" role="separator" aria-orientation="vertical" aria-label="Resize panels">
    <div class="bar"></div>
  </div>

  <div class="right">
    <h1>The Tomb of the Silver Serpent <span class="small">— GURPS Lite Quick-Links</span></h1>
    <p class="small">Tap any blue keyword to jump the PDF viewer on the left. Works on mobile & desktop.</p>

    <div class="panel">
      <p class="small">You are a novice delver sent to recover the Silver Serpent Idol from an old hill-tomb.</p>
      <div class="map small"><strong>Flow:</strong> A. Village → B. Sink-Stairs → C. Whispering Antechamber → D. Hall of Echoes → E. Barred Door & Crawl → F. Ember Room → G. Prisoner → H. Serpent Shrine → I. Idol & Collapse → J. Exit</div>
    </div>

    <div class="panel">
      <h3>Quick-Start Character</h3>
      <p><strong>Rowan</strong> — ST 11, DX 12, IQ 11, HT 11; HP 11, FP 11; Basic Speed 5.75, Move 5, Dodge 8 (<span class="pdf" data-page="6">Secondary & Dodge p.6</span>).</p>
      <p><strong>Advantage:</strong> <span class="pdf" data-page="9">Combat Reflexes p.9</span></p>
      <p><strong>Skills:</strong>
        Broadsword-13; Shield-12 (<span class="pdf" data-page="14">Melee Weapons p.14-15</span>);
        <span class="pdf" data-page="22">Climbing p.22</span>; Stealth (<span class="pdf" data-page="13">Skill list p.13-16</span>);
        <span class="pdf" data-page="30">First Aid p.30</span>; <span class="pdf" data-page="14">Lockpicking p.14</span>;
        <span class="pdf" data-page="22">Hiking p.22-23</span>;
        Diplomacy / Fast-Talk / Intimidation (<span class="pdf" data-page="24">Influence p.24</span>);
        Jumping (<span class="pdf" data-page="14">skill p.14</span>; <span class="pdf" data-page="23">rules p.23</span>).
      </p>
      <p><strong>Kit:</strong> Light armor (<span class="pdf" data-page="18">DR p.18-19</span>), rope, torches, picks, bandages. Track <span class="pdf" data-page="22">Encumbrance & Move p.22</span>.</p>
    </div>

    <div class="panel" id="A">
      <h2>A. Village Edge <span class="pill">Reaction</span> <span class="pill">Influence</span></h2>
      <div class="readaloud"><p>Old Maera meets you by a standing stone: “Bring back the idol and hush the hill.”</p></div>
      <p>Roll <span class="pdf" data-page="3">Reaction p.3</span> or use an <span class="pdf" data-page="24">Influence roll p.24</span> as a <span class="pdf" data-page="3">Quick Contest p.3</span>.</p>
      <p class="small">Optional trail: <span class="pdf" data-page="22">Hiking p.22-23</span> · Fatigue basics <span class="pdf" data-page="31">p.31</span></p>
    </div>

    <div class="panel" id="B">
      <h2>B. Sink-Stairs <span class="pill">Climbing</span> <span class="pill">Encumbrance</span> <span class="pill">Falling</span></h2>
      <div class="readaloud"><p>Collapsed stone stairs spiral into dark.</p></div>
      <p>Tie rope; roll <span class="pdf" data-page="22">Climbing p.22</span> (start; then each 5 min). Apply <span class="pdf" data-page="22">Encumbrance p.22</span>. Failure → <span class="pdf" data-page="31">Falling p.31</span>; Jumping help <span class="pdf" data-page="23">p.23</span>.</p>
    </div>

    <div class="panel" id="C">
      <h2>C. Whispering Antechamber <span class="pill">Perception</span> <span class="pill">Fright</span></h2>
      <div class="readaloud"><p>Faint sibilant whispers drift from ahead.</p></div>
      <p><span class="pdf" data-page="24">Hearing p.24</span> to parse. Then a chill passes—make a <span class="pdf" data-page="24">Fright Check p.24</span> (+2 if <span class="pdf" data-page="9">Combat Reflexes p.9</span>).</p>
    </div>

    <div class="panel" id="D">
      <h2>D. Hall of Echoes <span class="pill">Stealth vs Hearing</span> <span class="pill">Maneuvers</span></h2>
      <div class="readaloud"><p>The ceiling is webbed with bats.</p></div>
      <p>Use Stealth vs. <span class="pdf" data-page="24">Hearing p.24</span> as a <span class="pdf" data-page="3">Quick Contest p.3</span>. If swarmed, consider <span class="pdf" data-page="25">All-Out Defense p.25-27</span>.</p>
    </div>

    <div class="panel" id="E">
      <h2>E. Barred Door & Crawl <span class="pill">Lockpicking</span> <span class="pill">Contests</span> <span class="pill">Poison</span></h2>
      <div class="readaloud"><p>Cold air hisses through iron bars. A wall crack beckons.</p></div>
      <ul>
        <li><strong>Pick:</strong> <span class="pdf" data-page="14">Lockpicking p.14</span>; spot with <span class="pdf" data-page="24">Vision p.24</span>. Fail & prick → <span class="pdf" data-page="32">Poison p.32</span>.</li>
        <li><strong>Force:</strong> your ST as a <span class="pdf" data-page="3">Quick Contest p.3</span> vs Door 13 (crit fail: lose FP <span class="pdf" data-page="31">p.31</span>).</li>
        <li><strong>Crawl:</strong> <span class="pdf" data-page="24">Vision p.24</span> + <span class="pdf" data-page="22">Climbing p.22</span> (Flexibility helps <span class="pdf" data-page="9">p.9</span>); back out with <span class="pdf" data-page="25">Ready p.25-27</span>.</li>
      </ul>
    </div>

    <div class="panel" id="F">
      <h2>F. Ember Room <span class="pill">Flame</span> <span class="pill">Heat</span> <span class="pill">Fatigue</span></h2>
      <div class="readaloud"><p>Four braziers and a serpent relief with four fire-icons.</p></div>
      <p>Flame hurts: <span class="pdf" data-page="32">Flame p.32</span> (ignite; put out with <span class="pdf" data-page="25">Ready p.25-27</span>). Heat drains FP: <span class="pdf" data-page="32">Heat p.32</span>, <span class="pdf" data-page="31">Fatigue p.31</span>.</p>
    </div>

    <div class="panel" id="G">
      <h2>G. Prisoner <span class="pill">First Aid</span> <span class="pill">Disease</span> <span class="pill">Reaction</span></h2>
      <div class="readaloud"><p>Tavi, a sickly tomb-robber, pleads for help.</p></div>
      <p><span class="pdf" data-page="3">Reaction p.3</span> or <span class="pdf" data-page="24">Influence p.24</span>. Spores as <span class="pdf" data-page="31">Disease p.31-32</span>. Treat with <span class="pdf" data-page="30">First Aid p.30</span>.</p>
    </div>

    <div class="panel" id="H">
      <h2>H. Serpent Shrine <span class="pill">Combat</span> <span class="pill">Defenses</span> <span class="pill">Damage & DR</span> <span class="pill">Poison</span></h2>
      <div class="readaloud"><p>Scales rustle around a coiled stone idol…</p></div>
      <p class="small"><strong>Silver Serpent:</strong> ST 13, DX 12, HT 12; HP 13; Basic Speed 6.00 (Move 6), Dodge 9; DR 2. Bite 1d-1 imp + <span class="pdf" data-page="32">poison p.32</span> (HT−3; 1 tox/min ×6). Tail 1d-1 cr. Uses <span class="pdf" data-page="25">All-Out Attack p.25-27</span> at times; fears fire.</p>
      <ul>
        <li><span class="pdf" data-page="25">Turn Sequence p.25</span>; pick maneuvers <span class="pdf" data-page="25">p.25-27</span>.</li>
        <li><span class="pdf" data-page="28">Dodge/Parry/Block p.28</span> (Dodge from <span class="pdf" data-page="6">p.6</span>).</li>
        <li>Apply <span class="pdf" data-page="29">DR & wounding modifiers p.29</span>.</li>
        <li>Injury thresholds <span class="pdf" data-page="29">p.29-30</span>; low FP penalties <span class="pdf" data-page="31">p.31</span>.</li>
        <li>After: <span class="pdf" data-page="30">First Aid p.30</span>.</li>
      </ul>
    </div>

    <div class="panel" id="I">
      <h2>I. Idol & Collapse <span class="pill">Encumbrance</span> <span class="pill">Jumping</span> <span class="pill">Falling</span></h2>
      <div class="readaloud"><p>The plinth’s idol (~15 lb) triggers a rumble when lifted.</p></div>
      <p>Spot seams: <span class="pdf" data-page="24">Vision p.24</span>. Flee 5 turns. Recalc <span class="pdf" data-page="22">Encumbrance p.22</span>. Gap (3 yd): <span class="pdf" data-page="14">Jumping (skill) p.14</span> / DX; distance rules <span class="pdf" data-page="23">p.23</span>. Fail → <span class="pdf" data-page="31">Fall p.31</span>, then <span class="pdf" data-page="22">Climb p.22</span>.</p>
    </div>

    <div class="panel" id="J">
      <h2>J. Exit & Return <span class="pill">Hiking</span> <span class="pill">Poison/Disease Cycles</span> <span class="pill">Reaction</span></h2>
      <p><span class="pdf" data-page="22">Hiking p.22-23</span> for the march. Finish poison cycles <span class="pdf" data-page="32">p.32</span>. Tomorrow’s disease cycles & remedies <span class="pdf" data-page="31">p.31-32</span>. Back in town: <span class="pdf" data-page="3">Reaction p.3</span> or <span class="pdf" data-page="24">Influence p.24</span>.</p>
    </div>
  </div>
</div>

<script>
  // ---------- PDF.js setup (render to canvas) ----------
  (function initPDF(){
    const errEl = document.getElementById('pdfError');
    const canvas = document.getElementById('pdfCanvas');
    const ctx = canvas.getContext('2d');
    let pdfDoc = null, currentPage = 1, totalPages = 0, scale = 1.2, rendering = false, pendingPage = null;

    function msg(t){ errEl.textContent = t; }
    function b64ToUint8Array(b64){ const bin = atob(b64); const len = bin.length; const bytes = new Uint8Array(len); for(let i=0;i<len;i++) bytes[i]=bin.charCodeAt(i); return bytes; }
    function fitWidth(page, desiredWidth){ const vp = page.getViewport({scale:1}); return desiredWidth / vp.width; }

    function renderPage(num, autoFit=false){
      rendering = true;
      pdfDoc.getPage(num).then(page=>{
        let useScale = scale;
        if(autoFit){
          const viewer = document.getElementById('viewer');
          const maxW = viewer.clientWidth - 22; // padding/border allowance
          useScale = Math.max(0.5, Math.min(2.8, fitWidth(page, maxW)));
          scale = useScale;
        }
        const viewport = page.getViewport({ scale: useScale });
        const dpr = window.devicePixelRatio || 1;
        canvas.width = Math.floor(viewport.width * dpr);
        canvas.height = Math.floor(viewport.height * dpr);
        canvas.style.width = Math.floor(viewport.width) + 'px';
        canvas.style.height = Math.floor(viewport.height) + 'px';
        const renderTask = page.render({
          canvasContext: ctx,
          viewport,
          transform: dpr !== 1 ? [dpr,0,0,dpr,0,0] : null
        });
        renderTask.promise.then(()=>{
          rendering = false;
          document.getElementById('pageInput').value = String(num);
          document.getElementById('pageCount').textContent = '/ ' + totalPages;
          if(pendingPage!==null){ const p = pendingPage; pendingPage=null; renderPage(p); }
        }).catch(e=>msg('Render error: '+e));
      }).catch(e=>msg('Page error: '+e));
    }
    function queueRender(num, autoFit=false){ if(rendering){ pendingPage=num; } else { renderPage(num, autoFit); } }
    function goTo(num, autoFit=false){ if(num<1 || num>totalPages) return; currentPage=num; queueRender(num, autoFit); }

    document.getElementById('prevBtn').addEventListener('click', ()=>goTo(Math.max(1,currentPage-1)));
    document.getElementById('nextBtn').addEventListener('click', ()=>goTo(Math.min(totalPages,currentPage+1)));
    document.getElementById('zoomIn').addEventListener('click', ()=>{ scale=Math.min(3,scale+0.15); goTo(currentPage); });
    document.getElementById('zoomOut').addEventListener('click', ()=>{ scale=Math.max(0.4,scale-0.15); goTo(currentPage); });
    document.getElementById('fitWidth').addEventListener('click', ()=>goTo(currentPage,true));
    document.getElementById('pageInput').addEventListener('change', e=>{ const v=parseInt(e.target.value,10); if(!isNaN(v)) goTo(v); });

    // adventure links
    document.querySelectorAll('.pdf[data-page]').forEach(el=>{
      el.addEventListener('click', ()=>{ const p=parseInt(el.getAttribute('data-page'),10); if(!isNaN(p)) goTo(p,true); });
      el.setAttribute('title', (el.textContent.trim()||'Open PDF')+' → page '+el.getAttribute('data-page'));
    });

    function start(pdfjsLib){
      pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdn.jsdelivr.net/npm/pdfjs-dist@3.11.174/build/pdf.worker.min.js';
      const data = b64ToUint8Array('__PDF_B64__');
      pdfjsLib.getDocument({data}).promise.then(doc=>{
        pdfDoc=doc; totalPages=doc.numPages; goTo(1,true);
      }).catch(e=>msg('Failed to load PDF: '+e));
    }
    const s=document.createElement('script');
    s.src='https://cdn.jsdelivr.net/npm/pdfjs-dist@3.11.174/build/pdf.min.js';
    s.onload=()=>start(window['pdfjsLib']);
    s.onerror=()=>msg('Could not load PDF.js from CDN.');
    document.head.appendChild(s);

    // ---------- Resizable Split Pane ----------
    const wrap = document.getElementById('splitWrap');
    const gutter = document.getElementById('gutter');

    let dragging=false, wrapRect=null, minPct=0, maxPct=100, lastPct=null, lastTap=0;

    function setSplit(pct){
      pct = Math.max(minPct, Math.min(maxPct, pct));
      wrap.style.setProperty('--left', pct+'%');
      wrap.style.setProperty('--right', (100 - pct)+'%');
      lastPct = pct;
      gutter.setAttribute('aria-valuenow', String(Math.round(pct)));
    }

    function pointerDown(e){
      dragging=true;
      gutter.classList.add('active');
      wrapRect = wrap.getBoundingClientRect();
      e.preventDefault();
    }
    function pointerMove(e){
      if(!dragging) return;
      const clientX = e.clientX ?? (e.touches && e.touches[0].clientX);
      if(typeof clientX !== 'number') return;
      const pct = ((clientX - wrapRect.left) / wrapRect.width) * 100;
      setSplit(pct);
    }
    function pointerUp(){
      if(!dragging) return;
      dragging=false;
      gutter.classList.remove('active');
      // After resizing, auto fit current page to new width for crispness
      goTo(currentPage, true);
    }

    // Pointer events (with touch fallback)
    if(window.PointerEvent){
      gutter.addEventListener('pointerdown', pointerDown);
      window.addEventListener('pointermove', pointerMove);
      window.addEventListener('pointerup', pointerUp);
      window.addEventListener('pointercancel', pointerUp);
    }else{
      gutter.addEventListener('mousedown', pointerDown);
      window.addEventListener('mousemove', pointerMove);
      window.addEventListener('mouseup', pointerUp);
      gutter.addEventListener('touchstart', pointerDown, {passive:false});
      window.addEventListener('touchmove', pointerMove, {passive:false});
      window.addEventListener('touchend', pointerUp);
      window.addEventListener('touchcancel', pointerUp);
    }

    // Double-click / double-tap to reset split
    gutter.addEventListener('dblclick', ()=>{ setSplit(46); goTo(currentPage,true); });
    gutter.addEventListener('touchend', (e)=>{
      const now=Date.now();
      if(now - lastTap < 350){ setSplit(46); goTo(currentPage,true); }
      lastTap = now;
    });

    // Initialize ARIA state
    gutter.setAttribute('aria-valuemin', String(minPct));
    gutter.setAttribute('aria-valuemax', String(maxPct));
    setSplit(46);
  })();
</script>
</body>
</html>
"""

html = html.replace("__PDF_B64__", pdf_b64).replace("__PDF_NAME__", pdf_path.name)

st.components.v1.html(html, height=900, scrolling=False)
st.caption("Drag the vertical bar to resize the panels. Double-click (or double-tap) the bar to reset.")
