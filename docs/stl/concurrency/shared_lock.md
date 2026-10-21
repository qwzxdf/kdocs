---
title: std::shared_lock
summary: "`shared_mutex` を「読む側」としてロックする鍵。"
order: 82
tags:
  - 並行処理
---

# std::shared_lock

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="perf perf-2">△ やや重い</span>
<span class="ver ver-14">C++14</span>
`#include <shared_mutex>`
</div>

`std::shared_lock` は、**[`shared_mutex`](shared_mutex.md) を「読む側」として（共有で）ロックする**ための鍵です。作ったときに共有ロックをかけ、スコープを抜けるときに開けます。書く側は `std::unique_lock` / `lock_guard` です。

!!! tip "ポイント"
    - `std::shared_lock lock(rw_mutex);` で、読む側として入る。
    - 何人でも同時に持てる。書く側が待っている間は、新しい読む側が入れないことがある。
    - `lock_guard` の共有版、と考える。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

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

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 読み込みの多いテーブルを参照する | `std::shared_lock lock(table_mutex_);` |

## よくあるミス

??? failure "書き込みに shared_lock を使う"
    `shared_lock` は読み取り専用です。書き込むなら `unique_lock` / `lock_guard` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::shared_mutex`](shared_mutex.md) | 本体 |
| [`std::lock_guard`](lock_guard.md) | 排他ロック |

## コンパイラ対応

C++14 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `shared_mutex` を読む側でロックする
    - [x] 何人でも同時に持てる
    - [x] 書く側は `unique_lock`

## 関連ページ

- [cpprefjp: std::shared_lock](https://cpprefjp.github.io/reference/shared_mutex/shared_lock.html)
- [cppreference: std::shared_lock](https://en.cppreference.com/w/cpp/thread/shared_lock)
