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

`iswctype` に渡す、「どの分類か」を表す型です。`wctype("alpha")` で作ります。ロケールごとの独自の分類を使いたいときに使います。

!!! tip "ポイント"
    - `<cwctype>` の部品。
    - ロケールに依存する。
    - ふつうは `iswalpha` などの固定の関数を使う。

!!! info "このページを読む前に"
    [`std::iswalpha`](iswalpha.md) を先に読んでください。

## 関数の詳しい説明

### std::wctype_t {#wctype_t}

```cpp
using wctype_t = /* 実装定義 */;
```

- 戻り値: なし（型）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cwctype>
#include <print>

int main() {
  std::wctype_t t = std::wctype("alpha");
  std::println("{}", t != 0);
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
    - [x] ワイド文字の分類の種類を表す型
    - [x] `<cwctype>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::wctype_t](https://cpprefjp.github.io/reference/cwctype/wctype_t.html)
- [cppreference: std::wctype_t](https://en.cppreference.com/w/cpp/string/wide/wctype_t)
