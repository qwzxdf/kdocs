---
title: std::chrono::nanoseconds
summary: "ナノ秒（10 億分の 1 秒）を数える duration の別名。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::nanoseconds

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <chrono>`
</div>

`std::chrono::steady_clock::now()` の差を取ると、その型は `nanoseconds` です。標準の時計は、多くの環境でナノ秒の単位で値を返します。`nanoseconds` は、10 億分の 1 秒を単位として数える `duration` の別名で、現在の標準のなかでいちばん細かい単位です。

!!! tip "ポイント"
    - `duration<整数, ratio<1, 1000000000>>` の別名。内部の整数は 64 ビット以上
    - 表せる範囲はおよそ ±292 年
    - 時計の差は、普通この型で出てくる。`duration_cast` でミリ秒などに直して使う
    - 見かけがナノ秒でも、時計の実際の精度がナノ秒とは限らない

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`microseconds`](microseconds.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::nanoseconds {#nanoseconds}

```cpp
using nanoseconds = duration<int-at-least-64-bits, std::nano>;
```

整数の型が 64 ビットなので、最大でおよそ 92 億秒、つまり 292 年ぶんのナノ秒が表せます。それ以上の長さの時間をナノ秒で持つと、あふれます。歴史的な日付の差などには使いません。

`steady_clock` と `system_clock` の時点の差は、時計の `duration` の型（多くの環境でナノ秒）で得られます。環境によって単位が違うので、表示や保存のときは、`duration_cast` で、決まった単位に直します。

ナノ秒は、`microseconds` や `milliseconds` へ、暗黙には変換できません。端数が出るためです。小数のミリ秒にするなら、`duration<double, std::milli>` に代入します。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;
  using namespace std::chrono_literals;

  const nanoseconds ns = 2'500'000ns;

  // 小数のミリ秒へは暗黙に変換できる
  const duration<double, std::milli> ms = ns;
  std::println("{} ミリ秒", ms.count());

  // 整数の秒へは切り捨て
  std::println("{} 秒 (切り捨て)", duration_cast<seconds>(ns).count());

  // 表せる範囲: およそ何年か
  std::println("最大でおよそ {} 年",
               duration_cast<years>(nanoseconds::max()).count());
}
```

```text title="実行結果"
2.5 ミリ秒
0 秒 (切り捨て)
最大でおよそ 292 年
```

`nanoseconds::max()` は、`duration` の最大値です。年に直すと 292 年で、ナノ秒の範囲の限界が分かります。

## ゲームでの使いどころ

計測の結果の受け皿として使います。`steady_clock` の差が出てきたら、すぐ `duration<double, std::milli>` に直して、ミリ秒の小数で扱うのが、分かりやすい書き方です。

## よくあるミス

??? failure "ナノ秒の精度があると思い込む"
    型がナノ秒でも、時計の更新が 100 ナノ秒や 1 マイクロ秒ごとの環境があります。1 回の計測の細かい値を、比べすぎないようにします。

??? failure "長い期間をナノ秒で持つ"
    292 年を超えるとあふれます。長期間は `seconds` や `days` で持ちます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`microseconds`](microseconds.md) | マイクロ秒の単位 |
| [`steady_clock`](steady_clock.md) | 差がナノ秒で得られる時計 |
| [`duration_cast`](duration_cast.md) | 単位を変換する |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `nanoseconds` は、10 億分の 1 秒を単位とする `duration`
    - [x] 範囲はおよそ ±292 年。時計の差が、この型で出てくる
    - [x] 小数のミリ秒に直して扱うと読みやすい

## 関連ページ

- [cpprefjp: nanoseconds](https://cpprefjp.github.io/reference/chrono/duration.html)
- [cppreference: std::chrono::nanoseconds](https://en.cppreference.com/w/cpp/chrono/duration)
