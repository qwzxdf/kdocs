(() => {
  function LabelTables() {
    document.querySelectorAll(".md-typeset table:not([class])").forEach((table) => {
      const heads = Array.from(table.querySelectorAll("thead th")).map((th) => th.textContent.trim());
      if (heads.length === 0) {
        return;
      }
      const visible = heads.filter((h) => h !== "重要度");
      if (visible.length === 2) {
        const mapHeads = ["項目", "要素", "場面", "場合", "状況", "目的", "やりたいこと", "対象", "部品", "段階", "種類", "フェーズ", "使う場面", "用途", "場所", "タイミング", "症状", "状態", "入力", "やること", "例"];
        table.dataset.tbl = mapHeads.includes(visible[0]) ? "map" : "term";
      } else if (visible.length >= 3) {
        table.dataset.tbl = "wide";
      }
      table.querySelectorAll("tbody tr").forEach((row) => {
        const firstText = row.firstElementChild ? row.firstElementChild.textContent.trim() : "";
        if (firstText.length > 9) {
          row.dataset.long = "1";
        }
        Array.from(row.children).forEach((cell, i) => {
          if (heads[i] && !cell.dataset.label) {
            cell.dataset.label = heads[i];
          }
        });
        const rank = row.querySelector('td[data-label="重要度"] .rank');
        const first = row.firstElementChild;
        if (rank && first && !first.querySelector(".rank-inline")) {
          const badge = rank.cloneNode(true);
          badge.classList.add("rank-inline");
          first.appendChild(document.createTextNode(" "));
          first.appendChild(badge);
        }
      });
      // 1 行でも長いラベルがあれば、全行を同じ並べ方（ラベルの下に説明）にそろえる。
      // 混ざっていると、短い行だけ幅の広い枠になって、そろわない。
      if (table.dataset.tbl === "term" && table.querySelector("tbody tr[data-long]")) {
        table.querySelectorAll("tbody tr").forEach((row) => {
          row.dataset.long = "1";
        });
      }
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
