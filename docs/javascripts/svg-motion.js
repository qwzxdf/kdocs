(() => {
  const kSelector = "svg.motion";

  function Setup() {
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const svgs = document.querySelectorAll(kSelector);
    if (svgs.length === 0) return;

    if (reduce) {
      svgs.forEach((svg) => {
        if (svg.pauseAnimations) svg.pauseAnimations();
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
