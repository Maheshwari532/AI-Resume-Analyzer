const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const dzTitle = document.getElementById('dzTitle');
const dzSub = document.getElementById('dzSub');
const scanIcon = document.getElementById('scanIcon');
const analyzeBtn = document.getElementById('analyzeBtn');
const analyzeForm = document.getElementById('analyzeForm');
const errorMsg = document.getElementById('errorMsg');

const emptyState = document.getElementById('emptyState');
const loadingState = document.getElementById('loadingState');
const loadingText = document.getElementById('loadingText');
const report = document.getElementById('report');

const historyList = document.getElementById('historyList');
const historyEmpty = document.getElementById('historyEmpty');
const clearHistoryBtn = document.getElementById('clearHistoryBtn');

const HISTORY_KEY = 'scanline_history';
const HISTORY_LIMIT = 10;

let selectedFile = null;

// ---------- dropzone interactions ----------
dropzone.addEventListener('click', () => fileInput.click());
dropzone.setAttribute('tabindex', '0');
dropzone.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' || e.key === ' ') fileInput.click();
});

['dragenter', 'dragover'].forEach(evt => {
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.add('drag-over');
  });
});
['dragleave', 'drop'].forEach(evt => {
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.remove('drag-over');
  });
});
dropzone.addEventListener('drop', (e) => {
  const file = e.dataTransfer.files[0];
  if (file) handleFile(file);
});
fileInput.addEventListener('change', () => {
  if (fileInput.files[0]) handleFile(fileInput.files[0]);
});

function handleFile(file) {
  const allowed = ['pdf', 'docx', 'txt'];
  const ext = file.name.split('.').pop().toLowerCase();
  if (!allowed.includes(ext)) {
    showError('Please upload a PDF, DOCX, or TXT file.');
    return;
  }
  if (file.size > 4 * 1024 * 1024) {
    showError('File is too large. Max size is 4MB.');
    return;
  }
  selectedFile = file;
  errorMsg.textContent = '';
  dropzone.classList.add('has-file');
  dzTitle.textContent = file.name;
  dzSub.innerHTML = `${(file.size / 1024).toFixed(0)} KB · <span class="link">choose a different file</span>`;
  analyzeBtn.disabled = false;
}

function showError(msg) {
  errorMsg.textContent = msg;
}

// ---------- submit ----------
analyzeForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  if (!selectedFile) return;

  errorMsg.textContent = '';
  emptyState.classList.add('hidden');
  report.classList.add('hidden');
  loadingState.classList.remove('hidden');
  scanIcon.classList.add('scanning');
  analyzeBtn.disabled = true;

  const loadingMessages = ['Reading document...', 'Detecting sections...', 'Matching skills...', 'Scoring resume...'];
  let msgIndex = 0;
  loadingText.textContent = loadingMessages[0];
  const loadingInterval = setInterval(() => {
    msgIndex = (msgIndex + 1) % loadingMessages.length;
    loadingText.textContent = loadingMessages[msgIndex];
  }, 700);

  const formData = new FormData();
  formData.append('resume', selectedFile);
  formData.append('job_description', document.getElementById('jobDescription').value);

  try {
    const res = await fetch('/analyze', { method: 'POST', body: formData });
    const data = await res.json();

    clearInterval(loadingInterval);
    scanIcon.classList.remove('scanning');
    loadingState.classList.add('hidden');
    analyzeBtn.disabled = false;

    if (!res.ok) {
      showError(data.error || 'Something went wrong. Please try again.');
      emptyState.classList.remove('hidden');
      return;
    }

    renderReport(data);
    report.classList.remove('hidden');

    addToHistory({
      id: Date.now().toString(36) + Math.random().toString(36).slice(2, 6),
      filename: selectedFile.name,
      date: new Date().toISOString(),
      score: data.score,
      data: data,
    });
  } catch (err) {
    clearInterval(loadingInterval);
    scanIcon.classList.remove('scanning');
    loadingState.classList.add('hidden');
    emptyState.classList.remove('hidden');
    analyzeBtn.disabled = false;
    showError('Could not reach the server. Please try again.');
  }
});

