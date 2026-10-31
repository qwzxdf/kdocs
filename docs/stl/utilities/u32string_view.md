---
title: std::u32string_view
summary: "`char32_t` を文字の型にもつ、文字列を借りて見るだけの型。"
order: 900
tags:
  - ユーティリティ
---

# std::u32string_view

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <string_view>`
</div>

`std::u32string_view` は、`char32_t` の文字列を所有せずに見る型です。`char32_t` は UTF-32 の 1 単位で、1 要素がちょうど 1 つのコードポイント（Unicode の文字）に対応します。サロゲート ペアがないので、文字を 1 つずつ扱うのに向いています。

!!! tip "ポイント"
    - `basic_string_view<char32_t>` の別名
    - 1 要素 = 1 コードポイント。絵文字も 1 要素
    - 文字数を数えたいときに、`size()` が素直に使える
    - 大きさは UTF-8 の最大 4 倍。メモリを多く使う

!!! info "このページを読む前に"
    [`std::basic_string_view`](basic_string_view.md) を先に読んでください。

## 関数の詳しい説明

### std::u32string_view {#u32string_view}

<span class="ver ver-17">C++17</span>

```cpp
using u32string_view = basic_string_view<char32_t>;
```

1 要素が 1 コードポイントなので、`size()` が文字数に近い値になります。ただし、見た目の 1 文字（グラフィム）は、複数のコードポイント（濃点つきの文字を基本文字と結合文字で表す、肌の色つきの絵文字など）でできることがあります。見た目の文字数が必要な場面では、さらに別の処理が要ります。

リテラルは `U"..."` です。

メモリは、UTF-8 より多く使います。ASCII だけの文字列で、4 倍です。そのため、保存や通信には UTF-8 を使い、文字単位の加工のときだけ UTF-32 にする、という使い分けが一般的です。

## 実際に動かしてみる

```cpp
#include <print>
#include <string_view>

int main() {
  const std::u32string_view v = U"あ😀A";

  std::println("要素数: {}", v.size());
  std::println("2 つ目は絵文字 U+1F600: {}", v[1] == 0x1F600);
  std::println("バイト数: {}", v.size() * sizeof(char32_t));
}
```

```text title="実行結果"
要素数: 3
2 つ目は絵文字 U+1F600: true
バイト数: 12
```

## ゲームでの使いどころ

テキスト エンジンで、1 文字ずつ描画するとき、UTF-8 を UTF-32 のコードポイントの列に直して、扱うことがあります。

## よくあるミス

??? failure "見た目の文字数と同じだと思う"
    結合文字や、複数のコードポイントでできた絵文字は、見た目は 1 文字でも、複数の要素です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`u16string_view`](u16string_view.md) | UTF-16。サロゲート ペアがある |
| [`u8string_view`](u8string_view.md) | UTF-8。1 要素が 1〜4 バイトのうちの 1 バイト |
| [`basic_string_view`](basic_string_view.md) | 元のテンプレート |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::u32string_view](https://cpprefjp.github.io/reference/string_view/basic_string_view.html)
- [cppreference: std::u32string_view](https://en.cppreference.com/w/cpp/string/basic_string_view)
