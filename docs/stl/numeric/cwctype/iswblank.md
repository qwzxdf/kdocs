---
title: std::iswblank
summary: "ワイド文字が空白かタブかを調べる。"
order: 900
group: <cwctype> のワイド文字の判定・変換
tags:
  - 数値
---

# std::iswblank

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwctype>`
</div>

Windows の API や、ワイド文字列（`wchar_t`）を扱うコードで、文字の種類を調べたくなります。`<cctype>` の `std::isblank` は 1 バイトの `char` 用で、`wchar_t` には使えません。`std::iswblank` は、その<strong>ワイド文字版</strong>で、文字が空白かタブかを調べます。

!!! tip "ポイント"
    - 調べる対象は、半角スペースまたはタブ
    - 戻り値は `int`。条件を満たせば 0 以外、満たさなければ 0
    - 引数は `wint_t`。`wchar_t` の文字をそのまま渡せる
    - `char` 版は `<cctype>` の `std::isblank`

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::iswblank {#iswblank}

```cpp
int iswblank(std::wint_t wc);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `wc` | `wint_t` | 調べるワイド文字。`WEOF` も渡せる |

戻り値は、`wc` が上の条件に当てはまれば 0 以外、当てはまらなければ 0 です。真偽値として条件式に書けますが、型は `int` なので、`!= 0` で比べます。

`char` 版（`isalpha` など）と違い、引数を `unsigned char` にキャストする必要はありません。`wint_t` は `wchar_t` を含む型だからです。

判定の基準はロケールで決まります。既定の "C" ロケールでは ASCII の範囲だけが対象です。日本語の環境で `setlocale` を呼ぶと、Windows では `iswalpha(L'あ')` が真になるなど、結果が変わります。ロケールに依存する結果は、環境をまたぐとずれるため、判定の結果を保存するデータに使うときは注意が要ります。

Windows の `wchar_t` は 16 ビットで、UTF-16 のコード単位を表します。絵文字のようにサロゲートペア（2 つのコード単位）で表される文字は、1 つの `wchar_t` では判定できません。

## 実際に動かしてみる

```cpp
#include <cwctype>
#include <print>

int main() {
  std::println("iswblank(L' ') = {}", std::iswblank(L' ') != 0);
  std::println("iswblank(L'a') = {}", std::iswblank(L'a') != 0);
  std::println("iswblank(L'5') = {}", std::iswblank(L'5') != 0);
}
```

```text title="実行結果"
iswblank(L' ') = true
iswblank(L'a') = false
iswblank(L'5') = false
```

## ゲームでの使いどころ

ワイド文字列を直接解析する処理で使います。現代のゲームでは、文字列は UTF-8 の `std::string` で持つのが一般的で、`wchar_t` を使うのは Windows API に渡す境界に限られます。

```cpp
// Windows のパス（wchar_t）の先頭が英字か
if (std::iswblank(path[0])) { /* ドライブ文字 */ }
```

## よくあるミス

??? failure "UTF-16 のサロゲートペアを 1 文字として判定する"
    2 つのコード単位で 1 文字です。Unicode 対応のライブラリを使います。

??? failure "ロケールに依存した結果を、他の環境と比べる"
    同じ入力でも環境で結果が違います。ASCII の判定に限るなら `<cctype>` で足ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::isblank`](../cctype/isblank.md) | `char` 版 |
| [`iswalpha`](iswalpha.md) | 英字か |
| [`iswdigit`](iswdigit.md) | 数字か |

## コンパイラ対応

C++98 から使えます（C 言語由来）。`<cwctype>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `iswblank` は文字が空白かタブか
    - [x] `<cctype>` の `isblank` のワイド文字版
    - [x] 戻り値は `int`（0 以外が真）。ロケールに依存する

## 関連ページ

- [cpprefjp: std::iswblank](https://cpprefjp.github.io/reference/cwctype/iswblank.html)
- [cppreference: std::iswblank](https://en.cppreference.com/w/cpp/string/wide/iswblank)
