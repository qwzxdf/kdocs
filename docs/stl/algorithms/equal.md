---
title: std::ranges::equal / mismatch
tags:
  - アルゴリズム
---

# std::ranges::equal / mismatch

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::equal` は、**2 つの範囲の中身が全部同じか**を調べるアルゴリズムです。`std::ranges::mismatch` は、**最初に違っているところ**を探します。`lexicographical_compare` は辞書順で大小を比べます。vector 同士なら `==` で比べられますが、vector と配列、list と vector のように**型の違う範囲どうし**でも比べられるのが利点です。

!!! tip "結論"
    - 同じコンテナ同士なら `a == b` で十分。型が違う範囲どうしなら `std::ranges::equal(a, b)`。
    - どこが違うか知りたいなら `std::ranges::mismatch`。
    - 「入力したコマンドが正解の手順と同じか」などに使える。

## 関数一覧

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`std::ranges::equal`](#equal) | <span class="rank rank-sometimes">たまに</span> | 全部同じか | O(n) |
| [`std::ranges::mismatch`](#mismatch) | <span class="rank rank-sometimes">たまに</span> | 最初に違うところを探す | O(n) |
| [`std::ranges::lexicographical_compare`](#lexicographical_compare) | <span class="rank rank-rare">知ってるだけ</span> | 辞書順で小さいか | O(n) |
| [`std::ranges::is_permutation`](#is_permutation) | <span class="rank rank-rare">知ってるだけ</span> | 並び替えれば同じになるか | O(n²) |

## よくある使い方

```cpp
#include <algorithm>
#include <array>
#include <print>
#include <vector>

enum class Key { kUp, kDown, kLeft, kRight, kA, kB };

int main() {
  // 隠しコマンド
  constexpr std::array kSecret = {Key::kUp, Key::kUp, Key::kDown, Key::kDown, Key::kA};
  std::vector<Key> input = {Key::kUp, Key::kUp, Key::kDown, Key::kDown, Key::kA};

  std::println("成功？ {}", std::ranges::equal(input, kSecret));  // array と vector を比べる
}
```

```text title="実行結果"
成功？ true
```

## 関数の詳しい説明

### std::ranges::equal {#equal}

```cpp
template <input_range R1, input_range R2, class Pred = ranges::equal_to,
          class Proj1 = identity, class Proj2 = identity>
constexpr bool equal(R1&& r1, R2&& r2, Pred pred = {}, Proj1 proj1 = {}, Proj2 proj2 = {});
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `r1`, `r2` | 範囲 | 比べる 2 つ（型が違ってもいい） | 省略不可 |
| `pred` | 関数 | 「等しい」の判定 | `==` |
| `proj1`, `proj2` | プロジェクション | それぞれの比べる前の変換 | そのまま |

- 戻り値: 長さが同じで、全部の要素が等しければ `true`

### std::ranges::mismatch {#mismatch}

```cpp
template <input_range R1, input_range R2, class Pred = ranges::equal_to,
          class Proj1 = identity, class Proj2 = identity>
constexpr mismatch_result<borrowed_iterator_t<R1>, borrowed_iterator_t<R2>>
mismatch(R1&& r1, R2&& r2, Pred pred = {}, Proj1 proj1 = {}, Proj2 proj2 = {});
```

- 戻り値: `.in1` と `.in2`（最初に違った位置。全部同じなら短いほうの終わり）

```cpp
#include <algorithm>
#include <print>
#include <string>

int main() {
  std::string answer = "dragon";
  std::string input = "drag0n";
  auto [a, b] = std::ranges::mismatch(answer, input);
  std::println("{} 文字目が違う（正解 {} / 入力 {}）", a - answer.begin() + 1, *a, *b);
}
```

```text title="実行結果"
5 文字目が違う（正解 o / 入力 0）
```

### std::ranges::lexicographical_compare {#lexicographical_compare}

```cpp
template <input_range R1, input_range R2, class Proj1 = identity, class Proj2 = identity,
          class Comp = ranges::less>
constexpr bool lexicographical_compare(R1&& r1, R2&& r2, Comp comp = {}, Proj1 proj1 = {},
                                       Proj2 proj2 = {});
```

- 先頭から比べて、`r1` が辞書順で小さければ `true`（文字列の比較と同じルール）

### std::ranges::is_permutation {#is_permutation}

```cpp
template <forward_range R1, forward_range R2, class Proj1 = identity, class Proj2 = identity,
          class Pred = ranges::equal_to>
constexpr bool is_permutation(R1&& r1, R2&& r2, Pred pred = {}, Proj1 proj1 = {}, Proj2 proj2 = {});
```

- 並び替えれば同じになるか（要素の種類と数が同じか）。パズルの「ピースが全部そろっているか」の判定に使えます

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> v1 = {1, 2, 3};
  std::vector<int> v2 = {1, 3, 0};
  std::vector<int> pieces = {3, 1, 2};
  std::println("{} {}", std::ranges::lexicographical_compare(v1, v2),
               std::ranges::is_permutation(v1, pieces));
}
```

```text title="実行結果"
true true
```

## フラグ・オプション

`pred` / `proj` で比べ方を変えられます（大文字小文字を無視、メンバで比べる、など）。

## ゲームでの使いどころ

| 場面 | 関数 |
| --- | --- |
| コマンド入力・パスワード | `equal` |
| 答え合わせでどこが違うか表示 | `mismatch` |
| パズルの完成判定 | `equal` / `is_permutation` |

## よくあるミス

??? failure "長さの違う範囲を古い std::equal で比べる"
    古い `std::equal(a.begin(), a.end(), b.begin())` は、b が短いと範囲外を読みます。ranges 版は長さも比べるので安全です。

## 理解度チェック

!!! question "Q1. `std::ranges::equal(std::vector{1, 2}, std::vector{1, 2, 3})` は？"
    <div class="spoiler" markdown>

    **答え:** `false`。長さが違うからです。

    </div>

## これだけ覚える

!!! abstract "まとめ"
    - [x] 型の違う範囲の比較は equal
    - [x] 違う場所は mismatch

## 関連ページ

- [std::ranges::find](find.md)
- [cppreference: std::ranges::equal](https://en.cppreference.com/w/cpp/algorithm/ranges/equal)
