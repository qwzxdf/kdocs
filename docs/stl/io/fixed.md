---
title: std::fixed
summary: "小数を「固定小数点の形」（小数点以下の桁数を指定）で出力する。"
order: 80
tags:
  - 入出力・文字列
---

# std::fixed

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <ios>`
</div>

`std::fixed` は、**小数を固定小数点の形（`3.140000` のように、小数点以下の桁数をそろえる形）で出力する**マニピュレーターです。[`std::setprecision`](setprecision.md) と組み合わせて、小数点以下の桁数を指定します。**設定は残り続ける**ので注意します。新しいコードでは `std::println("{:.2f}", x)` が簡単です。

!!! tip "ポイント"
    - `std::cout << std::fixed << std::setprecision(2) << 3.14159;` → `3.14`。
    - `fixed` なしの `setprecision(2)` は、全体の有効桁数になる。
    - 新しいコードでは `{:.2f}`。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) などの出力ストリームの設定です。新しいコードでは [`std::println`](../utilities/print.md) の書式が簡単です。

## 関数の詳しい説明

### std::fixed {#fixed}

```cpp
std::ios_base& fixed(std::ios_base& str);
```

- 戻り値: `str`
- 計算量: O(1)

```cpp
#include <iomanip>
#include <iostream>

int main() {
  std::cout << std::fixed << std::setprecision(2) << 3.14159 << '\n';
}
```

```text title="実行結果"
3.14
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 古いコードで、小数点以下の桁数をそろえる | `std::cout << std::fixed << std::setprecision(1) << hp_rate;` |

## よくあるミス

??? failure "設定が残る"
    後の `double` の出力も固定小数点になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`setprecision`](setprecision.md) | 桁数を決める |
| [`std::println`](../utilities/print.md) | `{:.2f}` |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 固定小数点の形で出す
    - [x] setprecision と組み合わせる
    - [x] 設定が残る

## 関連ページ

- [cpprefjp: std::fixed](https://cpprefjp.github.io/reference/ios/fixed.html)
- [cppreference: std::fixed](https://en.cppreference.com/w/cpp/io/manip/fixed)
