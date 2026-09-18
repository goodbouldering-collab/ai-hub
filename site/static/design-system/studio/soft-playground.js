/* A local example only: no input collection, requests, storage or generation. */
(() => {
  'use strict';
  const root = document.getElementById('studio-playground');
  if (!root || root.dataset.softReady === 'true') return;
  const controls = root.querySelector('[data-sp-controls]');
  const tabs = [...root.querySelectorAll('[data-sp-tab]')];
  const panels = [...root.querySelectorAll('[data-sp-panel]')];
  const modes = [...root.querySelectorAll('input[name="studio-playground-mode"]')];
  const status = root.querySelector('[data-sp-status]');
  // A partial page must keep its readable, unenhanced fallback intact.
  if (!controls || !status || tabs.length !== 3 || panels.length !== 3 || modes.length !== 2) return;
  if (tabs.some(tab => !panels.some(panel => panel.dataset.spPanel === tab.dataset.spTab))) return;
  if (panels.some(panel => !panel.querySelector('[data-sp-mode="manual"]') || !panel.querySelector('[data-sp-mode="ai"]'))) return;

  let active = tabs[0].dataset.spTab;
  let mode = modes.find(input => input.checked)?.value === 'manual' ? 'manual' : 'ai';

  const render = (announce = false) => {
    tabs.forEach(tab => {
      const selected = tab.dataset.spTab === active;
      tab.setAttribute('aria-selected', String(selected));
      tab.tabIndex = selected ? 0 : -1;
    });
    panels.forEach(panel => {
      panel.hidden = panel.dataset.spPanel !== active;
      panel.querySelectorAll('[data-sp-mode]').forEach(example => {
        example.hidden = example.dataset.spMode !== mode;
      });
    });
    modes.forEach(input => { input.checked = input.value === mode; });
    root.dataset.spMode = mode;
    if (announce) {
      const label = tabs.find(tab => tab.dataset.spTab === active).textContent.trim();
      status.textContent = `${label}：${mode === 'ai' ? 'AIと進める' : '手作業で進める'}例を表示しています。`;
    }
  };

  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => {
      active = tab.dataset.spTab;
      render(true);
    });
    tab.addEventListener('keydown', event => {
      let next;
      if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
      else if (event.key === 'ArrowLeft') next = (index + tabs.length - 1) % tabs.length;
      else if (event.key === 'Home') next = 0;
      else if (event.key === 'End') next = tabs.length - 1;
      else return;
      event.preventDefault();
      active = tabs[next].dataset.spTab;
      render(true);
      tabs[next].focus();
    });
  });
  modes.forEach(input => {
    input.addEventListener('change', () => {
      if (!input.checked || !['manual', 'ai'].includes(input.value)) return;
      mode = input.value;
      render(true);
    });
  });
  panels.forEach(panel => {
    panel.setAttribute('role', 'tabpanel');
    panel.setAttribute('aria-labelledby', `studio-playground-tab-${panel.dataset.spPanel}`);
    panel.tabIndex = 0;
  });
  render();
  root.dataset.softReady = 'true';
  controls.hidden = false;
})();
