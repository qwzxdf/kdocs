---
title: シェーダー
tags:
  - シェーダー
---

# シェーダー

このセクションは、<strong>ゲームの画面を作る、シェーダーで書く描画手法</strong>を、原理から説明します。「3D ゲーム」のセクションが座標・カメラ・基本のライティングといった土台を扱うのに対し、ここではその上に積む影・環境光遮蔽（AO）・反射・間接光・ポストプロセスなどを方式ごとに扱います。それぞれの手法が「何を近似しているのか」「どんな式なのか」「どこで破綻するのか」を、順に追います。速さの話（何が重く、どう減らすか）は、[描画最適化](../rendering/index.md)に分けて書いています。

## セクションの地図

各分野をタップ（クリック）すると、ページの一覧が開きます。見出しの下の最初のリンクは、その分野のトップです。

??? abstract map "Ambient Occlusion (AO)"
    <strong>[Ambient Occlusion (AO) のトップ](ao/index.md)</strong>

    - [AO Theory](ao/theory/index.md)
    - [Crytek SSAO](ao/ssao-crytek.md)
    - [Hemisphere SSAO](ao/ssao-hemisphere.md)
    - [Alchemy AO](ao/alchemy-ao.md)
    - [SAO (Scalable AO)](ao/sao.md)
    - [HBAO](ao/hbao.md)
    - [HBAO+](ao/hbao-plus.md)
    - [GTAO](ao/gtao.md)
    - [Ray-Traced, Distance-Field and Voxel AO](ao/world-space/index.md)
    - [AO Filtering](ao/filtering/index.md)
    - [AO Comparison](ao/comparison.md)
    - [AO Artifacts](ao/artifacts/index.md)

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

??? abstract map "Global Illumination (GI)"
    [Global Illumination (GI) のトップ](gi/index.md)

    - [GI Theory](gi/theory/index.md)
    - [Lightmaps](gi/lightmaps/index.md)
    - [Probe GI](gi/probes/index.md)
    - [SSGI](gi/ssgi.md)
    - [Voxel GI](gi/voxel-gi.md)
    - [DDGI](gi/ddgi.md)
    - [Ray-Traced GI](gi/rt-gi/index.md)
    - [GI Comparison](gi/comparison.md)

??? abstract map "Post-Processing"
    [Post-Processing のトップ](postprocess/index.md)

    - [Tone Mapping and Exposure](postprocess/tonemapping/index.md)
    - [Bloom](postprocess/bloom/index.md)
    - [Depth of Field (DOF)](postprocess/dof/index.md)
    - [Motion Blur](postprocess/motion-blur/index.md)
    - [Anti-Aliasing](postprocess/antialiasing/index.md)
    - [Color Grading](postprocess/color-grading/index.md)
    - [Lens Effects](postprocess/lens-effects/index.md)
    - [Outlines and Toon](postprocess/stylized/index.md)

??? abstract map "Translucency"
    [Translucency のトップ](translucency/index.md)

    - [Alpha Blending and Sorting](translucency/blending-sorting/index.md)
    - [Alpha Testing](translucency/alpha-test/index.md)
    - [Order-Independent Transparency (OIT)](translucency/oit/index.md)
    - [Refraction](translucency/refraction/index.md)

??? abstract map "Water"
    [Water のトップ](water/index.md)

    - [Water Waves](water/waves/index.md)
    - [Water Shading](water/shading/index.md)
    - [Shore Foam](water/shore-foam/index.md)
    - [Water Interaction](water/interaction/index.md)
    - [Underwater Rendering](water/underwater/index.md)

??? abstract map "Terrain"
    [Terrain のトップ](terrain/index.md)

    - [Heightmaps and Meshes](terrain/heightmap-mesh/index.md)
    - [LOD](terrain/lod/index.md)
    - [Terrain Texturing](terrain/texturing/index.md)
    - [Vegetation](terrain/vegetation/index.md)
    - [Terrain Generation](terrain/generation/index.md)

