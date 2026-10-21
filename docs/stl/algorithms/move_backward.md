---
title: std::ranges::move_backward
summary: "範囲の要素を、後ろから順にムーブして移す。"
order: 50
tags:
  - アルゴリズム
---

# std::ranges::move_backward

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::move_backward` は、[`copy_backward`](copy_backward.md) のムーブ版です。**後ろの要素から順にムーブして**、範囲を後ろへずらします。`unique_ptr` や `std::string` の配列の途中に空きを作るときに使います。

!!! tip "ポイント"
    - 移し先は**終わりの位置**を渡す。
    - 前へずらすなら [`move`](move.md)、後ろへずらすなら `move_backward`。

!!! info "このページを読む前に"
    [ムーブ](../../basics/move.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::move_backward {#move_backward}

```cpp
template <bidirectional_range R, bidirectional_iterator I>
constexpr move_backward_result<borrowed_iterator_t<R>, I> move_backward(R&& r, I result);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | 範囲 | 移す元 |
| `result` | イテレータ | 移し先の**終わりの位置** |

- 戻り値: `in` と `out` の組
- 計算量: 要素数 n に対して、n 回のムーブ代入

```cpp
#include <algorithm>
#include <print>
#include <ranges>
#include <string>
#include <vector>

int main() {
  std::vector<std::string> names = {"A", "B", "C", ""};  // 末尾に空きがある

  // 先頭の 3 個を、1 つ後ろへずらす
  std::ranges::move_backward(std::ranges::subrange(names.begin(), names.begin() + 3), names.end());
  names[0] = "新入り";
  std::println("{}", names);
}
```

```text title="実行結果"
["新入り", "A", "B", "C"]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| `std::string` や `unique_ptr` の並びの途中に空きを作る | `move_backward(range, end)` |

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| 移し先が、移す元の範囲の内側に入る | 未定義動作 |

## よくあるミス

??? failure "移し先に先頭を渡す"
    `copy_backward` と同じで、移し先は**終わりの位置**です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::move`](move.md) | 前から順にムーブする |
| [`std::ranges::copy_backward`](copy_backward.md) | コピーする版 |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 後ろから順にムーブする
    - [x] 移し先は終わりの位置
    - [x] 後ろへずらすときに使う

## 関連ページ

- [cpprefjp: std::ranges::move_backward](https://cpprefjp.github.io/reference/algorithm/ranges_move_backward.html)
- [cppreference: std::ranges::move_backward](https://en.cppreference.com/w/cpp/algorithm/ranges/move_backward)
