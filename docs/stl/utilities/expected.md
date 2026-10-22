---
title: std::expected
summary: "「成功した値」か「エラー」の、どちらかを返す。例外を使わないエラー処理に。"
order: 52
tags:
  - ユーティリティ
  - エラー処理
---

# std::expected

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="perf perf-4">◎ 速い</span>
<span class="ver ver-23">C++23</span>
`#include <expected>`
</div>

`std::expected<T, E>` は、<strong>「成功したときの値 T」か「失敗したときのエラー E」のどちらかを持つ型</strong>です。[`std::optional`](optional.md) は「値があるか無いか」しか分かりませんが、expected は**なぜ失敗したか**も一緒に返せます。例外を使わずにエラーを伝えられるので、例外を切っているゲームのコードと相性が良いです。

!!! tip "ポイント"
    - <strong>失敗の理由を返したい関数の戻り値に使う。</strong> ファイル読み込み、セーブデータの解析、ネットワークなど。
    - 成功なら `return 値;`、失敗なら `return std::unexpected(エラー);`。
    - 成功したかは `if (result)`、値は `*result`、エラーは `result.error()`。
    - エラーの型は `enum class` か `std::string` が使いやすい。

!!! info "このページを読む前に"
    [`std::optional`](optional.md) を先に読むと、ほぼ差分だけで理解できます。

## 宣言

```cpp
template <class T, class E>
class expected;

template <class E>
class unexpected;
```

| テンプレート引数 | 意味 | 例 |
| --- | --- | --- |
| `T` | 成功したときの値の型（値が要らなければ `void`） | `int`、`Texture`、`void` |
| `E` | 失敗したときのエラーの型 | `enum class LoadError`、`std::string` |

## 関数一覧

