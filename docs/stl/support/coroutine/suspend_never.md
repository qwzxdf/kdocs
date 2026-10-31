---
title: std::suspend_never
summary: "「一時停止しない」ことを表す待ち受け体。"
order: 3
group: コルーチン（<coroutine>）
tags:
  - 型・言語サポート
---

# std::suspend_never

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <coroutine>`
</div>

コルーチンの要所で、「ここでは止まらない」と書きたいことがあります。`std::suspend_never` は、`co_await` しても止まらず、すぐ次へ進む、中身のない待ち受け体です。`initial_suspend()` に使うと、呼んだ瞬間から本体が動き出します（即時開始）。

!!! tip "ポイント"
    - `await_ready` が常に `true` なので、止まらない
    - `initial_suspend` に使うと、呼んだ時点で本体が動く（即時開始）
    - `final_suspend` に使うと、終わると同時にフレームが自動的に消える
    - `suspend_always` の反対

!!! info "このページを読む前に"
    [`co_await`](co_await.md) を先に読んでください。

## 関数の詳しい説明

### std::suspend_never {#suspend_never}

```cpp
struct suspend_never {
  constexpr bool await_ready() const noexcept { return true; }
  constexpr void await_suspend(std::coroutine_handle<>) const noexcept {}
  constexpr void await_resume() const noexcept {}
};
```

`await_ready` が `true` を返すので、`await_suspend` は呼ばれず、止まりません。

#### initial_suspend に使う（即時開始）

`initial_suspend()` が `suspend_never` を返すと、コルーチンを呼んだときに、すぐ本体が動き出します。最初の `co_await` や `co_yield` で止まるまで進み、そこで呼び出し側へ戻ります。「呼ぶだけで始まる」ので、`resume()` を呼ぶ手間が要りません。

#### final_suspend に使う（自動で片づく）

`final_suspend()` が `suspend_never` を返すと、本体が終わった直後に、フレームが自動的に解放されます。`destroy()` を呼ぶ必要はありませんが、ハンドルが宙に浮くので、終わったあとに `done()` や `resume()` を呼ぶと、未定義動作です。終わったことを外から知る別の方法が要ります。

## 実際に動かしてみる

```cpp
#include <coroutine>
#include <exception>
#include <print>
#include <utility>
#include <vector>

struct Task {
  struct promise_type {
    Task get_return_object() { return Task{std::coroutine_handle<promise_type>::from_promise(*this)}; }
    std::suspend_never initial_suspend() noexcept { return {}; }   // 呼んだ瞬間に動き出す
    std::suspend_always final_suspend() noexcept { return {}; }
    void return_void() {}
    void unhandled_exception() { std::terminate(); }
  };

  std::coroutine_handle<promise_type> handle;
  explicit Task(std::coroutine_handle<promise_type> h) : handle(h) {}
  Task(Task&& other) noexcept : handle(std::exchange(other.handle, {})) {}
  ~Task() {
    if (handle) handle.destroy();
  }
};

Task Loading() {
  std::println("ロード開始");
  co_await std::suspend_never{};   // 止まらずに次へ進む
  std::println("ロード中");
  co_await std::suspend_always{};  // ここで止まる
  std::println("ロード完了");
}

int main() {
  std::println("コルーチンを呼ぶ");
  Task t = Loading();
  std::println("呼び出しが戻った");
  t.handle.resume();
}
```

```text title="実行結果"
コルーチンを呼ぶ
ロード開始
ロード中
呼び出しが戻った
ロード完了
```

## ゲームでの使いどころ

「呼んだらすぐ始まる」コルーチン（即時開始のタスク）を作るときに、`initial_suspend` で使います。

## よくあるミス

??? failure "final_suspend を suspend_never にして、あとで done() を呼ぶ"
    フレームが消えているので未定義動作です。

??? failure "止まらないつもりで suspend_always を使う"
    `suspend_always` は必ず止まります。止めたくない所には `suspend_never` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`suspend_always`](suspend_always.md) | 必ず止まる待ち受け体 |
| [`co_await`](co_await.md) | 待ち受け体の 3 関数 |
| [`coroutine_handle`](coroutine_handle.md) | `resume()` と `done()` |

## コンパイラ対応

C++20 から使えます。MSVC・GCC・Clang とも対応しています。

## 関連ページ

- [cpprefjp: std::suspend_never](https://cpprefjp.github.io/reference/coroutine/suspend_never.html)
- [cppreference: std::suspend_never](https://en.cppreference.com/w/cpp/coroutine/suspend_never)
