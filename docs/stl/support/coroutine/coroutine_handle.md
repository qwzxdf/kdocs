---
title: std::coroutine_handle
summary: "コルーチンの再開・破棄を操作する「取っ手」。"
order: 1
group: コルーチン（<coroutine>）
tags:
  - 型・言語サポート
---

# std::coroutine_handle

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <coroutine>`
</div>

`std::coroutine_handle<Promise>` は、**一時停止しているコルーチンを再開したり破棄したりするための「取っ手」**です。`resume()` で続きを実行し、`done()` で終わったかを調べ、`destroy()` で後片付けします。コルーチンを自作する（`Task` のような型を作る）ときに必要になります。

!!! tip "ポイント"
    - `handle.resume()` で、次の一時停止か終了まで進める。
    - `handle.done()` が `true` になったら、`resume()` してはいけない。
    - `destroy()` を呼ぶ責任は、普通は戻り値の型のデストラクターが持つ。

!!! info "このページを読む前に"
    [`std::generator`](../generator.md) のページにコルーチンの簡単な例があります。

## 関数の詳しい説明

### std::coroutine_handle {#coroutine_handle}

```cpp
template <class Promise = void>
struct coroutine_handle {
  void resume() const;
  bool done() const;
  void destroy() const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `Promise` | テンプレート引数 | そのコルーチンの promise 型 |

- 戻り値: （取っ手）。`resume` / `done` / `destroy` で操作する
- 計算量: resume は次の停止点まで

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

Task Count() {
  std::println("1");
  co_await std::suspend_always{};  // ここで一時停止
  std::println("2");
}

int main() {
  Task t = Count();   // 最初に止まる設定なので、まだ何も実行されない
  t.handle.resume();  // 1 を出して一時停止
  t.handle.resume();  // 2 を出して終了
  std::println("done: {}", t.handle.done());
}
```

```text title="実行結果"
1
2
done: true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ゲームのシーケンス（イベント演出）を複数フレームにまたがって書く | 毎フレーム `handle.resume()` で続きを進める |

## よくあるミス

??? failure "done なのに resume する"
    終わったコルーチンの `resume` は未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`suspend_always`](suspend_always.md) | 一時停止の指示 |
| [`std::generator`](../generator.md) | 値を順に返すコルーチン（C++23） |

## コンパイラ対応

C++20 の機能です。GCC 10 / Clang 14 / MSVC 19.28 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] コルーチンの取っ手
    - [x] `resume` / `done` / `destroy`
    - [x] 終わった後は resume しない

## 関連ページ

- [cpprefjp: std::coroutine_handle](https://cpprefjp.github.io/reference/coroutine/coroutine_handle.html)
- [cppreference: std::coroutine_handle](https://en.cppreference.com/w/cpp/coroutine/coroutine_handle)
