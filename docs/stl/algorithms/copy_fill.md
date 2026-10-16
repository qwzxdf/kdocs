---
title: std::ranges::copy / fill / iota など
tags:
  - アルゴリズム
---

# std::ranges::copy / fill / iota など

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>` / `#include <numeric>`
</div>

このページでは、**範囲に値を書き込む系のアルゴリズム**をまとめて扱います。別の場所へコピーする `copy`、条件に合うものだけコピーする `copy_if`、全部同じ値で埋める `fill`、連番で埋める `iota`、関数の結果で埋める `generate`、各要素を変換して書き込む `transform` です。

!!! tip "結論"
    - vector を丸ごとコピーするなら `b = a;` で十分。これらは「一部だけ」「別の種類のコンテナへ」「既にある場所へ」書き込むときに使う。
    - 書き込み先が空の vector なら `std::back_inserter(v)` を渡す（足りない場所に書くと未定義動作）。
    - 新しい vector が欲しいだけなら、[`std::views`](views.md) + [`std::ranges::to`](ranges_to.md) のほうが短く書けることが多い。

## 関数一覧

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`std::ranges::copy`](#copy) | <span class="rank rank-sometimes">たまに</span> | 別の場所へコピー | O(n) |
| [`std::ranges::fill`](#fill) | <span class="rank rank-sometimes">たまに</span> | 全部同じ値で埋める | O(n) |
| [`std::ranges::copy_if`](#copy_if) | <span class="rank rank-sometimes">たまに</span> | 条件に合うものだけコピー | O(n) |
| [`std::ranges::transform`](#transform) | <span class="rank rank-sometimes">たまに</span> | 各要素を変換して書き込む | O(n) |
| [`std::iota`](#iota) | <span class="rank rank-sometimes">たまに</span> | 連番で埋める | O(n) |
| [`std::ranges::generate`](#generate) | <span class="rank rank-rare">知ってるだけ</span> | 関数の結果で埋める | O(n) |
| [`std::ranges::copy_n`](#copy_n) | <span class="rank rank-rare">知ってるだけ</span> | 先頭 n 個をコピー | O(n) |
| [`std::ranges::fill_n`](#fill_n) | <span class="rank rank-rare">知ってるだけ</span> | 先頭 n 個を埋める | O(n) |

## よくある使い方

```cpp
#include <algorithm>
#include <iterator>
#include <numeric>
#include <print>
#include <vector>

int main() {
  std::vector<int> ids(5);
  std::iota(ids.begin(), ids.end(), 100);  // 100, 101, 102, ...
  std::println("{}", ids);

  std::vector<int> even;
  std::ranges::copy_if(ids, std::back_inserter(even), [](int x) { return x % 2 == 0; });
  std::println("{}", even);

  std::ranges::fill(ids, -1);
  std::println("{}", ids);
}
```

```text title="実行結果"
[100, 101, 102, 103, 104]
[100, 102, 104]
[-1, -1, -1, -1, -1]
```

## 関数の詳しい説明

### std::ranges::copy {#copy}

```cpp
template <input_range R, weakly_incrementable O>
constexpr copy_result<borrowed_iterator_t<R>, O> copy(R&& r, O result);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | 範囲 | コピー元 |
| `result` | 出力イテレータ | 書き込み先の先頭。**足りる大きさがあるか、`std::back_inserter` にする** |

- 戻り値: `.in`（読み終わった位置）と `.out`（書き終わった次の位置）を持つ構造体

```cpp
#include <algorithm>
#include <array>
#include <print>
#include <vector>

int main() {
  std::array<int, 3> src = {1, 2, 3};
  std::vector<int> dst(5, 0);
  std::ranges::copy(src, dst.begin() + 1);  // 添字 1 から上書き
  std::println("{}", dst);
}
```

```text title="実行結果"
[0, 1, 2, 3, 0]
```

### std::ranges::fill {#fill}

```cpp
template <class T, output_range<const T&> R>
constexpr borrowed_iterator_t<R> fill(R&& r, const T& value);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | 範囲 | 埋める範囲 |
| `value` | `const T&` | 入れる値 |

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> visited(6, 1);
  std::ranges::fill(visited, 0);  // 毎回の探索の前にリセット
  std::println("{}", visited);
}
```

```text title="実行結果"
[0, 0, 0, 0, 0, 0]
```

### std::ranges::copy_if {#copy_if}

```cpp
template <input_range R, weakly_incrementable O, class Proj = identity, class Pred>
constexpr copy_if_result<borrowed_iterator_t<R>, O> copy_if(R&& r, O result, Pred pred, Proj proj = {});
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | 範囲 | コピー元 |
| `result` | 出力イテレータ | 書き込み先 |
| `pred` | 関数 | **コピーするなら `true`** |
| `proj` | プロジェクション | `pred` に渡す前の変換 |

```cpp
#include <algorithm>
#include <iterator>
#include <print>
#include <vector>

struct Enemy {
  int id;
  bool visible;
};

int main() {
  std::vector<Enemy> enemies = {{1, true}, {2, false}, {3, true}};
  std::vector<Enemy> to_draw;
  std::ranges::copy_if(enemies, std::back_inserter(to_draw), &Enemy::visible);
  std::println("描画するのは {} 体", to_draw.size());
}
```

```text title="実行結果"
描画するのは 2 体
```

### std::ranges::transform {#transform}

```cpp
template <input_range R, weakly_incrementable O, class F, class Proj = identity>
constexpr unary_transform_result<borrowed_iterator_t<R>, O> transform(R&& r, O result, F op, Proj proj = {});
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | 範囲 | 元 |
| `result` | 出力イテレータ | 書き込み先（元と同じでも OK） |
| `op` | 関数 | 要素を受け取って、書き込む値を返す |

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<float> speeds = {1.0f, 2.0f, 3.0f};
  // その場で全部 1.5 倍にする（書き込み先 = 元）
  std::ranges::transform(speeds, speeds.begin(), [](float s) { return s * 1.5f; });
  std::println("{}", speeds);
}
```

```text title="実行結果"
[1.5, 3, 4.5]
```

!!! note "実際は"
    その場で書き換えるなら、範囲 for で `for (auto& s : speeds) s *= 1.5f;` と書くほうが読みやすいことも多いです。

### std::iota {#iota}

```cpp
template <class ForwardIt, class T>
constexpr void iota(ForwardIt first, ForwardIt last, T value);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `first`, `last` | イテレータ | 埋める範囲 |
| `value` | `T` | 最初の値。1 ずつ増える |

- `<numeric>` にあります。C++23 では `std::ranges::iota(r, value)` もあります

```cpp
#include <numeric>
#include <print>
#include <vector>

int main() {
  std::vector<int> order(4);
  std::iota(order.begin(), order.end(), 0);  // 0, 1, 2, 3（添字の配列を作る定番）
  std::println("{}", order);
}
```

```text title="実行結果"
[0, 1, 2, 3]
```

### std::ranges::generate {#generate}

```cpp
template <class R, copy_constructible F>
constexpr borrowed_iterator_t<R> generate(R&& r, F gen);
```

- 各要素に `gen()` の戻り値を入れます。呼ぶたびに違う値を返す関数（乱数など）と組み合わせます

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  int n = 1;
  std::vector<int> powers(5);
  std::ranges::generate(powers, [&n] {
    int current = n;
    n *= 2;
    return current;
  });
  std::println("{}", powers);
}
```

```text title="実行結果"
[1, 2, 4, 8, 16]
```

### std::ranges::copy_n {#copy_n}

```cpp
template <input_iterator I, weakly_incrementable O>
constexpr copy_n_result<I, O> copy_n(I first, std::iter_difference_t<I> n, O result);
```

- `first` から `n` 個を `result` にコピーします

### std::ranges::fill_n {#fill_n}

```cpp
template <class T, output_iterator<const T&> O>
constexpr O fill_n(O first, std::iter_difference_t<O> n, const T& value);
```

- `first` から `n` 個を `value` で埋めます

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> src = {9, 8, 7, 6};
  std::vector<int> dst(4, 0);
  std::ranges::copy_n(src.begin(), 2, dst.begin());
  std::ranges::fill_n(dst.begin() + 2, 2, 5);
  std::println("{}", dst);
}
```

```text title="実行結果"
[9, 8, 5, 5]
```

## フラグ・オプション

書き込み先によく渡すものです。

| 渡すもの | 重要度 | 意味 |
| --- | --- | --- |
| `std::back_inserter(v)` | <span class="rank rank-often">よく使う</span> | `v.push_back` で追加しながら書く（`<iterator>`） |
| `v.begin()` | <span class="rank rank-sometimes">たまに</span> | 既にある要素を上書きする（大きさが足りている必要がある） |
| `std::inserter(s, s.end())` | <span class="rank rank-rare">知ってるだけ</span> | set / map に `insert` しながら書く |

## ゲームでの使いどころ

| 場面 | 関数 |
| --- | --- |
| 盤面・訪問フラグのリセット | `fill` |
| 添字の配列を作る | `iota` |
| 描画対象だけ集める | `copy_if` |
| ステータスを一括で倍率補正 | `transform` |

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| 書き込み先の大きさが足りない（`begin()` を渡した場合） | 未定義動作 |
| コピー元とコピー先が重なっている（`copy` で後ろへずらす） | 未定義動作（`copy_backward` を使う） |

## よくあるミス

??? failure "空の vector の begin() に書き込む"
    ```cpp
    std::vector<int> dst;
    std::ranges::copy(src, dst.begin());  // dst は空なので範囲外に書く

    std::ranges::copy(src, std::back_inserter(dst));  // OK
    ```

## 理解度チェック

!!! question "Q1. `std::vector<int> v(3); std::iota(v.begin(), v.end(), 5);` のあと v は？"
    <div class="spoiler" markdown>

    **答え:** `[5, 6, 7]`。

    </div>

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::views::filter`](views.md#filter) + [`to`](ranges_to.md) | 新しい vector を作るなら短く書ける |
| [`std::views::iota`](views.md#iota) | 連番を「見る」だけ |
| `v.assign(n, value)` | vector のメンバで埋め直す |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。`std::ranges::iota` は C++23（GCC 13 / MSVC 17.4 以降が目安）です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 空の vector へは `std::back_inserter(v)` で書く
    - [x] リセットは `fill`、連番は `iota`、絞り込みコピーは `copy_if`

## 関連ページ

- [cpprefjp: std::ranges::copy](https://cpprefjp.github.io/reference/algorithm/ranges_copy.html)
- [cppreference: std::ranges::copy](https://en.cppreference.com/w/cpp/algorithm/ranges/copy)
