---
title: std::make_optional
summary: "値から optional を作る（型を書かなくてよい）。"
order: 900
tags:
  - ユーティリティ
---

# std::make_optional

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-17">C++17</span>
`#include <optional>`
</div>

`std::optional<T>` に値を入れて作るとき、`std::optional<std::string>(std::string("Hero"))` と型を書くのは長いです。`std::make_optional(値)` は、型を推論して、値のある `optional` を作ります。コンストラクターの引数をそのまま渡す形（`make_optional<T>(args...)`）もあり、`T` をその場で作れます。

C++17 からは、CTAD で `std::optional o(5);` と書けるので、`make_optional` が必要になる場面は多くありません。

!!! tip "ポイント"
    - `make_optional(値)` は、`optional<decay した型>` を作る
    - `make_optional<T>(引数...)` は、`T` を引数から直接作って入れる
    - 値のある `optional` が作られる。空にはならない
    - C++17 の CTAD（`std::optional o(5)`）で足りる場面が多い

!!! info "このページを読む前に"
    [`std::optional`](optional.md) と [`std::nullopt`](nullopt.md) を先に読んでください。

## 関数の詳しい説明

### std::make_optional {#make_optional}

<span class="ver ver-17">C++17</span>

```cpp
template <class T>
constexpr std::optional<std::decay_t<T>> make_optional(T&& value);

template <class T, class... Args>
constexpr std::optional<T> make_optional(Args&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `value` | 任意の型 | 入れる値（1 つ目の形） |
| `T` | テンプレート引数 | 作る型（2 つ目の形） |
| `args` | コンストラクターの引数 | `T` を作るための引数 |

1 つ目の形は、値から型を推論します。文字列リテラルを渡すと、`optional<const char*>` になります。`std::string` にしたいなら、`std::string("abc")` を渡します。

2 つ目の形は、型を明示して、引数を直接渡します。`make_optional<std::string>(3, 'x')` は、`std::string(3, 'x')` で作った文字列を入れた `optional` で、一時オブジェクトのコピーやムーブがありません。

どちらの形も、値のある `optional` を返します。空の `optional` を作るのは、`std::nullopt` です。

## 実際に動かしてみる

```cpp
#include <optional>
#include <print>
#include <string>

int main() {
  // 値から型を推論
  auto a = std::make_optional(5);  // optional<int>
  std::println("{}", *a);

  // 型を指定して、引数から直接作る
  auto b = std::make_optional<std::string>(3, 'x');  // string(3, 'x')
  std::println("{}", *b);

  // 文字列リテラルは const char* になる
  auto c = std::make_optional("abc");
  static_assert(std::is_same_v<decltype(c), std::optional<const char*>>);

  // C++17: CTAD で足りる
  std::optional d(7);
  std::println("{}", *d);
}
```

```text title="実行結果"
5
xxx
7
```

## ゲームでの使いどころ

関数が `optional` を返すとき、`return std::make_optional<Player>(5, "Hero");` のように、型を指定して直接作ると、コピーが減ります。

## よくあるミス

??? failure "文字列リテラルが std::string になると思う"
    `optional<const char*>` です。`std::make_optional<std::string>("abc")` と書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::nullopt`](nullopt.md) | 空の `optional` を作る |
| [`std::optional`](optional.md) | 本体 |
| `std::optional::emplace` | 既存の `optional` の中で作り直す |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::make_optional](https://cpprefjp.github.io/reference/optional/make_optional.html)
- [cppreference: std::make_optional](https://en.cppreference.com/w/cpp/utility/optional/make_optional)
