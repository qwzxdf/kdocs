---
title: std::bad_function_call
summary: "空の std::function を呼んだときの例外。"
order: 12
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::bad_function_call

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++11</span>
`#include <functional>`
</div>

標準ライブラリの機能は、前提が満たされないとき、例外を投げて失敗を伝えます。`std::bad_function_call` は、<strong>空の `std::function` を呼び出したことを表す例外</strong>。

!!! tip "ポイント"
    - 空の `std::function` を呼ぶと投げられる
    - `if (f)` で、空かどうかを確かめられる
    - `<functional>` で宣言される
    - コールバックの設定忘れで起きる

!!! info "このページを読む前に"
    [エラー処理の設計](../../../design/foundations/error-handling.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::bad_function_call {#bad_function_call}

```cpp
class bad_function_call : public std::exception {
 public:
  const char* what() const noexcept override;
};
```

何も代入されていない `std::function` を呼び出すと、投げられます。コールバックを後から設定する仕組みで、設定前に呼ぶ間違いが典型です。

呼び出す前に `if (f)` で空でないことを確かめれば、避けられます。

## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int main() {
  std::function<void()> callback;      // 空
  try {
    callback();
  } catch (const std::bad_function_call&) {
    std::println("bad_function_call を捕まえた");
  }
  std::println("空かどうかは if で分かる: {}", !callback);
}
```

```text title="実行結果"
bad_function_call を捕まえた
空かどうかは if で分かる: true
```

## ゲームでの使いどころ

コールバックを呼ぶ前に、空でないか確かめます。

```cpp
if (on_hit) on_hit(damage);   // 例外を避ける
```

## よくあるミス

??? failure "捕まえずに放置して、プログラムが終了する"
    例外を投げうる機能を使うときは、`try` / `catch` で受けるか、事前に条件を確かめます。

??? failure "`catch (std::exception)` と値で捕まえる"
    `const` 参照で捕まえます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`exception`](exception.md) | すべての標準例外の基底 |
| [`function`](../../utilities/function.md) | 呼び出し可能なものを保持する |

## コンパイラ対応

C++11 から使えます。`<functional>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 空の `std::function` を呼ぶと投げられる
    - [x] `what()` でメッセージを取れる（内容は実装で違う）
    - [x] `const` 参照で捕まえる

## 関連ページ

- [cpprefjp: std::bad_function_call](https://cpprefjp.github.io/reference/functional/bad_function_call.html)
- [cppreference: std::bad_function_call](https://en.cppreference.com/w/cpp/utility/functional/bad_function_call)
