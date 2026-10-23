---
title: std::chrono
group: 時間（std::chrono）
summary: "時間の長さ・時刻を扱う。フレームの時間計測や待ち時間に。"
order: 55
tags:
  - ユーティリティ
  - 時間
---

# std::chrono

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-4">◎ 速い</span>
<span class="ver ver-11">C++11</span>
`#include <chrono>`
</div>

フレームの処理に何ミリ秒かかったか。前のフレームから何秒たったか。時間を扱うとき、数値だけで持つと、秒なのかミリ秒なのかが分からなくなります。`std::chrono` は、時間の長さ・時刻・時計を扱うライブラリです。「何秒か」を表す `duration`、「ある時点」を表す `time_point`、現在の時刻を教える時計（clock）の 3 つが中心で、単位を型で区別するので、取り違えがコンパイルで見つかります。

!!! tip "ポイント"
    - <strong>フレーム時間・処理時間の計測は `std::chrono::steady_clock::now()` の差。</strong> 時計が巻き戻らないので安全。
    - 秒の小数（`float`）が欲しいなら `std::chrono::duration<float>(差).count()`。
    - `using namespace std::chrono_literals;` で `16ms`、`3s` のように書ける。
    - カレンダーの日付・現在時刻の表示は `system_clock`。

!!! info "このページを読む前に"
    時間の単位（秒、ミリ秒）と、時刻と時間の長さの違いが分かると読みやすいです。

## 主な型

