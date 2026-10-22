---
title: std::chrono::duration
summary: "時間の長さ。単位（ミリ秒、秒など）を型で持つので、取り違えない。"
order: 1
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::duration

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">C++11</span>
`#include <chrono>`
</div>

「待ち時間を 500」と書いたとき、これがミリ秒なのか秒なのか、コードを読んだだけでは分かりません。単位を取り違えて、500 秒待たせてしまうバグは、よく起きます。`std::chrono::duration` は、時間の長さを、単位ごと型に持たせるクラスです。`500ms` と書けばミリ秒だと一目で分かり、秒と足し算をしても、単位を自動でそろえてくれます。

!!! tip "ポイント"
    - 単位は型で決まる。`milliseconds`、`seconds`、`minutes`、`hours` などが用意されている。
    - 数値を取り出すのは `.count()`。単位を変えるのは `duration_cast`。
    - 小数の秒が欲しいときは `duration<float>` を使う。ゲームのデルタタイムは、これが便利。

!!! info "このページを読む前に"
    [chrono の全体](../chrono.md) を先に読むと、`duration`、`time_point`、時計の関係が分かります。

## 関数の詳しい説明

### std::chrono::duration {#duration}

```cpp
template <class Rep, class Period = std::ratio<1>>
class duration;
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `Rep` | 数値の型 | `long long`、`float` など |  |
| `Period` | `std::ratio` | 1 あたり何秒か（`std::milli` なら 1/1000 秒） | `ratio<1>`（秒） |

`duration<Rep, Period>` は、2 つのテンプレート引数を取ります。`Rep` は数値を持つ型（`int`、`long long`、`float` など）、`Period` は 1 目盛りが何秒かを表す比率です。`seconds` は `duration<long long, ratio<1>>`、`milliseconds` は `duration<long long, ratio<1, 1000>>` の別名です。

`duration<float>` は、`Period` を省略したもので、1 目盛りが 1 秒、数値が `float` の時間です。デルタタイムを `float` の秒で持ちたいときに使います。

異なる単位どうしの足し算・引き算は、細かい単位にそろって行われます。`1500ms + 2s` は `3500ms` です。細かい単位から粗い単位へ（ミリ秒から秒へ）の変換は、情報が失われるので暗黙にはできず、`duration_cast` が必要です。ただし、浮動小数点型の `duration` へなら、暗黙に変換できます。

- 戻り値: （クラス）。`count()` で数値、`+ - * /` と比較が使える
- 計算量: 演算は O(1)

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  milliseconds a(1500);
  seconds b(2);

  auto sum = a + b;  // 細かいほう（ミリ秒）にそろって計算される
  std::println("{} / {}", sum, sum.count());

  duration<double> sec = a;  // 小数の秒に直す（情報が失われないので暗黙に変換できる）
  std::println("{}", sec.count());
}
```

```text title="実行結果"
3500ms / 3500
1.5
```

### count {#count}

```cpp
constexpr Rep count() const;
```

`count()` は、`duration` が持つ数値をそのまま返します。`milliseconds(1500).count()` は `1500` です。単位は型が持っているので、数値だけを取り出すと単位の情報が消えます。関数に渡すときは、`duration` のまま渡すほうが安全です。

- 戻り値: 数値（単位は型で決まる）
- 計算量: O(1)

### zero, min, max {#zero}

```cpp
static constexpr duration zero() noexcept;
static constexpr duration min() noexcept;
static constexpr duration max() noexcept;
```

`duration::zero()` は 0 の長さ、`min()` と `max()` は表せる最小と最大の長さです。`zero()` は、タイマーが 0 以下かを調べるときに使います。`max()` は、制限なしの待ち時間の印として使えます。

- 戻り値: 0、表せる最小、表せる最大
- 計算量: O(1)

### operator+ {#op_plus}

```cpp
template <class Rep1, class Period1, class Rep2, class Period2>
constexpr auto operator+(const duration<Rep1, Period1>& lhs, const duration<Rep2, Period2>& rhs);
```