| 関数 | 重要度 | 何をする |
| --- | --- | --- |
| [`operator bool`](#bool) | <span class="rank rank-must">必須</span> | 成功したか |
| [`operator*`](#deref) | <span class="rank rank-must">必須</span> | 成功の値（チェックなし） |
| [`error`](#error) | <span class="rank rank-must">必須</span> | 失敗のエラー |
| [`operator->`](#arrow) | <span class="rank rank-often">よく使う</span> | 成功の値のメンバ |
| [`value_or`](#value_or) | <span class="rank rank-often">よく使う</span> | 成功ならその値、失敗なら代わりの値 |
| [`has_value`](#has_value) | <span class="rank rank-sometimes">たまに</span> | 成功したか（bool と同じ） |
| [`value`](#value) | <span class="rank rank-sometimes">たまに</span> | 成功の値（失敗なら例外） |
| [`and_then`](#and_then) | <span class="rank rank-sometimes">たまに</span> | 成功なら次の処理（expected を返す）へつなぐ |
| [`transform`](#transform) | <span class="rank rank-sometimes">たまに</span> | 成功なら値を変換 |
| [`or_else`](#or_else) | <span class="rank rank-rare">知ってるだけ</span> | 失敗なら回復の処理を呼ぶ |
| [`transform_error`](#transform_error) | <span class="rank rank-rare">知ってるだけ</span> | 失敗ならエラーを変換 |
| [`error_or`](#error_or) | <span class="rank rank-rare">知ってるだけ</span> | 失敗ならそのエラー、成功なら代わりのエラー <span class="ver ver-26">C++26</span> |

## よくある使い方

### 1. 失敗の理由を返す

```cpp
#include <expected>
#include <print>
#include <string>

enum class LoadError { kNotFound, kBroken };

std::expected<int, LoadError> LoadHighScore(const std::string& file) {
  if (file.empty()) {
    return std::unexpected(LoadError::kNotFound);
  }
  if (file == "broken.dat") {
    return std::unexpected(LoadError::kBroken);
  }
  return 9800;
}

int main() {
  for (std::string file : {"save.dat", "", "broken.dat"}) {
    auto result = LoadHighScore(file);
    if (result) {
      std::println("ハイスコア {}", *result);
    } else if (result.error() == LoadError::kNotFound) {
      std::println("セーブなし");
    } else {
      std::println("データが壊れている");
    }
  }
}
```

```text title="実行結果"
ハイスコア 9800
セーブなし
データが壊れている
```

### 2. 値の要らない処理（void）

```cpp
#include <expected>
#include <print>
#include <string>

std::expected<void, std::string> Connect(bool online) {
  if (!online) {
    return std::unexpected("オフラインです");
  }
  return {};  // 成功（値なし）
}

int main() {
  if (auto r = Connect(false); !r) {
    std::println("接続失敗: {}", r.error());
  }
}
```

```text title="実行結果"
接続失敗: オフラインです
```

## 関数の詳しい説明

### operator bool {#bool}

```cpp
constexpr explicit operator bool() const noexcept;
```

- 成功なら `true`、失敗なら `false`

### operator* {#deref}

```cpp
constexpr T& operator*() & noexcept;
```

- 成功の値を返します。**失敗のときに使うと未定義動作**

### error {#error}

```cpp
constexpr E& error() & noexcept;
constexpr const E& error() const& noexcept;
```

- 失敗のエラーを返します。**成功のときに使うと未定義動作**

### operator-> {#arrow}

```cpp
constexpr T* operator->() noexcept;
```

- 成功の値のメンバにアクセスします

```cpp
#include <expected>
#include <print>
#include <string>

struct Config {
  int width;
  int height;
};

std::expected<Config, std::string> LoadConfig() { return Config{1280, 720}; }

int main() {
  auto config = LoadConfig();
  if (config) {
    std::println("{}x{}", config->width, (*config).height);
  } else {
    std::println("{}", config.error());
  }
}
```

```text title="実行結果"
1280x720
```

### value_or {#value_or}

```cpp
template <class U>
constexpr T value_or(U&& default_value) const&;
```

- 成功ならその値、失敗なら `default_value` を返します

```cpp
#include <expected>
#include <print>

std::expected<int, int> Parse(bool ok) {
  if (ok) {
    return 42;
  }
  return std::unexpected(-1);
}

int main() {
  std::println("{} {}", Parse(true).value_or(0), Parse(false).value_or(0));
}
```

```text title="実行結果"
42 0
```

### has_value {#has_value}

```cpp
constexpr bool has_value() const noexcept;
```

- 成功なら `true`

### value {#value}

```cpp
constexpr T& value() &;
```

- 成功の値を返します。**失敗なら `std::bad_expected_access<E>` 例外**

```cpp
#include <expected>
#include <print>

int main() {
  std::expected<int, int> r = std::unexpected(5);
  std::println("{}", r.has_value());
  try {
    std::println("{}", r.value());
  } catch (const std::bad_expected_access<int>& e) {
    std::println("失敗: エラー {}", e.error());
  }
}
```

```text title="実行結果"
false
失敗: エラー 5
```

### and_then {#and_then}

```cpp
template <class F>
constexpr auto and_then(F&& f) &;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `f` | 関数 | 成功の値を受け取り、**expected（エラーの型は同じ）を返す** |

- 成功なら `f(値)` の結果、失敗ならそのエラーをそのまま返します

### transform {#transform}

```cpp
template <class F>
constexpr auto transform(F&& f) &;
```

- 成功なら `f(値)` を新しい成功の値にします。失敗ならそのまま

### or_else {#or_else}

```cpp
template <class F>
constexpr auto or_else(F&& f) &;
```

- 失敗なら `f(エラー)`（expected を返す関数）を呼んで回復を試みます。成功ならそのまま

### transform_error {#transform_error}

```cpp
template <class F>
constexpr auto transform_error(F&& f) &;
```

- 失敗ならエラーを `f(エラー)` に変換します（エラーコードを表示用の文字列にするなど）

```cpp
#include <expected>
#include <print>
#include <string>

enum class Err { kEmpty, kRange };

std::expected<int, Err> Parse(const std::string& s) {
  if (s.empty()) {
    return std::unexpected(Err::kEmpty);
  }
  return std::stoi(s);
}

std::expected<int, Err> CheckRange(int v) {
  if (v < 0 || v > 100) {
    return std::unexpected(Err::kRange);
  }
  return v;
}

int main() {
  for (std::string input : {"40", "500", ""}) {
    auto text = Parse(input)
                    .and_then(CheckRange)
                    .transform([](int v) { return std::to_string(v) + "%"; })
                    .transform_error([](Err e) {
                      return e == Err::kEmpty ? std::string("空") : std::string("範囲外");
                    });
    std::println("{}", text ? *text : "エラー: " + text.error());
  }
  auto fixed = Parse("").or_else([](Err) { return std::expected<int, Err>(0); });
  std::println("回復後 {}", *fixed);
}
```

```text title="実行結果"
40%
エラー: 範囲外
エラー: 空
回復後 0
```

### error_or <span class="ver ver-26">C++26</span> {#error_or data-toc-label="error_or"}

- 失敗ならそのエラー、成功なら引数で渡したエラーを返します。C++26 の機能です

## フラグ・オプション

| 値 | 重要度 | 意味 |
| --- | --- | --- |
| `std::unexpected(e)` | <span class="rank rank-must">必須</span> | 失敗を表す |
| `std::unexpect` | <span class="rank rank-rare">知ってるだけ</span> | コンストラクタで「エラーとして作る」目印（`std::expected<int, Err> r(std::unexpect, Err::kEmpty);`） |

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    // 戻り値でエラーコード、結果は出力引数
    LoadError LoadHighScore(const std::string& file, int* out_score);

    // 例外
    int LoadHighScore(const std::string& file);  // 失敗すると throw
    ```

=== "今の書き方（C++23）"

    ```cpp
    std::expected<int, LoadError> LoadHighScore(const std::string& file);
    ```

### emplace {#emplace}

```cpp
template <class... Args>
T& emplace(Args&&... args) noexcept;
```

- 計算量: 定数 + 構築

今の中身を捨てて、引数から値をその場で作り直します（成功の状態になります）。

### swap {#swap}

```cpp
void swap(expected& other);
```

- 計算量: 中身による

中身を入れ替えます。

### operator= {#op_assign}

```cpp
expected& operator=(const expected& rhs);
expected& operator=(expected&& rhs);
template <class U = T> expected& operator=(U&& v);
```

- 計算量: 中身による

別の `expected` または値を代入します。

### operator== {#op_eq}

```cpp
template <class T2, class E2>
bool operator==(const expected& x, const expected<T2, E2>& y);
```

- 計算量: 中身による

どちらも成功なら値を、どちらも失敗ならエラーを比べます。成功と失敗の比較は `false`。

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| ファイル読み込み | `std::expected<Texture, LoadError> LoadTexture(path)` |
| セーブデータ | バージョン違い・破損を区別して返す |
| 設定の解析 | どの行が間違っているかを文字列で返す |
| ネットワーク | タイムアウト・切断・認証失敗を区別 |

## パフォーマンス

- 値とエラーのどちらか一方だけを持つので、大きさは「大きいほう + 少し」です。ヒープは使いません。
- 例外と違って、失敗しても普通の戻り値と同じコストです。

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| 失敗なのに `*r` / `r->` | 未定義動作 |
| 成功なのに `r.error()` | 未定義動作 |
| 失敗なのに `r.value()` | `std::bad_expected_access` 例外 |

## よくあるミス

??? failure "エラーを unexpected で包み忘れる"
    ```cpp
    std::expected<int, int> F() {
      return -1;  // エラーのつもりが「成功の値 -1」になる
      return std::unexpected(-1);  // OK
    }
    ```

??? failure "確認せずに * で取り出す"
    `auto r = Load(); Use(*r);` は失敗したときに未定義動作です。

## 類似クラス

| 名前 | 違い | こっちを使うとき |
| --- | --- | --- |
| [`std::optional`](optional.md) | 失敗の理由を持てない | 「無い」だけで十分 |
| 例外（`throw`） | 呼び出し元をいくつも飛び越えて伝わる | 本当に想定外のエラー（ゲームでは切ることが多い） |
| [`std::variant<T, E>`](variant.md) | どちらが成功か決まっていない | 成功・失敗ではない「どれか」 |

## コンパイラ対応

| 機能 | MSVC | GCC | Clang (libc++) |
| --- | --- | --- | --- |
| `std::expected` <span class="ver ver-23">C++23</span> | VS 2022 17.3〜 | 12〜 | 16〜 |
| `and_then` / `transform` など <span class="ver ver-23">C++23</span> | VS 2022 17.6〜 | 13〜 | 17〜 |

## これだけ覚える

!!! abstract "まとめ"
    - [x] 成功の値か失敗の理由を返すなら `std::expected<T, E>`
    - [x] 失敗は `return std::unexpected(e);`
    - [x] `if (r)` → `*r`、だめなら `r.error()`

## 関連ページ

- [cpprefjp: std::expected](https://cpprefjp.github.io/reference/expected/expected.html)
- [cppreference: std::expected](https://en.cppreference.com/w/cpp/utility/expected)
