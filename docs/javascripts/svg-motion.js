(() => {
  const kSelector = "svg.motion";

  function Setup() {
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const svgs = document.querySelectorAll(kSelector);
    if (svgs.length === 0) return;

    if (reduce) {
      svgs.forEach((svg) => {
        if (!svg.pauseAnimations) return;
        svg.pauseAnimations();
        const still = parseFloat(svg.getAttribute("data-still"));
        if (!isNaN(still)) svg.setCurrentTime(still);
        if (svg.nextElementSibling && svg.nextElementSibling.classList.contains("motion-play")) return;
        const button = document.createElement("button");
        button.type = "button";
        button.className = "motion-play";
        button.textContent = "▶ アニメーションを再生";
        button.addEventListener("click", () => {
          if (svg.animationsPaused()) {
            svg.setCurrentTime(0);
            svg.unpauseAnimations();
            button.textContent = "⏸ 一時停止";
          } else {
            svg.pauseAnimations();
            button.textContent = "▶ アニメーションを再生";
          }
        });
        svg.insertAdjacentElement("afterend", button);
      });
      return;
    }

    if (!("IntersectionObserver" in window)) return;
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          const svg = entry.target;
          if (!svg.pauseAnimations) return;
          if (entry.isIntersecting) svg.unpauseAnimations();
          else svg.pauseAnimations();
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
