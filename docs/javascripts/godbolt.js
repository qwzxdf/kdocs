(() => {
  const kCompilerId = "g161";
  const kOptions = "-std=c++23 -O2 -Wall";
  const kLibraries = [
    { prefix: "nlohmann/", lib: { name: "nlohmann_json", ver: "trunk" } },
    { prefix: "simdjson.h", lib: { name: "simdjson", ver: "502" } },
    { prefix: "cereal/", lib: { name: "cereal", ver: "132" } },
  ];

  function FindLibraries(source) {
    const libs = [];
    const pattern = /^\s*#\s*include\s*[<"]([^>"]+)[>"]/gm;
    let match;
    while ((match = pattern.exec(source)) !== null) {
      const header = match[1];
      if (!header.includes("/") && !header.includes(".")) {
        continue;
      }
      const known = kLibraries.find((entry) => header.startsWith(entry.prefix));
      if (!known) {
        return null;
      }
      if (!libs.some((lib) => lib.name === known.lib.name)) {
        libs.push(known.lib);
      }
    }
    return libs;
  }

  function ToBase64(text) {
    const bytes = new TextEncoder().encode(text);
    let binary = "";
    bytes.forEach((b) => {
      binary += String.fromCharCode(b);
    });
    return btoa(binary);
  }

  function BuildUrl(source, libs) {
    const state = {
      sessions: [
        {
          id: 1,
          language: "c++",
          source: source,
          compilers: [],
          executors: [
            {
              arguments: "",
              compiler: { id: kCompilerId, libs: libs, options: kOptions },
              stdin: "",
            },
          ],
        },
      ],
    };
    return "https://godbolt.org/clientstate/" + encodeURIComponent(ToBase64(JSON.stringify(state)));
  }

  function AddButtons() {
    document.querySelectorAll(".language-cpp.highlight").forEach((block) => {
      if (block.dataset.godbolt) {
        return;
      }
      const code = block.querySelector("code");
      if (!code || !/\bint main\s*\(/.test(code.textContent)) {
        return;
      }
      const libs = FindLibraries(code.textContent);
      if (libs === null) {
        return;
      }
      block.dataset.godbolt = "1";
      const link = document.createElement("a");
      link.className = "godbolt-link";
      link.href = BuildUrl(code.textContent, libs);
      link.target = "_blank";
      link.rel = "noopener";
      link.textContent = "▶ Compiler Explorer で実行";
      block.insertAdjacentElement("afterend", link);
    });
  }

  if (typeof document$ !== "undefined") {
    document$.subscribe(AddButtons);
  } else {
    document.addEventListener("DOMContentLoaded", AddButtons);
  }
})();
