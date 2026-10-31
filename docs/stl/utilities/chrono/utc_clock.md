---
title: std::chrono::utc_clock
summary: "うるう秒を数に入れた、協定世界時（UTC）の時計。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::utc_clock

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

普段の日付の計算（`system_clock`）では、1 日は必ず 86400 秒です。ところが現実の UTC には、不定期に「うるう秒」が挿入され、その日は 86401 秒になります。2 つの時刻の本当の経過時間を知りたいときは、うるう秒も数に入れる必要があります。`std::chrono::utc_clock` は、うるう秒を数えながら進む、UTC の時計です。

!!! tip "ポイント"
    - 起点は `system_clock` と同じ 1970-01-01 00:00:00 UTC
    - うるう秒を挿入した日に、23:59:60 という秒が現れる
    - `sys_time` との変換は `clock_cast`、または `utc_clock::to_sys` / `from_sys`
    - 日常のゲームでは `system_clock` で足りる。精密な経過時間が要るときだけ

!!! info "このページを読む前に"
    [`system_clock`](system_clock.md) と [`leap_second`](leap_second.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::utc_clock {#utc_clock}

<span class="ver ver-20">C++20</span>

```cpp
class utc_clock {
 public:
  using rep = /* 符号つき算術型 */;
  using period = std::nano;
  using duration = chrono::duration<rep, period>;
  using time_point = chrono::time_point<utc_clock>;
  static constexpr bool is_steady = false;

  static time_point now();
  template <class Duration>
  static sys_time<common_type_t<Duration, seconds>> to_sys(const utc_time<Duration>& t);
  template <class Duration>
  static utc_time<common_type_t<Duration, seconds>> from_sys(const sys_time<Duration>& t);
};
```

`utc_clock` の秒数は、`system_clock` より、挿入されたうるう秒の分だけ大きくなります。1972 年から 2017 年までに 27 回のうるう秒が入ったので、2017 年以降の同じ瞬間は、`utc_time` のほうが 27 秒大きい値を持ちます。

`from_sys` と `to_sys` で、`sys_time` と相互に変換します。うるう秒の最中（23:59:60）の `utc_time` を `sys_time` に直すと、1 つ前の秒にまとめられます。うるう秒の一覧は、時刻のデータベースが持っていて、OS が更新します。

`is_steady` は偽です。`now()` を 2 回呼んだ差を、経過時間の計測に使うのは、`steady_clock` にします。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  // 2026-01-01 の system_clock と utc_clock の差は、挿入済みのうるう秒の数
  const sys_days day = 2026y / January / 1;
  const utc_seconds u = clock_cast<utc_clock>(day);
  const seconds diff = u.time_since_epoch() - day.time_since_epoch();
  std::println("うるう秒の累計: {} 秒", diff.count());

  // 1970 年の時点では、まだうるう秒はない
  const sys_days epoch{};
  const utc_seconds ue = clock_cast<utc_clock>(epoch);
  std::println("1970-01-01 の差: {} 秒", (ue.time_since_epoch()).count());
}
```

```text title="実行結果"
うるう秒の累計: 27 秒
1970-01-01 の差: 0 秒
```

## ゲームでの使いどころ

ゲームではほぼ使いません。科学技術計算や、GPS と連動する機器との時刻合わせなど、うるう秒まで数えたい場面で使います。

## よくあるミス

??? failure "経過時間の計測に使う"
    システム時計の調整で戻ることがあります。`steady_clock` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`system_clock`](system_clock.md) | うるう秒を数えない |
| [`tai_clock`](tai_clock.md) | うるう秒の影響を受けない、連続した時間 |
| [`gps_clock`](gps_clock.md) | GPS の時間 |
| [`clock_cast`](clock_cast.md) | 時計どうしの変換 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: utc_clock](https://cpprefjp.github.io/reference/chrono/utc_clock.html)
- [cppreference: std::chrono::utc_clock](https://en.cppreference.com/w/cpp/chrono/utc_clock)
