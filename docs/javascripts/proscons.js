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

  // 「ページ | 内容」の目次の表を、1 ページ 1 項目の縦のリスト(題名の下に説明)にする。
  function BuildPageLists() {
    document.querySelectorAll(".md-typeset table").forEach((table) => {
      if (table.dataset.pc) return;
      const heads = Array.from(table.querySelectorAll("thead th")).map((th) => th.textContent.trim());
      if (heads[0] !== "ページ" || heads.length < 2 || heads.length > 3) return;
      const descIndex = heads.findIndex((h, i) => i > 0 && h !== "重要度");
      if (descIndex < 0) return;
      const rows = Array.from(table.querySelectorAll("tbody tr"));
      const ok = rows.length >= 3 && rows.every((r) => {
        const a = r.firstElementChild && r.firstElementChild.querySelectorAll("a");
        return a && a.length === 1 && /\.md|\/$|\/#|\.html/.test(a[0].getAttribute("href") || "") === true;
      });
      if (!ok) return;
      table.dataset.pc = "list";
      const ul = document.createElement("ul");
      ul.className = "page-list";
      rows.forEach((r) => {
        const cells = Array.from(r.children);
        const li = document.createElement("li");
        const head = document.createElement("div");
        head.className = "pl-head";
        head.innerHTML = cells[0].innerHTML;
        heads.forEach((h, i) => {
          if (h === "重要度" && cells[i]) head.insertAdjacentHTML("beforeend", " " + cells[i].innerHTML);
        });
        const desc = document.createElement("div");
        desc.className = "pl-desc";
        desc.innerHTML = cells[descIndex].innerHTML;
        li.appendChild(head);
        li.appendChild(desc);
        ul.appendChild(li);
      });
      const wrap = table.closest(".md-typeset__scrollwrap") || table;
      wrap.replaceWith(ul);
    });
  }
  const Run = () => { Build(); BuildPageLists(); };
  if (typeof document$ !== "undefined") document$.subscribe(Run);
  else document.addEventListener("DOMContentLoaded", Run);
})();
