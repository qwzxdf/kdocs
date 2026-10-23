---
title: Placement Generation
tags:
  - 描画
---

# Placement Generation

<strong>木・岩・草の配置もルールから自動で生成</strong>できます。高さ・傾き・湿度などの条件から、密度を決めて散布します。このページでは配置の生成を説明します。

!!! tip "ポイント"
    - 条件（高さ・傾き・水辺）から、密度マップを作る。
    - ブルー ノイズで、均等に散布する。
    - シード値で決定的にする。
    - 手動の配置と併用する。

!!! info "このページを読む前に"
    - [Terrain Generation](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 配置の生成
<strong>地形の上に何を置くかも手続き的に決められます</strong>。

| 要素 | 内容 |
| --- | --- |
| 植生 | 高さ・傾き・湿度・ノイズから密度を決める（[Vegetation](../vegetation/index.md)） |
| 岩 | 傾きが急な所／侵食で削れた所 |
| 道 | 2 点間の最小コスト経路（A\*）。傾きが緩い所を通る |
| 集落 | 平らで水に近い所 |
| ポアソン円盤サンプリング | 点が近づきすぎない、自然な散らばり |

## 配置の 3 つの問題

木・岩・草を地形の上に置くとき、次の 3 つを解く必要があります。

| 問題 | 内容 |
| --- | --- |
| ① どこに置くか（密度） | 条件（高さ傾き、湿度）から場所ごとの置く確率を決める |
| ② どう散らすか（分布） | 点が、かたまらず自然にばらけるようにする |
| ③ 同じ結果にする（決定性） | 何度、生成しても同じ位置に置く。セーブ データとネットワークで、位置が食い違わないように |

## ① 密度マップ

条件から <strong>0〜1 の密度</strong>を、地形全体に計算します。

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
| 傾き | 急斜面は木が生えない（岩だけ） |
| 湿度・水からの距離 | 川の近くは植物が、多い |
| 低周波のノイズ | 森の、かたまりと空き地を作る |
| 手描きのマスク | アーティストが、「ここには置かない」を塗る |
| 道・建物 | 道や建物の周りは、密度を 0 にする |

## ② 点をどう散らすか

### 悪い例：一様乱数

座標を <strong>一様な乱数</strong>で決めると点が、かたまったり空いたりします。木が一直線やダマに並びます。

### 良い例 1：ジッタード グリッド

地形を格子に分けて 各セルに、1 つずつ点を置き、セルの中の位置を乱数でずらします。簡単で速く、点の間隔がある程度、そろいます。

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

どの 2 点も最小距離 r 以上、離れているように点を置きます（ポアソン円盤分布）。ブルー ノイズに近く 自然な散らばりです。Bridson（2007）の方法が、O(n) で速く広く使われています。

```cpp
// Bridson のポアソン円盤サンプリング（2D、簡略版）。
std::vector<float2> PoissonDisk(float width, float height, float r, int k, uint32_t seed) {
  const float cell = r / std::sqrt(2.0f);            // 1 セルに、点は最大 1 つしか入らない
  Grid<int> grid(int(width / cell) + 1, int(height / cell) + 1, -1);
  std::vector<float2> points, active;
  Rng rng(seed);
```

準備です。格子の 1 セルの大きさを `r / √2` にすると、セルの対角線が `r` になるので、1 つのセルには点が高々 1 つしか、入りません。格子には点の番号を入れ空は `−1` にします。これで「近くに点があるか」を、周りの数セルを見るだけで判定できます。

```cpp
  auto add = [&](float2 p) {
    grid.At(int(p.x / cell), int(p.y / cell)) = int(points.size());
    points.push_back(p);
    active.push_back(p);
  };
  add({rng.Uniform(0, width), rng.Uniform(0, height)});
```

点を追加する関数と最初の 1 点です。追加した点は格子と点の一覧と、「活動中」の一覧に入れます。

```cpp
  while (!active.empty()) {
    const int i = rng.Index(active.size());
    bool found = false;
```

活動中の点を 1 つランダムに、選びます。この点の周りに新しい点を置けるか、試していきます。

```cpp
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
```

半径 `r` から `2r` の環の中に候補を、`k` 回（30 回が標準）、作り盤面の中で周りの点と `r` 以上、離れていれば採用します。近くを調べるのは周りの 5×5 セルで、十分です。

```cpp
    if (!found) active.erase(active.begin() + i);      // 置けなくなった点は、外す
  }
  return points;
}
```

### 密度に合わせて半径を変える

密度が高い所は半径 r を小さく、低い所は大きくします。場所ごとに半径が変わるポアソン円盤です。簡単な方法は 最も細かい半径で点を、密に作り、密度に応じて間引くことです。

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
| ジッタード グリッド | まずまず | 速い（並列化が簡単） | セルの境目の点が、近づくことがある |
| ポアソン円盤 | 自然 | やや遅い（順序が、必要） | GPU での並列化が、難しい |
| ブルー ノイズ テクスチャ | 自然 | 速い（テクスチャを引くだけ） | 密度の閾値で、間引くとブルー ノイズが保たれる |

Lagae と Dutré（2008）は、ポアソン円盤を作るさまざまな方法を、比較しています。

## ③ 決定性（同じ結果にする）

配置が <strong>生成のたびに変わる</strong>と、セーブ後に木の位置が変わり消した木が、元に戻ります。位置を座標から決定的に決めるようにします。

| 方法 | 内容 |
| --- | --- |
| 座標から乱数の種を作る | `seed = Hash(cell_x, cell_y, world_seed)`。同じセルは必ず同じ点 |
| 乱数を共有しない | 「全体で、1 つの乱数列を順に消費する」と、生成順が変わると結果も変わる。セルごとに独立した乱数を使う |
| 変更は差分で保存 | 「このセルの、3 番目の木を伐採した」だけを、保存する。木の位置自体は保存しない |

```hlsl
// セルの座標と、全体の種から、決定的な乱数を作る（PCG ハッシュ）。
float Random01(int2 cell, uint world_seed, uint channel) {
  uint h = Pcg(cell.x + Pcg(cell.y + Pcg(world_seed + channel)));
  return (h & 0xffffffu) / 16777216.0;
}
```

## 実行時の配置（GPU で生成する）

近年の大規模なゲームでは <strong>配置を、実行時に GPU の計算シェーダーで、生成</strong>します。van Muijden（2017）は、Horizon Zero Dawn で、プレイヤーの周りに 木・岩・草を、リアルタイムに配置する仕組みを、発表しています。

| 項目 | 内容 |
| --- | --- |
| 入力 | 高さ傾き植生マスク、道のマスクなど地形の属性マップ |
| 処理 | 計算シェーダーが、各セルで決定的に点の位置と種類、サイズ、回転を計算する |
| 出力 | インスタンス バッファ（位置、回転、スケール）。そのまま描画に使う |
| 利点 | ディスクに配置データを、持たなくてよい。地形を編集すると配置が自動で更新される |
| 注意 | 毎フレームでなく、カメラが動いた分の新しい範囲だけ、生成する（タイルのキャッシュ） |

生成した点を描画へつなぐ方法は、[Instancing](../vegetation/instancing.md) と [Vegetation Culling](../vegetation/culling.md) を見てください。

## 配置の優先度と除外

複数の種類（木、低木、草、岩）を重ならないように置くとき、<strong>大きいものから先に置きます</strong>。

| 順 | 種類 | 理由 |
| --- | --- | --- |
| 1 | 岩・大木 | 大きく、数が少ない。先に置いて場所を確保 |
| 2 | 低木・小さい木 | 大きな物の周りを、避けて置く |
| 3 | 草・花 | 残った場所に密に、置く |

| 除外する場所 | 内容 |
| --- | --- |
| 道・建物の敷地 | 密度マップで、0 にする |
| 先に置いた物の周り | 半径 r の中には、置かない（ポアソン円盤の最小距離を、種類ごとに変える） |
| 水の中 | 水位より低い場所 |

## よくあるミス

??? failure "木が、一直線や固まりで並ぶ"
    <strong>ブルー ノイズ</strong>で散布する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 条件で密度を決めて散布

## 参考

- Bridson, "Fast Poisson Disk Sampling in Arbitrary Dimensions", SIGGRAPH 2007 Sketches
- Lagae, Dutré, "A Comparison of Methods for Generating Poisson Disk Distributions", Computer Graphics Forum, Vol. 27, No. 1, 2008
- van Muijden, "GPU-Based Run-Time Procedural Placement in Horizon Zero Dawn", Game Developers Conference 2017
- Jarzynski, Olano, "Hash Functions for GPU Rendering", Journal of Computer Graphics Techniques, Vol. 9, No. 3, 2020
- Cook, "Stochastic Sampling in Computer Graphics", ACM Transactions on Graphics, Vol. 5, No. 1, 1986（ジッタード サンプリングと、ブルー ノイズ的な分布）

## 関連ページ

- [Terrain Generation](index.md)
- [Vegetation](../vegetation/index.md)
