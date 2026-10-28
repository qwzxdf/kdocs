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

エラーを上位に伝えるとき、原因を失いたくないことがあります。「読み込みに失敗」と伝えつつ、その原因の「ファイルがない」も残したい。`std::nested_exception` は、<strong>別の例外を中に入れて持つ</strong>ための基底クラスです。

!!! tip "ポイント"
    - 別の例外を内側に保持する基底クラス
    - `throw_with_nested` で作り、`rethrow_if_nested` でたどる
    - エラーの原因を連鎖で残せる
    - 直接ではなく、2 つの関数を介して使う

!!! info "このページを読む前に"
    [エラー処理の設計](../../../design/foundations/error-handling.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::nested_exception {#nested_exception}

<span class="ver ver-11">C++11</span>

```cpp
class nested_exception {
 public:
  nested_exception() noexcept;
  std::exception_ptr nested_ptr() const noexcept;
  [[noreturn]] void rethrow_nested() const;
};
```

`std::throw_with_nested` で投げると、元の例外が `nested_exception` として内側に保持されます。受け取った側は、`std::rethrow_if_nested` で内側を取り出して、原因をたどれます。

例外のチェーン（原因の連鎖）を作る仕組みです。ログには、外側から内側へ順にメッセージを出力すると、原因がたどれます。

`nested_exception` を直接使うことは少なく、`throw_with_nested` と `rethrow_if_nested` を使います。

## 実際に動かしてみる

```cpp
#include <exception>
#include <print>
#include <stdexcept>

void Load() {
  try {
    throw std::runtime_error("ファイルがない");
  } catch (...) {
    std::throw_with_nested(std::runtime_error("読み込みに失敗"));   // 元の例外を内側に入れて投げる
  }
}

void Print(const std::exception& e) {
  std::println("{}", e.what());
  try {
    std::rethrow_if_nested(e);                // 内側があれば投げ直す
  } catch (const std::exception& inner) {
    Print(inner);
  }
}

int main() {
  try {
    Load();
  } catch (const std::exception& e) {
    Print(e);
  }
}
```

```text title="実行結果"
読み込みに失敗
ファイルがない
```

## ゲームでの使いどころ

上位の処理で意味のある説明を足しつつ、元の原因も残します。

```cpp
try {
  LoadTexture(path);
} catch (...) {
  std::throw_with_nested(std::runtime_error("ステージの読み込みに失敗"));
}
```

## よくあるミス

??? failure "内側を取り出すのを忘れて、原因が分からない"
    ログ出力で、`rethrow_if_nested` を再帰的に呼びます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`throw_with_nested`](throw_with_nested.md) | 入れ子にして投げる |
| [`rethrow_if_nested`](rethrow_if_nested.md) | 内側を取り出す |

## コンパイラ対応

C++11 から使えます。`<exception>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `nested_exception` は別の例外を内側に持つ
    - [x] `throw_with_nested` と `rethrow_if_nested` を使う
    - [x] エラーの原因を連鎖で残せる

## 関連ページ

- [cpprefjp: std::nested_exception](https://cpprefjp.github.io/reference/exception/nested_exception.html)
- [cppreference: std::nested_exception](https://en.cppreference.com/w/cpp/error/nested_exception)
