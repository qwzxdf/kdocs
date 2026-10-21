---
title: co_await
summary: "コルーチンを一時停止して、あとで結果を受け取って再開する演算子。"
order: 4
group: コルーチン（<coroutine>）
tags:
  - 型・言語サポート
---

# co_await

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <coroutine>`
</div>

`co_await` は、**コルーチンの実行をいったん止めて、準備ができたら続きから再開する**ためのキーワードです。「ロードが終わるまで待つ」「1 秒待つ」のような、非同期処理の待ちを、普通の順番の文章のように書けるのが利点です。待つ相手は「待ち受け体（awaitable）」です。

!!! tip "ポイント"
    - `co_await 待つもの;` の形。待つものが `await_ready` で「準備できている」と答えれば、止まらない。
    - 標準で用意されているのは [`suspend_always`](suspend_always.md) / [`suspend_never`](suspend_never.md)。
    - Unity 風の「N 秒待つ」などは、自分で待ち受け体を作る。

!!! info "このページを読む前に"
    [`std::generator`](../generator.md) のページに、コルーチンの簡単な例があります。

## 関数の詳しい説明

### co_await {#co_await}

```cpp
co_await expression;
```

- 戻り値: 待った結果（`await_resume` の戻り値）
- 計算量: 待ち受け体による

```cpp
#include <coroutine>
#include <print>

struct Task {
  struct promise_type {
    Task get_return_object() { return Task{std::coroutine_handle<promise_type>::from_promise(*this)}; }
    std::suspend_always initial_suspend() noexcept { return {}; }
    std::suspend_always final_suspend() noexcept { return {}; }
    void return_void() {}
    void unhandled_exception() {}
  };

  std::coroutine_handle<promise_type> handle;
  explicit Task(std::coroutine_handle<promise_type> h) : handle(h) {}
  ~Task() {
    if (handle) handle.destroy();
  }
};

Task Sequence() {
  std::println("演出開始");
  co_await std::suspend_always{};   // 1 フレーム待つ（再開されるまで止まる）
  std::println("演出の続き");
}

int main() {
  Task t = Sequence();
  t.handle.resume();   // 1 フレーム目
  t.handle.resume();   // 次のフレーム
}
```

```text title="実行結果"
演出開始
演出の続き
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 「3 秒待ってから次の演出」を、スレッドを使わずに書く | `co_await Wait(3s);` |

## よくあるミス

??? failure "co_await を普通の関数で使う"
    コルーチン（`co_await` / `co_yield` / `co_return` を含む関数）の中でだけ使えます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`coroutine_handle`](coroutine_handle.md) | 再開を操作する |
| [`std::async`](../../concurrency/async.md) | スレッドで非同期にする別の方法 |

## コンパイラ対応

C++20 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 一時停止して再開する
    - [x] 待ち受け体を待つ
    - [x] コルーチンの中だけ

## 関連ページ

- [cpprefjp: co_await](https://cpprefjp.github.io/reference/coroutine/co_await.html)
- [cppreference: co_await](https://en.cppreference.com/w/cpp/language/coroutines)
