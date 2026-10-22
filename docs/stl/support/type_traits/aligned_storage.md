---
title: std::aligned_storage
summary: "指定した大きさと境界の、生のメモリ領域の型。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::aligned_storage

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <type_traits>`
</div>

`std::optional` や自作のコンテナのように、あとでオブジェクトを作る前の「ただのメモリ」を用意したいことがあります。`aligned_storage<Size, Align>` は、その大きさと境界のメモリを表す型です。C++23 で非推奨になり、`alignas` を付けた `std::byte` 配列に置き換えるのが推奨されています。

!!! tip "ポイント"
    - C++23 で非推奨。`alignas(T) std::byte buf[sizeof(T)];` が代わりになる。
    - `::type` が領域の型、`_t` 版もある。
    - 領域は初期化されない。

!!! info "このページを読む前に"
    [<type_traits>](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::aligned_storage {#aligned_storage}

```cpp
template <size_t Len, size_t Align = /* 既定 */>
struct aligned_storage { using type = /* Len バイト、Align 境界の POD */; };
template <size_t Len, size_t Align = /* 既定 */>
using aligned_storage_t = typename aligned_storage<Len, Align>::type;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `Len` | size_t | 大きさ（バイト） |
| `Align` | size_t | 境界（省略可） |

- 戻り値: 領域の型（`::type`）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("{}", sizeof(std::aligned_storage_t<16, 8>));
  std::println("{}", alignof(std::aligned_storage_t<16, 8>));
}
```

```text title="実行結果"
16
8
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | あとでオブジェクトを作るためのメモリを用意する |

## よくあるミス

??? failure "新しいコードで使う"
    非推奨です。`alignas(T) std::byte buf[sizeof(T)];` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`aligned_union`](aligned_union.md) | 複数の型を入れられる領域 |

## コンパイラ対応

C++11 から使えます。C++23 で非推奨になりました。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 指定した大きさと境界の、生のメモリ領域の型
    - [x] C++23 で非推奨。`alignas(T) std::byte buf[sizeof(T)];` が代わりになる
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::aligned_storage](https://cpprefjp.github.io/reference/type_traits/aligned_storage.html)
- [cppreference: std::aligned_storage](https://en.cppreference.com/w/cpp/types/aligned_storage)
