---
title: std::chrono::make24
summary: "12 時間制の時を、24 時間制の時（0〜23）に直す。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::make24

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

「午後 3 時」を 24 時間制の 15 時に直したい。`std::chrono::make24` は、12 時間制の時（1〜12）と、午後かどうかの `bool` を受け取って、24 時間制の `hours`（0〜23）を返す関数です。`make12` の逆変換です。

!!! tip "ポイント"
    - 第 1 引数は 12 時間制の時（1〜12）、第 2 引数は午後なら `true`
    - 12 AM は 0 時、12 PM は 12 時
    - 戻り値は `hours`（0〜23）
    - 入力が 1〜12 の範囲外だと、結果は規定されない

!!! info "このページを読む前に"
    [`make12`](make12.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::make24 {#make24}

<span class="ver ver-20">C++20</span>

```cpp
constexpr hours make24(const hours& h, bool is_pm) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `h` | `hours` | 12 時間制の時（1〜12） |
| `is_pm` | `bool` | 午後なら `true` |

変換の規則は、次のとおりです。

| 12 時間制 | `is_pm` | 24 時間制 |
| --- | --- | --- |
| 12 | `false` | 0 |
| 1〜11 | `false` | 1〜11 |
| 12 | `true` | 12 |
| 1〜11 | `true` | 13〜23 |

12 時の扱いが特別です。「12 AM」は深夜の 0 時、「12 PM」は正午の 12 時になります。この例外のために、`h + (is_pm ? 12 : 0)` と単純に書くと、12 PM が 24 時になる間違いが起きます。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  std::println("12 AM → {}", make24(hours{12}, false).count());
  std::println(" 3 AM → {}", make24(hours{3}, false).count());
  std::println("12 PM → {}", make24(hours{12}, true).count());
  std::println(" 3 PM → {}", make24(hours{3}, true).count());
}
```

```text title="実行結果"
12 AM → 0
 3 AM → 3
12 PM → 12
 3 PM → 15
```

## ゲームでの使いどころ

プレイヤーが入力した「午後 3 時」を、内部の 24 時間制の時刻にそろえるときに使います。12 時の例外を自分で書かずに済みます。

## よくあるミス

??? failure "12 PM を 24 時にしてしまう"
    単純に 12 を足すと、12 PM が 24 になります。`make24` が 12 の例外を扱います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`make12`](make12.md) | 逆変換 |
| [`is_pm`](is_pm.md) | 午後かを調べる |
| [`hours`](hours.md) | 時間の単位 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: make24](https://cpprefjp.github.io/reference/chrono/make24.html)
- [cppreference: std::chrono::make24](https://en.cppreference.com/w/cpp/chrono/make24)
