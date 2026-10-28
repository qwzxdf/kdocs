---
title: std::wctype_t
summary: "ワイド文字の分類の種類を表す型。"
order: 900
group: <cwctype> のワイド文字の判定・変換
tags:
  - 数値
---

# std::wctype_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cwctype>`
</div>

`std::wctype` が返す、文字の分類を表す値の型が `std::wctype_t` です。`iswctype` に渡して使います。

!!! tip "ポイント"
    - `wctype` の戻り値の型
    - 中身は環境依存の整数型（値の意味は触らない）
    - 0 は「無効な分類」
    - `iswctype` に渡して使う

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::wctype_t {#wctype_t}

```cpp
using wctype_t = /* 環境依存の整数型 */;
```

`std::wctype_t` は、文字の分類（英字、数字など）を識別する値を保持する型で、実体は環境の整数型です。値の中身に意味はなく、`std::wctype` が返した値をそのまま `std::iswctype` に渡すだけです。

比較できるのは 0 だけです。`wctype("unknown")` のように、名前が正しくない場合に 0 を返すので、`!= 0` で有効か確かめます。

値同士の大小や、数値としての計算には意味がありません。

## 実際に動かしてみる

```cpp
#include <cwctype>
#include <print>

int main() {
  std::wctype_t cat = std::wctype("alpha");
  std::println("有効な分類: {}", cat != 0);
}
```

```text title="実行結果"
有効な分類: true
```

## ゲームでの使いどころ

`wctype` の戻り値を保持する変数の型として登場します。

```cpp
std::wctype_t category = std::wctype("digit");   // 保持して、何度も使う
```

## よくあるミス

??? failure "値を計算に使おうとする"
    値の意味は環境依存です。0 かどうかを確かめるだけにします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`wctype`](wctype.md) | 分類を得る関数 |
| [`wctrans_t`](wctrans_t.md) | 変換を表す型 |

## コンパイラ対応

C++98 から使えます（C 言語由来）。`<cwctype>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `wctype_t` は文字の分類を表す型
    - [x] `wctype` の戻り値を保持して `iswctype` に渡す
    - [x] 0 は無効

## 関連ページ

- [cpprefjp: std::wctype_t](https://cpprefjp.github.io/reference/cwctype/wctype_t.html)
- [cppreference: std::wctype_t](https://en.cppreference.com/w/cpp/string/wide/wctype_t)
