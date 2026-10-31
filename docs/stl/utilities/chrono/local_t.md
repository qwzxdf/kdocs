---
title: std::chrono::local_t
summary: "「どのタイムゾーンでもない、地域の時刻」を表す疑似の時計の型。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::local_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

「2026 年 1 月 1 日 9 時」と言ったとき、それが日本時間なのか UTC なのかは、タイムゾーンを決めるまで分かりません。タイムゾーンを決める前の、壁掛け時計の表記そのものを表すために、`std::chrono::local_t` という、時計に似た型が用意されています。実際の時計ではないので、`now()` は持ちません。`time_point<local_t, Duration>` の形で、`local_time` として使います。

!!! tip "ポイント"
    - `local_t` は、タイムゾーンなしの時刻を表すための、時計の代わりの型
    - `now()` がない。現在時刻は取れない
    - `local_time<Duration>` は `time_point<local_t, Duration>` の別名
    - タイムゾーンと組み合わせて、初めて特定の瞬間になる

!!! info "このページを読む前に"
    [`system_clock`](system_clock.md) と [`time_zone`](time_zone.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::local_t {#local_t}

<span class="ver ver-20">C++20</span>

```cpp
struct local_t {};
template <class Duration>
using local_time = time_point<local_t, Duration>;
```

`local_t` は、`time_point` の第 1 引数に入れるための型で、`is_clock_v<local_t>` は偽です。`now()` や `is_steady` がないからです。

役割は、型で区別することです。UTC の時点（`sys_time`）とタイムゾーンなしの時刻（`local_time`）を混ぜて比べたり、足したりすることは、型エラーになります。「9 時」を UTC として扱ってしまう事故を、コンパイル時に防ぎます。

`local_time` を、特定の瞬間（`sys_time`）に直すには、タイムゾーンが必要です。`time_zone::to_sys(local_time)` か、`zoned_time` を使います。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>
#include <type_traits>

int main() {
  using namespace std::chrono;

  static_assert(std::is_same_v<local_seconds, local_time<seconds>>);
  std::println("local_t は時計ではない: {}", !is_clock_v<local_t>);

  // 壁掛け時計の表記: 2026-01-01 09:00:00
  const local_seconds wall = local_days{2026y / January / 1} + 9h;
  std::println("{:%F %T}", wall);
}
```

```text title="実行結果"
local_t は時計ではない: true
2026-01-01 09:00:00
```

`local_days{...} + 9h` で、日付に 9 時間を足して、9 時という壁掛け時計の表記を作りました。タイムゾーンはまだ決まっていません。

## ゲームでの使いどころ

「毎日朝 5 時にリセット」のような、地域の時刻で決める設計値を持つときに使います。タイムゾーンを決めると、実際の UTC の瞬間が求まります。

## よくあるミス

??? failure "local_time に now() を期待する"
    `local_t` は時計ではありません。現在時刻は `zoned_time{current_zone(), system_clock::now()}` で得ます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`local_time`](local_time.md) | `local_t` の時点を表す別名 |
| [`sys_time`](sys_time.md) | UTC の時点 |
| [`zoned_time`](zoned_time.md) | タイムゾーンつきの時点 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: local_t](https://cpprefjp.github.io/reference/chrono/local_t.html)
- [cppreference: std::chrono::local_t](https://en.cppreference.com/w/cpp/chrono/local_t)
