P = "graphics/ao/"
MOVED = {
    P + "theory.md": P + "theory/index.md",
    P + "world-space.md": P + "world-space/index.md",
    P + "filtering.md": P + "filtering/index.md",
    P + "artifacts.md": P + "artifacts/index.md",
}
GLOSSARY = {
    P + "world-space.md": [("RTAO", P + "world-space/rtao.md"), ("DFAO", P + "world-space/dfao.md"), ("距離場", P + "world-space/dfao.md"), ("VXAO", P + "world-space/vxao.md"), ("ボクセル", P + "world-space/vxao.md")],
    P + "filtering.md": [("バイラテラル", P + "filtering/bilateral-blur.md"), ("アップサンプル", P + "filtering/upsample.md"), ("時間", P + "filtering/temporal.md")],
    P + "artifacts.md": [("ハロー", P + "artifacts/halo.md"), ("自己遮蔽", P + "artifacts/self-occlusion.md")],
    P + "theory.md": [("オブスキュランス", P + "theory/obscurance.md")],
}
