---
title: std::forward_like
summary: "別の式の値カテゴリ（左辺値 / 右辺値、const）を、メンバにも引き継いで転送する。"
order: 900
tags:
  - ユーティリティ
---

# std::forward_like

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <utility>`
</div>

`this auto&& self` を使ったメンバ関数（deducing this）で、`self` が右辺値なら中のメンバも右辺値として返したいことがあります。`std::forward_like<T>(x)` は、`T` の左辺値・右辺値・const の性質を `x` に写して転送します。

!!! tip "ポイント"
    - `std::forward` は型 T のまま転送し、`forward_like` は **T の性質を別の x に写す**。
    - deducing this で、メンバを返す関数を 1 つで書くときに使う。

!!! info "このページを読む前に"
    [`std::forward`](forward.md) と [`std::move`](move.md) を先に読んでください。

## 関数の詳しい説明

### std::forward_like {#forward_like}

```cpp
template <class T, class U>
constexpr auto&& forward_like(U&& x) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | テンプレート引数 | 性質を借りる型（`decltype(self)` など） |
| `x` | U&& | 転送する式（メンバなど） |

- 戻り値: `T` の性質を写した `x` の参照
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <type_traits>
#include <utility>

struct Player {
  std::string name = "alice";
  auto&& GetName(this auto&& self) {
    return std::forward_like<decltype(self)>(self.name);
  }
};

int main() {
  Player p;
  std::println("{}", std::is_lvalue_reference_v<decltype(p.GetName())>);
  std::println("{}", std::is_rvalue_reference_v<decltype(std::move(p).GetName())>);
}
```

```text title="実行結果"
true
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| オブジェクトが右辺値ならメンバもムーブして返す | `return std::forward_like<decltype(self)>(self.name);` |

## よくあるミス

??? failure "`forward` と取り違える"
    `forward<T>(x)` は x を T として転送します。`forward_like<T>(x)` は x の型を保ったまま、T の参照・const の性質を写します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`forward`](forward.md) | 同じ型で転送する |
| [`move`](move.md) | 右辺値にする |

## コンパイラ対応

C++23 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] T の性質を別の式に写して転送
    - [x] deducing this と相性がよい
    - [x] forward とは違う

## 関連ページ

- [cpprefjp: std::forward_like](https://cpprefjp.github.io/reference/utility/forward_like.html)
- [cppreference: std::forward_like](https://en.cppreference.com/w/cpp/utility/forward_like)
