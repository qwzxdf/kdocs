---
title: std::chrono::hours
summary: "時間を数える duration の別名。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::hours

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <chrono>`
</div>

ゲームの中の時間を「時間」の単位で持ちたい。ログインボーナスの再受け取りまで 20 時間、イベントの期間は 72 時間、といった具合です。`std::chrono::hours` は、1 時間を単位として数える `duration` の別名です。`hours(20)` や、リテラルの `20h` と書けば、単位が型に入るので、秒と取り違える心配がありません。

!!! tip "ポイント"
    - `duration<整数, ratio<3600>>` の別名。1 つぶんが 3600 秒
    - 大きな単位から小さな単位（`minutes`、`seconds`）へは、暗黙に変換できる
    - 小さな単位から大きな単位へは `duration_cast` が必要で、端数は切り捨てられる
    - 内部の整数型は、23 ビット以上の符号つき整数

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::hours {#hours}

```cpp
using hours = duration<int-at-least-23-bits, std::ratio<3600>>;
```

`hours` は型の別名で、`hours h{2};` のように、数を渡して作ります。数は `count()` で取り出せます。

大きな単位から小さな単位への変換は、値が失われないので、暗黙にできます。`minutes m = hours{2};` は 120 分になります。逆に、`hours h = minutes{150};` は、端数が出るのでコンパイル エラーです。`duration_cast<hours>(minutes{150})` と書くと、端数を切り捨てて 2 時間になります。端数を残したいなら、`duration<double, std::ratio<3600>>` のように、小数の型の `duration` を使います。

内部の整数は、少なくとも 23 ビットの符号つき整数です。1 時間単位で数えると、数百年を超える範囲になるので、ゲームの用途で足りなくなることはありません。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  const hours h{2};
  const minutes m = h;  // 暗黙の変換: 2 時間 = 120 分
  std::println("2 時間は {} 分", m.count());

  // 小さな単位から大きな単位へは duration_cast。端数は切り捨て
  std::println("150 分は {} 時間", duration_cast<hours>(minutes{150}).count());

  // 計算もできる
  const auto total = hours{1} + minutes{30};
  std::println("1 時間 30 分は {} 分", duration_cast<minutes>(total).count());
}
```

```text title="実行結果"
2 時間は 120 分
150 分は 2 時間
1 時間 30 分は 90 分
```

`hours{1} + minutes{30}` の型は、共通の単位である `minutes` になります。

## ゲームでの使いどころ

「前回の受け取りから 20 時間たったか」のような、長い間隔の判定に使います。時刻の差を `duration_cast<hours>` で時間にして、20 以上かを調べます。

## よくあるミス

??? failure "小さな単位から暗黙に変換しようとする"
    `hours h = minutes{90};` はコンパイル エラーです。端数が出るので、`duration_cast` を明示します。

??? failure "duration_cast で端数が切り捨てられるのを忘れる"
    `duration_cast<hours>(minutes{119})` は 1 時間です。四捨五入したいなら `round<hours>`、切り上げなら `ceil<hours>` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`minutes`](minutes.md) | 分の単位 |
| [`days`](days.md) | 日の単位（C++20） |
| [`duration_cast`](duration_cast.md) | 単位を変換する |
| [`literals`](literals.md) | `2h` のように書くリテラル |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `hours` は、1 時間を単位とする `duration`
    - [x] 大きな単位から小さな単位へは暗黙に変換できる
    - [x] 逆は `duration_cast`。端数は切り捨て

## 関連ページ

- [cpprefjp: hours](https://cpprefjp.github.io/reference/chrono/duration.html)
- [cppreference: std::chrono::hours](https://en.cppreference.com/w/cpp/chrono/duration)