??? abstract map "Sky and Atmosphere"
    [Sky and Atmosphere のトップ](atmosphere/index.md)

    - [Sky Models](atmosphere/sky-models/index.md)
    - [Atmospheric Scattering](atmosphere/scattering/index.md)
    - [Aerial Perspective and Fog](atmosphere/aerial-fog/index.md)
    - [Volumetric Fog](atmosphere/volumetric-fog/index.md)
    - [Clouds](atmosphere/clouds/index.md)
    - [God Rays](atmosphere/god-rays/index.md)

??? abstract map "Skin and Hair"
    [Skin and Hair のトップ](skin-hair/index.md)

    - [Skin Overview](skin-hair/skin/index.md)
    - [Subsurface Scattering](skin-hair/skin/subsurface-theory.md)
    - [Diffusion Profiles](skin-hair/skin/diffusion-profile.md)
    - [Separable SSS](skin-hair/skin/screen-space-sss.md)
    - [Pre-Integrated Skin Shading](skin-hair/skin/pre-integrated.md)
    - [Thin Translucency](skin-hair/skin/thin-translucency.md)
    - [Skin Specular](skin-hair/skin/specular.md)
    - [Skin Micro-Detail](skin-hair/skin/micro-detail.md)
    - [Eye Rendering](skin-hair/skin/eyes.md)
    - [Hair Overview](skin-hair/hair/index.md)
    - [Hair Geometry](skin-hair/hair/geometry.md)
    - [Kajiya-Kay](skin-hair/hair/kajiya-kay.md)
    - [Marschner Model](skin-hair/hair/marschner.md)
    - [Hair Transparency](skin-hair/hair/transparency.md)
    - [Hair Shadows](skin-hair/hair/shadows.md)
    - [Hair Anti-Aliasing](skin-hair/hair/anti-aliasing.md)

## 読み方

| 目的 | 順番 |
| --- | --- |
| コードを実際に動かしたい（DirectX 11 の、土台） | [D3D11 Pass Recipes](../directx/dx11/pass-recipes.md)（ビュー・フルスクリーン三角形・ディスパッチ・定数バッファ・束縛の衝突）→ 各セクションへ |
| AO を実装したい | [AO Theory](ao/theory/index.md) → [Hemisphere SSAO](ao/ssao-hemisphere.md) → [AO Filtering](ao/filtering/index.md) → 品質を上げるなら [GTAO](ao/gtao.md) |
| 重い・遅いときに直したい | [描画最適化](../rendering/index.md)の[手法の地図](../rendering/index.md#手法の地図) → 各分野の「コスト」のページ（下の表） |
| 方式を選びたい | [AO Comparison](ao/comparison.md) |
| アーティファクトを直したい | [AO Artifacts](ao/artifacts/index.md) |

## 原理と最適化の対応

同じ話題は、<strong>原理（どう見せるか）をこのセクション、コスト（どう軽くするか）を[描画最適化](../rendering/index.md)</strong>に分けて書いています。

| 話題 | 原理（このセクション） | 軽くする（描画最適化） |
| --- | --- | --- |
| 影 | [Shadows](shadows/index.md) | [影のコスト](../rendering/shadows.md) |
| ポストプロセス | [Post-Processing](postprocess/index.md) | [ポストプロセス](../rendering/postprocess.md)・[TAA・アップスケーラ・VRS](../rendering/taa-upscaling.md) |
| AO・反射の高速化 | [Ambient Occlusion (AO)](ao/index.md)・[Reflections](reflections/index.md) | [Hi-Z とスクリーン空間トレース](../rendering/hiz.md)・[縮小バッファの効果](../rendering/low-res-effects.md) |
| 半透明 | [Translucency](translucency/index.md) | [パーティクルと半透明](../rendering/particles.md)・[オーバードロー](../rendering/overdraw.md) |
| 地形の LOD | [Terrain](terrain/index.md) | [LOD とインポスター](../rendering/lod.md) |
| シェーダーの計算 | （各分野のコード） | [シェーダーのコスト](../rendering/shader-cost.md) |

## 関連ページ

- [3D ゲーム](../3d/index.md)
- [法線とライティング](../3d/lighting-normals.md)
- [PBR](../3d/pbr.md)
- [描画最適化](../rendering/index.md)