// ---------- render ----------
function renderReport(data) {
  // Score dial
  const circumference = 326.7; // 2 * PI * 52
  const offset = circumference - (data.score / 100) * circumference;
  const dialFill = document.getElementById('dialFill');
  const scoreNumber = document.getElementById('scoreNumber');
  const scoreLabel = document.getElementById('scoreLabel');

  let color = '#3FE0C5';
  let label = 'Strong — ATS ready';
  if (data.score < 50) { color = '#FF6B6B'; label = 'Needs work — several gaps found'; }
  else if (data.score < 75) { color = '#F2B84B'; label = 'Decent — a few quick fixes away'; }

  requestAnimationFrame(() => {
    dialFill.style.stroke = color;
    dialFill.style.strokeDashoffset = offset;
  });
  animateNumber(scoreNumber, data.score);
  scoreLabel.textContent = label;
  scoreLabel.style.color = color;

  document.getElementById('wordCount').textContent = data.word_count;
  document.getElementById('bulletCount').textContent = data.bullets;
  document.getElementById('verbCount').textContent = data.action_verbs;

  // Contact + sections
  const contactList = document.getElementById('contactList');
  contactList.innerHTML = '';
  const contactItems = [
    ['Email address', !!data.contact.email],
    ['Phone number', !!data.contact.phone],
    ['LinkedIn profile', !!data.contact.linkedin],
  ];
  contactItems.forEach(([label, present]) => {
    contactList.appendChild(makeCheckItem(label, present));
  });

  const sectionList = document.getElementById('sectionList');
  sectionList.innerHTML = '';
  Object.entries(data.sections).forEach(([section, present]) => {
    sectionList.appendChild(makeCheckItem(section, present));
  });

  // Skills
  const skillsContent = document.getElementById('skillsContent');
  skillsContent.innerHTML = '';
  const skillEntries = Object.entries(data.skills || {});
  if (skillEntries.length === 0) {
    skillsContent.innerHTML = '<p class="muted">No recognized skills found. Consider adding a dedicated Skills section.</p>';
  } else {
    skillEntries.forEach(([category, skills]) => {
      const wrap = document.createElement('div');
      const title = document.createElement('div');
      title.className = 'skill-group-title';
      title.textContent = category;
      const chipRow = document.createElement('div');
      chipRow.className = 'chip-row';
      skills.forEach(s => {
        const chip = document.createElement('span');
        chip.className = 'chip';
        chip.textContent = s;
        chipRow.appendChild(chip);
      });
      wrap.appendChild(title);
      wrap.appendChild(chipRow);
      skillsContent.appendChild(wrap);
    });
  }

  // Job match
  const jdContent = document.getElementById('jdContent');
  jdContent.innerHTML = '';
  if (data.job_match) {
    const pct = data.job_match.match_percentage;
    const pctBlock = document.createElement('div');
    pctBlock.className = 'jd-match-pct';
    pctBlock.textContent = `${pct}%`;
    pctBlock.style.color = pct >= 75 ? '#3FE0C5' : pct >= 50 ? '#F2B84B' : '#FF6B6B';

    const bar = document.createElement('div');
    bar.className = 'jd-bar';
    const barFill = document.createElement('div');
    barFill.className = 'jd-bar-fill';
    barFill.style.width = '0%';
    bar.appendChild(barFill);

    jdContent.appendChild(pctBlock);
    const capLabel = document.createElement('div');
    capLabel.className = 'muted';
    capLabel.textContent = 'of key job description terms found in your resume';
    jdContent.appendChild(capLabel);
    jdContent.appendChild(bar);
    requestAnimationFrame(() => { barFill.style.width = `${pct}%`; });

    if (data.job_match.missing_keywords.length > 0) {
      const missingTitle = document.createElement('div');
      missingTitle.className = 'missing-kw-title';
      missingTitle.textContent = 'Missing keywords';
      jdContent.appendChild(missingTitle);
      const chipRow = document.createElement('div');
      chipRow.className = 'chip-row';
      data.job_match.missing_keywords.forEach(kw => {
        const chip = document.createElement('span');
        chip.className = 'chip';
        chip.style.color = '#FF6B6B';
        chip.style.borderColor = 'rgba(255,107,107,.3)';
        chip.style.background = 'rgba(255,107,107,.1)';
        chip.textContent = kw;
        chipRow.appendChild(chip);
      });
      jdContent.appendChild(chipRow);
    }
  } else {
    jdContent.innerHTML = '<p class="muted">Paste a job description to see keyword match.</p>';
  }

  // Fix list
  const fixList = document.getElementById('fixList');
  fixList.innerHTML = '';
  data.suggestions.forEach(tip => {
    const li = document.createElement('li');
    li.textContent = tip;
    fixList.appendChild(li);
  });
}

