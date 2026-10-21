---
title: std::as_const
summary: "値を const 参照として扱う。"
order: 8
group: 小さな便利機能（<utility>）
tags:
  - 型・言語サポート
---

# std::as_const

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <utility>`
</div>

`std::as_const(x)` は、**`x` を `const` 参照として返す**関数です。`const_cast<const T&>(x)` の簡単な書き方で、「この呼び出しでは変更しない」と明示して、`const` 版のメンバ関数（`operator[]` など）を選ばせるときに使います。

!!! tip "ポイント"
    - `for (auto& e : std::as_const(container))` で、読み取り専用の走査。
    - `std::map::operator[]` のような、挿入してしまう関数を避ける。
    - 右辺値を渡すことはできない（削除されている）。

!!! info "このページを読む前に"
    [小さな便利機能](utility-misc.md) の概要と合わせて読むと分かりやすいです。

## 関数の詳しい説明

### std::as_const {#as_const}

<span class="ver ver-17">C++17</span>

```cpp
template <class T>
constexpr const T& as_const(T& t) noexcept;
```

- const 参照にします。const 版の関数を呼びたいときや、範囲 for で書き換えないことを保証したいときに使います

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>
#include <utility>
#include <vector>

int main() {
  std::vector<int> v = {1};
  auto& cv = std::as_const(v);
  std::println("{}", std::is_const_v<std::remove_reference_t<decltype(cv)>>);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 範囲 for で、書き換えないことを明示する | `for (const auto& e : std::as_const(v))` |

## よくあるミス

??? failure "一時オブジェクトを渡す"
    コンパイルエラーです（ぶら下がりを防ぐため）。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::views::as_const`](../algorithms/views/as_const.md) | 範囲の要素を const にする |

## コンパイラ対応

C++17〜C++23 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] const 参照として扱う
    - [x] const 版の関数を選ばせる
    - [x] 一時オブジェクトは不可

## 関連ページ

- [cpprefjp: std::as_const](https://cpprefjp.github.io/reference/utility/as_const.html)
- [cppreference: std::as_const](https://en.cppreference.com/w/cpp/utility/as_const)
