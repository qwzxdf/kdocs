---
title: std::ctype
summary: "文字の分類（数字か、英字か）と、大文字小文字の変換を担当するファセット。"
order: 900
tags:
  - 入出力・文字列
---

# std::ctype

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <locale>`
</div>

`isalpha`・`toupper` のようなロケール付きの文字の分類・変換は、`ctype` ファセットが担当しています。`std::use_facet<std::ctype<char>>(loc)` で取り出して使います。

!!! tip "ポイント"
    - ロケール（言語・地域ごとの規則）の部品。
    - ふつうは `std::locale` 経由で使う。
    - ゲームのローカライズでは、書式（日付・数字）に関わる。

!!! info "このページを読む前に"
    [`std::locale`](../locale.md) を先に読んでください。

## 関数の詳しい説明

### std::ctype {#ctype}

```cpp
template <class CharT>
class ctype;  // is(), toupper(), tolower(), widen(), narrow() など
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `CharT` | 型 | 文字の型 |

- 戻り値: 分類・変換の関数をもつ
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <locale>
#include <print>

int main() {
  const auto& ct = std::use_facet<std::ctype<char>>(std::locale::classic());
  std::println("{}", ct.toupper('a'));
}
```

```text title="実行結果"
A
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ロケールごとの大文字小文字の変換 |

## よくあるミス

??? failure "日本語の変換を期待する"
    大文字小文字の概念がない文字は変換されません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`toupper`](../../numeric/cctype/toupper.md) | C の関数 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字の分類（数字か、英字か）と、大文字小文字の変換を担当するファセット
    - [x] ロケール（言語・地域ごとの規則）の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::ctype](https://cpprefjp.github.io/reference/locale/ctype.html)
- [cppreference: std::ctype](https://en.cppreference.com/w/cpp/locale/ctype)
