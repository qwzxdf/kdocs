---
title: 定義済みマクロ（__FILE__ など）
tags:
  - 基礎
---

# 定義済みマクロ（__FILE__ など）

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
</div>

ログに「どのファイルの何行目か」を出したい `assert` が失敗したときに式をそのまま表示したい、Debug のときだけ処理を足したい。こういうとき C++ では**コンパイラがあらかじめ用意しているマクロ**を使います。ファイル名の `__FILE__`、行番号の `__LINE__`、関数名の `__func__` などです。

マクロはプリプロセッサがコンパイルの前に文字列として置き換えます。そのため、書いた場所の情報を取れる一方で、置き換えの落とし穴もあります。C++20 以降は場所の情報を取るだけなら [`std::source_location`](../stl/support/source_location.md) を使うほうが安全です。それでも `#expr` のような式の文字列化や条件付きコンパイルはマクロでしかできません。

!!! tip "ポイント"
    - 場所を取るのは `__FILE__`、`__LINE__`、`__func__`。ログとアサートの定番。
    - 文字列にするには `#`。2 段のマクロ（`STR(__LINE__)`）を経由しないと行番号の数字にならない。
    - `__DATE__` と `__TIME__` はビルドのたびに結果が変わる。再現できるビルドには向かない。
    - コンパイラや OS を分けるときは `_MSC_VER`、`__clang__`、`_WIN64` などを使う。
    - 新しい機能が使えるかは `__cplusplus` ではなく `__cpp_lib_xxx` などの機能テスト マクロで調べる。

!!! info "このページを読む前に"
    プリプロセッサとマクロの基本は [コンパイラとビルドの仕組み](compiler.md) と [プリプロセッサマクロ](../vs/preprocessor.md)（Visual Studio での定義のしかた）にあります。このページはすでに定義されているマクロの使い方を扱います。

## 場所を取るマクロ

### `__FILE__` {#file}

今のソース ファイルの名前が文字列リテラルとして入ります。**どんな形の名前になるかはコンパイラに渡したパス次第**です。次のように `src/main.cpp` をそのまま渡したときは、`"src/main.cpp"` になります。

```text
g++ src/main.cpp         →  "src/main.cpp"
g++ C:/kdemo/game/src/main.cpp   →  "C:/kdemo/game/src/main.cpp"
```

Visual Studio でビルドすると、ふつうは絶対パス（`C:\Users\...\main.cpp`）が渡されます。そのため、ログに出すと長くなります。しかもリリースしたゲームの実行ファイルに自分の PC のフォルダ名（ユーザー名を含む）が文字列として残ります。見られて困る場合は `/d1trimfile:`（MSVC）や `-ffile-prefix-map=`（GCC / Clang）で、パスの前半を削ります。

`__FILE__` はファイルごとに文字列が実行ファイルに埋め込まれます。ただし、同じ文字列は 1 つにまとめられるので、ログ マクロを何百か所で使っても、ファイル名の分しか増えません。

### `__LINE__` {#line}

今の行番号が整数のリテラルとして入ります。`#line 100` と書くとそこから数え直せます（自動生成コードで使われます）。

注意が必要なのはマクロの**中**で使ったときです。マクロは呼び出した場所に展開されるので、`__LINE__` も呼び出した行の番号になります。これがログ マクロを作る理由です。

```cpp
#include <iostream>

// 呼び出した行のファイル名と行番号が出る。
#define LOG(msg) std::cout << __FILE__ << ":" << __LINE__ << " " << msg << std::endl

int main() {
  LOG("開始");
}
```

```text title="実行結果"
src/macros.cpp:28 開始
```

### `__func__` {#func}

今の関数の名前が入ります。C++11 の規格にあり関数の中でだけ使えます。マクロではなく各関数の中で自動的に宣言される `static const char[]` の変数です。そのため、`#ifdef __func__` では調べられません。

```cpp
void Func() {
  std::cout << "__func__ = " << __func__ << std::endl;
}
```

