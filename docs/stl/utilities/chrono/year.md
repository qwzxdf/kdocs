---
title: std::chrono::year
summary: "年を表す型。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::year

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

年を `int` で持つと、うるう年の判定を自分で書くことになります。`std::chrono::year` は、年を型で表し、`is_leap()` でうるう年かを教えてくれます。

!!! tip "ポイント"
    - `year{2024}` や `2024y` で作る。
    - `is_leap()` でうるう年かを調べる。
    - `int` に変換して値を取り出す。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::year {#year}

```cpp
class year {
 public:
  constexpr explicit year(int y) noexcept;
  constexpr explicit operator int() const noexcept;
  constexpr bool is_leap() const noexcept;
  constexpr bool ok() const noexcept;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `y` | int | 年（負の年も使える） |

- 戻り値: `is_leap()` はうるう年なら `true`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;
  std::println("{} {}", int(2024y), 2024y.is_leap());
  std::println("{}", 2023y.is_leap());
}
```

```text title="実行結果"
2024 true
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| セーブデータの日付の検証 | `year{y}.ok()` |

## よくあるミス

??? failure "`2024` と `2024y` を取り違える"
    `2024y` は `year` 型のリテラル（`using namespace std::chrono_literals` か `std::literals` が必要）です。単なる `2024` は `int` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`month`](month.md) | 月 |
| [`year_month_day`](year_month_day.md) | 年月日 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 年の型
    - [x] is_leap() でうるう年判定
    - [x] 2024y リテラル

## 関連ページ

- [cpprefjp: std::chrono::year](https://cpprefjp.github.io/reference/chrono/year.html)
- [cppreference: std::chrono::year](https://en.cppreference.com/w/cpp/chrono/year)
