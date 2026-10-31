---
title: std::chrono::file_time
summary: "file_clock の時点を表す別名（単位を選べる）。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::file_time

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

`std::chrono::file_time<Duration>` は、`file_clock` の時点を `Duration` の単位で表す型です。`time_point<file_clock, Duration>` の別名で、`std::filesystem::file_time_type` は、この `file_time` の一種です。

!!! tip "ポイント"
    - `time_point<file_clock, Duration>` の別名
    - `filesystem::file_time_type` は `file_time<環境ごとの duration>`
    - `sys_time` に直すには `clock_cast<system_clock>`
    - 秒に落として使うなら `floor<seconds>`

!!! info "このページを読む前に"
    [`file_clock`](file_clock.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::file_time {#file_time}

<span class="ver ver-20">C++20</span>

```cpp
template <class Duration>
using file_time = time_point<file_clock, Duration>;
```

`file_time_type` の `Duration` は環境で違い、MSVC では 100 ナノ秒単位、libstdc++ ではナノ秒単位です。ファイルの更新日時を比べるだけなら、型を気にせず、`auto` で受けます。

ファイルの更新日時を、ログなどに秒の細かさで表示するときは、次の順に変換します。

1. `clock_cast<system_clock>` で、`sys_time` にする
2. `floor<seconds>` で、秒にそろえる
3. `{:%F %T}` で書式にかける

## 実際に動かしてみる

```cpp
#include <chrono>
#include <filesystem>
#include <print>

int main() {
  using namespace std::chrono;

  // file_time_type は file_time の一種
  static_assert(std::is_same_v<std::filesystem::file_time_type::clock, file_clock>);

  // 現在のファイル時刻を秒にそろえる
  const auto ft = std::filesystem::file_time_type::clock::now();
  const sys_seconds s = floor<seconds>(clock_cast<system_clock>(ft));
  std::println("2026 年以降: {}", s >= sys_days{2026y / January / 1});
}
```

```text title="実行結果"
2026 年以降: true
```

## ゲームでの使いどころ

アセットが更新されたかを、保存しておいた更新日時と比べて調べます。

## よくあるミス

??? failure "file_time どうしの差の単位を決め打ちする"
    `file_time_type` の `Duration` は環境で違います。ミリ秒などで使うなら、`duration_cast` します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`file_clock`](file_clock.md) | この別名の元になる時計 |
| [`sys_time`](sys_time.md) | `system_clock` の時点 |
| [`clock_cast`](clock_cast.md) | 時計どうしを変換する |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: file_time](https://cpprefjp.github.io/reference/chrono/file_clock.html)
- [cppreference: std::chrono::file_time](https://en.cppreference.com/w/cpp/chrono/file_clock)
