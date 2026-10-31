---
title: co_return
summary: "コルーチンを終了して、値を返す。"
order: 6
group: コルーチン（<coroutine>）
tags:
  - 型・言語サポート
---

# co_return

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <coroutine>`
</div>

関数の途中で結果を返して終わる `return` と同じことを、コルーチンでもしたい。ただし、コルーチンの中では `return` は使えません。代わりに `co_return` を使います。`co_return;`（値なし）は `promise.return_void()` を、`co_return 値;` は `promise.return_value(値)` を呼んで、コルーチンを終わらせます。

!!! tip "ポイント"
    - コルーチンの終わりは `co_return` で書く（`return` は使えない）
    - 値なしなら `return_void()`、値ありなら `return_value(v)` を `promise_type` に用意する
    - 本体の最後まで進んだ場合は、`co_return;` と同じ扱い
    - `return_void` と `return_value` を同じ `promise_type` に両方書くことはできない

!!! info "このページを読む前に"
    [`std::generator`](../generator.md) のページに、コルーチンの簡単な例があります。

## 関数の詳しい説明

### co_return {#co_return}

```cpp
co_return;              // promise.return_void() を呼ぶ
co_return expression;   // promise.return_value(expression) を呼ぶ
```

`co_return` を実行すると、まず `return_void` か `return_value` が呼ばれ、その後ローカル変数が破棄されて、`final_suspend()` へ進みます。結果の値を呼び出し側に渡したいときは、`return_value` の中で、`promise_type` のメンバーへ保存します。

値を持つコルーチンの本体が、`co_return` を通らずに最後まで進むと、未定義動作になります。`return_value` を使う型では、すべての経路で `co_return` を書いてください。値を持たない（`return_void`）なら、最後まで進んでも、問題ありません。

## 実際に動かしてみる

```cpp
#include <coroutine>
#include <exception>
#include <print>
#include <utility>
#include <vector>

struct IntTask {
  struct promise_type {
    int result = 0;
    IntTask get_return_object() { return IntTask{std::coroutine_handle<promise_type>::from_promise(*this)}; }
    std::suspend_always initial_suspend() noexcept { return {}; }
    std::suspend_always final_suspend() noexcept { return {}; }
    void return_value(int v) { result = v; }   // co_return v; で呼ばれる
    void unhandled_exception() { std::terminate(); }
  };

  std::coroutine_handle<promise_type> handle;
  explicit IntTask(std::coroutine_handle<promise_type> h) : handle(h) {}
  IntTask(IntTask&& other) noexcept : handle(std::exchange(other.handle, {})) {}
  ~IntTask() {
    if (handle) handle.destroy();
  }

  // 終わるまで進めて、結果を返す
  int Get() {
    if (!handle.done()) handle.resume();
    return handle.promise().result;
  }
};

IntTask Add(int a, int b) {
  co_return a + b;
}

int main() {
  IntTask t = Add(3, 4);
  std::println("3 + 4 = {}", t.Get());
}
```

```text title="実行結果"
3 + 4 = 7
```

## ゲームでの使いどころ

ロードやパスの探索のような、時間のかかる処理が「終わったときの結果」を、コルーチンから呼び出し側へ返すときに使います。

## よくあるミス

??? failure "コルーチンの中で return を使う"
    コンパイル エラーです。`co_return` を使います。

??? failure "値を返す型で co_return を書かずに終わる"
    `return_value` を持つ型では、最後まで進むと未定義動作です。

??? failure "return_void と return_value を両方書く"
    同じ `promise_type` に両方あると、コンパイル エラーです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`co_yield`](co_yield.md) | 途中の値を出す |
| [`co_await`](co_await.md) | 止めて待つ |
| [`coroutine_handle`](coroutine_handle.md) | `done()` で終わったかを調べる |

## コンパイラ対応

C++20 の機能です。MSVC・GCC・Clang とも対応しています。

## 関連ページ

- [cpprefjp: コルーチン](https://cpprefjp.github.io/reference/coroutine.html)
- [cppreference: Coroutines](https://en.cppreference.com/w/cpp/language/coroutines)
