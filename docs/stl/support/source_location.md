---
title: std::source_location
summary: "今の場所（ファイル・行・関数）を取得する。"
order: 1
tags:
  - 型・言語サポート
---

# std::source_location

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <source_location>`
</div>

ログに「どのファイルの何行目のどの関数から出たか」を付けたいことは、よくあります。C++17 までは `__FILE__` と `__LINE__` を使うためにログ関数を**マクロ**にするしかありませんでした。マクロは名前空間を無視しますし、引数を何回も評価されるなどの落とし穴もあります。

`std::source_location` を使うと普通の関数のまま**呼び出した側の場所**を受け取れます。関数の引数の既定値に `std::source_location::current()` を書いておくだけで、呼ぶ側は何も書かなくても呼んだ場所のファイル名、行、関数名が入ります。

!!! tip "ポイント"
    - 関数の引数の既定値に `current()` を書くと呼び出し側の位置が取れる。関数の中で呼ぶとその関数の中の位置になる。
    - 取り出せるのは `file_name()`、`line()`、`function_name()`、`column()` の 4 つ。
    - `function_name()` と `column()` の中身はコンパイラによって違う。結果を解析しない。
    - `file_name()` はコンパイラに渡したパスのまま。ビルドの仕方で相対にも絶対にもなる。
    - `__FILE__` や `__LINE__` の関数版の置き換え。

!!! info "このページを読む前に"
    関数の引数の既定値と `__FILE__` などのマクロは、[定義済みマクロ](../../basics/predefined-macros.md) で説明しています。既定値が「呼び出した側」で評価される点がこのクラスの仕組みの中心です。

## 関数一覧

| 関数 | 何を返すか | 型 |
| --- | --- | --- |
| [`current`](#current) | 今の場所を表すオブジェクトを作る | `source_location` |
| [`file_name`](#file_name) | ファイル名 | `const char*` |
| [`line`](#line) | 行番号 | `std::uint_least32_t` |
| [`function_name`](#function_name) | 関数名 | `const char*` |
| [`column`](#column) | 列番号 | `std::uint_least32_t` |

## よくある使い方

### 1. ログに呼び出し位置を付ける

呼び出した場所がログに出ます。下のプログラムは関数の種類ごとに `function_name()` が何を返すかも見せています。

```cpp
#include <filesystem>
#include <print>
#include <source_location>
#include <string>
#include <string_view>
#include <type_traits>

// 呼び出した側の場所を引数の既定値で受け取る。
void Log(std::string_view msg, std::source_location loc = std::source_location::current()) {
  std::println("{}:{} [{}] {}", loc.file_name(), loc.line(), loc.function_name(), msg);
}

struct Player {
  Player() { Log("コンストラクタ"); }
  void Update(float dt) { Log("メンバ関数"); }
  template <class T>
  void Set(T value) { Log("テンプレート"); }
};

namespace game {
void Reset(int level) { Log("名前空間の関数"); }
}  // namespace game