```text title="実行結果"
__func__ = Func
```

名前空間やクラス名は付きません。`Player::Update` の中でも `Update` だけです。

### `__FUNCTION__`、`__PRETTY_FUNCTION__`、`__FUNCSIG__` {#function-names}

`__func__` より詳しい関数名を取りたいときコンパイラが独自のものを用意しています。

| 名前 | 使えるコンパイラ | 例（`void Func()` の中） |
| --- | --- | --- |
| `__FUNCTION__` | MSVC、GCC、Clang | `Func` |
| `__PRETTY_FUNCTION__` | GCC、Clang | `void Func()` |
| `__FUNCSIG__` | MSVC | `void __cdecl Func(void)` |

`__PRETTY_FUNCTION__` と `__FUNCSIG__` は戻り値の型、引数の型、テンプレート引数まで含みます。テンプレート関数の中で使うと `T` が何だったかまで分かるので、デバッグでは便利です。

```cpp
#if defined(__GNUC__) || defined(__clang__)
  std::cout << "__PRETTY_FUNCTION__ = " << __PRETTY_FUNCTION__ << std::endl;
#endif
```

```text title="実行結果（GCC / Clang）"
__PRETTY_FUNCTION__ = void Func()
```

コンパイラごとに書き方が違うので、移植性が必要なコードでは `std::source_location::function_name()` を使います。ただし、その結果の形式もコンパイラごとに違います（[`std::source_location`](../stl/support/source_location.md) に実際の文字列を並べています）。

### `__FILE_NAME__` {#file-name}

ディレクトリを除いたファイル名だけが入ります。GCC（12 以降）と Clang で使えます。`__FILE__` の長いパスの代わりにログに出したいときに便利です。

```text title="実行結果（GCC / Clang）"
__FILE_NAME__ = macros.cpp
```

MSVC では手元で確認できていません。使えない環境も想定するなら `std::filesystem::path(__FILE__).filename()` で、実行時に取り出します。

## 式を文字列にする

### `#`（文字列化） {#stringize}

マクロの引数の前に `#` を付けると、引数がそのまま文字列リテラルになります。`assert` が失敗した式を表示できるのは、この仕組みです。

```cpp
#define CHECK(cond) \
  do { if (!(cond)) std::cout << "CHECK 失敗: " #cond " (" << __FILE__ << ":" << __LINE__ << ")" << std::endl; } while (0)

int hp = 0;
CHECK(hp > 0);
```

```text title="実行結果"
CHECK 失敗: hp > 0 (src/macros.cpp:30)
```

`#cond` は書いたとおりの文字列（`hp > 0`）になります。コードの意味ではなく見た目の文字列です。値が何だったかは分からないので、必要なら値も別に出力します。

### 数字を文字列にする罠 {#stringize-trap}

`__LINE__` のような別のマクロの結果を文字列にしたいときは、`#` を 2 段にしなければなりません。1 段だと展開される前の `__LINE__` という文字がそのまま文字列になります。

```cpp
#define STR_(x) #x
#define STR(x) STR_(x)

std::cout << STR(__LINE__) << ", " << STR(1 + 2) << std::endl;
```

```text title="実行結果"
34, 1 + 2
```

`STR_(__LINE__)` と書くと `"__LINE__"` になってしまいます。外側の `STR` が先に `__LINE__` を `34` に展開してから、`STR_` に渡すという流れです。

### `##`（連結）と `__COUNTER__` {#paste}

`##` は 2 つの文字を 1 つの名前につなげます。`__COUNTER__` は使うたびに 0、1、2…と増える数字です。この 2 つを組み合わせると、マクロの中で重ならない変数名を作れます。

```cpp
#define CAT_(a, b) a##b
#define CAT(a, b) CAT_(a, b)
#define GUARD(name) Guard CAT(guard_, __COUNTER__){name}

GUARD("A");  // Guard guard_0{"A"};
GUARD("B");  // Guard guard_1{"B"};
```

