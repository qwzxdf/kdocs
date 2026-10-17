---
title: std::source_location / std::stacktrace
tags:
  - 型・言語サポート
  - デバッグ
---

# std::source_location / std::stacktrace

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
<span class="ver ver-23">C++23</span>
`#include <source_location>` / `#include <stacktrace>`
</div>

`std::source_location` は、<strong>関数を呼んだ場所（ファイル名・行番号・関数名）</strong>を取得できる型です。ログやアサートの関数に引数として付けておくと、「どこから呼ばれたか」が自動で記録されます。`std::stacktrace`（C++23）は、**今いる場所までの関数の呼び出し履歴**を取得します。落ちる直前のログに出すと、原因を探す手がかりになります。

!!! tip "ポイント"
    - ログ関数のデフォルト引数に `std::source_location loc = std::source_location::current()` を付けると、呼んだ場所が自動で入る。
    - `__FILE__` / `__LINE__` のマクロを使わなくて済む。
    - stacktrace はコンパイラ対応がまだ限られる（GCC はリンクオプションが必要）。

## 関数一覧

| 名前 | 重要度 | 何をする |
| --- | --- | --- |
| [`std::source_location::current`](#current) | <span class="rank rank-sometimes">たまに</span> | 呼んだ場所を取得 <span class="ver ver-20">C++20</span> |
| [`file_name`](#file_name) | <span class="rank rank-sometimes">たまに</span> | ファイル名 |
| [`line`](#line) | <span class="rank rank-sometimes">たまに</span> | 行番号 |
| [`function_name`](#function_name) | <span class="rank rank-sometimes">たまに</span> | 関数名 |
| [`column`](#column) | <span class="rank rank-rare">知ってるだけ</span> | 列番号 |
| [`std::stacktrace::current`](#stacktrace) | <span class="rank rank-rare">知ってるだけ</span> | 呼び出し履歴を取得 <span class="ver ver-23">C++23</span> |

## よくある使い方

```cpp
#include <print>
#include <source_location>
#include <string_view>

// 呼んだ場所が自動で loc に入る
void Log(std::string_view message,
         std::source_location loc = std::source_location::current()) {
  std::println("[{}:{}] {}", loc.line(), loc.function_name(), message);
}

void LoadStage() { Log("ステージを読み込み中"); }

int main() {
  LoadStage();
  Log("起動完了");
}
```

```text title="実行結果"
[11:void LoadStage()] ステージを読み込み中
[15:int main()] 起動完了
```

（関数名の書き方はコンパイラによって違います。この例は GCC。ファイル名は長くなるので省いています。）

## 詳しい説明

### std::source_location::current {#current}

```cpp
static consteval source_location current() noexcept;
```

- これを書いた場所の情報を返します。**関数のデフォルト引数に書くと、呼び出した側の場所**になります（ここが一番のポイント）

### file_name {#file_name}

```cpp
constexpr const char* file_name() const noexcept;
```

- ファイル名（パス付きのことがある）

### line {#line}

```cpp
constexpr std::uint_least32_t line() const noexcept;
```

- 行番号

### function_name {#function_name}

```cpp
constexpr const char* function_name() const noexcept;
```

- 関数名。どこまで詳しく出るかはコンパイラ次第です

### column {#column}

```cpp
constexpr std::uint_least32_t column() const noexcept;
```

- 列番号（その行の何文字目か）。実装によっては 0

### std::stacktrace::current {#stacktrace}

<span class="ver ver-23">C++23</span>

```cpp
static basic_stacktrace current(const allocator_type& alloc = allocator_type()) noexcept;
```

- 今までの関数の呼び出し履歴を取得します。`std::println("{}", std::stacktrace::current())` や `std::to_string(trace)` で表示できます
- GCC では `-lstdc++exp`（GCC 13 / 14）や `-lstdc++`（GCC 15 以降）のリンクが必要、MSVC は VS 2022 17.4 以降で使えます

```cpp
// 実行には環境ごとのリンク設定が必要なので、ここでは書き方だけ
#include <print>
#include <stacktrace>

void Crash() {
  std::println("呼び出し履歴:\n{}", std::stacktrace::current());
}
```

## フラグ・オプション

フラグはありません。

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    #define LOG(msg) LogImpl(msg, __FILE__, __LINE__, __func__)
    LOG("起動");
    ```

=== "今の書き方（C++20）"

    ```cpp
    void Log(std::string_view msg, std::source_location loc = std::source_location::current());
    Log("起動");
    ```

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| ログ | どの関数から出たログか自動で付ける |
| 自作のアサート | 失敗した場所を表示する |
| クラッシュレポート | stacktrace を保存してバグの原因を探す |

## よくあるミス

??? failure "関数の中で current() を呼ぶ"
    `Log` の中で `std::source_location::current()` を呼ぶと、Log 自身の場所になってしまいます。デフォルト引数に書きます。

## 理解度チェック

!!! question "Q1. source_location をデフォルト引数に書くと、なぜ呼んだ側の場所になる？"
    <div class="spoiler" markdown>

    **答え:** デフォルト引数は「呼び出したその場所」で評価されるからです。`current()` はそこで評価され、呼び出し元のファイル・行が入ります。

    </div>

## これだけ覚える

!!! abstract "まとめ"
    - [x] ログ関数のデフォルト引数に `source_location::current()`
    - [x] `__FILE__` / `__LINE__` マクロは不要に

## 関連ページ

- [エラー処理の方針](../../design/error-handling.md)
- [cppreference: std::source_location](https://en.cppreference.com/w/cpp/utility/source_location)
