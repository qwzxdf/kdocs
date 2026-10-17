P = "graphics/reflections/"
MOVED = {
    P + "ssr-basics.md": P + "ssr-basics/index.md",
    P + "probes.md": P + "probes/index.md",
    P + "rt-reflections.md": P + "rt-reflections/index.md",
}
GLOSSARY = {
    P + "ssr-basics.md": [("厚み", P + "ssr-basics/thickness.md"), ("線形", P + "ssr-basics/linear-march.md")],
    P + "probes.md": [("Split-Sum", P + "probes/prefilter.md"), ("事前フィルタ", P + "probes/prefilter.md"), ("視差", P + "probes/parallax.md"), ("ボックス投影", P + "probes/parallax.md")],
    P + "rt-reflections.md": [("BVH", P + "rt-reflections/hit-shading.md"), ("デノイ", P + "rt-reflections/denoise.md")],
}
