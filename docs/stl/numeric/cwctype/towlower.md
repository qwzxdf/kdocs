---
title: std::towlower
summary: "ワイド文字を小文字にする。"
order: 900
group: <cwctype> のワイド文字の判定・変換
tags:
  - 数値
---

# std::towlower

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwctype>`
</div>

`<cctype>` の `tolower` の、`wchar_t`（ワイド文字）版です。

!!! tip "ポイント"
    - `wint_t` を受け取って `wint_t` を返す。
    - ロケールで対象の文字が変わる。
    - `char` 版は `<cctype>`。

!!! info "このページを読む前に"
    [`std::isalpha`](../cctype/isalpha.md) を先に読んでください。

## 関数の詳しい説明

### std::towlower {#towlower}

```cpp
std::wint_t towlower(std::wint_t wc);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `wc` | wint_t | 変換するワイド文字 |

- 戻り値: 変換した文字（変換できなければそのまま）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cwctype>
#include <print>

int main() {
  std::println("{}", static_cast<char>(std::towlower(L'A')));
}
```

```text title="実行結果"
a
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | wchar_t の文字列の大文字小文字をそろえる |

## よくあるミス

??? failure "文字の数が変わる言語を考えない"
    ドイツ語の `ß` のように 1 文字が 2 文字になる変換はできません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`tolower`](../cctype/tolower.md) | char 版 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ワイド文字を小文字にする
    - [x] `wint_t` を受け取って `wint_t` を返す
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::towlower](https://cpprefjp.github.io/reference/cwctype/towlower.html)
- [cppreference: std::towlower](https://en.cppreference.com/w/cpp/string/wide/towlower)
