const commandInput = document.querySelector('#commandInput');
const errorInput = document.querySelector('#errorInput');
const modelSelect = document.querySelector('#modelSelect');
const modelStatus = document.querySelector('#modelStatus');
const statusText = document.querySelector('#statusText');
const analyzeButton = document.querySelector('#analyzeButton');
const message = document.querySelector('#message');
const resultPanel = document.querySelector('#resultPanel');
const resultContent = document.querySelector('#resultContent');
const HISTORY_KEY = 'phantomshell.history.v1';
const HISTORY_ENABLED_KEY = 'phantomshell.history-enabled.v1';
const HISTORY_LIMIT = 12;
function historyEnabled() {
  try { return localStorage.getItem(HISTORY_ENABLED_KEY) === 'true'; }
  catch { return false; }
}

function readHistory() {
  try {
    const value = JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]');
    return Array.isArray(value) ? value.filter(item => item && typeof item.analysis === 'string') : [];
  } catch { return []; }
}

function saveHistory(item) {
  if (!historyEnabled()) return;
  try { localStorage.setItem(HISTORY_KEY, JSON.stringify([item, ...readHistory()].slice(0, HISTORY_LIMIT))); }
  catch { showMessage('Analysis worked, but this browser could not save local history.'); }
}

function showMessage(text) {
  message.textContent = text;
  message.hidden = false;
}

function updateCount() {
  const total = commandInput.value.length + errorInput.value.length;
  document.querySelector('#charCount').textContent = `${total.toLocaleString()} / 25,000`;
  document.querySelector('#charCount').classList.toggle('over-limit', total > 25000);
}

async function refreshModels() {
  modelStatus.className = 'status-pill';
  statusText.textContent = 'Connecting';
  try {
    const response = await fetch('/api/status');
    const data = await response.json();
    if (!response.ok || !data.available) throw new Error(data.error || 'Ollama is unavailable.');
    modelSelect.replaceChildren();
    if (!data.models.length) {
      modelSelect.add(new Option('No models installed', ''));
      modelSelect.disabled = true;
      modelStatus.classList.add('offline');
      statusText.textContent = 'No models found';
      return;
    }
    for (const name of data.models) modelSelect.add(new Option(name, name));
    modelSelect.disabled = false;
    modelStatus.classList.add('online');
    statusText.textContent = `${data.models.length} model${data.models.length === 1 ? '' : 's'} ready`;
  } catch (error) {
    modelSelect.replaceChildren(new Option('Ollama unavailable', ''));
    modelSelect.disabled = true;
    modelStatus.classList.add('offline');
    statusText.textContent = 'Offline';
    showMessage(`${error.message} Start Ollama and reload this page.`);
  }
}

async function analyzeInput() {
  message.hidden = true;
  const command = commandInput.value.trim();
  const error = errorInput.value.trim();
  if (!command && !error) { showMessage('Paste a command, an error message, or both to get started.'); return; }
  if (command.length > 15000 || error.length > 15000 || command.length + error.length > 25000) {
    showMessage('Keep each field under 15,000 characters and the combined input under 25,000.'); return;
  }
  if (!modelSelect.value) { showMessage('No Ollama model is selected. Start Ollama, install a model, then refresh this page.'); return; }
  analyzeButton.disabled = true;
  document.querySelector('#buttonLabel').textContent = 'Reading the runes…';
  try {
    const response = await fetch('/api/analyze', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command, error, model: modelSelect.value, spooky: document.querySelector('#spookyToggle').checked })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'The analysis could not be completed.');
    resultContent.textContent = data.analysis;
    resultPanel.hidden = false;
    resultPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    saveHistory({ command, error, model: modelSelect.value, analysis: data.analysis, createdAt: Date.now() });
    renderHistory();
  } catch (error) { showMessage(error.message); }
  finally { analyzeButton.disabled = false; document.querySelector('#buttonLabel').textContent = 'Summon an explanation'; }
}

function renderHistory() {
  const list = document.querySelector('#historyList');
  list.replaceChildren();
  const history = readHistory();
  if (!history.length) {
    const empty = document.createElement('div'); empty.className = 'history-empty';
    empty.textContent = historyEnabled()
      ? 'No séances yet. Your saved analyses will appear here.'
      : 'History is off. Turn it on below to keep future analyses on this device.';
    list.append(empty); return;
  }
  history.forEach((item, index) => {
    const card = document.createElement('button'); card.type = 'button'; card.className = 'history-item';
    const time = document.createElement('div'); time.className = 'history-time';
    time.textContent = new Date(item.createdAt || Date.now()).toLocaleString();
    const title = document.createElement('div'); title.className = 'history-title';
    title.textContent = (item.command || item.error || 'Terminal analysis').split('\n')[0];
    card.append(time, title);
    card.addEventListener('click', () => { resultContent.textContent = item.analysis; resultPanel.hidden = false; closeDrawer(); });
    list.append(card);
  });
}

function openDrawer() {
  document.querySelector('#historyEnabled').checked = historyEnabled();
  renderHistory(); document.querySelector('#historyDrawer').classList.add('open');
  document.querySelector('#historyDrawer').setAttribute('aria-hidden', 'false'); document.querySelector('#backdrop').classList.add('visible');
}
function closeDrawer() {
  document.querySelector('#historyDrawer').classList.remove('open');
  document.querySelector('#historyDrawer').setAttribute('aria-hidden', 'true'); document.querySelector('#backdrop').classList.remove('visible');
}

document.querySelector('#analyzeButton').addEventListener('click', analyzeInput);
document.querySelector('#historyToggle').addEventListener('click', openDrawer);
document.querySelector('#closeHistory').addEventListener('click', closeDrawer);
document.querySelector('#backdrop').addEventListener('click', closeDrawer);
document.querySelector('#clearHistory').addEventListener('click', () => {
  try { localStorage.removeItem(HISTORY_KEY); renderHistory(); }
  catch { showMessage('This browser could not access local history.'); }
});
document.querySelector('#historyEnabled').addEventListener('change', event => {
  try { localStorage.setItem(HISTORY_ENABLED_KEY, String(event.currentTarget.checked)); renderHistory(); }
  catch { event.currentTarget.checked = false; showMessage('This browser could not update local history settings.'); }
});
document.querySelector('#copyButton').addEventListener('click', async event => {
  try { await navigator.clipboard.writeText(resultContent.textContent); event.currentTarget.textContent = 'COPIED'; setTimeout(() => { event.currentTarget.textContent = 'COPY'; }, 1400); }
  catch { showMessage('Clipboard access was denied. Select and copy the diagnosis manually.'); }
});
commandInput.addEventListener('input', updateCount);
errorInput.addEventListener('input', updateCount);
refreshModels();
