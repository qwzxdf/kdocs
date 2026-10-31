---
title: std::chrono::minutes
summary: "分を数える duration の別名。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::minutes

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <chrono>`
</div>

クールダウンが 90 分、スタミナの回復に 5 分ごと。ゲームには、分の単位の時間がよく出てきます。`std::chrono::minutes` は、1 分を単位として数える `duration` の別名で、`minutes(90)` や `90min` と書けば、単位が型に入ります。

!!! tip "ポイント"
    - `duration<整数, ratio<60>>` の別名。1 つぶんが 60 秒
    - `seconds` や `milliseconds` へは暗黙に変換でき、`hours` へは `duration_cast` が必要
    - リテラルは `min`。`m` は月ではなくメートルなど別の意味に紛らわしいので、`min` と書く
    - 内部の整数型は、29 ビット以上の符号つき整数

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`hours`](hours.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::minutes {#minutes}

```cpp
using minutes = duration<int-at-least-29-bits, std::ratio<60>>;
```

`minutes m{90};` のように作ります。`m.count()` で数を取り出せます。

分から秒やミリ秒への変換は、暗黙に行われます。`seconds s = minutes{2};` は 120 秒です。分から時間への変換は、端数が出るので `duration_cast<hours>(m)` が必要で、90 分は 1 時間に切り捨てられます。

時・分・秒に分けて表示したいときは、`hh_mm_ss` を使うと、分解の計算を自分で書かなくて済みます。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;
  using namespace std::chrono_literals;

  const minutes m = 90min;  // リテラル
  std::println("90 分は {} 秒", duration_cast<seconds>(m).count());
  std::println("90 分は {} 時間 (切り捨て)", duration_cast<hours>(m).count());

  // 5 分ごとの回復で、2 時間ぶん回復する回数
  const int times = hours{2} / minutes{5};
  std::println("2 時間で {} 回回復する", times);
}
```

```text title="実行結果"
90 分は 5400 秒
90 分は 1 時間 (切り捨て)
2 時間で 24 回回復する
```

`hours{2} / minutes{5}` のように、`duration` どうしを割ると、単位が打ち消されて、整数の 24 になります。

## ゲームでの使いどころ

スタミナの回復や、クールダウンの間隔のように、分単位で決める設計値を、`minutes` で持ちます。

## よくあるミス

??? failure "m と min を取り違える"
    `chrono` のリテラルに `m` はありません。分は `min` です（月は `m` ではなく `months`）。

??? failure "分の数を int で持ち、秒と取り違える"
    関数の引数が `int minutes` だと、秒を渡しても気づきません。引数の型を `std::chrono::minutes` にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`hours`](hours.md) | 時間の単位 |
| [`seconds`](seconds.md) | 秒の単位 |
| [`hh_mm_ss`](hh_mm_ss.md) | 時・分・秒に分解する |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `minutes` は、1 分を単位とする `duration`
    - [x] リテラルは `min`
    - [x] `duration` どうしの割り算で、回数が整数で求まる

## 関連ページ

- [cpprefjp: minutes](https://cpprefjp.github.io/reference/chrono/duration.html)
- [cppreference: std::chrono::minutes](https://en.cppreference.com/w/cpp/chrono/duration)
