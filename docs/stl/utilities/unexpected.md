---
title: std::unexpected
summary: "expected に「失敗」の値を入れるための包み。"
order: 59
tags:
  - ユーティリティ
---

# std::unexpected

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-23">C++23</span>
`#include <expected>`
</div>

`std::unexpected` は、**`std::expected` に「成功した値」ではなく「失敗した理由（エラー）」を入れるときの包み**です。`return std::unexpected(ErrorCode::kNotFound);` のように書いて、失敗を返します。成功値と同じ型のエラーを返すときの、取り違えを防ぎます。

!!! tip "ポイント"
    - 失敗を返すときは `return std::unexpected(エラー);`。成功は、値をそのまま `return`。
    - `expected<int, int>` のように、成功とエラーが同じ型でも、取り違えない。
    - `std::unexpected` 自身は、`expected` の外ではほとんど使わない。

!!! info "このページを読む前に"
    [`std::expected`](expected.md) を先に読んでください。

## 関数の詳しい説明

### std::unexpected {#unexpected}

```cpp
template <class E>
class unexpected {
 public:
  constexpr explicit unexpected(E&& e);
  constexpr const E& error() const& noexcept;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `e` | エラーの値 | 失敗の理由 |

- `return std::unexpected(エラー);` と書くと、expected が「失敗」の状態で作られます
- 包まずに `return エラー;` と書くと、成功の値として扱われてしまうことがある（型によってはコンパイルエラー）

## 実際に動かしてみる

```cpp
#include <expected>
#include <print>
#include <string>

int main() {
  std::expected<int, std::string> e = std::unexpected("読み込み失敗");
  std::println("{} {}", e.has_value(), e.error());
}
```

```text title="実行結果"
false 読み込み失敗
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ファイルの読み込みが失敗したことを返す | `return std::unexpected(LoadError::kNotFound);` |

## よくあるミス

??? failure "成功値とエラーが同じ型で取り違える"
    `std::expected<int, int>` で `return 5;` は成功の 5、`return std::unexpected(5);` は失敗の 5 です。包みが区別を付けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::expected`](expected.md) | 成功か失敗のどちらかを返す |
| [`std::optional`](optional.md) | 理由は要らない「ある / ない」 |

## コンパイラ対応

C++23 の機能です。GCC 12 / Clang 16 / MSVC 19.33 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 失敗の値を `expected` に入れる包み
    - [x] `return std::unexpected(エラー);`
    - [x] C++23

## 関連ページ

- [cpprefjp: std::unexpected](https://cpprefjp.github.io/reference/expected/unexpected.html)
- [cppreference: std::unexpected](https://en.cppreference.com/w/cpp/utility/expected/unexpected)