int main() {
  Log("main の中");
  Player player;
  player.Update(0.016f);
  player.Set(1.5f);
  game::Reset(3);
  auto lambda = [] { Log("ラムダ式"); };
  lambda();

  // 場所の中身を 1 つずつ見る。
  std::source_location here = std::source_location::current();
  std::println("file_name     = {}", here.file_name());
  std::println("line          = {}", here.line());
  std::println("column        = {}", here.column());
  std::println("function_name = {}", here.function_name());

  // ファイル名だけにする。
  std::println("filename only = {}", std::filesystem::path(here.file_name()).filename().string());
}
```

`g++ src/main.cpp` でコンパイルして動かした結果です（GCC 14.2）。

```text title="実行結果（GCC）"
src/main.cpp:25 [int main()] main の中
src/main.cpp:14 [Player::Player()] コンストラクタ
src/main.cpp:15 [void Player::Update(float)] メンバ関数
src/main.cpp:17 [void Player::Set(T) [with T = float]] テンプレート
src/main.cpp:21 [void game::Reset(int)] 名前空間の関数
src/main.cpp:30 [main()::<lambda()>] ラムダ式
file_name     = src/main.cpp
line          = 34
column        = 60
function_name = int main()
filename only = main.cpp
```

Windows の Clang 21（MSVC の標準ライブラリ）では、関数名の形式が変わります。行番号はどの場合も呼び出した行（14、15、17…）で同じです。

```text title="実行結果（Clang 21、Windows）"
src/main.cpp:25 [int __cdecl main(void)] main の中
src/main.cpp:14 [__cdecl Player::Player(void)] コンストラクタ
src/main.cpp:15 [void __cdecl Player::Update(float)] メンバ関数
src/main.cpp:17 [void __cdecl Player::Set(T) [T = float]] テンプレート
src/main.cpp:21 [void __cdecl game::Reset(int)] 名前空間の関数
src/main.cpp:30 [auto __cdecl main()::(anonymous class)::operator()(void) const] ラムダ式
file_name     = src/main.cpp
line          = 34
column        = 31
function_name = int __cdecl main(void)
filename only = main.cpp
```

「Compiler Explorer で実行」を押すとファイル名が `<source>` になるなど、上とは少し違う結果になります。

### 2. 書式付きのログにする

`Log("HP は {} です", hp)` のように書式文字列と引数を渡すログ関数にも位置を付けたくなります。ただ、引数が可変個（`Args...`）だと末尾に `source_location` の既定値を置けません。書式文字列と位置を 1 つの入れ物にまとめる定番の書き方があります。

```cpp
#include <format>
#include <iostream>
#include <source_location>
#include <type_traits>

// 書式文字列と、呼び出し位置を 1 つにまとめる入れ物。
template <class... Args>
struct FormatLocation {
  std::format_string<Args...> fmt;
  std::source_location loc;

  // 文字列リテラルから暗黙に作れる。位置は、ここで呼ばれた場所になる。
  template <class T>
  consteval FormatLocation(const T& s, std::source_location l = std::source_location::current())
      : fmt(s), loc(l) {}
};

// std::type_identity_t で、Args の推論を後ろの引数だけに任せる。
template <class... Args>
void LogF(FormatLocation<std::type_identity_t<Args>...> f, Args&&... args) {
  std::cout << f.loc.file_name() << ":" << f.loc.line() << " "
            << std::vformat(f.fmt.get(), std::make_format_args(args...)) << std::endl;
}

