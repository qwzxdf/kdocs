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

非 `const` のオブジェクトに対して、「`const` として扱いたい」場面があります。たとえば、`const` 版のメンバー関数やオーバーロードを、わざと呼びたい。`const_cast<const T&>(x)` と書くと長いです。`std::as_const(x)` は、<strong>`x` を `const` 参照にして返します</strong>。

!!! tip "ポイント"
    - `std::as_const(x)` は `const T&` を返す
    - `const_cast` より短く、安全（`const` を付けるだけ）
    - 範囲 for で、コンテナの要素を変更しない読み取り専用の走査にする
    - 右辺値は受け付けない（ぶら下がりを避けるため）

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::as_const {#as_const}

<span class="ver ver-17">C++17</span>

```cpp
template <class T>
constexpr std::add_const_t<T>& as_const(T& t) noexcept;
template <class T>
void as_const(const T&&) = delete;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `t` | 左辺値 | `const` にしたいオブジェクト |

`std::as_const(x)` は、`x` と同じ型の `const` 参照を返します。コピーは起きません。

用途として典型的なのは、`std::vector` などの `begin()` / `end()` で、`const` 版（`const_iterator` を返す）を選びたいときです。範囲 for の中でコンテナの要素を書き換えない意図を示すために、`for (auto& x : std::as_const(v))` と書けます。

一時オブジェクトを渡すコンパイルエラーになるのは、返した参照が式の終わりでぶら下がる事故を避けるためです。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>
#include <utility>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};
  using Ref = decltype(*std::as_const(v).begin());
  std::println("const 版の begin が選ばれる: {}", std::is_same_v<Ref, const int&>);
  std::println("同じオブジェクトを指す: {}", &std::as_const(v) == &v);
}
```

```text title="実行結果"
const 版の begin が選ばれる: true
同じオブジェクトを指す: true
```

## ゲームでの使いどころ

読み取り専用であることを、コードで明示します。

```cpp
for (const auto& enemy : std::as_const(enemies)) {   // 変更しない走査
  Draw(enemy);
}
```

## よくあるミス

??? failure "一時オブジェクトを渡してコンパイルエラーになる"
    いったん変数に入れます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`add_const`](type_traits/add_const.md) | 型に `const` を付ける |
| [`byte`](byte.md) | バイトを表す型 |

## コンパイラ対応

C++17 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::as_const(x)` は `const` 参照を返す
    - [x] `const_cast` より安全
    - [x] 一時オブジェクトは渡せない

## 関連ページ

- [cpprefjp: std::as_const](https://cpprefjp.github.io/reference/utility/as_const.html)
- [cppreference: std::as_const](https://en.cppreference.com/w/cpp/utility/as_const)
