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

`local_time` は、`system_clock`（UTC 基準）とは別に、「タイムゾーンが決まっていない時刻」を表します。その型の目印になる疑似の時計が `local_t` です。実際の時計ではなく、`now()` はありません。`time_zone` を通して、`sys_time` と変換して初めて、特定の瞬間になります。

!!! tip "ポイント"
    - `local_time<Duration>` = `time_point<local_t, Duration>`。
    - 時計として `now()` は持たない。
    - `time_zone::to_sys` で UTC の時点に変換する。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::chrono::local_t {#local_t}

```cpp
struct local_t {};
```

- 戻り値: なし（目印の型）
- 計算量: なし


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>
#include <type_traits>

int main() {
  using LT = std::chrono::local_time<std::chrono::seconds>;
  std::println("{}", std::is_same_v<LT, std::chrono::time_point<std::chrono::local_t, std::chrono::seconds>>);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 「毎日朝 6 時」のような地域の時刻を扱う | `std::chrono::local_days{...} + 6h` |

## よくあるミス

??? failure "実際の瞬間と思う"
    `local_time` は、タイムゾーンが決まるまで、特定の瞬間ではありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`local_time`](local_time.md) | ローカル時刻の別名 |
| [`time_zone`](time_zone.md) | 変換する |

## コンパイラ対応

C++20 の機能です。GCC 13 以降、MSVC 19.29 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] タイムゾーンなしの時刻の目印
    - [x] now() を持たない
    - [x] time_zone で変換

## 関連ページ

- [cpprefjp: std::chrono::local_t](https://cpprefjp.github.io/reference/chrono/local_t.html)
- [cppreference: std::chrono::local_t](https://en.cppreference.com/w/cpp/chrono/local_t)
