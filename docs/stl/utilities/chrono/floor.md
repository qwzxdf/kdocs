---
title: std::chrono::floor
summary: "duration（または time_point）を、別の単位に丸める（切り捨て・切り上げ・四捨五入）。"
order: 7
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::floor

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <chrono>`
</div>

`std::chrono::floor`・`ceil`・`round` は、**`duration` や `time_point` を別の単位に変換するとき、丸め方を選べる**関数です。[`duration_cast`](duration_cast.md) は切り捨てだけですが、こちらは「切り捨て（floor）」「切り上げ（ceil）」「四捨五入（round）」を選べます。`round` は半分のとき**偶数のほう**へ丸めます。

!!! tip "ポイント"
    - 3 つとも同じ形: `floor<seconds>(d)`、`ceil<seconds>(d)`、`round<seconds>(d)`。
    - `round` は 0.5 のとき偶数へ（1.5 秒 → 2 秒、2.5 秒 → 2 秒）。
    - `time_point` や `abs`（絶対値）にも使える。

!!! info "このページを読む前に"
    [`std::chrono`](../chrono.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### floor, ceil, round {#floor}

```cpp
template <class ToDuration, class Rep, class Period>
constexpr ToDuration floor(const duration<Rep, Period>& d);   // 切り捨て
template <class ToDuration, class Rep, class Period>
constexpr ToDuration ceil(const duration<Rep, Period>& d);    // 切り上げ
template <class ToDuration, class Rep, class Period>
constexpr ToDuration round(const duration<Rep, Period>& d);   // 四捨五入（半分は偶数へ）
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ToDuration` | テンプレート引数 | 変換先の `duration` 型 |
| `d` | `duration` | 変換元 |

- 戻り値: 丸めた `ToDuration`
- 計算量: O(1)

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;
  using namespace std::chrono_literals;

  milliseconds t = 1600ms;
  std::println("{} {} {}", floor<seconds>(t), ceil<seconds>(t), round<seconds>(t));

  // 半分のときは偶数へ丸められる
  std::println("{} {}", round<seconds>(1500ms), round<seconds>(2500ms));
}
```

```text title="実行結果"
1s 2s 2s
2s 2s
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 残り時間を「切り上げて」秒で表示する（0.1 秒残っているなら 1 と表示） | `ceil<seconds>(remaining)` |
| 日時を秒単位に切り捨てて出力する | `floor<seconds>(system_clock::now())` |

## よくあるミス

??? failure "四捨五入のつもりで round を使う"
    半分（x.5）のときは、偶数へ丸めるので、2.5 は 3 ではなく 2 になります。

??? failure "古い環境"
    `floor` / `ceil` / `round` は C++17 です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`duration_cast`](duration_cast.md) | 切り捨てだけ |
| [`std::floor` / `std::round`](../../numeric/cmath/floor.md) | 数値の丸め |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 丸め方を選んで単位を変換する
    - [x] `round` は半分のとき偶数へ
    - [x] C++17

## 関連ページ

- [cpprefjp: std::chrono::floor](https://cpprefjp.github.io/reference/chrono/duration/floor.html)
- [cppreference: std::chrono::floor](https://en.cppreference.com/w/cpp/chrono/duration/floor)
