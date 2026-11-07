---
title: グラフィックス
tags:
  - シェーダー
  - 描画
  - 最適化
---

# グラフィックス

このセクションは、<strong>ゲームの画面を作る描画手法</strong>を、原理から軽量化まで説明します。「3D ゲーム」のセクションが座標・カメラ・基本のライティングといった土台を扱うのに対し、ここではその上に積む影・環境光遮蔽（AO）・反射・間接光・ポストプロセスなどを方式ごとに扱います。それぞれの手法が「何を近似しているのか」「どんな式なのか」「どこで破綻するのか」を順に追います。各分野には、その手法を軽くする話（コスト）のページもあります。描画全体の流れと、何が重くなるかは、[Optimization](optimization/index.md)で説明します。

## セクションの地図

各分野をタップ（クリック）すると、ページの一覧が開きます。各分野の最初のリンクは、その分野のトップです。

??? abstract map "Lighting"
    [Lighting のトップ](lighting/index.md)

    - [Forward and Deferred](lighting/forward-deferred.md)
    - [Tiled and Clustered](lighting/light-culling.md)
    - [Visibility Buffer](lighting/visibility-buffer.md)

??? abstract map "Shadows"
    [Shadows のトップ](shadows/index.md)

    - [Shadow Map Basics](shadows/shadow-map-basics/index.md)
    - [Shadow Bias](shadows/bias/index.md)
    - [PCF](shadows/pcf.md)
    - [PCSS](shadows/pcss.md)
    - [VSM, ESM and MSM](shadows/vsm/index.md)
    - [Cascaded Shadow Maps (CSM)](shadows/cascaded.md)
    - [Point and Spot Light Shadows](shadows/local-lights/index.md)
    - [Contact Shadows](shadows/contact-shadows.md)
    - [Distance Field Shadows](shadows/sdf-shadows.md)
    - [Ray-Traced Shadows](shadows/ray-traced.md)
    - [Virtual Shadow Maps](shadows/virtual-shadow-maps.md)
    - [Shadow Volumes](shadows/shadow-volumes.md)
    - [Special Cases](shadows/special-cases/index.md)
    - [Shadow Techniques Compared](shadows/comparison.md)
    - [Shadow Cost](shadows/cost.md)

??? abstract map "Ambient Occlusion (AO)"
    [Ambient Occlusion (AO) のトップ](ao/index.md)

    - [AO Theory](ao/theory/index.md)
    - [Crytek SSAO](ao/ssao-crytek.md)
    - [Hemisphere SSAO](ao/ssao-hemisphere.md)
    - [Alchemy AO](ao/alchemy-ao.md)
    - [SAO (Scalable AO)](ao/sao.md)
    - [HBAO](ao/hbao.md)
    - [HBAO+](ao/hbao-plus.md)
    - [GTAO](ao/gtao.md)
    - [XeGTAO](ao/xegtao.md)
    - [ASSAO and CACAO](ao/assao-cacao.md)
    - [MSSAO](ao/mssao.md)
    - [Ray-Traced, Distance-Field and Voxel AO](ao/world-space/index.md)
    - [AO Filtering](ao/filtering/index.md)
    - [AO Comparison](ao/comparison.md)
    - [AO Artifacts](ao/artifacts/index.md)

??? abstract map "Global Illumination (GI)"
    [Global Illumination (GI) のトップ](gi/index.md)

    - [GI Theory](gi/theory/index.md)
    - [Lightmaps](gi/lightmaps/index.md)
    - [Probe GI](gi/probes/index.md)
    - [SSGI](gi/ssgi.md)
    - [Voxel GI](gi/voxel-gi.md)
    - [DDGI](gi/ddgi.md)
    - [Ray-Traced GI](gi/rt-gi/index.md)
    - [ReSTIR](gi/restir.md)
    - [Lumen and Nanite](gi/lumen.md)
    - [GI Comparison](gi/comparison.md)

??? abstract map "Reflections"
    [Reflections のトップ](reflections/index.md)

    - [Planar Reflections](reflections/planar.md)
    - [Reflection Probes](reflections/probes/index.md)
    - [SSR Basics](reflections/ssr-basics/index.md)
    - [Hi-Z SSR](reflections/ssr-hiz.md)
    - [Stochastic SSR](reflections/ssr-stochastic.md)
    - [SSR Fallback and Compositing](reflections/ssr-fallback.md)
    - [Ray-Traced Reflections](reflections/rt-reflections/index.md)
    - [Reflection Comparison](reflections/comparison.md)

??? abstract map "Translucency"
    [Translucency のトップ](translucency/index.md)

    - [Alpha Blending and Sorting](translucency/blending-sorting/index.md)
    - [Alpha Testing](translucency/alpha-test/index.md)
    - [Order-Independent Transparency (OIT)](translucency/oit/index.md)
    - [Refraction](translucency/refraction/index.md)
    - [Particles and Translucency Cost](translucency/particles-cost.md)

??? abstract map "Skin and Hair"
    [Skin and Hair のトップ](skin-hair/index.md)

    - [Skin Overview](skin-hair/skin/index.md)
    - [Hair Overview](skin-hair/hair/index.md)

??? abstract map "Terrain"
    [Terrain のトップ](terrain/index.md)

    - [Heightmaps and Meshes](terrain/heightmap-mesh/index.md)
    - [Terrain LOD](terrain/lod/index.md)
    - [Terrain Texturing](terrain/texturing/index.md)
    - [Vegetation](terrain/vegetation/index.md)
    - [Terrain Generation](terrain/generation/index.md)

