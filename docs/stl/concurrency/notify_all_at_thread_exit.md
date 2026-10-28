---
title: std::notify_all_at_thread_exit
summary: "スレッドが完全に終わった（後始末も済んだ）あとで、条件変数に通知する。"
order: 900
tags:
  - 並行処理
---

# std::notify_all_at_thread_exit

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <condition_variable>`
</div>

スレッドの終了時に `notify_all()` を呼ぶと、待っているスレッドがまだ終わっていないスレッドのローカル変数を見てしまう危険があります。`notify_all_at_thread_exit(cv, lock)` なら、スレッドのローカル変数の後始末が全部済んでから通知されるので安全です。

!!! tip "ポイント"
    - 第 2 引数にすでに取っているロックを渡す。
    - スレッドが終わるときに、ロックを解除して通知する。
    - `thread_local` の変数が破棄されたあとに通知される。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::notify_all_at_thread_exit {#notify_all_at_thread_exit}

```cpp
void notify_all_at_thread_exit(condition_variable& cond, unique_lock<mutex> lk);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `cond` | condition_variable& | 通知する条件変数 |
| `lk` | unique_lock<mutex> | 取得済みのロック（ムーブで渡す） |

- 戻り値: なし
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <condition_variable>
#include <mutex>
#include <print>
#include <thread>

int main() {
  std::mutex m;
  std::condition_variable cv;
  bool done = false;
  std::thread t([&] {
    std::unique_lock lk(m);
    done = true;
    std::notify_all_at_thread_exit(cv, std::move(lk));
  });
  {
    std::unique_lock lk(m);
    cv.wait(lk, [&] { return done; });
  }
  t.join();
  std::println("done");
}
```

```text title="実行結果"
done
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| スレッドの終了と結果を同時に知らせる | `std::notify_all_at_thread_exit(cv, std::move(lk));` |

## よくあるミス

??? failure "ロックを取らずに呼ぶ"
    ロックを取った `unique_lock` を渡す必要があります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`condition_variable`](condition_variable.md) | 条件変数 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] スレッド終了後に通知する
    - [x] ロックを渡す
    - [x] ローカル変数の後始末のあとで通知される

## 関連ページ

- [cpprefjp: std::notify_all_at_thread_exit](https://cpprefjp.github.io/reference/condition_variable/notify_all_at_thread_exit.html)
- [cppreference: std::notify_all_at_thread_exit](https://en.cppreference.com/w/cpp/thread/notify_all_at_thread_exit)
