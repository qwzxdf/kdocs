---
title: 侵食
tags:
  - 描画
---

# 侵食

**現実の地形は、雨と川の流れで削られています**。**シミュレーションで侵食を加えると、谷や尾根が自然になります**。このページでは、**侵食のシミュレーション**を説明します。

!!! tip "ポイント"
    - **水滴を落として、流れる様子を追う**（水滴ベース）。
    - **傾きの大きい所は削られ、緩い所に堆積する**。
    - **熱侵食：急斜面が崩れる**。
    - **GPU で並列に計算できる**。
    - **重いので、事前に計算するのが普通**。

## 侵食
**ノイズだけの地形は、「ふにゃふにゃ」して不自然**です。**本物の山は水の流れが削った谷と尾根の網目**があります。**水による侵食を模擬**すると**劇的にリアル**になります。

| 方式 | 内容 |
| --- | --- |
| <strong>熱侵食（Thermal）</strong> | **急すぎる斜面の土が崩れて下に積もる**（**安息角**）。**崖が緩やかな斜面と裾野になる** |
| <strong>水力侵食（Hydraulic）</strong> | **雨が降り、流れて、削り、運び、堆積**。**谷・尾根・扇状地ができる** |
| **粒子ベース** | **水滴を 1 つずつ、地形の上で転がす**。**簡単** |
| <strong>格子ベース（パイプ モデル）</strong> | **水の量・流れ・土砂を格子で計算**。**GPU 向き** |

### 粒子ベースの水力侵食

**水滴をランダムな位置に落とし**、**高さの勾配に沿って転がします**。**勢い（速さ）と水量で運べる土砂の量が決まり**、**多すぎれば堆積、少なければ削ります**。

```cpp
void ErodeDroplet(HeightMap& map, std::mt19937& rng, const ErosionParams& p) {
  float x = RandomRange(rng, 1.0f, map.width - 2.0f);
  float y = RandomRange(rng, 1.0f, map.height - 2.0f);
  float dir_x = 0.0f;
  float dir_y = 0.0f;
  float speed = p.initial_speed;
  float water = p.initial_water;
  float sediment = 0.0f;

  for (int step = 0; step < p.max_lifetime; ++step) {
    int ix = static_cast<int>(x);
    int iy = static_cast<int>(y);
    glm::vec2 gradient = map.GradientAt(x, y);
    float old_height = map.HeightAt(x, y);

    dir_x = dir_x * p.inertia - gradient.x * (1.0f - p.inertia);
    dir_y = dir_y * p.inertia - gradient.y * (1.0f - p.inertia);
    float length = std::sqrt(dir_x * dir_x + dir_y * dir_y);
    if (length < 1e-6f) break;
    dir_x /= length;
    dir_y /= length;

    x += dir_x;
    y += dir_y;
    if (x < 1 || x >= map.width - 2 || y < 1 || y >= map.height - 2) break;

    float new_height = map.HeightAt(x, y);
    float delta = new_height - old_height;

    float capacity = std::max(-delta * speed * water * p.capacity_factor, p.min_capacity);
    if (sediment > capacity || delta > 0.0f) {
      float deposit = delta > 0.0f ? std::min(delta, sediment)
                                   : (sediment - capacity) * p.deposit_rate;
      sediment -= deposit;
      map.Deposit(ix, iy, deposit);
    } else {
      float erode = std::min((capacity - sediment) * p.erode_rate, -delta);
      sediment += erode;
      map.Erode(ix, iy, erode);
    }

    speed = std::sqrt(std::max(speed * speed + delta * p.gravity, 0.0f));
    water *= 1.0f - p.evaporation;
  }
}
```

| パラメータ | 意味 |
| --- | --- |
| **inertia** | **慣性**。**大きいと真っ直ぐ、小さいと勾配に忠実** |
| **capacity_factor** | **水が運べる土砂の量の係数** |
| **erode_rate / deposit_rate** | **削る・積もらせる速さ** |
| **evaporation** | **蒸発**。**水が減ると運べる量が減る** |
| **max_lifetime** | **水滴が転がる最大の歩数**（30 程度） |
| **水滴の数** | **十万〜数百万**。**多いほど、谷がはっきり** |

**削った・積もらせた量は、周囲のセルに重みを付けて配る**（**半径 3 程度のブラシ**）と、**滑らかな谷**になります。

### 結果

| 変化 | 内容 |
| --- | --- |
| **谷の網目** | **水が集まる所に深い谷**ができ、**支流が合流する** |
| **尾根の鋭さ** | **谷に挟まれた尾根が鋭くなる** |
| **扇状地・堆積** | **谷の出口に土砂が平らに積もる** |
| **地面の種類のヒント** | **堆積した所は土、削れた所は岩**（**スプラット マップに使える**） |

## よくあるミス

??? failure "侵食後も、地形が不自然に滑らか"
    **水滴の数・反復**を**増やす**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **水が削り、運ぶ様子をシミュレート**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [地形の生成](index.md)
- [川と湖](rivers.md)
