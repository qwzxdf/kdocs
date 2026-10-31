---
title: std::chrono::time_zone
summary: "1 つのタイムゾーン（例: Asia/Tokyo）を表す型。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::time_zone

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

日本では UTC より 9 時間進み、ニューヨークでは夏時間があって 4 時間か 5 時間遅れます。地域ごとの時差と夏時間の規則を、まとめて持つのが `std::chrono::time_zone` です。`"Asia/Tokyo"` のような名前で `locate_zone` から取得し、UTC の時刻とその地域の壁掛け時計の時刻を、相互に変換します。

!!! tip "ポイント"
    - 自分では作れない。`locate_zone("Asia/Tokyo")` などで、データベースから取得する
    - `to_local` で UTC → 地域の時刻、`to_sys` で地域の時刻 → UTC
    - `get_info` で、その時点の時差・夏時間・略称が分かる
    - 夏時間のある地域では、`to_sys` が例外を投げる時刻がある

!!! info "このページを読む前に"
    [`sys_time`](sys_time.md) と [`local_time`](local_time.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::time_zone {#time_zone}

<span class="ver ver-20">C++20</span>

```cpp
class time_zone {
 public:
  string_view name() const noexcept;
  template <class Duration> sys_info get_info(const sys_time<Duration>&) const;
  template <class Duration> local_info get_info(const local_time<Duration>&) const;
  template <class Duration> auto to_local(const sys_time<Duration>&) const;
  template <class Duration> auto to_sys(const local_time<Duration>&) const;
  template <class Duration> auto to_sys(const local_time<Duration>&, choose) const;
};
```

コピーもムーブもできません。データベースが持つ実体を、`const time_zone*` で指して使います。

### to_local {#to_local}

UTC の時点（`sys_time`）を、その地域の壁掛け時計の時刻（`local_time`）に直します。UTC に時差を足すだけですが、夏時間の期間かどうかを、時点に応じて自動で判断します。変換は必ず 1 通りに決まるので、例外は投げません。

### to_sys {#to_sys}

地域の時刻（`local_time`）を UTC の時点にします。こちらは、1 通りに決まらない場合があります。夏時間の終わりでは同じ時刻が 2 回現れ（曖昧）、始まりでは時刻が飛ぶ（存在しない）からです。その場合は、`ambiguous_local_time` か `nonexistent_local_time` の例外を投げます。`choose::earliest` か `choose::latest` を渡す版なら、曖昧さを解決して値を返します。

### get_info {#get_info}

ある時点について、時差（`offset`）、夏時間の補正（`save`）、略称（`abbrev`）、その情報が有効な期間（`begin`、`end`）を、`sys_info` で返します。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  const time_zone* tokyo = locate_zone("Asia/Tokyo");
  std::println("名前: {}", tokyo->name());

  // UTC 2026-01-01 00:00 → 東京の壁掛け時計
  const sys_seconds utc = sys_days{2026y / January / 1};
  std::println("東京: {:%F %T}", tokyo->to_local(utc));

  // 東京の 2026-01-01 09:00 → UTC
  const local_seconds wall = local_days{2026y / January / 1} + 9h;
  std::println("UTC: {:%F %T}", tokyo->to_sys(wall));

  // 時差と略称
  const sys_info info = tokyo->get_info(utc);
  std::println("時差 {} 時間 略称 {}", duration_cast<hours>(info.offset).count(), info.abbrev);
}
```

```text title="実行結果"
名前: Asia/Tokyo
東京: 2026-01-01 09:00:00
UTC: 2026-01-01 00:00:00
時差 9 時間 略称 JST
```

## ゲームでの使いどころ

プレイヤーの地域の「朝 5 時」でイベントをリセットするとき、`current_zone()` でその人のタイムゾーンを取得し、`to_sys` で UTC の時刻に直します。サーバーは UTC で動かします。

## よくあるミス

??? failure "夏時間の境目で to_sys が例外を投げる"
    存在しない時刻や曖昧な時刻を渡すと、例外が飛びます。`choose` を渡すか、例外を `catch` します。

??? failure "time_zone をコピーする"
    コピーできません。ポインタで持ちます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`zoned_time`](zoned_time.md) | タイムゾーンと時点を組にした型。普段はこちら |
| [`locate_zone`](locate_zone.md) | 名前から `time_zone` を取る |
| [`sys_info`](sys_info.md) | 時差などの情報 |
| [`choose`](choose.md) | 曖昧さの解決の指定 |

## コンパイラ対応

C++20 から使えます。MSVC は Windows の ICU を使います。

## 関連ページ

- [cpprefjp: time_zone](https://cpprefjp.github.io/reference/chrono/time_zone.html)
- [cppreference: std::chrono::time_zone](https://en.cppreference.com/w/cpp/chrono/time_zone)
