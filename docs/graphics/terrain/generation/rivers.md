---
title: Rivers and Lakes
tags:
  - 描画
---

# Rivers and Lakes

<strong>川は高い所から低い所へ流れ、谷に沿います</strong>。侵食の結果から流れの量を求めて、川を決められます。このページでは川と湖の生成を説明します。

!!! tip "ポイント"
    - 流れの量（フロー アキュムレーション）を計算する。
    - 流量が多い所を川にする。
    - くぼ地に水がたまり、湖になる。
    - 川の水面は[Water](../../water/index.md)で描く。

!!! info "このページを読む前に"
    - [Terrain Generation](index.md)（このセクション全体の地図と、読む順番）

## 川と湖
<strong>侵食の結果から川を取り出せます</strong>。

| 方法 | 内容 |
| --- | --- |
| 流量マップ | 各セルについて、上流から集まる水量を数える（高い所から低い所へ累積）。水量が多い所が川 |
| スプライン化 | 川の経路を折れ線／スプラインに抽出し、水面メッシュを沿わせる |
| 窪地の処理 | 行き止まり（窪み）は、湖にするか堤を越えて流す |
| 幅と深さ | 水量に比例して川幅を広げる |

川の水面は[Water](../../water/index.md)のフローマップ（[水面のインタラクション](../../water/interaction/index.md)）で流れを表現します。

## 川を作る 2 つの考え方

| 方式 | 順番 | 特徴 |
| --- | --- | --- |
| 地形から川を求める | ① 地形を作る → ② 水の流れをシミュレーションして川の位置を決める | 簡単。川が地形に必ず合う。ただし、湖や複雑な水系は調整が必要 |
| 川から地形を作る | ① 川の網（ネットワーク）を作る → ② 川に沿って地形を作る | 川の形を制御できる。川が必ず海へつながる |

ここでは、<strong>まず作りやすい地形から求める方法</strong>を中心に説明します。川から地形を作る方法は Génevaux ら（2013）が体系的に整理しています。

## 地形から川を求める

### ① 水がどこへ流れるか

高さマップの各画素に「<strong>どの隣へ流れるか</strong>」を決めます。最も単純なのは 8 つの隣のうち、いちばん低い隣へ流れる方法です（D8 法）。

```cpp
// D8 法: 各セルについて、最も急に下る隣の方向を求める。
struct FlowDir { int dx, dy; };

FlowDir ComputeFlowDirection(const HeightMap& h, int x, int y) {
  FlowDir best = {0, 0};
  float best_slope = 0.0f;
  for (int dy = -1; dy <= 1; ++dy) {
    for (int dx = -1; dx <= 1; ++dx) {
      if (dx == 0 && dy == 0) continue;
      const float dist = (dx != 0 && dy != 0) ? 1.4142f : 1.0f;     // 斜めは、少し遠い
      const float slope = (h.At(x, y) - h.At(x + dx, y + dy)) / dist;
      if (slope > best_slope) {
        best_slope = slope;
        best = {dx, dy};
      }
    }
  }
  return best;   // {0, 0} なら、周りより低い（窪地）
}
```

### ② 窪地を埋める

水が 周りより低い窪地にたどり着くとそこで、止まります。実際の地形では窪地は 水が満たされた湖です。そのまま続けると流れが途切れてしまうので窪地を溢れる高さまで埋めて流れを海へつなげます。

窪地を手早く埋めるアルゴリズムが Priority-Flood（Barnes ら、2014）です。外側（海、地形の縁）から低い順に処理して、窪地を埋める方法です。

```cpp
// Priority-Flood（簡略版）: 縁から、低い順に内側へ広げながら、窪地を埋める。
struct Cell { float height; int x, y; };
struct Greater { bool operator()(const Cell& a, const Cell& b) const { return a.height > b.height; } };
```

セルの高さと位置をまとめた構造体と高さの、低い順に取り出すための比較関数です。優先度つきキューはこれで最も低いセルを常に先頭に置きます。

```cpp
void FillDepressions(HeightMap& h) {
  std::priority_queue<Cell, std::vector<Cell>, Greater> open;
  Grid<bool> closed(h.width, h.height, false);
  // 縁のセルをすべて、開始点として入れる
  for (const auto& [x, y] : h.BorderCells()) {
    open.push({h.At(x, y), x, y});
    closed.At(x, y) = true;
  }
```

優先度つきキューと「処理済み」の印を用意し、縁のセルをすべて開始点に入れます。縁は水が地形の外へ流れ出せる出口と、みなします。

```cpp
  while (!open.empty()) {
    const Cell c = open.top();
    open.pop();
    for (int dy = -1; dy <= 1; ++dy) {
      for (int dx = -1; dx <= 1; ++dx) {
        const int nx = c.x + dx, ny = c.y + dy;
        if (!h.InBounds(nx, ny) || closed.At(nx, ny)) continue;
        closed.At(nx, ny) = true;
        // 隣がいまの水位より低ければ、水位まで持ち上げる（窪地を埋める）
        h.At(nx, ny) = std::max(h.At(nx, ny), c.height);
        open.push({h.At(nx, ny), nx, ny});
      }
    }
  }
}
```

