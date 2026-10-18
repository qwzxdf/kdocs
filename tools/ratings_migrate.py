"""ratings.yml を 5 段階(重さ・品質・難易度)へ移す。

  perf    : 1 = とても軽い … 5 = とても重い(負荷の大きさ)
  quality : 1 = かんたんな近似 … 5 = 基準になる正確さ(書かない = 好みの問題)
  diff    : 1 = 入門 … 5 = 上級(理解・実装の難しさ)

古い値(perf 1〜3、quality 1〜3)を 5 段階に割り当て直し、
両端(1 と 5)は、ページ名で決めた例外の一覧で、振り分ける。
"""
import io
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
SRC = "ratings.yml"

# ---- 重さ: 古い perf 1 のうち、ほぼ無料のもの → 1
PERF1 = ["tonemapping/", "color-grading/", "lens-effects/vignette", "lens-effects/film-grain", "lens-effects/chromatic",
         "shadows/bias/constant-bias", "shadows/bias/slope", "shadows/bias/front-face", "shadows/bias/normal-offset",
         "shadow-map-basics/comparison-sampler", "shadow-map-basics/light-matrix", "gi/lightmaps/", "reflections/probes/",
         "heightmap-mesh/", "terrain/texturing/weights", "terrain/texturing/tiling", "atmosphere/sky-models/", "atmosphere/aerial-fog/",
         "god-rays/tuning", "bloom/threshold", "bloom/composite", "stylized/cel-shading", "stylized/posterize", "water/waves/sine",
         "water/waves/gerstner", "translucency/blending-sorting/", "gi/probes/"]
# ---- 重さ: 古い perf 3 のうち、特に重いもの → 5
PERF5 = ["shadows/ray-traced", "world-space/rtao", "rt-reflections/index", "rt-reflections/ray-generation", "rt-reflections/hit-shading",
         "rt-gi/index", "rt-gi/restir", "rt-gi/lumen", "rt-gi/noise", "depth-peeling", "gi/voxel-gi", "world-space/vxao", "virtual-shadow",
         "dof/scatter", "fft-ocean", "volumetric-fog/index", "clouds/index", "clouds/raymarch", "shadowmap-march"]
# ---- 品質: 古い quality 1 のうち、特に粗いもの → 1
QUAL1 = ["constant-bias", "blob-planar", "water/waves/sine", "sky-models/gradient", "clouds/cheap", "ssao-crytek", "camera-blur"]
# ---- 品質: 古い quality 3 のうち、基準になるもの → 5
QUAL5 = ["shadows/ray-traced", "world-space/rtao", "rt-reflections/", "gi/lightmaps/", "depth-peeling", "oit/ppll", "fft-ocean",
         "diffusion-profile", "shadow-volumes", "rt-gi/restir", "rt-gi/index", "rt-gi/lumen", "rt-gi/choosing", "rt-gi/noise"]

# ---- 難易度: 最初に一致したものを使う(上から、細かい順)
DIFF = [
    (1, ["exposure", "gamma-srgb", "vignette", "film-grain", "constant-bias", "blob-planar", "sine-waves", "fxaa", "basic-adjustments",
         "white-balance", "comparison-sampler", "light-matrix", "cel-shading", "posterize", "blend-state", "sky-models/gradient", "outline-hull"]),
    (5, ["restir", "lumen-style", "radiance-cascades", "hillaire", "bruneton", "multiple-scattering", "fft-ocean", "marschner",
         "diffusion-profile", "vsm/evsm", "vsm/msm", "virtual-shadow", "gi/ddgi", "gi/voxel-gi", "vxao", "pcss"]),
    (4, ["gtao", "dfao", "rtao", "ssr-hiz", "ssr-stochastic", "rt-reflections/", "rt-gi/", "volumetric-fog/injection",
         "volumetric-fog/integration", "volumetric-fog/froxel", "clouds/raymarch", "clouds/lighting", "sdf-shadows", "shadow-volumes",
         "vsm/index", "hair/shadows", "hair/transparency", "antialiasing/taa", "antialiasing/smaa", "dof/scatter", "tile-max",
         "oit/depth-peeling", "oit/ppll", "oit/stochastic", "gi/theory/", "ao/theory/from-rendering", "single-scattering",
         "ssgi", "dynamic-update", "sh-storage", "motion-blur/blur-pass", "water/shore-foam/crest-jacobian", "terrain/lod/cdlod",
         "terrain/lod/clipmap", "terrain/texturing/virtual-texture", "terrain/generation/erosion", "gi/probes/placement",
         "hbao-plus", "skin-hair/skin/subsurface-theory", "reflections/probes/parallax", "bloom/karis", "auto-exposure"]),
    (3, ["cascaded", "ao/hbao", "ao/sao", "ao/alchemy", "vsm/", "dof/gather", "dof/coc", "dof/near-far", "oit/wboit", "oit/index",
         "object-blur", "motion-blur/index", "taa-challenges", "transmittance", "phase-function", "atmosphere/scattering/",
         "tonemapping/agx", "hue-preservation", "clouds/", "volumetric-fog/", "god-rays/shadowmap", "god-rays/volume", "ssr-basics/",
         "reflections/rt-", "bias/receiver", "shadow-map-basics/aliasing", "terrain/generation/", "terrain/texturing/triplanar",
         "terrain/texturing/height-blend", "terrain/lod/", "water/waves/fft", "water/interaction/apply", "skin-hair/", "gi/probes/",
         "gi/lightmaps/baking", "gi/lightmaps/uv2", "alpha-to-coverage", "hashed-alpha", "refraction/", "ao/world-space/",
         "ao/filtering/", "ao/ssao-hemisphere", "dof/", "bloom/", "lut-3d", "lift-gamma-gain", "lens-flare"]),
    (2, ["index", "comparison", "choosing", "compare", "basic", "blend-state", "sorting", "soft-particles", "premultiplied",
         "alpha-test/", "dither", "exposure", "gamma", "reinhard", "filmic", "aces", "vignette", "film-grain", "chromatic",
         "white-balance", "lut-authoring", "constant-bias", "slope", "normal-offset", "front-face", "comparison-sampler",
         "light-matrix", "minimal-code", "render-depth", "blob", "fxaa", "msaa", "sine", "gerstner", "sky-models/", "aerial-fog/",
         "lightmaps/", "heightmap-mesh/", "ssr-fallback", "pre-integrated", "thin-translucency", "kajiya", "outline", "cel-",
         "posterize", "water/", "terrain/", "fresnel", "pcf", "contact-shadows", "special-cases/", "ssao-crytek", "reflections/",
         "motion-blur/", "lens-effects/", "color-grading/", "stylized/", "translucency/"]),
]

