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

「午後 3 時」を内部の時刻に直すには、24 時間制にします。`make24(hours{3}, true)` は `hours{15}` です（2 つ目の引数が「午後か」）。

!!! tip "ポイント"
    - 2 つ目の引数が `true` なら午後。
    - 12 時午後は 12 時、12 時午前は 0 時。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::make24 {#make24}

```cpp
constexpr hours make24(const hours& h, bool is_pm) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `h` | hours | 12 時間制の時（1〜12） |
| `is_pm` | bool | 午後なら `true` |

- 戻り値: 24 時間制の時（0〜23）の `hours`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;
  std::println("{}", make24(hours{3}, true).count());
  std::println("{}", make24(hours{12}, false).count());
}
```

```text title="実行結果"
15
0
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ユーザーが入力した 12 時間制の時刻を直す | `make24(hours{h}, pm)` |

## よくあるミス

??? failure "12 時の扱い"
    午前 12 時は 0 時、午後 12 時は 12 時です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`make12`](make12.md) | 逆の変換 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 12 → 24 時間制
    - [x] 2 つ目は午後か
    - [x] 12 時の扱いに注意

## 関連ページ

- [cpprefjp: std::chrono::make24](https://cpprefjp.github.io/reference/chrono/make24.html)
- [cppreference: std::chrono::make24](https://en.cppreference.com/w/cpp/chrono/hour_of_day/make24)
