(() => {
  const kSvgNs = "http://www.w3.org/2000/svg";
  const kGridX = 150;
  const kGridY = 64;
  const kPad = 14;
  const kNodeHeight = 34;
  const kIntervalMs = 1700;
  const kLastHoldMs = 2400;

  function ParseGraph(source) {
    return source
      .split(/^---\s*$/m)
      .map((block) => {
        const nodes = [];
        const links = [];
        block.split("\n").forEach((raw) => {
          const line = raw.trim();
          if (line === "" || line.startsWith("#")) {
            return;
          }
          const t = line.split(/\s+/);
          if (t[0] === "n" && t.length >= 5) {
            nodes.push({
              id: t[1],
              label: t[2].replace(/_/g, " "),
              col: Number(t[3]),
              row: Number(t[4]),
              cls: t[5] || "",
            });
          } else if (t[0] === "l" && t.length >= 3) {
            links.push({
              from: t[1],
              to: t[2],
              cls: t[3] || "",
              label: (t[4] || "").replace(/_/g, " "),
            });
          }
        });
        return { nodes: nodes, links: links };
      })
      .filter((frame) => frame.nodes.length > 0);
  }

  function NodeWidth(label) {
    let units = 0;
    for (const ch of label) {
      units += ch.charCodeAt(0) > 255 ? 1 : 0.55;
    }
    return Math.max(64, Math.round(units * 13 + 22));
  }

  function Svg(tag, attrs) {
    const el = document.createElementNS(kSvgNs, tag);
    Object.entries(attrs || {}).forEach(([k, v]) => el.setAttribute(k, v));
    return el;
  }

  function EdgePoint(a, b) {
    const dx = b.x - a.x;
    const dy = b.y - a.y;
    if (Math.abs(dx) * 0.5 >= Math.abs(dy)) {
      const sign = dx >= 0 ? 1 : -1;
      return { x: a.x + (sign * a.w) / 2, y: a.y, dir: "h" };
    }
    const sign = dy >= 0 ? 1 : -1;
    return { x: a.x, y: a.y + (sign * kNodeHeight) / 2, dir: "v" };
  }

  function LinkPath(a, b) {
    const p = EdgePoint(a, b);
    const q = EdgePoint(b, a);
    if (p.dir === "h") {
      const mid = (p.x + q.x) / 2;
      return `M${p.x},${p.y} C${mid},${p.y} ${mid},${q.y} ${q.x},${q.y}`;
    }
    const mid = (p.y + q.y) / 2;
    return `M${p.x},${p.y} C${p.x},${mid} ${q.x},${mid} ${q.x},${q.y}`;
  }

  function Flash(el, cls, previous) {
    if (previous !== cls && cls !== "") {
      el.classList.remove("pop");
      void el.getBoundingClientRect();
      el.classList.add("pop");
    }
  }

  function Build(root, serial) {
    const source = root.textContent;
    const frames = ParseGraph(source);
    if (frames.length === 0) {
      return;
    }
    const label = root.dataset.label || "";
    const notes = [...source.matchAll(/^#\s*(.+)$/gm)].map((m) => m[1]);
    root.textContent = "";
    root.dataset.ready = "1";
    root.setAttribute("role", "img");
    root.setAttribute("aria-label", label + (notes.length ? "：" + notes.join(" → ") : ""));

    const widths = {};
    let maxCol = 0;
    let maxRow = 0;
    let lastWidth = 0;
    frames.forEach((frame) => {
      frame.nodes.forEach((node) => {
        widths[node.id] = Math.max(widths[node.id] || 0, NodeWidth(node.label));
        maxCol = Math.max(maxCol, node.col);
        maxRow = Math.max(maxRow, node.row);
      });
    });
    frames.forEach((frame) => {
      frame.nodes.forEach((node) => {
        if (node.col === maxCol) {
          lastWidth = Math.max(lastWidth, widths[node.id]);
        }
      });
    });
    const width = kPad * 2 + maxCol * kGridX + lastWidth;
    const height = kPad * 2 + maxRow * kGridY + kNodeHeight;

    const title = document.createElement("div");
    title.className = "anim-title";
    title.textContent = label;

    const svg = Svg("svg", { viewBox: `0 0 ${width} ${height}`, class: "anim-graph" });
    svg.style.maxWidth = width + "px";
    const markerId = "kd-arrow-" + serial;
    const defs = Svg("defs");
    const marker = Svg("marker", {
      id: markerId,
      viewBox: "0 0 10 10",
      refX: "9",
      refY: "5",
      markerWidth: "7",
      markerHeight: "7",
      orient: "auto-start-reverse",
    });
    marker.appendChild(Svg("path", { d: "M0,0 L10,5 L0,10 z", class: "anim-arrow" }));
    defs.appendChild(marker);
    svg.appendChild(defs);
    const linkLayer = Svg("g");
    const nodeLayer = Svg("g");
    svg.append(linkLayer, nodeLayer);
    root.append(title, svg);

    const nodeEls = {};
    const linkEls = {};

    function Pos(node) {
      return {
        x: kPad + node.col * kGridX + widths[node.id] / 2,
        y: kPad + node.row * kGridY + kNodeHeight / 2,
        w: widths[node.id],
      };
    }

    let index = 0;

    function Render() {
      const frame = frames[index];
      const present = new Set();
      const positions = {};
      frame.nodes.forEach((node) => {
        present.add(node.id);
        const pos = Pos(node);
        positions[node.id] = pos;
        let el = nodeEls[node.id];
        if (!el) {
          el = Svg("g", { class: "anim-node" });
          el.appendChild(Svg("rect", { height: kNodeHeight, rx: 6, y: -kNodeHeight / 2 }));
          el.appendChild(Svg("text", { "text-anchor": "middle", "dominant-baseline": "central" }));
          nodeLayer.appendChild(el);
          nodeEls[node.id] = el;
        }
        const rect = el.firstChild;
        rect.setAttribute("width", pos.w);
        rect.setAttribute("x", -pos.w / 2);
        el.lastChild.textContent = node.label;
        el.style.transform = `translate(${pos.x}px, ${pos.y}px)`;
        const previous = el.dataset.cls;
        el.setAttribute("class", "anim-node " + node.cls);
        Flash(el, node.cls, previous);
        el.dataset.cls = node.cls;
      });
      Object.entries(nodeEls).forEach(([id, el]) => {
        if (!present.has(id)) {
          el.setAttribute("class", "anim-node off");
          el.dataset.cls = "off";
        }
      });

      const linkPresent = new Set();
      frame.links.forEach((link) => {
        const a = positions[link.from];
        const b = positions[link.to];
        if (!a || !b) {
          return;
        }
        const key = link.from + ">" + link.to;
        linkPresent.add(key);
        let el = linkEls[key];
        if (!el) {
          el = Svg("g", { class: "anim-link" });
          el.appendChild(Svg("path", { "marker-end": `url(#${markerId})` }));
          el.appendChild(Svg("text", { "text-anchor": "middle", class: "anim-link-label" }));
          linkLayer.appendChild(el);
          linkEls[key] = el;
        }
        el.firstChild.setAttribute("d", LinkPath(a, b));
        const text = el.lastChild;
        text.textContent = link.label;
        text.setAttribute("x", (a.x + b.x) / 2);
        text.setAttribute("y", (a.y + b.y) / 2 - 6);
        const previous = el.dataset.cls;
        el.setAttribute("class", "anim-link " + link.cls);
        Flash(el, link.cls, previous);
        el.dataset.cls = link.cls;
      });
      Object.entries(linkEls).forEach(([key, el]) => {
        if (!linkPresent.has(key)) {
          el.setAttribute("class", "anim-link off");
          el.dataset.cls = "off";
        }
      });
    }

    function Tick() {
      index = (index + 1) % frames.length;
      Render();
      setTimeout(Tick, index === frames.length - 1 ? kLastHoldMs : kIntervalMs);
    }

    Render();
    setTimeout(Tick, kIntervalMs);
  }

  let serial = 0;

  function Init() {
    document.querySelectorAll('.anim[data-type="graph"]').forEach((root) => {
      if (!root.dataset.ready) {
        serial += 1;
        Build(root, serial);
      }
    });
  }

  if (typeof document$ !== "undefined") {
    document$.subscribe(Init);
  } else {
    document.addEventListener("DOMContentLoaded", Init);
  }
})();
