---
title: std::u32string
summary: "`char32_t` を文字の型にもつ文字列。"
order: 900
tags:
  - コンテナ
---

# std::u32string

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <string>`
</div>

`std::u32string` は、`char32_t` の文字列で、UTF-32 を表します。1 要素が 1 つのコードポイントなので、文字単位の処理がしやすい代わりに、メモリを多く使います。

!!! tip "ポイント"
    - `basic_string<char32_t>` の別名
    - リテラルは `U"..."`
    - 1 要素 = 1 コードポイント。絵文字も 1 要素
    - UTF-8 の最大 4 倍の大きさ

!!! info "このページを読む前に"
    [`std::string`](string.md) を先に読んでください。

## 関数の詳しい説明

### std::u32string {#u32string}

<span class="ver ver-11">C++11</span>

```cpp
using u32string = basic_string<char32_t>;
```

文字ごとに加工する処理（ひらがなをカタカナにする、文字種を調べる）は、UTF-32 に変換してから行うと、サロゲートや複数バイトを気にせずに済みます。見た目の 1 文字（結合文字を含むもの）は、複数のコードポイントになることがあります。

保存や通信には、UTF-8 を使い、加工のときだけ UTF-32 にするのが、一般的な使い分けです。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>

int main() {
  std::u32string s = U"あ😀A";
  std::println("要素数: {}", s.size());

  // 1 文字ずつ加工しやすい
  s[2] = U'B';
  std::println("3 つ目: {}", s[2] == U'B');
  std::println("2 つ目は絵文字: {}", s[1] == 0x1F600);
}
```

```text title="実行結果"
要素数: 3
3 つ目: true
2 つ目は絵文字: true
```

## ゲームでの使いどころ

テキスト エンジンで、1 文字ずつ描画・加工するときに使います。

## よくあるミス

??? failure "保存に使う"
    4 バイト単位でメモリを使います。保存は UTF-8 にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`string`](string.md) | UTF-8 |
| [`u16string`](u16string.md) | UTF-16 |
| [`u8string`](u8string.md) | `char8_t` の UTF-8 |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::u32string](https://cpprefjp.github.io/reference/string/basic_string.html)
- [cppreference: std::u32string](https://en.cppreference.com/w/cpp/string/basic_string)
