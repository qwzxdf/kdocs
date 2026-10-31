---
title: std::shared_timed_mutex
summary: "読み取りは同時に、書き込みは 1 つだけで、時間切れも指定できるミューテックス。"
order: 900
tags:
  - 並行処理
---

# std::shared_timed_mutex

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-14">C++14</span>
`#include <shared_mutex>`
</div>

読む側は複数同時でよく、書く側は 1 人だけ。この「読み書きロック」を表すのが `std::shared_mutex` ですが、`std::shared_timed_mutex` は、さらに「一定時間だけ待つ」ロックの試みができる版です。C++14 で追加されました。

!!! tip "ポイント"
    - 読み取りの共有ロック（`lock_shared`）と、書き込みの排他ロック（`lock`）
    - `try_lock_for` / `try_lock_until` で、時間切れを指定できる
    - 時間指定が要らないなら、軽い `shared_mutex`
    - 共有ロックの保持者がいる間、排他ロックは取れない

!!! info "このページを読む前に"
    [`std::mutex`](mutex.md) を先に読んでください。

## 関数の詳しい説明

### std::shared_timed_mutex {#shared_timed_mutex}

<span class="ver ver-14">C++14</span>

```cpp
class shared_timed_mutex {
 public:
  void lock();                                   // 排他
  bool try_lock();
  template <class Rep, class Period>
  bool try_lock_for(const std::chrono::duration<Rep, Period>& d);
  void unlock();

  void lock_shared();                            // 共有
  bool try_lock_shared();
  template <class Rep, class Period>
  bool try_lock_shared_for(const std::chrono::duration<Rep, Period>& d);
  void unlock_shared();
};
```

排他ロックは、共有ロックも排他ロックも保持者がいないときに取れます。共有ロックは、排他ロックの保持者がいないときに取れます。

時間つきの関数は、時間内に取れれば `true`、取れなければ `false` です。時間を過ぎる前に取れた場合は、すぐ戻ります。

`std::shared_lock`（共有ロックの自動解放）と、`std::unique_lock`（排他ロックの自動解放）を組み合わせて使います。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <mutex>
#include <print>
#include <shared_mutex>
#include <thread>

int main() {
  using namespace std::chrono_literals;
  std::shared_timed_mutex m;

  m.lock_shared();  // 読み手がいる

  bool write_ok = true;
  bool read_ok = false;
  std::thread t([&] {
    write_ok = m.try_lock_for(10ms);      // 読み手がいる間は、書けない
    read_ok = m.try_lock_shared_for(10ms);  // 読みは、同時にできる
    if (read_ok) m.unlock_shared();
  });
  t.join();

  std::println("書き込みロック: {}", write_ok);
  std::println("読み込みロック: {}", read_ok);
  m.unlock_shared();
}
```

```text title="実行結果"
書き込みロック: false
読み込みロック: true
```

## ゲームでの使いどころ

設定のデータを多数のスレッドが読み、まれに 1 つのスレッドが更新する場面で使います。

## よくあるミス

??? failure "共有ロックのまま書き込む"
    共有ロックの間は、書き込みは未定義です。排他ロックを取ります。

??? failure "同じスレッドで共有と排他を取る"
    デッドロックします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`shared_lock`](shared_lock.md) | 共有ロックの自動解放 |
| [`shared_mutex`](shared_mutex.md) | 時間指定のない軽い版 |
| [`timed_mutex`](timed_mutex.md) | 排他だけの時間指定つき |

## コンパイラ対応

C++14 から使えます。

## 関連ページ

- [cpprefjp: std::shared_timed_mutex](https://cpprefjp.github.io/reference/shared_mutex/shared_timed_mutex.html)
- [cppreference: std::shared_timed_mutex](https://en.cppreference.com/w/cpp/thread/shared_timed_mutex)
