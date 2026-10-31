---
title: std::copyable_function
summary: "コピーできる、const や noexcept も指定できる関数のラッパー。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::copyable_function

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <functional>`
</div>

`std::function` には、`const` の関数オブジェクトでも非 `const` の `operator()` を呼べてしまう、`noexcept` を型で表せない、という古い設計の問題があります。`std::copyable_function` は、それらを直した新しい版で、`const` や `noexcept` を型に書けます。コピーもできます。ムーブしかできない版は `std::move_only_function` です。

!!! tip "ポイント"
    - `std::function` の後継。コピーできる呼び出し可能オブジェクトを保持する
    - `R(Args...) const` のように、`const` や `noexcept` を型に書ける
    - `const` を書けば、`operator() const` だけが呼ばれる（安全）
    - コピーできないものは、`move_only_function` に入れる

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::copyable_function {#copyable_function}

<span class="ver ver-26">C++26</span>

```cpp
template <class... Signature>
class copyable_function;

// Signature の例: R(Args...)、R(Args...) const、R(Args...) noexcept、R(Args...) & など
```

| 引数 | 意味 |
| --- | --- |
| `R(Args...)` | 呼び出しの形。`cv` 修飾（`const`）、参照修飾（`&`・`&&`）、`noexcept` を付けられる |

`std::function<int(int)>` に、`mutable` なラムダを入れて、`const` の `std::function` から呼ぶと、中のラムダが書き換わってしまいます。型の上では `const` なのに、実際には状態が変わる、という不具合の元です。

`copyable_function<int(int) const>` と書くと、保持するものは、`const` で呼べるものでなければなりません。`mutable` なラムダを入れようとするとコンパイル エラーになるので、安全です。

`noexcept` も同様に、`copyable_function<void() noexcept>` のように型に書けます。例外を投げうるものを入れるとコンパイル エラーです。

コピーの意味は、`std::function` と同じです。コピーすると、中の関数オブジェクトもコピーされます。小さい関数オブジェクトは、ヒープ確保なしに内部に保存される（小さな領域の最適化）実装が多いです。

空のオブジェクトを呼ぶのは、未定義動作です。`if (f)` で確認します。

## 使い方の形

```cpp
#include <functional>
#include <print>

int main() {
  // const で呼べる関数だけを受け付ける
  std::copyable_function<int(int) const> triple = [](int x) { return x * 3; };
  std::println("{}", triple(5));

  // コピーすると、中の関数オブジェクトも別になる
  int base = 100;
  std::copyable_function<int(int)> add = [base](int x) mutable {
    base += x;
    return base;
  };
  auto add_copy = add;   // コピー
  std::println("{}", add(1));       // 元: 101
  std::println("{}", add(1));       // 元: 102
  std::println("{}", add_copy(1));  // コピー: 101 (別の状態)

  // 空かどうかの確認
  std::copyable_function<void()> empty;
  std::println("空: {}", !empty);
}
```


## ゲームでの使いどころ

ボタンのクリック時のコールバックなど、複数の場所にコピーして配るコールバックの保存に使います。`const` で呼べるものだけを受けたいときに、型で表せます。

## よくあるミス

??? failure "mutable なラムダを const のシグネチャに入れる"
    コンパイル エラーです。`const` を外すか、ラムダの `mutable` を外します。

??? failure "空のまま呼ぶ"
    未定義動作です。`if (f)` で確認します。

??? failure "ムーブ専用のものを入れる"
    コピーできないものは入りません。`std::move_only_function` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`function_ref`](function_ref.md) | 借りるだけの軽い版 |
| [`std::function`](../../utilities/function.md) | 従来の版 |
| [`invoke`](invoke.md) | 呼び出す関数 |

## コンパイラ対応

C++26 です。手元の MSVC（Visual Studio 2026）では、まだ `std::copyable_function` が無く、コンパイルできませんでした。そのため、このページのサンプルは動かして確かめていません。使えるようになったら、実行結果を確かめて書き足します。

## 関連ページ

- [cpprefjp: std::copyable_function](https://cpprefjp.github.io/reference/functional/copyable_function.html)
- [cppreference: std::copyable_function](https://en.cppreference.com/w/cpp/utility/functional/copyable_function)
