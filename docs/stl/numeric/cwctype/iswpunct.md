---
title: std::iswpunct
summary: "ワイド文字が記号かを調べる。"
order: 900
group: <cwctype> のワイド文字の判定・変換
tags:
  - 数値
---

# std::iswpunct

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwctype>`
</div>

`<cctype>` の `ispunct` の、`wchar_t`（ワイド文字）版です。Windows の API の `wchar_t` 文字列を扱うときに使います。ロケールによって、ASCII 以外の文字の扱いが変わります。

!!! tip "ポイント"
    - `wint_t` を受け取り、真なら 0 以外を返す。
    - ロケールの設定で、日本語などの判定が変わる。
    - `char` 版は `<cctype>`。

!!! info "このページを読む前に"
    [`std::isalpha`](../cctype/isalpha.md) を先に読んでください。

## 関数の詳しい説明

### std::iswpunct {#iswpunct}

```cpp
int iswpunct(std::wint_t wc);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `wc` | wint_t | 調べるワイド文字 |

- 戻り値: 条件に合えば 0 以外、合わなければ 0
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cwctype>
#include <print>

int main() {
  std::println("{}", std::iswpunct(L'!') != 0);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | wchar_t 文字列の検査 |

## よくあるミス

??? failure "ロケールを設定せずに日本語を渡す"
    既定の `"C"` ロケールでは ASCII 以外の判定が使えません。`std::setlocale` を呼びます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ispunct`](../cctype/isalpha.md) | char 版 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ワイド文字が記号かを調べる
    - [x] `wint_t` を受け取り、真なら 0 以外を返す
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::iswpunct](https://cpprefjp.github.io/reference/cwctype/iswpunct.html)
- [cppreference: std::iswpunct](https://en.cppreference.com/w/cpp/string/wide/iswpunct)
