/* UACB-604 live classroom client.
 * Solo mode (no ?role=...): does nothing, slides work offline / on GitHub Pages.
 * ?role=teacher&key=...   : broadcasts the current slide, shows results with names when you leave a slide.
 * ?role=student           : follows the teacher's slide, sends answers to games and quizzes.
 */
(function (global) {
  'use strict';
  var params = new URLSearchParams(location.search);
  var inFrame = window.top !== window.self || params.has('receiver');   // speaker-view previews must stay passive
  var role = inFrame ? null : params.get('role');
  var key = params.get('key') || '';
  var deck = location.pathname.replace(/^\//, '');
  var STORE = 'uacb604-student';
  var me = null, sent = {};

  function loadMe() { try { return JSON.parse(localStorage.getItem(STORE) || 'null'); } catch (e) { return null; } }
  function post(path, body) {
    return fetch(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
      .then(function (r) { return r.json().then(function (j) { j._status = r.status; return j; }); });
  }
  function el(tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }
  function esc(s) { var d = document.createElement('div'); d.textContent = s; return d.innerHTML; }

  var chip;
  function setChip(html) { if (!chip) { chip = el('div', null); chip.id = 'live-chip'; document.body.appendChild(chip); } chip.innerHTML = html; }

  // ------------------------------------------------------------ student
  function initStudent() {
    me = loadMe();
    if (!me || !me.id) { location.href = '/classroom/join.html'; return; }
    document.documentElement.classList.add('live-student');
    Reveal.configure({ controls: false, keyboard: false, touch: false, overview: false, hash: false, help: false });
    var t = document.getElementById('timer-chip'); if (t) t.style.display = 'none';
    setChip('👤 ' + esc(me.name) + ' · connecting…');
    var es = new EventSource('/api/events');
    es.onopen = function () { setChip('👤 ' + esc(me.name) + ' · <span class="live-dot"></span> live'); };
    es.onerror = function () { setChip('👤 ' + esc(me.name) + ' · reconnecting…'); };
    es.onmessage = function (ev) {
      var s = JSON.parse(ev.data);
      if (!s.deck) return;
      if (s.deck !== deck) { es.close(); location.href = '/' + s.deck + '?role=student'; return; }
      var cur = Reveal.getIndices();
      if (cur.h !== s.h || (cur.v || 0) !== s.v || (cur.f == null ? -1 : cur.f) !== s.f) Reveal.slide(s.h, s.v, s.f);
    };
  }

  // ------------------------------------------------------------ teacher
  var overlay = null;
  function closeOverlay() { if (overlay) { overlay.remove(); overlay = null; } }
  function showOverlay(title, res, forceBoard) {
    closeOverlay();
    overlay = el('div'); overlay.id = 'live-overlay';
    var card = el('div', 'live-card');
    card.appendChild(el('div', 'kicker', 'Results'));
    card.appendChild(el('h2', null, esc(title)));
    var qs = res.questions;
    if (!forceBoard && qs.length && qs.length <= 4) {
      qs.forEach(function (q) {
        var box = el('div', 'live-q');
        var n = q.right.length + q.wrong.length;
        box.appendChild(el('div', 'live-qlabel', esc(q.label) + ' <span class="muted">· ' + q.right.length + ' of ' + n + ' correct</span>'));
        var chips = el('div', 'live-chips');
        q.right.forEach(function (name) { chips.appendChild(el('span', 'live-name ok', '✓ ' + esc(name))); });
        if (!q.right.length) chips.appendChild(el('span', 'muted', 'Nobody yet!'));
        box.appendChild(chips);
        card.appendChild(box);
      });
    } else {
      var ol = el('ol', 'live-board');
      var medals = ['🥇', '🥈', '🥉'];
      res.board.slice(0, 12).forEach(function (b, i) {
        ol.appendChild(el('li', i < 3 ? 'top' : '',
          '<b>' + (medals[i] ? medals[i] + ' ' : '') + esc(b.name) + '</b><span>' + b.correct + ' / ' + b.attempted + ' correct</span>'));
      });
      card.appendChild(ol);
      if (res.board.length > 12) card.appendChild(el('p', 'muted', '+ ' + (res.board.length - 12) + ' more'));
    }
    card.appendChild(el('p', 'tiny', res.board.length + ' of ' + res.students + ' students answered · press any key or click to continue'));
    overlay.appendChild(card);
    overlay.addEventListener('click', closeOverlay);
    document.body.appendChild(overlay);
  }
  function fetchResults(slide) {
    var q = '/api/results?key=' + encodeURIComponent(key) + '&deck=' + encodeURIComponent(deck) + (slide == null ? '' : '&slide=' + slide);
    return fetch(q).then(function (r) { return r.json(); });
  }
  function slideTitle(h) {
    var s = Reveal.getSlide(h); var t = s && s.querySelector('h2');
    return t ? t.textContent : 'Slide ' + (h + 1);
  }

  function initTeacher() {
    document.documentElement.classList.add('live-teacher');
    function broadcast() {
      var i = Reveal.getIndices();
      post('/api/state', { key: key, deck: deck, h: i.h, v: i.v || 0, f: i.f == null ? -1 : i.f }).then(function (r) {
        if (r._status === 403) setChip('⚠ wrong teacher key');
      });
    }
    Reveal.on('slidechanged', function (e) {
      broadcast();
      if (e.previousSlide) {
        var prevH = Reveal.getIndices(e.previousSlide).h;
        if (prevH === e.indexh) return;
        var board = e.previousSlide.getAttribute('data-results') === 'board';
        fetchResults(prevH).then(function (res) { if (res.questions && res.questions.length) showOverlay(slideTitle(prevH), res, board); });
      }
    });
    Reveal.on('fragmentshown', broadcast);
    Reveal.on('fragmenthidden', broadcast);
    broadcast();

    // Any key closes the results overlay instead of moving the slides
    document.addEventListener('keydown', function (e) {
      if (!overlay) return;
      e.preventDefault(); e.stopImmediatePropagation(); closeOverlay();
    }, true);
    Reveal.addKeyBinding({ keyCode: 76, key: 'L', description: 'Class leaderboard (whole lecture)' }, function () {
      fetchResults(null).then(function (res) { showOverlay('Leaderboard: this lecture', res, true); });
    });

    var es = new EventSource('/api/events');
    es.onmessage = function (ev) {
      var s = JSON.parse(ev.data);
      setChip('<span class="live-dot"></span> live · 👥 ' + s.joined + ' joined · ✍ ' + s.answered + ' answered this slide');
    };
    es.onerror = function () { setChip('⚠ server not reachable'); };
  }

  // ------------------------------------------------------------ public API
  var Live = {
    role: role,
    isStudent: role === 'student',
    init: function () {
      if (role === 'student') initStudent();
      else if (role === 'teacher') initTeacher();
    },
    /* report(el, qid, label, correct, answer): first answer per question counts */
    report: function (elm, qid, label, correct, answer) {
      if (role !== 'student' || !me || sent[qid]) return;
      sent[qid] = true;
      var sec = elm && elm.closest ? elm.closest('section') : null;
      var slide = sec ? Reveal.getIndices(sec).h : Reveal.getIndices().h;
      post('/api/answer', { id: me.id, deck: deck, slide: slide, qid: qid, label: label, correct: !!correct, answer: String(answer == null ? '' : answer) })
        .then(function (r) { if (r._status === 401) location.href = '/classroom/join.html'; })
        .catch(function () { sent[qid] = false; });
    }
  };
  global.Live = Live;
})(window);
