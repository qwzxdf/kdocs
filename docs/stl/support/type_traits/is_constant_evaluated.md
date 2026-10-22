---
title: std::is_constant_evaluated
summary: "いま、コンパイル時に評価されているかを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_constant_evaluated

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <type_traits>`
</div>

同じ `constexpr` 関数でも、コンパイル時には正確だが遅い方法を、実行時には速い方法を使い分けたいことがあります。`is_constant_evaluated()` は、その関数がコンパイル時の評価中なら `true` を返します。C++23 では `if consteval` が読みやすいです。

!!! tip "ポイント"
    - コンパイル時に評価されているときだけ `true`。
    - `constexpr` 変数の初期化や `static_assert` の中が対象。
    - C++23 では `if consteval` を優先する。

!!! info "このページを読む前に"
    [<type_traits>](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_constant_evaluated {#is_constant_evaluated}

```cpp
constexpr bool is_constant_evaluated() noexcept;
```

- 戻り値: コンパイル時に評価中なら `true`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

constexpr int F(int n) {
  return std::is_constant_evaluated() ? n : -n;
}

int main() {
  constexpr int a = F(3);
  int n = 3;
  int b = F(n);
  std::println("{} {}", a, b);
}
```

```text title="実行結果"
3 -3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | コンパイル時と実行時で処理を変える |

## よくあるミス

??? failure "`if constexpr` の条件に使う"
    `if constexpr (std::is_constant_evaluated())` は常に `true` になります。普通の `if` に書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`if consteval`](../../../basics/compiler.md) | C++23 の書き方 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] いま、コンパイル時に評価されているかを調べる
    - [x] コンパイル時に評価されているときだけ `true`
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::is_constant_evaluated](https://cpprefjp.github.io/reference/type_traits/is_constant_evaluated.html)
- [cppreference: std::is_constant_evaluated](https://en.cppreference.com/w/cpp/types/is_constant_evaluated)
