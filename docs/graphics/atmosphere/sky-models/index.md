---
title: Sky Models
tags:
  - 描画
---

# Sky Models

<strong>空は背景として画面の大きな面積を占め、シーンの雰囲気を決めます</strong>。単純なグラデーションから物理に基づく計算まで、方法がいくつかあります。このセクションでは空の描き方・グラデーション・解析的なモデル・太陽と月と星・空をライティングに使う・昼夜のサイクルを 1 つずつ別のページで説明します。

## 空の描き方
<strong>空はワールドの一番遠くにある背景</strong>です。描き方は 2 通りあります。

空の描き方は 2 通りあります。スカイボックスはキューブマップ（6 枚の絵）を貼った箱をカメラ中心に描きます。全画面で計算する方式は画面の各ピクセルから視線の向きを求め、その向きの色を計算します。

スカイボックスは絵が固定ですが、全画面計算は時刻や天気に応じて色を変えられます。

### 視線の向きを求める

ピクセルごとの視線の向きは、逆射影行列で作ります。

```hlsl
float3 ViewDirection(float2 uv) {
  float2 ndc = float2(uv.x * 2.0 - 1.0, 1.0 - uv.y * 2.0);
  float4 clip = float4(ndc, 1.0, 1.0);
  float4 world = mul(clip, inverse_view_projection);
  return normalize(world.xyz / world.w - camera_position);
}
```

コードの要点です。クリップ空間の Z = 1 は最も遠い面です（リバース Z なら 0）。`mul(行ベクトル, 行列)` は行ベクトル規約（`v * M`）に従います。カメラ位置を引いてワールド位置から方向を求めます。

### 深度テストで最奥だけに描く

空は他の物を描いた後で深度が最奥のピクセルだけを塗ります（描画量が減る）。

空は他の物を描いた後に深度が最奥のピクセルだけを塗ると、描画量が減ります。方法は 2 つあります。フル スクリーン三角形を Z = 1（最奥）で描き、深度テストの比較を `LESS_EQUAL` にする方法。不透明物の後で半透明の前に描くことで、早期 Z により物があるピクセルを省略する方法です。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Gradient Sky](gradient.md) | 最も簡単な空 |
| [Analytic Sky Models](analytic.md) | Preetham・Hosek-Wilkie |
| [Sun, Moon and Stars](celestial.md) | 天体の描き方 |
| [Using the Sky for Lighting](sky-lighting.md) | 環境光・IBL |
| [Day-Night Cycle](day-night.md) | 時間による変化 |

## 空を描く方法の選択肢

空の色を決める方法は <strong>単純な、グラデーション</strong>から 物理ベースの、大気散乱まで幅があります。

| 方式 | 内容 | 品質 | コスト | 向く場面 |
| --- | --- | --- | --- | --- |
| グラデーション | 天頂の色 → 地平線の色を補間する | 低 | 最小 | モバイル、ローポリ、スタイライズ |
| 解析的な空のモデル（Preetham、Hošek-Wilkie） | 太陽の高さと、濁りから空の色を式で計算 | 中〜高 | 小 | 昼の空だけ。リアルな昼空 |
| 事前計算の大気散乱（Bruneton） | 散乱を事前に、テクスチャへ | 高 | 小（実行時） | 固定の大気 |
| リアルタイムの大気散乱（Hillaire） | 4 つの小さな、LUT を毎フレーム、更新 | 高 | 小 | 時間帯の変化、宇宙から地上まで |
| キューブマップ（HDRI） | 撮影・作成した、空の画像をそのまま貼る | 最高（実写なら） | 最小 | 固定の空。時間帯の変化は複数枚の補間 |

## 選び方

| 状況 | おすすめ |
| --- | --- |
| まず、空を出したい | グラデーション（[Gradient Sky](gradient.md)） |
| 昼のリアルな空（時間帯はあまり、変えない） | 解析的モデル（[Analytic Sky Models](analytic.md)） |
| 時間帯が変わる（朝、昼、夕、夜）、天候 | Hillaire（[Hillaire 2020: Four LUTs](../scattering/hillaire.md)） |
| スタイライズ（アニメ調の空） | グラデーション + ノイズの雲 + 太陽・月の絵 |

## 空の構成要素

空は <strong>1 つの色</strong>ではありません。複数の層を重ねます。

```text
奥     星空（夜）
 │     月、太陽の円盤（[Sun, Moon and Stars](celestial.md)）
 │     大気の散乱（空の青さ、夕焼け）
 │     雲（[Clouds](../clouds/index.md)）
手前   遠景（山）、空気遠近法（[Aerial Perspective and Fog](../aerial-fog/index.md)）
```

| 層 | 内容 | ページ |
| --- | --- | --- |
| 大気の散乱（空の色） | 空の背景の色 | このカテゴリ |
| 太陽・月・星 | 空に浮かぶ天体 | [Sun, Moon and Stars](celestial.md) |
| 雲 | 空の中の立体物 | [Clouds](../clouds/index.md) |
| 空気遠近法 | 地上の遠景の、霞 | [Aerial Perspective and Fog](../aerial-fog/index.md) |

## 空のもう 1 つの役割：ライティング

空は <strong>見た目</strong>だけでなく 光源でもあります。空全体がシーンを照らす（環境光）ので、空の色が地面や物の色に影響します（[Using the Sky for Lighting](sky-lighting.md)）。空の色を変えたら環境光も変える必要があります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 空は背景であり、ライティングの源

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique", Computer Graphics Forum (Eurographics Symposium on Rendering 2020)
- Bruneton, Neyret, "Precomputed Atmospheric Scattering", Computer Graphics Forum (Eurographics Symposium on Rendering 2008)
- Preetham, Shirley, Smits, "A Practical Analytic Model for Daylight", SIGGRAPH 1999
- Hošek, Wilkie, "An Analytic Model for Full Spectral Sky-Dome Radiance", ACM Transactions on Graphics (SIGGRAPH 2012)
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018

## 関連ページ

- [Sky and Atmosphere](../index.md)
- [Atmospheric Scattering](../scattering/index.md)
- [Clouds](../clouds/index.md)
