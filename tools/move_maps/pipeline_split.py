# graphics/pipeline/ を、Lighting・Draw Submission・Optimization の 3 つに分ける
P = "graphics/pipeline/"
L = "graphics/lighting/"
D = "graphics/draw-submission/"
O = "graphics/optimization/"

MOVES = {P + "index.md": O + "index.md"}                       # 手法の地図（コストの一覧）は、最適化のハブ
for name in ("forward-deferred", "light-culling", "visibility-buffer"):
    MOVES[P + name + ".md"] = L + name + ".md"
for name in ("overview", "draw-calls", "culling", "lod", "gpu-driven", "mesh-shaders", "2d"):
    MOVES[P + name + ".md"] = D + name + ".md"
for name in ("bottlenecks", "bandwidth", "overdraw", "low-res-effects", "hiz", "shader-cost", "texture-streaming",
             "async-compute", "tools", "cases"):
    MOVES[P + name + ".md"] = O + name + ".md"
for name in ("index", "bindless", "culling", "execute-indirect", "hiz-two-pass", "meshlets", "scene-data", "sync-debug"):
    MOVES[P + "gpu-driven-dx12/" + name + ".md"] = D + "gpu-driven-dx12/" + name + ".md"

TITLES = {
    O + "index.md": "Optimization",
    D + "overview.md": "Rendering Pipeline Overview",
}
