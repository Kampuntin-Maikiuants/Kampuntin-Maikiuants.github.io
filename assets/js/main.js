// Maikiuants · Kampuntin – kleine Helfer. Die Seite funktioniert auch ohne JavaScript.
document.addEventListener('DOMContentLoaded', () => {
  const $ = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));

  // --- Mobiles Menü -----------------------------------------------------
  const burger = $('.burger');
  if (burger) {
    const setOpen = (open) => {
      burger.setAttribute('aria-expanded', String(open));
      document.body.classList.toggle('nav-open', open);
    };
    burger.addEventListener('click', () => setOpen(burger.getAttribute('aria-expanded') !== 'true'));
    $('#site-nav').addEventListener('click', (e) => { if (e.target.closest('a')) setOpen(false); });
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && burger.getAttribute('aria-expanded') === 'true') { setOpen(false); burger.focus(); }
    });
  }

  // --- Lightbox für Fotos -------------------------------------------------
  const lightbox = $('#lightbox');
  if (lightbox && typeof lightbox.showModal === 'function') {
    const img = $('img', lightbox);
    const caption = $('figcaption', lightbox);
    let list = [];
    let index = 0;
    const show = (i) => {
      index = (i + list.length) % list.length;
      const link = list[index];
      img.src = link.href;
      img.alt = link.dataset.caption || '';
      caption.textContent = (link.dataset.caption || '') + (list.length > 1 ? ` · ${index + 1} / ${list.length}` : '');
    };
    document.addEventListener('click', (e) => {
      const link = e.target.closest('a[data-lightbox]');
      if (!link) return;
      e.preventDefault();
      // Album: alle Fotos desselben Albums (auch die versteckten), sonst alle sichtbaren Fotos
      // Album: nach Dateinummer sortieren, damit die Zählung (z. B. 12 / 14) zur Nummer im Dateinamen passt
      list = link.dataset.album
        ? $$(`a[data-lightbox][data-album="${CSS.escape(link.dataset.album)}"]`)
            .sort((a, b) => a.getAttribute('href').localeCompare(b.getAttribute('href'), undefined, { numeric: true }))
        : $$('a[data-lightbox]').filter((a) => !a.closest('[hidden]'));
      show(list.indexOf(link));
      lightbox.showModal();
    });
    lightbox.addEventListener('click', (e) => {
      if (e.target === lightbox || e.target.closest('[data-close]')) lightbox.close();
      else if (e.target.closest('[data-prev]')) show(index - 1);
      else if (e.target.closest('[data-next]')) show(index + 1);
    });
    lightbox.addEventListener('close', () => { img.src = 'data:,'; });
    lightbox.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowLeft') show(index - 1);
      if (e.key === 'ArrowRight') show(index + 1);
    });
  }

  // --- Einbettungen erst nach Klick laden (Datenschutz) -------------------
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('button[data-embed]');
    if (!btn) return;
    const box = btn.closest('.embed');
    const src = btn.dataset.src;
    if (btn.dataset.embed === 'instagram') {
      const quote = document.createElement('blockquote');
      quote.className = 'instagram-media';
      quote.setAttribute('data-instgrm-permalink', src);
      quote.setAttribute('data-instgrm-version', '14');
      box.replaceChildren(quote);
      if (window.instgrm) {
        window.instgrm.Embeds.process();
      } else {
        const script = document.createElement('script');
        script.src = 'https://www.instagram.com/embed.js';
        script.async = true;
        document.body.append(script);
      }
    } else {
      const frame = document.createElement('iframe');
      frame.src = src;
      frame.title = btn.dataset.title || '';
      frame.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
      frame.allowFullscreen = true;
      box.replaceChildren(frame);
    }
    box.classList.add('loaded');
  });

  // --- Kleines Fenster mit dem nächsten Tour-Termin (Startseite) -----------
  // Erscheint bei jedem Aufruf der Startseite nach ein paar Sekunden; × oder Esc schließt es.
  const popup = $('#tour-popup');
  if (popup) {
    const close = () => {
      popup.classList.remove('is-visible');
      window.setTimeout(() => { popup.hidden = true; }, 350);
    };
    $('.tour-popup__close', popup).addEventListener('click', close);
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && popup.classList.contains('is-visible') && !$('dialog[open]')) close();
    });
    window.setTimeout(() => {
      popup.hidden = false;
      void popup.offsetWidth; // Layout erzwingen, damit die Einblend-Animation startet
      popup.classList.add('is-visible');
    }, 3500);
  }

  // --- Tour: Leistungen und Packliste nur auf dem Handy zugeklappt, am Computer immer offen ----
  const wide = window.matchMedia('(min-width: 760px)');
  const syncToggles = () => document.querySelectorAll('.panel--toggle').forEach((d) => { d.open = wide.matches; });
  syncToggles();
  wide.addEventListener('change', syncToggles);
  document.querySelectorAll('.panel--toggle summary').forEach((s) => {
    s.addEventListener('click', (e) => { if (wide.matches) e.preventDefault(); });
  });

  // --- Aufklappbare Reiseprogramme: ein Link auf #id öffnet das <details> ----
  const openDetails = (hash) => {
    if (!hash || hash.length < 2) return;
    const el = document.getElementById(decodeURIComponent(hash.slice(1)));
    if (el && el.tagName === 'DETAILS') el.open = true;
  };
  openDetails(location.hash);
  window.addEventListener('hashchange', () => openDetails(location.hash));
  document.querySelectorAll('a[href^="#"]').forEach((a) => {
    a.addEventListener('click', () => openDetails(a.getAttribute('href')));
  });

  // --- Kopfbild bewegt sich beim Scrollen langsamer mit (Parallax) ----------
  const heroBg = $('.page-hero__bg');
  if (heroBg && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    let ticking = false;
    const update = () => {
      const y = window.scrollY;
      if (y < window.innerHeight * 1.5) heroBg.style.transform = `translate3d(0, ${Math.round(y * 0.35)}px, 0)`;
      ticking = false;
    };
    window.addEventListener('scroll', () => {
      if (!ticking) { ticking = true; window.requestAnimationFrame(update); }
    }, { passive: true });
  }
});