| 型 | 重要度 | 何を表す |
| --- | --- | --- |
| [`steady_clock`](chrono/steady_clock.md) | <span class="rank rank-must">必須</span> | 巻き戻らない時計（計測用） |
| [`duration`](chrono/duration.md) | <span class="rank rank-must">必須</span> | 時間の長さ（`milliseconds` など） |
| [`time_point`](chrono/time_point.md) | <span class="rank rank-often">よく使う</span> | ある時点 |
| [`system_clock`](chrono/system_clock.md) | <span class="rank rank-sometimes">たまに</span> | 現実の時刻（カレンダー） |
| [`high_resolution_clock`](chrono/high_resolution_clock.md) | <span class="rank rank-rare">知ってるだけ</span> | 一番細かい時計（中身は上のどちらか） |
| [`std::chrono::utc_clock`](chrono/utc_clock.md) | <span class="rank rank-rare">知ってるだけ</span> | うるう秒を数に入れた、協定世界時（UTC）の時計。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::tai_clock`](chrono/tai_clock.md) | <span class="rank rank-rare">知ってるだけ</span> | うるう秒を含まず、連続して進む国際原子時（TAI）の時計。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::gps_clock`](chrono/gps_clock.md) | <span class="rank rank-rare">知ってるだけ</span> | GPS の時刻に合わせた時計。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::clock_cast`](chrono/clock_cast.md) | <span class="rank rank-rare">知ってるだけ</span> | 時計どうしの時点を、別の時計の時点に変換する。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::nanoseconds`](chrono/nanoseconds.md) | <span class="rank rank-rare">知ってるだけ</span> | ナノ秒（10 億分の 1 秒）を数える duration の別名。 |
| [`std::chrono::microseconds`](chrono/microseconds.md) | <span class="rank rank-rare">知ってるだけ</span> | マイクロ秒（100 万分の 1 秒）を数える duration の別名。 |
| [`std::chrono::milliseconds`](chrono/milliseconds.md) | <span class="rank rank-sometimes">たまに</span> | ミリ秒（1000 分の 1 秒）を数える duration の別名。 |
| [`std::chrono::seconds`](chrono/seconds.md) | <span class="rank rank-sometimes">たまに</span> | 秒を数える duration の別名。 |
| [`std::chrono::minutes`](chrono/minutes.md) | <span class="rank rank-rare">知ってるだけ</span> | 分を数える duration の別名。 |
| [`std::chrono::hours`](chrono/hours.md) | <span class="rank rank-rare">知ってるだけ</span> | 時間を数える duration の別名。 |
| [`std::chrono::days`](chrono/days.md) | <span class="rank rank-rare">知ってるだけ</span> | 日を数える duration の別名。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::weeks`](chrono/weeks.md) | <span class="rank rank-rare">知ってるだけ</span> | 週を数える duration の別名。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::months`](chrono/months.md) | <span class="rank rank-rare">知ってるだけ</span> | 月（平均の長さ）を数える duration の別名。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::years`](chrono/years.md) | <span class="rank rank-rare">知ってるだけ</span> | 年（平均の長さ）を数える duration の別名。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::time_point_cast`](chrono/time_point_cast.md) | <span class="rank rank-rare">知ってるだけ</span> | time_point の単位を、別の単位に変換する（切り捨て）。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::treat_as_floating_point`](chrono/treat_as_floating_point.md) | <span class="rank rank-rare">知ってるだけ</span> | duration の中身（rep）を、小数として扱うかの特性。 <span class="ver ver-11">C++11</span> |
| [`std::chrono::duration_values`](chrono/duration_values.md) | <span class="rank rank-rare">知ってるだけ</span> | duration の rep について、0・最小・最大を返す。 <span class="ver ver-11">C++11</span> |
| [`std::chrono::day`](chrono/day.md) | <span class="rank rank-rare">知ってるだけ</span> | 月の中の日（1〜31）を表す型。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::month`](chrono/month.md) | <span class="rank rank-rare">知ってるだけ</span> | 月（1〜12）を表す型。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::year`](chrono/year.md) | <span class="rank rank-rare">知ってるだけ</span> | 年を表す型。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::weekday`](chrono/weekday.md) | <span class="rank rank-rare">知ってるだけ</span> | 曜日を表す型。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::weekday_indexed`](chrono/weekday_indexed.md) | <span class="rank rank-rare">知ってるだけ</span> | 「第 n の曜日」を表す型（第 2 月曜日など）。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::weekday_last`](chrono/weekday_last.md) | <span class="rank rank-rare">知ってるだけ</span> | 「最後の曜日」を表す型（最終金曜日など）。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::month_day`](chrono/month_day.md) | <span class="rank rank-rare">知ってるだけ</span> | 月と日の組（誕生日のような、年を問わない日付）。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::month_day_last`](chrono/month_day_last.md) | <span class="rank rank-rare">知ってるだけ</span> | 「その月の最終日」を表す型。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::month_weekday`](chrono/month_weekday.md) | <span class="rank rank-rare">知ってるだけ</span> | 「その月の第 n 曜日」を表す型（年を問わない）。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::month_weekday_last`](chrono/month_weekday_last.md) | <span class="rank rank-rare">知ってるだけ</span> | 「その月の最後の曜日」を表す型（年を問わない）。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::year_month`](chrono/year_month.md) | <span class="rank rank-rare">知ってるだけ</span> | 年と月の組。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::year_month_day_last`](chrono/year_month_day_last.md) | <span class="rank rank-rare">知ってるだけ</span> | 「その年のその月の最終日」を表す型。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::year_month_weekday`](chrono/year_month_weekday.md) | <span class="rank rank-rare">知ってるだけ</span> | 「その年のその月の第 n 曜日」を表す型。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::year_month_weekday_last`](chrono/year_month_weekday_last.md) | <span class="rank rank-rare">知ってるだけ</span> | 「その年のその月の最後の曜日」を表す型。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::last_spec`](chrono/last_spec.md) | <span class="rank rank-rare">知ってるだけ</span> | 「最後」を表す定数 `std::chrono::last` の型。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::is_am`](chrono/is_am.md) | <span class="rank rank-rare">知ってるだけ</span> | 24 時間制の時刻が午前かを調べる。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::is_pm`](chrono/is_pm.md) | <span class="rank rank-rare">知ってるだけ</span> | 24 時間制の時刻が午後かを調べる。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::make12`](chrono/make12.md) | <span class="rank rank-rare">知ってるだけ</span> | 24 時間制の時を、12 時間制の時（1〜12）に直す。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::make24`](chrono/make24.md) | <span class="rank rank-rare">知ってるだけ</span> | 12 時間制の時を、24 時間制の時（0〜23）に直す。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::sys_time`](chrono/sys_time.md) | <span class="rank rank-rare">知ってるだけ</span> | system_clock の時点を表す別名（単位を選べる）。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::sys_seconds`](chrono/sys_seconds.md) | <span class="rank rank-rare">知ってるだけ</span> | system_clock の時点を、秒の単位で表す別名。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::sys_days`](chrono/sys_days.md) | <span class="rank rank-rare">知ってるだけ</span> | system_clock の時点を、日の単位で表す別名（カレンダーの日付）。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::local_time`](chrono/local_time.md) | <span class="rank rank-rare">知ってるだけ</span> | タイムゾーンのない、地域の時刻を表す別名。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::local_seconds`](chrono/local_seconds.md) | <span class="rank rank-rare">知ってるだけ</span> | ローカル時刻を、秒の単位で表す別名。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::local_days`](chrono/local_days.md) | <span class="rank rank-rare">知ってるだけ</span> | ローカル時刻を、日の単位で表す別名（地域のカレンダーの日付）。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::utc_time`](chrono/utc_time.md) | <span class="rank rank-rare">知ってるだけ</span> | utc_clock の時点を表す別名（単位を選べる）。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::file_time`](chrono/file_time.md) | <span class="rank rank-rare">知ってるだけ</span> | file_clock の時点を表す別名（単位を選べる）。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::time_zone`](chrono/time_zone.md) | <span class="rank rank-rare">知ってるだけ</span> | 1 つのタイムゾーン（例: Asia/Tokyo）を表す型。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::locate_zone`](chrono/locate_zone.md) | <span class="rank rank-rare">知ってるだけ</span> | 名前から time_zone を取得する。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::current_zone`](chrono/current_zone.md) | <span class="rank rank-rare">知ってるだけ</span> | 今の環境のタイムゾーンを取得する。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::tzdb`](chrono/tzdb.md) | <span class="rank rank-rare">知ってるだけ</span> | タイムゾーンのデータベース（IANA）を表す型。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::tzdb_list`](chrono/tzdb_list.md) | <span class="rank rank-rare">知ってるだけ</span> | tzdb の更新履歴（世代ごとの一覧）を管理する型。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::get_tzdb`](chrono/get_tzdb.md) | <span class="rank rank-rare">知ってるだけ</span> | 現在のタイムゾーンデータベースを取得する。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::time_zone_link`](chrono/time_zone_link.md) | <span class="rank rank-rare">知ってるだけ</span> | 別名のタイムゾーン（古い名前から新しい名前への対応）を表す型。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::sys_info`](chrono/sys_info.md) | <span class="rank rank-rare">知ってるだけ</span> | ある UTC の時点での、時差・夏時間・略称の情報。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::local_info`](chrono/local_info.md) | <span class="rank rank-rare">知ってるだけ</span> | あるローカル時刻の時差情報（曖昧・存在しない場合も表す）。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::nonexistent_local_time`](chrono/nonexistent_local_time.md) | <span class="rank rank-rare">知ってるだけ</span> | 夏時間の切り替えで存在しないローカル時刻を変換したときの例外。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::ambiguous_local_time`](chrono/ambiguous_local_time.md) | <span class="rank rank-rare">知ってるだけ</span> | 夏時間の終わりで 2 回ある（曖昧な）ローカル時刻を変換したときの例外。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::leap_second`](chrono/leap_second.md) | <span class="rank rank-rare">知ってるだけ</span> | うるう秒の挿入日と値を表す型。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::get_leap_second_info`](chrono/get_leap_second_info.md) | <span class="rank rank-rare">知ってるだけ</span> | ある UTC の時点が、うるう秒の中か、それまでに何秒入ったかを調べる。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::parse`](chrono/parse.md) | <span class="rank rank-rare">知ってるだけ</span> | 文字列を書式に従って読み込み、chrono の型にするための入力マニピュレータ。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::from_stream`](chrono/from_stream.md) | <span class="rank rank-rare">知ってるだけ</span> | ストリームから書式に従って chrono の型を読み込む。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::to_stream`](chrono/to_stream.md) | <span class="rank rank-rare">知ってるだけ</span> | 書式に従って chrono の型をストリームに書き出す。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::abs`](chrono/abs.md) | <span class="rank rank-rare">知ってるだけ</span> | duration の絶対値を返す。 <span class="ver ver-17">C++17</span> |
| [`std::chrono::ceil`](chrono/ceil.md) | <span class="rank rank-rare">知ってるだけ</span> | duration / time_point を、指定した単位に切り上げる。 <span class="ver ver-17">C++17</span> |
| [`std::chrono::round`](chrono/round.md) | <span class="rank rank-rare">知ってるだけ</span> | duration / time_point を、指定した単位に四捨五入する。 <span class="ver ver-17">C++17</span> |
| [`std::chrono::is_clock`](chrono/is_clock.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が chrono の「時計」の条件を満たすかを調べる型特性。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::local_t`](chrono/local_t.md) | <span class="rank rank-rare">知ってるだけ</span> | 「どのタイムゾーンでもない、地域の時刻」を表す疑似の時計の型。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::choose`](chrono/choose.md) | <span class="rank rank-rare">知ってるだけ</span> | 曖昧なローカル時刻の変換で、どちらを選ぶかを指定する列挙型。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::reload_tzdb`](chrono/reload_tzdb.md) | <span class="rank rank-rare">知ってるだけ</span> | タイムゾーンのデータベースを、最新のものに読み込み直す。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::remote_version`](chrono/remote_version.md) | <span class="rank rank-rare">知ってるだけ</span> | OS が持つ、最新のタイムゾーンデータベースの版を返す。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::zoned_traits`](chrono/zoned_traits.md) | <span class="rank rank-rare">知ってるだけ</span> | zoned_time が、ゾーンの指定をどう解釈するかを決める特性。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::tai_time`](chrono/tai_time.md) | <span class="rank rank-rare">知ってるだけ</span> | tai_clock の時点（単位を選べる）を表す別名。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::tai_seconds`](chrono/tai_seconds.md) | <span class="rank rank-rare">知ってるだけ</span> | tai_clock の時点（秒単位）を表す別名。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::gps_time`](chrono/gps_time.md) | <span class="rank rank-rare">知ってるだけ</span> | gps_clock の時点（単位を選べる）を表す別名。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::gps_seconds`](chrono/gps_seconds.md) | <span class="rank rank-rare">知ってるだけ</span> | gps_clock の時点（秒単位）を表す別名。 <span class="ver ver-20">C++20</span> |
| [`std::chrono::utc_seconds`](chrono/utc_seconds.md) | <span class="rank rank-rare">知ってるだけ</span> | utc_clock の時点（秒単位）を表す別名。 <span class="ver ver-20">C++20</span> |

## 関数一覧

| 関数 | 重要度 | 何をする |
| --- | --- | --- |
| [`now`](chrono/steady_clock.md) | <span class="rank rank-must">必須</span> | 今の時点を取得 |
| [`count`](chrono/duration.md) | <span class="rank rank-must">必須</span> | duration を数値で取り出す |
| [`duration_cast`](chrono/duration_cast.md) | <span class="rank rank-often">よく使う</span> | 単位を変換する（切り捨て） |
| [`time_since_epoch`](chrono/time_point.md) | <span class="rank rank-sometimes">たまに</span> | 基準時刻からの経過 |
| [`std::this_thread::sleep_for`](../concurrency/this_thread/sleep_for.md) | <span class="rank rank-sometimes">たまに</span> | 指定時間だけ待つ |
| [`floor` / `ceil` / `round`](chrono/floor.md) | <span class="rank rank-rare">知ってるだけ</span> | 単位を変換する（丸め方を選ぶ） |
| [`zero` / `min` / `max`](chrono/duration.md) | <span class="rank rank-rare">知ってるだけ</span> | 0 / 最小 / 最大の duration |

## よくある使い方

### 1. 処理時間を測る

```cpp
#include <chrono>
#include <print>

