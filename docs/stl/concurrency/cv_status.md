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

`condition_variable::wait_for` や `wait_until` は、時間切れになるか、通知で起きるかのどちらかで戻ります。どちらで戻ったかを知らせる列挙型が `std::cv_status` で、`no_timeout`（通知で起きた）と `timeout`（時間切れ）の 2 つの値があります。

!!! tip "ポイント"
    - `wait_for` / `wait_until`（述語なし）の戻り値
    - `std::cv_status::timeout` は時間切れ、`no_timeout` は通知
    - 偽の目覚めでも `no_timeout` になりうる
    - 述語つきの版は、`bool` を返す

!!! info "このページを読む前に"
    [`std::mutex`](mutex.md) を先に読んでください。

## 関数の詳しい説明

### std::cv_status {#cv_status}

<span class="ver ver-11">C++11</span>

```cpp
enum class cv_status { no_timeout, timeout };
```

述語なしの `wait_for(lock, 10ms)` は、`cv_status` を返します。ただし、`no_timeout` でも、条件が成立しているとは限りません。偽の目覚め（通知がないのに起きる）があるからです。

そのため、条件を確かめるには、述語つきの `wait_for(lock, 10ms, pred)` を使います。この版の戻り値は `bool` で、`pred` が真になって抜けたら `true`、時間切れで `pred` が偽のままなら `false` です。

述語なしの版を使うときは、戻ったあとで自分で条件を確かめ、必要なら待ち直します。

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

  std::unique_lock<std::mutex> lock(m);

  // 誰も通知しないので、時間切れ
  const std::cv_status s = cv.wait_for(lock, 10ms);
  std::println("時間切れ: {}", s == std::cv_status::timeout);

  // 述語つきは bool を返す
  const bool ok = cv.wait_for(lock, 10ms, [] { return false; });
  std::println("条件が成立: {}", ok);
}
```

```text title="実行結果"
時間切れ: true
条件が成立: false
```

## ゲームでの使いどころ

一定時間だけ待って、来なければ他の処理に移る、タイムアウトつきの待ち合わせに使います。

## よくあるミス

??? failure "no_timeout を、条件の成立と思う"
    偽の目覚めがあります。条件を確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`condition_variable`](condition_variable.md) | `wait_for` を持つ |
| [`future_status`](future_status.md) | `future` の同様の列挙型 |
| [`condition_variable_any`](condition_variable_any.md) | 任意のロック型 |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::cv_status](https://cpprefjp.github.io/reference/condition_variable/cv_status.html)
- [cppreference: std::cv_status](https://en.cppreference.com/w/cpp/thread/cv_status)
