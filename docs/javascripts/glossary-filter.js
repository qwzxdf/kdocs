(() => {
  function Setup() {
    const input = document.getElementById("glossary-filter");
    if (!input) return;
    const rows = Array.from(document.querySelectorAll(".md-typeset table tbody tr"));
    const headings = Array.from(document.querySelectorAll(".md-typeset h2[id^='g-']"));

    function Apply() {
      const query = input.value.trim().toLowerCase();
      rows.forEach((row) => {
        const hit = query === "" || row.textContent.toLowerCase().includes(query);
        row.style.display = hit ? "" : "none";
      });
      headings.forEach((heading) => {
        let node = heading.nextElementSibling;
        while (node && node.tagName !== "TABLE" && !/^H[1-6]$/.test(node.tagName)) {
          node = node.nextElementSibling;
        }
        if (!node || node.tagName !== "TABLE") return;
        const visible = Array.from(node.querySelectorAll("tbody tr")).some((r) => r.style.display !== "none");
        heading.style.display = visible ? "" : "none";
        node.style.display = visible ? "" : "none";
      });
    }

    input.addEventListener("input", Apply);
  }

  if (typeof document$ !== "undefined") {
    document$.subscribe(Setup);
  } else {
    document.addEventListener("DOMContentLoaded", Setup);
  }
})();