```text title="実行結果"
終了: B
終了: A
```

`__COUNTER__` は規格にはありませんが MSVC、GCC、Clang のどれでも使えます。1 つのソース ファイル（翻訳単位）の中で数えるので、別のファイルではまた 0 から始まります。`CAT` を 2 段にしているのは、`STR` と同じ理由です。

## 可変個の引数を渡す

### `__VA_ARGS__` と `__VA_OPT__` {#va-args}

マクロの引数の数を決めずに受け取りたいときは、パラメーターの最後に `...` と書いて、中で `__VA_ARGS__` と書きます。引数が 0 個のときは直前のカンマが余って、構文エラーになります。C++20 の `__VA_OPT__(,)` を使うと引数があるときだけカンマが入ります。

```cpp
#define LOGF(fmt, ...) std::printf("%s:%d " fmt "\n", __FILE__, __LINE__ __VA_OPT__(,) __VA_ARGS__)

LOGF("開始");
LOGF("HP は %d です", 42);
```

```text title="実行結果"
src/va.cpp:6 開始
src/va.cpp:7 HP は 42 です
```

書式文字列を `fmt` を連結する形（`"%s:%d " fmt`）で受け取るので、`fmt` には文字列リテラルを直接書く必要があります。`std::format` と組み合わせたいならマクロより `std::source_location` を使った関数のほうが扱いやすくなります。

## ビルドの情報

### `__DATE__`、`__TIME__`、`__TIMESTAMP__` {#date-time}

コンパイルした日付と時刻が文字列として入ります。

```text title="実行結果"
__DATE__ = Oct 21 2026
__TIME__ = 22:48:25
```

形式は `__DATE__` が `Mmm dd yyyy`（日が 1 桁のときは、先頭が空白）、`__TIME__` が `hh:mm:ss` です。タイトル画面にビルドの日付を出すのに便利です。

ただし、**ビルドのたびに実行ファイルの中身が変わります**。同じソースから同じ実行ファイルを作る（再現可能なビルド）ことができなくなり、差分の確認やキャッシュも効きにくくなります。ビルドの識別が欲しいときは Git のコミット ハッシュなどをビルド時に `/D` や `-D` で渡すほうが向いています。

### `__cplusplus` {#cplusplus}

使っている C++ の規格の版が数字で入ります。C++20 なら `202002L`、C++23 なら `202302L` です。

```text title="実行結果（GCC / Clang、-std=c++23）"
__cplusplus = 202302
```

**MSVC は例外**です。既定ではどの規格を指定しても `199711L` のままです（昔のコードを壊さないため）。本当の値を出すには `/Zc:__cplusplus` を付けます。MSVC では代わりに `_MSVC_LANG` を見ます。

新しい機能が使えるかを調べるなら版の数字ではなく、次の機能テスト マクロを使うほうが確実です。

### 機能テスト マクロ（`__cpp_lib_xxx`、`__has_include`） {#feature-test}

機能ごとに「その機能に対応した版の数字」を持つマクロがあります。`<version>` を `#include` すると標準ライブラリ側のもの（`__cpp_lib_xxx`）がまとめて定義されます。

```cpp
#include <version>

#if __has_include(<format>)
  // <format> というヘッダがある
#endif
#ifdef __cpp_lib_format
  std::cout << "__cpp_lib_format = " << __cpp_lib_format << std::endl;
#endif
```

```text title="実行結果（GCC 14 / Clang 21）"
<format> がある
__cpp_lib_format = 202110   （GCC）
__cpp_lib_format = 202304   （Clang。Windows、MSVC の標準ライブラリ）
```

`std::format` が使えるという点は同じですが、数字が違います。数字は対応している規格の変更が決まった年月（`yyyymm`）で、新しいほどあとから規格に入った修正まで含みます。`__cpp_lib_format` の場合、202304 はポインターを書式化できる変更（P2510）まで入っている印です。ある機能が必要かどうかは `#if __cpp_lib_format >= 202304` のように数字で比べられます。

