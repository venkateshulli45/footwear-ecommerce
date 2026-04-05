(function () {
  var STORAGE_KEY = 'jagam-color-scheme';

  function normalize(value) {
    if (value === 'light' || value === 'dark') return value;
    return 'system';
  }

  function getStoredTheme() {
    try {
      return normalize(localStorage.getItem(STORAGE_KEY) || 'system');
    } catch (e) {
      return 'system';
    }
  }

  function isDarkEffective() {
    var t = document.documentElement.getAttribute('data-theme') || 'system';
    if (t === 'dark') return true;
    if (t === 'light') return false;
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  }

  function syncMetaThemeColor() {
    var meta = document.getElementById('meta-theme-color');
    if (!meta) return;
    meta.setAttribute('content', isDarkEffective() ? '#0f1412' : '#1e3a2f');
  }

  function setTriggerIcon(theme) {
    var icon = document.getElementById('theme-menu-icon');
    if (!icon) return;
    icon.className = 'bi theme-menu__icon ';
    var isDark = theme === 'dark' || (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);
    if (isDark) {
      icon.classList.add('bi-moon-stars-fill');
    } else {
      icon.classList.add('bi-sun-fill');
    }
  }

  function setTriggerLabel(theme) {
    var el = document.getElementById('theme-menu-label');
    if (!el) return;
    var label =
      theme === 'dark' ? 'Dark theme' : theme === 'light' ? 'Light theme' : 'Match system theme';
    el.textContent = 'Theme: ' + label;
  }

  function updateOptionSelection(theme) {
    theme = normalize(theme);
    document.querySelectorAll('.theme-menu__option[data-theme-choice]').forEach(function (btn) {
      var v = btn.getAttribute('data-theme-choice');
      var selected = v === theme;
      btn.setAttribute('aria-selected', selected ? 'true' : 'false');
    });
  }

  function apply(theme, persist) {
    theme = normalize(theme);
    document.documentElement.setAttribute('data-theme', theme);
    if (persist !== false) {
      try {
        localStorage.setItem(STORAGE_KEY, theme);
      } catch (e) {}
    }
    syncMetaThemeColor();
    setTriggerIcon(theme);
    setTriggerLabel(theme);
    updateOptionSelection(theme);
  }

  function closeMenu() {
    var panel = document.getElementById('theme-menu-panel');
    var trigger = document.getElementById('theme-menu-trigger');
    if (!panel || !trigger) return;
    panel.hidden = true;
    trigger.setAttribute('aria-expanded', 'false');
  }

  function openMenu() {
    var panel = document.getElementById('theme-menu-panel');
    var trigger = document.getElementById('theme-menu-trigger');
    if (!panel || !trigger) return;
    panel.hidden = false;
    trigger.setAttribute('aria-expanded', 'true');
  }

  function toggleMenu() {
    var panel = document.getElementById('theme-menu-panel');
    if (!panel) return;
    if (panel.hidden) openMenu();
    else closeMenu();
  }

  function init() {
    apply(getStoredTheme(), false);

    var trigger = document.getElementById('theme-menu-trigger');
    var panel = document.getElementById('theme-menu-panel');
    if (!trigger || !panel) return;

    trigger.addEventListener('click', function (e) {
      e.stopPropagation();
      toggleMenu();
    });

    document.addEventListener('click', function () {
      closeMenu();
    });

    panel.addEventListener('click', function (e) {
      e.stopPropagation();
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeMenu();
    });

    panel.querySelectorAll('.theme-menu__option[data-theme-choice]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var v = btn.getAttribute('data-theme-choice');
        apply(v, true);
        closeMenu();
      });
    });

    window
      .matchMedia('(prefers-color-scheme: dark)')
      .addEventListener('change', function () {
        var t = document.documentElement.getAttribute('data-theme');
        if (t === 'system') {
          syncMetaThemeColor();
          setTriggerIcon('system');
        }
      });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
