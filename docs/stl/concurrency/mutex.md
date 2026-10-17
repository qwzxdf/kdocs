---
title: std::mutex / std::lock_guard
tags:
  - 並行処理
---

# std::mutex / std::lock_guard

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-2">△ やや重い</span>
<span class="ver ver-11">C++11</span>
`#include <mutex>`
</div>

`std::mutex` は、<strong>「一度に 1 つのスレッドしか入れない」部屋の鍵</strong>のようなものです。共有するデータを触る前に鍵をかけ（lock）、終わったら開けます（unlock）。他のスレッドは、鍵が開くまで待たされます。鍵のかけ忘れ・開け忘れを防ぐため、実際には **`std::lock_guard` や `std::scoped_lock`** を使って、スコープを抜けると自動で開くようにします。

!!! tip "ポイント"
    - 共有データは `std::mutex` とセットで持ち、触るときは **`std::lock_guard lock(mutex);`**。
    - 複数の mutex を同時にロックするなら **`std::scoped_lock lock(a, b);`**（デッドロックしない）。
    - `lock()` / `unlock()` を直接呼ばない（例外や return で開け忘れる）。
    - ロックしている時間は短く。ロックの中で重い処理やファイル読み込みをしない。
    - 単純な数値 1 つなら [`std::atomic`](atomic.md) のほうが軽い。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 主な型

