# app.py
# Streamlit app: The Tomb of the Silver Serpent (PDF viewer with reliable jump-to-page)
# Put "GURPS 4e - Lite.pdf" in the same folder as this file (or change the name in the sidebar).

import base64
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="The Tomb of the Silver Serpent — GURPS Lite Viewer", layout="wide")

st.sidebar.title("Settings")
pdf_filename = st.sidebar.text_input("PDF file name:", value="GURPS 4e - Lite.pdf")

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
<style>
  :root{--bg:#0e0f12; --panel:#151821; --ink:#e7ecf3; --muted:#b7c3d6; --accent:#79b8ff; --accent2:#a4f9c8; --pill:#1e2430; --pill-border:#2a3142; --link:#9ed0ff;}
  html,body{background:var(--bg); color:var(--ink); margin:0; font-family:system-ui,-apple-system,Segoe UI,Roboto,Inter,Helvetica,Arial,sans-serif; line-height:1.55}
  .wrap{display:grid; grid-template-columns: 44% 56%; gap:16px; height:100vh; box-sizing:border-box; padding:12px}
  .viewer{position:sticky; top:0; height:calc(100vh - 24px); background:#0b0c10; border:1px solid #222839; border-radius:12px; overflow:hidden}
  .viewer iframe{width:100%; height:100%; border:0}
  .right{overflow:auto; padding-right:6px}
  h1{font-size:1.5rem; margin:.2rem 0 .7rem}
  h2{font-size:1.2rem; margin:1.2rem 0 .4rem}
  h3{font-size:1.02rem; margin:1rem 0 .3rem; color:var(--muted)}
  p{margin:.5rem 0}
  .panel{background:var(--panel); border:1px solid #222839; border-radius:14px; padding:14px 16px; margin:10px 0}
  .readaloud{border-left:4px solid var(--accent2); background:#182028; padding:10px 12px; border-radius:10px}
  .pill{display:inline-block; background:var(--pill); border:1px solid var(--pill-border); border-radius:999px; padding:.18rem .55rem; margin:.12rem .2rem; font-size:.86rem; color:var(--muted)}
  a.pdf{color:var(--link); text-decoration:none; border-bottom:1px dotted #3b5b7c; cursor:pointer}
  a.pdf:hover{text-decoration:underline}
  .small{font-size:.92rem; color:var(--muted)}
  .map{white-space:nowrap; overflow:auto}
  .kbd{font-family:ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; background:#212634; border:1px solid #2a3142; padding:.08rem .4rem; border-radius:6px}
</style>
</head>
<body>
<div class="wrap">
  <div class="viewer">
    <iframe id="pdfFrame" src="about:blank"></iframe>
  </div>

  <div class="right">
    <h1>The Tomb of the Silver Serpent <span class="small">— GURPS Lite Quick-Links</span></h1>
    <p class="small">Click any blue keyword to jump the PDF viewer on the left. Using: <span class="kbd">{PDF_NAME}</span></p>

    <div class="panel">
      <p class="small">You are a novice delver sent to recover the Silver Serpent Idol from an old hill-tomb.</p>
      <div class="map small"><strong>Flow:</strong> A. Village → B. Sink-Stairs → C. Whispering Antechamber → D. Hall of Echoes → E. Barred Door &amp; Crawl → F. Ember Room → G. Prisoner → H. Serpent Shrine → I. Idol &amp; Collapse → J. Exit</div>
    </div>

    <div class="panel">
      <h3>Quick-Start Character</h3>
      <p><strong>Rowan</strong> — ST 11, DX 12, IQ 11, HT 11; HP 11, FP 11; Basic Speed 5.75, Move 5, Dodge 8 (<a class="pdf" data-page="6">Secondary &amp; Dodge p.6</a>).</p>
      <p><strong>Advantage:</strong> <a class="pdf" data-page="9">Combat Reflexes p.9</a></p>
      <p><strong>Skills:</strong>
        Broadsword-13; Shield-12 (<a class="pdf" data-page="14">Melee Weapons p.14-15</a>);
        <a class="pdf" data-page="22">Climbing p.22</a>; Stealth (<a class="pdf" data-page="13">Skill list p.13-16</a>);
        <a class="pdf" data-page="30">First Aid p.30</a>; <a class="pdf" data-page="14">Lockpicking p.14</a>;
        <a class="pdf" data-page="22">Hiking p.22-23</a>;
        Diplomacy / Fast-Talk / Intimidation (<a class="pdf" data-page="24">Influence p.24</a>);
        Jumping (<a class="pdf" data-page="14">skill p.14</a>; <a class="pdf" data-page="23">rules p.23</a>).
      </p>
      <p><strong>Kit:</strong> Light armor (<a class="pdf" data-page="18">DR p.18-19</a>), rope, torches, picks, bandages. Track <a class="pdf" data-page="22">Encumbrance &amp; Move p.22</a>.</p>
    </div>

    <div class="panel" id="A">
      <h2>A. Village Edge <span class="pill">Reaction</span> <span class="pill">Influence</span></h2>
      <div class="readaloud"><p>Old Maera meets you by a standing stone: “Bring back the idol and hush the hill.”</p></div>
      <p>Roll <a class="pdf" data-page="3">Reaction p.3</a> or use an <a class="pdf" data-page="24">Influence roll p.24</a> as a <a class="pdf" data-page="3">Quick Contest p.3</a>.</p>
      <p class="small">Optional trail: <a class="pdf" data-page="22">Hiking p.22-23</a> · Fatigue basics <a class="pdf" data-page="31">p.31</a></p>
    </div>

    <div class="panel" id="B">
      <h2>B. Sink-Stairs <span class="pill">Climbing</span> <span class="pill">Encumbrance</span> <span class="pill">Falling</span></h2>
      <div class="readaloud"><p>Collapsed stone stairs spiral into dark.</p></div>
      <p>Tie rope; roll <a class="pdf" data-page="22">Climbing p.22</a> (start; then each 5 min). Apply <a class="pdf" data-page="22">Encumbrance p.22</a>. Failure → <a class="pdf" data-page="31">Falling p.31</a>; Jumping help <a class="pdf" data-page="23">p.23</a>.</p>
    </div>

    <div class="panel" id="C">
      <h2>C. Whispering Antechamber <span class="pill">Perception</span> <span class="pill">Fright</span></h2>
      <div class="readaloud"><p>Faint sibilant whispers drift from ahead.</p></div>
      <p><a class="pdf" data-page="24">Hearing p.24</a> to parse. Then a chill passes—make a <a class="pdf" data-page="24">Fright Check p.24</a> (+2 if <a class="pdf" data-page="9">Combat Reflexes p.9</a>).</p>
    </div>

    <div class="panel" id="D">
      <h2>D. Hall of Echoes <span class="pill">Stealth vs Hearing</span> <span class="pill">Maneuvers</span></h2>
      <div class="readaloud"><p>The ceiling is webbed with bats.</p></div>
      <p>Use Stealth vs. <a class="pdf" data-page="24">Hearing p.24</a> as a <a class="pdf" data-page="3">Quick Contest p.3</a>. If swarmed, consider <a class="pdf" data-page="25">All-Out Defense p.25-27</a>.</p>
    </div>

    <div class="panel" id="E">
      <h2>E. Barred Door &amp; Crawl <span class="pill">Lockpicking</span> <span class="pill">Contests</span> <span class="pill">Poison</span></h2>
      <div class="readaloud"><p>Cold air hisses through iron bars. A wall crack beckons.</p></div>
      <ul>
        <li><strong>Pick:</strong> <a class="pdf" data-page="14">Lockpicking p.14</a>; spot trap with <a class="pdf" data-page="24">Vision p.24</a>. Fail &amp; prick → <a class="pdf" data-page="32">Poison p.32</a>.</li>
        <li><strong>Force:</strong> your ST as a <a class="pdf" data-page="3">Quick Contest p.3</a> vs Door 13 (crit fail: lose FP <a class="pdf" data-page="31">p.31</a>).</li>
        <li><strong>Crawl:</strong> <a class="pdf" data-page="24">Vision p.24</a> + <a class="pdf" data-page="22">Climbing p.22</a> (Flexibility helps <a class="pdf" data-page="9">p.9</a>); back out with <a class="pdf" data-page="25">Ready p.25-27</a>.</li>
      </ul>
    </div>

    <div class="panel" id="F">
      <h2>F. Ember Room <span class="pill">Flame</span> <span class="pill">Heat</span> <span class="pill">Fatigue</span></h2>
      <div class="readaloud"><p>Four braziers and a serpent relief with four fire-icons.</p></div>
      <p>Flame hurts: <a class="pdf" data-page="32">Flame p.32</a> (ignite; put out with <a class="pdf" data-page="25">Ready p.25-27</a>). Heat drains FP: <a class="pdf" data-page="32">Heat p.32</a>, <a class="pdf" data-page="31">Fatigue p.31</a>.</p>
    </div>

    <div class="panel" id="G">
      <h2>G. Prisoner <span class="pill">First Aid</span> <span class="pill">Disease</span> <span class="pill">Reaction</span></h2>
      <div class="readaloud"><p>Tavi, a sickly tomb-robber, pleads for help.</p></div>
      <p><a class="pdf" data-page="3">Reaction p.3</a> or <a class="pdf" data-page="24">Influence p.24</a>. Spores as <a class="pdf" data-page="31">Disease p.31-32</a>. Treat with <a class="pdf" data-page="30">First Aid p.30</a>.</p>
    </div>

    <div class="panel" id="H">
      <h2>H. Serpent Shrine <span class="pill">Combat</span> <span class="pill">Defenses</span> <span class="pill">Damage &amp; DR</span> <span class="pill">Poison</span></h2>
      <div class="readaloud"><p>Scales rustle around a coiled stone idol…</p></div>
      <p class="small"><strong>Silver Serpent:</strong> ST 13, DX 12, HT 12; HP 13; Basic Speed 6.00 (Move 6), Dodge 9; DR 2. Bite 1d-1 imp + <a class="pdf" data-page="32">poison p.32</a> (HT−3; 1 tox/min ×6). Tail 1d-1 cr. Uses <a class="pdf" data-page="25">All-Out Attack p.25-27</a> at times; fears fire.</p>
      <ul>
        <li><a class="pdf" data-page="25">Turn Sequence p.25</a>; pick maneuvers <a class="pdf" data-page="25">p.25-27</a>.</li>
        <li><a class="pdf" data-page="28">Dodge/Parry/Block p.28</a> (Dodge from <a class="pdf" data-page="6">p.6</a>).</li>
        <li>Apply <a class="pdf" data-page="29">DR &amp; wounding modifiers p.29</a>.</li>
        <li>Injury thresholds <a class="pdf" data-page="29">p.29-30</a>; low FP penalties <a class="pdf" data-page="31">p.31</a>.</li>
        <li>After: <a class="pdf" data-page="30">First Aid p.30</a>.</li>
      </ul>
    </div>

    <div class="panel" id="I">
      <h2>I. Idol &amp; Collapse <span class="pill">Encumbrance</span> <span class="pill">Jumping</span> <span class="pill">Falling</span></h2>
      <div class="readaloud"><p>The plinth’s idol (~15 lb) triggers a rumble when lifted.</p></div>
      <p>Spot seams: <a class="pdf" data-page="24">Vision p.24</a>. Flee 5 turns. Recalc <a class="pdf" data-page="22">Encumbrance p.22</a>. Gap (3 yd): <a class="pdf" data-page="14">Jumping (skill) p.14</a> / DX; distance rules <a class="pdf" data-page="23">p.23</a>. Fail → <a class="pdf" data-page="31">Fall p.31</a>, then <a class="pdf" data-page="22">Climb p.22</a>.</p>
    </div>

    <div class="panel" id="J">
      <h2>J. Exit &amp; Return <span class="pill">Hiking</span> <span class="pill">Poison/Disease Cycles</span> <span class="pill">Reaction</span></h2>
      <p><a class="pdf" data-page="22">Hiking p.22-23</a> for the march. Finish poison cycles <a class="pdf" data-page="32">p.32</a>. Tomorrow’s disease cycles &amp; remedies <a class="pdf" data-page="31">p.31-32</a>. Back in town: <a class="pdf" data-page="3">Reaction p.3</a> or <a class="pdf" data-page="24">Influence p.24</a>.</p>
    </div>
  </div>
</div>

<script>
  // --- Build a Blob URL from the base64 PDF (reliable with #page= jumps) ---
  const b64 = "__PDF_B64__";
  function b64ToBlobUrl(b64Data, contentType="application/pdf") {
    const byteChars = atob(b64Data);
    const byteNums = new Array(byteChars.length);
    for (let i=0; i<byteChars.length; i++) byteNums[i] = byteChars.charCodeAt(i);
    const byteArray = new Uint8Array(byteNums);
    const blob = new Blob([byteArray], {type: contentType});
    return URL.createObjectURL(blob);
  }
  const blobURL = b64ToBlobUrl(b64);

  const frame = document.getElementById('pdfFrame');

  function setPage(p){
    // Force a refresh so some viewers re-parse the #page fragment.
    frame.src = "about:blank";
    setTimeout(() => {
      frame.src = blobURL + "#page=" + encodeURIComponent(p);
    }, 50);
  }

  // Initial page
  setPage(1);

  // Wire all keyword links
  document.querySelectorAll('a.pdf').forEach(a => {
    const p = a.getAttribute('data-page') || "";
    a.addEventListener('click', (e) => {
      e.preventDefault();
      if (p) setPage(p);
    }, false);
    a.title = (a.textContent.trim() || "Open PDF") + (p ? " → page " + p : "");
  });
</script>
</body>
</html>
"""

html = html.replace("__PDF_B64__", pdf_b64).replace("{PDF_NAME}", pdf_filename)

st.components.v1.html(html, height=900, scrolling=False)
st.caption("Click any blue keyword to jump the PDF. If Safari still ignores jumps, try Chrome/Edge/Firefox.")
