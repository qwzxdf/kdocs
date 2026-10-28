---
title: std::showpos
summary: "正の数の出力に、`+` を付ける。"
order: 900
tags:
  - 入出力・文字列
---

# std::showpos

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iostream>`
</div>

ダメージの増減を「+10」「-5」のように、符号つきで表示したい。`std::cout << 10` は `10` と出て、プラスの符号は付きません。`std::showpos` は、<strong>0 以上の数値にも `+` を付けて</strong>出します。

!!! tip "ポイント"
    - `std::showpos` で、正の数や 0 に `+` を付けて出す
    - 負の数は、いつも `-` が付く
    - 設定は残る。戻すには `std::noshowpos`
    - 整数にも浮動小数点数にも効く

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::showpos {#showpos}

```cpp
std::ios_base& showpos(std::ios_base& str);
```

`showpos` フラグを立てます。0 以上の数値を出力するとき、先頭に `+` を付けます。0 も `+0` になります。

増減を表す値（ダメージ、回復量、補正値、ゲージの変化）の表示で、符号が見えると、意味が伝わりやすくなります。

`hex` と組み合わせた場合、符号つきの数値の 16 進表記は、環境によって扱いが異なります。符号の付く 10 進数に使うのが無難です。

`noshowpos` で元に戻します。C++20 の `std::format("{:+}", n)` も、同じ表示ができます。

## 実際に動かしてみる

```cpp
#include <iostream>

int main() {
  std::cout << std::showpos;
  std::cout << 10 << ' ' << -5 << ' ' << 0 << ' ' << 2.5 << '\n';
  std::cout << std::noshowpos << 10 << '\n';
}
```

```text title="実行結果"
+10 -5 +0 +2.5
10
```

## ゲームでの使いどころ

ダメージ表示の「+12」「-3」、補正値の表示、差分の表示などで使います。増えたのか減ったのかが、符号で分かります。

## よくあるミス

??? failure "戻し忘れて、他の数値にも `+` が付く"
    `noshowpos` で戻します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`showbase`](showbase.md) | 基数の印を付ける |
| [`showpoint`](showpoint.md) | 小数点を必ず出す |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 正の数にも `+` を付ける
    - [x] 設定は残る
    - [x] 戻すのは `noshowpos`

## 関連ページ

- [cpprefjp: std::showpos](https://cpprefjp.github.io/reference/ios/showpos.html)
- [cppreference: std::showpos](https://en.cppreference.com/w/cpp/io/manip/showpos)
