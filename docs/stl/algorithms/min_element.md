---
title: std::ranges::min_element
summary: "範囲の中で、最小の要素の「位置（イテレータ）」を返す。"
order: 27
tags:
  - アルゴリズム
---

# std::ranges::min_element

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

いちばん近い敵をターゲットにする、体力が最も少ない仲間を回復する。最小値そのものではなく、「どの要素が最小か」を知りたい場面は、ゲームに頻出です。`std::ranges::min(v)` は値のコピーを返すだけです。`min_element` は、最小の要素の位置（イテレーター）を返すので、見つけた要素を書き換えたり、添え字を求めたりできます。

!!! tip "ポイント"
    - 「一番近い敵」「一番 HP の低い仲間」のように、<strong>見つけて何かする</strong>ときに使う。
    - メンバで比べるならプロジェクション: `std::ranges::min_element(enemies, {}, &Enemy::distance)`。
    - 空の範囲だと `end()` が返る。**必ず `end()` と比べてから使う**。
    - 同じ値が複数あると、**最初の**ものを返す。

!!! info "このページを読む前に"
    [`std::ranges::min`](min.md) は最小の値を返します。位置が欲しいときは、このページの `min_element` を使います。

## 関数の詳しい説明

### std::ranges::min_element {#min_element}

```cpp
template <forward_range R, class Proj = identity, class Comp = ranges::less>
constexpr borrowed_iterator_t<R> min_element(R&& r, Comp comp = {}, Proj proj = {});
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `r` | 範囲 | 調べる範囲 | 省略不可 |
| `comp` | 比較関数 | 大小の決め方 | `<` |
| `proj` | プロジェクション | 比べる前の変換 | そのまま |

- 戻り値: 最小の要素のイテレータ。同じ値が複数なら最初のもの。**空なら `end()`**
- 計算量: O(n)

<div class="anim" data-label="std::ranges::min_element(v)">
4 2 7 1 5 # v
*4 2 7 1 5 # 最小の候補は 4
4 *2 7 1 5 # 2 が小さいので候補が変わる
4 2 7 *1 5 # 1 がさらに小さい
4 2 7 *1 5 # 最後まで見て、1 の位置を返す
</div>

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> times = {52, 47, 61, 47};
  auto it = std::ranges::min_element(times);
  std::println("ベストタイム {} は {} 回目", *it, it - times.begin() + 1);
}
```

```text title="実行結果"
ベストタイム 47 は 2 回目
```


## よくある使い方

### 一番近い敵をターゲットにする

```cpp
#include <algorithm>
#include <print>
#include <string>
#include <vector>

struct Enemy {
  std::string name;
  float distance;
  int hp;
};

int main() {
  std::vector<Enemy> enemies = {
      {"スライム", 8.0f, 10}, {"ゴブリン", 2.5f, 30}, {"コウモリ", 5.0f, 5}};

  auto nearest = std::ranges::min_element(enemies, {}, &Enemy::distance);
  if (nearest != enemies.end()) {
    nearest->hp -= 20;  // 見つけた敵を直接書き換える
    std::println("{} に攻撃。残り HP {}", nearest->name, nearest->hp);
  }
}
```

```text title="実行結果"
ゴブリン に攻撃。残り HP 10
```

## フラグ・オプション

| 引数 | 重要度 | 渡すもの | 意味 |
| --- | --- | --- | --- |
| `proj` | <span class="rank rank-must">必須</span> | `&Type::member` | メンバで比べる |
| `proj` | <span class="rank rank-sometimes">たまに</span> | ラムダ式 | 計算した値（距離の 2 乗など）で比べる |
| `comp` | <span class="rank rank-rare">知ってるだけ</span> | `std::greater{}` | 大小を逆にする |

## ゲームでの使いどころ

最も近い敵を探す処理が代表例です。`std::ranges::min_element(enemies, {}, &Enemy::distance)` と書くと、距離のメンバが最小の敵の位置が得られます。距離を毎フレーム更新しておくか、比較用のラムダ式の中で 2 乗の距離を計算します。

回復の対象選びにも使います。HP の割合が最も低い仲間を探して、その仲間に回復魔法を使います。

全要素を並べ替える `sort` と比べると、最小の 1 つだけが欲しいときは `min_element` が O(n) で、速くなります。

## パフォーマンス

- 全要素を 1 回なめる O(n) です。
- 距離で比べるときは、`std::sqrt` を使わずに**距離の 2 乗**で比べると速くなります（大小関係は同じです）。

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| 空の範囲の結果（`end()`）を `*` / `->` で読む | 未定義動作 |

## よくあるミス

??? failure "空の範囲で、`end()` を逆参照する"
    空の `vector` に `min_element` を呼ぶと `end()` が返ります。`*it` で参照すると未定義動作なので、`if (it != v.end())` と確かめてから使います。

??? failure "比較用のラムダ式の中で、重い計算を毎回する"
    `min_element` は、比較のたびにラムダ式を呼びます。ラムダ式の中で距離を `sqrt` で求めると、要素数に比例して重くなります。2 乗の距離で比べる、または計算済みの値を持っておきます。

??? failure "同じ値が複数あるときの結果を勘違いする"
    最小の値が複数あるとき、最初のものが返ります。2 番目以降が欲しいなら、結果の次から範囲を狭めて、もう一度探します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`max_element`](max_element.md) | 最大の要素の位置 |
| [`std::ranges::min`](min.md) | 最小の値のコピー |
| [`sort`](sort.md) | 全体を並べる。最小 1 つなら `min_element` のほうが速い |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 最小の要素の位置が欲しいなら `min_element`、値だけなら `ranges::min`。
    - [x] 空の範囲では `end()`。使う前に必ず比べる。
    - [x] 比較のラムダ式は軽くする。

## 関連ページ

- [cpprefjp: std::ranges::min_element](https://cpprefjp.github.io/reference/algorithm/ranges_min_element.html)
- [cppreference: std::ranges::min_element](https://en.cppreference.com/w/cpp/algorithm/ranges/min_element)
