(() => {
  const kCodeLike = /^[\x20-\x7e]+$/;

  function Setup() {
    document
      .querySelectorAll(".md-nav--secondary .md-nav__item .md-nav .md-nav__link")
      .forEach((link) => {
        const text = link.textContent.trim();
        if (kCodeLike.test(text)) {
          link.classList.add("toc-code");
        }
      });
  }

  if (typeof document$ !== "undefined") {
    document$.subscribe(Setup);
  } else {
    document.addEventListener("DOMContentLoaded", Setup);
  }
})();