int main() {
  LogF("HP は {} です", 42);
  LogF("{} の座標は ({}, {})", "player", 1.5f, -2.0f);
}
```

```text title="実行結果（GCC / Clang）"
src/fmt.cpp:28 HP は 42 です
src/fmt.cpp:29 player の座標は (1.5, -2)
```

`FormatLocation` のコンストラクタが文字列リテラルから暗黙に変換されて呼ばれるときその既定引数の `current()` が、呼び出し側の位置になります。`std::type_identity_t` は `Args` を `FormatLocation` ではなく後ろの引数（`args`）だけから推論させるために付けています。これがないと書式文字列の型から `Args` を決めようとして、コンパイルに失敗します。

## 関数の詳しい説明

### std::source_location::current {#current}

```cpp
static consteval source_location current() noexcept;
```

これを書いた場所の情報を持つ `source_location` を返します。

関数の**本体の中**で呼ぶとその関数の中の位置になります。**引数の既定値**に書くとその既定値が評価される場所、つまり関数を**呼んだ側**の位置になります。ログ関数がこの仕組みで呼び出し位置を取ります。

`consteval` なのでコンパイル時に値が決まります。ただ、返ってきたオブジェクトは普通の値なので、変数に入れたり関数の引数に渡したりコピーしたりできます。ファイル名や関数名の文字列はプログラムの全期間で生きる領域に置かれるので、オブジェクトをコピーしてもポインターが無効になることはありません。

### file_name {#file_name}

```cpp
constexpr const char* file_name() const noexcept;
```

ソース ファイルの名前を返します。

返る文字列は**コンパイラに渡したパスそのまま**です。`g++ src/main.cpp` と相対パスで渡せば `src/main.cpp`、絶対パスで渡せば `C:/kdemo/game/src/main.cpp` です。次は同じソースを渡し方だけ変えて動かした結果です（GCC、Clang とも同じでした）。

```text title="g++ C:/kdemo/game/src/main.cpp"
C:/kdemo/game/src/main.cpp:25 [int main()] main の中
file_name     = C:/kdemo/game/src/main.cpp
filename only = main.cpp
```

Visual Studio でビルドすると、ふつうは絶対パスが渡されるので、ログが長くなります。ファイル名だけが欲しいときは上の例のように `std::filesystem::path(...).filename()` を使います。毎回のログで文字列を作るのが気になるなら `std::string_view` で最後の `/` か `\` より後ろを切り出します。

リリースする実行ファイルには `file_name()` の文字列が埋め込まれます。パスにユーザー名が入っていると、プライバシーの問題になるので、`/d1trimfile:`（MSVC）や `-ffile-prefix-map=`（GCC / Clang）で、前半を取り除いておきます（[定義済みマクロ](../../basics/predefined-macros.md#file)）。

### line {#line}

```cpp
constexpr std::uint_least32_t line() const noexcept;
```

行番号を返します。1 から始まります。上の実行結果ではどの場合も `Log(...)` と書いた行（14、15、17…）でした。

### function_name {#function_name}

```cpp
constexpr const char* function_name() const noexcept;
```

関数の名前を返します。**中身の形式は規格で決まっていません**。上の実行結果を関数の種類ごとに並べると、次のようになります。

| 場所 | GCC | Clang（Windows） |
| --- | --- | --- |
| `main` | `int main()` | `int __cdecl main(void)` |
| コンストラクタ | `Player::Player()` | `__cdecl Player::Player(void)` |
| メンバ関数 | `void Player::Update(float)` | `void __cdecl Player::Update(float)` |
| テンプレート | `void Player::Set(T) [with T = float]` | `void __cdecl Player::Set(T) [T = float]` |
| 名前空間の関数 | `void game::Reset(int)` | `void __cdecl game::Reset(int)` |
| ラムダ式 | `main()::<lambda()>` | `auto __cdecl main()::(anonymous class)::operator()(void) const` |

どちらも、戻り値の型、名前空間やクラス名、引数の型まで含んだ長い形で返ります。GCC は `__PRETTY_FUNCTION__` に近い形で Clang（Windows）は、MSVC の `__FUNCSIG__` に近い形です。Windows の Clang は MSVC の標準ライブラリを使うので、`__cdecl`（Windows の呼び出し規約）が付きます。Visual Studio の `cl` も同じ標準ライブラリなので、`__cdecl` 付きの形になるはずですが、手元では確認できていません。Linux の Clang（libc++）は、また別の形式になることがあります。

テンプレート関数のときは `T` が実際に何だったか（`[with T = float]`）まで分かるので、デバッグには便利です。ラムダ式は名前のない関数なので、`<lambda()>` や `(anonymous class)` のようなコンパイラが決めた名前になります。

**この文字列をプログラムで解析してはいけません。** コンパイラやバージョンで形式が変わるので、画面やログファイルに出すだけにします。関数名だけを短く出したいときは関数の中で `__func__`（`Update` のような名前空間や型のない名前）を使います。

### column {#column}

```cpp
constexpr std::uint_least32_t column() const noexcept;
```

列番号（その行の左から何文字目か）を返します。1 から始まります。

どの位置を「この場所」とみなすかが、コンパイラごとに違います。次のコードで `current()` を呼んだ行の列を比べます。

```cpp
  std::source_location here = std::source_location::current();
