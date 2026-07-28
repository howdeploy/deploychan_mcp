(function () {
  const root = document.documentElement;
  const script = document.currentScript;
  const compactBreakpoint = Number(script?.dataset.compactBreakpoint) || 880;
  const touchBreakpoint = Number(script?.dataset.touchBreakpoint) || 1024;
  const compactWidth = window.matchMedia(`(max-width: ${compactBreakpoint}px)`);
  const compactTouch = window.matchMedia(`(hover: none) and (pointer: coarse) and (max-width: ${touchBreakpoint}px)`);
  const touchInput = window.matchMedia('(hover: none), (pointer: coarse)');

  function applyDeviceProfile() {
    const compact = compactWidth.matches || compactTouch.matches;
    const viewportHeight = window.visualViewport?.height || window.innerHeight;

    root.dataset.layout = compact ? 'compact' : 'desktop';
    root.dataset.input = touchInput.matches ? 'touch' : 'pointer';
    root.dataset.orientation = window.innerWidth > viewportHeight ? 'landscape' : 'portrait';
    root.style.setProperty('--app-height', `${Math.round(viewportHeight)}px`);

    window.dispatchEvent(new CustomEvent('deviceprofilechange', {
      detail: { compact, touch: touchInput.matches },
    }));
  }

  [compactWidth, compactTouch, touchInput].forEach((query) => {
    if (query.addEventListener) query.addEventListener('change', applyDeviceProfile);
    else query.addListener(applyDeviceProfile);
  });
  window.visualViewport?.addEventListener('resize', applyDeviceProfile, { passive: true });
  window.addEventListener('orientationchange', applyDeviceProfile, { passive: true });
  applyDeviceProfile();
}());
