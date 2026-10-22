---
title: std::chrono::sys_info
summary: "ある UTC の時点での、時差・夏時間・略称の情報。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::sys_info

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

あるゾーンの「ある瞬間」の時差（UTC との差）や、夏時間かどうか、略称（JST など）を知りたいことがあります。`time_zone::get_info(sys_time)` が返す `sys_info` に入っています。

!!! tip "ポイント"
    - `offset`（UTC との差）、`save`（夏時間のずれ）、`abbrev`（略称）をもつ。
    - `begin` と `end` は、この情報が有効な期間。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::sys_info {#sys_info}

```cpp
struct sys_info {
  sys_seconds begin;
  sys_seconds end;
  seconds offset;
  minutes save;
  string abbrev;
};
```

- 戻り値: 時差などの情報
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;
  const auto* tz = locate_zone("Asia/Tokyo");
  auto info = tz->get_info(sys_days{2024y / January / 1});
  std::println("{} {}", info.offset.count(), info.abbrev);
}
```

```text title="実行結果"
32400 JST
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| プレイヤーの時差を表示 | `tz->get_info(now).offset` |

## よくあるミス

??? failure "夏時間を考えない"
    `offset` には夏時間のずれが含まれます。`save` が 0 でないときは夏時間の最中です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`local_info`](local_info.md) | ローカル時刻から調べる |
| [`time_zone`](time_zone.md) | ゾーン |

## コンパイラ対応

C++20 の機能です。GCC 14 以降、MSVC 19.29 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] UTC 時点の時差情報
    - [x] offset / save / abbrev
    - [x] get_info で得る

## 関連ページ

- [cpprefjp: std::chrono::sys_info](https://cpprefjp.github.io/reference/chrono/sys_info.html)
- [cppreference: std::chrono::sys_info](https://en.cppreference.com/w/cpp/chrono/sys_info)