RE = re.compile(r"^(graphics/\S+\.md):\s*\{([^}]*)\}\s*$")


def Match(path, words):
    return any(w in path for w in words)


def Diff(path):
    if path.endswith("/index.md"):
        return 2 if not Match(path, ["rt-gi/", "volumetric-fog/", "clouds/", "world-space/", "theory/"]) else 3
    for level, words in DIFF:
        if Match(path, words):
            return level
    return 3


out = []
stats = {"perf": {}, "quality": {}, "diff": {}}
for line in open(SRC, encoding="utf-8").read().split("\n"):
    m = RE.match(line)
    if not m:
        out.append(line)
        continue
    path, body = m.group(1), m.group(2)
    d = {}
    for kv in body.split(","):
        if ":" in kv:
            k, v = kv.split(":")
            d[k.strip()] = int(v)
    new = {}
    if "perf" in d:
        o = d["perf"]
        if o == 1:
            p = 1 if Match(path, PERF1) else 2
        elif o == 2:
            p = 3
        else:
            p = 5 if Match(path, PERF5) else 4
        new["perf"] = p
    if "quality" in d:
        o = d["quality"]
        if o == 1:
            q = 1 if Match(path, QUAL1) else 2
        elif o == 2:
            q = 3
        else:
            q = 5 if Match(path, QUAL5) else 4
        new["quality"] = q
    new["diff"] = Diff(path)
    for k, v in new.items():
        stats[k][v] = stats[k].get(v, 0) + 1
    out.append("%s: {%s}" % (path, ", ".join("%s: %d" % (k, v) for k, v in new.items())))

text = "\n".join(out)
head = """# 描画の項目の評価。docs からの相対パス: {perf, quality, diff}
# 3 つとも 5 段階。
#
# perf（重さ。数が大きいほど重い）
#   1 = とても軽い（ほぼ無料。フレームの 0.1 ms 未満）
#   2 = 軽い（0.1〜0.3 ms）
#   3 = 普通（0.3〜1 ms）
#   4 = 重い（1〜3 ms。使いどころを選ぶ）
#   5 = とても重い（3 ms 超。品質設定で切る・専用の工夫が要る）
# quality（見た目の正確さ・きれいさ。数が大きいほど良い）
#   1 = かんたんな近似 / 2 = 簡易 / 3 = 標準 / 4 = 高い / 5 = 基準になる正確さ
# diff（理解・実装の難しさ。数が大きいほど難しい）
#   1 = 入門（式も要らない）
#   2 = やさしい（基本の数学・1 回の描画で書ける）
#   3 = ふつう（複数パス・行列・サンプリングの理解）
#   4 = 難しい（確率・積分・時間方向・複数の技術の組み合わせ）
#   5 = 上級（論文レベル・最新手法・自前の実装が大変）
# quality を書かない = 好みや表現の問題で、「高いほど良い」とは言えない項目
# perf を書かない = 手法の比較・理論など、負荷を一つに決められないページ
"""
text = re.sub(r"\A(#[^\n]*\n)+", head, text)
open(SRC, "w", encoding="utf-8").write(text)
for k, v in stats.items():
    print(k, sorted(v.items()))
