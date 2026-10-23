---
title: 経路探索（A*）
tags:
  - ゲームエンジン
---

# 経路探索（A*）

敵を主人公へ向かわせるのに、まっすぐ座標を近づけるだけでは、壁にぶつかって止まります。壁を避けて、迷路でも出口までたどりつくには、「マップのどこを通ればゴールに着くか」を調べる必要があります。これが経路探索です。

ゲームで最もよく使われるのは A*（エースター）です。<strong>「ここまでにかかった距離」に「ゴールまでの見積もり」を足した値が小さい場所から、順に調べていく</strong>ので、無駄なく最短の道を見つけられます。

!!! tip "ポイント"
    - マップを、点（ノード）と線（辺）のグラフにして、その上で探す。格子（グリッド）かナビメッシュが定番
    - A* は、実際の距離 g と、ゴールまでの見積もり h の合計 f が小さい順に調べる
    - 見積もりが実際より大きくなければ、最短の経路が保証される。格子では、マンハッタン距離やユークリッド距離を使う
    - 探すたびに重いので、毎フレームではなく、必要なときだけ呼ぶ
    - 3D の立体的なマップは、ナビメッシュ（歩ける面の集まり）を使う。Recast & Detour が自動で作る

!!! info "このページを読む前に"
    - [ゲーム AI](index.md)
    - [priority_queue](../../stl/containers/priority_queue.md)（優先度付きキュー）

## 探索の考え方 {#idea}

最も単純な探索は、スタートから周りへ、同心円状に広げていき、ゴールに着いたら終わり、という幅優先探索です。確実ですが、ゴールと反対の方向も同じように調べるので、無駄が多くなります。

A* は、「ゴールに近そうな場所を先に調べる」ことで、無駄を減らします。各ノードに、次の値を付けます。

- g：スタートから、そのノードまで、実際にかかった距離
- h：そのノードから、ゴールまでの見積もり（ヒューリスティック）
- f = g + h：このノードを通った場合の、全体の距離の見積もり

f が一番小さいノードを取り出して、隣のノードの g と f を更新します。これをゴールに着くまで繰り返します。

## 見積もり h の選び方 {#heuristic}

h は、<strong>実際の距離より大きくしてはいけません</strong>。大きすぎると、最短でない経路が選ばれることがあります。小さすぎる分には、最短は保証されますが、探索が広がり、遅くなります。

| マップ | 動ける方向 | 使う h |
| --- | --- | --- |
| 格子 | 上下左右の 4 方向 | マンハッタン距離 `abs(dx) + abs(dy)` |
| 格子 | 斜めを含む 8 方向 | オクタイル距離、またはユークリッド距離 |
| 自由な空間 | どの方向にも | ユークリッド距離 `sqrt(dx*dx + dy*dy)` |

## 格子マップでの実装 {#grid}

```cpp
#include <algorithm>
#include <cmath>
#include <queue>
#include <vector>

struct Cell {
  int x, y;
};

struct QueueItem {
  float f;        // g + h
  int index;      // 格子上の位置（y * width + x）
  bool operator>(const QueueItem& other) const { return f > other.f; }
};

// 格子上の経路を探す。見つからなければ空
std::vector<Cell> FindPath(const std::vector<char>& walls, int width, int height,
                           Cell start, Cell goal) {
  const int n = width * height;
  std::vector<float> g(n, 1e30f);         // スタートからの実際の距離
  std::vector<int> parent(n, -1);         // 経路をたどるための、1 つ前のノード
  std::priority_queue<QueueItem, std::vector<QueueItem>, std::greater<>> open;

  auto index = [&](Cell c) { return c.y * width + c.x; };
  auto heuristic = [&](Cell c) {
    return static_cast<float>(std::abs(c.x - goal.x) + std::abs(c.y - goal.y));  // マンハッタン距離
  };

  g[index(start)] = 0.0f;
  open.push({heuristic(start), index(start)});

  const int dx[] = {1, -1, 0, 0};
  const int dy[] = {0, 0, 1, -1};

  while (!open.empty()) {
    const QueueItem top = open.top();
    open.pop();
    const Cell current{top.index % width, top.index / width};

    if (current.x == goal.x && current.y == goal.y) {
      // ゴールに着いた。parent をたどってスタートまで戻り、逆順にして返す
      std::vector<Cell> path;
      for (int i = top.index; i != -1; i = parent[i]) path.push_back({i % width, i / width});
      std::reverse(path.begin(), path.end());
      return path;
    }

    for (int d = 0; d < 4; ++d) {
      const Cell next{current.x + dx[d], current.y + dy[d]};
      if (next.x < 0 || next.y < 0 || next.x >= width || next.y >= height) continue;  // 範囲外
      if (walls[index(next)]) continue;                                                // 壁

      const float new_g = g[top.index] + 1.0f;  // 隣への移動は距離 1
      if (new_g < g[index(next)]) {              // より短い経路が見つかったら更新
        g[index(next)] = new_g;
        parent[index(next)] = top.index;
        open.push({new_g + heuristic(next), index(next)});
      }
    }
  }
  return {};  // ゴールに着けなかった
}
```

