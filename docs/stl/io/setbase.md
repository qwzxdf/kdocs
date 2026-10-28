---
title: std::setbase
summary: "整数の基数（8・10・16）を設定する。"
order: 900
tags:
  - 入出力・文字列
---

# std::setbase

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iostream>`
</div>

`hex`、`dec`、`oct` は、基数をそれぞれ名前で選びます。変数で基数を切り替えたい（ユーザーが選んだ表示形式に従う）ときは、数値で指定できる `std::setbase` が便利です。

!!! tip "ポイント"
    - `std::setbase(16)` は `std::hex` と同じ。8 と 10 も使える
    - それ以外の数を渡すと、10 進数になる（出力）
    - 入力では `setbase(0)` が特別で、接頭辞から基数を自動判定する
    - `<iomanip>` が必要

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::setbase {#setbase}

```cpp
/* 未規定 */ setbase(int base);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `base` | `int` | 基数。8、10、16 のいずれか。ほかの値は 10 進数になる |

出力では、`8`、`10`、`16` のどれかを受け付けます。2 進数は指定できません。2 進数で出したいときは、`std::bitset` を使うか、`std::format("{:b}", n)` を使います。

入力では、`0` を渡すと、接頭辞による自動判定になります。`0x1F` は 16 進数、`017` は 8 進数、`17` は 10 進数として読まれます。設定ファイルから、基数の決まっていない数値を読むときに便利です。

使うには `<iomanip>` が必要です。`hex` などは `<ios>` に入っているのと、違う点です。

## 実際に動かしてみる

```cpp
#include <iomanip>
#include <iostream>
#include <sstream>

int main() {
  std::cout << std::setbase(16) << 255 << '\n';   // ff
  std::cout << std::setbase(8) << 255 << '\n';    // 377
  std::cout << std::setbase(10) << 255 << '\n';   // 255

  // 入力: 0 を指定すると、接頭辞で判定する
  std::istringstream in("0x1F 017 17");
  int a, b, c;
  in >> std::setbase(0) >> a >> b >> c;
  std::cout << a << ' ' << b << ' ' << c << '\n';
}
```

```text title="実行結果"
ff
377
255
31 15 17
```

## ゲームでの使いどころ

ユーザーが表示形式を選べるツール（メモリ ビューアーなど）で、基数を変数で切り替えるときに使います。設定ファイルで、数値が 10 進数なのか 16 進数なのかが混在する場合の読み込みにも使えます。

## よくあるミス

??? failure "2 進数を指定して、10 進数になる"
    `setbase` は 8、10、16 だけです。2 進数は `bitset` か `std::format` を使います。

??? failure "`<iomanip>` を include し忘れてコンパイル エラー"
    `hex` などと違い、`<iomanip>` が必要です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`hex`](hex.md) | 16 進数にする |
| [`dec`](dec.md) | 10 進数にする |
| [`oct`](oct.md) | 8 進数にする |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 基数を数値で指定する
    - [x] 入力では `0` で自動判定
    - [x] `<iomanip>` が要る

## 関連ページ

- [cpprefjp: std::setbase](https://cpprefjp.github.io/reference/ios/setbase.html)
- [cppreference: std::setbase](https://en.cppreference.com/w/cpp/io/manip/setbase)
