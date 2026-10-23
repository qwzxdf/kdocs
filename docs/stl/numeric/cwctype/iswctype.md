---
title: std::iswctype
summary: "ワイド文字が、指定した分類に属するかを調べる。"
order: 900
group: <cwctype> のワイド文字の判定・変換
tags:
  - 数値
---

# std::iswctype

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cwctype>`
</div>

`iswalpha` などの固定の関数ではなく、`wctype` で取った分類の値で、実行時に分類を選んで判定します。

!!! tip "ポイント"
    - `<cwctype>` の部品。
    - ロケールに依存する。
    - ふつうは `iswalpha` などの固定の関数を使う。

!!! info "このページを読む前に"
    [`std::iswalpha`](iswalpha.md) を先に読んでください。

## 関数の詳しい説明

### std::iswctype {#iswctype}

```cpp
int iswctype(std::wint_t wc, std::wctype_t desc);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `wc` | wint_t | 調べるワイド文字 |
| `desc` | wctype_t | `wctype` で取った分類 |

- 戻り値: 属していれば 0 以外
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cwctype>
#include <print>

int main() {
  std::println("{}", std::iswctype(L'a', std::wctype("alpha")) != 0);
}
```

```text title="実行結果"
true
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
    - [x] ワイド文字が、指定した分類に属するかを調べる
    - [x] `<cwctype>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::iswctype](https://cpprefjp.github.io/reference/cwctype/iswctype.html)
- [cppreference: std::iswctype](https://en.cppreference.com/w/cpp/string/wide/iswctype)
