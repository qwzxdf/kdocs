---
title: std::showpoint
summary: "小数の出力に、小数点と末尾の 0 を必ず付ける。"
order: 900
tags:
  - 入出力・文字列
---

# std::showpoint

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iostream>`
</div>

`3.0` と出したいのに、`std::cout << 3.0` は `3` と出ます。小数点以下が全部 0 のとき、小数点も 0 も省かれるからです。`std::showpoint` は、<strong>小数点と、末尾の 0 を必ず出す</strong>操作子です。

!!! tip "ポイント"
    - `std::showpoint` で、`3` が `3.00000` のように、小数点と精度の桁数ぶんの 0 を付けて出る
    - 既定の書式（`defaultfloat`）で、精度の桁数までを出す
    - `fixed` では、もともと小数点が付く
    - 設定は残る。戻すには `std::noshowpoint`

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::showpoint {#showpoint}

```cpp
std::ios_base& showpoint(std::ios_base& str);
```

既定の書式では、浮動小数点数の末尾の 0 は省かれ、整数と同じ値なら小数点も出ません。`showpoint` を立てると、精度で決まる桁数まで 0 を出して、小数点も必ず出します。

`std::cout << std::showpoint << 3.0` は、既定の精度 6（有効数字）なので `3.00000` です。有効数字の桁数分が出る点に注意します。小数点以下の桁数を決めたいときは、`fixed` と `setprecision` を使います。

整数型には効きません。

## 実際に動かしてみる

```cpp
#include <iostream>

int main() {
  std::cout << 3.0 << '\n';                          // 3
  std::cout << std::showpoint << 3.0 << '\n';        // 3.00000
  std::cout << 2.5 << '\n';                          // 2.50000
  std::cout << std::noshowpoint << 2.5 << '\n';      // 2.5
}
```

```text title="実行結果"
3
3.00000
2.50000
2.5
```

## ゲームでの使いどころ

小数であることを、見た目ではっきりさせたいときに使います。桁をそろえる目的なら、`fixed` と `setprecision` のほうが確実です。

## よくあるミス

??? failure "`showpoint` で小数点以下 2 桁が出ると期待する"
    出るのは有効数字の桁数です。小数点以下の桁数は `fixed` と `setprecision` で決めます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fixed`](fixed.md) | 固定小数点にする |
| [`setprecision`](setprecision.md) | 桁数を決める |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 小数点と末尾の 0 を必ず出す
    - [x] 有効数字の桁数まで出る
    - [x] 戻すのは `noshowpoint`

## 関連ページ

- [cpprefjp: std::showpoint](https://cpprefjp.github.io/reference/ios/showpoint.html)
- [cppreference: std::showpoint](https://en.cppreference.com/w/cpp/io/manip/showpoint)
