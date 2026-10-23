---
title: アルゴリズムとデータ構造
tags:
  - 最適化
---

# アルゴリズムとデータ構造

最適化で、**一番効果が大きい**のが、アルゴリズム（処理のやり方）とデータ構造の見直しです。ほかの最適化（キャッシュ、SIMD など）は、同じ処理を数倍速くしますが、アルゴリズムを変えると、処理の回数そのものが桁違いに減ることがあります。たとえば、敵が 1000 体いて、全員と全員の当たり判定を取ると 100 万回（1000 × 1000）ですが、近くの敵だけを調べるようにすれば、数千回で済みます。これを、計算量（データが増えたとき、処理がどれだけ増えるか）で考えます（[計算量（基礎）](../basics/big-o.md)）。

!!! tip "ポイント"
    - まず<strong>計算量</strong>を見る。<strong>O(n²) になっている所</strong>が、最初の候補。
    - 「全員 × 全員」「ループの中の検索」「ループの中の erase」が、典型的な遅さの原因。
    - 当たり判定は空間分割（グリッド・四分木）で、近いものだけ調べる。
    - 同じ計算を何度もしているなら、結果を覚える（キャッシュ・ダーティ フラグ）。
    - データ構造は、実際のデータ量で選ぶ。要素が少ないうちは、`vector` の線形探索が、速いことも多い。

## 計算量で、遅さを見つける

