---
title: std::aligned_accessor
summary: "要素が指定した境界に並ぶことを保証する mdspan のアクセサ。"
order: 900
tags:
  - コンテナ
---

# std::aligned_accessor

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <mdspan>`
</div>

SIMD で配列を処理するとき、配列の先頭が 16 バイト境界などに揃っていると速くなります。`aligned_accessor<T, N>` は、「この配列は N バイト境界に揃っている」と約束するアクセサで、コンパイラが速いコードを出せるようになります。

!!! tip "ポイント"
    - `byte_alignment` に境界のバイト数が入る。
    - 約束が嘘だと未定義動作。
    - [`assume_aligned`](../memory/assume_aligned.md) と同じ考え方。

!!! info "このページを読む前に"
    [`std::mdspan`](mdspan.md) を先に読んでください。

## 関数の詳しい説明

### std::aligned_accessor {#aligned_accessor}

```cpp
template <class ElementType, std::size_t ByteAlignment>
struct aligned_accessor {
  static constexpr std::size_t byte_alignment = ByteAlignment;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ElementType` | 型 | 要素の型 |
| `ByteAlignment` | size_t | 境界のバイト数（2 のべき乗） |

- 戻り値: `byte_alignment` に境界が入る
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <mdspan>
#include <print>

int main() {
  std::println("{}", std::aligned_accessor<float, 16>::byte_alignment);
}
```

```text title="実行結果"
16
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 16 バイト境界の配列を SIMD で処理する | `std::mdspan<float, Ext, std::layout_right, std::aligned_accessor<float, 16>>` |

## よくあるミス

??? failure "境界が合っていない配列を渡す"
    約束が守られないと未定義動作です。`alignas` で確保した配列だけに使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`default_accessor`](default_accessor.md) | 標準のアクセサ |
| [`assume_aligned`](../memory/assume_aligned.md) | ポインタに境界を約束する |

## コンパイラ対応

C++26 の機能です。対応は新しい標準ライブラリに限られます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 境界を保証するアクセサ
    - [x] byte_alignment
    - [x] 嘘は未定義動作

## 関連ページ

- [cpprefjp: std::aligned_accessor](https://cpprefjp.github.io/reference/mdspan/aligned_accessor.html)
- [cppreference: std::aligned_accessor](https://en.cppreference.com/w/cpp/container/mdspan/aligned_accessor)
