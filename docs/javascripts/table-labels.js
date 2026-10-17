(() => {
  function LabelTables() {
    document.querySelectorAll(".md-typeset table:not([class])").forEach((table) => {
      const heads = Array.from(table.querySelectorAll("thead th")).map((th) => th.textContent.trim());
      if (heads.length === 0) {
        return;
      }
      table.querySelectorAll("tbody tr").forEach((row) => {
        Array.from(row.children).forEach((cell, i) => {
          if (heads[i] && !cell.dataset.label) {
            cell.dataset.label = heads[i];
          }
        });
      });
    });
  }

  if (typeof document$ !== "undefined") {
    document$.subscribe(LabelTables);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", LabelTables);
  } else {
    LabelTables();
  }
})();