- 計算量: 定数

2 つの `duration` を足します。単位が違うときは、細かいほうの単位にそろえて計算します（`1s + 500ms` は `1500ms`）。

### operator- {#operator}

```cpp
template <class Rep1, class Period1, class Rep2, class Period2>
constexpr auto operator-(const duration<Rep1, Period1>& lhs, const duration<Rep2, Period2>& rhs);
```

- 計算量: 定数

2 つの `duration` を引きます。単位が違うときは、細かいほうの単位にそろえます。

### operator* {#op_deref}

```cpp
template <class Rep1, class Period, class Rep2>
constexpr auto operator*(const duration<Rep1, Period>& d, const Rep2& s);
```

- 計算量: 定数

`duration` を整数や小数倍します。`16ms * 3` は `48ms` です。

### operator+= {#op_plus_assign}

```cpp
constexpr duration& operator+=(const duration& d);
```

- 計算量: 定数

自分に足します。

### operator== {#op_eq}

```cpp
template <class Rep1, class Period1, class Rep2, class Period2>
constexpr bool operator==(const duration<Rep1, Period1>& lhs, const duration<Rep2, Period2>& rhs);
```

- 計算量: 定数

単位が違っても、同じ長さなら `true`（`1s == 1000ms`）。

### operator<=> <span class="ver ver-20">C++20</span> {#op_cmp data-toc-label="operator<=>"}

```cpp
template <class Rep1, class Period1, class Rep2, class Period2>
constexpr auto operator<=>(const duration<Rep1, Period1>& lhs, const duration<Rep2, Period2>& rhs);
```

- 計算量: 定数

長さを比べる三方比較。単位が違っても比べられます。

## ゲームでの使いどころ

待ち時間やタイマーの引数に使います。`std::this_thread::sleep_for(16ms)` のように書くと、単位の間違いがありません。`16ms` のように書ける仕組みは、[chrono のリテラル](literals.md)です。

ゲームのデルタタイムを `duration<float>` で受けて、`.count()` で秒の `float` にします。位置の更新は `pos += velocity * dt.count();` です。

クールダウン、バフの残り時間、アニメーションの長さなど、時間を扱う設定値を `milliseconds` で持つと、単位の混乱が減ります。設定ファイルから読み込む値は `int` のミリ秒で保存して、`milliseconds(value)` に包みます。

## よくあるミス

??? failure "単位が違う値を数値のまま比べる"
    `int wait = 500;` と書いて、あとで秒だと思って使うと、500 秒になります。`std::chrono::milliseconds wait{500};` と型に単位を持たせます。

??? failure "`count()` の値を別の単位として使う"
    `milliseconds ms = ...; sleep_for(seconds(ms.count()));` と書くと、ミリ秒の数値が秒として解釈されます。単位を変えるなら `duration_cast<seconds>(ms)` です。

??? failure "粗い単位に暗黙に変換しようとする"
    `seconds s = milliseconds(1500);` はコンパイルエラーです。0.5 秒が失われるからです。`duration_cast<seconds>(ms)` を使って、切り捨てることを明示します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`time_point`](time_point.md) | 時刻。`duration` は長さ、`time_point` は時点 |
| [`duration_cast`](duration_cast.md) | 単位を変える |
| [`steady_clock`](steady_clock.md) | 2 つの時点の差から `duration` が得られる |

## コンパイラ対応

C++11 から使えます。`std::println` で出力するには C++20 の chrono 書式が必要です（GCC 13 以降）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 単位を型に持たせて、取り違えを防ぐ。
    - [x] `count()` は数値だけ。単位の変更は `duration_cast`。
    - [x] デルタタイムは `duration<float>` が便利。

## 関連ページ

- [cpprefjp: std::chrono::duration](https://cpprefjp.github.io/reference/chrono/duration.html)
- [cppreference: std::chrono::duration](https://en.cppreference.com/w/cpp/chrono/duration)
