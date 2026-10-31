---
title: std::noop_coroutine
summary: "何もしないコルーチンのハンドルを返す。"
order: 900
group: コルーチン（<coroutine>）
tags:
  - 型・言語サポート
---

# std::noop_coroutine

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <coroutine>`
</div>

コルーチンが終わったとき、次に実行するコルーチンを呼び出し側へ返す「対称転送」という書き方があります。ところが、「次はない、元の呼び出し側へ戻りたい」場面もあります。その「次はなし」を表すのが `std::noop_coroutine()` で、`resume()` しても何も起きない、特別なコルーチンのハンドルを返します。

!!! tip "ポイント"
    - `resume()` しても何も起こらない
    - `await_suspend` の戻り値として「何もしない」を表すときに使う
    - `done()` は常に `false`。`destroy()` も何もしない
    - 対称転送で、スタックが深くならずに連結するための部品

!!! info "このページを読む前に"
    [`coroutine_handle`](coroutine_handle.md) と [`co_await`](co_await.md) を先に読んでください。

## 関数の詳しい説明

### std::noop_coroutine {#noop_coroutine}

```cpp
noop_coroutine_handle noop_coroutine() noexcept;
using noop_coroutine_handle = std::coroutine_handle<std::noop_coroutine_promise>;
```

戻り値は、共有された 1 つの何もしないコルーチンを指すハンドルです。`std::coroutine_handle<>` に代入できるので、`await_suspend` の戻り値の型 `std::coroutine_handle<>` として返せます。

#### 対称転送とは

`await_suspend` が `std::coroutine_handle<>` を返すと、コンパイラは、そのハンドルのコルーチンへ直接切り替えます。関数呼び出しのようにスタックが積まれないので、コルーチンを何段つないでも、スタックが深くなりません。

終わったコルーチンの次に動くコルーチンがあるなら、そのハンドルを返します。ないなら（一番外側のコルーチンが終わったときなど）、`noop_coroutine()` を返します。すると、何も実行されずに、`resume()` を呼んだ側へ戻ります。

## 実際に動かしてみる

```cpp
#include <coroutine>
#include <exception>
#include <print>
#include <utility>
#include <vector>

struct Task {
  struct promise_type {
    // 自分が終わった後に再開するコルーチン。既定は「なし」
    std::coroutine_handle<> next = std::noop_coroutine();

    Task get_return_object() { return Task{std::coroutine_handle<promise_type>::from_promise(*this)}; }
    std::suspend_always initial_suspend() noexcept { return {}; }

    struct FinalAwaiter {
      bool await_ready() noexcept { return false; }
      // 終わったら、next へ直接切り替える（next が noop なら、呼び出し側へ戻る）
      std::coroutine_handle<> await_suspend(std::coroutine_handle<promise_type> h) noexcept {
        return h.promise().next;
      }
      void await_resume() noexcept {}
    };
    FinalAwaiter final_suspend() noexcept { return {}; }

    void return_void() {}
    void unhandled_exception() { std::terminate(); }
  };

  std::coroutine_handle<promise_type> handle;
  explicit Task(std::coroutine_handle<promise_type> h) : handle(h) {}
  Task(Task&& other) noexcept : handle(std::exchange(other.handle, {})) {}
  ~Task() {
    if (handle) handle.destroy();
  }

  // この Task を co_await できるようにする: 呼んだ側を next に覚えて、自分に切り替える
  bool await_ready() const noexcept { return false; }
  std::coroutine_handle<> await_suspend(std::coroutine_handle<> caller) noexcept {
    handle.promise().next = caller;
    return handle;
  }
  void await_resume() const noexcept {}
};

Task Inner() {
  std::println("内側のタスク");
  co_return;
}

Task Outer() {
  std::println("外側のタスク 開始");
  co_await Inner();   // 内側へ切り替わり、終わると外側へ戻ってくる
  std::println("外側のタスク 終了");
}

int main() {
  Task t = Outer();
  t.handle.resume();   // 外側が終わる(next が noop)と、ここへ戻る
  std::println("done: {}", t.handle.done());

  std::coroutine_handle<> h = std::noop_coroutine();
  h.resume();   // 何も起きない
  std::println("noop の done: {}", h.done());
}
```

```text title="実行結果"
外側のタスク 開始
内側のタスク
外側のタスク 終了
done: true
noop の done: false
```

## ゲームでの使いどころ

ゲームの演出を、コルーチンの入れ子（演出の中から別の演出を `co_await`）で組むとき、終わったら親へ戻る処理の中で使います。

## よくあるミス

??? failure "destroy() を呼ぶ"
    ハンドルは共有された 1 つの実体なので、`destroy()` に意味はありません。

??? failure "「次なし」に nullptr のハンドルを返す"
    空のハンドルを `resume()` すると未定義動作です。「次なし」は `noop_coroutine()` で表します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`coroutine_handle`](coroutine_handle.md) | ハンドルの操作 |
| [`co_await`](co_await.md) | `await_suspend` の戻り値の意味 |
| [`suspend_always`](suspend_always.md) | 転送しない、ただ止まる版 |

## コンパイラ対応

C++20 から使えます。MSVC・GCC・Clang とも対応しています。

## 関連ページ

- [cpprefjp: std::noop_coroutine](https://cpprefjp.github.io/reference/coroutine/noop_coroutine.html)
- [cppreference: std::noop_coroutine](https://en.cppreference.com/w/cpp/coroutine/noop_coroutine)
