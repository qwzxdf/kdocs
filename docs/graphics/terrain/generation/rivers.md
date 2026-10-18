---
title: Rivers and Lakes
tags:
  - 描画
---

# Rivers and Lakes

<strong>川は、高い所から低い所へ流れ、谷に沿います</strong>。<strong>侵食の結果から、流れの量を求めて、川を決められます</strong>。このページでは、川と湖の生成を説明します。

!!! tip "ポイント"
    - 流れの量（フロー アキュムレーション）を計算する。
    - 流量が多い所を、川にする。
    - くぼ地に水がたまり、湖になる。
    - 川の水面は、[Water](../../water/index.md)で描く。

## 川と湖
<strong>侵食の結果から、川を取り出せます</strong>。

| 方法 | 内容 |
| --- | --- |
| 流量マップ | 各セルについて、上流から集まる水量を数える（高い所から低い所へ累積）。水量が多い所が川 |
| スプライン化 | 川の経路を折れ線／スプラインに抽出し、水面メッシュを沿わせる |
| 窪地の処理 | 行き止まり（窪み）は、湖にするか、堤を越えて流す |
| 幅と深さ | 水量に比例して川幅を広げる |

<strong>川の水面</strong>は、[Water](../../water/index.md)の<strong>フローマップ</strong>（[水面のインタラクション](../../water/interaction/index.md)）で流れを表現します。

## 川を作る、2 つの考え方

| 方式 | 順番 | 特徴 |
| --- | --- | --- |
| 地形から、川を求める | ① 地形を作る → ② 水の流れを、シミュレーションして、川の位置を決める | 簡単。川が、地形に、必ず合う。ただし、湖や、複雑な水系は、調整が必要 |
| 川から、地形を作る | ① 川の網（ネットワーク）を作る → ② 川に沿って、地形を、作る | 川の形を、制御できる。川が、必ず、海へつながる |

ここでは、<strong>まず作りやすい、地形から求める方法</strong>を、中心に説明します。<strong>川から地形を作る方法</strong>は、Génevaux ら（2013）が、体系的に整理しています。

## 地形から、川を求める

### ① 水が、どこへ流れるか

高さマップの、各画素に、「<strong>どの隣へ流れるか</strong>」を決めます。最も単純なのは、<strong>8 つの隣のうち、いちばん低い隣へ流れる</strong>方法です（D8 法）。

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

水が、<strong>周りより低い窪地</strong>に、たどり着くと、そこで、止まります。実際の地形では、窪地は、<strong>水が満たされた湖</strong>です。そのまま続けると、流れが、途切れてしまうので、窪地を、溢れる高さまで埋めて、流れを、海へつなげます。

窪地を、効率的に埋めるアルゴリズムが、<strong>Priority-Flood</strong>（Barnes ら、2014）です。<strong>外側（海、地形の縁）から、低い順に処理して、窪地を埋める</strong>方法です。

```cpp
// Priority-Flood（簡略版）: 縁から、低い順に、内側へ広げながら、窪地を埋める。
struct Cell { float height; int x, y; };
struct Greater { bool operator()(const Cell& a, const Cell& b) const { return a.height > b.height; } };

void FillDepressions(HeightMap& h) {
  std::priority_queue<Cell, std::vector<Cell>, Greater> open;
  Grid<bool> closed(h.width, h.height, false);
  // 縁のセルを、すべて、開始点として入れる
  for (const auto& [x, y] : h.BorderCells()) {
    open.push({h.At(x, y), x, y});
    closed.At(x, y) = true;
  }
  while (!open.empty()) {
    const Cell c = open.top();
    open.pop();
    for (int dy = -1; dy <= 1; ++dy) {
      for (int dx = -1; dx <= 1; ++dx) {
        const int nx = c.x + dx, ny = c.y + dy;
        if (!h.InBounds(nx, ny) || closed.At(nx, ny)) continue;
        closed.At(nx, ny) = true;
        // 隣が、いまの水位より低ければ、水位まで持ち上げる（窪地を埋める）
        h.At(nx, ny) = std::max(h.At(nx, ny), c.height);
        open.push({h.At(nx, ny), nx, ny});
      }
    }
  }
}
```

実際には、埋めた量が、<strong>湖の深さ</strong>になるので、湖の水面の高さとして、保存しておきます。

