---
title: std::addressof
summary: "`operator&` が書き換えられていても、オブジェクトの本当のアドレスを取る。"
order: 73
tags:
  - ユーティリティ
---

# std::addressof

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <memory>`
</div>

`std::addressof(x)` は、**`&` 演算子が上書きされている型でも、オブジェクトの本当のアドレスを取る**関数です。普通は `&x` で足りますが、`operator&` をオーバーロードした型（スマートポインターの一部、`_com_ptr_t` など）でも、確実に取れます。テンプレートで、任意の型のアドレスを取るときに使います。

!!! tip "ポイント"
    - テンプレートのコードでは `&x` ではなく `std::addressof(x)` を使うと安全。
    - 普通の型では `&x` と同じ結果。
    - `std::to_address` とは別（そちらはポインターのようなものから生ポインターを取る）。

!!! info "このページを読む前に"
    - [stl/index.md](../index.md)（STL 全体の地図（どこに何があるか））
    - [ムーブ（コピーとムーブ）](../../basics/move.md)（ムーブの基礎）

## 関数の詳しい説明

### std::addressof {#addressof}

```cpp
template <class T>
constexpr T* addressof(T& x) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | `T&` | アドレスを取りたいオブジェクト |

- 戻り値: `x` の本当のアドレス
- 計算量: O(1)

```cpp
#include <memory>
#include <print>

struct Weird {
  int operator&() const { return 0; }  // & を上書きしている（悪い例）
};

int main() {
  Weird w;
  Weird* p = std::addressof(w);  // &w では int が返ってしまう
  std::println("{}", p != nullptr);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 任意の型を受け取るテンプレートで、アドレスを取る | `std::addressof(obj)` |

## よくあるミス

??? failure "operator& を上書きする"
    そもそも上書きしないのが安全です。COM のスマートポインターには、`GetAddressOf()` などの専用関数があります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`to_address`](../memory/to_address.md) | ポインターのようなものから生ポインターを取る |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 本当のアドレスを取る
    - [x] テンプレートで安全
    - [x] 普通の型では &x と同じ

## 関連ページ

- [cpprefjp: std::addressof](https://cpprefjp.github.io/reference/memory/addressof.html)
- [cppreference: std::addressof](https://en.cppreference.com/w/cpp/memory/addressof)
