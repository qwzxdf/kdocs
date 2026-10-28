---
title: std::get_money
summary: "金額を、ロケールの形式で入力する。"
order: 900
tags:
  - 入出力・文字列
---

# std::get_money

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <sstream>`
</div>

ロケールの通貨の書式で書かれた文字列を金額の数値として読み込みます。

!!! tip "ポイント"
    - ロケールの `money_get` の書式に従う。
    - 戻りは最小単位の整数。
    - `<iomanip>` が必要。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::get_money {#get_money}

```cpp
template <class MoneyT>
/* 実装定義 */ get_money(MoneyT& mon, bool intl = false);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `mon` | long double / string | 結果を入れる変数 |
| `intl` | bool | 省略可。国際表記にするか |

- 戻り値: ストリームへの参照
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <iomanip>
#include <locale>
#include <print>
#include <sstream>

int main() {
  std::istringstream in("123");
  in.imbue(std::locale::classic());
  long double v = 0;
  in >> std::get_money(v);
  std::println("{}", static_cast<int>(v));
}
```

```text title="実行結果"
123
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 出力の書式をストリームに設定する |

## よくあるミス

??? failure "ロケールの違いを考えない"
    国によって区切りや記号が違います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`put_money`](put_money.md) | 出力 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 金額をロケールの形式で入力する
    - [x] ロケールの `money_get` の書式に従う
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::get_money](https://cpprefjp.github.io/reference/ios/get_money.html)
- [cppreference: std::get_money](https://en.cppreference.com/w/cpp/io/manip/get_money)
