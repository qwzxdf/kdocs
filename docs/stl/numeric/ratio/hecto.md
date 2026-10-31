---
title: std::hecto
summary: "SI 接頭辞「hecto」（100 倍）を表す `ratio` の別名。"
order: 900
tags:
  - 数値
---

# std::hecto

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <ratio>`
</div>

距離を 100 メートル単位でまとめたい、タイマーを 100 秒単位で持ちたい。100 倍の単位を型として持ちたいときに、`std::hecto`（ヘクト、100 倍）を使います。`ratio<100, 1>` の別名です。

!!! tip "ポイント"
    - 中身は `std::ratio<100, 1>`
    - `::num`（分子）と `::den`（分母）をコンパイル時の定数として取り出せる
    - `std::chrono::duration` の単位（第 2 テンプレート引数）として使う
    - 型の別名であり、関数ではない（値は持たない）

!!! info "このページを読む前に"
    [`<ratio>`](../ratio.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::hecto {#hecto}

<span class="ver ver-11">C++11</span>

```cpp
using hecto = ratio<100, 1>;
```

`std::hecto` は、`std::ratio<100, 1>` の別名で、値は 100 倍 を表します。`std::hecto::num` が 100、`std::hecto::den` が 1 で、いずれもコンパイル時の定数です。実行時のコストはありません。

`std::ratio` は分数を型で表す仕組みで、分子・分母は約分された形で保持されます。接頭辞の別名は、よく使う分数に名前を付けたものです。

単位の変換を型で表したいとき、この別名を `std::ratio_multiply` などと組み合わせて使えます。

分母や分子が `std::intmax_t` に収まらない接頭辞（`yotta`、`zetta` など）は、環境によっては定義されません。このページの `hecto` は、64 ビットの範囲に収まるので、どの環境でも使えます。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>
#include <ratio>

int main() {
  using Round = std::chrono::duration<int, std::hecto>;   // 1 単位が 100 秒

  Round two{2};
  auto sec = std::chrono::duration_cast<std::chrono::seconds>(two);
  std::println("2 単位は {} 秒", sec.count());

  // 気圧の単位 hPa(ヘクトパスカル)の換算: 1 hPa = 100 Pa
  constexpr long long pa = 1013LL * std::hecto::num / std::hecto::den;
  std::println("1013 hPa = {} Pa", pa);
}
```

```text title="実行結果"
2 単位は 200 秒
1013 hPa = 101300 Pa
```

`hecto` は、気圧の単位 hPa（ヘクトパスカル）で見かける接頭辞です。1013 hPa は 101300 Pa です。

## ゲームでの使いどころ

時間やスコアを 100 単位の区切りで持ちたいときに使えます。天候の演出で、気圧のような数値を扱うときにも出てきます。

## よくあるミス

??? failure "hecto と centi を取り違える"
    `hecto` は 100 倍、`centi` は 1/100 です。

??? failure "ヘクタール（面積）の ha と混同する"
    面積の単位ヘクタールは、10000 平方メートルです。`hecto` は、面積ではなく、100 倍を表す接頭辞です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ratio`](../ratio.md) | 分数を型で表す基本の仕組み |
| [`std::chrono::duration`](../../utilities/chrono/duration.md) | 時間を単位つきで表す |

## コンパイラ対応

C++11 から使えます。`<ratio>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::hecto` は `ratio<100, 1>` の別名（100 倍）
    - [x] `::num` と `::den` が定数として取れる
    - [x] `duration` の単位などに使う

## 関連ページ

- [cpprefjp: std::hecto](https://cpprefjp.github.io/reference/ratio/ratio.html)
- [cppreference: std::hecto](https://en.cppreference.com/w/cpp/numeric/ratio/ratio)
