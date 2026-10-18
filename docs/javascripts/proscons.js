(() => {
  // 「長所 / 短所」の表を、左右 2 枚のカードにする。「コスト」の見出しの下の表は、値を大きく見せる。
  function Build() {
    document.querySelectorAll(".md-typeset table").forEach((table) => {
      if (table.dataset.pc) return;
      const rows = Array.from(table.querySelectorAll("tbody tr"));
      if (rows.length === 0) return;
      const labels = rows.map((r) => (r.firstElementChild ? r.firstElementChild.textContent.trim() : ""));
      if (labels.every((l) => l === "長所" || l === "短所")) {
        table.dataset.pc = "1";
        const box = document.createElement("div");
        box.className = "pc-box";
        [["長所", "pc-pro"], ["短所", "pc-con"]].forEach(([name, cls]) => {
          const col = document.createElement("div");
          col.className = "pc-col " + cls;
          const title = document.createElement("div");
          title.className = "pc-title";
          title.textContent = name;
          const ul = document.createElement("ul");
          rows.forEach((r, i) => {
            if (labels[i] === name) {
              const li = document.createElement("li");
              li.innerHTML = r.children[1].innerHTML;
              ul.appendChild(li);
            }
          });
          if (ul.children.length === 0) return;
          col.appendChild(title);
          col.appendChild(ul);
          box.appendChild(col);
        });
        const wrap = table.closest(".md-typeset__scrollwrap") || table.parentElement;
        (wrap.tagName === "DIV" && wrap.classList.contains("md-typeset__scrollwrap") ? wrap : table).replaceWith(box);
        return;
      }
      let h = table.closest(".md-typeset__scrollwrap") || table;
      while (h && !/^H[1-6]$/.test(h.tagName)) h = h.previousElementSibling;
      if (h && /^コスト/.test(h.textContent.replace(/¶/g, "").trim())) {
        table.dataset.pc = "cost";
        table.classList.add("pc-cost");
      }
    });
  }
  if (typeof document$ !== "undefined") document$.subscribe(Build);
  else document.addEventListener("DOMContentLoaded", Build);
})();
