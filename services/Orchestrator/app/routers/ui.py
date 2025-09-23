from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

HTML = """
<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Orchestrator UI</title>
  <style>
    body { font-family: system-ui, sans-serif; margin: 24px; }
    .card { border: 1px solid #ddd; border-radius: 12px; padding: 16px; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,.04); }
    label { display:block; font-weight:600; margin: 8px 0 4px; }
    input[type=number], input[type=range] { width: 100%; }
    button { padding: 8px 14px; border-radius: 10px; border: 1px solid #ccc; background: #fafafa; cursor: pointer; }
    button:hover { background: #f3f3f3; }
    .row { display:flex; gap:12px; flex-wrap:wrap; }
  </style>
</head>
<body>
  <h1>Orchestrator</h1>

  <div class=\"card\">
    <h2>Config</h2>
    <label>height <span id=\"h_val\"></span></label>
    <input id=\"height\" type=\"range\" min=\"1\" max=\"200\" value=\"5\" />

    <label>width <span id=\"w_val\"></span></label>
    <input id=\"width\" type=\"range\" min=\"1\" max=\"300\" value=\"10\" />

    <label>error_factor (0..1) <span id=\"e_val\"></span></label>
    <input id=\"error\" type=\"range\" min=\"0\" max=\"1\" step=\"0.01\" value=\"0\" />

    <div style=\"margin-top:10px\" class=\"row\">
      <button id=\"save_cfg\">Save Config</button>
      <button id=\"pulse\">Pulse Once</button>
    </div>
    <pre id=\"cfg_out\"></pre>
  </div>

  <div class=\"card\">
    <h2>Loop</h2>
    <label>interval_ms</label>
    <input id=\"interval\" type=\"number\" min=\"100\" value=\"1000\" />
    <div style=\"margin-top:10px\" class=\"row\">
      <button id=\"set_interval\">Set Interval</button>
      <button id=\"start\">Start</button>
      <button id=\"stop\">Stop</button>
      <button id=\"status\">Status</button>
    </div>
    <pre id=\"loop_out\"></pre>
  </div>

  <div class=\"card\">
    <h2>Metrics</h2>
    <button id=\"metrics\">Get Metrics</button>
    <pre id=\"metrics_out\"></pre>
  </div>

<script>
const api = (p, opts={}) => fetch(p, {headers:{'Content-Type':'application/json'}, ...opts}).then(r=>r.json());

const $ = (id) => document.getElementById(id);

const syncLabels = () => {
  $("h_val").textContent = $("height").value;
  $("w_val").textContent = $("width").value;
  $("e_val").textContent = $("error").value;
};
["height","width","error"].forEach(id=> $(id).addEventListener('input', syncLabels));
syncLabels();

$("save_cfg").onclick = async () => {
  const body = JSON.stringify({
    height: parseInt($("height").value,10),
    width: parseInt($("width").value,10),
    error_factor: parseFloat($("error").value)
  });
  const res = await api('/config', {method:'POST', body});
  $("cfg_out").textContent = JSON.stringify(res, null, 2);
};

$("pulse").onclick = async () => {
  const res = await api('/pulse', {method:'POST', body: JSON.stringify({})});
  $("cfg_out").textContent = JSON.stringify(res, null, 2);
};

$("set_interval").onclick = async () => {
  const body = JSON.stringify({}); // query param style
  const ms = parseInt($("interval").value,10);
  const res = await api(`/loop/interval?interval_ms=${ms}`, {method:'POST', body});
  $("loop_out").textContent = JSON.stringify(res, null, 2);
};

$("start").onclick = async () => {
  const res = await api('/loop/start', {method:'POST', body: JSON.stringify({})});
  $("loop_out").textContent = JSON.stringify(res, null, 2);
};

$("stop").onclick = async () => {
  const res = await api('/loop/stop', {method:'POST', body: JSON.stringify({})});
  $("loop_out").textContent = JSON.stringify(res, null, 2);
};

$("status").onclick = async () => {
  const res = await api('/loop/status');
  $("loop_out").textContent = JSON.stringify(res, null, 2);
};

$("metrics").onclick = async () => {
  const res = await api('/metrics');
  $("metrics_out").textContent = JSON.stringify(res, null, 2);
};
</script>
</body>
</html>
"""

@router.get("/ui")
async def ui():
    return HTMLResponse(HTML)