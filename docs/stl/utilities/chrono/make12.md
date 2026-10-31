---
title: std::chrono::make12
summary: "24 時間制の時を、12 時間制の時（1〜12）に直す。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::make12

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

24 時間制の 15 時を、12 時間制の「3 時」に直したい。`std::chrono::make12` は、`hours`（0〜23）を、12 時間制の 1〜12 に直す関数です。0 時は 12 になり、12 時も 12 のままです。AM / PM は別に、`is_pm` で判定します。

!!! tip "ポイント"
    - 0 時 → 12、1〜11 時はそのまま、12 時 → 12、13〜23 時 → 1〜11
    - 戻り値は `hours`（1〜12）
    - AM か PM かは分からない。`is_am` / `is_pm` と組み合わせる
    - 逆変換は `make24`

!!! info "このページを読む前に"
    [`is_am`](is_am.md) と [`is_pm`](is_pm.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::make12 {#make12}

<span class="ver ver-20">C++20</span>

```cpp
constexpr hours make12(const hours& h) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `h` | `hours` | 24 時間制の時（0〜23） |

変換の規則は、次のとおりです。

| 24 時間制 | 12 時間制 |
| --- | --- |
| 0 | 12（AM） |
| 1〜11 | 1〜11（AM） |
| 12 | 12（PM） |
| 13〜23 | 1〜11（PM） |

深夜 0 時は「12 AM」、正午は「12 PM」と書く習慣に合わせています。範囲外の値を渡すと、結果は規定されていません。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  for (const int h : {0, 1, 11, 12, 13, 23}) {
    std::println("{:2} 時 → {:2} {}", h, make12(hours{h}).count(),
                 is_pm(hours{h}) ? "PM" : "AM");
  }
}
```

```text title="実行結果"
 0 時 → 12 AM
 1 時 →  1 AM
11 時 → 11 AM
12 時 → 12 PM
13 時 →  1 PM
23 時 → 11 PM
```

## ゲームでの使いどころ

英語向けの時刻表示で、12 時間制にするときに使います。`std::format` の `{:%I %p}` でも同じ表示にできるので、時刻全体を書式にかけるなら、そちらが楽です。

## よくあるミス

??? failure "0 時を 0 と表示する"
    12 時間制では 12 です。自分で `h % 12` と書くと、0 時と 12 時が 0 になってしまいます。`make12` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`make24`](make24.md) | 逆変換 |
| [`is_am`](is_am.md) / [`is_pm`](is_pm.md) | 午前か午後か |
| [`hh_mm_ss`](hh_mm_ss.md) | 時・分・秒に分解する |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: make12](https://cpprefjp.github.io/reference/chrono/make12.html)
- [cppreference: std::chrono::make12](https://en.cppreference.com/w/cpp/chrono/make12)
