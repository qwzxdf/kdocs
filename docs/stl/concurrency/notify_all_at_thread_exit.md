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

スレッドの終わりに、結果を共有データに書き、条件変数で待っているスレッドを起こしたい。ところが、`notify_all` を呼んだ直後に、待っている側が先に進み、結果を使い始めても、書いた側のスレッドのローカル変数は、まだ破棄されていないことがあります。`std::notify_all_at_thread_exit(cv, lock)` は、<strong>スレッドのローカル変数がすべて破棄された後</strong>に通知します。

!!! tip "ポイント"
    - スレッド終了時、`thread_local` の破棄が終わってから通知する
    - `lock` は、その時点まで保持される
    - `detach` したスレッドの完了を、通知する手段に使う
    - 使う場面は限られる

!!! info "このページを読む前に"
    [`std::mutex`](mutex.md) を先に読んでください。

## 関数の詳しい説明

### std::notify_all_at_thread_exit {#notify_all_at_thread_exit}

<span class="ver ver-11">C++11</span>

```cpp
void notify_all_at_thread_exit(std::condition_variable& cond,
                               std::unique_lock<std::mutex> lk);
```

`lk` は、すでにロックされている必要があります。所有権は、この関数が受け取り、スレッドの終了処理の最後で、`cond.notify_all()` を呼んでからロックを解放します。

通常の `notify_all` との違いは、通知のタイミングです。スレッドの `thread_local` 変数のデストラクターが、通知のあとに走ると、待っているスレッドが先に進んだ後も、デストラクターが動き続けます。それが共有データを触ると、競合が起きます。

`std::promise::set_value_at_thread_exit` も、同じ考え方の関数です。

## 実際に動かしてみる

```cpp
#include <condition_variable>
#include <mutex>
#include <print>
#include <thread>

std::mutex m;
std::condition_variable cv;
bool done = false;
int result = 0;

int main() {
  std::thread worker([] {
    std::unique_lock<std::mutex> lk(m);
    result = 42;
    done = true;
    // スレッドの後始末がすべて終わってから通知する
    std::notify_all_at_thread_exit(cv, std::move(lk));
  });
  worker.detach();  // 完了は条件変数で知る

  std::unique_lock<std::mutex> lk(m);
  cv.wait(lk, [] { return done; });
  std::println("結果: {}", result);
}
```

```text title="実行結果"
結果: 42
```

## ゲームでの使いどころ

`detach` したスレッドの完了を、後始末まで含めて待つときに使います。通常は `join` で足ります。

## よくあるミス

??? failure "lk がロックされていない"
    未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`condition_variable`](condition_variable.md) | 通知先 |
| [`promise`](promise.md) | `set_value_at_thread_exit` で似たことをする |
| [`thread`](thread.md) | `join` で完了を待つ |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::notify_all_at_thread_exit](https://cpprefjp.github.io/reference/condition_variable/notify_all_at_thread_exit.html)
- [cppreference: std::notify_all_at_thread_exit](https://en.cppreference.com/w/cpp/thread/notify_all_at_thread_exit)
