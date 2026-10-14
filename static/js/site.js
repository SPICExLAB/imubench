/* OmniIMU-Bench site: nav, reveal, finding toggles, task cards, leaderboard tabs, hero IMU trace, copy BibTeX. */
(function () {
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* nav: solid after scroll, mobile toggle */
  var nav = $('#nav');
  function onScroll() { if (nav) nav.classList.toggle('scrolled', window.scrollY > 10); }
  window.addEventListener('scroll', onScroll, { passive: true }); onScroll();
  var tog = $('.nav-toggle');
  if (tog) tog.addEventListener('click', function () { nav.classList.toggle('open'); tog.setAttribute('aria-expanded', nav.classList.contains('open')); });
  $$('.nav-links a').forEach(function (a) { a.addEventListener('click', function () { nav.classList.remove('open'); }); });

  /* reveal: visible at rest, animated in once when it enters the viewport */
  if (!reduce && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    $$('.reveal').forEach(function (el) { io.observe(el); });
  }

  /* findings: Discover more / Go back */
  $$('.finding').forEach(function (f) {
    $$('.discover, .back', f).forEach(function (b) {
      b.addEventListener('click', function () {
        f.classList.toggle('open');
        var open = f.classList.contains('open');
        $$('.discover', f).forEach(function (d) { d.setAttribute('aria-expanded', open); });
        if (!open) f.scrollIntoView({ block: 'nearest', behavior: reduce ? 'auto' : 'smooth' });
      });
    });
  });

  /* task cards */
  $$('.mcard').forEach(function (c) {
    c.addEventListener('click', function () { c.classList.toggle('open'); c.setAttribute('aria-expanded', c.classList.contains('open')); });
  });

  /* leaderboard protocol tabs */
  $$('.tabs').forEach(function (tabs) {
    var btns = $$('.tab', tabs);
    btns.forEach(function (b) {
      b.addEventListener('click', function () {
        btns.forEach(function (o) { o.setAttribute('aria-selected', o === b); var p = document.getElementById(o.getAttribute('aria-controls')); if (p) p.hidden = (o !== b); });
        $$('.tt-cap').forEach(function (c) { if (btns.some(function (o) { return o.getAttribute('aria-controls') === c.getAttribute('data-for'); })) c.hidden = (c.getAttribute('data-for') !== b.getAttribute('aria-controls')); });
      });
    });
  });

  /* figures: click to enlarge */
  $$('.f-fig img, figure.paper-fig img').forEach(function (img) {
    img.addEventListener('click', function () {
      var lb = document.createElement('div'); lb.className = 'lightbox'; lb.setAttribute('role', 'dialog'); lb.setAttribute('aria-label', img.alt || 'Figure');
      var big = document.createElement('img'); big.src = img.src; big.alt = img.alt; lb.appendChild(big);
      var fig = img.closest('figure'), cap = fig && fig.querySelector('figcaption');
      if (cap) { var c = document.createElement('p'); c.className = 'lb-cap'; c.textContent = cap.textContent.replace(/\s*Click a figure to enlarge\.?$/, ''); lb.appendChild(c); }
      function close() { lb.remove(); document.removeEventListener('keydown', onKey); }
      function onKey(e) { if (e.key === 'Escape') close(); }
      lb.addEventListener('click', close); document.addEventListener('keydown', onKey);
      document.body.appendChild(lb);
    });
  });

  /* copy BibTeX */
  $$('.copy-btn').forEach(function (b) {
    b.addEventListener('click', function () {
      var pre = $('pre', b.parentNode); if (!pre) return;
      var done = function () { b.textContent = 'Copied'; setTimeout(function () { b.textContent = 'Copy'; }, 1600); };
      var fallback = function () { var r = document.createRange(); r.selectNodeContents(pre); var s = window.getSelection(); s.removeAllRanges(); s.addRange(r); b.textContent = 'Selected'; setTimeout(function () { b.textContent = 'Copy'; }, 1600); };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(pre.textContent).then(done, fallback); else fallback();
    });
  });

  /* hero: six-channel IMU trace (acc x/y/z, gyro x/y/z) drawn on canvas */
  var cv = $('#imu-trace');
  if (cv && cv.getContext) {
    var ctx = cv.getContext('2d'), W = 0, H = 0, t0 = performance.now();
    var cols = ['#2f7d6b', '#c2662a', '#1d6f8f', '#7c5fa8', '#2f7d6b', '#c2662a'];
    var chans = [
      [[1.0, 0.0, 0.9], [2.3, 1.1, 0.25], [5.1, 0.4, 0.08]],
      [[1.0, 1.3, 0.7], [3.1, 0.2, 0.3], [7.2, 2.0, 0.06]],
      [[1.0, 2.6, 1.0], [1.9, 0.9, 0.35], [6.4, 1.4, 0.07]],
      [[1.0, 0.4, 0.6], [2.7, 2.2, 0.4], [8.3, 0.7, 0.05]],
      [[1.0, 1.9, 0.8], [3.6, 0.6, 0.2], [5.7, 2.8, 0.09]],
      [[1.0, 3.1, 0.5], [2.1, 1.7, 0.45], [9.0, 0.1, 0.04]]
    ];
    function size() {
      var r = cv.getBoundingClientRect(), d = Math.min(window.devicePixelRatio || 1, 2);
      W = Math.max(1, Math.floor(r.width)); H = Math.max(1, Math.floor(r.height));
      cv.width = W * d; cv.height = H * d; ctx.setTransform(d, 0, 0, d, 0, 0);
    }
    function sig(c, x) { var v = 0, k = chans[c]; for (var i = 0; i < k.length; i++) v += k[i][2] * Math.sin(k[i][0] * x + k[i][1]); return v; }
    function draw(now) {
      var t = reduce ? 0 : (now - t0) / 1000;
      ctx.clearRect(0, 0, W, H);
      var lanes = 6, top = H * 0.08, lane = (H * 0.84) / lanes;
      ctx.lineWidth = 1.2;
      for (var c = 0; c < lanes; c++) {
        var y0 = top + lane * (c + 0.5), amp = lane * 0.42;
        ctx.strokeStyle = cols[c]; ctx.globalAlpha = 0.5;
        ctx.beginPath();
        for (var x = 0; x <= W; x += 3) {
          var u = x / 110 + t * 0.45 + c * 0.7;
          var y = y0 - amp * sig(c, u);
          if (x === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
        }
        ctx.stroke();
      }
      ctx.globalAlpha = 1;
      if (!reduce) requestAnimationFrame(draw);
    }
    size(); window.addEventListener('resize', function () { size(); if (reduce) draw(performance.now()); });
    requestAnimationFrame(draw);
  }
})();