int main() {
  auto start = std::chrono::steady_clock::now();

  long long sum = 0;
  for (int i = 0; i < 1000000; ++i) {
    sum += i;
  }

  auto end = std::chrono::steady_clock::now();
  auto elapsed = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
  std::println("合計 {} / かかった時間は 0 以上？ {}", sum, elapsed.count() >= 0);
}
```

```text title="実行結果"
合計 499999500000 / かかった時間は 0 以上？ true
```

実際の時間は環境によって変わるので、ここでは表示していません。`elapsed` を `std::println("{}", elapsed)` で出すと `123us` のように単位付きで表示されます。

### 2. デルタタイム（前のフレームからの経過秒）

```cpp
#include <chrono>
#include <print>
#include <thread>

int main() {
  using Clock = std::chrono::steady_clock;
  auto previous = Clock::now();

  for (int frame = 0; frame < 3; ++frame) {
    std::this_thread::sleep_for(std::chrono::milliseconds(16));  // 1 フレームぶんの処理のつもり

    auto now = Clock::now();
    float delta = std::chrono::duration<float>(now - previous).count();  // 秒（float）
    previous = now;
    std::println("frame {}: 0.016 秒以上？ {}", frame, delta >= 0.016f);
  }
}
```

```text title="実行結果"
frame 0: 0.016 秒以上？ true
frame 1: 0.016 秒以上？ true
frame 2: 0.016 秒以上？ true
```

### 3. 単位付きで書く

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono_literals;
  auto cooldown = 1500ms;
  auto total = cooldown + 2s;  // 単位が違っても足せる
  std::println("{} / {} ms", total, total.count());
}
```

