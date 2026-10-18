---
title: 描画
tags:
  - 描画
---

# 描画

このセクションは、**ゲームの画面を作る描画手法**を、**原理から**説明します。「3D ゲーム」のセクションが座標・カメラ・基本のライティングといった**土台**を扱うのに対し、ここではその上に積む**影・環境光遮蔽（AO）・反射・間接光・ポストプロセス**などを**方式ごとに**扱います。それぞれの手法が「何を近似しているのか」「どんな式なのか」「どこで破綻するのか」を、順に追います。速さの話（何が重く、どう減らすか）は、[描画最適化](../rendering/index.md)に分けて書いています。

## アイコンの見方

**各項目の名前の横に、負荷と品質の目安をアイコンで付けています**。

| アイコン | 意味 |
| --- | --- |
| <span class="perf perf-3">⚡軽い</span> | **パフォーマンス：負荷が小さい**（**フレームの数 %**） |
| <span class="perf perf-2">⚡普通</span> | **パフォーマンス：中程度の負荷**（**数 %〜10 % 前後**） |
| <span class="perf perf-1">⚡重い</span> | **パフォーマンス：負荷が大きい**（**使いどころを絞る・品質設定で切る**） |
| <span class="qual qual-1">★☆☆</span>〜<span class="qual qual-3">★★★</span> | **品質：★ が多いほど、見た目が正確できれい** |

**品質のアイコンが無い項目**は、**好みや表現の問題で、「高いほど良い」とは言えないもの**です（**色収差・セル シェーディングなど**）。**負荷は、画面の解像度・シーン・GPU で大きく変わる**ので、**あくまで相対的な目安**です。

## セクションの地図

| 分野 | 内容 |
| --- | --- |
| [Ambient Occlusion (AO)](ao/index.md) | AO Theory・Crytek SSAO・Hemisphere SSAO・Alchemy AO・SAO (Scalable AO)・HBAO・HBAO+・GTAO・Ray-Traced, Distance-Field and Voxel AO・AO Filtering・AO Comparison・AO Artifacts |
| [Shadows](shadows/index.md) | Shadow Map Basics・Shadow Bias・PCF・PCSS・VSM, ESM and MSM・Cascaded Shadow Maps (CSM)・Point and Spot Light Shadows・Contact Shadows・Distance Field Shadows・Ray-Traced Shadows・Virtual Shadow Maps・Shadow Volumes・Special Cases・Shadow Techniques Compared |
| [Reflections](reflections/index.md) | Planar Reflections・Reflection Probes・SSR Basics・Hi-Z SSR・Stochastic SSR・SSR Fallback and Compositing・Ray-Traced Reflections・Reflection Comparison |
| [Global Illumination (GI)](gi/index.md) | GI Theory・Lightmaps・Probe GI・SSGI・Voxel GI・DDGI・Ray-Traced GI・GI Comparison |
| [Post-Processing](postprocess/index.md) | Tone Mapping and Exposure・Bloom・Depth of Field (DOF)・Motion Blur・Anti-Aliasing・Color Grading・Lens Effects・Outlines and Toon |
| [Translucency](translucency/index.md) | Alpha Blending and Sorting・Alpha Testing・Order-Independent Transparency (OIT)・Refraction |
| [Water](water/index.md) | Water Waves・Water Shading・Shore Foam・Water Interaction・Underwater Rendering |
| [Terrain](terrain/index.md) | Heightmaps and Meshes・LOD・Terrain Texturing・Vegetation・Terrain Generation |
| [Sky and Atmosphere](atmosphere/index.md) | Sky Models・Atmospheric Scattering・Aerial Perspective and Fog・Volumetric Fog・Clouds・God Rays |
| [Skin and Hair](skin-hair/index.md) | Skin Overview・Subsurface Scattering・Diffusion Profiles・Separable SSS・Pre-Integrated Skin Shading・Thin Translucency・Skin Specular・Skin Micro-Detail・Eye Rendering・Hair Overview・Hair Geometry・Kajiya-Kay・Marschner Model・Hair Transparency・Hair Shadows・Hair Anti-Aliasing |

## 読み方

| 目的 | 順番 |
| --- | --- |
| **AO を実装したい** | [AO Theory](ao/theory/index.md) → [Hemisphere SSAO](ao/ssao-hemisphere.md) → [AO Filtering](ao/filtering/index.md) → 品質を上げるなら [GTAO](ao/gtao.md) |
| **方式を選びたい** | [AO Comparison](ao/comparison.md) |
| **アーティファクトを直したい** | [AO Artifacts](ao/artifacts/index.md) |

## 関連ページ

- [3D ゲーム](../3d/index.md)
- [法線とライティング](../3d/lighting-normals.md)
- [PBR](../3d/pbr.md)
- [描画最適化](../rendering/index.md)
