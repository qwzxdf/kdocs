---
title: std::chrono::abs
summary: "duration の絶対値を返す。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::abs

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <chrono>`
</div>

`duration` が負のこともある差（`now - target`）から、「どれだけずれているか」の大きさだけが欲しいことがあります。`std::chrono::abs(d)` は、`duration` の絶対値を返します。整数の `abs` を使うと、`count()` を取り出す手間が増えます。

!!! tip "ポイント"
    - `duration` を受け取り、同じ型で返す。
    - 符号つきの `rep` の `duration` だけで使える。
    - `std::abs`（数値）とは別の関数。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::chrono::abs {#abs}

```cpp
template <class Rep, class Period>
constexpr duration<Rep, Period> abs(duration<Rep, Period> d);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `d` | duration | 絶対値を求める時間 |

- 戻り値: `|d|`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono_literals;
  auto d = 100ms - 250ms;
  std::println("{}", std::chrono::abs(d).count());
}
```

```text title="実行結果"
150
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 目標時刻とのずれの大きさ | `std::chrono::abs(now - target)` |

## よくあるミス

??? failure "符号なしの rep で使う"
    `rep` が符号なし整数の `duration` には使えません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`floor`](floor.md) | 単位を丸める |
| [`duration`](duration.md) | 時間の長さ |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] duration の絶対値
    - [x] now - target の大きさ
    - [x] std::abs とは別

## 関連ページ

- [cpprefjp: std::chrono::abs](https://cpprefjp.github.io/reference/chrono/abs.html)
- [cppreference: std::chrono::abs](https://en.cppreference.com/w/cpp/chrono/abs)
