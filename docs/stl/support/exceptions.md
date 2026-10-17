---
title: 標準の例外（<stdexcept>）
tags:
  - 型・言語サポート
  - エラー処理
---

# 標準の例外（&lt;stdexcept&gt;）

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++98〜</span>
`#include <stdexcept>` / `#include <exception>`
</div>

C++ の標準ライブラリは、失敗したときに**例外**を投げることがあります（`vector::at` の範囲外、`std::stoi` の変換失敗、filesystem の操作失敗など）。それらの例外の型は、すべて `std::exception` を親とする**決まった階層**になっています。自分で例外を投げるときも、この型を使うか継承すると、受け取る側が `catch (const std::exception& e)` でまとめて扱えます。

!!! tip "ポイント"
    - 受け取るときは **`catch (const std::exception& e)`**（const 参照で）、`e.what()` で説明を取る。
    - 自分で投げるなら `std::runtime_error("説明")` か、それを継承した型。
    - ゲームでは例外を使わない方針も多い（[エラー処理の方針](../../design/foundations/error-handling.md)）。その場合でも、標準ライブラリの例外を投げる関数を知っておく。

## 例外の階層

<div class="anim" data-type="graph" data-label="標準の例外の継承関係">
n ex std::exception 0 6
n lg logic_error 1 1.5
n rt runtime_error 1 5
n oor out_of_range 2 0
n ia invalid_argument 2 1
n le length_error 2 2
n de domain_error 2 3
n rg range_error_等 2 4
n se system_error 2 5
n fe format_error 2 6
n ba bad_alloc 1 7
n bo bad_optional_access 1 8
n bv bad_variant_access 1 9
n bf bad_function_call 1 10
n bc bad_any_cast 1 11
n be bad_expected_access 1 12
l ex lg
l ex rt
l lg oor
l lg ia
l lg le
l lg de
l rt rg
l rt se
l rt fe
l ex ba
l ex bo
l ex bv
l ex bf
l ex bc
l ex be
</div>

| 例外 | いつ出るか |
| --- | --- |
| `logic_error` | プログラムのミス（事前に防げるもの） |
| `out_of_range` | `vector::at`、`string::substr` の範囲外 |
| `invalid_argument` | `std::stoi` に数字でない文字列 |
| `length_error` | `vector::reserve` が大きすぎる |
| `runtime_error` | 実行してみないと分からないもの |
| `system_error` | OS のエラー（`filesystem_error` はこの子） |
| `format_error` | `vformat` の書式間違い |
| `bad_alloc` | メモリ不足 |
| `bad_optional_access` | `optional::value()` で値なし |
| `bad_variant_access` | `std::get` で型違い |
| `bad_function_call` | 空の `std::function` を呼んだ |
| `bad_any_cast` | `any_cast` で型違い |
| `bad_expected_access` | `expected::value()` でエラー |

## 型一覧

