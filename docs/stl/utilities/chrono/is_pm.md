---
title: std::chrono::is_pm
summary: "24 時間制の時刻が午後かを調べる。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::is_pm

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

時刻を「午前 / 午後」で表示するとき、24 時間制の時を 12 より大きいかで判定するのは手間です。`is_pm` が、午前（0〜11 時）か午後（12〜23 時）かを教えてくれます。

!!! tip "ポイント"
    - 引数は `hours`（0〜23）。
    - `make12` と組み合わせて 12 時間制の表示を作る。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::is_pm {#is_pm}

```cpp
constexpr bool is_pm(const hours& h) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `h` | hours | 24 時間制の時（0〜23） |

- 戻り値: 午後なら `true`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  std::println("{}", std::chrono::is_pm(std::chrono::hours{13}));
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 12 時間制の表示 | `is_am(h) ? "AM" : "PM"` |

## よくあるミス

??? failure "範囲外の時を渡す"
    0〜23 以外の値は未定義です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`make12`](make12.md) | 12 時間制に直す |
| [`make24`](make24.md) | 24 時間制に直す |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 24 時間制の時刻が午後かを調べる
    - [x] 引数は 0〜23 の hours
    - [x] make12 とセットで使う

## 関連ページ

- [cpprefjp: std::chrono::is_pm](https://cpprefjp.github.io/reference/chrono/is_pm.html)
- [cppreference: std::chrono::is_pm](https://en.cppreference.com/w/cpp/chrono/hour_of_day/is_am)
