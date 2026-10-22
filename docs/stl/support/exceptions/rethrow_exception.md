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

`current_exception()` や `make_exception_ptr()` で保存した例外を、別の場所で投げ直します。`std::async` や `future::get` が、別スレッドの例外を呼び出し元に渡す仕組みも、この関数と同じ考え方です。

!!! tip "ポイント"
    - 例外の関連の部品。
    - `try` / `catch` と組み合わせて使う。
    - ゲームでは、ファイルや外部入力のエラーの扱いに登場する。

!!! info "このページを読む前に"
    [例外](../../../basics/index.md) の基本と、[`std::exception`](exception.md) を先に読んでください。

## 関数の詳しい説明

### std::rethrow_exception {#rethrow_exception}

```cpp
[[noreturn]] void rethrow_exception(std::exception_ptr p);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | exception_ptr | 投げ直す例外（空でないこと） |

- 戻り値: 戻らない（例外を投げる）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <exception>
#include <print>
#include <stdexcept>

int main() {
  std::exception_ptr p = std::make_exception_ptr(std::runtime_error("boom"));
  try {
    std::rethrow_exception(p);
  } catch (const std::runtime_error& e) {
    std::println("{}", e.what());
  }
}
```

```text title="実行結果"
boom
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ワーカースレッドの例外をメインスレッドで投げ直す |

## よくあるミス

??? failure "空のポインタを渡す"
    空の `exception_ptr` を渡すと未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`current_exception`](current_exception.md) | 保存する |
| [`make_exception_ptr`](make_exception_ptr.md) | 例外から作る |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 保存した exception_ptr の例外を、もう一度投げる
    - [x] 例外の関連の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::rethrow_exception](https://cpprefjp.github.io/reference/exception/rethrow_exception.html)
- [cppreference: std::rethrow_exception](https://en.cppreference.com/w/cpp/error/rethrow_exception)
