/* =========================================================
   Aliens SVG Icon System — Apple SF Symbols Inspired
   Auto-injects icons into nav, buttons, stats, cards
   ========================================================= */
(function () {
  'use strict';

  /* ---- SVG wrapper ---- */
  function svg(paths, cls) {
    return '<svg class="' + (cls || 'icon') +
      '" viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
      'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">' +
      paths + '</svg>';
  }

  /* ---- Icon path library ---- */
  var P = {
    /* Navigation */
    home:     '<path d="M3 10.5L12 3l9 7.5"/><path d="M5 12v7a2 2 0 002 2h3v-5h4v5h3a2 2 0 002-2v-7"/>',
    about:    '<circle cx="12" cy="8" r="4"/><path d="M4 21v-1a7 7 0 0114 0v1"/>',
    projects: '<path d="M12 2L2 7l10 5 10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/>',
    star:     '<path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01z"/>',
    envelope: '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="M22 6l-10 7L2 6"/>',
    people:   '<path d="M16 21v-2a4 4 0 00-4-4H6a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/>',
    checklist:'<path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/>',

    /* Responsibility cards */
    target:   '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    chart:    '<path d="M18 20V10"/><path d="M12 20V4"/><path d="M6 20v-6"/>',
    lightbulb:'<path d="M9 18h6"/><path d="M10 22h4"/><path d="M12 2a7 7 0 00-4 12.7V17h8v-2.3A7 7 0 0012 2z"/>',
    document: '<path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6"/><path d="M16 13H8"/><path d="M16 17H8"/><path d="M10 9H8"/>',
    building: '<rect x="4" y="2" width="16" height="20" rx="2"/><path d="M9 22v-4h6v4"/><path d="M8 6h2"/><path d="M14 6h2"/><path d="M8 10h2"/><path d="M14 10h2"/><path d="M8 14h2"/><path d="M14 14h2"/>',
    flask:    '<path d="M9 3h6"/><path d="M10 9V3h4v6l5 8a2 2 0 01-1.7 3H6.7A2 2 0 015 17z"/>',
    globe:    '<circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/>',
    grid4:    '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/>',
    briefcase:'<rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v2"/>',

    /* Button / action icons */
    plus:     '<path d="M12 5v14"/><path d="M5 12h14"/>',
    save:     '<path d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z"/><path d="M17 21v-8H7v8"/><path d="M7 3v5h8"/>',
    copy:     '<rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/>',
    trash:    '<path d="M3 6h18"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6"/><path d="M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2"/>',
    wand:     '<path d="M15 4V2"/><path d="M15 16v-2"/><path d="M8 9h2"/><path d="M20 9h2"/><path d="M17.8 11.8L19 13"/><path d="M15 9h.01"/><path d="M17.8 6.2L19 5"/><path d="M11 6.2L9.7 5"/><path d="M3 21l9-9"/>',
    send:     '<path d="M22 2L11 13"/><path d="M22 2l-7 20-4-9-9-4z"/>',
    search:   '<circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>',
    xmark:    '<path d="M18 6L6 18"/><path d="M6 6l12 12"/>',
    eraser:   '<path d="M20 20H7L3 16l8-8 9 9-3 3"/><path d="M6 11l9 9"/>',

    /* Stat / info icons */
    layers:      '<path d="M12 2L2 7l10 5 10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/>',
    checkCircle: '<path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><path d="M22 4L12 14.01l-3-3"/>',
    clock:       '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    calendar:    '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4"/><path d="M8 2v4"/><path d="M3 10h18"/>',
    folder:      '<path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/>',
    eye:         '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>',
    database:    '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>',
    bell:        '<path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 01-3.46 0"/>',

    /* Tab / misc */
    list:   '<path d="M8 6h13"/><path d="M8 12h13"/><path d="M8 18h13"/><path d="M3 6h.01"/><path d="M3 12h.01"/><path d="M3 18h.01"/>',
    table:  '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/><path d="M3 15h18"/><path d="M9 3v18"/>',

    /* About page */
    heart:   '<path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z"/>',
    compass: '<circle cx="12" cy="12" r="10"/><path d="M16.24 7.76l-2.12 6.36-6.36 2.12 2.12-6.36z"/>',
    award:   '<circle cx="12" cy="8" r="6"/><path d="M15.477 12.89l1.414 6.764-4.89-2.695-4.89 2.695 1.414-6.764"/>',

    /* Contact */
    user:  '<path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    mail:  '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="M22 6l-10 7L2 6"/>',
    pen:   '<path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z"/>',

    /* Extra */
    link:  '<path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/>',
    download:'<path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><path d="M7 10l5 5 5-5"/><path d="M12 15V3"/>',
    filter: '<path d="M22 3H2l8 9.46V19l4 2v-8.54z"/>',
  };


  /* ============================================================
     1) NAVIGATION ICONS
     ============================================================ */
  var navMap = {
    'home':       'home',
    'about':      'about',
    'projects':   'projects',
    'characters': 'star',
    'gallery':    'star',
    'contact':    'envelope',
    'meeting':    'people',
    'todo':       'checklist',
  };

  function injectNavIcons(selector, iconCls) {
    document.querySelectorAll(selector).forEach(function (a) {
      var txt = a.textContent.trim().toLowerCase();
      var key = navMap[txt];
      if (key && P[key]) {
        a.innerHTML = svg(P[key], iconCls) + '<span>' + a.innerHTML + '</span>';
      }
    });
  }

  injectNavIcons('.quick-sidebar a', 'nav-icon');
  injectNavIcons('.main-nav a', 'nav-icon nav-icon-sm');


  /* ============================================================
     2) RESPONSIBILITY CARDS — replace emoji with SVG
     ============================================================ */
  var emojiMap = {
    '\uD83D\uDCCC': 'target',      // 📌
    '\uD83D\uDCCA': 'chart',       // 📊
    '\uD83D\uDC65': 'people',      // 👥
    '\uD83E\uDDE0': 'lightbulb',   // 🧠
    '\uD83E\uDDFE': 'document',    // 🧾
    '\uD83C\uDFE2': 'building',    // 🏢
    '\uD83E\uDDEA': 'flask',       // 🧪
    '\uD83C\uDF10': 'globe',       // 🌐
    '\uD83E\uDDE9': 'grid4',       // 🧩
    '\uD83D\uDCBC': 'briefcase',   // 💼
  };

  document.querySelectorAll('.resp-card h4').forEach(function (h4) {
    var text = h4.textContent;
    for (var emoji in emojiMap) {
      if (text.indexOf(emoji) !== -1) {
        var iconKey = emojiMap[emoji];
        h4.innerHTML = svg(P[iconKey], 'card-icon') + ' ' + text.replace(emoji, '').trim();
        break;
      }
    }
  });


  /* ============================================================
     3) STAT CARDS — inject icon before label
     ============================================================ */
  var statIconMap = {
    'total files':   'folder',
    'preview ready': 'eye',
    'total size':    'database',
    'total tasks':   'layers',
    'completed':     'checkCircle',
    'pending':       'clock',
    'today':         'calendar',
  };

  document.querySelectorAll('.meeting-stat').forEach(function (stat) {
    var label = stat.querySelector('p');
    if (!label) return;
    var key = label.textContent.trim().toLowerCase();
    var iconName = statIconMap[key];
    if (iconName && P[iconName]) {
      label.insertAdjacentHTML('beforebegin', svg(P[iconName], 'stat-icon'));
    }
  });


  /* ============================================================
     4) BUTTONS — inject icon by ID or text
     ============================================================ */
  var btnIdMap = {
    /* ToDo page */
    'tdAddBtn':    'plus',
    'tdClearForm': 'xmark',
    'tdClearDone': 'trash',
    'tdClearAll':  'trash',
    /* Meeting page */
    'tnGenerate':  'wand',
    'tnClear':     'eraser',
    'tnSave':      'save',
    'tnCopyTable': 'copy',
  };

  for (var id in btnIdMap) {
    var btn = document.getElementById(id);
    if (btn && P[btnIdMap[id]]) {
      btn.innerHTML = svg(P[btnIdMap[id]], 'btn-icon') + ' ' + btn.innerHTML;
    }
  }

  /* Contact form send button */
  document.querySelectorAll('.contact-form .btn').forEach(function (btn) {
    if (btn.textContent.trim().toLowerCase().indexOf('send') !== -1) {
      btn.innerHTML = svg(P.send, 'btn-icon') + ' ' + btn.innerHTML;
    }
  });

  /* Open Source File link */
  var openLink = document.getElementById('openSourceLink');
  if (openLink) {
    openLink.innerHTML = svg(P.link, 'btn-icon') + ' ' + openLink.innerHTML;
  }


  /* ============================================================
     5) TAB BUTTONS
     ============================================================ */
  document.querySelectorAll('.tab-btn').forEach(function (tab) {
    var txt = tab.textContent.trim().toLowerCase();
    var key = txt === 'records' ? 'list' : txt === 'table new' ? 'table' : null;
    if (key && P[key]) {
      tab.innerHTML = svg(P[key], 'btn-icon') + ' ' + tab.innerHTML;
    }
  });


  /* ============================================================
     6) SEARCH INPUTS — add icon prefix
     ============================================================ */
  document.querySelectorAll('input[type="search"], #tdSearch').forEach(function (input) {
    if (input.parentElement.classList.contains('search-icon-wrap')) return;
    var wrap = document.createElement('div');
    wrap.className = 'search-icon-wrap';
    input.parentNode.insertBefore(wrap, input);
    wrap.appendChild(input);
    wrap.insertAdjacentHTML('afterbegin', svg(P.search, 'search-icon'));
  });


  /* ============================================================
     7) ABOUT PAGE — panel headings
     ============================================================ */
  var aboutMap = {
    'strengths':     'heart',
    'vision':        'compass',
    'certification': 'award',
  };

  document.querySelectorAll('.about-grid h3').forEach(function (h3) {
    var txt = h3.textContent.trim().toLowerCase();
    var key = aboutMap[txt];
    if (key && P[key]) {
      h3.innerHTML = svg(P[key], 'heading-icon') + ' ' + h3.innerHTML;
    }
  });


  /* ============================================================
     8) HERO SECTION — heading icon
     ============================================================ */
  var respHeader = document.querySelector('.resp-section header h3');
  if (respHeader && respHeader.textContent.indexOf('Responsibilities') !== -1) {
    respHeader.innerHTML = svg(P.briefcase, 'heading-icon') + ' ' + respHeader.innerHTML;
  }

})();
