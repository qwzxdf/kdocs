---
title: std::towctrans
summary: "ワイド文字を、指定した変換で変換する。"
order: 900
group: <cwctype> のワイド文字の判定・変換
tags:
  - 数値
---

# std::towctrans

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cwctype>`
</div>

`towupper` などの固定の関数ではなく、`wctrans` で取った変換の値で、実行時に変換を選んで適用します。

!!! tip "ポイント"
    - `<cwctype>` の部品。
    - ロケールに依存する。
    - ふつうは `iswalpha` などの固定の関数を使う。

!!! info "このページを読む前に"
    [`std::iswalpha`](iswalpha.md) を先に読んでください。

## 関数の詳しい説明

### std::towctrans {#towctrans}

```cpp
std::wint_t towctrans(std::wint_t wc, std::wctrans_t desc);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `wc` | wint_t | 変換するワイド文字 |
| `desc` | wctrans_t | `wctrans` で取った変換 |

- 戻り値: 変換した文字
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cwctype>
#include <print>

int main() {
  std::println("{}", static_cast<char>(std::towctrans(L'a', std::wctrans("toupper"))));
}
```

```text title="実行結果"
A
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 実行時に分類・変換を選ぶ |

## よくあるミス

??? failure "名前を間違える"
    名前が不正だと 0 が返ります。0 を確かめてから使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`iswalpha`](iswalpha.md) | 固定の分類の関数 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ワイド文字を、指定した変換で変換する
    - [x] `<cwctype>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::towctrans](https://cpprefjp.github.io/reference/cwctype/towctrans.html)
- [cppreference: std::towctrans](https://en.cppreference.com/w/cpp/string/wide/towctrans)
