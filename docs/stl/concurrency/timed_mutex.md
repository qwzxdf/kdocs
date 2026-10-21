---
title: std::timed_mutex
summary: "時間を決めて待てる鍵。取れなければ諦められる。"
order: 85
tags:
  - 並行処理
---

# std::timed_mutex

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="perf perf-2">△ やや重い</span>
<span class="ver ver-11">C++11</span>
`#include <mutex>`
</div>

`std::timed_mutex` は、**「何ミリ秒まで待つ」と時間を決めて鍵を取りに行ける**mutex です。普通の `mutex` の `lock()` は取れるまで待ち続けますが、`try_lock_for` なら時間切れで諦めて、別の処理に回れます。

!!! tip "ポイント"
    - `try_lock_for(duration)` で、時間つきで待つ。取れたら `true`。
    - `try_lock_until(time_point)` なら、時刻で指定する。
    - 取れたら必ず `unlock()`（または `unique_lock` に `adopt_lock` で渡す）。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### try_lock_for {#try_lock_for}

```cpp
template <class Rep, class Period>
bool try_lock_for(const std::chrono::duration<Rep, Period>& timeout);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `timeout` | `duration` | 最大で待つ時間 |

- 戻り値: 鍵が取れれば `true`、時間切れなら `false`
- 計算量: 最大で `timeout`

```cpp
#include <chrono>
#include <mutex>
#include <print>

int main() {
  using namespace std::chrono_literals;

  std::timed_mutex m;
  if (m.try_lock_for(100ms)) {   // 誰も持っていないので、すぐ取れる
    std::println("取れた");
    m.unlock();
  }
}
```

```text title="実行結果"
取れた
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ロードのスレッドが鍵を持ったままの間、メインスレッドは 5ms だけ待ってスキップする | `if (m.try_lock_for(5ms)) { ... m.unlock(); }` |

## よくあるミス

??? failure "時間切れを無視して使う"
    `try_lock_for` の戻り値が `false` のとき、鍵は取れていません。そのまま共有データに触ると競合します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::mutex`](mutex.md) | 時間指定のない鍵 |
| [`std::recursive_mutex`](recursive_mutex.md) | 同じスレッドなら何度でも |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 時間を決めて待てる mutex
    - [x] `try_lock_for` / `try_lock_until`
    - [x] 取れたら必ず `unlock`

## 関連ページ

- [cpprefjp: std::timed_mutex](https://cpprefjp.github.io/reference/mutex/timed_mutex.html)
- [cppreference: std::timed_mutex](https://en.cppreference.com/w/cpp/thread/timed_mutex)
