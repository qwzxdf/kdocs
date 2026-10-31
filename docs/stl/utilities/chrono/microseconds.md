---
title: std::chrono::microseconds
summary: "マイクロ秒（100 万分の 1 秒）を数える duration の別名。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::microseconds

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <chrono>`
</div>

1 フレームの処理を細かく測ると、ミリ秒では粗すぎて、変化が見えないことがあります。マイクロ秒（100 万分の 1 秒）の単位で数える `std::chrono::microseconds` は、そうした計測に向いています。`us` のリテラル（`500us`）でも書けます。

!!! tip "ポイント"
    - `duration<整数, ratio<1, 1000000>>` の別名。内部の整数は 55 ビット以上
    - 表せる範囲はおよそ ±29 万年。実用上、あふれない
    - `nanoseconds` へは暗黙に変換でき、`milliseconds` へは `duration_cast` が必要
    - ミリ秒を小数で欲しいなら `duration<double, std::milli>`

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`milliseconds`](milliseconds.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::microseconds {#microseconds}

```cpp
using microseconds = duration<int-at-least-55-bits, std::micro>;
```

`microseconds us{1500};` のように作ります。マイクロ秒は、ミリ秒の 1000 分の 1 です。

マイクロ秒から、ミリ秒への変換は、端数が出るので `duration_cast<milliseconds>` が必要です。1500 マイクロ秒は、1 ミリ秒に切り捨てられます。0.5 ミリ秒の端数も残したいときは、小数の `duration` に変換します。

```cpp
const duration<double, std::milli> ms = us;   // 1.5 ミリ秒
```

小数の `duration` へは、端数が失われないので、暗黙に変換できます。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;
  using namespace std::chrono_literals;

  const microseconds us = 1500us;

  // 整数のミリ秒へは切り捨て
  std::println("整数のミリ秒: {}", duration_cast<milliseconds>(us).count());

  // 小数のミリ秒なら、端数が残る
  const duration<double, std::milli> ms = us;
  std::println("小数のミリ秒: {}", ms.count());

  // ミリ秒からは暗黙に変換できる
  const microseconds from_ms = 2ms;
  std::println("2 ミリ秒は {} マイクロ秒", from_ms.count());
}
```

```text title="実行結果"
整数のミリ秒: 1
小数のミリ秒: 1.5
2 ミリ秒は 2000 マイクロ秒
```

## ゲームでの使いどころ

関数 1 つの処理時間のように、フレームより細かい計測の結果を `microseconds` で受けます。表示は、小数のミリ秒にすると読みやすくなります。

## よくあるミス

??? failure "整数のミリ秒に変換して、端数を失う"
    `duration_cast<milliseconds>` は切り捨てるので、1999 マイクロ秒が 1 ミリ秒になります。小数の `duration` を使います。

??? failure "リテラルを us ではなく μs と書こうとする"
    リテラルの接尾辞は `us` です。`μs` と書くことはできません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`milliseconds`](milliseconds.md) | ミリ秒の単位 |
| [`nanoseconds`](nanoseconds.md) | ナノ秒の単位 |
| [`duration_cast`](duration_cast.md) | 単位を変換する |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `microseconds` は、100 万分の 1 秒を単位とする `duration`
    - [x] リテラルは `us`
    - [x] 端数を残したいなら、小数の `duration`

## 関連ページ

- [cpprefjp: microseconds](https://cpprefjp.github.io/reference/chrono/duration.html)
- [cppreference: std::chrono::microseconds](https://en.cppreference.com/w/cpp/chrono/duration)
