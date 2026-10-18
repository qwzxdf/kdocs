---
title: 描画
tags:
  - 描画
---

# 描画

このセクションは、<strong>ゲームの画面を作る描画手法</strong>を、<strong>原理から</strong>説明します。「3D ゲーム」のセクションが座標・カメラ・基本のライティングといった土台を扱うのに対し、ここではその上に積む影・環境光遮蔽（AO）・反射・間接光・ポストプロセスなどを方式ごとに扱います。それぞれの手法が「何を近似しているのか」「どんな式なのか」「どこで破綻するのか」を、順に追います。速さの話（何が重く、どう減らすか）は、[描画最適化](../rendering/index.md)に分けて書いています。

## アイコンの見方

<strong>各項目の名前の横に、速度・品質・難易度の目安を、ローマ数字（Ⅰ〜Ⅴ）のバッジで付けています</strong>（それぞれ 5 段階）。

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
    <strong>[Shadows のトップ](shadows/index.md)</strong>

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
    <strong>[Reflections のトップ](reflections/index.md)</strong>

    - [Planar Reflections](reflections/planar.md)
    - [Reflection Probes](reflections/probes/index.md)
    - [SSR Basics](reflections/ssr-basics/index.md)
    - [Hi-Z SSR](reflections/ssr-hiz.md)
    - [Stochastic SSR](reflections/ssr-stochastic.md)
    - [SSR Fallback and Compositing](reflections/ssr-fallback.md)
    - [Ray-Traced Reflections](reflections/rt-reflections/index.md)
    - [Reflection Comparison](reflections/comparison.md)

??? abstract map "Global Illumination (GI)"
    <strong>[Global Illumination (GI) のトップ](gi/index.md)</strong>

    - [GI Theory](gi/theory/index.md)
    - [Lightmaps](gi/lightmaps/index.md)
    - [Probe GI](gi/probes/index.md)
    - [SSGI](gi/ssgi.md)
    - [Voxel GI](gi/voxel-gi.md)
    - [DDGI](gi/ddgi.md)
    - [Ray-Traced GI](gi/rt-gi/index.md)
    - [GI Comparison](gi/comparison.md)

??? abstract map "Post-Processing"
    <strong>[Post-Processing のトップ](postprocess/index.md)</strong>

    - [Tone Mapping and Exposure](postprocess/tonemapping/index.md)
    - [Bloom](postprocess/bloom/index.md)
    - [Depth of Field (DOF)](postprocess/dof/index.md)
    - [Motion Blur](postprocess/motion-blur/index.md)
    - [Anti-Aliasing](postprocess/antialiasing/index.md)
    - [Color Grading](postprocess/color-grading/index.md)
    - [Lens Effects](postprocess/lens-effects/index.md)
    - [Outlines and Toon](postprocess/stylized/index.md)

??? abstract map "Translucency"
    <strong>[Translucency のトップ](translucency/index.md)</strong>

    - [Alpha Blending and Sorting](translucency/blending-sorting/index.md)
    - [Alpha Testing](translucency/alpha-test/index.md)
    - [Order-Independent Transparency (OIT)](translucency/oit/index.md)
    - [Refraction](translucency/refraction/index.md)

??? abstract map "Water"
    <strong>[Water のトップ](water/index.md)</strong>

    - [Water Waves](water/waves/index.md)
    - [Water Shading](water/shading/index.md)
    - [Shore Foam](water/shore-foam/index.md)
    - [Water Interaction](water/interaction/index.md)
    - [Underwater Rendering](water/underwater/index.md)

??? abstract map "Terrain"
    <strong>[Terrain のトップ](terrain/index.md)</strong>

    - [Heightmaps and Meshes](terrain/heightmap-mesh/index.md)
    - [LOD](terrain/lod/index.md)
    - [Terrain Texturing](terrain/texturing/index.md)
    - [Vegetation](terrain/vegetation/index.md)
    - [Terrain Generation](terrain/generation/index.md)

??? abstract map "Sky and Atmosphere"
    <strong>[Sky and Atmosphere のトップ](atmosphere/index.md)</strong>

    - [Sky Models](atmosphere/sky-models/index.md)
    - [Atmospheric Scattering](atmosphere/scattering/index.md)
    - [Aerial Perspective and Fog](atmosphere/aerial-fog/index.md)
    - [Volumetric Fog](atmosphere/volumetric-fog/index.md)
    - [Clouds](atmosphere/clouds/index.md)
    - [God Rays](atmosphere/god-rays/index.md)

??? abstract map "Skin and Hair"
    <strong>[Skin and Hair のトップ](skin-hair/index.md)</strong>

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
| 方式を選びたい | [AO Comparison](ao/comparison.md) |
| アーティファクトを直したい | [AO Artifacts](ao/artifacts/index.md) |

## 関連ページ

- [3D ゲーム](../3d/index.md)
- [法線とライティング](../3d/lighting-normals.md)
- [PBR](../3d/pbr.md)
- [描画最適化](../rendering/index.md)
