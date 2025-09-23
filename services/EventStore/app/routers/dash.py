from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

HTML = """
<!doctype html><meta charset="utf-8"><title>EventStore Dash</title>
<style>body{font-family:system-ui;margin:20px} table{border-collapse:collapse} th,td{padding:6px 10px;border-bottom:1px solid #eee}</style>
<h1>EventStore – Dashboard</h1>
<button id="refresh">Refresh</button> <span id="ts"></span>
<h2>Overview (5 min)</h2><pre id="ov"></pre>
<h2>Top Videos (60 min)</h2><pre id="tv"></pre>
<h2>RPM by minute (30 min)</h2><pre id="rpm"></pre>
<script>
async function load(){
  const [a,b,c]=await Promise.all([
    fetch('/stats/overview?minutes=5').then(r=>r.json()),
    fetch('/stats/top-videos?minutes=60').then(r=>r.json()),
    fetch('/stats/rpm?minutes=30').then(r=>r.json()),
  ]);
  document.getElementById('ov').textContent = JSON.stringify(a, null, 2);
  document.getElementById('tv').textContent = JSON.stringify(b, null, 2);
  document.getElementById('rpm').textContent = JSON.stringify(c, null, 2);
  document.getElementById('ts').textContent = new Date().toLocaleTimeString();
}
document.getElementById('refresh').onclick = load;
setInterval(load, 3000); load();
</script>
"""
@router.get("/dash")
def dash():
    return HTMLResponse(HTML)
