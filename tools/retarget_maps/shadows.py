P = "graphics/shadows/"
MOVED = {
    P + "shadow-map-basics.md": P + "shadow-map-basics/index.md",
    P + "bias.md": P + "bias/index.md",
    P + "vsm.md": P + "vsm/index.md",
    P + "special-cases.md": P + "special-cases/index.md",
    P + "local-lights.md": P + "local-lights/index.md",
}
GLOSSARY = {
    P + "bias.md": [("スロープ", P + "bias/slope-scale-bias.md"), ("法線オフセット", P + "bias/normal-offset.md"), ("受け手", P + "bias/receiver-plane-bias.md"), ("ピーター", P + "bias/peter-panning.md"), ("アクネ", P + "bias/index.md")],
    P + "vsm.md": [("ESM", P + "vsm/esm.md"), ("EVSM", P + "vsm/evsm.md"), ("MSM", P + "vsm/msm.md"), ("光漏れ", P + "vsm/light-bleeding.md")],
    P + "local-lights.md": [("キューブ", P + "local-lights/point-cubemap.md"), ("パラボロイド", P + "local-lights/dual-paraboloid.md"), ("スポット", P + "local-lights/spot-light.md")],
}
