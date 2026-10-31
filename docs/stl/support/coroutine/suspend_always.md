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

コルーチンの要所で、「ここで必ず止まる」と書きたいことがあります。`std::suspend_always` は、`co_await` すると必ず止まる、中身のない待ち受け体です。止まる以外は何もしないので、`initial_suspend()` / `final_suspend()` の戻り値や、「1 回止まって呼び出し側に戻る」だけのときに使います。

!!! tip "ポイント"
    - `await_ready` が常に `false` なので、必ず止まる
    - 再開しても何も返さない（`await_resume` は `void`）
    - `initial_suspend` に使うと、呼んだ時点では本体が動かない（遅延開始）
    - `final_suspend` に使うと、終わったあとも `done()` で状態を見られる

!!! info "このページを読む前に"
    [`co_await`](co_await.md) を先に読んでください。

## 関数の詳しい説明

### std::suspend_always {#suspend_always}

```cpp
struct suspend_always {
  constexpr bool await_ready() const noexcept { return false; }
  constexpr void await_suspend(std::coroutine_handle<>) const noexcept {}
  constexpr void await_resume() const noexcept {}
};
```

3 つの関数は何もしません。`await_ready` が `false` を返すので、必ず止まります。

#### initial_suspend に使う（遅延開始）

`initial_suspend()` が `suspend_always` を返すと、コルーチンを呼んだ直後（本体の最初の文の前）で止まります。`resume()` を呼ぶまで、本体は 1 行も動きません。ゲームの演出のように、「作っておいて、あとで好きなタイミングで始める」ときに便利です。

#### final_suspend に使う（終了後も保持）

`final_suspend()` が `suspend_always` を返すと、本体が終わったあとも、フレームが残ります。`done()` が `true` になるので、外から終了を確認でき、`destroy()` で自分で片づけられます。`suspend_never` を返すと、終わったとたんにフレームが自動的に消えるので、外から `done()` を呼べなくなります。

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
    std::suspend_always initial_suspend() noexcept { return {}; }   // 最初に止まる
    std::suspend_always final_suspend() noexcept { return {}; }     // 終わっても残る
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

Task Cutscene() {
  std::println("暗転");
  co_await std::suspend_always{};   // ここで必ず止まる
  std::println("明転");
}

int main() {
  std::println("コルーチンを作る");
  Task t = Cutscene();
  std::println("作っただけ (本体はまだ動かない)");

  t.handle.resume();
  std::println("1 回目の resume の後: done = {}", t.handle.done());
  t.handle.resume();
  std::println("2 回目の resume の後: done = {}", t.handle.done());
}
```

```text title="実行結果"
コルーチンを作る
作っただけ (本体はまだ動かない)
暗転
1 回目の resume の後: done = false
明転
2 回目の resume の後: done = true
```

## ゲームでの使いどころ

演出やイベントのコルーチンを、「作っておいて、始めるタイミングは自分で決める」とき（遅延開始）や、「1 フレームだけ止まる」ときに使います。

## よくあるミス

??? failure "final_suspend を suspend_never にして、あとで done() を呼ぶ"
    終わった瞬間にフレームが消えるので、あとで `done()` を呼ぶと未定義動作です。外から見たいなら `suspend_always` にします。

??? failure "止まったまま誰も resume しない"
    `suspend_always` は止まるだけで、再開は自分で呼ぶ必要があります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`suspend_never`](suspend_never.md) | 止まらない待ち受け体 |
| [`co_await`](co_await.md) | 待ち受け体の 3 関数 |
| [`coroutine_handle`](coroutine_handle.md) | `resume()` と `done()` |

## コンパイラ対応

C++20 から使えます。MSVC・GCC・Clang とも対応しています。

## 関連ページ

- [cpprefjp: std::suspend_always](https://cpprefjp.github.io/reference/coroutine/suspend_always.html)
- [cppreference: std::suspend_always](https://en.cppreference.com/w/cpp/coroutine/suspend_always)
