(() => {
  function Toggle(element) {
    const revealed = element.classList.toggle("revealed");
    element.setAttribute("aria-expanded", revealed ? "true" : "false");
  }

  function Setup() {
    document.querySelectorAll(".spoiler").forEach((element) => {
      if (element.dataset.spoiler) {
        return;
      }
      element.dataset.spoiler = "1";
      element.setAttribute("role", "button");
      element.setAttribute("tabindex", "0");
      element.setAttribute("aria-expanded", "false");
      element.title = "クリックで答えを表示";
      element.addEventListener("click", () => Toggle(element));
      element.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          Toggle(element);
        }
      });
    });
  }

  if (typeof document$ !== "undefined") {
    document$.subscribe(Setup);
  } else {
    document.addEventListener("DOMContentLoaded", Setup);
  }
})();