??? abstract map "Water"
    [Water のトップ](water/index.md)

    - [Water Waves](water/waves/index.md)
    - [Water Shading](water/shading/index.md)
    - [Shore Foam](water/shore-foam/index.md)
    - [Water Interaction](water/interaction/index.md)
    - [Underwater Rendering](water/underwater/index.md)

??? abstract map "Sky and Atmosphere"
    [Sky and Atmosphere のトップ](atmosphere/index.md)

    - [Sky Models](atmosphere/sky-models/index.md)
    - [Atmospheric Scattering](atmosphere/scattering/index.md)
    - [Aerial Perspective and Fog](atmosphere/aerial-fog/index.md)
    - [Volumetric Fog](atmosphere/volumetric-fog/index.md)
    - [Clouds](atmosphere/clouds/index.md)
    - [God Rays](atmosphere/god-rays/index.md)

??? abstract map "Post-Processing"
    [Post-Processing のトップ](postprocess/index.md)

    - [Tone Mapping and Exposure](postprocess/tonemapping/index.md)
    - [Color Grading](postprocess/color-grading/index.md)
    - [Bloom](postprocess/bloom/index.md)
    - [Lens Effects](postprocess/lens-effects/index.md)
    - [Depth of Field (DOF)](postprocess/dof/index.md)
    - [Motion Blur](postprocess/motion-blur/index.md)
    - [Anti-Aliasing](postprocess/antialiasing/index.md)
    - [Upscaling](postprocess/upscaling/index.md)
    - [Outlines and Toon](postprocess/stylized/index.md)
    - [Post-Processing Cost](postprocess/cost.md)
    - [TAA, Upscaling and VRS Cost](postprocess/taa-upscaling-cost.md)

??? abstract map "Draw Call"
    [Draw Call のトップ](draw-call/index.md)

    - [Rendering Pipeline Overview](draw-call/overview.md)
    - [Draw Calls and Batching](draw-call/draw-calls.md)
    - [Culling](draw-call/culling.md)
    - [LOD and Impostors](draw-call/lod.md)
    - [GPU Driven Rendering](draw-call/gpu-driven.md)
    - [GPU Driven (D3D12)](draw-call/gpu-driven-dx12/index.md)
    - [Mesh Shader and Meshlet](draw-call/mesh-shaders.md)
    - [2D Rendering](draw-call/2d.md)

??? abstract map "Optimization"
    [Optimization のトップ](optimization/index.md)

    - [Bottlenecks](optimization/bottlenecks.md)
    - [Memory Bandwidth](optimization/bandwidth.md)
    - [Overdraw](optimization/overdraw.md)
    - [Low-Resolution Effects](optimization/low-res-effects.md)
    - [Hi-Z and Screen-Space Tracing](optimization/hiz.md)
    - [Shader Cost](optimization/shader-cost.md)
    - [Texture Streaming](optimization/texture-streaming.md)
    - [Async Compute](optimization/async-compute.md)
    - [Profiling Tools](optimization/tools.md)
    - [Optimization Case Studies](optimization/cases.md)

## 読み方

| 目的 | 順番 |
| --- | --- |
| コードを実際に動かしたい（DirectX 11 の、土台） | [D3D11 Pass Recipes](../directx/dx11/pass-recipes.md)（ビュー・フルスクリーン三角形・ディスパッチ・定数バッファ・束縛の衝突）→ 各セクションへ |
| 影を付けたい | [Shadow Map Basics](shadows/shadow-map-basics/index.md) → [Shadow Bias](shadows/bias/index.md) → [PCF](shadows/pcf.md) → 広い場面なら [Cascaded Shadow Maps (CSM)](shadows/cascaded.md) |
| AO を実装したい | [AO Theory](ao/theory/index.md) → [Hemisphere SSAO](ao/ssao-hemisphere.md) → [AO Filtering](ao/filtering/index.md) → 品質を上げるなら [GTAO](ao/gtao.md) |
| 間接光を入れたい | [GI Theory](gi/theory/index.md) → [Lightmaps](gi/lightmaps/index.md) または [Probe GI](gi/probes/index.md) → 動的にするなら [GI Comparison](gi/comparison.md) |
| 反射を入れたい | [Reflection Probes](reflections/probes/index.md) → [SSR Basics](reflections/ssr-basics/index.md) → [SSR Fallback and Compositing](reflections/ssr-fallback.md) |
| 画面の仕上げをしたい | [Tone Mapping and Exposure](postprocess/tonemapping/index.md) → [Bloom](postprocess/bloom/index.md) → [Anti-Aliasing](postprocess/antialiasing/index.md) |
| 重い・遅いときに直したい | [Optimization](optimization/index.md)の[手法の地図](optimization/index.md#手法の地図) → 各分野の「Cost」のページ（[Shadow Cost](shadows/cost.md)・[Post-Processing Cost](postprocess/cost.md) など） |
| 方式を選びたい | 各分野の比較ページ（[Shadow Techniques Compared](shadows/comparison.md)・[AO Comparison](ao/comparison.md)・[GI Comparison](gi/comparison.md)・[Reflection Comparison](reflections/comparison.md)） |
| アーティファクトを直したい | [AO Artifacts](ao/artifacts/index.md)・[Shadow Bias](shadows/bias/index.md)・[Special Cases](shadows/special-cases/index.md) |

## 関連ページ

- [3D ゲーム](../3d/index.md)
- [法線とライティング](../3d/lighting-normals.md)
- [PBR](../3d/pbr.md)
- [Optimization](optimization/index.md)
