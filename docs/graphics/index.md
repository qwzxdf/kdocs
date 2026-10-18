---
title: 描画
tags:
  - 描画
---

# 描画

このセクションは、<strong>ゲームの画面を作る描画手法</strong>を、<strong>原理から</strong>説明します。「3D ゲーム」のセクションが座標・カメラ・基本のライティングといった土台を扱うのに対し、ここではその上に積む影・環境光遮蔽（AO）・反射・間接光・ポストプロセスなどを方式ごとに扱います。それぞれの手法が「何を近似しているのか」「どんな式なのか」「どこで破綻するのか」を、順に追います。速さの話（何が重く、どう減らすか）は、[描画最適化](../rendering/index.md)に分けて書いています。

## アイコンの見方

<strong>各項目の名前の横に、速度・品質・難易度の目安を、ローマ数字（Ⅰ〜Ⅴ）のバッジで付けています</strong>（速度は、大きいほど速い）（それぞれ 5 段階）。

### 速度（パフォーマンス。Ⅴ が最も速い）

| アイコン | 目安 |
| --- | --- |
| <span class="perf perf-lv1">速度 Ⅴ</span> | ほぼ無料（フレームの 0.1 ms 未満） |
| <span class="perf perf-lv2">速度 Ⅳ</span> | 0.1〜0.3 ms |
| <span class="perf perf-lv3">速度 Ⅲ</span> | 0.3〜1 ms |
| <span class="perf perf-lv4">速度 Ⅱ</span> | 1〜3 ms。使いどころを選ぶ |
| <span class="perf perf-lv5">速度 Ⅰ</span> | 3 ms 超。品質設定で切る・専用の工夫が要る |

### 品質（見た目の正確さ・きれいさ）

| アイコン | 目安 |
| --- | --- |
| <span class="qual qual-1">品質 Ⅰ</span> | かんたんな近似。見た目は粗い |
| <span class="qual qual-2">品質 Ⅱ</span> | 簡易 |
| <span class="qual qual-3">品質 Ⅲ</span> | 標準 |
| <span class="qual qual-4">品質 Ⅳ</span> | 高い |
| <span class="qual qual-5">品質 Ⅴ</span> | 基準になる正確さ（レイトレーシングなど） |

### 難易度（理解・実装の難しさ）

| アイコン | 目安 |
| --- | --- |
| <span class="diff diff-1">難易度 Ⅰ</span> | 入門。式も要らない |
| <span class="diff diff-2">難易度 Ⅱ</span> | やさしい。基本の数学・1 回の描画で書ける |
| <span class="diff diff-3">難易度 Ⅲ</span> | ふつう。複数のパス・行列・サンプリングの理解が要る |
| <span class="diff diff-4">難易度 Ⅳ</span> | 難しい。確率・積分・時間方向の扱い・技術の組み合わせ |
| <span class="diff diff-5">難易度 Ⅴ</span> | 上級。論文レベル・最新の手法・自前の実装が大変 |

<strong>品質のアイコンが無い項目</strong>は、<strong>好みや表現の問題で、「高いほど良い」とは言えないもの</strong>です（色収差・セル シェーディングなど）。負荷は、画面の解像度・シーン・GPU で大きく変わるので、あくまで相対的な目安です。

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
| AO を実装したい | [AO Theory](ao/theory/index.md) → [Hemisphere SSAO](ao/ssao-hemisphere.md) → [AO Filtering](ao/filtering/index.md) → 品質を上げるなら [GTAO](ao/gtao.md) |
| 方式を選びたい | [AO Comparison](ao/comparison.md) |
| アーティファクトを直したい | [AO Artifacts](ao/artifacts/index.md) |

## 関連ページ

- [3D ゲーム](../3d/index.md)
- [法線とライティング](../3d/lighting-normals.md)
- [PBR](../3d/pbr.md)
- [描画最適化](../rendering/index.md)
