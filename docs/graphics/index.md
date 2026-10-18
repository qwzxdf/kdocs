---
title: 描画
tags:
  - 描画
---

# 描画

このセクションは、**ゲームの画面を作る描画手法**を、**原理から**説明します。「3D ゲーム」のセクションが座標・カメラ・基本のライティングといった**土台**を扱うのに対し、ここではその上に積む**影・環境光遮蔽（AO）・反射・間接光・ポストプロセス**などを**方式ごとに**扱います。それぞれの手法が「何を近似しているのか」「どんな式なのか」「どこで破綻するのか」を、順に追います。速さの話（何が重く、どう減らすか）は、[描画最適化](../rendering/index.md)に分けて書いています。

## How to Read the Icons {#アイコンの見方}

**各項目の名前の横に、負荷と品質の目安をアイコンで付けています**。

| アイコン | 意味 |
| --- | --- |
| <span class="perf perf-3">⚡軽い</span> | **パフォーマンス：負荷が小さい**（**フレームの数 %**） |
| <span class="perf perf-2">⚡普通</span> | **パフォーマンス：中程度の負荷**（**数 %〜10 % 前後**） |
| <span class="perf perf-1">⚡重い</span> | **パフォーマンス：負荷が大きい**（**使いどころを絞る・品質設定で切る**） |
| <span class="qual qual-1">★☆☆</span>〜<span class="qual qual-3">★★★</span> | **品質：★ が多いほど、見た目が正確できれい** |

**品質のアイコンが無い項目**は、**好みや表現の問題で、「高いほど良い」とは言えないもの**です（**色収差・セル シェーディングなど**）。**負荷は、画面の解像度・シーン・GPU で大きく変わる**ので、**あくまで相対的な目安**です。

## Section Map {#セクションの地図}

| 分野 | 内容 |
| --- | --- |
| [Ambient Occlusion (AO)](ao/index.md) | 原理・SSAO・Alchemy・SAO・HBAO・HBAO+・GTAO・レイトレ AO・距離場 AO・フィルタ |
| [Shadows](shadows/index.md) | シャドウ マップ・バイアス・PCF・PCSS・VSM・CSM・ローカル ライト・接触影・距離場・レイトレ影・仮想シャドウ マップ |
| [Reflections](reflections/index.md) | 平面反射・プローブ・SSR（基礎・Hi-Z・確率的）・フォールバック・レイトレ反射 |
| [Global Illumination (GI)](gi/index.md) | 理論・ライトマップ・プローブ・SSGI・ボクセル・DDGI・レイトレ GI・Radiance Cascades |
| [Post-Processing](postprocess/index.md) | トーンマップ・ブルーム・DOF・モーション ブラー・AA・カラー グレーディング・レンズ効果・輪郭線 |
| [Translucency](translucency/index.md) | ブレンドとソート・アルファ テスト・OIT・屈折 |
| [Water](water/index.md) | 波・シェーディング・岸辺と泡・波紋・水中 |
| [Terrain](terrain/index.md) | 高さマップ・LOD・テクスチャ・草と木・生成 |
| [Sky and Atmosphere](atmosphere/index.md) | 空のモデル・大気散乱・距離フォグ・ボリューメトリック フォグ・雲・光の筋 |
| [Skin and Hair](skin-hair/index.md) | 次表面散乱・肌の鏡面・目・髪のシェーディング・髪の透明と影 |

## How to Read {#読み方}

| 目的 | 順番 |
| --- | --- |
| **AO を実装したい** | [AO Theory](ao/theory/index.md) → [SSAO（半球）](ao/ssao-hemisphere.md) → [フィルタ](ao/filtering/index.md) → 品質を上げるなら [GTAO](ao/gtao.md) |
| **方式を選びたい** | [AO Comparison](ao/comparison.md) |
| **アーティファクトを直したい** | [AO Artifacts](ao/artifacts/index.md) |

## Related Pages {#関連ページ}

- [3D ゲーム](../3d/index.md)
- [法線とライティング](../3d/lighting-normals.md)
- [PBR](../3d/pbr.md)
- [描画最適化](../rendering/index.md)
