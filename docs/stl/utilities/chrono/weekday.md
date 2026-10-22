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