| 型 | 重要度 | 投げられる場面 |
| --- | --- | --- |
| [`std::exception`](#exception) | <span class="rank rank-sometimes">たまに</span> | すべての親。catch でまとめて受け取る |
| [`std::runtime_error`](#runtime_error) | <span class="rank rank-sometimes">たまに</span> | 自分で投げるときの定番 |
| [`std::out_of_range`](#out_of_range) | <span class="rank rank-sometimes">たまに</span> | `at()`、`substr`、`stoi` の範囲外 |
| [`std::invalid_argument`](#invalid_argument) | <span class="rank rank-sometimes">たまに</span> | `stoi` などに変換できない文字列 |
| [`std::logic_error`](#logic_error) | <span class="rank rank-rare">知ってるだけ</span> | プログラムのミスを表す親 |
| [`std::bad_alloc`](#bad_alloc) | <span class="rank rank-rare">知ってるだけ</span> | メモリ確保の失敗 |
| [`std::system_error`](#system_error) | <span class="rank rank-rare">知ってるだけ</span> | OS のエラー（エラーコード付き） |
| [`std::exception_ptr`](#exception_ptr) | <span class="rank rank-rare">知ってるだけ</span> | 例外を保存して、別の場所で投げ直す |

## よくある使い方

```cpp
#include <print>
#include <stdexcept>
#include <string>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};
  try {
    std::println("{}", v.at(10));
  } catch (const std::out_of_range& e) {  // 細かい型から先に書く
    std::println("範囲外");
  } catch (const std::exception& e) {     // その他全部
    std::println("その他: {}", e.what());
  }

  try {
    std::stoi("abc");
  } catch (const std::invalid_argument&) {
    std::println("数字ではない");
  }
}
```

```text title="実行結果"
範囲外
数字ではない
```

## 詳しい説明

### std::exception {#exception}

```cpp
class exception {
 public:
  virtual const char* what() const noexcept;
};
```

- すべての標準例外の親。`what()` で説明の文字列が取れます

### std::runtime_error {#runtime_error}

```cpp
class runtime_error : public exception {
 public:
  explicit runtime_error(const std::string& what_arg);
};
```

- 実行してみないと分からない失敗（ファイルが壊れていた、など）。自分で投げるときに一番よく使います

```cpp
#include <print>
#include <stdexcept>
#include <string>

int LoadLevel(const std::string& name) {
  if (name.empty()) {
    throw std::runtime_error("ステージ名が空です");
  }
  return 1;
}

int main() {
  try {
    LoadLevel("");
  } catch (const std::exception& e) {
    std::println("失敗: {}", e.what());
  }
}
```

```text title="実行結果"
失敗: ステージ名が空です
```

### std::out_of_range {#out_of_range}

```cpp
class out_of_range : public logic_error;
```

- 範囲外を表します。`vector::at`、`string::at`、`string::substr`、`map::at`、`stoi`（int に入らない）が投げます

### std::invalid_argument {#invalid_argument}

```cpp
class invalid_argument : public logic_error;
```

- 引数がおかしいことを表します。`std::stoi` などに数字で始まらない文字列を渡すと投げられます

### std::logic_error {#logic_error}

```cpp
class logic_error : public exception;
```

- プログラムのミス（事前に確認すれば防げた失敗）を表す型の親です

### std::bad_alloc {#bad_alloc}

```cpp
class bad_alloc : public exception;
```

- `new` や vector の確保でメモリが足りなかったときに投げられます

### std::system_error {#system_error}

```cpp
class system_error : public runtime_error {
 public:
  const std::error_code& code() const noexcept;
};
```

- OS が返したエラーコード付きの例外。filesystem の失敗（`filesystem_error`）はこれの子です

### std::exception_ptr {#exception_ptr}

```cpp
std::exception_ptr std::current_exception() noexcept;
[[noreturn]] void std::rethrow_exception(std::exception_ptr p);
```

- 今処理中の例外を保存して、あとで（別のスレッドで）投げ直せます。`std::async` の例外が `get()` で投げ直される仕組みもこれです

```cpp
#include <exception>
#include <print>
#include <stdexcept>
#include <thread>

int main() {
  std::exception_ptr error;
  std::jthread([&error] {
    try {
      throw std::runtime_error("スレッドの中で失敗");
    } catch (...) {
      error = std::current_exception();  // 保存しておく
    }
  }).join();

  try {
    if (error) {
      std::rethrow_exception(error);  // メインスレッドで投げ直す
    }
  } catch (const std::exception& e) {
    std::println("{}", e.what());
  }
}
```

```text title="実行結果"
スレッドの中で失敗
```

## フラグ・オプション

| 書き方 | 意味 |
| --- | --- |
| `catch (...)` | どんな例外でも受け取る（型は分からない） |
| `throw;` | 今受け取った例外をそのまま投げ直す |
| `noexcept` | この関数は例外を投げないと約束する（投げると `std::terminate`） |

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| 例外を使うプロジェクトの読み込み処理 | ファイル形式のエラーを runtime_error で投げ、ロード画面でまとめて受け取る |
| 例外を使わないプロジェクト | 例外を投げる標準関数（`at`、`stoi`、filesystem）を避ける |

## よくあるミス

??? failure "値で catch する"
    `catch (std::exception e)` は、派生クラスの部分が切り落とされて（スライシング）`what()` の説明が変わることがあります。必ず `const&` で受け取ります。

??? failure "catch の順番が逆"
    親の型（`std::exception`）を先に書くと、子の型（`std::out_of_range`）の catch には来ません。細かい型から順に書きます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] すべての親は std::exception。const& で受けて what()
    - [x] 自分で投げるなら runtime_error
    - [x] catch は細かい型から

## 関連ページ

- [エラー処理の方針](../../design/foundations/error-handling.md)
- [cppreference: Exceptions](https://en.cppreference.com/w/cpp/error/exception)
