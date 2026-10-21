---
title: std::chrono::hh_mm_ss
summary: "経過時間を「時・分・秒」に分解する。"
order: 10
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::hh_mm_ss

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

`std::chrono::hh_mm_ss` は、**`duration` を「時・分・秒・（秒未満）」に分解する**クラスです。ゲームのプレイ時間「1:02:05」のような表示を作るときに使います。割り算や剰余を自分で書かなくて済みます。

!!! tip "ポイント"
    - `hh_mm_ss t{duration};` と作って、`t.hours()`、`t.minutes()`、`t.seconds()` で取り出す。
    - 各要素は `duration` なので、数値は `.count()`。
    - `std::println("{:%T}", t)` のように、書式で直接出すこともできる。

!!! info "このページを読む前に"
    [`std::chrono`](../chrono.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::chrono::hh_mm_ss {#hh_mm_ss}

```cpp
template <class Duration>
class hh_mm_ss {
 public:
  constexpr explicit hh_mm_ss(Duration d) noexcept;
  constexpr hours hours() const noexcept;
  constexpr minutes minutes() const noexcept;
  constexpr seconds seconds() const noexcept;
};
```

- 戻り値: （クラス）。各部分を取り出す関数を持つ
- 計算量: O(1)

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  hh_mm_ss t{seconds{3725}};   // 3725 秒
  std::println("{}:{:02}:{:02}", t.hours().count(), t.minutes().count(), t.seconds().count());
}
```

```text title="実行結果"
1:02:05
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| プレイ時間の表示（1:02:05） | `hh_mm_ss{play_time}` |
| レースのラップタイム表示 | `hh_mm_ss` で分・秒・ミリ秒に分ける |

## よくあるミス

??? failure "分や秒を元の合計と取り違える"
    `t.minutes()` は「時を除いた分」（0〜59）です。合計の分ではありません。合計の分は `duration_cast<minutes>(d)` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`duration`](duration.md) | 分解する元 |
| [`duration_cast`](duration_cast.md) | 合計の単位変換 |

## コンパイラ対応

C++20 の機能です。GCC 11 / Clang 16 / MSVC 19.29 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `duration` を時・分・秒に分解する
    - [x] 各部分は `.count()` で数値に
    - [x] C++20

## 関連ページ

- [cpprefjp: std::chrono::hh_mm_ss](https://cpprefjp.github.io/reference/chrono/hh_mm_ss.html)
- [cppreference: std::chrono::hh_mm_ss](https://en.cppreference.com/w/cpp/chrono/hh_mm_ss)
