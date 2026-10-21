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

`std::suspend_never` は、`co_await` に渡しても**一時停止しない**待ち受け体です。`initial_suspend()` が `suspend_never` を返すと、コルーチンは呼び出した瞬間に実行を始めます（すぐ実行する型の Task を作るとき）。

!!! tip "ポイント"
    - `initial_suspend` が `suspend_never` → 呼び出した瞬間に最初の一時停止点（または終了）まで走る。
    - `final_suspend` に `suspend_never` を返すと、終わった時点で自動で破棄される（取っ手が無効になる）。

!!! info "このページを読む前に"
    [`std::generator`](../generator.md) のページに、コルーチンの簡単な例があります。

## 関数の詳しい説明

### std::suspend_never {#suspend_never}

```cpp
struct suspend_never {
  constexpr bool await_ready() const noexcept { return true; }    // 止まらない
  constexpr void await_suspend(coroutine_handle<>) const noexcept {}
  constexpr void await_resume() const noexcept {}
};
```

- 戻り値: （空の型）。`co_await` しても止まらない
- 計算量: O(1)

```cpp
#include <coroutine>
#include <print>

struct Task {
  struct promise_type {
    Task get_return_object() { return Task{std::coroutine_handle<promise_type>::from_promise(*this)}; }
    std::suspend_never initial_suspend() noexcept { return {}; }
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
  std::println("すぐ実行された");
  co_return;
}

int main() {
  Task t = Run();  // initial_suspend が suspend_never なので、呼んだ瞬間に実行される
  std::println("呼び出した直後");
}
```

```text title="実行結果"
すぐ実行された
呼び出した直後
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 呼んだらすぐ動き出す非同期処理 | `initial_suspend` で `suspend_never` |

## よくあるミス

??? failure "final_suspend に suspend_never を返して、取っ手を使う"
    終わった時点で破棄されるので、その後に `done()` や `destroy()` を呼ぶと未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`suspend_always`](suspend_always.md) | 必ず止まる |

## コンパイラ対応

C++20 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 一時停止しない
    - [x] 最初に使うと即実行
    - [x] final に使うと自動破棄

## 関連ページ

- [cpprefjp: std::suspend_never](https://cpprefjp.github.io/reference/coroutine/suspend_never.html)
- [cppreference: std::suspend_never](https://en.cppreference.com/w/cpp/coroutine/suspend_never)
