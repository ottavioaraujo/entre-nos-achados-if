(() => {
  const overlay = document.querySelector(".transition");
  const background = document.querySelector(".transition-bg");
  const texts = Array.from(document.querySelectorAll(".page-transition-text"));
  if (!overlay || !background || texts.length < 2) return;

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

  const textAnimations = texts.map((text) =>
    text.animate(
      text.classList.contains("is-welcome")
        ? [{ transform: "translateX(calc(52vw + 50%))" }, { transform: "translateX(0)" }]
        : [{ transform: "translateX(0)" }, { transform: "translateX(calc(-52vw - 50%))" }],
      { duration: 1900, easing, fill: "forwards" }
    )
  );
  const backgroundAnimation = background.animate(
    [{ transform: "scale(1)" }, { transform: "scale(0)" }],
    { duration: 600, delay: 2400, easing: "ease", fill: "forwards" }
  );

  animations = [...textAnimations, backgroundAnimation];
  safetyTimer = window.setTimeout(finish, 4200);
  backgroundAnimation.finished.then(finish).catch(finish);
})();