```text title="実行結果"
3500ms / 3500 ms
```

## フラグ・オプション（単位の一覧）

| 型 | リテラル | 意味 |
| --- | --- | --- |
| `std::chrono::milliseconds` | `16ms` | ミリ秒（1/1000 秒） |
| `std::chrono::seconds` | `3s` | 秒 |
| `std::chrono::duration<float>` | | 秒（小数）。ゲームのデルタタイム |
| `std::chrono::microseconds` | `500us` | マイクロ秒（1/1,000,000 秒）。処理時間の計測 |
| `std::chrono::nanoseconds` | `100ns` | ナノ秒 |
| `std::chrono::minutes` | `5min` | 分 |
| `std::chrono::hours` | `2h` | 時間 |
| `std::chrono::days` / `weeks` / `months` / `years` | | 日・週・月・年 <span class="ver ver-20">C++20</span> |

時計の一覧です。

| 時計 | 重要度 | 巻き戻らない？ | 使う場面 |
| --- | --- | --- | --- |
| `steady_clock` | <span class="rank rank-must">必須</span> | ○ | 経過時間・フレーム時間 |
| `system_clock` | <span class="rank rank-sometimes">たまに</span> | × | 現在の日時、セーブの日付 |
| `high_resolution_clock` | <span class="rank rank-rare">知ってるだけ</span> | 実装による | 使わない |
| `utc_clock` / `tai_clock` / `gps_clock` / `file_clock` | <span class="rank rank-rare">知ってるだけ</span> | | 特殊な時刻系 <span class="ver ver-20">C++20</span> |

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    DWORD start = GetTickCount();  // Windows 専用、ミリ秒、精度が粗い
    clock_t c = clock();            // CPU 時間で、経過時間ではない
    ```

=== "今の書き方"

    ```cpp
    auto start = std::chrono::steady_clock::now();
    ```

## ゲームでの使いどころ

フレーム時間とデルタタイムの計測が基本です。`steady_clock::now()` を毎フレーム取って、前のフレームとの差を `duration<float>` で受ければ、秒の `float` が得られます。位置の更新は、これに速度を掛けて行います。

処理時間の計測にも使います。重そうな処理の前後で時刻を取り、差をログに出します。単位つきで書けるので、`16ms` や `3s` のように、読みやすくなります。

待ち時間やタイムアウトの指定、クールダウンの管理にも向いています。現在の日時が必要なら、`system_clock` を使います。計測には、巻き戻らない `steady_clock` を選びます。

## パフォーマンス

- `now()` は OS に問い合わせるので、1 フレームに何千回も呼ぶものではありません。フレームの最初に 1 回取って使い回します。
- duration の計算自体は整数の足し算と同じ速さです。

## よくあるミス

??? failure "count() の単位を勘違いする"
    `(end - start).count()` の単位は時計によって違います（ナノ秒のことが多い）。必ず `duration_cast` か `duration<float>` で単位を決めてから `count()` します。

??? failure "system_clock で計測する"
    時計の自動補正などで巻き戻ると、経過時間がマイナスになることがあります。計測は `steady_clock` です。

??? failure "float の秒を足し続けて誤差が溜まる"
    長時間のプレイ時間を `float` の秒で足し続けると、誤差で進み方がおかしくなります。合計は整数の `milliseconds` などで持ちます。

## 類似

| 名前 | 違い |
| --- | --- |
| `SDL_GetTicks` / `QueryPerformanceCounter` | OS・ライブラリ専用の時計 |
| [`std::format`](format.md) | `{:%H:%M}` などで時刻を整形できる |

## コンパイラ対応

C++11 からある機能です。日付（`year_month_day` など）と `println` での出力は C++20 で、主要なコンパイラの最近のバージョンで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 計測は `steady_clock::now()` の差
    - [x] 秒の float は `duration<float>(差).count()`
    - [x] 単位変換は `duration_cast`（切り捨て）
    - [x] `using namespace std::chrono_literals;` で `16ms` と書ける

## 関連ページ

- [cpprefjp: <chrono>](https://cpprefjp.github.io/reference/chrono.html)
- [cppreference: Date and time library](https://en.cppreference.com/w/cpp/chrono)
