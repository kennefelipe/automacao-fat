// Pilula deslizante da navegacao por abas (HUB OPERACIONAL).
// Roda no documento principal do Streamlit; a borda da frente anda mais
// rapido que a de tras, entao a pilula "estica" ao trocar de aba.
(function () {
  if (window.__hubNav) { window.__hubNav.sync(); return; }

  var reduzir = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var EASE = 'cubic-bezier(.65,0,.35,1)';

  function sync() {
    document.querySelectorAll('[data-testid="stTabs"] [role="tablist"]').forEach(function (tl) {
      var pill = tl.querySelector(':scope > .hub-pill');
      if (!pill) {
        pill = document.createElement('div');
        pill.className = 'hub-pill';
        tl.prepend(pill);
        tl.classList.add('hub-pill-on');
      }
      var sel = tl.querySelector('[role="tab"][aria-selected="true"]');
      if (!sel || !sel.offsetWidth) return;

      var L = sel.offsetLeft;
      var R = tl.clientWidth - (sel.offsetLeft + sel.offsetWidth);
      if (pill.dataset.l === String(L) && pill.dataset.r === String(R)) return;

      var primeira = pill.dataset.l === undefined;
      var paraDireita = L > parseFloat(pill.dataset.l || L);
      if (primeira || reduzir) {
        pill.style.transition = 'none';
      } else {
        pill.style.transition =
          'left ' + (paraDireita ? 0.55 : 0.36) + 's ' + EASE + ', ' +
          'right ' + (paraDireita ? 0.36 : 0.55) + 's ' + EASE;
      }
      pill.style.left = L + 'px';
      pill.style.right = R + 'px';
      pill.dataset.l = String(L);
      pill.dataset.r = String(R);
    });
  }

  var raf = 0;
  function agendar() { cancelAnimationFrame(raf); raf = requestAnimationFrame(sync); }

  new MutationObserver(agendar).observe(document.body, {
    subtree: true, childList: true, attributes: true, attributeFilter: ['aria-selected']
  });
  window.addEventListener('resize', agendar);
  if (document.fonts && document.fonts.ready) { document.fonts.ready.then(agendar); }

  window.__hubNav = { sync: sync };
  agendar();
})();
