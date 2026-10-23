---
title: std::wctrans_t
summary: "ワイド文字の変換の種類を表す型。"
order: 900
group: <cwctype> のワイド文字の判定・変換
tags:
  - 数値
---

# std::wctrans_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cwctype>`
</div>

`std::wctrans` が返す、文字の変換を表す値の型が `std::wctrans_t` です。`towctrans` に渡して使います。

!!! tip "ポイント"
    - `wctrans` の戻り値の型
    - 中身は環境依存の整数型（値の意味は触らない）
    - 0 は「無効な変換」
    - `towctrans` に渡して使う

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::wctrans_t {#wctrans_t}

```cpp
using wctrans_t = /* 環境依存の整数型 */;
```

`std::wctrans_t` は、文字の変換（小文字化、大文字化）を識別する値を保持する型で、実体は環境の整数型です。値の中身に意味はなく、`std::wctrans` が返した値を、そのまま `std::towctrans` に渡します。

0 と比べて、有効かを確かめる以外の使い方はありません。

## 実際に動かしてみる

```cpp
#include <cwctype>
#include <print>

int main() {
  std::wctrans_t t = std::wctrans("tolower");
  std::println("有効な変換: {}", t != 0);
}
```

```text title="実行結果"
有効な変換: true
```

## ゲームでの使いどころ

`wctrans` の戻り値を保持する変数の型として登場します。

```cpp
std::wctrans_t to_lower = std::wctrans("tolower");
```

## よくあるミス

??? failure "値を計算に使おうとする"
    0 かどうかを確かめるだけにします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`wctrans`](wctrans.md) | 変換を得る関数 |
| [`wctype_t`](wctype_t.md) | 分類を表す型 |

## コンパイラ対応

C++98 から使えます（C 言語由来）。`<cwctype>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `wctrans_t` は文字の変換を表す型
    - [x] `wctrans` の戻り値を保持して `towctrans` に渡す
    - [x] 0 は無効

## 関連ページ

- [cpprefjp: std::wctrans_t](https://cpprefjp.github.io/reference/cwctype/wctrans_t.html)
- [cppreference: std::wctrans_t](https://en.cppreference.com/w/cpp/string/wide/wctrans_t)
