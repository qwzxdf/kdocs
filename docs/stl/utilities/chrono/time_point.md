---
title: std::chrono::time_point
summary: "時計の上の「ある時点」。"
order: 2
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::time_point

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-11">C++11</span>
`#include <chrono>`
</div>

「処理を開始した時刻」と「いまの時刻」を覚えておいて、差を取りたい。時刻と時間の長さは別のものです。「午後 3 時」は時刻、「2 時間」は長さで、時刻どうしを引くと長さに、時刻に長さを足すと別の時刻になります。`std::chrono::time_point` は、ある時計の上の「ある時点」を表すクラスで、この関係を型で守ってくれます。

!!! tip "ポイント"
    - `time_point - time_point` が `duration`、`time_point + duration` が `time_point`。
    - **違う時計の時点どうしは比べられない**（型が違う）。
    - `time_since_epoch()` で、基準時刻からの経過時間が取れる。

!!! info "このページを読む前に"
    [`std::chrono::duration`](duration.md) と、[`steady_clock`](steady_clock.md) を先に読んでください。`time_point` は、時計の上の時点を表します。

## 関数の詳しい説明

### std::chrono::time_point {#time_point}

```cpp
template <class Clock, class Duration = typename Clock::duration>
class time_point;
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `Clock` | 時計 | `steady_clock`、`system_clock` など |  |
| `Duration` | `duration` | 時点を表す精度 | `Clock::duration` |

- 戻り値: （クラス）。`+` `-` `<` `==` などが使える
- 計算量: 演算は O(1)

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;
  using namespace std::chrono_literals;

  steady_clock::time_point t0{};   // 基準時刻（エポック）
  auto t1 = t0 + 250ms;            // 250ms 後の時点

  std::println("差 {} / 後ろのほうが新しい？ {}", duration_cast<milliseconds>(t1 - t0), t1 > t0);
}
```

```text title="実行結果"
差 250ms / 後ろのほうが新しい？ true
```

### time_since_epoch {#time_since_epoch}

```cpp
constexpr duration time_since_epoch() const;
```

- 戻り値: 基準時刻（エポック）からの経過時間
- 計算量: O(1)

### min {#min}

```cpp
static constexpr time_point min() noexcept;
```

- 計算量: 定数

表せる最も早い時点。

### max {#max}

```cpp
static constexpr time_point max() noexcept;
```

- 計算量: 定数

表せる最も遅い時点。

### operator+ {#op_plus}

```cpp
constexpr time_point operator+(const time_point& tp, const duration& d);
```

- 計算量: 定数

時点に `duration` を足して、あとの時点を作ります。

### operator- {#operator}

```cpp
constexpr time_point operator-(const time_point& tp, const duration& d);
constexpr auto operator-(const time_point& lhs, const time_point& rhs);
```

- 計算量: 定数

時点から `duration` を引く、または 2 つの時点の差（`duration`）を求めます。経過時間の計算に使います。

### operator+= {#op_plus_assign}

```cpp
constexpr time_point& operator+=(const duration& d);
```

- 計算量: 定数

自分の時点を、`d` だけ進めます。

### operator== {#op_eq}

```cpp
constexpr bool operator==(const time_point& lhs, const time_point& rhs);
```

- 計算量: 定数

同じ時点なら `true`。

### operator<=> <span class="ver ver-20">C++20</span> {#op_cmp data-toc-label="operator<=>"}

```cpp
constexpr auto operator<=>(const time_point& lhs, const time_point& rhs);
```

- 計算量: 定数

時点の先後を比べる三方比較。

## しくみ

`time_point<Clock, Duration>` は、内部に「その時計の基準時刻からの経過時間」を `duration` として持っています。時計が違うと基準も違うので、違う時計の時点どうしは比べられません（型が違うため、コンパイルエラーになります）。

使える演算は決まっています。`time_point - time_point` は `duration`、`time_point + duration` と `time_point - duration` は `time_point` です。時点どうしを足すことはできません。

`time_since_epoch()` で、基準時刻からの経過時間が取れますが、基準時刻は時計の実装次第です。`steady_clock` では意味のある値にならないので、差を取ったときにだけ使います。

## ゲームでの使いどころ

処理時間の計測の起点と終点を、`auto start = steady_clock::now();` として保存しておくのが基本です。差が `duration` になります。

イベントを時刻で管理するとき、`std::vector<std::pair<time_point, Event>>` のように、予定の時刻を持たせます。いまの時刻と比べて、過ぎていれば実行します。

保存したい日時は、`system_clock` の `time_point` を使います。`steady_clock` の時点は、再起動で意味が変わるので、ファイルに保存してはいけません。

## よくあるミス

??? failure "違う時計の時点を引き算する"
    `steady_clock::now() - system_clock::now()` は、型が違うのでコンパイルエラーです。基準が違う時計の時点を、直接比べることはできません。

??? failure "`steady_clock` の時点をファイルに保存する"
    `steady_clock` の基準は、実装ごとに違い、再起動でも変わります。保存した値を後で読み込んでも、意味を持ちません。日時を保存するなら `system_clock` です。

??? failure "時点どうしを足そうとする"
    時点を足す演算はありません。差（`duration`）を足すのは正しい操作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`duration`](duration.md) | 時間の長さ。時点の差 |
| [`steady_clock`](steady_clock.md) | 巻き戻らない時計。計測用 |
| [`system_clock`](system_clock.md) | 世の中の時刻。日時の保存用 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `time_point - time_point` が `duration`、`time_point + duration` が `time_point`。
    - [x] 違う時計の時点は比べられない。
    - [x] 保存するのは `system_clock` の時点。

## 関連ページ

- [cpprefjp: std::chrono::time_point](https://cpprefjp.github.io/reference/chrono/time_point.html)
- [cppreference: std::chrono::time_point](https://en.cppreference.com/w/cpp/chrono/time_point)
