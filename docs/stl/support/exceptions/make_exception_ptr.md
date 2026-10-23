---
title: std::make_exception_ptr
summary: "例外オブジェクトから、exception_ptr を作る。"
order: 900
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::make_exception_ptr

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <exception>`
</div>

例外を「投げずに」、`exception_ptr` として用意したい。たとえば、非同期処理の結果として、失敗を表す値を返したい。`std::make_exception_ptr(e)` は、<strong>例外オブジェクトから `exception_ptr` を作ります</strong>。

!!! tip "ポイント"
    - 例外オブジェクトから `exception_ptr` を作る
    - `throw` と `catch` を経由しない
    - `promise::set_exception` に渡す
    - 渡した `e` のコピーが保持される

!!! info "このページを読む前に"
    [エラー処理の設計](../../../design/foundations/error-handling.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::make_exception_ptr {#make_exception_ptr}

<span class="ver ver-11">C++11</span>

```cpp
template <class E>
std::exception_ptr make_exception_ptr(E e) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `e` | 例外オブジェクト | 保持させる例外 |

`throw` と `catch` を経由せずに、`exception_ptr` を直接作れます。内部では、例外オブジェクトを `e` のコピーで作ります。

`std::promise::set_exception` に渡して、`future` の側に失敗を伝える、といった使い方があります。

## 実際に動かしてみる

```cpp
#include <exception>
#include <print>
#include <stdexcept>

int main() {
  std::exception_ptr p = std::make_exception_ptr(std::runtime_error("先に失敗"));
  std::println("空でない: {}", static_cast<bool>(p));
  try {
    std::rethrow_exception(p);
  } catch (const std::exception& e) {
    std::println("{}", e.what());
  }
}
```

```text title="実行結果"
空でない: true
先に失敗
```

## ゲームでの使いどころ

非同期処理で、失敗を `promise` に設定します。

```cpp
promise.set_exception(std::make_exception_ptr(std::runtime_error("ロード失敗")));
```

## よくあるミス

??? failure "投げるつもりで呼んで、何も起きない"
    作るだけで投げません。投げるには `rethrow_exception`。

## 類似

| 名前 | 違い |
| --- | --- |
| [`exception_ptr`](exception_ptr.md) | 例外を保持する型 |
| [`rethrow_exception`](rethrow_exception.md) | 投げ直す |

## コンパイラ対応

C++11 から使えます。`<exception>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `make_exception_ptr(e)` は例外から `exception_ptr` を作る
    - [x] 投げずに作れる
    - [x] `promise::set_exception` に渡せる

## 関連ページ

- [cpprefjp: std::make_exception_ptr](https://cpprefjp.github.io/reference/exception/make_exception_ptr.html)
- [cppreference: std::make_exception_ptr](https://en.cppreference.com/w/cpp/error/make_exception_ptr)
