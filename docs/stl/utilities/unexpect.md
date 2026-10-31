---
title: std::unexpect
summary: "expected に、エラー側をその場で作らせる目印。"
order: 900
tags:
  - ユーティリティ
---

# std::unexpect

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <expected>`
</div>

`std::expected<T, E>` を、値ではなくエラーで作りたいとき、`expected<int, std::string> e("error");` と書くと、`T` と `E` のどちらで作る意図なのかが曖昧です。`std::unexpect` は、「エラーの値で作ります」と伝える印で、`expected` のコンストラクターに渡します。

!!! tip "ポイント"
    - `std::expected<T, E> e(std::unexpect, エラーの引数...)` で、エラーの状態を直接作る
    - `T` と `E` が同じ型でも、エラーで作ることを明示できる
    - エラーを `unexpected(エラー)` で包んで渡す方法もある
    - C++23

!!! info "このページを読む前に"
    [`std::expected`](expected.md) と [`std::unexpected`](unexpected.md) を先に読んでください。

## 関数の詳しい説明

### std::unexpect {#unexpect}

<span class="ver ver-23">C++23</span>

```cpp
struct unexpect_t { explicit unexpect_t() = default; };
inline constexpr std::unexpect_t unexpect{};
```

`unexpect` は、値を持たない空の印です。`std::expected` のコンストラクターのオーバーロードを選ぶために渡します。

```cpp
std::expected<int, std::string> e(std::unexpect, "not found");
```

`E` のコンストラクターの引数を、そのまま渡せるので、エラーの値を一時オブジェクトとして作らずに済みます。`E` が `std::string` なら、`"not found"` から直接作られます。

`unexpected(エラー)` で包む方法と、使い分けは次のとおりです。

| 方法 | 使いどころ |
| --- | --- |
| `return std::unexpected("error");` | 関数の `return` で、エラーを返す。普通はこちら |
| `std::expected<T, E> e(std::unexpect, 引数...)` | 変数を作るとき。`E` を引数から直接作る |

## 実際に動かしてみる

```cpp
#include <expected>
#include <print>
#include <string>

int main() {
  // エラーの状態で直接作る
  std::expected<int, std::string> e(std::unexpect, "not found");
  std::println("値がある: {}", e.has_value());
  std::println("エラー: {}", e.error());

  // E のコンストラクター引数を、そのまま渡せる
  std::expected<int, std::string> f(std::unexpect, 3, 'x');  // string(3, 'x')
  std::println("エラー: {}", f.error());

  // 通常の値で作る
  std::expected<int, std::string> g = 5;
  std::println("値: {}", g.value());
}
```

```text title="実行結果"
値がある: false
エラー: not found
エラー: xxx
値: 5
```

## ゲームでの使いどころ

アセットの読み込みの結果を `expected<Asset, LoadError>` で返すときに、関数の中では `return std::unexpected(...)` を使います。`unexpect` は、変数を直接エラーで作るときだけ使います。

## よくあるミス

??? failure "unexpected と取り違える"
    `unexpected` はエラーの値を包む型、`unexpect` は印です。名前が似ていますが、役目が違います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::unexpected`](unexpected.md) | エラーの値を包む型 |
| [`std::expected`](expected.md) | 本体 |
| [`std::bad_expected_access`](bad_expected_access.md) | 値がないときに `value()` が投げる例外 |

## コンパイラ対応

C++23 から使えます。

## 関連ページ

- [cpprefjp: std::unexpect](https://cpprefjp.github.io/reference/expected/unexpect.html)
- [cppreference: std::unexpect](https://en.cppreference.com/w/cpp/utility/expected/unexpect)
