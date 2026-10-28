// サイト内検索。hooks/searchindex.py が作る search/meta.json と search/body.*.json を読み、
// 索引は作らずに部分一致で走査する。見出し（meta.json）は小さいので先に読み、本文は読み終わった時点で検索結果に足す。
(() => {
  const MaxTerms = 8;
  const MaxPages = 40;
  const MaxSubs = 3;
  const SnippetBefore = 28;
  const SnippetAfter = 72;
  const HighlightParam = "h";

  const state = {
    meta: null,
    titles: [],
    names: [],
    pageTitles: [],
    bodies: null,
    lower: null,
    loading: null,
    failed: false,
    open: false,
    active: -1,
    frame: 0,
    opener: null,
  };

  let root = null;
  let input = null;
  let list = null;
  let status = null;

  function Base() {
    return typeof __md_scope !== "undefined" ? __md_scope : new URL(".", location.href);
  }

  function Normalize(text) {
    return text.normalize("NFKC").toLowerCase();
  }

  // 名前の比較用。std:: と括弧、山かっこを落とす
  function NameOf(text) {
    return Normalize(text)
      .replace(/[（(].*?[）)]/g, "")
      .replace(/std::/g, "")
      .replace(/[<>]/g, "")
      .trim();
  }

  function Escape(text) {
    return text.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
  }

  async function Load() {
    if (state.loading) {
      return state.loading;
    }
    state.loading = (async () => {
      try {
        const base = Base();
        const metaResponse = await fetch(new URL("search/meta.json", base));
        if (!metaResponse.ok) {
          throw new Error(String(metaResponse.status));
        }
        const meta = await metaResponse.json();
        state.meta = meta;
        state.pageTitles = meta.pages.map((page) => NameOf(page[1]));
        state.titles = meta.secs.map((sec) => Normalize(sec[2]));
        state.names = meta.secs.map((sec) => NameOf(sec[2]));
        Refresh();
        const bodyResponse = await fetch(new URL("search/" + meta.body, base), { cache: "force-cache" });
        if (!bodyResponse.ok) {
          throw new Error(String(bodyResponse.status));
        }
        state.bodies = await bodyResponse.json();
        state.lower = state.bodies.map((text) => text.toLowerCase());
        Refresh();
      } catch (e) {
        state.failed = true;
        state.loading = null;
        Refresh();
      }
    })();
    return state.loading;
  }

  // ---- 検索 ----

  function Terms(query) {
    return Normalize(query)
      .split(/\s+/)
      .filter((term) => term !== "")
      .slice(0, MaxTerms);
  }

  function Count(text, term, limit) {
    let count = 0;
    let at = text.indexOf(term);
    while (at >= 0 && count < limit) {
      count++;
      at = text.indexOf(term, at + term.length);
    }
    return count;
  }

  // 名前が合っているほど高い点にする
  function NameScore(name, term, exact, prefix, part) {
    if (name === term) {
      return exact;
    }
    if (name.startsWith(term)) {
      return prefix;
    }
    if (name.includes(term)) {
      return part;
    }
    return 0;
  }

  function Run(query) {
    const terms = Terms(query);
    if (terms.length === 0 || !state.meta) {
      return null;
    }
    const names = terms.map((term) => (term.startsWith("std::") ? term.slice(5) : term));
    const secs = state.meta.secs;
    const hits = [];
    for (let i = 0; i < secs.length; i++) {
      const page = secs[i][0];
      const pageTitle = state.pageTitles[page];
      const title = state.titles[i];
      const body = state.lower ? state.lower[i] : "";
      let score = 0;
      let ok = true;
      for (let t = 0; t < terms.length; t++) {
        const term = terms[t];
        const name = names[t];
        const pageScore = NameScore(pageTitle, name, 1000, 600, 300);
        const titleScore = secs[i][1] === "" ? 0 : NameScore(state.names[i], name, 500, 300, 150);
        const inTitle = title.includes(term);
        const count = body === "" ? 0 : Count(body, term, 5);
        if (pageScore === 0 && titleScore === 0 && !inTitle && count === 0) {
          ok = false;
          break;
        }
        score += pageScore + titleScore + (inTitle ? 40 : 0) + (count > 0 ? 10 + count : 0);
      }
      if (!ok) {
        continue;
      }
      if (secs[i][1] === "") {
        score += 1;
      }
      hits.push({ index: i, page: page, score: score });
    }
    hits.sort((a, b) => b.score - a.score || a.index - b.index);
    const pages = new Map();
    for (const hit of hits) {
      let group = pages.get(hit.page);
      if (!group) {
        if (pages.size >= MaxPages) {
          continue;
        }
        group = { page: hit.page, score: hit.score, subs: [] };
        pages.set(hit.page, group);
      }
      group.subs.push(hit);
    }
    return { terms: terms, groups: [...pages.values()], total: hits.length };
  }

  // ---- 表示 ----

  function Snippet(index, terms) {
    if (!state.bodies) {
      return "";
    }
    const text = state.bodies[index];
    const lower = state.lower[index];
    let best = -1;
    for (const term of terms) {
      const at = lower.indexOf(term);
      if (at >= 0 && (best < 0 || at < best)) {
        best = at;
      }
    }
    if (best < 0) {
      return Escape(text.slice(0, SnippetBefore + SnippetAfter));
    }
    const start = Math.max(0, best - SnippetBefore);
    const piece = text.slice(start, best + SnippetAfter);
    const pieceLower = lower.slice(start, best + SnippetAfter);
    const marks = [];
    for (const term of terms) {
      let at = pieceLower.indexOf(term);
      while (at >= 0) {
        marks.push([at, at + term.length]);
        at = pieceLower.indexOf(term, at + term.length);
      }
    }
    marks.sort((a, b) => a[0] - b[0]);
    let html = "";
    let cursor = 0;
    for (const [from, to] of marks) {
      if (from < cursor) {
        continue;
      }
      html += Escape(piece.slice(cursor, from)) + "<mark>" + Escape(piece.slice(from, to)) + "</mark>";
      cursor = to;
    }
    html += Escape(piece.slice(cursor));
    return (start > 0 ? "…" : "") + html + "…";
  }

  function Href(page, anchor, query) {
    const url = new URL(state.meta.pages[page][0], Base());
    url.searchParams.set(HighlightParam, query);
    url.hash = anchor;
    return url.href;
  }

  function Where(url) {
    const parts = url.split("/").filter((part) => part !== "");
    return parts.slice(0, -1).join(" / ");
  }

  function Render(result, query) {
    state.active = -1;
    if (!result) {
      list.innerHTML = "";
      return;
    }
    const secs = state.meta.secs;
    const pages = state.meta.pages;
    let html = "";
    for (const group of result.groups) {
      const subs = group.subs.slice(0, MaxSubs);
      const first = subs[0];
      const top = secs[first.index][1] === "" ? first : null;
      const rest = top ? subs.slice(1) : subs;
      const path = Where(pages[group.page][0]);
      html += '<li class="kd-search__group">';
      html += '<a class="kd-search__hit kd-search__page" href="' + Escape(Href(group.page, "", query)) + '">';
      html += '<span class="kd-search__title">' + Escape(pages[group.page][1]) + "</span>";
      if (path !== "") {
        html += '<span class="kd-search__path">' + Escape(path) + "</span>";
      }
      const lead = top ? Snippet(top.index, result.terms) : "";
      if (lead !== "") {
        html += '<span class="kd-search__snippet">' + lead + "</span>";
      }
      html += "</a>";
      for (const sub of rest) {
        const sec = secs[sub.index];
        if (sec[1] === "") {
          continue;
        }
        html += '<a class="kd-search__hit kd-search__sub" href="' + Escape(Href(group.page, sec[1], query)) + '">';
        html += '<span class="kd-search__heading">' + Escape(sec[2]) + "</span>";
        const text = Snippet(sub.index, result.terms);
        if (text !== "") {
          html += '<span class="kd-search__snippet">' + text + "</span>";
        }
        html += "</a>";
      }
      html += "</li>";
    }
    list.innerHTML = html;
  }

  function Refresh() {
    if (!root) {
      return;
    }
    const query = input.value.trim();
    if (state.failed) {
      status.textContent = "検索データを読み込めませんでした。サイトをビルドし直してから開いてください。";
      list.innerHTML = "";
      return;
    }
    if (!state.meta) {
      status.textContent = "検索データを読み込んでいます…";
      return;
    }
    if (query === "") {
      status.textContent = state.bodies ? "キーワードを入力してください。空白で区切ると、すべてを含むページを探します。" : "見出しは検索できます。本文を読み込んでいます…";
      list.innerHTML = "";
      return;
    }
    const result = Run(query);
    if (!result || result.groups.length === 0) {
      status.textContent = state.bodies ? "見つかりませんでした。" : "見出しに見つかりませんでした。本文を読み込んでいます…";
      list.innerHTML = "";
      return;
    }
    const loading = state.bodies ? "" : "（本文を読み込み中）";
    status.textContent = result.groups.length + " ページ、" + result.total + " 件" + loading;
    Render(result, query);
  }

  function Schedule() {
    if (state.frame) {
      return;
    }
    state.frame = setTimeout(() => {
      state.frame = 0;
      Refresh();
    }, 0);
  }

  function Hits() {
    return [...list.querySelectorAll(".kd-search__hit")];
  }

  function Move(step) {
    const hits = Hits();
    if (hits.length === 0) {
      return;
    }
    state.active = (state.active + step + hits.length) % hits.length;
    hits.forEach((hit, i) => hit.classList.toggle("is-active", i === state.active));
    hits[state.active].scrollIntoView({ block: "nearest" });
  }

  // ---- 開閉 ----

  function Build() {
    root = document.createElement("div");
    root.className = "kd-search";
    root.hidden = true;
    root.innerHTML =
      '<div class="kd-search__scrim"></div>' +
      '<div class="kd-search__panel" role="dialog" aria-modal="true" aria-label="サイト内検索">' +
      '<div class="kd-search__bar">' +
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9.5 3A6.5 6.5 0 0 1 16 9.5c0 1.61-.59 3.09-1.56 4.23l.27.27h.79l5 5-1.5 1.5-5-5v-.79l-.27-.27A6.516 6.516 0 0 1 9.5 16 6.5 6.5 0 0 1 3 9.5 6.5 6.5 0 0 1 9.5 3m0 2C7 5 5 7 5 9.5S7 14 9.5 14 14 12 14 9.5 12 5 9.5 5"/></svg>' +
      '<input type="search" placeholder="検索（例: push_back、定数バッファ）" aria-label="検索" autocomplete="off" spellcheck="false" enterkeyhint="search">' +
      '<kbd>Esc</kbd>' +
      "</div>" +
      '<div class="kd-search__status" role="status" aria-live="polite"></div>' +
      '<ol class="kd-search__list"></ol>' +
      "</div>";
    document.body.appendChild(root);
    input = root.querySelector("input");
    list = root.querySelector(".kd-search__list");
    status = root.querySelector(".kd-search__status");
    root.querySelector(".kd-search__scrim").addEventListener("click", Close);
    input.addEventListener("input", Schedule);
    input.addEventListener("keydown", (event) => {
      if (event.isComposing) {
        return;
      }
      if (event.key === "ArrowDown") {
        event.preventDefault();
        Move(1);
      } else if (event.key === "ArrowUp") {
        event.preventDefault();
        Move(-1);
      } else if (event.key === "Enter") {
        const hits = Hits();
        const target = hits[state.active >= 0 ? state.active : 0];
        if (target) {
          event.preventDefault();
          location.href = target.href;
        }
      }
    });
    list.addEventListener("mousemove", (event) => {
      const hit = event.target.closest(".kd-search__hit");
      if (!hit) {
        return;
      }
      const hits = Hits();
      state.active = hits.indexOf(hit);
      hits.forEach((item, i) => item.classList.toggle("is-active", i === state.active));
    });
  }

  function Open() {
    if (!root) {
      Build();
    }
    if (state.open) {
      input.focus();
      return;
    }
    state.open = true;
    state.opener = document.activeElement;
    root.hidden = false;
    document.documentElement.classList.add("kd-search-open");
    input.focus();
    input.select();
    Load();
    Refresh();
  }

  function Close() {
    if (!state.open) {
      return;
    }
    state.open = false;
    root.hidden = true;
    document.documentElement.classList.remove("kd-search-open");
    if (state.opener && state.opener.focus) {
      state.opener.focus();
    }
  }

  function IsTyping(target) {
    return target instanceof HTMLElement && (target.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName));
  }

  function AddButton() {
    if (document.querySelector(".kd-search-button")) {
      return;
    }
    const inner = document.querySelector(".md-header__inner");
    if (!inner) {
      return;
    }
    const button = document.createElement("button");
    button.type = "button";
    button.className = "kd-search-button";
    button.setAttribute("aria-label", "検索");
    button.title = "検索（/ または Ctrl+K）";
    button.innerHTML =
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9.5 3A6.5 6.5 0 0 1 16 9.5c0 1.61-.59 3.09-1.56 4.23l.27.27h.79l5 5-1.5 1.5-5-5v-.79l-.27-.27A6.516 6.516 0 0 1 9.5 16 6.5 6.5 0 0 1 3 9.5 6.5 6.5 0 0 1 9.5 3m0 2C7 5 5 7 5 9.5S7 14 9.5 14 14 12 14 9.5 12 5 9.5 5"/></svg>' +
      '<span class="kd-search-button__label">検索</span><kbd>/</kbd>';
    button.addEventListener("click", Open);
    button.addEventListener("pointerenter", Load, { once: true });
    button.addEventListener("focus", Load, { once: true });
    const palette = inner.querySelector("[data-md-component=palette]");
    inner.insertBefore(button, palette ?? inner.querySelector(".md-header__source"));
  }

  // ---- 検索から来たページで、語を目立たせる ----

  function Highlight() {
    const params = new URLSearchParams(location.search);
    const query = params.get(HighlightParam);
    if (!query) {
      return;
    }
    params.delete(HighlightParam);
    const rest = params.toString();
    history.replaceState(history.state, "", location.pathname + (rest ? "?" + rest : "") + location.hash);
    const container = document.querySelector(".md-content__inner");
    const terms = Terms(query);
    if (!container || terms.length === 0) {
      return;
    }
    const walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT, {
      acceptNode: (node) => (node.parentElement && node.parentElement.closest("script, style, mark, .headerlink") ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT),
    });
    const nodes = [];
    while (walker.nextNode()) {
      nodes.push(walker.currentNode);
    }
    let made = 0;
    let firstMark = null;
    for (const node of nodes) {
      if (made >= 300) {
        break;
      }
      const text = node.data;
      const lower = text.toLowerCase();
      const spans = [];
      for (const term of terms) {
        let at = lower.indexOf(term);
        while (at >= 0) {
          spans.push([at, at + term.length]);
          at = lower.indexOf(term, at + term.length);
        }
      }
      if (spans.length === 0) {
        continue;
      }
      spans.sort((a, b) => a[0] - b[0]);
      const fragment = document.createDocumentFragment();
      let cursor = 0;
      for (const [from, to] of spans) {
        if (from < cursor) {
          continue;
        }
        fragment.append(text.slice(cursor, from));
        const mark = document.createElement("mark");
        mark.className = "kd-mark";
        mark.textContent = text.slice(from, to);
        fragment.append(mark);
        firstMark = firstMark ?? mark;
        cursor = to;
        made++;
      }
      fragment.append(text.slice(cursor));
      node.replaceWith(fragment);
    }
    if (firstMark && !location.hash) {
      firstMark.scrollIntoView({ block: "center" });
    }
  }

  function Init() {
    AddButton();
    Highlight();
    if (typeof requestIdleCallback === "function") {
      requestIdleCallback(() => Load(), { timeout: 4000 });
    } else {
      setTimeout(Load, 2000);
    }
  }

  document.addEventListener("keydown", (event) => {
    const mod = event.ctrlKey || event.metaKey;
    if (mod && !event.altKey && event.key.toLowerCase() === "k") {
      event.preventDefault();
      Open();
    } else if (!mod && !event.altKey && event.key === "/" && !IsTyping(event.target)) {
      event.preventDefault();
      Open();
    } else if (event.key === "Escape" && state.open) {
      event.preventDefault();
      Close();
    }
  });

  if (typeof document$ !== "undefined") {
    document$.subscribe(Init);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", Init);
  } else {
    Init();
  }
})();
