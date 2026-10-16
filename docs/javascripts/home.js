(() => {
  function Setup() {
    const title = document.querySelector(".md-header__title");
    const logo = document.querySelector(".md-header__button.md-logo");
    if (!title || !logo || title.dataset.home) {
      return;
    }
    title.dataset.home = "1";
    title.setAttribute("role", "link");
    title.setAttribute("tabindex", "0");
    title.title = "ホームに戻る";
    const go = () => {
      window.location.href = logo.href;
    };
    title.addEventListener("click", go);
    title.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        go();
      }
    });
  }

  if (typeof document$ !== "undefined") {
    document$.subscribe(Setup);
  } else {
    document.addEventListener("DOMContentLoaded", Setup);
  }
})();
