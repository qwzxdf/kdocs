---
title: std::lconv
summary: "数値と通貨の書式情報をまとめた構造体。"
order: 900
tags:
  - 入出力・文字列
---

# std::lconv

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <clocale>`
</div>

`localeconv()` が返す構造体です。`decimal_point`（小数点）、`thousands_sep`（桁区切り）、`grouping`（桁のグループ）、`currency_symbol`（通貨記号）などのメンバをもちます。

!!! tip "ポイント"
    - ロケール（言語・地域ごとの規則）の部品。
    - ふつうは `std::locale` 経由で使う。
    - ゲームのローカライズでは、書式（日付・数字）に関わる。

!!! info "このページを読む前に"
    [`std::locale`](../locale.md) を先に読んでください。

## 関数の詳しい説明

### std::lconv {#lconv}

```cpp
struct lconv {
  char* decimal_point;
  char* thousands_sep;
  char* grouping;
  char* currency_symbol;
  // ...
};
```

- 戻り値: なし（構造体）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <clocale>
#include <print>

int main() {
  const std::lconv* lc = std::localeconv();
  std::println("{}", lc->thousands_sep[0] == '\0');
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 桁区切りが設定されているかを調べる |

## よくあるミス

??? failure "文字列として保存せず、ポインタを保持する"
    ポインタは、次の `setlocale` で無効になります。必要ならコピーします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`localeconv`](localeconv.md) | 取得する関数 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 数値と通貨の書式情報をまとめた構造体
    - [x] ロケール（言語・地域ごとの規則）の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::lconv](https://cpprefjp.github.io/reference/locale/lconv.html)
- [cppreference: std::lconv](https://en.cppreference.com/w/cpp/locale/lconv)
