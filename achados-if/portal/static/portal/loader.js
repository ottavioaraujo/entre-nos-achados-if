(() => {
  const overlay = document.querySelector(".transition");
  const background = document.querySelector(".transition-bg");
  const brand = document.querySelector(".page-transition-text.is-brand");
  const welcome = document.querySelector(".page-transition-text.is-welcome");
  if (!overlay || !background || !brand || !welcome) return;

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduceMotion || typeof background.animate !== "function") {
    overlay.style.display = "none";
    return;
  }

  const easing = "cubic-bezier(0.76, 0, 0.24, 1)";
  let animations = [];
  let finished = false;
  let safetyTimer;

  document.body.classList.add("no-scroll-transition");
  document.body.setAttribute("aria-busy", "true");
  overlay.style.display = "block";

  const finish = () => {
    if (finished) return;
    finished = true;
    window.clearTimeout(safetyTimer);
    animations.forEach((animation) => animation.cancel());
    overlay.style.display = "none";
    document.body.classList.remove("no-scroll-transition");
    document.body.removeAttribute("aria-busy");
  };

  const brandAnimation = brand.animate(
    [
      { opacity: 0, transform: "translateY(12px)", offset: 0 },
      { opacity: 1, transform: "translateY(0)", offset: 0.25 },
      { opacity: 1, transform: "translateY(0)", offset: 0.72 },
      { opacity: 0, transform: "translateY(-10px)", offset: 1 }
    ],
    { duration: 1400, easing, fill: "forwards" }
  );
  const welcomeAnimation = welcome.animate(
    [
      { opacity: 0, transform: "translateY(12px)" },
      { opacity: 1, transform: "translateY(0)" }
    ],
    { duration: 500, delay: 1350, easing, fill: "both" }
  );
  const backgroundAnimation = background.animate(
    [{ transform: "scale(1)" }, { transform: "scale(0)" }],
    { duration: 800, delay: 2000, easing: "ease", fill: "forwards" }
  );

  animations = [brandAnimation, welcomeAnimation, backgroundAnimation];
  safetyTimer = window.setTimeout(finish, 3800);
  backgroundAnimation.finished.then(finish).catch(finish);
})();
