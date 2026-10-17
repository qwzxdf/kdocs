(() => {
  const kIntervalMs = 1200;
  const kLastHoldMs = 2200;

  function ParseFrames(source) {
    return source
      .split("\n")
      .map((line) => line.trim())
      .filter((line) => line.length > 0)
      .map((line) => {
        const [cellsText, note = ""] = line.split("#");
        const cells = cellsText
          .trim()
          .split(/\s+/)
          .map((token) => {
            if (token === "|") {
              return { cls: "gap", text: "" };
            }
            if (token === "_") {
              return { cls: "free", text: "　" };
            }
            if (token.startsWith("+")) {
              return { cls: "new", text: token.slice(1) };
            }
            if (token.startsWith(">")) {
              return { cls: "move", text: token.slice(1) };
            }
            if (token.startsWith("x")) {
              return { cls: "gone", text: token.slice(1) };
            }
            if (token.startsWith("*")) {
              return { cls: "hit", text: token.slice(1) };
            }
            return { cls: "", text: token };
          });
        return { cells: cells, note: note.trim() };
      });
  }

  function Build(root) {
    const frames = ParseFrames(root.textContent);
    if (frames.length === 0) {
      return;
    }
    const label = root.dataset.label || "";
    root.textContent = "";
    root.dataset.ready = "1";
    root.setAttribute("role", "img");
    root.setAttribute(
      "aria-label",
      label + "：" + frames.map((frame) => frame.note).filter(Boolean).join(" → "));

    const title = document.createElement("div");
    title.className = "anim-title";
    title.textContent = label;

    const stage = document.createElement("div");
    stage.className = "mem-cells anim-stage";
    root.append(title, stage);

    let index = 0;
    let timer = null;
    const cellElements = [];

    function Render() {
      const frame = frames[index];
      while (cellElements.length < frame.cells.length) {
        const element = document.createElement("span");
        stage.appendChild(element);
        cellElements.push(element);
      }
      while (cellElements.length > frame.cells.length) {
        cellElements.pop().remove();
      }
      frame.cells.forEach((cell, i) => {
        const element = cellElements[i];
        const changed = element.textContent !== cell.text || element.dataset.cls !== cell.cls;
        element.textContent = cell.text;
        element.dataset.cls = cell.cls;
        element.className = cell.cls;
        if (changed && cell.cls !== "") {
          element.classList.remove("pop");
          void element.offsetWidth;
          element.classList.add("pop");
        }
      });
    }

    function Tick() {
      index = (index + 1) % frames.length;
      Render();
      const last = index === frames.length - 1;
      timer = setTimeout(Tick, last ? kLastHoldMs : kIntervalMs);
    }

    function Start() {
      if (timer === null) {
        timer = setTimeout(Tick, kIntervalMs);
      }
    }

    Render();
    Start();
  }

  function Init() {
    document.querySelectorAll(".anim").forEach((root) => {
      if (!root.dataset.ready) {
        Build(root);
      }
    });
  }

  if (typeof document$ !== "undefined") {
    document$.subscribe(Init);
  } else {
    document.addEventListener("DOMContentLoaded", Init);
  }
})();
