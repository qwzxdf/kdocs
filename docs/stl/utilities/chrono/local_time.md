---
title: std::chrono::local_time
summary: "タイムゾーンのない、地域の時刻を表す別名。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::local_time

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

`std::chrono::local_time<Duration>` は、壁掛け時計に書かれた時刻をそのまま表す型です。`time_point<local_t, Duration>` の別名で、タイムゾーンが決まっていないので、特定の瞬間とは結びついていません。「毎朝 5 時」のような設計値の保存や、日付と時刻の組み立てに使います。

!!! tip "ポイント"
    - `time_point<local_t, Duration>` の別名
    - 現在時刻は取れない。`zoned_time` の `get_local_time()` で得る
    - `sys_time` との混用は、型エラーで防がれる
    - 特定の瞬間にするには、タイムゾーンが要る

!!! info "このページを読む前に"
    [`local_t`](local_t.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::local_time {#local_time}

<span class="ver ver-20">C++20</span>

```cpp
template <class Duration>
using local_time = time_point<local_t, Duration>;

using local_seconds = local_time<seconds>;
using local_days    = local_time<days>;
```

`local_days` と時・分・秒を組み合わせて、日付つきの壁掛け時刻が作れます。`local_days{2026y/March/9} + 14h + 30min` で、「2026 年 3 月 9 日 14:30」を表します。

タイムゾーンの影響で、同じ `local_time` が、その地域で 2 回現れる（夏時間の終わり）ことも、存在しない（夏時間の始まり）こともあります。`time_zone::to_sys` を呼ぶとき、そのような時刻は例外（`ambiguous_local_time`、`nonexistent_local_time`）になります。日本のように、夏時間のない地域では、起きません。

書式は `{:%F %T}` で、`sys_time` と同じです。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  const local_time<minutes> lt = local_days{2026y / March / 9} + 14h + 30min;
  std::println("{:%F %R}", lt);

  // 日付と時刻に分ける
  const local_days day = floor<days>(lt);
  const hh_mm_ss time{lt - day};
  std::println("{} 時 {} 分", time.hours().count(), time.minutes().count());
}
```

```text title="実行結果"
2026-03-09 14:30
14 時 30 分
```

`lt - day` で、日の始まりからの経過時間が取れます。`hh_mm_ss` で、時・分に分解しました。

## ゲームでの使いどころ

イベント開始の「毎日 5 時」「毎週月曜 4 時」を `local_time` で持ち、プレイヤーのタイムゾーンで、実際の UTC に直します。

## よくあるミス

??? failure "local_time と sys_time を直接比べる"
    型が違うので、コンパイルできません。タイムゾーンを通して、同じ種類の時点にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`local_t`](local_t.md) | この別名の元になる型 |
| [`local_seconds`](local_seconds.md) | 秒の単位 |
| [`local_days`](local_days.md) | 日の単位 |
| [`sys_time`](sys_time.md) | UTC の時点 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: local_time](https://cpprefjp.github.io/reference/chrono/local_t.html)
- [cppreference: std::chrono::local_time](https://en.cppreference.com/w/cpp/chrono/local_t)
