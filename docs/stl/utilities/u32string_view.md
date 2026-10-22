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

`u32string` を、コピーせずに見るだけの型です。1 コード単位が 1 コードポイントです。

!!! tip "ポイント"
    - `std::basic_string_view<char32_t>` の別名。
    - 持ち主ではないので、元の文字列より長く生きてはいけない。
    - `string_view` と同じ関数が使える。

!!! info "このページを読む前に"
    [`std::string_view`](string_view.md) を先に読んでください。

## 関数の詳しい説明

### std::u32string_view {#u32string_view}

```cpp
using u32string_view = basic_string_view<char32_t>;
```

- 戻り値: `u32string_view` の値
- 計算量: string_view と同じ


## 実際に動かしてみる

```cpp
#include <print>
#include <string_view>

int main() {
  std::u32string_view v = U"😀";
  std::println("{}", v.size());
}
```

```text title="実行結果"
1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 関数の引数で文字列を受ける | `void F(std::u32string_view s);` |

## よくあるミス

??? failure "元の文字列が先に消える"
    借りている先が消えると、中身は壊れます。一時オブジェクトから作った `string_view` を保存しないようにします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`string_view`](string_view.md) | char の版 |
| [`basic_string_view`](basic_string_view.md) | 元になるテンプレート |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] char32_t の string_view
    - [x] 借りるだけで持ち主ではない
    - [x] string_view と同じ使い方

## 関連ページ

- [cpprefjp: std::u32string_view](https://cpprefjp.github.io/reference/string_view/basic_string_view.html)
- [cppreference: std::u32string_view](https://en.cppreference.com/w/cpp/string/basic_string_view)