| 計算量 | n = 1,000 のとき | n = 10,000 のとき | 例 |
| --- | --- | --- | --- |
| [O(1)](../basics/big-o.md#o1) | 1 回 | 1 回 | `v[i]`、`unordered_map` の検索 |
| [O(log n)](../basics/big-o.md#ologn) | 約 10 回 | 約 13 回 | `map` の検索、二分探索 |
| [O(n)](../basics/big-o.md#on) | 1,000 回 | 10,000 回 | 全員を 1 回ずつ見る |
| [O(n log n)](../basics/big-o.md#onlogn) | 約 1 万回 | 約 13 万回 | `sort` |
| [O(n²)](../basics/big-o.md#on2) | **100 万回** | 1 億回 | 全員 × 全員 |

敵が 10 倍に増えると、O(n) は 10 倍、O(n²) は 100 倍遅くなります。ゲームが大きくなってから「急に重くなった」の原因は、ほぼ O(n²) です。

## よくある遅さと直し方

### 1. 全員 × 全員の当たり判定

```cpp
// 遅い：O(n²)。1000 体で 100 万回の判定
for (auto& a : enemies) {
  for (auto& b : enemies) {
    if (Overlaps(a, b)) { /* ... */ }
  }
}
```

**空間分割**で、近くにいるものだけを調べます。

| 方法 | 説明 | 向いている場面 |
| --- | --- | --- |
| グリッド（均等な格子） | 世界を格子に区切り、同じマスと隣のマスの敵だけ判定する | 敵の大きさが同じくらい。一番簡単で速い |
| 四分木 / 八分木 | 空間を、どんどん 4（8）分割していく | 密度に偏りがある（一部に集中） |
| BVH（境界ボリューム階層） | 近いものを箱でまとめて、木にする | 3D の静的な地形、レイキャスト |
| ソート & スイープ | 1 つの軸で並べて、重なるものだけ見る | 1 次元に近い配置 |

<div class="anim" data-label="グリッド：同じマスの相手だけ調べる">
A B C D E F G H # 敵が 8 体。総当たりなら 8 × 7 の組み合わせ
*A *B C D E F G H # マス 1：A と B だけを比べる
A B *C *D E F G H # マス 2：C と D だけを比べる
A B C D *E *F *G *H # マス 3：E、F、G、H だけを比べる
</div>

### 2. ループの中で、毎回検索する

```cpp
// 遅い：O(n × m)
for (const Item& want : wishlist) {
  auto it = std::ranges::find(inventory, want.id, &Item::id);  // 毎回、全体を探す
}

// 速い：先に、検索しやすい形にする。O(n + m)
std::unordered_set<int> owned;
for (const Item& item : inventory) {
  owned.insert(item.id);
}
for (const Item& want : wishlist) {
  bool has = owned.contains(want.id);                            // O(1)
}
```

### 3. ループの中で、毎回 erase する

```cpp
// 遅い：erase のたびに、後ろの要素がずれる。O(n²)
for (std::size_t i = 0; i < bullets.size();) {
  if (bullets[i].dead) {
    bullets.erase(bullets.begin() + i);
  } else {
    ++i;
  }
}

// 速い：1 回のパスで、まとめて消す。O(n)
std::erase_if(bullets, [](const Bullet& b) { return b.dead; });
```

順番がどうでもいいなら、「最後の要素と入れ替えて `pop_back`」も使えます（[erase_if](../stl/algorithms/erase_if.md)）。

### 4. 毎フレーム、全体を sort する

| 状況 | 直し方 |
| --- | --- |
| 描画順のために、毎フレーム全オブジェクトを `sort` | 変わったものだけ位置を直す。ほぼ整列済みなら、挿入ソート |
| 「一番近い敵」だけが欲しい | `sort` ではなく、`min_element`（O(n)）や `nth_element` |
| 上位 10 個だけ欲しい | `partial_sort`、または `priority_queue`（[partial_sort](../stl/algorithms/partial_sort.md)） |

### 5. 同じ計算を、毎フレーム繰り返す {#dirty}

結果が変わらないのに、毎フレーム計算していないか見直します。

| 方法 | 説明 |
| --- | --- |
| ダーティ フラグ | 変わったときだけ「再計算が必要」の印を付け、使うときに再計算する |
| キャッシュ | 計算結果を覚えておく（`unordered_map`）。同じ入力なら、再計算しない |
| コンパイル時に計算 | 定数は `constexpr` に。実行時の計算がなくなる |
| 更新頻度を下げる | 全員を毎フレーム更新せず、数フレームに 1 回（AI の判断など） |

```cpp
class Transform {
 public:
  void SetPosition(Vec3 p) { position_ = p; dirty_ = true; }   // 変わったら、印だけ付ける
  const Mat4& WorldMatrix() {
    if (dirty_) {                                              // 必要になったときだけ再計算
      world_ = ComputeMatrix(position_, rotation_, scale_);
      dirty_ = false;
    }
    return world_;
  }

 private:
  Vec3 position_; Quat rotation_; Vec3 scale_;
  Mat4 world_;
  bool dirty_ = true;
};
```

### 6. 文字列で比較・検索する

| 遅い | 速い |
| --- | --- |
| 毎フレーム `if (name == "player")` | `enum` や整数 ID で比べる |
| `std::map<std::string, T>` を毎フレーム引く | 起動時に、ID（整数）や[ハンドル](../engine/handle.md)に変換しておく |
| 文字列のハッシュを毎回計算 | コンパイル時のハッシュ（[std::hash](../stl/utilities/hash.md)） |

## データ構造を選ぶ

| やりたいこと | 第一候補 | 理由 |
| --- | --- | --- |
| 順に全部処理する | **`std::vector`** | 連続していて、速い（[メモリとキャッシュ](memory-cache.md)） |
| キーで引く（数が多い） | `std::unordered_map` | 平均 O(1)（[unordered_map](../stl/containers/unordered_map.md)） |
| キーで引く（数が少ない・整列したい） | `std::map`、または 整列済みの `vector` + 二分探索 | 小さいうちは、`vector` が速いことも多い |
| 重複なしの集合 | `std::unordered_set`、少なければ整列済み `vector` | |
| 先頭への追加・削除 | `std::deque`（`list` は避ける） | `list` は、要素がバラバラで遅い |
| 優先度の順に取り出す | `std::priority_queue` | O(log n) |
| ビット単位のフラグ | `std::bitset`、ビット演算 | 小さく、速い |

### 小さいデータでは、単純な方が速い

| 要素数 | 検索の目安 |
| --- | --- |
| 〜10 個程度 | `vector` の線形探索が、`unordered_map` より速いことも多い（ハッシュ計算とメモリのジャンプがないため） |
| 〜数百 | 整列済み `vector` + 二分探索、`flat_map` |
| 数千以上 | `unordered_map` |

計算量（O 記法）は、データが大きいときの話です。小さいデータでは、定数倍（1 回の重さ）が効きます。実際のデータ量で、ベンチマークで確かめます（[計測](measure.md)）。

## ゲームでの使いどころ

| 場面 | 直し方 |
| --- | --- |
| 敵が増えると、急に重くなる | 当たり判定・視界チェックを、空間分割に |
| 弾が増えると重い | `erase_if`、オブジェクトプール、描画のバッチ |
| AI の経路探索が重い | A* のキャッシュ、更新を数フレームに 1 回に、経路を共有 |
| UI のレイアウトが重い | 変わったときだけ再計算（ダーティ フラグ） |
| アセットの検索が遅い | 名前 → ID の変換を、起動時に 1 回 |
| 毎フレームの全体ソート | 変更部分だけ。または整列済みを保つ |

## よくあるミス

??? failure "計算量が同じ O(n) でも、定数倍の違いを無視する"
    O(n) どうしでも、メモリが連続している `vector` と、バラバラの `list` では、何倍も違います。計算量が同じなら、[メモリの並び](memory-cache.md)で比べます。

??? failure "小さいデータなのに、複雑なデータ構造を使う"
    10 個の要素のために `unordered_map` を使うと、ハッシュの計算とメモリ確保で、`vector` の線形探索より遅くなります。

??? failure "空間分割を、毎フレーム作り直す"
    構築のコストが、節約分を上回ることがあります。静止物は、最初に 1 回だけ作り、動くものだけを更新します。

??? failure "キャッシュの無効化を忘れる"
    元のデータが変わったのに、古い結果を使い続けるバグになります。ダーティ フラグを、変更する関数で必ず立てます（setter を通す）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 最初に疑うのは <strong>O(n²)</strong>（全員 × 全員、ループの中の検索・erase）
    - [x] 当たり判定は空間分割。検索は先にハッシュ・ID にする
    - [x] 同じ計算の繰り返しは、ダーティ フラグ・キャッシュで省く
    - [x] 小さなデータでは、単純な `vector` が速い。実際の量でベンチマークする
    - [x] アルゴリズムの改善は、ほかの最適化より桁違いに効く

## 関連ページ

- [最適化の進め方](index.md)
- [計算量（基礎）](../basics/big-o.md)
- [メモリとキャッシュ](memory-cache.md)
- [std::erase_if](../stl/algorithms/erase_if.md)
- [コンテナの選び方](../basics/container-chart.md)
- [std::hash とハッシュ](../stl/utilities/hash.md)
- [std::unordered_map](../stl/containers/unordered_map.md)
- [std::flat_map](../stl/containers/flat_map.md)
- [3D の衝突判定（ブロードフェーズ）](../3d/collision-3d.md)
- [ピッキングとレイキャスト](../3d/picking-raycast.md)
