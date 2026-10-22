---
title: std::u16string
summary: "`char16_t` を文字の型にもつ文字列。"
order: 900
tags:
  - コンテナ
---

# std::u16string

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <string>`
</div>

UTF-16 の文字列です。`あ` や `い` は 1 コード単位、絵文字などは 2 コード単位（サロゲートペア）になります。`size()` は文字数ではなく、コード単位の数です。

!!! tip "ポイント"
    - `std::basic_string<char16_t>` の別名。
    - 文字列リテラルは `u"..."` と書く。
    - `std::string` と同じ関数が使える。

!!! info "このページを読む前に"
    [`std::string`](string.md) を先に読んでください。

## 関数の詳しい説明

### std::u16string {#u16string}

```cpp
using u16string = basic_string<char16_t>;
```

- 戻り値: `u16string` の値
- 計算量: string と同じ


## 実際に動かしてみる

```cpp
#include <print>
#include <string>

int main() {
  std::u16string s = u"あい😀";
  std::println("{}", s.size());
}
```

```text title="実行結果"
4
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| プラットフォームの API に渡す | `std::u16string` |

## よくあるミス

??? failure "文字列の長さ = 文字数だと思う"
    `size()` は**コード単位**の数です。サロゲートペアや結合文字が入ると、見た目の文字数と一致しません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::string`](string.md) | char の文字列 |
| [`basic_string`](basic_string.md) | 元になるテンプレート |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] char16_t の文字列
    - [x] std::string と同じ使い方
    - [x] size() はコード単位の数

## 関連ページ

- [cpprefjp: std::u16string](https://cpprefjp.github.io/reference/string/basic_string.html)
- [cppreference: std::u16string](https://en.cppreference.com/w/cpp/string/basic_string)
