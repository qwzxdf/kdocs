(() => {
  const kSelector = "svg.motion";
  const kPlay = "▶ アニメーションを再生";
  const kPause = "⏸ 一時停止";

  function AddButton(svg) {
    const next = svg.nextElementSibling;
    if (next && next.classList.contains("motion-play")) return next;
    const button = document.createElement("button");
    button.type = "button";
    button.className = "motion-play";
    svg.insertAdjacentElement("afterend", button);
    return button;
  }

  function Setup() {
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const svgs = document.querySelectorAll(kSelector);
    if (svgs.length === 0) return;

    svgs.forEach((svg) => {
      if (!svg.pauseAnimations) return;
      const button = AddButton(svg);
      const Refresh = () => {
        button.textContent = svg.animationsPaused() ? kPlay : kPause;
      };
      button.onclick = () => {
        if (svg.animationsPaused()) {
          if (svg.dataset.userPaused !== "1") svg.setCurrentTime(0);
          svg.dataset.userPaused = "0";
          svg.unpauseAnimations();
        } else {
          svg.dataset.userPaused = "1";
          svg.pauseAnimations();
        }
        Refresh();
      };
      if (reduce) {
        svg.pauseAnimations();
        const still = parseFloat(svg.getAttribute("data-still"));
        if (!isNaN(still)) svg.setCurrentTime(still);
      }
      Refresh();
    });

    if (reduce || !("IntersectionObserver" in window)) return;
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          const svg = entry.target;
          if (!svg.pauseAnimations || svg.dataset.userPaused === "1") return;
          if (entry.isIntersecting) svg.unpauseAnimations();
          else svg.pauseAnimations();
          const button = svg.nextElementSibling;
          if (button && button.classList.contains("motion-play")) {
            button.textContent = svg.animationsPaused() ? kPlay : kPause;
          }
        });
      },
      { threshold: 0.05 }
    );
    svgs.forEach((svg) => observer.observe(svg));
  }

  if (typeof document$ !== "undefined") {
    document$.subscribe(Setup);
  } else {
    document.addEventListener("DOMContentLoaded", Setup);
  }
})();
