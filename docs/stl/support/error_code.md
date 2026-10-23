---
title: std::error_code
summary: "OS やライブラリのエラーを、値と分類で表す（例外を使わない失敗の通知）。"
order: 30
group: エラーコード（<system_error>）
tags:
  - 型・言語サポート
---

# std::error_code

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++11</span>
`#include <system_error>`
</div>

`std::error_code` は、**エラーを「値」と「分類（カテゴリ）」で表す**クラスです。例外を投げずに失敗を伝えるため、`filesystem` などの関数が引数で受け取ります。`if (ec)` で「エラーがあるか」を調べ、`ec.message()` で説明文を取れます。

!!! tip "ポイント"
    - `if (ec)` で、エラーがあるか調べる。
    - `ec == std::errc::no_such_file_or_directory` のように、環境に依存しない名前で比べる。
    - 例外を使う版と使わない版の両方を用意するのが標準ライブラリの流儀。

!!! info "このページを読む前に"
    - [stl/index.md](../index.md)（STL 全体の地図（どこに何があるか））
    - [テンプレート](../../basics/template.md)（テンプレートの基礎）

## 関数の詳しい説明

### std::error_code {#error_code}

```cpp
class error_code {
 public:
  int value() const noexcept;
  const error_category& category() const noexcept;
  std::string message() const;
  explicit operator bool() const noexcept;
};
```

- 戻り値: （クラス）。`value`、`category`、`message`、`bool` への変換
- 計算量: O(1)

```cpp
#include <print>
#include <system_error>

int main() {
  std::error_code ec = std::make_error_code(std::errc::no_such_file_or_directory);
  std::println("{} {}", static_cast<bool>(ec), ec == std::errc::no_such_file_or_directory);
}
```

```text title="実行結果"
true true
```

### value {#value}

```cpp
int value() const noexcept;
```

- 計算量: 定数

エラーの番号。意味は、`category()` が決めます。

### category {#category}

```cpp
const error_category& category() const noexcept;
```

- 計算量: 定数

エラーの種類（`generic_category`・`system_category` など）。

### message {#message}

```cpp
std::string message() const;
```

- 計算量: 定数

エラーの説明の文字列（`category().message(value())`）。ログに出すのに使います。

### clear {#clear}

```cpp
void clear() noexcept;
```

- 計算量: 定数

エラーなし（値 0、システムのカテゴリ）に戻します。

### assign {#assign}

```cpp
void assign(int val, const error_category& cat) noexcept;
```

- 計算量: 定数

エラーの番号とカテゴリを設定します。

### explicit operator bool {#op_bool}

```cpp
explicit operator bool() const noexcept;
```

- 計算量: 定数

エラーがあれば（`value() != 0`）`true`。`if (ec) { ... }` と書けます。

### default_error_condition {#default_error_condition}

```cpp
error_condition default_error_condition() const noexcept;
```

- 計算量: 定数

OS に依存しない形の `error_condition` に変換します。`==` で `errc` と比べられるのは、これのおかげです。

### operator= {#op_assign}

```cpp
error_code& operator=(ErrorCodeEnum e) noexcept;
```

- 計算量: 定数

`errc` などの列挙値から代入します。

### operator== {#op_eq}

```cpp
bool operator==(const error_code& lhs, const error_code& rhs) noexcept;
bool operator==(const error_code& code, const error_condition& cond) noexcept;
```

- 計算量: 定数

`error_code` どうし、または `error_condition` と比べます。`ec == std::errc::no_such_file_or_directory` のように使います。

### operator<=> <span class="ver ver-20">C++20</span> {#op_cmp data-toc-label="operator<=>"}

```cpp
std::strong_ordering operator<=>(const error_code& lhs, const error_code& rhs) noexcept;
```

- 計算量: 定数

カテゴリ、番号の順で比べる三方比較。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ファイル操作の失敗を、例外なしで受け取る | `std::filesystem::exists(path, ec)` |

## よくあるミス

??? failure "value() の数値を直接比べる"
    OS ごとに数値が違います。`std::errc` と比べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`errc`](errc.md) | 環境に依存しない名前 |
| [`error_condition`](error_condition.md) | 比べるための条件 |
| [`std::expected`](../utilities/expected.md) | 値とエラーを一緒に返す |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 値と分類でエラーを表す
    - [x] `if (ec)` で調べる
    - [x] 比べるのは `std::errc`

## 関連ページ

- [cpprefjp: std::error_code](https://cpprefjp.github.io/reference/system_error/error_code.html)
- [cppreference: std::error_code](https://en.cppreference.com/w/cpp/error/error_code)
