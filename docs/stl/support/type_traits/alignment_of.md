---
title: std::alignment_of
summary: "型のアライメント（配置できる境界のバイト数）を調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::alignment_of

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <type_traits>`
</div>

メモリ上に型の値を置くとき、アドレスは型ごとの倍数に揃っている必要があります（アラインメント）。`std::alignment_of` は、<strong>型のアラインメント</strong>を調べます。`alignof(T)` と同じ値です。

!!! tip "ポイント"
    - `std::alignment_of_v<T>` は `alignof(T)` と同じ
    - 戻り値は `std::size_t`
    - `double` は 8 バイト境界など、型で違う
    - テンプレートの中では `alignof(T)` を直接書くほうが短い

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::alignment_of_v {#alignment_of}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr std::size_t alignment_of_v = alignment_of<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | アラインメントを調べたい型 |

`alignment_of_v<T>` は、型 `T` のオブジェクトを置けるアドレスの間隔（バイト）です。`alignof(T)` と同じ値で、`alignof` のほうが言語の機能として短く書けます。この関数は、トレイトとして使いたい場面（`integral_constant` を継承したい場合）のために用意されています。

用途は、SIMD や GPU に渡すバッファの配置、自前のメモリ アロケーターで、境界を揃えるときの計算です。

## 実際に動かしてみる

```cpp
#include <cstddef>
#include <print>
#include <type_traits>

int main() {
  std::println("alignof(int)    と一致: {}", std::alignment_of_v<int> == alignof(int));
  std::println("alignof(double) と一致: {}", std::alignment_of_v<double> == alignof(double));
  std::println("2 の累乗: {}", (std::alignment_of_v<double> & (std::alignment_of_v<double> - 1)) == 0);
}
```

```text title="実行結果"
alignof(int)    と一致: true
alignof(double) と一致: true
2 の累乗: true
```

## ゲームでの使いどころ

自前のアロケーターで、確保するアドレスを型の境界に揃えます。

```cpp
constexpr std::size_t align = alignof(T);   // alignment_of_v<T> と同じ
address = (address + align - 1) & ~(align - 1);
```

## よくあるミス

??? failure "`alignof` と別の値を期待する"
    同じ値です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`alignof`](../../../basics/index.md) | 言語の演算子 |
| [`align`](../../memory/align.md) | ポインターを境界に揃える |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `alignment_of_v<T>` は `alignof(T)` と同じ
    - [x] アラインメントは 2 の累乗
    - [x] 自前のアロケーターで使う

## 関連ページ

- [cpprefjp: std::alignment_of](https://cpprefjp.github.io/reference/type_traits/alignment_of.html)
- [cppreference: std::alignment_of](https://en.cppreference.com/w/cpp/types/alignment_of)
