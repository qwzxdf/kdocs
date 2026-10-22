---
title: std::is_error_condition_enum
summary: "自作の列挙型を、error_condition に暗黙変換できるようにする特性。"
order: 900
group: エラーコード（<system_error>）
tags:
  - 型・言語サポート
---

# std::is_error_condition_enum

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <system_error>`
</div>

`is_error_code_enum` の、`error_condition` 版です。`std::errc` がこれに対応しています。自作の列挙型を、移植性のあるエラー条件として使いたいときに特殊化します。

!!! tip "ポイント"
    - 例外の関連の部品。
    - `try` / `catch` と組み合わせて使う。
    - ゲームでは、ファイルや外部入力のエラーの扱いに登場する。

!!! info "このページを読む前に"
    [`std::error_code`](error_code.md) を先に読んでください。

## 関数の詳しい説明

### std::is_error_condition_enum {#is_error_condition_enum}

```cpp
template <class T>
struct is_error_condition_enum : false_type {};
template <class T>
inline constexpr bool is_error_condition_enum_v = is_error_condition_enum<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる列挙型 |

- 戻り値: `error_condition` に変換できる列挙型なら `true`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <print>
#include <system_error>

int main() {
  std::println("{}", std::is_error_condition_enum_v<std::errc>);
  std::println("{}", std::is_error_condition_enum_v<int>);
}
```

```text title="実行結果"
true
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | エラーの意味を表す列挙型を作る |

## よくあるミス

??? failure "`is_error_code_enum` と取り違える"
    変換先が違います。コード（具体的な値）か、条件（移植性のある意味）かで使い分けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_error_code_enum`](is_error_code_enum.md) | error_code の版 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 自作の列挙型を、error_condition に暗黙変換できるようにする特性
    - [x] 例外の関連の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::is_error_condition_enum](https://cpprefjp.github.io/reference/exception/is_error_condition_enum.html)
- [cppreference: std::is_error_condition_enum](https://en.cppreference.com/w/cpp/error/is_error_condition_enum)
