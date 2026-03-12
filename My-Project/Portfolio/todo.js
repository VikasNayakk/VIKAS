/* ===== Aliens ToDo Task Manager ===== */
(function () {
  'use strict';

  const STORAGE_KEY = 'aliens_todo_tasks';
  const ALARM_KEY = 'aliens_todo_alarms';
  let tasks = [];
  let editingId = null;
  let alarmTimers = {};

  /* ---------- DOM refs ---------- */
  const $ = (id) => document.getElementById(id);
  let el = {};

  function queryEls() {
    el = {
      taskInput: $('tdTaskInput'),
      category: $('tdCategory'),
      priority: $('tdPriority'),
      date: $('tdDate'),
      time: $('tdTime'),
      alarm: $('tdAlarm'),
      notes: $('tdNotes'),
      addBtn: $('tdAddBtn'),
      clearForm: $('tdClearForm'),
      formStatus: $('tdFormStatus'),
      search: $('tdSearch'),
      filterStatus: $('tdFilterStatus'),
      filterPriority: $('tdFilterPriority'),
      filterCategory: $('tdFilterCategory'),
      sortBy: $('tdSortBy'),
      clearDone: $('tdClearDone'),
      clearAll: $('tdClearAll'),
      taskList: $('tdTaskList'),
      emptyMsg: $('tdEmptyMsg'),
      totalCount: $('tdTotalCount'),
      doneCount: $('tdDoneCount'),
      pendingCount: $('tdPendingCount'),
      todayDate: $('tdTodayDate'),
      alarmSound: $('alarmSound'),
      progressBar: $('tdProgressBar'),
      progressPct: $('tdProgressPct'),
      ringTotal: $('tdRingTotal'),
      ringDone: $('tdRingDone'),
      ringPending: $('tdRingPending'),
      toggleForm: $('tdToggleForm'),
      formBody: $('tdFormBody'),
      visibleCount: $('tdVisibleCount'),
      alarmBanner: $('tdAlarmBanner'),
    };
  }
  queryEls();

  /* ---------- Init ---------- */
  function init() {
    queryEls();
    if (!el.taskInput) return; // not on todo page
    loadTasks();
    setTodayDate();
    renderTasks();
    scheduleAllAlarms();
    requestNotificationPermission();

    el.addBtn.addEventListener('click', handleAddOrUpdate);
    el.taskInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') handleAddOrUpdate();
    });
    el.clearForm.addEventListener('click', resetForm);
    el.search.addEventListener('input', renderTasks);
    el.filterStatus.addEventListener('change', renderTasks);
    el.filterPriority.addEventListener('change', renderTasks);
    el.filterCategory.addEventListener('change', renderTasks);
    el.sortBy.addEventListener('change', renderTasks);
    el.clearDone.addEventListener('click', clearCompleted);
    el.clearAll.addEventListener('click', clearAll);

    // Form collapse toggle
    if (el.toggleForm) {
      el.toggleForm.addEventListener('click', function () {
        el.formBody.classList.toggle('collapsed');
        el.toggleForm.classList.toggle('collapsed');
      });
    }

    // check alarms every 30 seconds
    setInterval(checkAlarms, 30000);
  }

  /* ---------- Notification Permission ---------- */
  function requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }

  /* ---------- Storage ---------- */
  function loadTasks() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      tasks = raw ? JSON.parse(raw) : [];
    } catch { tasks = []; }
  }

  function saveTasks() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
  }

  /* ---------- Date display ---------- */
  function setTodayDate() {
    const d = new Date();
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    el.todayDate.textContent = d.getDate() + ' ' + months[d.getMonth()] + ' ' + d.getFullYear();
  }

  /* ---------- ID generator ---------- */
  function genId() {
    return Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
  }

  /* ---------- Add / Update ---------- */
  function handleAddOrUpdate() {
    const name = el.taskInput.value.trim();
    if (!name) {
      flashStatus('Task name is required!', 'err');
      el.taskInput.focus();
      return;
    }

    if (editingId) {
      const t = tasks.find((x) => x.id === editingId);
      if (t) {
        t.name = name;
        t.category = el.category.value;
        t.priority = el.priority.value;
        t.dueDate = el.date.value;
        t.dueTime = el.time.value;
        t.alarm = el.alarm.value;
        t.notes = el.notes.value.trim();
        t.updatedAt = new Date().toISOString();
        flashStatus('Task updated!', 'ok');
        scheduleAlarm(t);
      }
      editingId = null;
      el.addBtn.innerHTML = '&#10010; Add Task';
    } else {
      const task = {
        id: genId(),
        name: name,
        category: el.category.value,
        priority: el.priority.value,
        dueDate: el.date.value,
        dueTime: el.time.value,
        alarm: el.alarm.value,
        notes: el.notes.value.trim(),
        done: false,
        createdAt: new Date().toISOString(),
        updatedAt: null,
        alarmFired: false,
      };
      tasks.push(task);
      flashStatus('Task added!', 'ok');
      scheduleAlarm(task);
    }

    saveTasks();
    renderTasks();
    resetForm();
  }

  /* ---------- Form helpers ---------- */
  function resetForm() {
    el.taskInput.value = '';
    el.category.value = 'General';
    el.priority.value = 'Medium';
    el.date.value = '';
    el.time.value = '';
    el.alarm.value = '';
    el.notes.value = '';
    editingId = null;
    el.addBtn.innerHTML = '&#10010; Add Task';
    el.formStatus.textContent = '';
  }

  function flashStatus(msg, type) {
    el.formStatus.textContent = msg;
    el.formStatus.className = 'mono todo-status ' + (type === 'ok' ? 'status-ok' : 'status-err');
    setTimeout(() => { el.formStatus.textContent = ''; }, 3000);
  }

  /* ---------- Alarm system ---------- */
  function scheduleAllAlarms() {
    tasks.forEach((t) => scheduleAlarm(t));
  }

  function scheduleAlarm(task) {
    // clear existing timer
    if (alarmTimers[task.id]) {
      clearTimeout(alarmTimers[task.id]);
      delete alarmTimers[task.id];
    }
    if (!task.alarm || !task.dueDate || !task.dueTime || task.done || task.alarmFired) return;

    const dueMs = new Date(task.dueDate + 'T' + task.dueTime).getTime();
    if (isNaN(dueMs)) return;

    let offsetMin = 0;
    if (task.alarm === 'exact') offsetMin = 0;
    else offsetMin = parseInt(task.alarm, 10) || 0;

    const alarmMs = dueMs - offsetMin * 60000;
    const delay = alarmMs - Date.now();

    if (delay <= 0) return; // already past

    alarmTimers[task.id] = setTimeout(() => {
      fireAlarm(task);
    }, delay);
  }

  function checkAlarms() {
    const now = Date.now();
    tasks.forEach((t) => {
      if (!t.alarm || !t.dueDate || !t.dueTime || t.done || t.alarmFired) return;
      const dueMs = new Date(t.dueDate + 'T' + t.dueTime).getTime();
      if (isNaN(dueMs)) return;
      let offsetMin = t.alarm === 'exact' ? 0 : (parseInt(t.alarm, 10) || 0);
      const alarmMs = dueMs - offsetMin * 60000;
      if (now >= alarmMs && now < alarmMs + 60000) {
        fireAlarm(t);
      }
    });
  }

  function fireAlarm(task) {
    task.alarmFired = true;
    saveTasks();

    // Play sound
    try {
      if (el.alarmSound) {
        el.alarmSound.currentTime = 0;
        el.alarmSound.play().catch(() => {});
      }
    } catch {}

    // Browser notification
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('Aliens ToDo Alarm', {
        body: task.name + (task.dueTime ? ' — Due: ' + task.dueTime : ''),
        icon: 'assets/characters/aliens-badge.png',
      });
    }

    // In-page alert
    showAlarmBanner(task);
    renderTasks();
  }

  function showAlarmBanner(task) {
    var banner = el.alarmBanner || document.querySelector('.todo-alarm-banner');
    if (!banner) return;
    banner.innerHTML =
      '<span class="alarm-icon">&#9200;</span> <strong>' +
      escapeHtml(task.name) +
      '</strong> — Alarm! ' +
      (task.dueTime || '') +
      ' <button class="btn ghost alarm-dismiss">Dismiss</button>';
    banner.style.display = 'flex';
    banner.querySelector('.alarm-dismiss').addEventListener('click', () => {
      banner.style.display = 'none';
    });
  }

  /* ---------- Filter + Sort + Render ---------- */
  function getFilteredTasks() {
    let list = [...tasks];
    const search = el.search.value.trim().toLowerCase();
    const statusF = el.filterStatus.value;
    const priorityF = el.filterPriority.value;
    const categoryF = el.filterCategory.value;
    const sortF = el.sortBy.value;

    if (search) list = list.filter((t) => t.name.toLowerCase().includes(search) || (t.notes && t.notes.toLowerCase().includes(search)));
    if (statusF === 'pending') list = list.filter((t) => !t.done);
    else if (statusF === 'done') list = list.filter((t) => t.done);
    if (priorityF !== 'all') list = list.filter((t) => t.priority === priorityF);
    if (categoryF !== 'all') list = list.filter((t) => t.category === categoryF);

    const priOrder = { High: 0, Medium: 1, Low: 2 };
    switch (sortF) {
      case 'newest': list.sort((a, b) => (b.createdAt || '').localeCompare(a.createdAt || '')); break;
      case 'oldest': list.sort((a, b) => (a.createdAt || '').localeCompare(b.createdAt || '')); break;
      case 'due': list.sort((a, b) => ((a.dueDate || '9') + (a.dueTime || '')).localeCompare((b.dueDate || '9') + (b.dueTime || ''))); break;
      case 'priority': list.sort((a, b) => (priOrder[a.priority] ?? 1) - (priOrder[b.priority] ?? 1)); break;
      case 'name': list.sort((a, b) => a.name.localeCompare(b.name)); break;
    }
    return list;
  }

  function renderTasks() {
    const filtered = getFilteredTasks();
    updateStats();

    if (el.visibleCount) el.visibleCount.textContent = filtered.length + ' of ' + tasks.length;

    if (filtered.length === 0) {
      el.taskList.innerHTML = '';
      el.emptyMsg.style.display = 'flex';
      return;
    }
    el.emptyMsg.style.display = 'none';

    let html = '';
    filtered.forEach((t) => {
      const priClass = 'pri-' + t.priority.toLowerCase();
      const doneClass = t.done ? 'task-done' : '';
      const overdue = isOverdue(t) ? 'task-overdue' : '';
      const alarmBadge = t.alarm && !t.alarmFired ? '<span class="alarm-badge mono">&#128276; Alarm</span>' : '';
      const alarmFiredBadge = t.alarmFired ? '<span class="alarm-fired-badge mono">&#9200; Fired</span>' : '';

      html += '<div class="todo-item ' + doneClass + ' ' + overdue + '" data-id="' + t.id + '">' +
        '<div class="todo-item-left">' +
          '<button class="todo-check" title="Toggle complete" data-action="toggle">' +
            (t.done ? '&#10003;' : '') +
          '</button>' +
          '<div class="todo-item-info">' +
            '<p class="todo-item-name">' + escapeHtml(t.name) + '</p>' +
            '<div class="todo-meta mono">' +
              '<span class="todo-cat">' + escapeHtml(t.category) + '</span>' +
              '<span class="todo-pri ' + priClass + '">' + t.priority + '</span>' +
              (t.dueDate ? '<span>&#128197; ' + formatDate(t.dueDate) + '</span>' : '') +
              (t.dueTime ? '<span>&#128336; ' + t.dueTime + '</span>' : '') +
              alarmBadge + alarmFiredBadge +
            '</div>' +
            (t.notes ? '<p class="todo-notes-preview">' + escapeHtml(t.notes) + '</p>' : '') +
          '</div>' +
        '</div>' +
        '<div class="todo-item-actions">' +
          '<button class="btn ghost small" data-action="edit" title="Edit">&#9998;</button>' +
          '<button class="btn ghost small danger" data-action="delete" title="Delete">&#128465;</button>' +
        '</div>' +
      '</div>';
    });

    el.taskList.innerHTML = html;

    // Attach events
    el.taskList.querySelectorAll('[data-action]').forEach((btn) => {
      btn.addEventListener('click', handleTaskAction);
    });
  }

  function handleTaskAction(e) {
    const btn = e.currentTarget;
    const action = btn.dataset.action;
    const item = btn.closest('.todo-item');
    const id = item.dataset.id;
    const task = tasks.find((t) => t.id === id);
    if (!task) return;

    if (action === 'toggle') {
      task.done = !task.done;
      if (task.done) task.alarmFired = true; // cancel alarm if completed
      saveTasks();
      scheduleAlarm(task);
      renderTasks();
    } else if (action === 'edit') {
      editingId = task.id;
      el.taskInput.value = task.name;
      el.category.value = task.category;
      el.priority.value = task.priority;
      el.date.value = task.dueDate || '';
      el.time.value = task.dueTime || '';
      el.alarm.value = task.alarm || '';
      el.notes.value = task.notes || '';
      el.addBtn.innerHTML = '&#9998; Update Task';
      el.taskInput.focus();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } else if (action === 'delete') {
      if (!confirm('Delete "' + task.name + '"?')) return;
      tasks = tasks.filter((t) => t.id !== id);
      if (alarmTimers[id]) { clearTimeout(alarmTimers[id]); delete alarmTimers[id]; }
      saveTasks();
      renderTasks();
    }
  }

  /* ---------- Bulk actions ---------- */
  function clearCompleted() {
    const count = tasks.filter((t) => t.done).length;
    if (!count) return flashStatus('No completed tasks to clear.', 'err');
    if (!confirm('Remove ' + count + ' completed task(s)?')) return;
    tasks = tasks.filter((t) => !t.done);
    saveTasks();
    renderTasks();
    flashStatus(count + ' completed task(s) cleared!', 'ok');
  }

  function clearAll() {
    if (!tasks.length) return flashStatus('No tasks to clear.', 'err');
    if (!confirm('Remove ALL ' + tasks.length + ' task(s)? This cannot be undone.')) return;
    tasks = [];
    Object.keys(alarmTimers).forEach((k) => { clearTimeout(alarmTimers[k]); });
    alarmTimers = {};
    saveTasks();
    renderTasks();
    flashStatus('All tasks cleared.', 'ok');
  }

  /* ---------- Stats ---------- */
  function updateStats() {
    const total = tasks.length;
    const done = tasks.filter((t) => t.done).length;
    const pending = total - done;
    const pct = total ? Math.round((done / total) * 100) : 0;

    el.totalCount.textContent = total;
    el.doneCount.textContent = done;
    el.pendingCount.textContent = pending;

    // Progress bar
    if (el.progressBar) el.progressBar.style.width = pct + '%';
    if (el.progressPct) el.progressPct.textContent = pct + '%';

    // Ring animations (circumference = 2*PI*15.9 = 100 via stroke-dasharray)
    if (el.ringTotal) el.ringTotal.style.strokeDashoffset = total ? 0 : 100;
    if (el.ringDone)  el.ringDone.style.strokeDashoffset = total ? 100 - (done / Math.max(total, 1)) * 100 : 100;
    if (el.ringPending) el.ringPending.style.strokeDashoffset = total ? 100 - (pending / Math.max(total, 1)) * 100 : 100;
  }

  /* ---------- Helpers ---------- */
  function isOverdue(task) {
    if (task.done || !task.dueDate) return false;
    const due = new Date(task.dueDate + (task.dueTime ? 'T' + task.dueTime : 'T23:59:59'));
    return Date.now() > due.getTime();
  }

  function formatDate(dateStr) {
    if (!dateStr) return '';
    const d = new Date(dateStr + 'T00:00:00');
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return d.getDate() + ' ' + months[d.getMonth()] + ' ' + d.getFullYear();
  }

  function escapeHtml(str) {
    const d = document.createElement('div');
    d.textContent = str;
    return d.innerHTML;
  }

  /* ---------- Boot ---------- */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  /* Expose for SPA re-init */
  window._todoInit = init;
})();
