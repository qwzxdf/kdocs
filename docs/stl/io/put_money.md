---
title: std::put_money
summary: "金額を、ロケールの形式で出力する。"
order: 900
tags:
  - 入出力・文字列
---

# std::put_money

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <iostream>`
</div>

金額（整数の最小単位）をロケールに応じた通貨の書式で出力します。クラシックロケールでは、単なる数字になります。

!!! tip "ポイント"
    - ロケールの `money_put` の書式に従う。
    - `showbase` を付けると通貨記号も出る。
    - `<iomanip>` が必要。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::put_money {#put_money}

```cpp
template <class MoneyT>
/* 実装定義 */ put_money(const MoneyT& mon, bool intl = false);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `mon` | long double / string | 金額 |
| `intl` | bool | 省略可。国際表記にするか |

- 戻り値: ストリームへの参照
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <iomanip>
#include <iostream>
#include <locale>

int main() {
  std::cout.imbue(std::locale::classic());
  std::cout << std::put_money(12345.0L) << '\n';
}
```

```text title="実行結果"
12345
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 出力の書式をストリームに設定する |

## よくあるミス

??? failure "ロケールを設定しない"
    既定の `"C"` ロケールでは、通貨の区切りや記号は出ません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`get_money`](get_money.md) | 入力 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 金額をロケールの形式で出力する
    - [x] ロケールの `money_put` の書式に従う
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::put_money](https://cpprefjp.github.io/reference/ios/put_money.html)
- [cppreference: std::put_money](https://en.cppreference.com/w/cpp/io/manip/put_money)
