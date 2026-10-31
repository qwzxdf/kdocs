---
title: std::chrono::local_seconds
summary: "ローカル時刻を、秒の単位で表す別名。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::local_seconds

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

`std::chrono::local_seconds` は、タイムゾーンのない地域の時刻を、秒の細かさで表す型です。`local_time<seconds>` の別名で、`zoned_time` の `get_local_time()` を秒にそろえたものを受けるときなどに使います。

!!! tip "ポイント"
    - `local_time<seconds>` の別名
    - `local_days` に時・分・秒を足して作る
    - `zoned_time` から現在のローカル時刻を取るときの受け皿
    - 書式は `{:%F %T}`

!!! info "このページを読む前に"
    [`local_time`](local_time.md) と [`zoned_time`](zoned_time.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::local_seconds {#local_seconds}

<span class="ver ver-20">C++20</span>

```cpp
using local_seconds = local_time<seconds>;
```

現在のローカル時刻を秒で取るには、`zoned_time` を通します。

```cpp
const zoned_time zt{current_zone(), system_clock::now()};
const local_seconds now = floor<seconds>(zt.get_local_time());
```

`get_local_time()` はナノ秒に近い細かさなので、`floor<seconds>` で秒にそろえます。

`local_seconds` は、`sys_seconds` とは別の型です。UTC とローカルを取り違える事故が起きません。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  const local_seconds t = local_days{2026y / January / 1} + 9h + 30min + 15s;
  std::println("{:%F %T}", t);

  // 日付と時刻に分解
  const local_days d = floor<days>(t);
  const hh_mm_ss hms{t - d};
  std::println("{:02}:{:02}:{:02}", hms.hours().count(), hms.minutes().count(),
               hms.seconds().count());
}
```

```text title="実行結果"
2026-01-01 09:30:15
09:30:15
```

## ゲームでの使いどころ

ログイン画面の「現在時刻」の表示など、プレイヤーのタイムゾーンで見せる時刻を、秒の細かさで扱います。

## よくあるミス

??? failure "sys_seconds に代入しようとする"
    型が違うので、コンパイルできません。`time_zone::to_sys` で変換します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`local_time`](local_time.md) | 単位を選べる元の別名 |
| [`sys_seconds`](sys_seconds.md) | UTC の時点 |
| [`zoned_time`](zoned_time.md) | タイムゾーンつきの時点 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: local_seconds](https://cpprefjp.github.io/reference/chrono/local_t.html)
- [cppreference: std::chrono::local_seconds](https://en.cppreference.com/w/cpp/chrono/local_t)
