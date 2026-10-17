(() => {
  function Normalize(text) {
    return text
      .toLowerCase()
      .replace(/[（(].*?[）)]/g, "")
      .replace(/std::/g, "")
      .replace(/[<>]/g, "")
      .trim();
  }

  function Rank(title, query) {
    const names = title.split("/").map(Normalize);
    if (names.some((name) => name === query)) {
      return 0;
    }
    if (names.some((name) => name.startsWith(query))) {
      return 1;
    }
    if (names.some((name) => name.includes(query))) {
      return 2;
    }
    return 3;
  }

  function Sort(list, input) {
    const query = Normalize(input.value);
    if (query === "") {
      return;
    }
    const items = [...list.children];
    const ranked = items.map((item, index) => ({
      item: item,
      index: index,
      rank: Rank(item.querySelector("h1, h2")?.textContent ?? "", query),
    }));
    ranked.sort((a, b) => a.rank - b.rank || a.index - b.index);
    if (ranked.every((entry, i) => entry.item === items[i])) {
      return;
    }
    ranked.forEach((entry) => list.appendChild(entry.item));
  }

  function Init() {
    const input = document.querySelector("[data-md-component=search-query]");
    const result = document.querySelector("[data-md-component=search-result]");
    if (!input || !result || result.dataset.tuned) {
      return;
    }
    result.dataset.tuned = "1";
    let busy = false;
    const observer = new MutationObserver(() => {
      if (busy) {
        return;
      }
      const list = result.querySelector(".md-search-result__list");
      if (!list) {
        return;
      }
      busy = true;
      Sort(list, input);
      busy = false;
    });
    observer.observe(result, { childList: true, subtree: true });
  }

  if (typeof document$ !== "undefined") {
    document$.subscribe(Init);
  } else {
    document.addEventListener("DOMContentLoaded", Init);
  }
})();
