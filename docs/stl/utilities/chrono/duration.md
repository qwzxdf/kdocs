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

`std::chrono::duration` は、**時間の長さ**を表すクラスです。`milliseconds`、`seconds` のような別名があり、**単位が型に入っている**ので、「秒とミリ秒を取り違える」バグを防げます。違う単位どうしでも、足し算・引き算・比較ができます（細かいほうの単位に合わせて計算されます）。

!!! tip "ポイント"
    - 単位は型で決まる。`std::chrono::milliseconds`、`seconds`、`minutes`、`hours`、…
    - 数値として取り出すのは `.count()`。単位を変えるのは [`duration_cast`](duration_cast.md)。
    - 小数の秒が欲しいなら `std::chrono::duration<float>`（`float` の秒）。

!!! info "このページを読む前に"
    [`std::chrono`](../chrono.md) の概要を先に読むと分かりやすいです。

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

- 戻り値: 数値（単位は型で決まる）
- 計算量: O(1)

### zero, min, max {#zero}

```cpp
static constexpr duration zero() noexcept;
static constexpr duration min() noexcept;
static constexpr duration max() noexcept;
```

- 戻り値: 0、表せる最小、表せる最大
- 計算量: O(1)

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| フレーム時間・待ち時間・クールダウン | `std::chrono::duration<float> dt = now - last;` |
| タイムアウトの設定 | `std::chrono::seconds timeout(5);` |

## よくあるミス

??? failure "count() の単位を忘れる"
    `ms.count()` は「ミリ秒の数」です。秒として使うと 1000 倍ずれます。型で単位を持ち、数値にするのは最後の最後にします。

??? failure "細かい単位から粗い単位への代入"
    `seconds s = 1500ms;` は、情報が失われるのでコンパイルエラーです。`duration_cast` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`duration_cast`](duration_cast.md) | 単位を変換する（切り捨て） |
| [`time_point`](time_point.md) | 「ある時点」を表す |
| [`literals`](literals.md) | `16ms`、`2s` と書ける |

## コンパイラ対応

C++11 から使えます。`std::println` で出力するには C++20 の chrono 書式が必要です（GCC 13 以降）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 時間の長さ。単位が型に入っている
    - [x] 数値は `.count()`
    - [x] 粗い単位への変換は `duration_cast`

## 関連ページ

- [cpprefjp: std::chrono::duration](https://cpprefjp.github.io/reference/chrono/duration.html)
- [cppreference: std::chrono::duration](https://en.cppreference.com/w/cpp/chrono/duration)