| 型 | 重要度 | 何をする |
| --- | --- | --- |
| [`std::mutex`](#mutex) | <span class="rank rank-sometimes">たまに</span> | 鍵そのもの |
| [`std::lock_guard`](#lock_guard) | <span class="rank rank-sometimes">たまに</span> | スコープの間だけ鍵をかける |
| [`std::scoped_lock`](#scoped_lock) | <span class="rank rank-sometimes">たまに</span> | 複数の鍵をまとめてかける <span class="ver ver-17">C++17</span> |
| [`std::unique_lock`](#unique_lock) | <span class="rank rank-sometimes">たまに</span> | 途中で開け閉めできる鍵（条件変数で使う） |
| [`std::shared_mutex`](#shared_mutex) | <span class="rank rank-rare">知ってるだけ</span> | 読む人は何人でも、書く人は 1 人だけ <span class="ver ver-17">C++17</span> |
| [`std::shared_lock`](#shared_lock) | <span class="rank rank-rare">知ってるだけ</span> | 読むための鍵 <span class="ver ver-14">C++14</span> |
| [`std::recursive_mutex`](#recursive_mutex) | <span class="rank rank-rare">知ってるだけ</span> | 同じスレッドなら何度でもかけられる鍵 |
| [`std::call_once`](#call_once) | <span class="rank rank-rare">知ってるだけ</span> | 1 回だけ実行する |

## 関数一覧

| 関数 | 重要度 | 対象 | 何をする |
| --- | --- | --- | --- |
| [`lock`](#lock) | <span class="rank rank-rare">知ってるだけ</span> | mutex | 鍵をかける（かかるまで待つ） |
| [`unlock`](#unlock) | <span class="rank rank-rare">知ってるだけ</span> | mutex | 鍵を開ける |
| [`try_lock`](#try_lock) | <span class="rank rank-rare">知ってるだけ</span> | mutex | かけられなければすぐ諦める |

## よくある使い方

### 共有するログ

```cpp
#include <mutex>
#include <print>
#include <string>
#include <thread>
#include <utility>
#include <vector>

class Logger {
 public:
  void Add(std::string message) {
    std::lock_guard lock(mutex_);  // ここから } まで他のスレッドは入れない
    lines_.push_back(std::move(message));
  }

  std::size_t size() const {
    std::lock_guard lock(mutex_);
    return lines_.size();
  }

 private:
  mutable std::mutex mutex_;  // const 関数でもロックできるように mutable
  std::vector<std::string> lines_;
};

int main() {
  Logger log;
  {
    std::vector<std::jthread> workers;
    for (int t = 0; t < 4; ++t) {
      workers.emplace_back([&log, t] {
        for (int i = 0; i < 100; ++i) {
          log.Add("thread " + std::to_string(t));
        }
      });
    }
  }
  std::println("{} 行", log.size());
}
```

```text title="実行結果"
400 行
```

守るデータ（`lines_`）と mutex を同じクラスの private にまとめると、守り忘れが起きません。

## 型と関数の詳しい説明

### std::mutex {#mutex}

```cpp
class mutex;
```

- 鍵そのもの。コピーもムーブもできません

### std::lock_guard {#lock_guard}

```cpp
template <class Mutex>
class lock_guard {
 public:
  explicit lock_guard(Mutex& m);  // ここで lock
  ~lock_guard();                  // ここで unlock
};
```

- 作ったときに鍵をかけ、スコープを抜けるときに自動で開けます。途中で return や例外があっても必ず開きます

### std::scoped_lock {#scoped_lock}

<span class="ver ver-17">C++17</span>

```cpp
template <class... Mutexes>
class scoped_lock {
 public:
  explicit scoped_lock(Mutexes&... m);
};
```

- 複数の mutex を、デッドロックしない順番でまとめてロックします。1 つでも使えるので、lock_guard の代わりに全部これでも構いません

```cpp
#include <mutex>
#include <print>

struct Account {
  int gold = 100;
  std::mutex mutex;
};

void Transfer(Account& from, Account& to, int amount) {
  std::scoped_lock lock(from.mutex, to.mutex);  // 2 つを同時に（順番を気にしなくていい）
  from.gold -= amount;
  to.gold += amount;
}

int main() {
  Account a;
  Account b;
  Transfer(a, b, 30);
  Transfer(b, a, 10);
  std::println("{} {}", a.gold, b.gold);
}
```

```text title="実行結果"
80 120
```

### std::unique_lock {#unique_lock}

```cpp
template <class Mutex>
class unique_lock;
```

- lock_guard と同じですが、途中で `unlock()` / `lock()` したり、ムーブしたりできます。[`std::condition_variable`](condition_variable.md) で待つときに必要です

### std::shared_mutex {#shared_mutex}

<span class="ver ver-17">C++17</span>

```cpp
class shared_mutex;
```

- 「読むだけ」の人は同時に何人でも入れて、「書く」人は 1 人だけ入れる鍵。読む回数がとても多いデータ（設定、マスターデータ）に使います

### std::shared_lock {#shared_lock}

<span class="ver ver-14">C++14</span>

```cpp
template <class Mutex>
class shared_lock;
```

- shared_mutex を「読むため」にロックします。書くときは `std::unique_lock` か `std::lock_guard` を使います

```cpp
#include <map>
#include <mutex>
#include <print>
#include <shared_mutex>
#include <string>

class Config {
 public:
  int Get(const std::string& key) const {
    std::shared_lock lock(mutex_);  // 読む人は同時に入れる
    auto it = values_.find(key);
    return it != values_.end() ? it->second : 0;
  }
  void Set(const std::string& key, int value) {
    std::unique_lock lock(mutex_);  // 書く人は 1 人だけ
    values_[key] = value;
  }

 private:
  mutable std::shared_mutex mutex_;
  std::map<std::string, int> values_;
};

int main() {
  Config config;
  config.Set("volume", 80);
  std::println("{}", config.Get("volume"));
}
```

```text title="実行結果"
80
```

### std::recursive_mutex {#recursive_mutex}

```cpp
class recursive_mutex;
```

- 同じスレッドなら何度ロックしてもいい mutex（ロックした回数だけ unlock が必要）。必要になるのは設計がこじれているときが多いので、使わずに済むようにします

### std::call_once {#call_once}

```cpp
template <class Callable, class... Args>
void call_once(std::once_flag& flag, Callable&& f, Args&&... args);
```

- 何個のスレッドから呼ばれても、`f` を 1 回だけ実行します（初期化に使う）

```cpp
#include <mutex>
#include <print>
#include <thread>
#include <vector>

int main() {
  std::once_flag init_flag;
  int init_count = 0;
  {
    std::vector<std::jthread> threads;
    for (int i = 0; i < 4; ++i) {
      threads.emplace_back([&] { std::call_once(init_flag, [&] { ++init_count; }); });
    }
  }
  std::println("初期化 {} 回", init_count);
}
```

```text title="実行結果"
初期化 1 回
```

### lock {#lock}

```cpp
void lock();
```

- 鍵をかけます。他のスレッドがかけていれば、開くまで待ちます

### unlock {#unlock}

```cpp
void unlock();
```

- 鍵を開けます。かけていないのに呼ぶと未定義動作です

### try_lock {#try_lock}

```cpp
bool try_lock();
```

- 鍵をかけられたら `true`、他のスレッドが使っていたら待たずに `false` を返します

```cpp
#include <mutex>
#include <print>
#include <thread>

int main() {
  std::mutex m;
  bool got = true;

  m.lock();  // メインスレッドが鍵をかけている
  std::jthread([&] {
    got = m.try_lock();  // 別のスレッドから試す → 待たずに false
    if (got) {
      m.unlock();
    }
  }).join();
  std::println("かかっている間: {}", got);

  m.unlock();
  std::jthread([&] {
    got = m.try_lock();
    if (got) {
      m.unlock();
    }
  }).join();
  std::println("開けたあと: {}", got);
}
```

```text title="実行結果"
かかっている間: false
開けたあと: true
```

自分がすでにロックしている mutex に、同じスレッドから `lock()` や `try_lock()` を呼ぶのは未定義動作です。

## フラグ・オプション

ロックの作り方を変える「タグ」があります。

| タグ | 重要度 | 意味 |
| --- | --- | --- |
| `std::defer_lock` | <span class="rank rank-rare">知ってるだけ</span> | 作るときにはロックしない（あとで lock） |
| `std::try_to_lock` | <span class="rank rank-rare">知ってるだけ</span> | 作るときに try_lock する |
| `std::adopt_lock` | <span class="rank rank-rare">知ってるだけ</span> | すでにロック済みの mutex を引き取る |

```cpp
std::unique_lock lock(mutex, std::try_to_lock);
if (lock.owns_lock()) {
  // ロックできたときだけ処理
}
```

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| ロードスレッドからの結果の受け渡し | 読み込み済みのリソースのキュー |
| ログ | 複数のスレッドから書き込む |
| ジョブシステム | 仕事のキュー |

## よくあるミス

??? failure "ロックの中で重い処理をする"
    ロックしている間、他のスレッドは全部待たされます。データをコピーして、ロックの外で処理します。

??? failure "2 つの mutex を別々の順番でロックしてデッドロック"
    スレッド A が「a → b」、スレッド B が「b → a」の順にロックすると、お互いを待って止まります。`std::scoped_lock(a, b)` でまとめてロックします。

??? failure "守るデータを外に参照で返す"
    `const std::vector<T>& data() const { std::lock_guard l(m_); return data_; }` は、ロックが外れたあとに呼び出し側がデータを読むので守れていません。コピーを返すか、ロックの中で処理する関数を用意します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 共有データは mutex とセットで private に
    - [x] 触るときは `std::lock_guard lock(mutex);`
    - [x] 複数の mutex は scoped_lock
    - [x] ロックの中は短く

## 関連ページ

- [std::atomic](atomic.md)
- [std::condition_variable](condition_variable.md)
- [cppreference: std::mutex](https://en.cppreference.com/w/cpp/thread/mutex)
