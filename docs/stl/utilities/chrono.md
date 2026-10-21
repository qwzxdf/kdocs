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

`std::chrono` は、**時間の長さ・時刻・時計を扱うライブラリ**です。「何秒か」を表す `duration`、「ある時点」を表す `time_point`、今の時刻を教えてくれる「時計」（clock）の 3 つが中心です。単位（秒・ミリ秒など）を型で区別するので、「ミリ秒のつもりで秒を渡した」ような間違いがコンパイル時に見つかります。

!!! tip "ポイント"
    - <strong>フレーム時間・処理時間の計測は `std::chrono::steady_clock::now()` の差。</strong> 時計が巻き戻らないので安全。
    - 秒の小数（`float`）が欲しいなら `std::chrono::duration<float>(差).count()`。
    - `using namespace std::chrono_literals;` で `16ms`、`3s` のように書ける。
    - カレンダーの日付・現在時刻の表示は `system_clock`。

## 主な型

| 型 | 重要度 | 何を表す |
| --- | --- | --- |
| [`steady_clock`](chrono/steady_clock.md) | <span class="rank rank-must">必須</span> | 巻き戻らない時計（計測用） |
| [`duration`](chrono/duration.md) | <span class="rank rank-must">必須</span> | 時間の長さ（`milliseconds` など） |
| [`time_point`](chrono/time_point.md) | <span class="rank rank-often">よく使う</span> | ある時点 |
| [`system_clock`](chrono/system_clock.md) | <span class="rank rank-sometimes">たまに</span> | 現実の時刻（カレンダー） |
| [`high_resolution_clock`](chrono/high_resolution_clock.md) | <span class="rank rank-rare">知ってるだけ</span> | 一番細かい時計（中身は上のどちらか） |

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

| 場面 | 例 |
| --- | --- |
| デルタタイム | `duration<float>(now - prev).count()` |
| クールダウン | `now >= last_used + 1500ms` |
| 処理時間の計測（プロファイル） | `duration_cast<microseconds>(end - start)` |
| プレイ時間 | `seconds` で保存して `hh:mm:ss` で表示 |
| セーブの日時 | `system_clock::now()` |

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
