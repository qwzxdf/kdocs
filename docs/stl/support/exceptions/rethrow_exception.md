---
title: std::rethrow_exception
summary: "保存した exception_ptr の例外を、もう一度投げる。"
order: 900
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::rethrow_exception

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <exception>`
</div>

保存しておいた例外をあとで投げ直したい。`std::rethrow_exception(ptr)` は、<strong>`exception_ptr` が指す例外を改めて投げます</strong>。別スレッドで起きた例外をメイン スレッドで処理するときの最後の一歩です。

!!! tip "ポイント"
    - `exception_ptr` が指す例外を投げ直す
    - 元の型のまま投げられる
    - 空の `exception_ptr` を渡すと未定義動作
    - 戻らない（`[[noreturn]]`）

!!! info "このページを読む前に"
    [エラー処理の設計](../../../design/foundations/error-handling.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::rethrow_exception {#rethrow_exception}

<span class="ver ver-11">C++11</span>

```cpp
[[noreturn]] void rethrow_exception(std::exception_ptr p);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `exception_ptr` | 投げ直す例外。空でないこと |

`exception_ptr` が指す例外オブジェクトをそのまま投げます。型は、元の例外の型です。そのため、`catch (const std::runtime_error&)` で、元の型として受け取れます。

空の `exception_ptr` を渡すと、動作は未定義です。`if (ptr)` で確かめてから呼びます。この関数は戻らず、必ず例外を投げます（`[[noreturn]]`）。

## 実際に動かしてみる

```cpp
#include <exception>
#include <print>
#include <stdexcept>

int main() {
  std::exception_ptr p = std::make_exception_ptr(std::runtime_error("失敗"));
  try {
    std::rethrow_exception(p);
  } catch (const std::runtime_error& e) {
    std::println("元の型で捕まえた: {}", e.what());
  }
}
```

```text title="実行結果"
元の型で捕まえた: 失敗
```

## ゲームでの使いどころ

保存した例外を処理しやすい場所で投げ直します。

```cpp
if (error) std::rethrow_exception(error);
```

## よくあるミス

??? failure "空の `exception_ptr` を渡す"
    `if (ptr)` で確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`exception_ptr`](exception_ptr.md) | 例外を保持する型 |
| [`current_exception`](current_exception.md) | 今の例外を取る |

## コンパイラ対応

C++11 から使えます。`<exception>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `rethrow_exception(p)` は `p` が指す例外を投げ直す
    - [x] 空の `exception_ptr` は未定義動作
    - [x] 戻らない

## 関連ページ

- [cpprefjp: std::rethrow_exception](https://cpprefjp.github.io/reference/exception/rethrow_exception.html)
- [cppreference: std::rethrow_exception](https://en.cppreference.com/w/cpp/error/rethrow_exception)
