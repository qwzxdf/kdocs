---
title: std::chrono::local_info
summary: "あるローカル時刻の時差情報（曖昧・存在しない場合も表す）。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::local_info

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

夏時間の切り替えでは、同じローカル時刻が 2 回ある（曖昧）か、1 回もない（存在しない）ことがあります。`local_info` は、そうした状況を `result` で示し、`first` / `second` に候補の情報を入れます。

!!! tip "ポイント"
    - `result` は `unique`・`nonexistent`・`ambiguous` のどれか。
    - `first` と `second` は `sys_info`。
    - 曖昧なら両方、そうでなければ `first` だけ有効。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::local_info {#local_info}

```cpp
struct local_info {
  static constexpr int unique = 0;
  static constexpr int nonexistent = 1;
  static constexpr int ambiguous = 2;
  int result;
  sys_info first;
  sys_info second;
};
```

- 戻り値: 状況と候補の情報
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;
  const auto* tz = locate_zone("Asia/Tokyo");
  auto info = tz->get_info(local_days{2024y / January / 1});
  std::println("{}", info.first.abbrev);
}
```

```text title="実行結果"
JST
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 切り替え日のスケジュールを調べる | `info.result == local_info::ambiguous` |

## よくあるミス

??? failure "結果を無視して変換する"
    曖昧・存在しない時刻を `to_sys` に渡すと例外です。先に `local_info` で確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`sys_info`](sys_info.md) | UTC 側の情報 |
| [`nonexistent_local_time`](nonexistent_local_time.md) | 存在しない時刻の例外 |
| [`ambiguous_local_time`](ambiguous_local_time.md) | 曖昧な時刻の例外 |

## コンパイラ対応

C++20 の機能です。GCC 14 以降、MSVC 19.29 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ローカル時刻の時差情報
    - [x] result で曖昧さを表す
    - [x] first / second に候補

## 関連ページ

- [cpprefjp: std::chrono::local_info](https://cpprefjp.github.io/reference/chrono/local_info.html)
- [cppreference: std::chrono::local_info](https://en.cppreference.com/w/cpp/chrono/local_info)
