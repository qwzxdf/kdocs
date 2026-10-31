---
title: std::iswprint
summary: "ワイド文字が表示できる文字かを調べる。"
order: 900
group: <cwctype> のワイド文字の判定・変換
tags:
  - 数値
---

# std::iswprint

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwctype>`
</div>

Windows の API や、ワイド文字列（`wchar_t`）を扱うコードで、文字の種類を調べたくなります。`<cctype>` の `std::isprint` は 1 バイトの `char` 用で、`wchar_t` には使えません。`std::iswprint` は、その<strong>ワイド文字版</strong>で、文字が表示できる文字か（空白を含む）を調べます。

!!! tip "ポイント"
    - 調べる対象は、表示できる文字（空白を含む）
    - 戻り値は `int`。条件を満たせば 0 以外、満たさなければ 0
    - 引数は `wint_t`。`wchar_t` の文字をそのまま渡せる
    - `char` 版は `<cctype>` の `std::isprint`

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::iswprint {#iswprint}

```cpp
int iswprint(std::wint_t wc);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `wc` | `wint_t` | 調べるワイド文字。`WEOF` も渡せる |

戻り値は、`wc` が条件に当てはまれば 0 以外、当てはまらなければ 0 です。真偽値として条件式に書けますが、型は `int` なので、`!= 0` で比べます。

`char` 版（`isalpha` など）と違い、引数を `unsigned char` にキャストする必要はありません。`wint_t` は `wchar_t` を含む型だからです。

判定の基準はロケールで決まります。既定の "C" ロケールでは ASCII の範囲だけが対象です。日本語の環境で `setlocale` を呼ぶと、Windows では `iswalpha(L'あ')` が真になるなど、結果が変わります。ロケールに依存する結果は、環境をまたぐとずれるため、判定の結果を保存するデータに使うときは注意が要ります。

Windows の `wchar_t` は 16 ビットで、UTF-16 のコード単位を表します。絵文字のようにサロゲートペア（2 つのコード単位）で表される文字は、1 つの `wchar_t` では判定できません。

## 実際に動かしてみる

```cpp
#include <cwctype>
#include <print>

int main() {
  std::println("iswprint(L'A') = {}", std::iswprint(L'A') != 0);
  std::println("iswprint(L' ') = {}", std::iswprint(L' ') != 0);
  std::println("iswprint(L'5') = {}", std::iswprint(L'5') != 0);
}
```

```text title="実行結果"
iswprint(L'A') = true
iswprint(L' ') = true
iswprint(L'5') = true
```

## ゲームでの使いどころ

16 進ダンプの、文字を並べる欄を作ります。表示できる文字はそのまま、それ以外は `.` にします。ワイド文字列（`std::wstring`）を直接扱うのは、Windows API との境界に限られます。

```cpp
wchar_t DumpChar(wchar_t c) { return std::iswprint(c) ? c : L'.'; }
```

## よくあるミス

??? failure "UTF-16 のサロゲートペアを 1 文字として判定する"
    2 つのコード単位で 1 文字です。1 つの `wchar_t` では判定できません。Unicode 対応のライブラリを使います。

??? failure "UTF-8 の日本語を、表示できる文字だと思う"
    128 以上のバイトは、`isprint` が偽です。日本語の UTF-8 のダンプは、1 バイトずつ `.` になります。

??? failure "ロケールに依存した結果を、他の環境と比べる"
    同じ入力でも環境で結果が違います。ASCII の判定に限るなら `<cctype>` で足ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::isprint`](../cctype/isprint.md) | `char` 版 |
| [`iswgraph`](iswgraph.md) | 見える文字か（スペースを除く） |
| [`iswcntrl`](iswcntrl.md) | 制御文字か |

## コンパイラ対応

C++98 から使えます（C 言語由来）。`<cwctype>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `iswprint` は文字が表示できる文字か（空白を含む）
    - [x] `<cctype>` の `isprint` のワイド文字版
    - [x] 戻り値は `int`（0 以外が真）。ロケールに依存する

## 関連ページ

- [cpprefjp: std::iswprint](https://cpprefjp.github.io/reference/cwctype/iswprint.html)
- [cppreference: std::iswprint](https://en.cppreference.com/w/cpp/string/wide/iswprint)
