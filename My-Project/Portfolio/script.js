const deployProgress = document.getElementById("deployProgress");
const totalHours = document.getElementById("totalHours");
const floatingCard = document.querySelector("[data-float]");

function animateProgress() {
  if (!deployProgress) {
    return;
  }

  const target = 88;
  let current = 0;

  const timer = setInterval(() => {
    current += 1;
    deployProgress.style.width = `${current}%`;

    if (current >= target) {
      clearInterval(timer);
    }
  }, 20);
}

function animateHours() {
  if (!totalHours) {
    return;
  }

  const finalValue = 12340;
  let value = 11800;

  const timer = setInterval(() => {
    value += 12;
    if (value >= finalValue) {
      value = finalValue;
      clearInterval(timer);
    }
    totalHours.textContent = `${value}h`;
  }, 22);
}

function addHeroFloat() {
  if (!floatingCard) {
    return;
  }

  window.addEventListener("mousemove", (event) => {
    const x = (event.clientX / window.innerWidth - 0.5) * 8;
    const y = (event.clientY / window.innerHeight - 0.5) * 8;
    floatingCard.style.transform = `translate(${x}px, ${y}px)`;
  });
}

function addImageFallback() {
  const fallback =
    "data:image/svg+xml;utf8," +
    encodeURIComponent(
      '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#1a4eb9"/><stop offset="1" stop-color="#7a2adf"/></linearGradient></defs><rect width="400" height="400" fill="url(#g)"/><text x="200" y="210" text-anchor="middle" fill="#dff6ff" font-size="28" font-family="Arial">ALIENS CHARACTER</text></svg>'
    );

  document.querySelectorAll("img").forEach((img) => {
    img.addEventListener("error", () => {
      img.src = fallback;
    });
  });
}

