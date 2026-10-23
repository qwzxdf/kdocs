---
title: std::wctype
summary: "分類の名前から、wctype_t を取得する。"
order: 900
group: <cwctype> のワイド文字の判定・変換
tags:
  - 数値
---

# std::wctype

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cwctype>`
</div>

`"alpha"`・`"digit"`・`"upper"` などの名前から、分類を表す値を取り出します。`iswctype` と組み合わせて、実行時に分類を選べます。

!!! tip "ポイント"
    - `<cwctype>` の部品。
    - ロケールに依存する。
    - ふつうは `iswalpha` などの固定の関数を使う。

!!! info "このページを読む前に"
    [`std::iswalpha`](iswalpha.md) を先に読んでください。

## 関数の詳しい説明

### std::wctype {#wctype}

```cpp
std::wctype_t wctype(const char* property);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `property` | const char* | 分類の名前（`"alpha"` など） |

- 戻り値: 分類を表す値。名前が不正なら 0
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cwctype>
#include <print>

int main() {
  std::println("{}", std::wctype("alpha") != 0);
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
    - [x] 分類の名前から、wctype_t を取得する
    - [x] `<cwctype>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::wctype](https://cpprefjp.github.io/reference/cwctype/wctype.html)
- [cppreference: std::wctype](https://en.cppreference.com/w/cpp/string/wide/wctype)
