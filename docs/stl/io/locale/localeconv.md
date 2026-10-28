---
title: std::localeconv
summary: "現在のロケールの数値・通貨の書式情報を取得する。"
order: 900
tags:
  - 入出力・文字列
---

# std::localeconv

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <clocale>`
</div>

C のロケールに設定されている、小数点記号・桁区切り・通貨記号などを `lconv` 構造体で取得します。

!!! tip "ポイント"
    - ロケール（言語・地域ごとの規則）の部品。
    - ふつうは `std::locale` 経由で使う。
    - ゲームのローカライズでは、書式（日付・数字）に関わる。

!!! info "このページを読む前に"
    [`std::locale`](../locale.md) を先に読んでください。

## 関数の詳しい説明

### std::localeconv {#localeconv}

```cpp
std::lconv* localeconv();
```

- 戻り値: `lconv` へのポインタ（書き換え禁止）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <clocale>
#include <print>

int main() {
  std::println("{}", std::localeconv()->decimal_point);
}
```

```text title="実行結果"
.
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ロケールの小数点記号を調べる |

## よくあるミス

??? failure "戻り値を書き換える"
    戻り値は読み取り専用です。次の `setlocale` で書き換わります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`lconv`](lconv.md) | 構造体 |
| [`setlocale`](setlocale.md) | ロケールを設定する |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 現在のロケールの数値・通貨の書式情報を取得する
    - [x] ロケール（言語・地域ごとの規則）の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::localeconv](https://cpprefjp.github.io/reference/locale/localeconv.html)
- [cppreference: std::localeconv](https://en.cppreference.com/w/cpp/locale/localeconv)
