const drop = document.getElementById('drop');
const fileInput = document.getElementById('file');
const preview = document.getElementById('preview');
const dropInner = document.getElementById('dropInner');
const btn = document.getElementById('btn');
const statusEl = document.getElementById('status');
const resultEl = document.getElementById('result');
let currentFile = null;

drop.addEventListener('click', () => fileInput.click());
['dragover','dragenter'].forEach(ev => drop.addEventListener(ev, e => {
  e.preventDefault(); drop.classList.add('drag');
}));
['dragleave','drop'].forEach(ev => drop.addEventListener(ev, e => {
  e.preventDefault(); drop.classList.remove('drag');
}));
drop.addEventListener('drop', e => { if (e.dataTransfer.files[0]) setFile(e.dataTransfer.files[0]); });
fileInput.addEventListener('change', () => { if (fileInput.files[0]) setFile(fileInput.files[0]); });

function setFile(f) {
  if (!f.type.startsWith('image/')) { showError('File harus berupa gambar.'); return; }
  currentFile = f;
  const url = URL.createObjectURL(f);
  preview.src = url; preview.hidden = false; dropInner.hidden = true;
  btn.disabled = false;
  resultEl.hidden = true; statusEl.hidden = true;
}

btn.addEventListener('click', predict);

async function predict() {
  if (!currentFile) return;
  btn.disabled = true;
  resultEl.hidden = true;
  showStatus('<span class="spin"></span>Lagi mikir... inference CNN jalan di server PHP (bisa beberapa detik).');
  const fd = new FormData();
  fd.append('file', currentFile);
  try {
    const t0 = performance.now();
    const res = await fetch('predict.php', { method: 'POST', body: fd });
    const data = await res.json();
    if (!res.ok) { showError(data.error || 'Gagal memproses.'); btn.disabled = false; return; }
    render(data, performance.now() - t0);
  } catch (err) {
    showError('Gagal konek ke server: ' + err.message);
  }
  btn.disabled = false;
}

function render(d, clientMs) {
  statusEl.hidden = true;
  document.getElementById('topClass').textContent = d.prediction;
  document.getElementById('topConf').textContent = (d.confidence * 100).toFixed(1) + '% yakin';
  const bars = document.getElementById('bars');
  bars.innerHTML = '';
  d.top_k.forEach(item => {
    const pct = (item.confidence * 100).toFixed(1);
    const row = document.createElement('div');
    row.className = 'bar-row';
    row.innerHTML = `<div class="bar-name">${item.class}</div>
      <div class="bar-track"><div class="bar-fill"></div></div>
      <div class="bar-val">${pct}%</div>`;
    bars.appendChild(row);
    requestAnimationFrame(() => row.querySelector('.bar-fill').style.width = pct + '%');
  });
  document.getElementById('meta').textContent =
    `Model: ${d.model} · ${d.input_size}px · inference ${d.elapsed_ms} ms`;
  resultEl.hidden = false;
}

function showStatus(html){ statusEl.className='status'; statusEl.innerHTML=html; statusEl.hidden=false; }
function showError(msg){ statusEl.className='status err'; statusEl.textContent='⚠ '+msg; statusEl.hidden=false; }
