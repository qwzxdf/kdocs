---
title: std::exception_ptr
summary: "例外を保存して、別の場所・スレッドで投げ直す。"
order: 8
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::exception_ptr

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <exception>`
</div>

`std::exception_ptr` は、**例外を（ポインターのように）保存しておいて、あとで別の場所や別のスレッドで投げ直せる**型です。ワーカースレッドで起きた例外を、メインスレッドへ運ぶときに使います。`std::future` が内部でやっていることです。

!!! tip "ポイント"
    - `std::current_exception()` で、`catch` の中で今の例外を保存する。
    - `std::rethrow_exception(p)` で投げ直す。
    - `std::async` / `future::get()` は、これを自動でやってくれる。

!!! info "このページを読む前に"
    [標準の例外](../exceptions.md) の概要と合わせて読むと分かりやすいです。

## 関数の詳しい説明

### std::exception_ptr {#exception_ptr}

```cpp
std::exception_ptr std::current_exception() noexcept;
[[noreturn]] void std::rethrow_exception(std::exception_ptr p);
```

- 今処理中の例外を保存して、あとで（別のスレッドで）投げ直せます。`std::async` の例外が `get()` で投げ直される仕組みもこれです

```cpp
#include <exception>
#include <print>
#include <stdexcept>
#include <thread>

int main() {
  std::exception_ptr error;
  std::jthread([&error] {
    try {
      throw std::runtime_error("スレッドの中で失敗");
    } catch (...) {
      error = std::current_exception();  // 保存しておく
    }
  }).join();

  try {
    if (error) {
      std::rethrow_exception(error);  // メインスレッドで投げ直す
    }
  } catch (const std::exception& e) {
    std::println("{}", e.what());
  }
}
```

```text title="実行結果"
スレッドの中で失敗
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ワーカースレッドの例外を、メインスレッドへ運ぶ | `std::current_exception()` → `std::rethrow_exception()` |

## よくあるミス

??? failure "catch の外で current_exception を呼ぶ"
    空の `exception_ptr` が返ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::future`](../../concurrency/future.md) | 自動で運んでくれる |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 例外を保存して投げ直す
    - [x] スレッドをまたいで運べる
    - [x] `future` が内部で使う

## 関連ページ

- [cpprefjp: std::exception_ptr](https://cpprefjp.github.io/reference/stdexcept/exception_ptr.html)
- [cppreference: std::exception_ptr](https://en.cppreference.com/w/cpp/error/exception_ptr)