`open` は、f が小さい順に取り出せる優先度付きキューです。`std::priority_queue` は既定で大きい順なので、`std::greater<>` で小さい順にしています。

`g` は、各マスへの「いまわかっている最短距離」で、最初は無限大に近い値です。新しい経路のほうが短ければ更新して、キューに入れます。同じマスが複数回キューに入ることがありますが、取り出した時点でより良い g が見つかっていれば、結果は変わらないので、この単純な書き方で正しく動きます。

`parent` は、各マスに「どのマスから来たか」を記録します。ゴールに着いたら、そこから `parent` をたどってスタートまで戻り、逆順にすると経路になります。

## 格子の限界とナビメッシュ {#navmesh}

格子は単純ですが、3D の立体的なマップには向きません。広いフィールドを細かい格子にすると、マス数が膨大になり、探索が重くなります。経路も、角ばった動きになります。

ナビメッシュ（Navigation Mesh）は、<strong>歩ける面を、三角形や多角形の集まりで表す</strong>方式です。広い平地は、少数の大きな多角形で表せるので、ノードが少なく、探索が速くなります。経路は、多角形をつなぐ辺の上を、「じょうごアルゴリズム」で引き伸ばして、自然な直線に近い道にします。

ナビメッシュは、手作業で作らず、シーンのメッシュから自動生成します。[Recast & Detour](../../libs/recast/index.md) は、その定番のライブラリです。Recast が生成を、Detour が探索と移動を担当します。

## 経路の追従 {#follow}

経路が得られたら、キャラクターは、点を順にたどります。次の点に近づいたら、次の点を目標にします。点にぴったり着くまで待つと、止まったり、行き過ぎたりするので、「半径内に入ったら次へ」と判定します。

動く障害物（他のキャラクター）を避けるには、経路を引き直すより、局所的な回避（群衆の動き）を併用するほうが安定します。

## よくあるミス {#mistakes}

??? failure "斜めに壁をすり抜ける"
    斜め移動を許す格子で、斜めの両隣が壁の場合も通ってしまっています。斜めに進めるのは、隣り合う 2 マスが両方通れるときだけにします。

??? failure "毎フレーム探索して、ゲームが重い"
    目標が動いたときだけ、または数フレームに 1 回だけ探索します。同時に探索する数に上限を設けます。

??? failure "見積もりが大きすぎて、遠回りな経路が出た"
    h が実際の距離を超えています。h を小さくするか、移動のコストと単位を合わせます。

## これだけ覚える {#summary}

- A* は、g（来た距離）と h（残りの見積もり）の合計が小さい順に探す
- h は、実際の距離を超えない。超えると最短が保証されない
- 3D や広いマップは、ナビメッシュ。Recast & Detour が自動で作る

## 関連ページ

- [ゲーム AI](index.md)
- [ビヘイビア ツリー](behavior-tree.md)
- [Recast & Detour](../../libs/recast/index.md)
