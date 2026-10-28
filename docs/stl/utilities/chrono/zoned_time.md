---
title: std::chrono::zoned_time
summary: "タイムゾーンつきの日時。"
order: 11
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::zoned_time

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

`std::chrono::zoned_time` は、**時点を指定したタイムゾーン（"Asia/Tokyo" など）の現地時刻で表す**クラスです。世界共通の時刻（`system_clock`）を東京時間やニューヨーク時間で表示したいときに使います。夏時間の切り替えも自動で処理されます。

!!! tip "ポイント"
    - タイムゾーン名は IANA の名前（"Asia/Tokyo"、"America/New_York"）。
    - `std::chrono::current_zone()` で、今の PC のタイムゾーンが取れる。
    - タイムゾーンのデータ（tzdb）は、OS や標準ライブラリに含まれる。Windows でも使えるが、環境によっては初回が遅い。

!!! info "このページを読む前に"
    [`std::chrono`](../chrono.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::chrono::zoned_time {#zoned_time}

```cpp
template <class Duration, class TimeZonePtr = const time_zone*>
class zoned_time {
 public:
  zoned_time(std::string_view name, const sys_time<Duration>& st);
  local_time<Duration> get_local_time() const;
  sys_time<Duration> get_sys_time() const;
};
```

- 戻り値: （クラス）。`get_local_time()` で現地時刻、`get_sys_time()` で世界共通の時刻
- 計算量: O(1)（初回のタイムゾーン読み込みを除く）

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  // エポック（世界共通の 1970-01-01 00:00:00）を東京の時刻で表す
  zoned_time tokyo{"Asia/Tokyo", sys_seconds{}};
  std::println("{}", tokyo);
}
```

```text title="実行結果"
1970-01-01 09:00:00 JST
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| セーブデータの日時をプレイヤーの現地時刻で表示する | `zoned_time{current_zone(), now}` |
| 海外サーバーのイベント時刻を日本時間で表示する | `zoned_time{"Asia/Tokyo", server_time}` |

## よくあるミス

??? failure "古いコンパイラや環境で使えない"
    タイムゾーンの機能は C++20 でも後発で、GCC 13 / MSVC 19.29 以降です。Clang (libc++) は対応が遅れています。使えないときは、`<ctime>` の `localtime` を使います。

??? failure "タイムゾーン名のタイプミス"
    存在しない名前は `std::chrono::nonexistent_...` ではなく、`std::runtime_error` の例外になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`system_clock`](system_clock.md) | 世界共通の時刻 |
| [`year_month_day`](year_month_day.md) | カレンダーの日付 |

## コンパイラ対応

C++20 の機能です。GCC 13 / MSVC 19.29（VS 2019 16.10）以降で使えます。Clang (libc++) はまだ未対応のバージョンがあります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] タイムゾーンつきの日時
    - [x] 名前は "Asia/Tokyo" の形式
    - [x] 環境によって使えない

## 関連ページ

- [cpprefjp: std::chrono::zoned_time](https://cpprefjp.github.io/reference/chrono/zoned_time.html)
- [cppreference: std::chrono::zoned_time](https://en.cppreference.com/w/cpp/chrono/zoned_time)
