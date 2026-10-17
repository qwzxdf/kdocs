P = "graphics/water/"
MOVED = {
    P + "waves.md": P + "waves/index.md",
    P + "shading.md": P + "shading/index.md",
    P + "shore-foam.md": P + "shore-foam/index.md",
    P + "interaction.md": P + "interaction/index.md",
    P + "underwater.md": P + "underwater/index.md",
}
GLOSSARY = {
    P + "waves.md": [("Gerstner", P + "waves/gerstner.md"), ("FFT", P + "waves/fft-ocean.md")],
    P + "shading.md": [("Beer", P + "shading/depth-color.md"), ("フレネル", P + "shading/fresnel.md")],
    P + "shore-foam.md": [("ヤコビアン", P + "shore-foam/crest-jacobian.md")],
    P + "interaction.md": [("フローマップ", P + "interaction/flow-map.md")],
    P + "underwater.md": [("コースティクス", P + "underwater/caustics.md")],
}