### ③ 流量を数える（フロー アキュムレーション）

各画素が、<strong>上流から、いくつの画素の水を、受けているか</strong>を数えます。これを「流量（flow accumulation）」と呼びます。

```cpp
// 上流から下流へ、水を流して、流量を数える。
// 高い順に処理する（上流を先に処理すれば、下流に、足し込める）。
std::vector<int> order = SortCellsByHeightDescending(h);
Grid<float> flow(h.width, h.height, 1.0f);       // 各セルに、最初に、雨 1 を置く
for (int idx : order) {
  const auto [x, y] = ToXY(idx);
  const FlowDir d = dir.At(x, y);
  if (d.dx == 0 && d.dy == 0) continue;           // 流れ先が、ないセル（海、縁）
  flow.At(x + d.dx, y + d.dy) += flow.At(x, y);    // 自分の水を、下流に足す
}
```

### ④ しきい値で、川を決める

流量が、<strong>あるしきい値を超えたセル</strong>を、川とします。

| しきい値 | 結果 |
| --- | --- |
| 小さい | 小川が、たくさん。地形全体が、枝分かれした水系 |
| 大きい | 主要な川だけ |

流量が、<strong>大きいほど、川幅を広くする</strong>と、自然な水系になります。

```text
川幅 = k × (流量)^0.5      （流量が 4 倍で、川幅は 2 倍。実際の川の関係に近い）
```

## 川を、地形に刻む

求めた川の位置に、<strong>地形を削って</strong>、谷（川床）を作ります。

```hlsl
// 川に近い場所を、掘り下げる。
// river_dist は、最も近い川までの距離、river_width は、その川の幅。
float carve = smoothstep(river_width * 1.5, river_width * 0.5, river_dist);
float depth = river_depth * carve;
height -= depth;
```

| 工夫 | 内容 |
| --- | --- |
| 川底の勾配 | 川は、上流から下流へ、必ず、下る。川底を、緩やかに下る曲線に、整える（途中で、上り坂に、ならない） |
| 川の両岸 | 土手を、緩やかに、持ち上げる（滑らかな、マスク） |
| 川の水面 | 川床の高さ + 少し、の位置に、水面のメッシュを置く（[Water](../../water/index.md)） |

### 川の水面を作る

川の、水面のメッシュは、<strong>川の経路に沿った、リボン（帯）状のメッシュ</strong>で、作ります。

| 項目 | 内容 |
| --- | --- |
| 経路 | フローの、画素の列を、なめらかなスプラインに変換する |
| メッシュ | スプラインに沿って、幅と、高さを持つ、帯を作る |
| 流れ | 川の向きを、フロー マップとして、描く（[Flow Maps](../../water/interaction/flow-map.md)） |
| 水面の高さ | 川底の高さ + 水深。下流に向かって、必ず下がる |

## 湖

窪地を埋めたとき、<strong>水位が、埋めた高さ</strong>になります。その、<strong>平らな水面</strong>を、湖の水面とします。

| 項目 | 内容 |
| --- | --- |
| 水面の高さ | 窪地を埋めた、最終的な、高さ |
| 水深 | 埋めた量（水面の高さ − 元の高さ） |
| 岸 | 水深が 0 に、近づく場所が、岸（[Shore Foam](../../water/shore-foam/index.md)） |
| 出口 | 湖の最も低い縁が、川の、始まりになる |

## 川から、地形を作る方法（概要）

Génevaux ら（2013）の方式は、順序を逆にします。

| 段階 | 内容 |
| --- | --- |
| ① 川のグラフ | 河口から、上流へ向かって、木構造として、川の枝を、決める。川の流量（太さ）は、枝分かれで、決まる |
| ② 高さの制約 | 川の高さを、河口から、上流へ向かって、必ず上がるように、決める |
| ③ 地形の生成 | 川の高さを、制約として、その間を、ノイズで、埋める |

利点は、<strong>川が、必ず、河口につながる</strong>ことと、<strong>アーティストが、川の位置を、指定できる</strong>ことです。ただし、実装が、複雑です。

## よくあるミス

??? failure "川が、坂を登っている"
    <strong>水面の高さを、下流ほど低く</strong>する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 流量から川を、くぼ地から湖を決める

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
