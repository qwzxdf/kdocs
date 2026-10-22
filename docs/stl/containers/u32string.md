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

UTF-32 の文字列です。1 コード単位が 1 つのコードポイントなので、`size()` が「文字数」（コードポイント数）と一致します。メモリは多く使います。

!!! tip "ポイント"
    - `std::basic_string<char32_t>` の別名。
    - 文字列リテラルは `U"..."` と書く。
    - `std::string` と同じ関数が使える。

!!! info "このページを読む前に"
    [`std::string`](string.md) を先に読んでください。

## 関数の詳しい説明

### std::u32string {#u32string}

```cpp
using u32string = basic_string<char32_t>;
```

- 戻り値: `u32string` の値
- 計算量: string と同じ


## 実際に動かしてみる

```cpp
#include <print>
#include <string>

int main() {
  std::u32string s = U"あい😀";
  std::println("{}", s.size());
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| プラットフォームの API に渡す | `std::u32string` |

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
    - [x] char32_t の文字列
    - [x] std::string と同じ使い方
    - [x] size() はコード単位の数

## 関連ページ

- [cpprefjp: std::u32string](https://cpprefjp.github.io/reference/string/basic_string.html)
- [cppreference: std::u32string](https://en.cppreference.com/w/cpp/string/basic_string)
