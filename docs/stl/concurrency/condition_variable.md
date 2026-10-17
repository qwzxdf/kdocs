---
title: std::condition_variable
tags:
  - 並行処理
---

# std::condition_variable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-11">C++11</span>
`#include <condition_variable>`
</div>

`std::condition_variable`（条件変数）は、<strong>「ある条件が満たされるまで、CPU を使わずに眠って待つ」</strong>ための仕組みです。たとえば仕事を待つスレッドは、仕事のキューが空の間は眠っていて、誰かが仕事を入れて「起きて」と通知したら起きて処理します。`while (queue.empty()) {}` のように空回りして待つと CPU を 100% 使ってしまうので、その代わりに使います。

!!! tip "ポイント"
    - 必ず **mutex とセット**で使う。待つ側は `std::unique_lock` を渡す。
    - 待つときは**条件を書いた `wait(lock, 条件)`** を使う（勝手に起きる「偽の起床」に対応できる）。
    - 通知する側は、データを変えてから `notify_one()`（1 人起こす）か `notify_all()`（全員起こす）。
    - C++20 なら、単純なフラグ待ちは [`std::atomic::wait`](atomic.md#wait) で足りることも多い。

!!! info "このページを読む前に"
    [std::mutex](mutex.md) を先に読んでください。

## 関数一覧

| 関数 | 重要度 | 何をする |
| --- | --- | --- |
| [`wait`](#wait) | <span class="rank rank-sometimes">たまに</span> | 条件が満たされるまで眠って待つ |
| [`notify_one`](#notify_one) | <span class="rank rank-sometimes">たまに</span> | 待っているスレッドを 1 つ起こす |
| [`notify_all`](#notify_all) | <span class="rank rank-sometimes">たまに</span> | 待っているスレッドを全部起こす |
| [`wait_for`](#wait_for) | <span class="rank rank-rare">知ってるだけ</span> | 時間制限つきで待つ |
| [`wait_until`](#wait_until) | <span class="rank rank-rare">知ってるだけ</span> | 指定時刻まで待つ |
| [`std::condition_variable_any`](#condition_variable_any) | <span class="rank rank-rare">知ってるだけ</span> | どんなロックでも使える版（stop_token 対応） |

## よくある使い方

### 仕事のキュー（ワーカースレッド）

```cpp
#include <condition_variable>
#include <mutex>
#include <print>
#include <queue>
#include <thread>
#include <vector>

class JobQueue {
 public:
  void Push(int job) {
    {
      std::lock_guard lock(mutex_);
      jobs_.push(job);
    }
    cv_.notify_one();  // 待っているワーカーを 1 人起こす
  }

  void Close() {
    {
      std::lock_guard lock(mutex_);
      closed_ = true;
    }
    cv_.notify_all();  // 全員起こして終わらせる
  }

  // 仕事を取り出す。閉じられて空なら false
  bool Pop(int& job) {
    std::unique_lock lock(mutex_);
    cv_.wait(lock, [this] { return !jobs_.empty() || closed_; });  // 条件を満たすまで眠る
    if (jobs_.empty()) {
      return false;
    }
    job = jobs_.front();
    jobs_.pop();
    return true;
  }

 private:
  std::mutex mutex_;
  std::condition_variable cv_;
  std::queue<int> jobs_;
  bool closed_ = false;
};

int main() {
  JobQueue queue;
  std::vector<int> done;
  std::mutex done_mutex;
  {
    std::jthread worker([&] {
      int job = 0;
      while (queue.Pop(job)) {
        std::lock_guard lock(done_mutex);
        done.push_back(job * 10);
      }
    });
    for (int i = 1; i <= 3; ++i) {
      queue.Push(i);
    }
    queue.Close();
  }
  std::println("{}", done);
}
```

```text title="実行結果"
[10, 20, 30]
```

## 関数の詳しい説明

### wait {#wait}

```cpp
void wait(std::unique_lock<std::mutex>& lock);
template <class Predicate>
void wait(std::unique_lock<std::mutex>& lock, Predicate pred);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `lock` | `std::unique_lock<std::mutex>&` | ロック済みの unique_lock |
| `pred` | 関数 | 待ち終わる条件。`true` を返したら起きる |

- 待っている間は自動で**ロックを外し**、起きるときに**ロックをかけ直し**ます
- 条件付き版は `while (!pred()) wait(lock);` と同じで、勝手に起きても（偽の起床）条件を確かめ直してくれます

### notify_one {#notify_one}

```cpp
void notify_one() noexcept;
```

- 待っているスレッドを 1 つ起こします。仕事を 1 つ追加したときに使います

### notify_all {#notify_all}

```cpp
void notify_all() noexcept;
```

- 待っているスレッドを全部起こします。終了の合図など、全員に知らせたいときに使います

### wait_for {#wait_for}

```cpp
template <class Rep, class Period, class Predicate>
bool wait_for(std::unique_lock<std::mutex>& lock,
              const std::chrono::duration<Rep, Period>& rel_time, Predicate pred);
```

- 最大 `rel_time` だけ待ちます。条件が満たされたら `true`、時間切れなら `false`

```cpp
#include <chrono>
#include <condition_variable>
#include <mutex>
#include <print>

int main() {
  using namespace std::chrono_literals;
  std::mutex m;
  std::condition_variable cv;
  bool arrived = false;
  std::unique_lock lock(m);
  bool ok = cv.wait_for(lock, 10ms, [&] { return arrived; });  // 誰も通知しないので時間切れ
  std::println("届いた？ {}", ok);
}
```

```text title="実行結果"
届いた？ false
```

### wait_until {#wait_until}

```cpp
template <class Clock, class Duration, class Predicate>
bool wait_until(std::unique_lock<std::mutex>& lock,
                const std::chrono::time_point<Clock, Duration>& abs_time, Predicate pred);
```

- 指定した時刻まで待ちます。使い方は `wait_for` と同じです

### std::condition_variable_any {#condition_variable_any}

```cpp
class condition_variable_any;
```

- `std::unique_lock<std::mutex>` 以外のロックでも使える版。C++20 では `std::stop_token` を渡して「止める合図が来たら起きる」こともできます

## フラグ・オプション

`wait_for` / `wait_until`（条件なし版）の戻り値です。

| 値 | 意味 |
| --- | --- |
| `std::cv_status::no_timeout` | 通知で起きた（または偽の起床） |
| `std::cv_status::timeout` | 時間切れ |

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| ジョブシステム | ワーカースレッドが仕事を待つ |
| ロード | 読み込み要求が来るまでロードスレッドが眠る |
| 音声 | バッファが空くまでストリーミングスレッドが待つ |

## よくあるミス

??? failure "条件なしの wait を使う"
    条件変数は、通知が無くても勝手に起きることがあります（偽の起床）。`cv.wait(lock, 条件)` を使えば安全です。

??? failure "データを変えずに notify する・ロックせずに変える"
    待っている側は条件（`!jobs_.empty()` など）を見て起きるので、条件の元になるデータは必ず mutex の中で変えます。

??? failure "notify してから push する"
    先に通知すると、起きたスレッドがまだ空のキューを見て、また眠ってしまいます（通知が無駄になる）。データを変えてから通知します。

## 理解度チェック

!!! question "Q1. `while (queue.empty()) {}` で待つのと condition_variable で待つのは何が違う？"
    <div class="spoiler" markdown>

    **答え:** while の空回りは、待っている間も CPU を 100% 使い続けます（しかもロックが無いとデータ競争）。condition_variable は眠って待つので CPU を使いません。

    </div>

## これだけ覚える

!!! abstract "まとめ"
    - [x] mutex とセットで、`wait(lock, 条件)` で眠って待つ
    - [x] データを変えてから notify_one / notify_all
    - [x] 単純なフラグなら atomic::wait でも足りる

## 関連ページ

- [std::mutex](mutex.md)
- [std::atomic](atomic.md)
- [cppreference: std::condition_variable](https://en.cppreference.com/w/cpp/thread/condition_variable)