```

行頭の空白 2 文字のあと `std::source_location here = ` の次の列が 31 です。`std::source_location::current` という名前の先頭が 31 列目で、`(` が 60 列目になります。実行結果は次のとおりです。

| コンパイラ | `column()` | 指している場所 |
| --- | --- | --- |
| GCC 14 | 60 | `current` の後ろの `(` |
| Clang 21（Windows） | 31 | `std::source_location::current` の先頭 |

どちらが正しいということはなく、実装によって違います。ログには列まではあまり必要ないので、`line()` までにしておくのが無難です。

## ゲームでの使いどころ

ログ関数、アサート、リソースのロード失敗の報告など「どこで起きたか」を知りたい場面で使います。`Log`、`Warn`、`Error` のように重要度ごとの関数を作るならそれぞれに `source_location` の引数を持たせます。

Release ビルドでログの呼び出しごとにファイル名と関数名の文字列が実行ファイルに埋め込まれます。呼び出しが何千か所もあると実行ファイルが少し大きくなります。気になる場合は Release では引数を無視する別の関数に切り替えます。

## よくあるミス

??? failure "関数の中で current() を呼ぶ"
    呼び出し側ではなくその関数の中の位置になります。ログ関数の中で `std::source_location::current()` を直接書くといつも同じ行が出ます。引数の既定値に書きます。

??? failure "ラッパー関数が位置を渡していない"
    `Log` を呼ぶ別の関数（`Warn` など）を作ったとき `Warn` の中で `Log(msg)` と書くと、`Log` の既定値が評価されるのは `Warn` の中なので、いつも `Warn` の中の位置が出ます。`Warn` にも `source_location` の引数を持たせて、`Log(msg, loc)` と渡します。


    ```cpp
    #include <iostream>
    #include <source_location>
    #include <string_view>

    void Log(std::string_view msg, std::source_location loc = std::source_location::current()) {
      std::cout << loc.file_name() << ":" << loc.line() << " " << msg << std::endl;
    }

    // 悪い例: loc を渡していないので、Log の既定値が Warn の中の位置になる。
    void WarnBad(std::string_view msg) { Log(msg); }

    // 良い例: 受け取った loc をそのまま渡す。
    void Warn(std::string_view msg, std::source_location loc = std::source_location::current()) { Log(msg, loc); }

    int main() {
      WarnBad("悪い例");
      Warn("良い例");
    }
    ```

    ```text title="実行結果"
    src/chain.cpp:10 悪い例
    src/chain.cpp:17 良い例
    ```

??? failure "function_name() の文字列を解析して使う"
    `Player::Update` のように切り出そうとしても、GCC と Clang で形式が違うので、片方でしか動きません。表示だけに使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`__FILE__` / `__LINE__` / `__func__`](../../basics/predefined-macros.md) | マクロ。関数にはできないのでログ関数ごとマクロにする必要がある。書いた場所の位置が入る |
| [`std::stacktrace`](stacktrace.md) | 呼び出し履歴全体。`source_location` は呼び出しの 1 点だけ |

## コンパイラ対応

C++20 の機能です。GCC 11、Clang 16（libc++）、Visual Studio 2019 16.10 以降で使えます。バージョンは目安です。使えるかどうかは機能テスト マクロ `__cpp_lib_source_location` で調べられます（[定義済みマクロ](../../basics/predefined-macros.md#feature-test)）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 引数の既定値に `current()` を書くと呼び出し側の位置が取れる
    - [x] `file_name()` は渡したパスのまま `function_name()` はコンパイラ次第の長い形
    - [x] 文字列を解析せず画面やログに出すだけにする
    - [x] ラッパー関数では、`loc` を受け取ってそのまま渡す

## 関連ページ

- [定義済みマクロ](../../basics/predefined-macros.md)
- [`std::stacktrace`](stacktrace.md)
- [cpprefjp: std::source_location](https://cpprefjp.github.io/reference/source_location/source_location.html)
- [cppreference: std::source_location](https://en.cppreference.com/w/cpp/utility/source_location)
