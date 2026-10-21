---
title: std::suspend_always
summary: "「必ず一時停止する」ことを表す待ち受け体。"
order: 2
group: コルーチン（<coroutine>）
tags:
  - 型・言語サポート
---

# std::suspend_always

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <coroutine>`
</div>

`std::suspend_always` は、`co_await` に渡すと、**必ずコルーチンを一時停止する**待ち受け体（awaitable）です。コルーチンの最初（`initial_suspend`）や最後（`final_suspend`）で、「ここで一旦止まる」と指定するときによく使います。止まらない版は [`suspend_never`](suspend_never.md) です。

!!! tip "ポイント"
    - `co_await std::suspend_always{};` で、その場で一時停止。
    - `initial_suspend()` が `suspend_always` を返すと、呼び出した直後は何も実行されない。
    - `final_suspend()` も `suspend_always` にして、後片付けを呼び出し側で行うのが定番。

!!! info "このページを読む前に"
    [`std::generator`](../generator.md) のページに、コルーチンの簡単な例があります。

## 関数の詳しい説明

### std::suspend_always {#suspend_always}

```cpp
struct suspend_always {
  constexpr bool await_ready() const noexcept { return false; }   // 止まる
  constexpr void await_suspend(coroutine_handle<>) const noexcept {}
  constexpr void await_resume() const noexcept {}
};
```

- 戻り値: （空の型）。`co_await` すると一時停止する
- 計算量: O(1)

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

Task Run() {
  std::println("実行された");
  co_return;
}

int main() {
  Task t = Run();  // initial_suspend が suspend_always なので、まだ実行されない
  std::println("呼び出した直後");
  t.handle.resume();
}
```

```text title="実行結果"
呼び出した直後
実行された
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 呼び出したあと、準備ができるまで走らせない | `initial_suspend` で `suspend_always` |

## よくあるミス

??? failure "最初に止めるつもりで suspend_never を返す"
    呼び出した瞬間に実行が始まります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`suspend_never`](suspend_never.md) | 止まらない |
| [`coroutine_handle`](coroutine_handle.md) | 再開する |

## コンパイラ対応

C++20 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 必ず一時停止する
    - [x] 最初と最後の指定によく使う
    - [x] 止めないのは suspend_never

## 関連ページ

- [cpprefjp: std::suspend_always](https://cpprefjp.github.io/reference/coroutine/suspend_always.html)
- [cppreference: std::suspend_always](https://en.cppreference.com/w/cpp/coroutine/suspend_always)
