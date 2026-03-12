/* ═══════════════════════════════════════════════════════════
   Recorder Page — Audio Recording & Hinglish Transcription
   Aliens Company · Vikas Nayak · 2026
   ═══════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  /* ── Feature Detection ── */
  var HAS_RECORDER = typeof MediaRecorder !== 'undefined';
  var HAS_SPEECH = !!(window.SpeechRecognition || window.webkitSpeechRecognition);
  var HAS_MIC = !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);

  /* ── IndexedDB Config ── */
  var DB_NAME = 'aliens_recorder';
  var DB_VER = 1;
  var STORE = 'recordings';

  /* ── DOM refs ── */
  function $(id) { return document.getElementById(id); }
  var els = {};

  function queryEls() {
    els = {
    totalCount:     $('rcTotalCount'),
    totalDuration:  $('rcTotalDuration'),
    todayCount:     $('rcTodayCount'),
    todayDate:      $('rcTodayDate'),
    timer:          $('rcTimer'),
    canvas:         $('rcWaveform'),
    waveIdle:       $('rcWaveformIdle'),
    btnRec:         $('rcBtnRecord'),
    btnPause:       $('rcBtnPause'),
    btnStop:        $('rcBtnStop'),
    status:         $('rcStatus'),
    lang:           $('rcLang'),
    badge:          $('rcTranscriptBadge'),
    liveText:       $('rcLiveTranscript'),
    resultSec:      $('rcResultSection'),
    audioPlayer:    $('rcAudioPlayer'),
    audioMeta:      $('rcAudioMeta'),
    finalText:      $('rcFinalTranscript'),
    copyBtn:        $('rcCopyBtn'),
    dlBtn:          $('rcDownloadBtn'),
    copyStatus:     $('rcCopyStatus'),
    saveSec:        $('rcSaveSection'),
    className:      $('rcClassName'),
    notes:          $('rcNotes'),
    saveBtn:        $('rcSaveBtn'),
    discardBtn:     $('rcDiscardBtn'),
    saveStatus:     $('rcSaveStatus'),
    search:         $('rcSearch'),
    recCount:       $('rcRecordingCount'),
    recList:        $('rcRecordingsList'),
    emptyMsg:       $('rcEmptyMsg')
  };
  }
  queryEls();

  /* ── State ── */
  var S = {
    recording: false,
    paused: false,
    seconds: 0,
    timerInterval: null,
    mediaRec: null,
    chunks: [],
    stream: null,
    audioCtx: null,
    analyser: null,
    recognition: null,
    restartingRec: false,
    segments: [],
    interim: '',
    animId: null,
    blob: null,
    transcript: '',
    db: null,
    all: []
  };

  /* ═══════════════════════════════════
     IndexedDB
     ═══════════════════════════════════ */
  function openDB() {
    return new Promise(function (resolve, reject) {
      var req = indexedDB.open(DB_NAME, DB_VER);
      req.onupgradeneeded = function (e) {
        var db = e.target.result;
        if (!db.objectStoreNames.contains(STORE)) {
          var store = db.createObjectStore(STORE, { keyPath: 'id', autoIncrement: true });
          store.createIndex('className', 'className', { unique: false });
          store.createIndex('date', 'date', { unique: false });
        }
      };
      req.onsuccess = function (e) { resolve(e.target.result); };
      req.onerror = function (e) { reject(e.target.error); };
    });
  }

  function dbAdd(record) {
    return new Promise(function (resolve, reject) {
      var tx = S.db.transaction(STORE, 'readwrite');
      var st = tx.objectStore(STORE);
      var r = st.add(record);
      r.onsuccess = function () { resolve(r.result); };
      r.onerror = function () { reject(r.error); };
    });
  }

  function dbGetAll() {
    return new Promise(function (resolve, reject) {
      var tx = S.db.transaction(STORE, 'readonly');
      var st = tx.objectStore(STORE);
      var r = st.getAll();
      r.onsuccess = function () { resolve(r.result); };
      r.onerror = function () { reject(r.error); };
    });
  }

  function dbDelete(id) {
    return new Promise(function (resolve, reject) {
      var tx = S.db.transaction(STORE, 'readwrite');
      var st = tx.objectStore(STORE);
      var r = st.delete(id);
      r.onsuccess = function () { resolve(); };
      r.onerror = function () { reject(r.error); };
    });
  }

  /* ═══════════════════════════════════
     Hindi → Hinglish Transliteration
     ═══════════════════════════════════ */
  var CONSONANTS = {
    'क':'k','ख':'kh','ग':'g','घ':'gh','ङ':'ng',
    'च':'ch','छ':'chh','ज':'j','झ':'jh','ञ':'ny',
    'ट':'t','ठ':'th','ड':'d','ढ':'dh','ण':'n',
    'त':'t','थ':'th','द':'d','ध':'dh','न':'n',
    'प':'p','फ':'ph','ब':'b','भ':'bh','म':'m',
    'य':'y','र':'r','ल':'l','व':'v','श':'sh',
    'ष':'sh','स':'s','ह':'h'
  };
  var VOWELS = {
    'अ':'a','आ':'aa','इ':'i','ई':'ee','उ':'u','ऊ':'oo',
    'ऋ':'ri','ए':'e','ऐ':'ai','ओ':'o','औ':'au'
  };
  var MATRAS = {};
  MATRAS['\u093E']='aa'; MATRAS['\u093F']='i'; MATRAS['\u0940']='ee';
  MATRAS['\u0941']='u';  MATRAS['\u0942']='oo'; MATRAS['\u0943']='ri';
  MATRAS['\u0947']='e';  MATRAS['\u0948']='ai'; MATRAS['\u094B']='o';
  MATRAS['\u094C']='au';

  var HALANT = '\u094D';
  var NUKTA  = '\u093C';
  var NUKTA_MAP = {'क':'q','ख':'kh','ग':'gh','ज':'z','ड':'r','ढ':'rh','फ':'f'};

  function hindiToHinglish(text) {
    if (!text) return '';
    var out = '', i = 0;
    while (i < text.length) {
      var ch = text[i], nx = text[i + 1] || '';
      if (CONSONANTS[ch]) {
        if (nx === NUKTA) {
          var base = NUKTA_MAP[ch] || CONSONANTS[ch];
          i += 2;
          var af = text[i] || '';
          if (af === HALANT) { out += base; i++; }
          else if (MATRAS[af]) { out += base + MATRAS[af]; i++; }
          else { out += base + 'a'; }
        } else {
          out += CONSONANTS[ch]; i++;
          var af2 = text[i] || '';
          if (af2 === HALANT) { i++; }
          else if (MATRAS[af2]) { out += MATRAS[af2]; i++; }
          else { out += 'a'; }
        }
      }
      else if (VOWELS[ch])       { out += VOWELS[ch]; i++; }
      else if (ch === '\u0902')   { out += 'n'; i++; }  // anusvara
      else if (ch === '\u0903')   { out += 'h'; i++; }  // visarga
      else if (ch === '\u0901')   { out += 'n'; i++; }  // chandrabindu
      else if (ch >= '\u0966' && ch <= '\u096F') {
        out += String(ch.charCodeAt(0) - 0x0966); i++;
      }
      else if (ch === '\u0964')   { out += '.'; i++; }  // danda
      else { out += ch; i++; }
    }
    return out;
  }

  /* ═══════════════════════════════════
     Utilities
     ═══════════════════════════════════ */
  function esc(s) {
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;')
      .replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
  }

  function fmtTime(sec) {
    var h = Math.floor(sec / 3600);
    var m = Math.floor((sec % 3600) / 60);
    var s = sec % 60;
    return [h, m, s].map(function(v) { return String(v).padStart(2, '0'); }).join(':');
  }

  function fmtShort(sec) {
    var h = Math.floor(sec / 3600);
    var m = Math.floor((sec % 3600) / 60);
    var s = sec % 60;
    if (h > 0) return h + 'h ' + m + 'm';
    return m + 'm ' + s + 's';
  }

  /* ═══════════════════════════════════
     Timer
     ═══════════════════════════════════ */
  function startTimer() {
    S.timerInterval = setInterval(function () {
      S.seconds++;
      if (els.timer) els.timer.textContent = fmtTime(S.seconds);
    }, 1000);
  }
  function stopTimer() { clearInterval(S.timerInterval); S.timerInterval = null; }
  function resetTimer() { S.seconds = 0; if (els.timer) els.timer.textContent = '00:00:00'; }

  /* ═══════════════════════════════════
     Waveform Visualization
     ═══════════════════════════════════ */
  function sizeCanvas() {
    if (!els.canvas) return;
    var p = els.canvas.parentElement;
    els.canvas.width = p.clientWidth || 500;
    els.canvas.height = p.clientHeight || 120;
  }

  function drawWaveform() {
    if (!S.analyser || !els.canvas) return;
    var canvas = els.canvas;
    var ctx = canvas.getContext('2d');
    var bufLen = S.analyser.frequencyBinCount;
    var data = new Uint8Array(bufLen);

    function draw() {
      if (!S.recording) return;
      S.animId = requestAnimationFrame(draw);
      S.analyser.getByteFrequencyData(data);
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      var bars = 64;
      var bw = canvas.width / bars - 2;
      var step = Math.floor(bufLen / bars);

      for (var i = 0; i < bars; i++) {
        var val = data[i * step] || 0;
        var bh = (val / 255) * canvas.height * 0.88;
        var x = i * (bw + 2);
        var y = canvas.height - bh;

        var grad = ctx.createLinearGradient(x, canvas.height, x, y);
        grad.addColorStop(0, 'rgba(10, 132, 255, 0.85)');
        grad.addColorStop(0.5, 'rgba(137, 247, 255, 0.75)');
        grad.addColorStop(1, 'rgba(191, 90, 242, 0.65)');

        ctx.fillStyle = grad;
        if (ctx.roundRect) {
          ctx.beginPath();
          ctx.roundRect(x, y, bw, bh, 3);
          ctx.fill();
        } else {
          ctx.fillRect(x, y, bw, bh);
        }
      }
    }
    draw();
  }

  function stopWaveform() {
    if (S.animId) { cancelAnimationFrame(S.animId); S.animId = null; }
    if (els.canvas) {
      var ctx = els.canvas.getContext('2d');
      ctx.clearRect(0, 0, els.canvas.width, els.canvas.height);
    }
  }

  /* ═══════════════════════════════════
     Speech Recognition
     ═══════════════════════════════════ */
  function createRecognition() {
    if (!HAS_SPEECH) return null;
    var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    var rec = new SR();
    rec.lang = els.lang ? els.lang.value : 'hi-IN';
    rec.continuous = true;
    rec.interimResults = true;
    rec.maxAlternatives = 1;

    rec.onresult = function (e) {
      var interim = '';
      for (var i = e.resultIndex; i < e.results.length; i++) {
        var txt = e.results[i][0].transcript;
        if (rec.lang === 'hi-IN') txt = hindiToHinglish(txt);
        if (e.results[i].isFinal) {
          S.segments.push(txt);
          interim = '';
        } else {
          interim = txt;
        }
      }
      S.interim = interim;
      renderLive();
    };

    rec.onend = function () {
      if (S.recording && !S.paused && !S.restartingRec) {
        S.restartingRec = true;
        setTimeout(function () {
          if (S.recording && !S.paused) {
            try { rec.start(); } catch (e) { /* already running */ }
          }
          S.restartingRec = false;
        }, 150);
      }
    };

    rec.onerror = function (e) {
      if (e.error === 'no-speech' || e.error === 'aborted') return;
      console.warn('Speech error:', e.error);
    };

    return rec;
  }

  function renderLive() {
    if (!els.liveText) return;
    var final = S.segments.join(' ');
    var html = '';
    if (final) html += '<p class="rc-text-final">' + esc(final) + '</p>';
    if (S.interim) html += '<p class="rc-text-interim">' + esc(S.interim) + '</p>';
    if (!html) html = '<div class="rc-transcript-placeholder"><span>🎤</span><p>Listening...</p></div>';
    els.liveText.innerHTML = html;
    els.liveText.scrollTop = els.liveText.scrollHeight;
  }

  /* ═══════════════════════════════════
     Recording Controls
     ═══════════════════════════════════ */
  function startRecording() {
    if (!HAS_MIC || !HAS_RECORDER) {
      setStatus('Browser does not support audio recording. Use Chrome or Edge.', 'error');
      return;
    }

    navigator.mediaDevices.getUserMedia({
      audio: { echoCancellation: true, noiseSuppression: true, channelCount: 1 }
    }).then(function (stream) {
      S.stream = stream;

      // MediaRecorder
      var opts = { mimeType: 'audio/webm;codecs=opus' };
      try { S.mediaRec = new MediaRecorder(stream, opts); }
      catch (e) { S.mediaRec = new MediaRecorder(stream); }

      S.chunks = [];
      S.mediaRec.ondataavailable = function (e) {
        if (e.data.size > 0) S.chunks.push(e.data);
      };
      S.mediaRec.start(1000);

      // AudioContext for waveform
      S.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      var src = S.audioCtx.createMediaStreamSource(stream);
      S.analyser = S.audioCtx.createAnalyser();
      S.analyser.fftSize = 256;
      src.connect(S.analyser);

      // Speech Recognition
      S.segments = [];
      S.interim = '';
      S.recognition = createRecognition();
      if (S.recognition) { try { S.recognition.start(); } catch (e) {} }

      // Timer
      resetTimer();
      startTimer();

      // UI
      S.recording = true;
      S.paused = false;
      S.blob = null;
      S.transcript = '';
      updateControls();
      if (els.waveIdle) els.waveIdle.style.display = 'none';
      sizeCanvas();
      drawWaveform();
      if (els.resultSec) els.resultSec.style.display = 'none';
      if (els.saveSec) els.saveSec.style.display = 'none';

      setStatus('● Recording...', 'recording');
      setBadge('LIVE', true);
      renderLive();

    }).catch(function () {
      setStatus('Microphone access denied. Please allow mic permission.', 'error');
    });
  }

  function pauseRecording() {
    if (!S.recording || S.paused) return;
    if (S.mediaRec && S.mediaRec.state === 'recording') S.mediaRec.pause();
    if (S.recognition) { try { S.recognition.stop(); } catch (e) {} }
    stopTimer();
    S.paused = true;
    updateControls();
    setStatus('⏸ Paused', 'paused');
    setBadge('PAUSED', false);
  }

  function resumeRecording() {
    if (!S.recording || !S.paused) return;
    if (S.mediaRec && S.mediaRec.state === 'paused') S.mediaRec.resume();
    if (S.recognition) { try { S.recognition.start(); } catch (e) {} }
    startTimer();
    S.paused = false;
    updateControls();
    setStatus('● Recording...', 'recording');
    setBadge('LIVE', true);
  }

  function stopRecording() {
    if (!S.recording) return;
    S.recording = false;
    S.paused = false;

    if (S.mediaRec && S.mediaRec.state !== 'inactive') S.mediaRec.stop();
    if (S.recognition) { try { S.recognition.stop(); } catch (e) {} }
    stopTimer();
    stopWaveform();
    if (S.stream) S.stream.getTracks().forEach(function (t) { t.stop(); });
    if (S.audioCtx && S.audioCtx.state !== 'closed') S.audioCtx.close();

    setTimeout(function () {
      S.blob = new Blob(S.chunks, { type: 'audio/webm' });
      S.transcript = S.segments.join(' ');
      showResult();
      updateControls();
    }, 600);

    setStatus('Recording stopped', 'idle');
    if (els.waveIdle) els.waveIdle.style.display = '';
    setBadge('DONE', false);
  }

  /* ═══════════════════════════════════
     Result Panel
     ═══════════════════════════════════ */
  function showResult() {
    if (!els.resultSec) return;

    if (S.blob && els.audioPlayer) {
      els.audioPlayer.src = URL.createObjectURL(S.blob);
    }
    if (els.audioMeta) {
      var mb = S.blob ? (S.blob.size / (1024 * 1024)).toFixed(2) : '0';
      els.audioMeta.textContent = 'Duration: ' + fmtTime(S.seconds) + ' | Size: ' + mb + ' MB';
    }
    if (els.finalText) {
      els.finalText.innerHTML = S.transcript
        ? '<p>' + esc(S.transcript) + '</p>'
        : '<p class="mono" style="color:var(--muted);">No transcript captured. Make sure browser supports Speech Recognition (Chrome recommended).</p>';
    }
    els.resultSec.style.display = '';
    if (els.saveSec) els.saveSec.style.display = '';
  }

  /* ═══════════════════════════════════
     Save / Delete
     ═══════════════════════════════════ */
  function saveRecording() {
    var name = els.className ? els.className.value.trim() : '';
    if (!name) { setSaveStatus('Please enter a class/lecture name', 'error'); return; }
    if (!S.blob) { setSaveStatus('No recording to save', 'error'); return; }

    var record = {
      className: name,
      notes: els.notes ? els.notes.value.trim() : '',
      date: new Date().toISOString(),
      duration: S.seconds,
      transcript: S.transcript || '',
      audioBlob: S.blob,
      audioType: S.blob.type,
      audioSize: S.blob.size
    };

    dbAdd(record).then(function () {
      if (els.className) els.className.value = '';
      if (els.notes) els.notes.value = '';
      if (els.resultSec) els.resultSec.style.display = 'none';
      if (els.saveSec) els.saveSec.style.display = 'none';
      resetTimer();
      setSaveStatus('✓ Recording saved!', 'ok');
      loadRecordings();
    }).catch(function () {
      setSaveStatus('Error saving recording', 'error');
    });
  }

  function discardRecording() {
    S.blob = null; S.transcript = '';
    if (els.resultSec) els.resultSec.style.display = 'none';
    if (els.saveSec) els.saveSec.style.display = 'none';
    resetTimer();
    if (els.waveIdle) els.waveIdle.style.display = '';
    setStatus('Ready to record', 'idle');
    if (els.liveText) {
      els.liveText.innerHTML = '<div class="rc-transcript-placeholder"><span>📝</span><p>Live transcription will appear here as you speak...</p></div>';
    }
    setBadge('IDLE', false);
  }

  /* ═══════════════════════════════════
     Load & Render Recordings
     ═══════════════════════════════════ */
  function loadRecordings() {
    return dbGetAll().then(function (recs) {
      S.all = recs.sort(function (a, b) { return new Date(b.date) - new Date(a.date); });
      renderRecordings(S.all);
      updateStats();
    }).catch(function (err) { console.error('Load error:', err); });
  }

  function renderRecordings(list) {
    if (!els.recList) return;
    if (els.recCount) els.recCount.textContent = list.length + ' recording' + (list.length !== 1 ? 's' : '');
    if (!list.length) {
      els.recList.innerHTML = '';
      if (els.emptyMsg) els.emptyMsg.style.display = '';
      return;
    }
    if (els.emptyMsg) els.emptyMsg.style.display = 'none';

    els.recList.innerHTML = list.map(function (rec) {
      var d = new Date(rec.date);
      var ds = d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
      var ts = d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
      var dur = fmtShort(rec.duration);
      var mb = ((rec.audioSize || 0) / (1024 * 1024)).toFixed(1);
      var preview = rec.transcript
        ? esc(rec.transcript.substring(0, 150)) + (rec.transcript.length > 150 ? '...' : '')
        : '<em style="opacity:.4">No transcript</em>';

      return '<div class="rc-recording-card" data-id="' + rec.id + '">' +
        '<div class="rc-rec-header"><div class="rc-rec-title">' +
        '<h4 class="mono">' + esc(rec.className) + '</h4>' +
        '<div class="rc-rec-meta mono">' +
        '<span>📅 ' + ds + '</span><span>🕐 ' + ts + '</span>' +
        '<span>⏱️ ' + dur + '</span><span>💾 ' + mb + ' MB</span>' +
        '</div></div></div>' +
        (rec.notes ? '<p class="rc-rec-notes">' + esc(rec.notes) + '</p>' : '') +
        '<div class="rc-rec-transcript">' + preview + '</div>' +
        '<div class="rc-rec-player-wrap"><audio controls class="rc-rec-audio" data-rid="' + rec.id + '"></audio></div>' +
        '<div class="rc-rec-actions">' +
        '<button class="btn small rc-act" data-action="copy" data-id="' + rec.id + '">📋 Copy</button>' +
        '<button class="btn ghost small rc-act" data-action="download" data-id="' + rec.id + '">💾 Download</button>' +
        '<button class="btn ghost small rc-act" data-action="play" data-id="' + rec.id + '">▶️ Play</button>' +
        '<button class="btn ghost small danger rc-act" data-action="delete" data-id="' + rec.id + '">🗑️ Delete</button>' +
        '</div></div>';
    }).join('');
  }

  /* ═══════════════════════════════════
     Recording Card Actions (Delegated)
     ═══════════════════════════════════ */
  function handleCardAction(e) {
    var btn = e.target.closest('.rc-act');
    if (!btn) return;
    var action = btn.getAttribute('data-action');
    var id = Number(btn.getAttribute('data-id'));
    var rec = S.all.find(function (r) { return r.id === id; });
    if (!rec) return;

    if (action === 'copy' && rec.transcript) {
      navigator.clipboard.writeText(rec.transcript).catch(function () {});
      btn.textContent = '✓ Copied';
      setTimeout(function () { btn.textContent = '📋 Copy'; }, 1500);
    }
    else if (action === 'download' && rec.transcript) {
      downloadText(rec.transcript, rec.className.replace(/\s+/g, '_'));
    }
    else if (action === 'play' && rec.audioBlob) {
      var audio = document.querySelector('audio[data-rid="' + id + '"]');
      if (audio) {
        if (!audio.src || audio.src === '') audio.src = URL.createObjectURL(rec.audioBlob);
        audio.play();
      }
    }
    else if (action === 'delete') {
      if (!confirm('Delete this recording? This cannot be undone.')) return;
      dbDelete(id).then(loadRecordings).catch(function (err) { console.error(err); });
    }
  }

  /* ═══════════════════════════════════
     Search
     ═══════════════════════════════════ */
  function searchRecordings() {
    var q = els.search ? els.search.value.trim().toLowerCase() : '';
    if (!q) { renderRecordings(S.all); return; }
    var filtered = S.all.filter(function (r) {
      var dateStr = new Date(r.date).toLocaleDateString('en-IN');
      var hay = (r.className + ' ' + (r.notes || '') + ' ' + (r.transcript || '') + ' ' + dateStr).toLowerCase();
      return hay.indexOf(q) !== -1;
    });
    renderRecordings(filtered);
  }

  /* ═══════════════════════════════════
     Stats
     ═══════════════════════════════════ */
  function updateStats() {
    var recs = S.all;
    if (els.totalCount) els.totalCount.textContent = recs.length;
    if (els.totalDuration) {
      var total = recs.reduce(function (s, r) { return s + (r.duration || 0); }, 0);
      els.totalDuration.textContent = fmtShort(total);
    }
    if (els.todayCount) {
      var today = new Date().toDateString();
      els.todayCount.textContent = recs.filter(function (r) {
        return new Date(r.date).toDateString() === today;
      }).length;
    }
    if (els.todayDate) {
      els.todayDate.textContent = new Date().toLocaleDateString('en-IN', {
        day: 'numeric', month: 'short', year: 'numeric'
      });
    }
  }

  /* ═══════════════════════════════════
     UI Helpers
     ═══════════════════════════════════ */
  function updateControls() {
    if (!els.btnRec) return;
    if (S.recording) {
      els.btnRec.disabled = true;
      els.btnRec.classList.add('rc-recording');
      els.btnPause.disabled = false;
      els.btnStop.disabled = false;
      els.btnPause.textContent = S.paused ? '▶' : '⏸';
      els.btnPause.title = S.paused ? 'Resume' : 'Pause';
    } else {
      els.btnRec.disabled = false;
      els.btnRec.classList.remove('rc-recording');
      els.btnPause.disabled = true;
      els.btnStop.disabled = true;
      els.btnPause.textContent = '⏸';
    }
  }

  function setStatus(text, type) {
    if (!els.status) return;
    els.status.textContent = text;
    els.status.className = 'rc-status mono';
    if (type === 'recording') els.status.classList.add('rc-status-rec');
    else if (type === 'paused') els.status.classList.add('rc-status-pause');
    else if (type === 'error') els.status.classList.add('rc-status-err');
  }

  function setSaveStatus(text, type) {
    if (!els.saveStatus) return;
    els.saveStatus.textContent = text;
    els.saveStatus.className = 'mono rc-save-status';
    if (type === 'ok') els.saveStatus.classList.add('status-ok');
    else if (type === 'error') els.saveStatus.classList.add('status-err');
    setTimeout(function () { if (els.saveStatus) els.saveStatus.textContent = ''; }, 3000);
  }

  function setBadge(text, isLive) {
    if (!els.badge) return;
    els.badge.textContent = text;
    if (isLive) els.badge.classList.add('rc-badge-live');
    else els.badge.classList.remove('rc-badge-live');
  }

  /* ── Copy / Download ── */
  function copyTranscript() {
    var text = S.transcript;
    if (!text) return;
    navigator.clipboard.writeText(text).then(function () {
      if (els.copyStatus) {
        els.copyStatus.textContent = '✓ Copied!';
        els.copyStatus.className = 'mono rc-copy-status status-ok';
        setTimeout(function () { els.copyStatus.textContent = ''; }, 2000);
      }
    }).catch(function () {});
  }

  function downloadText(text, name) {
    if (!text) return;
    if (!name) name = 'transcript';
    var blob = new Blob([text], { type: 'text/plain' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = name + '.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  /* ═══════════════════════════════════
     Event Binding
     ═══════════════════════════════════ */
  function bind() {
    if (els.btnRec) els.btnRec.addEventListener('click', startRecording);
    if (els.btnPause) els.btnPause.addEventListener('click', function () {
      S.paused ? resumeRecording() : pauseRecording();
    });
    if (els.btnStop) els.btnStop.addEventListener('click', stopRecording);
    if (els.copyBtn) els.copyBtn.addEventListener('click', copyTranscript);
    if (els.dlBtn) els.dlBtn.addEventListener('click', function () {
      var name = els.className ? els.className.value.trim() || 'transcript' : 'transcript';
      downloadText(S.transcript, name);
    });
    if (els.saveBtn) els.saveBtn.addEventListener('click', saveRecording);
    if (els.discardBtn) els.discardBtn.addEventListener('click', discardRecording);
    if (els.search) els.search.addEventListener('input', searchRecordings);

    // Delegated card actions
    if (els.recList) els.recList.addEventListener('click', handleCardAction);

    // Resize waveform
    window.addEventListener('resize', function () { if (S.recording) sizeCanvas(); });
  }

  /* ═══════════════════════════════════
     Scroll Reveal
     ═══════════════════════════════════ */
  function initReveal() {
    var items = document.querySelectorAll('.reveal');
    if (!items.length) return;
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) entry.target.classList.add('visible');
      });
    }, { threshold: 0.08 });
    items.forEach(function (el) { obs.observe(el); });
  }

  /* ═══════════════════════════════════
     Init
     ═══════════════════════════════════ */
  function init() {
    queryEls();
    if (!els.btnRec) return;
    if (!HAS_MIC) setStatus('Audio recording not supported. Use Chrome or Edge.', 'error');
    if (!HAS_SPEECH) setStatus('Speech recognition not available. Use Chrome for live transcription.', 'error');

    openDB().then(function (db) {
      S.db = db;
      return loadRecordings();
    }).catch(function (err) { console.error('DB init error:', err); });

    bind();
    initReveal();
    updateStats();
    updateControls();
  }

  init();

  /* Expose for SPA re-init */
  window._recorderInit = init;
})();
