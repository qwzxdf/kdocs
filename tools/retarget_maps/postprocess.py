P = "graphics/postprocess/"
MOVED = {
    P + "tonemapping.md": P + "tonemapping/index.md",
    P + "bloom.md": P + "bloom/index.md",
    P + "dof.md": P + "dof/index.md",
    P + "motion-blur.md": P + "motion-blur/index.md",
    P + "antialiasing.md": P + "antialiasing/index.md",
    P + "color-grading.md": P + "color-grading/index.md",
    P + "lens-effects.md": P + "lens-effects/index.md",
    P + "stylized.md": P + "stylized/index.md",
}
GLOSSARY = {
    P + "tonemapping.md": [
        ("Reinhard", P + "tonemapping/reinhard.md"), ("ACES", P + "tonemapping/aces.md"), ("AgX", P + "tonemapping/agx.md"),
        ("Tony", P + "tonemapping/agx.md"), ("フィルミック", P + "tonemapping/filmic-hable.md"), ("Hable", P + "tonemapping/filmic-hable.md"),
        ("自動露出", P + "tonemapping/auto-exposure.md"), ("Eye Adaptation", P + "tonemapping/auto-exposure.md"), ("露出", P + "tonemapping/exposure.md"),
        ("EV", P + "tonemapping/exposure.md"), ("ガンマ", P + "tonemapping/gamma-srgb.md"), ("sRGB", P + "tonemapping/gamma-srgb.md"),
        ("HDR10", P + "tonemapping/gamma-srgb.md"), ("PQ", P + "tonemapping/gamma-srgb.md"), ("ペーパー", P + "tonemapping/gamma-srgb.md"),
    ],
    P + "bloom.md": [
        ("しきい値", P + "bloom/threshold.md"), ("ダウンサンプル", P + "bloom/downsample.md"), ("ミップ", P + "bloom/downsample.md"),
        ("ガウス", P + "bloom/gaussian.md"), ("Dual", P + "bloom/dual-filter.md"), ("Kawase", P + "bloom/dual-filter.md"),
        ("Karis", P + "bloom/karis-average.md"), ("ファイアフライ", P + "bloom/karis-average.md"), ("ダート", P + "bloom/composite.md"),
    ],
    P + "dof.md": [
        ("錯乱円", P + "dof/coc.md"), ("CoC", P + "dof/coc.md"), ("ギャザー", P + "dof/gather.md"), ("スキャッター", P + "dof/scatter.md"),
        ("ボケ", P + "dof/bokeh-shape.md"), ("前景", P + "dof/near-far.md"),
    ],
    P + "motion-blur.md": [
        ("速度バッファ", P + "motion-blur/velocity-buffer.md"), ("タイル", P + "motion-blur/tile-max.md"),
        ("カメラ モーション", P + "motion-blur/camera-blur.md"), ("オブジェクト モーション", P + "motion-blur/object-blur.md"),
        ("シャッター", P + "motion-blur/strength-taa.md"),
    ],
    P + "antialiasing.md": [
        ("MSAA", P + "antialiasing/msaa.md"), ("FXAA", P + "antialiasing/fxaa.md"), ("SMAA", P + "antialiasing/smaa.md"),
        ("TAA", P + "antialiasing/taa.md"), ("ジッター", P + "antialiasing/taa.md"), ("ゴースト", P + "antialiasing/taa-challenges.md"),
    ],
    P + "color-grading.md": [
        ("LUT", P + "color-grading/lut-3d.md"), ("ホワイト", P + "color-grading/white-balance.md"),
        ("リフト", P + "color-grading/lift-gamma-gain.md"), ("CDL", P + "color-grading/lift-gamma-gain.md"),
    ],
    P + "lens-effects.md": [
        ("色収差", P + "lens-effects/chromatic-aberration.md"), ("ビネット", P + "lens-effects/vignette.md"),
        ("グレイン", P + "lens-effects/film-grain.md"), ("フレア", P + "lens-effects/lens-flare.md"),
    ],
    P + "stylized.md": [
        ("アウトライン", P + "stylized/outline-hull.md"), ("輪郭", P + "stylized/outline-hull.md"), ("Sobel", P + "stylized/outline-edge.md"),
        ("セル", P + "stylized/cel-shading.md"), ("トゥーン", P + "stylized/cel-shading.md"),
        ("ポスタライズ", P + "stylized/posterize-halftone.md"), ("ハーフトーン", P + "stylized/posterize-halftone.md"),
    ],
}
