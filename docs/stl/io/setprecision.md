---
title: std::setprecision
summary: "小数の桁数を決める。"
order: 77
tags:
  - 入出力・文字列
---

# std::setprecision

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <iomanip>`
</div>

`std::setprecision(n)` は、**小数を出すときの桁数**を決めるマニピュレーターです。`std::fixed` と組み合わせると「小数点以下 n 桁」、単独だと「全体で n 桁（有効数字）」になります。**一度指定すると、以降ずっと有効**です。

!!! tip "ポイント"
    - `std::fixed` を付けると、小数点以下の桁数になる。
    - 指定は残り続ける。元に戻すには、元の設定を保存して復元する。
    - 新しいコードは `std::println("{:.2f}", x)`。

## 関数の詳しい説明

### std::setprecision {#setprecision}

```cpp
/* unspecified */ setprecision(int n);  // <iomanip>
```

- 浮動小数点の桁数。`std::fixed` と一緒に使うと「小数点以下 n 桁」、単独だと「全体で n 桁」。**以後ずっと**効きます

## 実際に動かしてみる

```cpp
#include <iomanip>
#include <iostream>

int main() {
  std::cout << std::setprecision(3) << 3.14159 << "\n";   // 有効数字 3 桁
}
```

```text title="実行結果"
3.14
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ステータス表を桁をそろえて出す | `std::cout << std::setprecision(...)` |

## よくあるミス

??? failure "指定が残り続けて、後の出力が崩れる"
    設定は出力の状態に残ります。出力の最後に、元に戻します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::println`](../utilities/print.md) | 書式 `{:>6}` `{:.2f}` `{:03}` で同じことができる |
| [`std::cout`](cout.md) | 出力先 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 小数の桁数を決める。
    - [x] 一部は設定が残り続ける
    - [x] 新しいコードは `println`

## 関連ページ

- [cpprefjp: std::setprecision](https://cpprefjp.github.io/reference/iomanip/setprecision.html)
- [cppreference: std::setprecision](https://en.cppreference.com/w/cpp/io/manip/setprecision)