function formatBytes(totalBytes) {
  if (!Number.isFinite(totalBytes) || totalBytes <= 0) {
    return "0 KB";
  }

  const units = ["B", "KB", "MB", "GB"];
  let bytes = totalBytes;
  let unitIndex = 0;

  while (bytes >= 1024 && unitIndex < units.length - 1) {
    bytes /= 1024;
    unitIndex += 1;
  }

  const value = unitIndex === 0 ? Math.round(bytes) : bytes.toFixed(1);
  return `${value} ${units[unitIndex]}`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function parseCsvRows(csvText) {
  return csvText
    .replaceAll("\r", "")
    .split("\n")
    .filter((line) => line.trim().length > 0)
    .map((line) => line.split(","));
}

function renderCsvTable(csvText) {
  const rows = parseCsvRows(csvText);
  if (!rows.length) {
    return "<p>No rows available.</p>";
  }

  const headCells = rows[0].map((cell) => `<th>${escapeHtml(cell.trim())}</th>`).join("");
  const bodyRows = rows
    .slice(1)
    .map((row) => {
      const rowCells = row.map((cell) => `<td>${escapeHtml(cell.trim())}</td>`).join("");
      return `<tr>${rowCells}</tr>`;
    })
    .join("");

  return `
    <div class="csv-wrap">
      <table class="csv-table">
        <thead><tr>${headCells}</tr></thead>
        <tbody>${bodyRows}</tbody>
      </table>
    </div>
  `;
}

function initMeetingRecordsPage() {
  const listNode = document.getElementById("recordList");
  const previewTitle = document.getElementById("previewTitle");
  const previewMeta = document.getElementById("previewMeta");
  const previewBody = document.getElementById("previewBody");
  const searchInput = document.getElementById("recordSearch");
  const openSourceLink = document.getElementById("openSourceLink");
  const recordCount = document.getElementById("recordCount");
  const previewCount = document.getElementById("previewCount");
  const totalSize = document.getElementById("totalSize");

  if (!listNode || !previewTitle || !previewMeta || !previewBody || !searchInput || !openSourceLink) {
    return;
  }

  const rawRecords = Array.isArray(window.ALIENS_MEETING_RECORDS) ? window.ALIENS_MEETING_RECORDS : [];
  const records = rawRecords.map((item) => ({
    ...item,
    content: typeof item.content === "string" ? item.content : "",
  }));

  if (recordCount) {
    recordCount.textContent = String(records.length);
  }

  if (previewCount) {
    previewCount.textContent = String(records.filter((item) => item.previewable).length);
  }

  if (totalSize) {
    const total = records.reduce((sum, item) => sum + (Number(item.size) || 0), 0);
    totalSize.textContent = formatBytes(total);
  }

  if (!records.length) {
    listNode.innerHTML = "<p class=\"mono\">No records found in data file.</p>";
    return;
  }

  let activeIndex = 0;
  let filtered = records;

  function renderPreview(record) {
    previewTitle.textContent = record.path;
    previewMeta.textContent = `${record.ext.toUpperCase()} | ${formatBytes(record.size)} | ${record.previewable ? "Preview available" : "Binary file"}`;

    const encodedPath = record.path.split("/").map(encodeURIComponent).join("/");
    openSourceLink.href = `aliens-meeting-records/${encodedPath}`;

    if (record.previewable) {
      if (record.ext === ".csv") {
        previewBody.innerHTML = renderCsvTable(record.content);
      } else {
        previewBody.innerHTML = `<pre>${escapeHtml(record.content)}</pre>`;
      }
    } else {
      previewBody.innerHTML = `<p class=\"mono\">Preview not available for ${escapeHtml(record.ext)} file. Use <b>Open Source File</b> to open/download.</p>`;
    }
  }

  function renderList() {
    if (!filtered.length) {
      listNode.innerHTML = "<p class=\"mono\">No matching records.</p>";
      previewTitle.textContent = "No file selected";
      previewMeta.textContent = "";
      previewBody.textContent = "Try another search keyword.";
      openSourceLink.href = "#";
      return;
    }

    if (activeIndex >= filtered.length) {
      activeIndex = 0;
    }

    listNode.innerHTML = filtered
      .map((item, index) => {
        const activeClass = index === activeIndex ? " active" : "";
        return `
          <button type=\"button\" class=\"record-item${activeClass}\" data-index=\"${index}\">
            <span class=\"mono\">${escapeHtml(item.path)}</span>
            <small>${escapeHtml(item.ext.toUpperCase())} | ${formatBytes(item.size)}</small>
          </button>
        `;
      })
      .join("");

    renderPreview(filtered[activeIndex]);
  }

  listNode.addEventListener("click", (event) => {
    const item = event.target.closest(".record-item");
    if (!item) {
      return;
    }

    const nextIndex = Number(item.dataset.index);
    if (!Number.isNaN(nextIndex)) {
      activeIndex = nextIndex;
      renderList();
    }
  });

  searchInput.addEventListener("input", (event) => {
    const keyword = event.target.value.trim().toLowerCase();
    filtered = records.filter((item) => {
      if (!keyword) {
        return true;
      }
      const haystack = `${item.path} ${item.content}`.toLowerCase();
      return haystack.includes(keyword);
    });
    activeIndex = 0;
    renderList();
  });

  renderList();
}

function initTableNew() {
  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabRecords = document.getElementById("tabRecords");
  const tabTableNew = document.getElementById("tabTableNew");

  if (!tabBtns.length || !tabRecords || !tabTableNew) {
    return;
  }

  tabBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      tabBtns.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      const target = btn.dataset.tab;
      tabRecords.style.display = target === "records" ? "" : "none";
      tabTableNew.style.display = target === "table-new" ? "" : "none";
    });
  });

  const presentBox = document.getElementById("tnPresentPaste");
  const lateBox = document.getElementById("tnLatePaste");
  const absentBox = document.getElementById("tnAbsentPaste");
  const generateBtn = document.getElementById("tnGenerate");
  const clearBtn = document.getElementById("tnClear");
  const outputWrap = document.getElementById("tnOutputWrap");
  const tableRender = document.getElementById("tnTableRender");
  const copyTableBtn = document.getElementById("tnCopyTable");
  const copyStatus = document.getElementById("tnCopyStatus");

  if (!presentBox || !lateBox || !absentBox || !generateBtn) {
    return;
  }

  const saveBtn = document.getElementById("tnSave");
  const saveNameInput = document.getElementById("tnSaveName");
  const outputTitle = document.getElementById("tnOutputTitle");
  const savedListNode = document.getElementById("savedTableList");
  const savedCountNode = document.getElementById("savedTableCount");

  const STORAGE_KEY = "aliens_saved_tables";
  let editingId = null;

  function loadSaved() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
    } catch (_) {
      return [];
    }
  }

  function saveToDisk(list) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
  }

  function parseNames(text) {
    return text
      .split("\n")
      .map((n) => n.trim())
      .filter((n) => n.length > 0);
  }

  let lastPresent = [];
  let lastLate = [];
  let lastAbsent = [];

  function buildTableHtml(present, late, absent) {
    const maxRows = Math.max(present.length, late.length, absent.length, 1);
    let headRow = "<tr><th>No.</th><th>Present Members</th><th>Late</th><th>Absent</th></tr>";
    let bodyRows = "";
    for (let i = 0; i < maxRows; i++) {
      bodyRows += "<tr>";
      bodyRows += `<td>${i + 1}</td>`;
      bodyRows += `<td>${escapeHtml(present[i] || "")}</td>`;
      bodyRows += `<td>${escapeHtml(late[i] || "")}</td>`;
      bodyRows += `<td>${escapeHtml(absent[i] || "")}</td>`;
      bodyRows += "</tr>";
    }
    return `<table class="csv-table"><thead>${headRow}</thead><tbody>${bodyRows}</tbody></table>`;
  }

  function buildTeamsText(present, late, absent) {
    const maxRows = Math.max(present.length, late.length, absent.length, 1);
    let lines = ["No.\tPresent Members\tLate\tAbsent"];
    for (let i = 0; i < maxRows; i++) {
      lines.push(`${i + 1}\t${present[i] || ""}\t${late[i] || ""}\t${absent[i] || ""}`);
    }
    return lines.join("\n");
  }

  function buildHtmlTable(present, late, absent) {
    const maxRows = Math.max(present.length, late.length, absent.length, 1);
    let html = '<table style="border-collapse:collapse;font-family:Segoe UI,sans-serif;font-size:13px">';
    html += '<tr>';
    ["No.", "Present Members", "Late", "Absent"].forEach((h) => {
      html += `<th style="border:1px solid #999;padding:6px 12px;background:#1a3a6a;color:#eaf5ff;text-align:left">${h}</th>`;
    });
    html += '</tr>';
    for (let i = 0; i < maxRows; i++) {
      html += '<tr>';
      html += `<td style="border:1px solid #bbb;padding:5px 10px;text-align:center">${i + 1}</td>`;
      html += `<td style="border:1px solid #bbb;padding:5px 10px">${escapeHtml(present[i] || "")}</td>`;
      html += `<td style="border:1px solid #bbb;padding:5px 10px">${escapeHtml(late[i] || "")}</td>`;
      html += `<td style="border:1px solid #bbb;padding:5px 10px">${escapeHtml(absent[i] || "")}</td>`;
      html += '</tr>';
    }
    html += '</table>';
    return html;
  }

  function copyRichTable(present, late, absent) {
    const htmlStr = buildHtmlTable(present, late, absent);
    const plainStr = buildTeamsText(present, late, absent);
    const htmlBlob = new Blob([htmlStr], { type: "text/html" });
    const textBlob = new Blob([plainStr], { type: "text/plain" });
    const item = new ClipboardItem({ "text/html": htmlBlob, "text/plain": textBlob });
    return navigator.clipboard.write([item]);
  }

  function flashStatus(msg) {
    if (!copyStatus) return;
    copyStatus.textContent = msg;
    setTimeout(() => { copyStatus.textContent = ""; }, 2500);
  }

  function todayString() {
    const d = new Date();
    return `${d.getMonth() + 1}-${d.getDate()}-${d.getFullYear()}`;
  }

  function resetForm() {
    presentBox.value = "";
    lateBox.value = "";
    absentBox.value = "";
    lastPresent = [];
    lastLate = [];
    lastAbsent = [];
    outputWrap.style.display = "none";
    tableRender.innerHTML = "";
    editingId = null;
    if (outputTitle) outputTitle.textContent = "Generated Table";
    if (saveBtn) saveBtn.textContent = "Save Table";
    if (saveNameInput) saveNameInput.value = "";
    flashStatus("");
  }

  function renderSavedList() {
    const list = loadSaved();
    if (savedCountNode) savedCountNode.textContent = `${list.length} table${list.length !== 1 ? "s" : ""}`;
    if (!savedListNode) return;

    if (!list.length) {
      savedListNode.innerHTML = '<p class="mono">No saved tables yet. Create one above!</p>';
      return;
    }

    savedListNode.innerHTML = list.map((item) => `
      <div class="saved-card" data-id="${escapeHtml(item.id)}">
        <header class="saved-card-head">
          <h4>${escapeHtml(item.name)}</h4>
          <small class="mono">${escapeHtml(item.date)} | P:${item.present.length} L:${item.late.length} A:${item.absent.length}</small>
        </header>
        <div class="csv-wrap">${buildTableHtml(item.present, item.late, item.absent)}</div>
        <div class="saved-card-actions">
          <button type="button" class="btn-copy-teams" title="Copy Table">Copy Table</button>
          <button type="button" class="btn-update" title="Edit this table">Update</button>
          <button type="button" class="btn-remove" title="Delete this table">Remove</button>
        </div>
      </div>
    `).join("");
  }

  function getItemById(id) {
    return loadSaved().find((t) => t.id === id);
  }

  generateBtn.addEventListener("click", () => {
    lastPresent = parseNames(presentBox.value);
    lastLate = parseNames(lateBox.value);
    lastAbsent = parseNames(absentBox.value);

    if (!lastPresent.length && !lastLate.length && !lastAbsent.length) {
      flashStatus("At least one column me names daalo!");
      return;
    }

    tableRender.innerHTML = buildTableHtml(lastPresent, lastLate, lastAbsent);
    outputWrap.style.display = "";
    if (saveNameInput && !saveNameInput.value.trim()) {
      saveNameInput.value = `Table-${todayString()}`;
    }
    flashStatus("Table generated!");
  });

  clearBtn.addEventListener("click", () => {
    resetForm();
  });

  if (saveBtn) {
    saveBtn.addEventListener("click", () => {
      if (!lastPresent.length && !lastLate.length && !lastAbsent.length) {
        flashStatus("Generate table first!");
        return;
      }
      const name = (saveNameInput && saveNameInput.value.trim()) || `Table-${todayString()}`;
      const list = loadSaved();

      if (editingId) {
        const idx = list.findIndex((t) => t.id === editingId);
        if (idx !== -1) {
          list[idx].name = name;
          list[idx].present = lastPresent.slice();
          list[idx].late = lastLate.slice();
          list[idx].absent = lastAbsent.slice();
          list[idx].date = todayString();
          saveToDisk(list);
          flashStatus(`"${name}" updated!`);
        } else {
          flashStatus("Table not found for update.");
        }
      } else {
        const newItem = {
          id: Date.now().toString(36) + Math.random().toString(36).slice(2, 6),
          name: name,
          date: todayString(),
          present: lastPresent.slice(),
          late: lastLate.slice(),
          absent: lastAbsent.slice(),
        };
        list.unshift(newItem);
        saveToDisk(list);
        flashStatus(`"${name}" saved!`);
      }

      renderSavedList();
      resetForm();
    });
  }

  copyTableBtn.addEventListener("click", () => {
    copyRichTable(lastPresent, lastLate, lastAbsent).then(
      () => flashStatus("Table copied! Paste in Teams / WhatsApp / Excel."),
      () => flashStatus("Copy failed — try manually.")
    );
  });

  if (savedListNode) {
    savedListNode.addEventListener("click", (e) => {
      const card = e.target.closest(".saved-card");
      if (!card) return;
      const id = card.dataset.id;
      const item = getItemById(id);

      if (e.target.closest(".btn-remove")) {
        const list = loadSaved().filter((t) => t.id !== id);
        saveToDisk(list);
        renderSavedList();
        if (editingId === id) resetForm();
        flashStatus("Table removed!");
        return;
      }

      if (e.target.closest(".btn-update") && item) {
        editingId = id;
        presentBox.value = item.present.join("\n");
        lateBox.value = item.late.join("\n");
        absentBox.value = item.absent.join("\n");
        lastPresent = item.present.slice();
        lastLate = item.late.slice();
        lastAbsent = item.absent.slice();
        tableRender.innerHTML = buildTableHtml(lastPresent, lastLate, lastAbsent);
        outputWrap.style.display = "";
        if (saveNameInput) saveNameInput.value = item.name;
        if (outputTitle) outputTitle.textContent = `Editing: ${item.name}`;
        if (saveBtn) saveBtn.textContent = "Update & Save";
        window.scrollTo({ top: 0, behavior: "smooth" });
        flashStatus(`Editing "${item.name}" — make changes and hit Update & Save`);
        return;
      }

      if (e.target.closest(".btn-copy-teams") && item) {
        copyRichTable(item.present, item.late, item.absent).then(
          () => flashStatus("Table copied!"),
          () => flashStatus("Copy failed.")
        );
        return;
      }
    });
  }

  renderSavedList();
}

animateProgress();
animateHours();
addHeroFloat();
addImageFallback();
initMeetingRecordsPage();
initTableNew();

/* ── Scroll Reveal ── */
(function initReveal() {
  const reveals = document.querySelectorAll('.reveal');
  if (!reveals.length) return;
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('visible'); io.unobserve(e.target); } });
  }, { threshold: 0.08 });
  reveals.forEach(el => io.observe(el));
})();
