---
title: std::is_error_code_enum
summary: "自作の列挙型を、error_code に暗黙変換できるようにする特性。"
order: 900
group: エラーコード（<system_error>）
tags:
  - 型・言語サポート
---

# std::is_error_code_enum

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <system_error>`
</div>

ゲーム固有のエラー（`GameError::OutOfMana`）を `std::error_code` として扱いたいとき、`is_error_code_enum<GameError>` を `true_type` に特殊化し、`make_error_code(GameError)` を定義します。すると、`std::error_code ec = GameError::OutOfMana;` と書けます。

!!! tip "ポイント"
    - 例外の関連の部品。
    - `try` / `catch` と組み合わせて使う。
    - ゲームでは、ファイルや外部入力のエラーの扱いに登場する。

!!! info "このページを読む前に"
    [`std::error_code`](error_code.md) を先に読んでください。

## 関数の詳しい説明

### std::is_error_code_enum {#is_error_code_enum}

```cpp
template <class T>
struct is_error_code_enum : false_type {};
template <class T>
inline constexpr bool is_error_code_enum_v = is_error_code_enum<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる列挙型 |

- 戻り値: `error_code` に変換できる列挙型なら `true`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <system_error>

struct GameCategory : std::error_category {
  const char* name() const noexcept override { return "game"; }
  std::string message(int c) const override { return c == 1 ? "out of mana" : "unknown"; }
};
const GameCategory& Game() {
  static GameCategory c;
  return c;
}

enum class GameError { OutOfMana = 1 };

namespace std {
template <>
struct is_error_code_enum<GameError> : true_type {};
}  // namespace std

std::error_code make_error_code(GameError e) {
  return {static_cast<int>(e), Game()};
}

int main() {
  std::error_code ec = GameError::OutOfMana;
  std::println("{}", ec.message());
}
```

```text title="実行結果"
out of mana
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 自作のエラー列挙型を標準のエラーの仕組みに乗せる |

## よくあるミス

??? failure "`std` 名前空間の外で特殊化する"
    特殊化は `namespace std` の中に書きます。`make_error_code` は、列挙型と同じ名前空間に置きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`error_category`](error_category.md) | 分類を作る |
| [`make_error_code`](make_error_code.md) | コードを作る |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 自作の列挙型を error_code に暗黙変換できるようにする特性
    - [x] 例外の関連の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::is_error_code_enum](https://cpprefjp.github.io/reference/exception/is_error_code_enum.html)
- [cppreference: std::is_error_code_enum](https://en.cppreference.com/w/cpp/error/is_error_code_enum)
