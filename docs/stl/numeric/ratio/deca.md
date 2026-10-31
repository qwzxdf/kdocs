---
title: std::deca
summary: "SI 接頭辞「deca」（10 倍）を表す `ratio` の別名。"
order: 900
tags:
  - 数値
---

# std::deca

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <ratio>`
</div>

ウェーブの間隔を「10 秒ごと」で数えたい、マップを 10 マス単位でまとめたい。10 倍の単位を型として持ちたいときに、`std::deca`（デカ、10 倍）を使います。`ratio<10, 1>` の別名です。

!!! tip "ポイント"
    - 中身は `std::ratio<10, 1>`
    - `::num`（分子）と `::den`（分母）をコンパイル時の定数として取り出せる
    - `std::chrono::duration` の単位（第 2 テンプレート引数）として使う
    - 型の別名であり、関数ではない（値は持たない）

!!! info "このページを読む前に"
    [`<ratio>`](../ratio.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::deca {#deca}

<span class="ver ver-11">C++11</span>

```cpp
using deca = ratio<10, 1>;
```

`std::deca` は、`std::ratio<10, 1>` の別名で、値は 10 倍 を表します。`std::deca::num` が 10、`std::deca::den` が 1 で、いずれもコンパイル時の定数です。実行時のコストはありません。

`std::ratio` は分数を型で表す仕組みで、分子・分母は約分された形で保持されます。接頭辞の別名は、よく使う分数に名前を付けたものです。

単位の変換を型で表したいとき、この別名を `std::ratio_multiply` などと組み合わせて使えます。

分母や分子が `std::intmax_t` に収まらない接頭辞（`yotta`、`zetta` など）は、環境によっては定義されません。このページの `deca` は、64 ビットの範囲に収まるので、どの環境でも使えます。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>
#include <ratio>

int main() {
  using TenSeconds = std::chrono::duration<int, std::deca>;   // 1 単位が 10 秒の時間

  TenSeconds wave{3};
  auto sec = std::chrono::duration_cast<std::chrono::seconds>(wave);
  std::println("3 単位は {} 秒", sec.count());
  std::println("deca = {}/{}", std::deca::num, std::deca::den);
}
```

```text title="実行結果"
3 単位は 30 秒
deca = 10/1
```

`duration` の第 2 引数に渡すと、「1 刻みが 10 秒」の型になります。秒への換算は、`duration_cast` が `ratio` の掛け算でコンパイル時に決めます。

## ゲームでの使いどころ

「10 秒ごとにウェーブが来る」のような、10 の倍数のタイマーを、別の単位の型として表せます。ただし、`deca` を使う場面は少なく、`std::chrono::seconds` の倍数として、`10s` と書くほうが、普通は読みやすくなります。

## よくあるミス

??? failure "deca と deci を取り違える"
    `deca` は 10 倍、`deci` は 1/10 です。名前が似ているので、`num` と `den` で値を確かめます。

??? failure "duration の 1 単位の長さを忘れる"
    `duration<int, std::deca>{3}` は 3 秒ではなく、30 秒です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ratio`](../ratio.md) | 分数を型で表す基本の仕組み |
| [`std::chrono::duration`](../../utilities/chrono/duration.md) | 時間を単位つきで表す |

## コンパイラ対応

C++11 から使えます。`<ratio>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::deca` は `ratio<10, 1>` の別名（10 倍）
    - [x] `::num` と `::den` が定数として取れる
    - [x] `duration` の単位などに使う

## 関連ページ

- [cpprefjp: std::deca](https://cpprefjp.github.io/reference/ratio/ratio.html)
- [cppreference: std::deca](https://en.cppreference.com/w/cpp/numeric/ratio/ratio)