function makeCheckItem(label, present) {
  const li = document.createElement('li');
  if (!present) li.classList.add('missing');
  const mark = document.createElement('span');
  mark.className = 'mark ' + (present ? 'yes' : 'no');
  mark.textContent = present ? '✓' : '✕';
  li.appendChild(mark);
  li.appendChild(document.createTextNode(label));
  return li;
}

function animateNumber(el, target) {
  let current = 0;
  const step = Math.max(1, Math.round(target / 30));
  const interval = setInterval(() => {
    current += step;
    if (current >= target) {
      current = target;
      clearInterval(interval);
    }
    el.textContent = current;
  }, 20);
}

// ---------- history (localStorage) ----------
function loadHistory() {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (e) {
    return [];
  }
}

function saveHistoryArray(arr) {
  try {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(arr));
  } catch (e) {
    // storage full or unavailable — fail silently, history is a bonus feature
    console.warn('Could not save scan history:', e);
  }
}

function addToHistory(entry) {
  const history = loadHistory();
  history.unshift(entry);
  saveHistoryArray(history.slice(0, HISTORY_LIMIT));
  renderHistoryList(entry.id);
}

function deleteFromHistory(id) {
  const history = loadHistory().filter(item => item.id !== id);
  saveHistoryArray(history);
  renderHistoryList();
}

function scoreColor(score) {
  if (score < 50) return '#FF6B6B';
  if (score < 75) return '#F2B84B';
  return '#3FE0C5';
}

function formatHistoryDate(iso) {
  const d = new Date(iso);
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) +
    ' · ' + d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
}

function renderHistoryList(activeId) {
  const history = loadHistory();
  historyList.innerHTML = '';

  if (history.length === 0) {
    historyEmpty.classList.remove('hidden');
    return;
  }
  historyEmpty.classList.add('hidden');

  history.forEach(item => {
    const li = document.createElement('li');
    li.className = 'history-item' + (item.id === activeId ? ' active' : '');
    li.tabIndex = 0;

    const scoreCircle = document.createElement('div');
    scoreCircle.className = 'history-score';
    scoreCircle.textContent = item.score;
    const color = scoreColor(item.score);
    scoreCircle.style.color = color;
    scoreCircle.style.borderColor = color;

    const info = document.createElement('div');
    info.className = 'history-info';
    const nameEl = document.createElement('div');
    nameEl.className = 'history-filename';
    nameEl.textContent = item.filename;
    const dateEl = document.createElement('div');
    dateEl.className = 'history-date';
    dateEl.textContent = formatHistoryDate(item.date);
    info.appendChild(nameEl);
    info.appendChild(dateEl);

    const deleteBtn = document.createElement('button');
    deleteBtn.type = 'button';
    deleteBtn.className = 'history-delete';
    deleteBtn.setAttribute('aria-label', `Remove ${item.filename} from history`);
    deleteBtn.textContent = '✕';
    deleteBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      deleteFromHistory(item.id);
    });

    li.addEventListener('click', () => {
      emptyState.classList.add('hidden');
      loadingState.classList.add('hidden');
      report.classList.remove('hidden');
      renderReport(item.data);
      document.querySelectorAll('.history-item').forEach(el => el.classList.remove('active'));
      li.classList.add('active');
    });
    li.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') li.click();
    });

    li.appendChild(scoreCircle);
    li.appendChild(info);
    li.appendChild(deleteBtn);
    historyList.appendChild(li);
  });
}

clearHistoryBtn.addEventListener('click', () => {
  if (loadHistory().length === 0) return;
  if (confirm('Clear all scan history? This cannot be undone.')) {
    saveHistoryArray([]);
    renderHistoryList();
  }
});

// initial paint
renderHistoryList();
