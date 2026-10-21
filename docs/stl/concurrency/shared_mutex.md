---
title: std::shared_mutex
summary: "読む人は何人でも同時に、書く人は 1 人だけ、という鍵。"
order: 81
tags:
  - 並行処理
---

# std::shared_mutex

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="perf perf-2">△ やや重い</span>
<span class="ver ver-17">C++17</span>
`#include <shared_mutex>`
</div>

`std::shared_mutex` は、**「読むだけの人は何人でも同時に入れて、書く人は 1 人だけ（ほかの全員が入れない）」**という鍵です。読み込みが圧倒的に多く、書き込みがまれなデータ（設定、マップ、アセット表）に向きます。読むときは [`shared_lock`](shared_lock.md)、書くときは `lock_guard` / `unique_lock` を使います。

!!! tip "ポイント"
    - 読み込みが多く、書き込みが少ないときだけ得をする。そうでなければ普通の `mutex` のほうが速い。
    - 読む側は `std::shared_lock`、書く側は `std::unique_lock`（または `lock_guard`）。
    - 読み込み中に書き込みを待たせるので、書く側が飢える実装もある。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::shared_mutex {#shared_mutex}

<span class="ver ver-17">C++17</span>

```cpp
class shared_mutex;
```

- 「読むだけ」の人は同時に何人でも入れて、「書く」人は 1 人だけ入れる鍵。読む回数がとても多いデータ（設定、マスターデータ）に使います

## 実際に動かしてみる

```cpp
#include <mutex>
#include <print>
#include <shared_mutex>

int main() {
  std::shared_mutex m;
  int value = 0;
  {
    std::unique_lock writer(m);  // 書く側
    value = 42;
  }
  {
    std::shared_lock reader(m);  // 読む側
    std::println("{}", value);
  }
}
```

```text title="実行結果"
42
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 読み込みが多いアセット表 | 読む側 `shared_lock`、更新する側 `unique_lock` |

## よくあるミス

??? failure "読み書きが同じくらい多い"
    普通の `mutex` のほうが速いことが多いです。測ってから選びます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::shared_lock`](shared_lock.md) | 読む側の鍵 |
| [`std::mutex`](mutex.md) | 1 人だけ |

## コンパイラ対応

C++17 から使えます（`shared_timed_mutex` は C++14）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 読みは大勢、書きは 1 人
    - [x] 読む側は `shared_lock`
    - [x] 読み込みが多いときだけ得

## 関連ページ

- [cpprefjp: std::shared_mutex](https://cpprefjp.github.io/reference/shared_mutex/shared_mutex.html)
- [cppreference: std::shared_mutex](https://en.cppreference.com/w/cpp/thread/shared_mutex)
