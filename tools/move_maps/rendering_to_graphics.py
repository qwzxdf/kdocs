# 描画最適化（rendering/）を、グラフィックス（graphics/）に統合する
R = "rendering/"
P = "graphics/pipeline/"

MOVES = {
    R + "index.md": P + "index.md",
    R + "pipeline.md": P + "overview.md",
}
for name in ("bottlenecks", "bandwidth", "forward-deferred", "light-culling", "draw-calls", "culling", "gpu-driven",
             "mesh-shaders", "visibility-buffer", "overdraw", "low-res-effects", "hiz", "shader-cost", "lod",
             "texture-streaming", "async-compute", "2d", "tools", "cases"):
    MOVES[R + name + ".md"] = P + name + ".md"
for name in ("index", "bindless", "culling", "execute-indirect", "hiz-two-pass", "meshlets", "scene-data", "sync-debug"):
    MOVES[R + "gpu-driven-dx12/" + name + ".md"] = P + "gpu-driven-dx12/" + name + ".md"
# 原理と重なる 4 ページは、対応する分野の中へ
MOVES[R + "shadows.md"] = "graphics/shadows/cost.md"
MOVES[R + "postprocess.md"] = "graphics/postprocess/cost.md"
MOVES[R + "taa-upscaling.md"] = "graphics/postprocess/taa-upscaling-cost.md"
MOVES[R + "particles.md"] = "graphics/translucency/particles-cost.md"

TITLES = {
    P + "index.md": "Pipeline and Optimization",
    P + "overview.md": "Rendering Pipeline Overview",
    P + "bottlenecks.md": "Bottlenecks",
    P + "bandwidth.md": "Memory Bandwidth",
    P + "forward-deferred.md": "Forward and Deferred",
    P + "light-culling.md": "Tiled and Clustered",
    P + "draw-calls.md": "Draw Calls and Batching",
    P + "culling.md": "Culling",
    P + "gpu-driven.md": "GPU Driven Rendering",
    P + "mesh-shaders.md": "Mesh Shader and Meshlet",
    P + "visibility-buffer.md": "Visibility Buffer",
    P + "overdraw.md": "Overdraw",
    P + "low-res-effects.md": "Low-Resolution Effects",
    P + "hiz.md": "Hi-Z and Screen-Space Tracing",
    P + "shader-cost.md": "Shader Cost",
    P + "lod.md": "LOD and Impostors",
    P + "texture-streaming.md": "Texture Streaming",
    P + "async-compute.md": "Async Compute",
    P + "2d.md": "2D Rendering",
    P + "tools.md": "Profiling Tools",
    P + "cases.md": "Optimization Case Studies",
    P + "gpu-driven-dx12/index.md": "GPU Driven (D3D12)",
    P + "gpu-driven-dx12/bindless.md": "Bindless",
    P + "gpu-driven-dx12/culling.md": "Compute Culling and Command Generation",
    P + "gpu-driven-dx12/execute-indirect.md": "ExecuteIndirect",
    P + "gpu-driven-dx12/hiz-two-pass.md": "Hi-Z Two-Pass Occlusion Culling",
    P + "gpu-driven-dx12/meshlets.md": "Meshlets and Mesh Shaders",
    P + "gpu-driven-dx12/scene-data.md": "Scene Data",
    P + "gpu-driven-dx12/sync-debug.md": "Synchronization and Debugging",
    "graphics/shadows/cost.md": "Shadow Cost",
    "graphics/postprocess/cost.md": "Post-Processing Cost",
    "graphics/postprocess/taa-upscaling-cost.md": "TAA, Upscaling and VRS Cost",
    "graphics/translucency/particles-cost.md": "Particles and Translucency Cost",
}
