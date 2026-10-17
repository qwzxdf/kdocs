---
title: std::ranges::min_element / max_element
tags:
  - アルゴリズム
---

# std::ranges::min_element / max_element

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`min_element` と `max_element` は、**範囲の中で最小・最大の要素の「位置」（イテレータ）を返す**関数です。[`std::ranges::min` / `max`](min_max.md) が「値のコピー」を返すのに対し、こちらは位置を返すので、見つけた要素を書き換えたり、何番目かを調べたりできます。

!!! tip "ポイント"
    - <strong>一番近い敵、一番 HP の低い仲間など、「見つけて何かする」ときに使う。</strong> 値だけ欲しいなら `std::ranges::min` / `max`。
    - メンバで比べるならプロジェクション: `std::ranges::min_element(enemies, {}, &Enemy::distance)`。
    - 空の範囲だと `end()` が返る。**必ず `end()` と比べてから使う**。
    - 同じ値が複数あると、`min_element` も `max_element` も**最初の**ものを返す。

## 関数一覧

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`std::ranges::min_element`](#min_element) | <span class="rank rank-often">よく使う</span> | 最小の要素の位置 | O(n) |
| [`std::ranges::max_element`](#max_element) | <span class="rank rank-often">よく使う</span> | 最大の要素の位置 | O(n) |
| [`std::ranges::minmax_element`](#minmax_element) | <span class="rank rank-rare">知ってるだけ</span> | 両方の位置を一度に | O(n) |

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

### std::ranges::max_element {#max_element}

```cpp
template <forward_range R, class Proj = identity, class Comp = ranges::less>
constexpr borrowed_iterator_t<R> max_element(R&& r, Comp comp = {}, Proj proj = {});
```

- 戻り値: 最大の要素のイテレータ。同じ値が複数なら**最初の**もの。空なら `end()`

<div class="anim" data-label="std::ranges::max_element(v)">
4 2 7 1 5 # v
*4 2 7 1 5 # 最大の候補は 4
4 2 *7 1 5 # 7 が大きいので候補が変わる
4 2 *7 1 5 # 最後まで見て、7 の位置を返す
</div>

```cpp
#include <algorithm>
#include <print>
#include <string>
#include <vector>

struct Member {
  std::string name;
  int aggro;
};

int main() {
  std::vector<Member> party = {{"戦士", 80}, {"魔法使い", 95}, {"僧侶", 40}};
  auto target = std::ranges::max_element(party, {}, &Member::aggro);
  std::println("敵は {} を狙う", target->name);
}
```

```text title="実行結果"
敵は 魔法使い を狙う
```

### std::ranges::minmax_element {#minmax_element}

```cpp
template <forward_range R, class Proj = identity, class Comp = ranges::less>
constexpr minmax_element_result<borrowed_iterator_t<R>> minmax_element(R&& r, Comp comp = {}, Proj proj = {});
```

- 戻り値: `.min` と `.max` を持つ構造体（どちらもイテレータ）。最大は同じ値なら**最後の**もの

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {3, 9, 1, 9};
  auto [lo, hi] = std::ranges::minmax_element(v);
  std::println("最小 {}番目 / 最大 {}番目", lo - v.begin(), hi - v.begin());
}
```

```text title="実行結果"
最小 2番目 / 最大 3番目
```

## フラグ・オプション

| 引数 | 重要度 | 渡すもの | 意味 |
| --- | --- | --- | --- |
| `proj` | <span class="rank rank-must">必須</span> | `&Type::member` | メンバで比べる |
| `proj` | <span class="rank rank-sometimes">たまに</span> | ラムダ式 | 計算した値（距離の 2 乗など）で比べる |
| `comp` | <span class="rank rank-rare">知ってるだけ</span> | `std::greater{}` | 大小を逆にする |

## ゲームでの使いどころ

| 場面 | 関数 |
| --- | --- |
| 一番近い敵 | `min_element(enemies, {}, 距離)` |
| 回復対象（HP が一番低い仲間） | `min_element(party, {}, &Member::hp)` |
| ヘイトが一番高い相手 | `max_element(party, {}, &Member::aggro)` |
| AI の最善手 | `max_element(actions, {}, &Action::score)` |

## パフォーマンス

- 全要素を 1 回なめる O(n) です。
- 距離で比べるときは、`std::sqrt` を使わずに**距離の 2 乗**で比べると速くなります（大小関係は同じ）。

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| 空の範囲の結果（`end()`）を `*` / `->` で読む | 未定義動作 |

## よくあるミス

??? failure "空のときに読んでしまう"
    敵が 0 体のときに `min_element(enemies)->hp` と書くと未定義動作です。必ず `!= enemies.end()` を確認します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::min` / `max`](min_max.md) | 値のコピーを返す（位置は分からない） |
| [`std::ranges::sort`](sort.md) | 全部並べる（最小・最大だけならこちらが速い） |
| [`std::ranges::nth_element`](partial_sort.md) | N 番目に小さいものを探す |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 最小・最大の「位置」が欲しいなら `min_element` / `max_element`
    - [x] メンバで比べるなら `{}, &T::member`
    - [x] 空なら end()。必ず確認する

## 関連ページ

- [cpprefjp: std::ranges::min_element](https://cpprefjp.github.io/reference/algorithm/ranges_min_element.html)
- [cppreference: std::ranges::min_element](https://en.cppreference.com/w/cpp/algorithm/ranges/min_element)
