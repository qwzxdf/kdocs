---
title: Placement Generation
tags:
  - 描画
---

# Placement Generation

**木・岩・草の配置も、ルールから自動で生成**できます。**高さ・傾き・湿度などの条件から、密度を決めて、散布**します。このページでは、**配置の生成**を説明します。

!!! tip "ポイント"
    - **条件（高さ・傾き・水辺）から、密度マップを作る**。
    - **ブルー ノイズで、均等に散布**する。
    - **シード値で、決定的にする**。
    - **手動の配置と、併用する**。

## 配置の生成
**地形の上に何を置くかも、手続き的に決められます**。

| 要素 | 内容 |
| --- | --- |
| **植生** | **高さ・傾き・湿度・ノイズから密度を決める**（[Vegetation](../vegetation/index.md)） |
| **岩** | **傾きが急な所／侵食で削れた所** |
| **道** | **2 点間の最小コスト経路（A\*）<strong>。</strong>傾きが緩い所を通る** |
| **集落** | **平らで水に近い所** |
| **ポアソン円盤サンプリング** | **点が近づきすぎない、自然な散らばり** |

## 配置の、3 つの問題

木・岩・草を、地形の上に置くとき、次の 3 つを、解く必要があります。

| 問題 | 内容 |
| --- | --- |
| ① どこに置くか（密度） | 条件（高さ、傾き、湿度）から、場所ごとの、**置く確率**を決める |
| ② どう散らすか（分布） | 点が、かたまらず、**自然に、ばらける**ようにする |
| ③ 同じ結果にする（決定性） | **何度、生成しても、同じ位置に**置く。セーブ データと、ネットワークで、位置が食い違わないように |

## ① 密度マップ

条件から、**0〜1 の密度**を、地形全体に、計算します。

```hlsl
// 木の密度: 平らで、湿っていて、高すぎない場所に多い。
float TreeDensity(float3 world_pos, float3 normal, float moisture) {
  float slope = 1.0 - saturate(normal.y);
  float flat_ok = 1.0 - smoothstep(0.15, 0.35, slope);                 // 急斜面には生えない
  float altitude_ok = 1.0 - smoothstep(tree_line - 50.0, tree_line, world_pos.y);  // 森林限界
  float wet = smoothstep(0.2, 0.6, moisture);                          // 乾いた所は、疎ら
  float noise = Fbm(world_pos.xz * 0.01, 3, 2.0, 0.5, 42) * 0.5 + 0.5; // 森のかたまりを作る
  return flat_ok * altitude_ok * wet * noise;
}
```

| 入力 | 内容 |
| --- | --- |
| 高さ | 森林限界、海岸近くの植物 |
| 傾き | 急斜面は、木が生えない（岩だけ） |
| 湿度・水からの距離 | 川の近くは、植物が、多い |
| 低周波のノイズ | 森の、かたまりと、空き地を、作る |
| 手描きのマスク | アーティストが、「ここには置かない」を、塗る |
| 道・建物 | 道や、建物の周りは、密度を 0 にする |

## ② 点を、どう散らすか

### 悪い例：一様乱数

座標を、**一様な乱数**で、決めると、点が、**かたまったり、空いたり**します。木が、一直線や、ダマに、並びます。

### 良い例 1：ジッタード グリッド

地形を、格子に分けて、**各セルに、1 つずつ点を、置き**、セルの中の位置を、乱数で、ずらします。**簡単で、速く**、点の間隔が、ある程度、そろいます。

```cpp
// ジッタード グリッド: 各セルに 1 つ、ランダムな位置に、点を置く。
for (int cy = 0; cy < cells_y; ++cy) {
  for (int cx = 0; cx < cells_x; ++cx) {
    const uint32_t seed = HashCell(cx, cy, global_seed);        // セル座標から、乱数の種
    const float2 jitter = {Random01(seed), Random01(seed + 1)};
    const float2 p = (float2(cx, cy) + jitter) * cell_size;
    if (Random01(seed + 2) < Density(p)) {                       // 密度で、間引く
      points.push_back(p);
    }
  }
}
```

### 良い例 2：ポアソン円盤サンプリング

**どの 2 点も、最小距離 r 以上、離れている**ように、点を置きます（ポアソン円盤分布）。ブルー ノイズに近く、**自然な散らばり**です。Bridson（2007）の方法が、O(n) で、速く、広く使われています。

```cpp
// Bridson のポアソン円盤サンプリング（2D、簡略版）。
std::vector<float2> PoissonDisk(float width, float height, float r, int k, uint32_t seed) {
  const float cell = r / std::sqrt(2.0f);            // 1 セルに、点は最大 1 つしか入らない
  Grid<int> grid(int(width / cell) + 1, int(height / cell) + 1, -1);
  std::vector<float2> points, active;
  Rng rng(seed);

  auto add = [&](float2 p) {
    grid.At(int(p.x / cell), int(p.y / cell)) = int(points.size());
    points.push_back(p);
    active.push_back(p);
  };
  add({rng.Uniform(0, width), rng.Uniform(0, height)});

  while (!active.empty()) {
    const int i = rng.Index(active.size());
    bool found = false;
    for (int n = 0; n < k; ++n) {                     // k 回（30 回が標準）、候補を試す
      // 半径 r〜2r の環の中から、候補を選ぶ
      const float angle = rng.Uniform(0, 6.2831853f);
      const float dist = rng.Uniform(r, 2 * r);
      const float2 c = active[i] + float2(std::cos(angle), std::sin(angle)) * dist;
      if (c.x < 0 || c.y < 0 || c.x >= width || c.y >= height) continue;
      if (FarEnough(grid, points, c, r, cell)) {      // 周りの 5×5 セルだけを調べれば、十分
        add(c);
        found = true;
        break;
      }
    }
    if (!found) active.erase(active.begin() + i);      // 置けなくなった点は、外す
  }
  return points;
}
```

