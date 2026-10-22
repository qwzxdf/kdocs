---
title: std::throw_with_nested
summary: "いま処理中の例外を包んだ上で、新しい例外を投げる。"
order: 900
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::throw_with_nested

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <exception>`
</div>

低レベルの例外を `catch` して、意味のある高レベルの例外に変えたいが、元の原因も残したいとき、`catch` の中で `throw_with_nested(新しい例外)` を呼びます。新しい例外の中に、元の例外が入った状態で投げられます。

!!! tip "ポイント"
    - 例外の関連の部品。
    - `try` / `catch` と組み合わせて使う。
    - ゲームでは、ファイルや外部入力のエラーの扱いに登場する。

!!! info "このページを読む前に"
    [例外](../../../basics/index.md) の基本と、[`std::exception`](exception.md) を先に読んでください。

## 関数の詳しい説明

### std::throw_with_nested {#throw_with_nested}

```cpp
template <class T>
[[noreturn]] void throw_with_nested(T&& t);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `t` | 例外 | 投げる新しい例外 |

- 戻り値: 戻らない（例外を投げる）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <exception>
#include <print>
#include <stdexcept>

int main() {
  try {
    try {
      throw std::runtime_error("file not found");
    } catch (...) {
      std::throw_with_nested(std::runtime_error("save failed"));
    }
  } catch (const std::exception& e) {
    std::println("{}", e.what());
  }
}
```

```text title="実行結果"
save failed
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ロード処理の失敗の理由をたどれるようにする |

## よくあるミス

??? failure "`catch` の外で呼ぶ"
    処理中の例外がないと、包むものがなく、`std::terminate` になることがあります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`nested_exception`](nested_exception.md) | 包まれた形 |
| [`rethrow_if_nested`](rethrow_if_nested.md) | 取り出す |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] いま処理中の例外を包んだ上で、新しい例外を投げる
    - [x] 例外の関連の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::throw_with_nested](https://cpprefjp.github.io/reference/exception/throw_with_nested.html)
- [cppreference: std::throw_with_nested](https://en.cppreference.com/w/cpp/error/throw_with_nested)