`__has_include(<ヘッダ>)` はそのヘッダが存在するかどうかを調べます。ライブラリがインストールされているときだけ機能を有効にする、という使い方ができます。

## 環境を調べるマクロ

### コンパイラ、OS、CPU、ビルド構成 {#environment}

コンパイラや OS ごとに書き方を変えたいときは、次のマクロで分けます。

| 調べたいこと | マクロ | 補足 |
| --- | --- | --- |
| MSVC | `_MSC_VER` | VS 2026 は 1950 台。Clang の clang-cl も定義する |
| Clang | `__clang__` | `__clang_major__` でメジャー バージョン |
| GCC | `__GNUC__` | Clang も（Linux では）定義することがある |
| Windows | `_WIN32` | 64 ビットでも定義される |
| 64 ビット Windows | `_WIN64` | |
| Linux | `__linux__` | |
| macOS | `__APPLE__` | |
| x64 の CPU | `_M_X64`（MSVC）、`__x86_64__`（GCC / Clang） | |
| Release ビルド | `NDEBUG` | `assert` を無効にする |
| Debug ビルド | `_DEBUG` | Visual Studio の Debug 構成で定義される |

`NDEBUG` と `_DEBUG` はどちらもビルドの設定で決まります。Visual Studio の Release 構成は `NDEBUG` を Debug 構成は `_DEBUG` を定義します。GCC や Clang は何も指定しなければ、どちらも定義しません。Release にしたいときは `-DNDEBUG` を付けます。

```text title="実行結果（g++ -O2 -DNDEBUG）"
NDEBUG 定義あり
```

注意したいのは `__GNUC__` が GCC だけを意味しないことです。Linux 上の Clang は GCC 互換のために `__GNUC__` を定義します。コンパイラを見分けるときは `__clang__` を先に調べてから、`__GNUC__` を調べます。上の実行結果の Clang は Windows の MSVC 互換モードなので、`__GNUC__` を定義していませんでした。

## よくあるミス

??? failure "`STR(__LINE__)` ではなく `STR_(__LINE__)` を使う"
    1 段のマクロ（`#x`）に別のマクロを渡すと展開される前の名前がそのまま文字列になります。`"__LINE__"` と表示されます。2 段にします。

??? failure "ログに長い絶対パスが並ぶ"
    Visual Studio は、ソースを絶対パスでコンパイラに渡します。`__FILE__` をそのままログに出すと長くなります。`std::filesystem::path(__FILE__).filename()` か `__FILE_NAME__`（GCC / Clang）で、ファイル名だけにします。

??? failure "リリースの実行ファイルに自分のフォルダ名が残る"
    `__FILE__` の文字列は実行ファイルに入ります。ユーザー名を含むパスだとプライバシーの問題になります。`/d1trimfile:`（MSVC）、`-ffile-prefix-map=`（GCC / Clang）で、前半を取り除きます。

??? failure "MSVC で `__cplusplus` が 199711 になる"
    `/Zc:__cplusplus` を付けていません。MSVC は既定では古い値を返します。`_MSVC_LANG` を見るかオプションを付けます。

??? failure "`__DATE__` を使って、毎回ビルドが変わる"
    ビルドのたびに実行ファイルが変わるので、差分の確認やビルドのキャッシュが効きません。ビルド番号やコミット ハッシュを `/D` で渡します。

## 関連ページ

- [`std::source_location`](../stl/support/source_location.md)
- [プリプロセッサマクロ](../vs/preprocessor.md)
- [コンパイラとビルドの仕組み](compiler.md)
- [cpprefjp: 定義済みマクロ](https://cpprefjp.github.io/lang/cpp11/predefined_macros.html)
- [cppreference: Predefined macros](https://en.cppreference.com/w/cpp/preprocessor/replace)
