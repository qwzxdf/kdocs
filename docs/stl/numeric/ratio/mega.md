---
title: std::mega
summary: "SI 接頭辞「mega」（100 万倍）を表す `ratio` の別名。"
order: 900
tags:
  - 数値
---

# std::mega

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <ratio>`
</div>

4K 画面の画素数は約 830 万（8.3 メガピクセル）、CPU のクロックは数 GHz。単位に「メガ」が付く量を、100 万倍の関係として型で扱いたいときに、`std::mega`（メガ、100 万倍）を使います。`ratio<1000000, 1>` の別名です。

!!! tip "ポイント"
    - 中身は `std::ratio<1000000, 1>`
    - `::num`（分子）と `::den`（分母）をコンパイル時の定数として取り出せる
    - `std::chrono::duration` の単位（第 2 テンプレート引数）として使う
    - 型の別名であり、関数ではない（値は持たない）

!!! info "このページを読む前に"
    [`<ratio>`](../ratio.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::mega {#mega}

<span class="ver ver-11">C++11</span>

```cpp
using mega = ratio<1000000, 1>;
```

`std::mega` は、`std::ratio<1000000, 1>` の別名で、値は 100 万倍 を表します。`std::mega::num` が 1000000、`std::mega::den` が 1 で、いずれもコンパイル時の定数です。実行時のコストはありません。

`std::ratio` は分数を型で表す仕組みで、分子・分母は約分された形で保持されます。接頭辞の別名は、よく使う分数に名前を付けたものです。

単位の変換を型で表したいとき、この別名を `std::ratio_multiply` などと組み合わせて使えます。

分母や分子が `std::intmax_t` に収まらない接頭辞（`yotta`、`zetta` など）は、環境によっては定義されません。このページの `mega` は、64 ビットの範囲に収まるので、どの環境でも使えます。

## 実際に動かしてみる

```cpp
#include <print>
#include <ratio>

int main() {
  // 4K 画面の画素数 (メガピクセル)
  constexpr long long pixels = 3840LL * 2160LL;
  std::println("4K の画素数: {} 画素", pixels);
  std::println("メガピクセル: {:.2f}", static_cast<double>(pixels) / std::mega::num);

  // フルHD(1920x1080) との比
  constexpr long long full_hd = 1920LL * 1080LL;
  std::println("4K は FullHD の {} 倍", pixels / full_hd);
}
```

```text title="実行結果"
4K の画素数: 8294400 画素
メガピクセル: 8.29
4K は FullHD の 4 倍
```

4K の画素数は 8294400 で、約 8.29 メガピクセルです。フル HD のちょうど 4 倍です。

## ゲームでの使いどころ

画素数、クロック周波数（MHz）、メモリの転送量など、桁の大きい性能値の表示や換算に使えます。

## よくあるミス

??? failure "mega を 1048576（2 の 20 乗）だと思う"
    `std::mega` は 1000000 です。1048576 は MiB（メビバイト）の係数です。

??? failure "int で計算して桁あふれする"
    `3840 * 2160` は `int` に収まりますが、`mega` を掛けると超えます。`long long` で計算します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ratio`](../ratio.md) | 分数を型で表す基本の仕組み |
| [`std::chrono::duration`](../../utilities/chrono/duration.md) | 時間を単位つきで表す |

## コンパイラ対応

C++11 から使えます。`<ratio>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::mega` は `ratio<1000000, 1>` の別名（100 万倍）
    - [x] `::num` と `::den` が定数として取れる
    - [x] `duration` の単位などに使う

## 関連ページ

- [cpprefjp: std::mega](https://cpprefjp.github.io/reference/ratio/ratio.html)
- [cppreference: std::mega](https://en.cppreference.com/w/cpp/numeric/ratio/ratio)
