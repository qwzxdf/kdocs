---
title: std::chrono::weekday
summary: "曜日を表す型。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::weekday

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

日付から曜日を知りたいとき、自分で計算式を書く必要はありません。`std::chrono::weekday` は曜日を表す型で、`sys_days` から作れます。`Sunday` ... `Saturday` の定数があります。

!!! tip "ポイント"
    - `weekday{sys_days{...}}` で日付から曜日を取り出す。
    - `c_encoding()` は日曜が 0、`iso_encoding()` は月曜が 1 で日曜が 7。
    - `Monday[2]` のように書くと「第 2 月曜」になる。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::weekday {#weekday}

```cpp
class weekday {
 public:
  constexpr weekday(const sys_days& d) noexcept;
  constexpr unsigned c_encoding() const noexcept;    // 日曜 = 0
  constexpr unsigned iso_encoding() const noexcept;  // 月曜 = 1, 日曜 = 7
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `d` | sys_days | 曜日を知りたい日付 |

- 戻り値: `c_encoding()` は日曜 0 〜 土曜 6
- 計算量: 定数

### std::chrono::Sunday <span class="ver ver-20">C++20</span> {#Sunday data-toc-label="std::chrono::Sunday"}

```cpp
inline constexpr std::chrono::weekday Sunday{0};
```

- 戻り値: 日曜日を表す定数
- 計算量: 定数

`std::chrono::Sunday` は、日曜日（`c_encoding()` が 0）を表す定数です。`Sunday[2]`（第 2 日曜日）や、`Sunday[std::chrono::last]`（最後の日曜日）のように使います。

### std::chrono::Monday <span class="ver ver-20">C++20</span> {#Monday data-toc-label="std::chrono::Monday"}

```cpp
inline constexpr std::chrono::weekday Monday{1};
```

- 戻り値: 月曜日を表す定数
- 計算量: 定数

`std::chrono::Monday` は、月曜日（`c_encoding()` が 1）を表す定数です。`Monday[2]`（第 2 月曜日）や、`Monday[std::chrono::last]`（最後の月曜日）のように使います。

### std::chrono::Tuesday <span class="ver ver-20">C++20</span> {#Tuesday data-toc-label="std::chrono::Tuesday"}

```cpp
inline constexpr std::chrono::weekday Tuesday{2};
```

- 戻り値: 火曜日を表す定数
- 計算量: 定数

`std::chrono::Tuesday` は、火曜日（`c_encoding()` が 2）を表す定数です。`Tuesday[2]`（第 2 火曜日）や、`Tuesday[std::chrono::last]`（最後の火曜日）のように使います。

### std::chrono::Wednesday <span class="ver ver-20">C++20</span> {#Wednesday data-toc-label="std::chrono::Wednesday"}

```cpp
inline constexpr std::chrono::weekday Wednesday{3};
```

- 戻り値: 水曜日を表す定数
- 計算量: 定数

`std::chrono::Wednesday` は、水曜日（`c_encoding()` が 3）を表す定数です。`Wednesday[2]`（第 2 水曜日）や、`Wednesday[std::chrono::last]`（最後の水曜日）のように使います。

### std::chrono::Thursday <span class="ver ver-20">C++20</span> {#Thursday data-toc-label="std::chrono::Thursday"}

```cpp
inline constexpr std::chrono::weekday Thursday{4};
```

- 戻り値: 木曜日を表す定数
- 計算量: 定数

`std::chrono::Thursday` は、木曜日（`c_encoding()` が 4）を表す定数です。`Thursday[2]`（第 2 木曜日）や、`Thursday[std::chrono::last]`（最後の木曜日）のように使います。

### std::chrono::Friday <span class="ver ver-20">C++20</span> {#Friday data-toc-label="std::chrono::Friday"}

```cpp
inline constexpr std::chrono::weekday Friday{5};
```

- 戻り値: 金曜日を表す定数
- 計算量: 定数

`std::chrono::Friday` は、金曜日（`c_encoding()` が 5）を表す定数です。`Friday[2]`（第 2 金曜日）や、`Friday[std::chrono::last]`（最後の金曜日）のように使います。

### std::chrono::Saturday <span class="ver ver-20">C++20</span> {#Saturday data-toc-label="std::chrono::Saturday"}

```cpp
inline constexpr std::chrono::weekday Saturday{6};
```

- 戻り値: 土曜日を表す定数
- 計算量: 定数

`std::chrono::Saturday` は、土曜日（`c_encoding()` が 6）を表す定数です。`Saturday[2]`（第 2 土曜日）や、`Saturday[std::chrono::last]`（最後の土曜日）のように使います。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;
  weekday w{sys_days{2024y / January / 1}};
  std::println("{}", w.c_encoding());
  std::println("{}", w == Monday);
}
```

```text title="実行結果"
1
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 「毎週月曜日」のイベント判定 | `weekday{today} == std::chrono::Monday` |

## よくあるミス

??? failure "日曜 = 7 だと思い込む"
    `c_encoding()` は日曜が 0、`iso_encoding()` は日曜が 7 です。どちらを使うかで結果が変わります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`weekday_indexed`](weekday_indexed.md) | 第 n 曜日 |
| [`weekday_last`](weekday_last.md) | 最後の曜日 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 曜日の型
    - [x] c_encoding は日曜 0
    - [x] Monday[2] で第 2 月曜

## 関連ページ

- [cpprefjp: std::chrono::weekday](https://cpprefjp.github.io/reference/chrono/weekday.html)
- [cppreference: std::chrono::weekday](https://en.cppreference.com/w/cpp/chrono/weekday)
