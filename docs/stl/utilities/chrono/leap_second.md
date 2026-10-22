---
title: std::chrono::leap_second
summary: "うるう秒の挿入日と値を表す型。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::leap_second

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

うるう秒は、UTC に不定期に足される 1 秒です。`leap_second` は、いつ入ったか（`date()`）と、何秒か（`value()`、普通は +1 秒）を表し、`tzdb.leap_seconds` に一覧があります。

!!! tip "ポイント"
    - `date()` は UTC のうるう秒の挿入時刻。
    - `value()` は +1 秒（正のうるう秒）か −1 秒。
    - `utc_clock` の計算に使われる。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::leap_second {#leap_second}

```cpp
class leap_second {
 public:
  constexpr sys_seconds date() const noexcept;
  constexpr seconds value() const noexcept;
};
```

- 戻り値: 挿入日と値
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  const auto& db = std::chrono::get_tzdb();
  std::println("{}", db.leap_seconds.front().value().count());
}
```

```text title="実行結果"
1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| うるう秒を含む経過時間の計算 | `get_leap_second_info(utc_time)` |

## よくあるミス

??? failure "日の長さを 86400 秒と決めつける"
    うるう秒がある日は 86401 秒です。`system_clock` はそれを無視し、`utc_clock` は数えます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`get_leap_second_info`](get_leap_second_info.md) | ある時点の情報 |
| [`utc_clock`](utc_clock.md) | うるう秒を数える時計 |

## コンパイラ対応

C++20 の機能です。GCC 14 以降、MSVC 19.29 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] うるう秒の記録
    - [x] date() と value()
    - [x] tzdb.leap_seconds に一覧

## 関連ページ

- [cpprefjp: std::chrono::leap_second](https://cpprefjp.github.io/reference/chrono/leap_second.html)
- [cppreference: std::chrono::leap_second](https://en.cppreference.com/w/cpp/chrono/leap_second)
