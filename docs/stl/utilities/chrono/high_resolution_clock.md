---
title: std::chrono::high_resolution_clock
summary: "最も細かい時計（実体は環境しだい）。使わず steady_clock を使う。"
order: 5
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::high_resolution_clock

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <chrono>`
</div>

「いちばん細かい時計」という名前から、計測にはこれを使いたくなりますが、実体は環境によって違います。MSVC では `steady_clock` の別名で、libstdc++ では `system_clock` の別名です。後者では、巻き戻る可能性があるので、計測に向きません。結局、`steady_clock` を使うのが安全で、`high_resolution_clock` を選ぶ理由は、ほとんどありません。

!!! tip "ポイント"
    - `steady_clock` か `system_clock` の別名。どちらかは環境しだい
    - MSVC は `steady_clock`、libstdc++ は `system_clock`
    - 名前に反して、`steady_clock` より細かいとは限らない
    - 計測には `steady_clock`

!!! info "このページを読む前に"
    [`steady_clock`](steady_clock.md) と [`system_clock`](system_clock.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::high_resolution_clock {#high_resolution_clock}

<span class="ver ver-11">C++11</span>

```cpp
class high_resolution_clock;  // 実装定義。別名であってもよい
```

規格は、「実装が持つ時計のうち、最も細かいもの」と書いていますが、`system_clock` や `steady_clock` の別名にしてよいとしています。実際の実装は、次のとおりです。

| 処理系 | 実体 |
| --- | --- |
| MSVC | `steady_clock` |
| libstdc++（GCC） | `system_clock` |
| libc++（Clang） | `steady_clock`（新しい版） |

`is_steady` は、実体が `steady_clock` なら真、`system_clock` なら偽です。コードが環境で違う動きをします。

分解能は、実体の時計のものと同じで、`high_resolution_clock` のほうが細かいわけではありません。標準の作者たちも、現在は使わないことを勧めています。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>
#include <type_traits>

int main() {
  using namespace std::chrono;

  // 実体は処理系しだい
  std::println("steady_clock と同じ型: {}",
               std::is_same_v<high_resolution_clock, steady_clock>);

  const auto t0 = high_resolution_clock::now();
  volatile int sum = 0;
  for (int i = 0; i < 1000; ++i) sum += i;
  const auto t1 = high_resolution_clock::now();
  std::println("経過時間は 0 以上: {}", t1 >= t0);
}
```

```text title="実行結果（MSVC）"
steady_clock と同じ型: true
経過時間は 0 以上: true
```

1 行目は MSVC の結果です。libstdc++ では `false` になります。

## ゲームでの使いどころ

使いません。フレーム時間やプロファイルの計測は、`steady_clock` です。

```cpp
const auto t0 = std::chrono::steady_clock::now();
// 計測したい処理
const auto t1 = std::chrono::steady_clock::now();
```

## よくあるミス

??? failure "名前につられて、計測に使う"
    環境によっては、巻き戻りうる `system_clock` になります。`steady_clock` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`steady_clock`](steady_clock.md) | 巻き戻らない時計。計測にはこちら |
| [`system_clock`](system_clock.md) | 日常の時刻。巻き戻りうる |

## コンパイラ対応

C++11 から使えます。実体は処理系ごとに違います。

## 関連ページ

- [cpprefjp: high_resolution_clock](https://cpprefjp.github.io/reference/chrono/high_resolution_clock.html)
- [cppreference: std::chrono::high_resolution_clock](https://en.cppreference.com/w/cpp/chrono/high_resolution_clock)
