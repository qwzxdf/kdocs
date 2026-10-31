---
title: std::centi
summary: "SI 接頭辞「centi」（100 分の 1）を表す `ratio` の別名。"
order: 900
tags:
  - 数値
---

# std::centi

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <ratio>`
</div>

センチメートルや、1/100 秒（センチ秒）のように、100 分の 1 の単位を型として持ちたいときに、`std::centi`（センチ、100 分の 1）を使います。`ratio<1, 100>` の別名です。

!!! tip "ポイント"
    - 中身は `std::ratio<1, 100>`
    - `::num`（分子）と `::den`（分母）をコンパイル時の定数として取り出せる
    - `std::chrono::duration` の単位（第 2 テンプレート引数）として使う
    - 型の別名であり、関数ではない（値は持たない）

!!! info "このページを読む前に"
    [`<ratio>`](../ratio.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::centi {#centi}

<span class="ver ver-11">C++11</span>

```cpp
using centi = ratio<1, 100>;
```

`std::centi` は、`std::ratio<1, 100>` の別名で、値は 100 分の 1 を表します。`std::centi::num` が 1、`std::centi::den` が 100 で、いずれもコンパイル時の定数です。実行時のコストはありません。

`std::ratio` は分数を型で表す仕組みで、分子・分母は約分された形で保持されます。接頭辞の別名は、よく使う分数に名前を付けたものです。

単位の変換を型で表したいとき、この別名を `std::ratio_multiply` などと組み合わせて使えます。

分母や分子が `std::intmax_t` に収まらない接頭辞（`yotta`、`zetta` など）は、環境によっては定義されません。このページの `centi` は、64 ビットの範囲に収まるので、どの環境でも使えます。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>
#include <ratio>

int main() {
  // 1/100 秒刻みのタイマー (センチ秒)
  using CentiSecond = std::chrono::duration<int, std::centi>;
  CentiSecond lap{1234};
  std::println("{} センチ秒 = {:.2f} 秒", lap.count(), std::chrono::duration<double>(lap).count());

  // 長さ: メートルの 1/100 がセンチメートル
  double meters = 1.85;
  std::println("{} m = {} cm", meters, meters * std::centi::den / std::centi::num);
}
```

```text title="実行結果"
1234 センチ秒 = 12.34 秒
1.85 m = 185 cm
```

1234 センチ秒は 12.34 秒です。メートルをセンチメートルにするには、`centi` の分母を掛けます。

## ゲームでの使いどころ

レースゲームのラップタイムのように、1/100 秒まで表示する時間を、整数で持ちたいときに使えます。

## よくあるミス

??? failure "centi と milli を取り違える"
    `centi` は 1/100、`milli` は 1/1000 です。

??? failure "メートルからセンチメートルへの変換を逆にする"
    `centi` は 1/100 なので、メートルの値は 100 倍にします。割ると逆の換算になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ratio`](../ratio.md) | 分数を型で表す基本の仕組み |
| [`std::chrono::duration`](../../utilities/chrono/duration.md) | 時間を単位つきで表す |

## コンパイラ対応

C++11 から使えます。`<ratio>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::centi` は `ratio<1, 100>` の別名（100 分の 1）
    - [x] `::num` と `::den` が定数として取れる
    - [x] `duration` の単位などに使う

## 関連ページ

- [cpprefjp: std::centi](https://cpprefjp.github.io/reference/ratio/ratio.html)
- [cppreference: std::centi](https://en.cppreference.com/w/cpp/numeric/ratio/ratio)
