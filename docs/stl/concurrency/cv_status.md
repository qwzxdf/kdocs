---
title: std::cv_status
summary: "条件変数の待機が、通知で終わったか、時間切れで終わったかを表す列挙型。"
order: 900
tags:
  - 並行処理
---

# std::cv_status

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <condition_variable>`
</div>

`cv.wait_for(lk, 時間)` は、通知を受けて起きた場合と、時間切れで起きた場合のどちらもあります。どちらだったかを `cv_status::no_timeout`（通知）か `cv_status::timeout`（時間切れ）で返します。述語つきの版は `bool` を返します。

!!! tip "ポイント"
    - `wait_for` / `wait_until` の戻り値（述語なしの版）。
    - `timeout` と `no_timeout` の 2 つ。
    - 偽の起床（spurious wakeup）で `no_timeout` が返ることがある。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::cv_status {#cv_status}

```cpp
enum class cv_status { no_timeout, timeout };
```

- 戻り値: なし（列挙型）
- 計算量: なし


## 実際に動かしてみる

```cpp
#include <chrono>
#include <condition_variable>
#include <mutex>
#include <print>

int main() {
  using namespace std::chrono_literals;
  std::mutex m;
  std::condition_variable cv;
  std::unique_lock lk(m);
  std::println("{}", cv.wait_for(lk, 10ms) == std::cv_status::timeout);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 通知を待つが、一定時間でなだめる | `if (cv.wait_for(lk, 100ms) == std::cv_status::timeout) { ... }` |

## よくあるミス

??? failure "`no_timeout` なら条件が成立したと思う"
    偽の起床でも `no_timeout` が返ります。条件は述語で確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`condition_variable`](condition_variable.md) | 条件変数 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 待機の結果を表す列挙型
    - [x] timeout / no_timeout
    - [x] 偽の起床に注意

## 関連ページ

- [cpprefjp: std::cv_status](https://cpprefjp.github.io/reference/condition_variable/cv_status.html)
- [cppreference: std::cv_status](https://en.cppreference.com/w/cpp/thread/cv_status)
