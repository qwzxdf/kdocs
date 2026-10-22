---
title: std::nested_exception
summary: "別の例外を中に抱えられる例外の土台。"
order: 900
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::nested_exception

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <exception>`
</div>

「ファイルを開けなかった」という低レベルの例外を、「セーブに失敗した」という高レベルの例外に包んで投げ直したい、ということがあります。元の例外の情報を失わずに包めるのが、`nested_exception` です。ふつうは [`throw_with_nested`](throw_with_nested.md) 経由で使います。

!!! tip "ポイント"
    - 例外の関連の部品。
    - `try` / `catch` と組み合わせて使う。
    - ゲームでは、ファイルや外部入力のエラーの扱いに登場する。

!!! info "このページを読む前に"
    [例外](../../../basics/index.md) の基本と、[`std::exception`](exception.md) を先に読んでください。

## 関数の詳しい説明

### std::nested_exception {#nested_exception}

```cpp
class nested_exception {
 public:
  nested_exception() noexcept;  // 今処理中の例外を覚える
  exception_ptr nested_ptr() const noexcept;
  [[noreturn]] void rethrow_nested() const;
};
```

- 戻り値: `nested_ptr()` が包んだ例外へのポインタ
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <exception>
#include <print>
#include <stdexcept>

int main() {
  try {
    try {
      throw std::runtime_error("inner");
    } catch (...) {
      std::throw_with_nested(std::logic_error("outer"));
    }
  } catch (const std::exception& e) {
    std::println("{}", e.what());
    try {
      std::rethrow_if_nested(e);
    } catch (const std::exception& inner) {
      std::println("{}", inner.what());
    }
  }
}
```

```text title="実行結果"
outer
inner
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ロード失敗の原因の鎖を保つ |

## よくあるミス

??? failure "`catch` の外で作る"
    `nested_exception` を作るとき、例外の処理中（`catch` の中）でないと、包むものがありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`throw_with_nested`](throw_with_nested.md) | 包んで投げる |
| [`rethrow_if_nested`](rethrow_if_nested.md) | 包まれたものを取り出す |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 別の例外を中に抱えられる例外の土台
    - [x] 例外の関連の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::nested_exception](https://cpprefjp.github.io/reference/exception/nested_exception.html)
- [cppreference: std::nested_exception](https://en.cppreference.com/w/cpp/error/nested_exception)
