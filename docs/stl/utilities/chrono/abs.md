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

2 つの時刻の差は、順番によって正にも負にもなります。「どれだけ離れているか」だけを知りたいときは、符号を取り除いた長さが欲しくなります。`std::chrono::abs` は、`duration` の絶対値を返す関数です。`duration` どうしの引き算で得られた差に使えます。

!!! tip "ポイント"
    - `abs(d)` は、`d >= 0` なら `d`、負なら `-d`
    - 符号つきの整数か、小数の `duration` だけで使える。符号なしの型ではコンパイルできない
    - 戻り値は同じ型の `duration`
    - 整数型の最小値の `duration` では、オーバーフローする

!!! info "このページを読む前に"
    [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::abs {#abs}

<span class="ver ver-17">C++17</span>

```cpp
template <class Rep, class Period>
constexpr duration<Rep, Period> abs(duration<Rep, Period> d);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `d` | `duration<Rep, Period>` | 絶対値を取る `duration` |

`d` が 0 以上なら `d` を、負なら `-d` を返します。型は変わりません。`Rep` が符号つき（または小数）でないと、`-d` が定義できないので、オーバーロードの解決から外れ、コンパイル エラーです。

`std::abs` は `duration` に使えません。`std::chrono::abs` を使います。名前空間の指定を忘れると、`std::abs(int)` が呼ばれて、`duration` が整数に変換できないために、コンパイル エラーになります。

整数の `Rep` の最小値（`INT_MIN`）の `duration` を渡すと、符号を反転した値が表せず、オーバーフローします。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;
  using namespace std::chrono_literals;

  std::println("{}", abs(-5s).count());
  std::println("{}", abs(5s).count());

  // 2 つの時点が、どれだけ離れているか
  const auto a = 3s;
  const auto b = 10s;
  std::println("離れている長さ: {} 秒", abs(a - b).count());

  // 小数の duration でも使える
  const duration<double> d{-1.5};
  std::println("{}", abs(d).count());
}
```

```text title="実行結果"
5
5
離れている長さ: 7 秒
1.5
```

`a - b` は -7 秒ですが、`abs` で 7 秒になります。

## ゲームでの使いどころ

「予定時刻と実際の時刻のずれ」のように、早い遅いを問わず、ずれの大きさを知りたいときに使います。ネットワークの時刻合わせで、差の大きさを閾値と比べる、といった場面です。

## よくあるミス

??? failure "std::abs を使う"
    `std::abs(duration)` は、コンパイルできません。`std::chrono::abs` です。

??? failure "符号なしの duration に使う"
    `duration<unsigned>` では `-d` が使えず、コンパイル エラーです。符号つきの型にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`duration`](duration.md) | 時間の長さの型 |
| [`floor`](floor.md) | 切り捨てて単位を変換する |
| `std::abs` | 数値用。`duration` には使えない |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: abs](https://cpprefjp.github.io/reference/chrono/abs.html)
- [cppreference: std::chrono::abs](https://en.cppreference.com/w/cpp/chrono/abs)
