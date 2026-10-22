---
title: std::scientific
summary: "浮動小数を指数表記（`1.5e+03`）で出す。"
order: 85
tags:
  - 入出力・文字列
---

# std::scientific

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <ios>`
</div>

非常に大きい、または小さい数は、`1500` よりも `1.5e+03` のほうが桁を読み取りやすくなります。`std::scientific` を流すと、浮動小数が指数表記になります。小数点以下の桁数は `setprecision` で決めます。

!!! tip "ポイント"
    - `scientific` で `d.ddde+xx` の形。
    - 桁数は `setprecision`。
    - 新しいコードは `println("{:.2e}", x)`。

## 関数の詳しい説明

### std::scientific {#scientific}

```cpp
ios_base& scientific(ios_base& str);
```

- 浮動小数を指数表記にします

## 実際に動かしてみる

```cpp
#include <iomanip>
#include <iostream>

int main() {
  std::cout << std::scientific << std::setprecision(2) << 1500.0 << "\n";
}
```

```text title="実行結果"
1.50e+03
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 物理量の桁を見る | `std::cout << std::scientific` |

## よくあるミス

??? failure "桁数が合わない"
    `setprecision` は、`scientific` のときは小数点以下の桁数になります。通常の表示とは意味が違います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::println`](../utilities/print.md) | 書式指定で同じことができる |
| [`std::fixed`](fixed.md) | 固定小数点表記 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 指数表記にするマニピュレーター。
    - [x] 桁数は `setprecision`。
    - [x] 新しいコードは `{:e}`。

## 関連ページ

- [cpprefjp: std::scientific](https://cpprefjp.github.io/reference/ios/scientific.html)
- [cppreference: std::scientific](https://en.cppreference.com/w/cpp/io/manip/fixed)
