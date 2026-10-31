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

プレイ時間 3725 秒を、「1 時間 2 分 5 秒」と表示したい。`duration` の数を 3600 や 60 で割って余りを取る計算は、よく間違えます。`std::chrono::hh_mm_ss` は、`duration` を時・分・秒（と、それ未満の端数）に分解して、`hours()`、`minutes()`、`seconds()` で取り出せるようにする型です。

!!! tip "ポイント"
    - `hh_mm_ss(duration)` で分解する。`hours()`、`minutes()`、`seconds()`、`subseconds()` で取り出す
    - 負の `duration` では、`is_negative()` が真になり、各部分は絶対値
    - 24 時間を超えても、`hours()` が 24 以上の値を持つ（日には繰り上がらない）
    - `std::format` の `{:%T}` でも書式にかけられる

!!! info "このページを読む前に"
    [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::hh_mm_ss {#hh_mm_ss}

<span class="ver ver-20">C++20</span>

```cpp
template <class Duration>
class hh_mm_ss {
 public:
  constexpr explicit hh_mm_ss(Duration d);
  constexpr bool is_negative() const noexcept;
  constexpr chrono::hours hours() const noexcept;
  constexpr chrono::minutes minutes() const noexcept;
  constexpr chrono::seconds seconds() const noexcept;
  constexpr precision subseconds() const noexcept;
  constexpr explicit operator precision() const noexcept;
};
```

`Duration` は分解したい `duration` の型です。秒より細かい単位（ミリ秒など）を渡すと、`subseconds()` に端数が入ります。

### 各部分の取り出し {#parts}

`hours()` は時間の部分、`minutes()` は 0〜59 の分、`seconds()` は 0〜59 の秒です。`subseconds()` は、秒未満の部分で、元の `duration` の単位のまま返ります。

時間の部分は、24 を超えても繰り上がりません。100 時間を渡すと、`hours()` は 100 です。日に直したいなら、先に `duration_cast<days>` で分けます。

### 負の値 {#negative}

負の `duration` を渡すと、`is_negative()` が真になり、各部分は、絶対値で入ります。表示するときは、`is_negative()` を見て、マイナス記号を自分で付けます。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  // プレイ時間 3725 秒
  const hh_mm_ss t{seconds{3725}};
  std::println("{} 時間 {} 分 {} 秒", t.hours().count(), t.minutes().count(),
               t.seconds().count());

  // ミリ秒つきの分解
  const hh_mm_ss u{milliseconds{61'500}};
  std::println("{} 分 {} 秒 {} ミリ秒", u.minutes().count(), u.seconds().count(),
               u.subseconds().count());

  // 負の値
  const hh_mm_ss neg{seconds{-90}};
  std::println("負: {} {} 分 {} 秒", neg.is_negative(), neg.minutes().count(),
               neg.seconds().count());
}
```

```text title="実行結果"
1 時間 2 分 5 秒
1 分 1 秒 500 ミリ秒
負: true 1 分 30 秒
```

3725 秒が 1 時間 2 分 5 秒、61500 ミリ秒が 1 分 1 秒 500 ミリ秒に分解されました。

## ゲームでの使いどころ

プレイ時間やタイマーの残り時間の表示で、時・分・秒を取り出します。自分で `%` と `/` を書くと、負の値や桁の扱いで間違えやすいので、`hh_mm_ss` に任せます。

## よくあるミス

??? failure "24 時間を超えても繰り上がると思う"
    `hours()` は 24 以上の値を持ちます。日数が欲しいなら、先に `days` に分けます。

??? failure "負の値で各部分が負になると思う"
    各部分は絶対値です。符号は `is_negative()` で見ます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`duration`](duration.md) | 分解前の、時間の長さ |
| [`make12`](make12.md) | 12 時間制の時に直す |
| [`duration_cast`](duration_cast.md) | 単位を変換する |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: hh_mm_ss](https://cpprefjp.github.io/reference/chrono/hh_mm_ss.html)
- [cppreference: std::chrono::hh_mm_ss](https://en.cppreference.com/w/cpp/chrono/hh_mm_ss)
