---
title: std::chrono::time_point_cast
summary: "time_point の単位を、別の単位に変換する（切り捨て）。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::time_point_cast

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

`time_point` の中の `duration` の単位を変えたいことがあります。たとえばミリ秒の時点を秒の時点にするときです。`time_point_cast<ToDuration>(tp)` が、単位を変えた `time_point` を作ります。

!!! tip "ポイント"
    - `duration_cast` の `time_point` 版。
    - デフォルトでは 0 方向への切り捨て。
    - 丸めたいときは `floor` / `ceil` / `round`。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::time_point_cast {#time_point_cast}

```cpp
template <class ToDuration, class Clock, class Duration>
constexpr time_point<Clock, ToDuration> time_point_cast(const time_point<Clock, Duration>& t);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ToDuration` | テンプレート引数 | 変換後の `duration` |
| `t` | time_point | 変換する時点 |

- 戻り値: 単位を変えた `time_point`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;
  system_clock::time_point tp{milliseconds{1500}};
  auto s = time_point_cast<seconds>(tp);
  std::println("{}", s.time_since_epoch().count());
}
```

```text title="実行結果"
1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ミリ秒の時刻を秒の精度に落とす | `time_point_cast<seconds>(tp)` |

## よくあるミス

??? failure "負の時刻の丸め"
    切り捨ては 0 方向です。負の時刻では「小さいほう」にはなりません。小さいほうへ丸めるなら `floor` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`duration_cast`](duration_cast.md) | duration の変換 |
| [`floor`](floor.md) | 小さいほうへ丸める |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] time_point の単位を変える
    - [x] 0 方向へ切り捨て
    - [x] 丸め方を選ぶなら floor / ceil / round

## 関連ページ

- [cpprefjp: std::chrono::time_point_cast](https://cpprefjp.github.io/reference/chrono/time_point_cast.html)
- [cppreference: std::chrono::time_point_cast](https://en.cppreference.com/w/cpp/chrono/time_point_cast)
