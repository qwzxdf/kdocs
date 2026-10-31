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

オブジェクトのアドレスは `&x` で取れるはずですが、クラスが `operator&` を上書きしていると、`&x` は、そのクラスが決めた別の値を返します。スマート ポインタの一部や、COM の ラッパーなどで見かけます。`std::addressof(x)` は、`operator&` に関係なく、<strong>オブジェクトの本当のアドレス</strong>を返します。

!!! tip "ポイント"
    - `&x` は、`operator&` が上書きされていると、別の意味になる
    - `std::addressof(x)` は、いつも本当のアドレスを返す
    - ライブラリのテンプレートは、`&x` ではなく `addressof` を使っている
    - 右辺値は渡せない（C++17 以降は削除されている）

!!! info "このページを読む前に"
    [ポインタ](../../basics/pointer.md)を先に読んでください。

## 関数の詳しい説明

### std::addressof {#addressof}

<span class="ver ver-11">C++11</span>

```cpp
template <class T> constexpr T* addressof(T& arg) noexcept;
template <class T> const T* addressof(const T&&) = delete;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `arg` | `T&` | アドレスを取りたいオブジェクト |

実装は、コンパイラの組み込み機能（`__builtin_addressof`）で、`operator&` を呼びません。C++17 から `constexpr` です。

`operator&` を上書きすることは、普通はしません。ただし、COM の スマート ポインタ（`CComPtr` など）は、`&` で「内部のポインタのアドレス」を返す設計になっています。そのオブジェクト自身のアドレスが欲しいときは、`std::addressof` を使います。

標準のコンテナやアルゴリズムは、内部で要素のアドレスを取るとき、`addressof` を使っています。そのため、`operator&` を上書きした型でも、`std::vector` に入れて使えます。

右辺値（一時オブジェクト）は渡せません。一時オブジェクトのアドレスを取っても、すぐに無効になるからです。

## 実際に動かしてみる

```cpp
#include <memory>
#include <print>

// operator& を上書きした、紛らわしい型
struct Evil {
  Evil* operator&() { return nullptr; }
};

int main() {
  Evil e;

  std::println("&e: {}", &e == nullptr);                    // 上書きされた値
  std::println("addressof: {}", std::addressof(e) != nullptr);  // 本当のアドレス

  int x = 0;
  std::println("普通の型は同じ: {}", std::addressof(x) == &x);
}
```

```text title="実行結果"
&e: true
addressof: true
普通の型は同じ: true
```

## ゲームでの使いどころ

テンプレートのライブラリを書くときに、任意の型のアドレスを安全に取るために使います。普段のゲームのコードでは、`&x` で足ります。

## よくあるミス

??? failure "COM のラッパーに & を使う"
    `&ptr` は、内部のポインタのアドレスで、オブジェクトのアドレスではありません。オブジェクトのアドレスが欲しいときは `std::addressof` です。

## 類似

| 名前 | 違い |
| --- | --- |
| `operator&` | 上書きされると別の値になる |
| [`std::declval`](declval.md) | 型の計算用の仮の値 |
| `std::to_address` | ポインタ風の型から、素のアドレスを取る |

## コンパイラ対応

C++11 から使えます。`constexpr` は C++17 から。

## 関連ページ

- [cpprefjp: std::addressof](https://cpprefjp.github.io/reference/memory/addressof.html)
- [cppreference: std::addressof](https://en.cppreference.com/w/cpp/memory/addressof)
