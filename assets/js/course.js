/* UACB-604 shared helpers: deck setup, DNA utilities, quiz builder, tiny SVG charts */
(function (global) {
  'use strict';

  // ---------- Deck setup ----------
  function initDeck(opts) {
    opts = opts || {};
    Reveal.initialize(Object.assign({
      hash: true,
      slideNumber: 'c/t',
      width: 1280,
      height: 760,
      margin: 0.05,
      center: false,
      transition: 'fade',
      plugins: [RevealMath.KaTeX, RevealNotes],
    }, opts)).then(function () { if (global.Live) global.Live.init(); });
    addTimer();
    // Keep keyboard shortcuts from firing while students type in widgets
    document.addEventListener('keydown', function (e) {
      var t = e.target;
      if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA')) e.stopPropagation();
    }, true);
  }

  // Click the chip to start / pause a lecture clock; double-click to reset
  function addTimer() {
    var chip = document.createElement('div');
    chip.id = 'timer-chip';
    chip.title = 'Click: start/pause · Double-click: reset';
    document.body.appendChild(chip);
    var start = null, acc = 0, running = false;
    function fmt(ms) { var s = Math.floor(ms / 1000); return Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0'); }
    function draw() { chip.textContent = '⏱ ' + fmt(acc + (running ? Date.now() - start : 0)); }
    chip.addEventListener('click', function () {
      if (running) { acc += Date.now() - start; running = false; } else { start = Date.now(); running = true; }
      draw();
    });
    chip.addEventListener('dblclick', function () { acc = 0; running = false; draw(); });
    setInterval(function () { if (running) draw(); }, 1000);
    draw();
  }

  // ---------- DNA utilities ----------
  var COMP = { A: 'T', T: 'A', G: 'C', C: 'G', N: 'N' };
  function clean(s) { return (s || '').toUpperCase().replace(/[^ACGTN]/g, ''); }
  function revcomp(s) { return s.split('').reverse().map(function (c) { return COMP[c] || 'N'; }).join(''); }
  function counts(s) {
    var c = { A: 0, C: 0, G: 0, T: 0, N: 0 };
    for (var i = 0; i < s.length; i++) if (c[s[i]] !== undefined) c[s[i]]++;
    return c;
  }
  function randomSeq(n, gc) {
    gc = gc === undefined ? 0.5 : gc;
    var out = '';
    for (var i = 0; i < n; i++) {
      var r = Math.random();
      out += r < gc ? (Math.random() < 0.5 ? 'G' : 'C') : (Math.random() < 0.5 ? 'A' : 'T');
    }
    return out;
  }
  function colorSeq(s, max) {
    if (max && s.length > max) s = s.slice(0, max) + '…';
    return s.split('').map(function (c) {
      return 'ACGT'.indexOf(c) >= 0 ? '<span class="nt-' + c + '">' + c + '</span>' : c;
    }).join('');
  }
  function fmtNum(x) {
    if (!isFinite(x)) return '–';
    var a = Math.abs(x);
    if (a >= 1e9) return (x / 1e9).toFixed(a >= 1e10 ? 0 : 1) + ' G';
    if (a >= 1e6) return (x / 1e6).toFixed(a >= 1e7 ? 0 : 1) + ' M';
    if (a >= 1e4) return (x / 1e3).toFixed(0) + ' k';
    if (a >= 100) return x.toFixed(0);
    if (a >= 1) return x.toFixed(2);
    if (a === 0) return '0';
    return x.toExponential(1);
  }

  // ---------- Multiple-choice quiz ----------
  // mcq(el, {id, q, options:[...], answer: index, explain: 'html'})
  // In live class mode the first answer is final and is sent to the teacher.
  function mcq(el, spec) {
    var locked = false;
    el.classList.add('widget');
    var html = '<p style="margin:0.2em 0 0.4em"><b>' + spec.q + '</b></p><div class="opts"></div><div class="feedback"></div>';
    el.innerHTML = html;
    var opts = el.querySelector('.opts'), fb = el.querySelector('.feedback');
    spec.options.forEach(function (o, i) {
      var b = document.createElement('button');
      b.innerHTML = o;
      b.addEventListener('click', function () {
        if (locked) return;
        if (live()) { locked = true; report(el, spec.id || spec.q, stripTags(spec.q), i === spec.answer, stripTags(o)); }
        opts.querySelectorAll('button').forEach(function (x, j) {
          x.classList.remove('right', 'wrong');
          if (j === spec.answer) x.classList.add('right');
        });
        if (i !== spec.answer) b.classList.add('wrong');
        fb.className = 'feedback ' + (i === spec.answer ? 'ok' : 'no');
        fb.innerHTML = (i === spec.answer ? '✓ Correct. ' : '✗ Not quite. ') + (spec.explain || '');
      });
      opts.appendChild(b);
    });
  }

  // ---------- Matching game ----------
  // matchGame(el, [[left, right], ...], {id: 'prefix', label: 'Match', leftClass: 'mono'})
  // A pair scores (in live mode) only if matched on the first try.
  function matchGame(el, pairs, opts) {
    opts = opts || {};
    el.classList.add('widget');
    el.innerHTML = '<div class="match-grid"></div><div class="feedback"></div><p class="tiny">Matched <b class="m-ok">0</b>/' + pairs.length + ' · attempts <b class="m-tries">0</b></p>';
    var grid = el.querySelector('.match-grid'), fb = el.querySelector('.feedback');
    var selL = null, tries = 0, ok = 0, failed = {}, left = [];
    var order = pairs.map(function (_, i) { return i; }).sort(function () { return Math.random() - 0.5; });
    pairs.forEach(function (p, r) {
      var bl = document.createElement('button'); bl.innerHTML = p[0]; bl.dataset.i = r; if (opts.leftClass) bl.className = opts.leftClass;
      var br = document.createElement('button'); br.innerHTML = pairs[order[r]][1]; br.dataset.i = order[r];
      bl.onclick = function () { if (bl.classList.contains('done')) return; left.forEach(function (b) { b.classList.remove('chosen'); }); bl.classList.add('chosen'); selL = bl; };
      br.onclick = function () {
        if (!selL || br.classList.contains('done')) return;
        tries++; el.querySelector('.m-tries').textContent = tries;
        if (selL.dataset.i === br.dataset.i) {
          report(el, (opts.id || 'match') + '-' + selL.dataset.i, (opts.label || 'Match') + ': ' + stripTags(selL.innerHTML), !failed[selL.dataset.i], stripTags(br.innerHTML));
          selL.classList.remove('chosen'); selL.classList.add('done'); br.classList.add('done'); ok++; el.querySelector('.m-ok').textContent = ok;
          fb.className = 'feedback ok'; fb.textContent = ok === pairs.length ? '🎉 All matched in ' + tries + ' attempts!' : '✓ Matched.'; selL = null;
        } else {
          failed[selL.dataset.i] = true; br.classList.add('wrong'); setTimeout(function () { br.classList.remove('wrong'); }, 600);
          fb.className = 'feedback no'; fb.textContent = '✗ Try again.';
        }
      };
      left.push(bl); grid.appendChild(bl); grid.appendChild(br);
    });
  }

  // ---------- Flash-card quiz ----------
  // cardGame(el, [{html, options: [...], answer: i or [i, j], explain}], {id: 'prefix', label: 'Cards', shuffle: false})
  // One answer per card (first answer counts); "Next" moves on.
  function cardGame(el, cards, opts) {
    opts = opts || {};
    el.classList.add('widget');
    el.innerHTML = '<p class="tiny" style="text-align:center;margin:0">Card <span class="c-i">1</span> of ' + cards.length + ' · score <b class="c-s">0</b></p>' +
      '<div class="c-card" style="text-align:center;margin:0.3em 0"></div><div class="c-opts" style="text-align:center"></div>' +
      '<div class="feedback" style="text-align:center"></div><p style="text-align:center;margin:0.2em 0 0"><button class="primary c-next">Next →</button></p>';
    var i = 0, score = 0, answered = false, fb = el.querySelector('.feedback');
    function isRight(c, k) { return Array.isArray(c.answer) ? c.answer.indexOf(k) >= 0 : c.answer === k; }
    function show() {
      var c = cards[i]; answered = false; fb.textContent = '';
      el.querySelector('.c-i').textContent = i + 1; el.querySelector('.c-card').innerHTML = c.html;
      var box = el.querySelector('.c-opts'); box.innerHTML = '';
      c.options.forEach(function (o, k) {
        var b = document.createElement('button'); b.innerHTML = o;
        b.onclick = function () {
          if (answered) return; answered = true;
          var good = isRight(c, k); if (good) score++; el.querySelector('.c-s').textContent = score;
          box.querySelectorAll('button').forEach(function (x, j) { if (isRight(c, j)) x.classList.add('right'); });
          if (!good) b.classList.add('wrong');
          fb.className = 'feedback ' + (good ? 'ok' : 'no'); fb.innerHTML = (good ? '✓ ' : '✗ ') + (c.explain || '');
          report(el, (opts.id || 'card') + '-' + i, (opts.label || 'Card') + ' ' + (i + 1) + ': ' + stripTags(c.html).slice(0, 60), good, stripTags(o));
        };
        box.appendChild(b);
      });
    }
    el.querySelector('.c-next').onclick = function () {
      if (i < cards.length - 1) { i++; show(); } else { fb.className = 'feedback ok'; fb.textContent = 'Done! You scored ' + score + '/' + cards.length + '.'; }
    };
    show();
  }

  // ---------- Website tour: tabs of annotated screenshots ----------
  // sites: [{label, img, url, date, legend: ['what ① shows', ...], note, caption, optional}]
  // opts.compact: legend under the picture (for a tour inside half a slide)
  // A tab whose image is missing is hidden, so a hand-taken screenshot can be
  // dropped into assets/img/screens/ later and appears without editing the deck.
  function siteTour(el, sites, opts) {
    opts = opts || {};
    el.classList.add('tour'); if (opts.compact) el.classList.add('compact');
    var tabs = document.createElement('div'); tabs.className = 'tour-tabs';
    var body = document.createElement('div'); body.className = 'tour-body';
    body.innerHTML = '<figure class="shot"><img alt=""><figcaption class="tiny"></figcaption></figure><div class="tour-legend small"></div>';
    el.appendChild(tabs); el.appendChild(body);
    var img = body.querySelector('img'), cap = body.querySelector('figcaption'), leg = body.querySelector('.tour-legend');
    var btns = [];
    function show(k) {
      var s = sites[k];
      btns.forEach(function (b, j) { b.classList.toggle('chosen', j === k); });
      img.src = s.img; img.alt = 'Screenshot: ' + s.label;
      var host = s.url.replace(/^https?:\/\//, '').split('/')[0];
      cap.innerHTML = s.caption ? s.caption + ' · click to enlarge' : 'Screenshot of <a href="' + s.url + '" target="_blank" rel="noopener">' + host + '</a>' + (s.date ? ', ' + s.date : '') + ' · click to enlarge';
      leg.innerHTML = (s.legend || []).map(function (t, i) {
        return '<div class="tour-item"><span class="num">' + (i + 1) + '</span><span>' + t + '</span></div>';
      }).join('') + (s.note ? '<div class="callout q">' + s.note + '</div>' : '');
    }
    sites.forEach(function (s, k) {
      var b = document.createElement('button'); b.textContent = s.label; b.onclick = function () { show(k); };
      tabs.appendChild(b); btns.push(b);
      var probe = new Image();
      probe.onerror = function () { b.style.display = 'none'; if (b.classList.contains('chosen')) { var f = btns.filter(function (x) { return x.style.display !== 'none'; })[0]; if (f) f.click(); } };
      probe.src = s.img;
    });
    img.onclick = function () { zoom(img.src, img.alt); };
    show(sites.findIndex ? Math.max(0, sites.findIndex(function (s) { return !s.optional; })) : 0);
  }
  function zoom(src, alt) {
    var o = document.createElement('div'); o.className = 'shot-zoom';
    o.innerHTML = '<img alt="' + (alt || '') + '" src="' + src + '"><span>click anywhere to close</span>';
    o.onclick = function () { o.remove(); };
    document.body.appendChild(o);
  }

  // ---------- Live-class helpers ----------
  function live() { return !!(global.Live && global.Live.isStudent); }
  function report(el, qid, label, correct, answer) { if (global.Live) global.Live.report(el, qid, label, correct, answer); }
  function stripTags(s) { var d = document.createElement('div'); d.innerHTML = s; return d.textContent; }

  // ---------- Tiny SVG helpers ----------
  var NS = 'http://www.w3.org/2000/svg';
  function svgEl(tag, attrs, parent) {
    var e = document.createElementNS(NS, tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  function svgText(parent, x, y, txt, attrs) {
    var t = svgEl('text', Object.assign({ x: x, y: y, 'font-size': 14, fill: '#1d2433' }, attrs || {}), parent);
    t.textContent = txt;
    return t;
  }

  global.CG = {
    initDeck: initDeck, clean: clean, revcomp: revcomp, counts: counts, randomSeq: randomSeq,
    colorSeq: colorSeq, fmtNum: fmtNum, mcq: mcq, svgEl: svgEl, svgText: svgText,
    live: live, report: report, matchGame: matchGame, cardGame: cardGame,
    siteTour: siteTour, zoom: zoom,
  };
})(window);