### 密度に合わせて、半径を変える

密度が高い所は、半径 r を小さく、低い所は、大きくします。**場所ごとに、半径が変わる**ポアソン円盤です。簡単な方法は、**最も細かい半径で、点を、密に作り**、**密度に応じて、間引く**ことです。

```cpp
// 密度で、間引く。点ごとに、決定的な乱数を使う。
for (const float2& p : dense_points) {
  const float d = Density(p);
  if (HashToFloat(p, global_seed) < d) kept.push_back(p);
}
```

### 方法の比較

| 方法 | 見た目 | 速さ | 特徴 |
| --- | --- | --- | --- |
| 一様乱数 | ダマになる | 最速 | 使わない |
| ジッタード グリッド | まずまず | 速い（並列化が簡単） | セルの境目の、点が、近づくことがある |
| ポアソン円盤 | 自然 | やや遅い（順序が、必要） | GPU での並列化が、難しい |
| ブルー ノイズ テクスチャ | 自然 | 速い（テクスチャを引くだけ） | 密度の閾値で、間引くと、ブルー ノイズが、保たれる |

Lagae と Dutré（2008）は、ポアソン円盤を、作る、さまざまな方法を、比較しています。

## ③ 決定性（同じ結果にする）

配置が、**生成のたびに、変わる**と、セーブ後に、木の位置が、変わり、消した木が、元に戻ります。**位置を、座標から、決定的に決める**ようにします。

| 方法 | 内容 |
| --- | --- |
| 座標から、乱数の種を作る | `seed = Hash(cell_x, cell_y, world_seed)`。同じセルは、必ず、同じ点 |
| 乱数を、共有しない | 「全体で、1 つの乱数列を、順に消費する」と、生成順が変わると、結果も変わる。**セルごとに、独立した乱数**を使う |
| 変更は、差分で保存 | 「このセルの、3 番目の木を、伐採した」だけを、保存する。木の位置自体は、保存しない |

```hlsl
// セルの座標と、全体の種から、決定的な乱数を作る（PCG ハッシュ）。
float Random01(int2 cell, uint world_seed, uint channel) {
  uint h = Pcg(cell.x + Pcg(cell.y + Pcg(world_seed + channel)));
  return (h & 0xffffffu) / 16777216.0;
}
```

## 実行時の配置（GPU で生成する）

近年の、大規模なゲームでは、**配置を、実行時に、GPU の計算シェーダーで、生成**します。van Muijden（2017）は、Horizon Zero Dawn で、プレイヤーの周りに、**木・岩・草を、リアルタイムに配置する**仕組みを、発表しています。

| 項目 | 内容 |
| --- | --- |
| 入力 | 高さ、傾き、植生マスク、道のマスクなど、地形の属性マップ |
| 処理 | 計算シェーダーが、各セルで、決定的に、点の位置と、種類、サイズ、回転を計算する |
| 出力 | **インスタンス バッファ**（位置、回転、スケール）。そのまま、描画に使う |
| 利点 | ディスクに、配置データを、持たなくてよい。地形を編集すると、配置が、自動で更新される |
| 注意 | 毎フレームでなく、**カメラが、動いた分の、新しい範囲だけ**、生成する（タイルのキャッシュ） |

生成した点を、描画へつなぐ方法は、[Instancing](../vegetation/instancing.md) と [Vegetation Culling](../vegetation/culling.md) を見てください。

## 配置の、優先度と、除外

複数の種類（木、低木、草、岩）を、重ならないように置くとき、**大きいものから先に、置きます**。

| 順 | 種類 | 理由 |
| --- | --- | --- |
| 1 | 岩・大木 | 大きく、数が少ない。先に置いて、場所を確保 |
| 2 | 低木・小さい木 | 大きな物の周りを、避けて置く |
| 3 | 草・花 | 残った場所に、密に、置く |

| 除外する場所 | 内容 |
| --- | --- |
| 道・建物の敷地 | 密度マップで、0 にする |
| 先に置いた物の周り | 半径 r の中には、置かない（ポアソン円盤の、最小距離を、種類ごとに変える） |
| 水の中 | 水位より、低い場所 |

## よくあるミス

??? failure "木が、一直線や固まりで並ぶ"
    **ブルー ノイズ**で**散布**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **条件で密度を決めて、散布**

## 参考

- Bridson, "Fast Poisson Disk Sampling in Arbitrary Dimensions", SIGGRAPH 2007 Sketches
- Lagae, Dutré, "A Comparison of Methods for Generating Poisson Disk Distributions", Computer Graphics Forum, Vol. 27, No. 1, 2008
- van Muijden, "GPU-Based Run-Time Procedural Placement in Horizon Zero Dawn", Game Developers Conference 2017
- Jarzynski, Olano, "Hash Functions for GPU Rendering", Journal of Computer Graphics Techniques, Vol. 9, No. 3, 2020
- Cook, "Stochastic Sampling in Computer Graphics", ACM Transactions on Graphics, Vol. 5, No. 1, 1986（ジッタード サンプリングと、ブルー ノイズ的な分布）

## 関連ページ

- [Terrain Generation](index.md)
- [Vegetation](../vegetation/index.md)
