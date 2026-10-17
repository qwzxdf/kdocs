P = "graphics/translucency/"
MOVED = {
    P + "blending-sorting.md": P + "blending-sorting/index.md",
    P + "alpha-test.md": P + "alpha-test/index.md",
    P + "oit.md": P + "oit/index.md",
    P + "refraction.md": P + "refraction/index.md",
}
GLOSSARY = {
    P + "blending-sorting.md": [("乗算済み", P + "blending-sorting/premultiplied.md"), ("ソフト", P + "blending-sorting/soft-particles.md"), ("ソート", P + "blending-sorting/sorting.md")],
    P + "alpha-test.md": [("Alpha to Coverage", P + "alpha-test/alpha-to-coverage.md"), ("A2C", P + "alpha-test/alpha-to-coverage.md"), ("ハッシュド", P + "alpha-test/hashed-alpha.md"), ("ディザ", P + "alpha-test/dither.md")],
    P + "oit.md": [("WBOIT", P + "oit/wboit.md"), ("Weighted", P + "oit/wboit.md"), ("PPLL", P + "oit/ppll.md"), ("Linked", P + "oit/ppll.md"), ("Peeling", P + "oit/depth-peeling.md")],
    P + "refraction.md": [("フレネル", P + "refraction/fresnel.md"), ("ビア", P + "refraction/thickness-color.md"), ("分散", P + "refraction/dispersion.md")],
}
