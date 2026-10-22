---
title: std::chrono::years
summary: "年（平均の長さ）を数える duration の別名。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::years

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

時間の長さを扱うとき、`duration<long long, std::ratio<1, 1000>>` のような書き方は長すぎます。標準は、よく使う単位に名前をつけています。`std::chrono::years` は、年（平均の長さ）を数える `duration` の別名です。

!!! tip "ポイント"
    - 1 つぶんの長さは 31,556,952 秒（約 365.2425 日）。
    - `count()` で数を取り出し、`duration_cast` で別の単位に変える。
    - リテラルでも書ける（[リテラル](literals.md) を参照）。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::years {#years}

```cpp
using years = duration</* 整数（17 ビット以上） */, ratio<31556952>>;
```

- 戻り値: `years{n}` は 年（平均の長さ）を n 個ぶん持つ duration
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  std::println("{}", std::chrono::duration_cast<std::chrono::days>(std::chrono::years{1}).count());
}
```

```text title="実行結果"
365
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 経過時間の指定 | `std::chrono::years{値}` |

## よくあるミス

??? failure "整数に切り捨てられる"
    整数の `duration` に `duration_cast` で大きい単位へ直すと、小数点以下は切り捨てられます。小数で受けたいなら `duration<double>` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`duration`](duration.md) | 時間の長さの型 |
| [`duration_cast`](duration_cast.md) | 単位を変換する |
| [`literals`](literals.md) | `ms` / `s` などの書き方 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 年（平均の長さ）を数える duration の別名
    - [x] `count()` で数を取り出す
    - [x] 単位の変換は duration_cast

## 関連ページ

- [cpprefjp: std::chrono::years](https://cpprefjp.github.io/reference/chrono/duration.html)
- [cppreference: std::chrono::years](https://en.cppreference.com/w/cpp/chrono/duration)