実際には、埋めた量が 湖の深さになるので、湖の水面の高さとして保存しておきます。

### ③ 流量を数える（フロー アキュムレーション）

各画素が 上流からいくつの画素の水を受けているかを数えます。これを「流量（flow accumulation）」と呼びます。

```cpp
// 上流から下流へ水を流して、流量を数える。
// 高い順に処理する（上流を先に処理すれば、下流に足し込める）。
std::vector<int> order = SortCellsByHeightDescending(h);
Grid<float> flow(h.width, h.height, 1.0f);       // 各セルに最初に、雨 1 を置く
for (int idx : order) {
  const auto [x, y] = ToXY(idx);
  const FlowDir d = dir.At(x, y);
  if (d.dx == 0 && d.dy == 0) continue;           // 流れ先がないセル（海、縁）
  flow.At(x + d.dx, y + d.dy) += flow.At(x, y);    // 自分の水を下流に足す
}
```

### ④ しきい値で川を決める

流量が あるしきい値を超えたセルを川とします。

| しきい値 | 結果 |
| --- | --- |
| 小さい | 小川がたくさん。地形全体が枝分かれした水系 |
| 大きい | 主要な川だけ |

流量が 大きいほど川幅を広くすると、自然な水系になります。

```text
川幅 = k × (流量)^0.5      （流量が 4 倍で、川幅は 2 倍。実際の川の関係に近い）
```

## 川を地形に刻む

求めた川の位置に <strong>地形を削って</strong>、谷（川床）を作ります。

```hlsl
// 川に近い場所を掘り下げる。
// river_dist は、最も近い川までの距離、river_width は、その川の幅。
float carve = smoothstep(river_width * 1.5, river_width * 0.5, river_dist);
float depth = river_depth * carve;
height -= depth;
```

| 工夫 | 内容 |
| --- | --- |
| 川底の勾配 | 川は上流から下流へ必ず下る。川底を緩やかに下る曲線に整える（途中で、上り坂にならない） |
| 川の両岸 | 土手を緩やかに、持ち上げる（滑らかなマスク） |
| 川の水面 | 川床の高さ + 少し、の位置に水面のメッシュを置く（[Water](../../water/index.md)） |

### 川の水面を作る

川の水面のメッシュは 川の経路に沿った、リボン（帯）状のメッシュで、作ります。

| 項目 | 内容 |
| --- | --- |
| 経路 | フローの画素の列をなめらかなスプラインに変換する |
| メッシュ | スプラインに沿って幅と、高さを持つ帯を作る |
| 流れ | 川の向きをフロー マップとして、描く（[Flow Maps](../../water/interaction/flow-map.md)） |
| 水面の高さ | 川底の高さ + 水深。下流に向かって必ず下がる |

## 湖

窪地を埋めたとき <strong>水位が埋めた高さ</strong>になります。その 平らな水面を湖の水面とします。

| 項目 | 内容 |
| --- | --- |
| 水面の高さ | 窪地を埋めた、最終的な高さ |
| 水深 | 埋めた量（水面の高さ − 元の高さ） |
| 岸 | 水深が 0 に近づく場所が岸（[Shore Foam](../../water/shore-foam/index.md)） |
| 出口 | 湖の最も低い縁が川の、始まりになる |

## 川から地形を作る方法（概要）

Génevaux ら（2013）の方式は、順序を逆にします。

| 段階 | 内容 |
| --- | --- |
| ① 川のグラフ | 河口から、上流へ向かって木構造として川の枝を決める。川の流量（太さ）は枝分かれで、決まる |
| ② 高さの制約 | 川の高さを河口から上流へ向かって必ず上がるように、決める |
| ③ 地形の生成 | 川の高さを制約としてその間をノイズで埋める |

利点は <strong>川が必ず河口につながる</strong>ことと、アーティストが川の位置を指定できることです。ただし、実装が複雑です。

## よくあるミス

??? failure "川が坂を登っている"
    <strong>水面の高さを下流ほど低く</strong>する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 流量から川をくぼ地から湖を決める

## 参考

- Génevaux, Galin, Guérin, Peytavie, Beneš, "Terrain Generation Using Procedural Models Based on Hydrology", ACM Transactions on Graphics (SIGGRAPH 2013)
- Barnes, Lehman, Mulla, "Priority-Flood: An Optimal Depression-Filling and Watershed-Labeling Algorithm for Digital Elevation Models", Computers & Geosciences, Vol. 62, 2014
- Galin, Guérin, Peytavie, Cordonnier, Cani, Beneš, Gain, "A Review of Digital Terrain Modeling", Computer Graphics Forum (Eurographics 2019 STAR)
- Kelley, Malin, Nielson, "Terrain Simulation Using a Model of Stream Erosion", SIGGRAPH 1988
- O'Callaghan, Mark, "The Extraction of Drainage Networks from Digital Elevation Data", Computer Vision, Graphics, and Image Processing, Vol. 28, 1984（D8 法の原典）

## 関連ページ

- [Terrain Generation](index.md)
- [Erosion](erosion.md)
- [Water](../../water/index.md)
