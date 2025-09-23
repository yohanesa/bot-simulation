from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/admin", tags=["admin-ui"]) 

HTML = """
<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>StreamingServer — Admin</title>
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 24px; }
    .wrap { display: grid; grid-template-columns: 1fr; gap: 16px; }
    .card { border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px; box-shadow: 0 2px 8px rgba(0,0,0,.04); }
    h1 { margin-top: 0; }
    table { width: 100%; border-collapse: collapse; }
    th, td { text-align: left; padding: 8px; border-bottom: 1px solid #eee; }
    .bar { height: 10px; background: #e5e7eb; border-radius: 6px; overflow: hidden; }
    .bar > div { height: 100%; background: #60a5fa; width: 0%; }
    .muted { color: #6b7280; }
    .row { display: flex; gap: 12px; align-items: center; }
    button { padding: 6px 10px; border: 1px solid #ddd; border-radius: 8px; background: #fafafa; cursor: pointer; }
  </style>
</head>
<body>
  <h1>StreamingServer — Admin</h1>
  <div class=\"wrap\">
    <div class=\"card\">
      <div class=\"row\">
        <h2 style=\"margin:0\">Metrics</h2>
        <button id=\"refresh\">Refresh</button>
        <span class=\"muted\" id=\"ts\"></span>
      </div>
      <div id=\"metrics\"></div>
    </div>

    <div class=\"card\">
      <h2 style=\"margin:0 0 8px 0\">Nodes</h2>
      <table id=\"nodes\"></table>
    </div>
  </div>

<script>
const $ = (sel) => document.querySelector(sel);
const f = (n) => typeof n === 'number' ? n.toFixed(2) : n;

async function load() {
  const [mres, nres] = await Promise.all([
    fetch('/admin/metrics'),
    fetch('/admin/nodes')
  ]);
  const m = await mres.json();
  const n = await nres.json();
  renderMetrics(m);
  renderNodes(n.nodes || n);
  $('#ts').textContent = new Date().toLocaleTimeString();
}

function renderMetrics(m){
  $('#metrics').innerHTML = `
    <div style=\"display:grid;grid-template-columns:repeat(3,1fr);gap:12px\">
      <div><div class=\"muted\">Active Sessions</div><div style=\"font-size:24px\">${m.active_sessions}</div></div>
      <div><div class=\"muted\">Nodes</div><div style=\"font-size:24px\">${m.nodes}</div></div>
      <div><div class=\"muted\">Events Emitted</div><div style=\"font-size:24px\">${m.events_emitted}</div></div>
      <div><div class=\"muted\">Scale Up</div><div style=\"font-size:24px\">${m.scale_up_count}</div></div>
      <div><div class=\"muted\">Scale Down</div><div style=\"font-size:24px\">${m.scale_down_count}</div></div>
      <div><div class=\"muted\">Ticks Running</div><div style=\"font-size:24px\">${m.ticks_running}</div></div>
    </div>`;
}

function renderNodes(nodes){
  const rows = (nodes || []).map(n => {
    const util = Math.min(100, Math.round((n.utilization || (n.active_sessions / Math.max(1, n.capacity))) * 100));
    return `
      <tr>
        <td style=\"width:80px\"><b>#${n.node_id}</b></td>
        <td>cap ${n.capacity}</td>
        <td>${n.active_sessions} active</td>
        <td style=\"width:50%\">
          <div class=\"bar\"><div style=\"width:${util}%\"></div></div>
          <span class=\"muted\">${util}%</span>
        </td>
      </tr>`
  }).join('');
  $('#nodes').innerHTML = `<tr><th>Node</th><th>Capacity</th><th>Active</th><th>Utilization</th></tr>${rows}`;
}

$('#refresh').onclick = load;
setInterval(load, 2000);
load();
</script>
</body>
</html>"""

@router.get("/ui")
async def admin_ui():
    return HTMLResponse(HTML)