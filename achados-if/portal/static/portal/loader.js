(() => {
  const loader = document.querySelector(".page-loader");
  if (!loader) return;

  const startedAt = performance.now();
  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const minimumDuration = prefersReducedMotion ? 0 : 650;
  let dismissed = false;

  const dismiss = () => {
    if (dismissed) return;
    dismissed = true;
    loader.classList.add("page-loader--loaded");
    const remaining = Math.max(0, minimumDuration - (performance.now() - startedAt));

    window.setTimeout(() => {
      loader.classList.add("page-loader--leaving");
      window.setTimeout(() => loader.remove(), 620);
    }, remaining);
  };

  if (document.readyState === "complete") {
    dismiss();
  } else {
    window.addEventListener("load", dismiss, { once: true });
  }

  // Never let the cover stay on screen if a third-party asset stalls.
  window.setTimeout(dismiss, 2200);
})();
