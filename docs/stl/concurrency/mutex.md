---
title: std::mutex
summary: "共有のデータを同時に触れないよう、鍵で守る。"
order: 77
tags:
  - 並行処理
---

# std::mutex

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
| [`std::lock_guard`](lock_guard.md) | <span class="rank rank-sometimes">たまに</span> | スコープの間だけ鍵をかける |
| [`std::scoped_lock`](scoped_lock.md) | <span class="rank rank-sometimes">たまに</span> | 複数の鍵をまとめてかける <span class="ver ver-17">C++17</span> |
| [`std::unique_lock`](unique_lock.md) | <span class="rank rank-sometimes">たまに</span> | 途中で開け閉めできる鍵 |
| [`std::shared_mutex`](shared_mutex.md) | <span class="rank rank-rare">知ってるだけ</span> | 読む人は何人でも、書く人は 1 人だけ |
| [`std::recursive_mutex`](recursive_mutex.md) | <span class="rank rank-rare">知ってるだけ</span> | 同じスレッドなら何度でも |
| [`std::call_once`](call_once.md) | <span class="rank rank-rare">知ってるだけ</span> | 1 回だけ実行する |

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
