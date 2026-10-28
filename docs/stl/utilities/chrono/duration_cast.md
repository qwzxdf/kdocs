---
title: std::chrono::duration_cast
summary: "時間の単位を変換する（切り捨て）。"
order: 6
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::duration_cast

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-11">C++11</span>
`#include <chrono>`
</div>

ミリ秒で測った処理時間を秒に直して画面に出したい。細かい単位から粗い単位へ変換すると、端数が失われます。C++ は、そのような情報が失われる変換を `=` で暗黙には許しません。`std::chrono::duration_cast` は、`duration` を別の単位へ明示的に変換する関数です。端数は切り捨てられます。

!!! tip "ポイント"
    - ミリ秒 → 秒のように、**粗くする変換は明示が必要**。
    - 粗い → 細かい（秒 → ミリ秒）は暗黙に変換できる。
    - 端数は切り捨て（0 に向かって）。

!!! info "このページを読む前に"
    [`std::chrono::duration`](duration.md) の単位と、型でのそろえ方を先に読んでください。

## 関数の詳しい説明

### std::chrono::duration_cast {#duration_cast}

```cpp
template <class ToDuration, class Rep, class Period>
constexpr ToDuration duration_cast(const duration<Rep, Period>& d);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ToDuration` | テンプレート引数 | 変換先の `duration` 型 |
| `d` | `duration` | 変換元 |

- 戻り値: 変換した `ToDuration`（端数は切り捨て）
- 計算量: O(1)

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;
  using namespace std::chrono_literals;

  std::println("{}", duration_cast<seconds>(1999ms));       // 1.999 秒 → 1 秒（切り捨て）
  std::println("{}", duration_cast<milliseconds>(1.5s));    // 1.5 秒 → 1500 ミリ秒
}
```

```text title="実行結果"
1s
1500ms
```

## しくみ

`duration_cast<ToDuration>(d)` は、`d` の値を `ToDuration` の単位に換算して、整数なら 0 に向かって切り捨てて返します。`duration_cast<seconds>(milliseconds(1999))` は `1s` です。

粗い単位から細かい単位（秒からミリ秒）への変換は、情報を失わないので、`duration_cast` なしで暗黙に変換できます。浮動小数点型の `duration`（`duration<double>`）への変換も、暗黙にできます。

切り捨てではなく、切り上げや四捨五入が欲しいときは、C++17 で追加された `std::chrono::ceil`、`round`、`floor` を使います。

## ゲームでの使いどころ

処理時間の計測結果を画面やログに出すために使います。`steady_clock` の差は、ナノ秒の `duration` で得られるので、`duration_cast<milliseconds>(end - start).count()` でミリ秒の整数に直します。

小数で欲しいときは、`duration_cast` を使わず、`duration<float, std::milli>` のように浮動小数点の型で受けます。`std::chrono::duration<float, std::milli> ms = end - start;` と書けば、端数を失いません。

タイマーの残り時間を「分:秒」で表示するときにも使います。`duration_cast<minutes>(remain)` で分を取り、残りの秒は `remain - minutes` で求めます。

## よくあるミス

??? failure "端数が切り捨てられて、0 になる"
    `duration_cast<seconds>(milliseconds(900))` は `0s` です。1 秒未満の処理時間を秒に変換して `0` と表示してしまう、というミスがよく起きます。小数の秒で受けるか、ミリ秒のまま表示します。

??? failure "`count()` を取ってから単位を変えようとする"
    `ms.count() / 1000` は、整数の割り算で端数が消えるうえ、単位の情報も失います。`duration` のまま変換して、最後に `count()` を呼びます。

??? failure "粗い単位への変換を `=` で書いてコンパイルエラー"
    `seconds s = milliseconds(1500);` はコンパイルエラーです。切り捨てが起きることを明示するために、`duration_cast` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`duration`](duration.md) | 時間の長さを表す型 |
| `std::chrono::round` | 四捨五入する |
| `std::chrono::floor` / `ceil` | 切り捨て（`duration_cast` と同じ向き）/ 切り上げ |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 単位を明示的に変換する。端数は切り捨て。
    - [x] 粗い単位から細かい単位への変換は、暗黙にできる。
    - [x] 小数で欲しいときは `duration<float>` で受ける。

## 関連ページ

- [cpprefjp: std::chrono::duration_cast](https://cpprefjp.github.io/reference/chrono/duration_cast.html)
- [cppreference: std::chrono::duration_cast](https://en.cppreference.com/w/cpp/chrono/duration/duration_cast)
