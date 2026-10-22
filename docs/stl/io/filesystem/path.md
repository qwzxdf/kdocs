---
title: std::filesystem::path
summary: "ファイルやフォルダの場所（パス）を表す型。"
order: 1
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::path

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

`"C:\\Users\\player\\saves\\slot1.dat"` と文字列で書くと、Windows では `\` を二重に書く必要があり、Linux では `/` を使います。ファイル名だけを取り出す、拡張子を変える、パスをつなぐ、といった処理も、文字列の操作で書くと間違えやすくなります。`std::filesystem::path` は、パスを専用の型で表し、区切り文字の違いを吸収しながら、これらの操作を関数として提供します。

!!! tip "ポイント"
    - パスは `path` で持ち、`/` でつなぐ（`dir / "save.dat"`）。
    - `filename()` `extension()` `stem()` `parent_path()` で分解できる。
    - Windows で日本語のパスは、`u8string()` などを経由して扱う。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### path {#path}

```cpp
class path;
```

パスを表す型です。文字列から作れて、`/` でつなげられます。区切り文字（`/` と `\`）の違いを吸収してくれます。

| メンバ | 重要度 | 何をする | `"assets/img/player.png"` の例 |
| --- | --- | --- | --- |
| `operator/` | <span class="rank rank-must">必須</span> | パスをつなげる | `fs::path("assets") / "img"` |
| `filename()` | <span class="rank rank-must">必須</span> | ファイル名 | `player.png` |
| `extension()` | <span class="rank rank-must">必須</span> | 拡張子（`.` 付き） | `.png` |
| `stem()` | <span class="rank rank-often">よく使う</span> | 拡張子なしのファイル名 | `player` |
| `parent_path()` | <span class="rank rank-often">よく使う</span> | 親フォルダ | `assets/img` |
| `string()` | <span class="rank rank-often">よく使う</span> | `std::string` に変換（OS の区切り文字） | Windows なら `\` になることも |
| `generic_string()` | <span class="rank rank-often">よく使う</span> | `/` 区切りの `std::string` | `assets/img/player.png` |
| `replace_extension(".jpg")` | <span class="rank rank-sometimes">たまに</span> | 拡張子を変える | `assets/img/player.jpg` |
| `has_extension()` など `has_*` | <span class="rank rank-sometimes">たまに</span> | その部分があるか | `true` |
| `is_absolute()` / `is_relative()` | <span class="rank rank-sometimes">たまに</span> | 絶対パスか | `false` / `true` |
| `operator+=` | <span class="rank rank-sometimes">たまに</span> | 区切りを入れずに後ろに足す | `p += ".tmp"` |
| `lexically_normal()` | <span class="rank rank-rare">知ってるだけ</span> | `a/./b/../c` を `a/c` に整える | |
| `begin()` / `end()` | <span class="rank rank-rare">知ってるだけ</span> | 区切りごとに回す | `assets`, `img`, `player.png` |
| `u8string()` | <span class="rank rank-rare">知ってるだけ</span> | UTF-8 の文字列（`std::u8string`） | |
| `native()` | <span class="rank rank-rare">知ってるだけ</span> | OS 固有の文字列（Windows は `std::wstring`） | |

```cpp
#include <filesystem>
#include <print>

int main() {
  std::filesystem::path p = "saves";
  p /= "slot1";               // saves/slot1
  p += ".dat";                // saves/slot1.dat（区切りなしで足す）
  auto backup = p;
  backup.replace_extension(".bak");
  std::println("{} {}", p.generic_string(), backup.generic_string());
  std::println("{}", std::filesystem::path("a/./b/../c").lexically_normal().generic_string());
}
```

```text title="実行結果"
saves/slot1.dat saves/slot1.bak
a/c
```

!!! warning "Windows で日本語のパス"
    Windows では、日本語を含むパスを `string()` で取り出すと文字化けや例外になることがあります。表示用には `generic_u8string()` や、Visual Studio の `/utf-8` オプションを使います。ファイルを開くときは `path` をそのまま `std::ifstream` に渡せば問題ありません。

### operator= {#op_assign}

```cpp
path& operator=(const path& p);
path& operator=(path&& p) noexcept;
template <class Source> path& operator=(const Source& source);
```

- 計算量: O(長さ)

別の `path`、または文字列から代入します。

### assign {#assign}

```cpp
template <class Source>
path& assign(const Source& source);
```

- 計算量: O(長さ)

文字列などを代入します（`operator=` と同じ働き）。

### operator/= {#operator}

```cpp
path& operator/=(const path& p);
```

- 計算量: O(長さ)

区切り文字（`/`）をはさんで、後ろにつなげます。`p` が絶対パスなら、置き換わります。

### append {#append}

```cpp
template <class Source>
path& append(const Source& source);
```

- 計算量: O(長さ)

`operator/=` と同じ働きです。区切り文字をはさんで、後ろにつなげます。

### operator+= {#op_plus_assign}

```cpp
path& operator+=(const path& p);
path& operator+=(const string_type& str);
```

- 計算量: O(長さ)

区切り文字を入れずに、後ろに文字列を足します。`player` に `.png` を足すときなどに使います。

### concat {#concat}

```cpp
template <class Source>
path& concat(const Source& source);
```

- 計算量: O(長さ)

`operator+=` と同じ働きです。区切り文字を入れずに、後ろに足します。

### clear {#clear}

```cpp
void clear() noexcept;
```

- 計算量: 定数

パスを空にします。

### make_preferred {#make_preferred}

```cpp
path& make_preferred();
```

- 計算量: O(長さ)

区切り文字を、その OS の好みの区切り（Windows なら `\`）に変換します。

### remove_filename {#remove_filename}

```cpp
path& remove_filename();
```

- 計算量: O(長さ)

最後の要素（ファイル名）を取り除き、フォルダまでのパスにします。

### replace_filename {#replace_filename}

```cpp
path& replace_filename(const path& replacement);
```

- 計算量: O(長さ)

最後の要素（ファイル名）を、別のものに置き換えます。

### replace_extension {#replace_extension}

```cpp
path& replace_extension(const path& replacement = path());
```

- 計算量: O(長さ)

拡張子を置き換えます。空を渡すと、拡張子を取り除きます。`.` は自動で補われます。

### swap {#swap}

```cpp
void swap(path& other) noexcept;
```

- 計算量: 定数

2 つの `path` を入れ替えます。

### native {#native}

```cpp
const string_type& native() const noexcept;
```

- 計算量: 定数

OS 固有の形式の文字列への参照。Windows では `std::wstring`、Linux では `std::string` です。OS の API に渡すときに使います。

### c_str {#c_str}

```cpp
const value_type* c_str() const noexcept;
```

- 計算量: 定数

OS 固有の形式の、終端つきの C 文字列。Windows では `const wchar_t*` です。

### string {#string}

```cpp
std::string string() const;
```

- 計算量: O(長さ)

`std::string` に変換します。Windows では、実行時の文字コード（多くは ANSI）への変換が入るので、日本語の扱いに注意が必要です。

### wstring {#wstring}

```cpp
std::wstring wstring() const;
```

- 計算量: O(長さ)

`std::wstring` に変換します。Windows API に渡すときに便利です。

### u8string {#u8string}

```cpp
std::u8string u8string() const;
```

- 計算量: O(長さ)

UTF-8 の文字列に変換します（C++20 では `char8_t` の `u8string`）。文字コードを UTF-8 に統一するなら、これを使います。

### generic_string {#generic_string}

```cpp
std::string generic_string() const;
```

- 計算量: O(長さ)

区切りを `/` にした、`std::string`（OS を問わず同じ形）。ログに出す、ファイルに保存する、といったときに使います。

### compare {#compare}

```cpp
int compare(const path& p) const noexcept;
```

- 計算量: O(長さ)

要素ごとに比べて、小さければ負、等しければ 0、大きければ正を返します。

### lexically_normal {#lexically_normal}

```cpp
path lexically_normal() const;
```

- 計算量: O(長さ)

`.` や `..` を取り除き、区切りを整えます。ファイルシステムは調べず、文字列だけで処理します。

### lexically_relative {#lexically_relative}

```cpp
path lexically_relative(const path& base) const;
```

- 計算量: O(長さ)

`base` から見た相対パスを、文字列だけで求めます。ファイルシステムは調べません。

### lexically_proximate {#lexically_proximate}

```cpp
path lexically_proximate(const path& base) const;
```

- 計算量: O(長さ)

`lexically_relative` と同じですが、作れないときは元のパスを返します。

### root_name {#root_name}

```cpp
path root_name() const;
```

- 計算量: O(長さ)

ルートの名前（Windows のドライブ名 `C:` など）。

### root_directory {#root_directory}

```cpp
path root_directory() const;
```

- 計算量: O(長さ)

ルートのフォルダ（`/`）。

### root_path {#root_path}

```cpp
path root_path() const;
```

- 計算量: O(長さ)

ルート名とルートフォルダを合わせたもの（`C:/`）。

### relative_path {#relative_path}

```cpp
path relative_path() const;
```

- 計算量: O(長さ)

ルートを除いた残りのパス。

### parent_path {#parent_path}

```cpp
path parent_path() const;
```

- 計算量: O(長さ)

親フォルダのパス（最後の要素を除いたもの）。

### filename {#filename}

```cpp
path filename() const;
```

- 計算量: O(長さ)

最後の要素（ファイル名）。`assets/img/player.png` なら `player.png`。

### stem {#stem}

```cpp
path stem() const;
```

- 計算量: O(長さ)

拡張子を除いたファイル名。`player.png` なら `player`。

### extension {#extension}

```cpp
path extension() const;
```

- 計算量: O(長さ)

拡張子（`.` を含む）。`player.png` なら `.png`。拡張子がなければ空。

### empty {#empty}

```cpp
[[nodiscard]] bool empty() const noexcept;
```

- 計算量: 定数

パスが空なら `true`。

### has_root_name {#has_root_name}

```cpp
bool has_root_name() const;
```

- 計算量: O(長さ)

ルート名（ドライブ名）があれば `true`。

### has_root_directory {#has_root_directory}

```cpp
bool has_root_directory() const;
```

- 計算量: O(長さ)

ルートフォルダ（先頭の `/`）があれば `true`。

### has_root_path {#has_root_path}

```cpp
bool has_root_path() const;
```

- 計算量: O(長さ)

ルートがあれば `true`。

### has_relative_path {#has_relative_path}

```cpp
bool has_relative_path() const;
```

- 計算量: O(長さ)

ルート以降の部分があれば `true`。

### has_parent_path {#has_parent_path}

```cpp
bool has_parent_path() const;
```

- 計算量: O(長さ)

親フォルダのパスがあれば `true`。

### has_filename {#has_filename}

```cpp
bool has_filename() const;
```

- 計算量: O(長さ)

ファイル名があれば `true`。末尾が `/` だと `false`。

### has_stem {#has_stem}

```cpp
bool has_stem() const;
```

- 計算量: O(長さ)

拡張子を除いたファイル名があれば `true`。

### has_extension {#has_extension}

```cpp
bool has_extension() const;
```

- 計算量: O(長さ)

拡張子があれば `true`。

### is_absolute {#is_absolute}

```cpp
bool is_absolute() const;
```

- 計算量: O(長さ)

絶対パスなら `true`。Windows では、ドライブ名とルートの両方が必要です（`/a` は絶対パスではありません）。

### is_relative {#is_relative}

```cpp
bool is_relative() const;
```

- 計算量: O(長さ)

相対パスなら `true`（`is_absolute()` の逆）。

### begin {#begin}

```cpp
iterator begin() const;
```

- 計算量: 定数

パスの要素（区切りごとの部分）の先頭。`for (auto& part : p)` でフォルダ名を順に取り出せます。

### end {#end}

```cpp
iterator end() const;
```

- 計算量: 定数

パスの要素の終端。

### operator== {#op_eq}

```cpp
bool operator==(const path& lhs, const path& rhs) noexcept;
```

- 計算量: O(長さ)

パスが等しければ `true`。文字列の比較で、`a/b` と `a//b` は等しいと見なされますが、ファイルシステム上の同一性は調べません（それは `equivalent`）。

### operator<=> <span class="ver ver-20">C++20</span> {#op_cmp data-toc-label="operator<=>"}

```cpp
std::strong_ordering operator<=>(const path& lhs, const path& rhs) noexcept;
```

- 計算量: O(長さ)

パスを、要素ごとに比べる三方比較。

## ゲームでの使いどころ

アセットのパスを組み立てる場面で使います。`fs::path dir = "assets"; fs::path file = dir / "textures" / "player.png";` と、`/` 演算子でつなげると、OS に合った区切りで連結されます。

拡張子を見て読み込み方を切り替える処理にも使います。`file.extension() == ".png"` で画像、`".json"` で設定、などの分岐です。`replace_extension(".dds")` で、同じ名前の別の形式のファイルを指せます。

セーブデータの置き場所は、`fs::path` のまま持っておきます。文字列に変換するのは、外部のライブラリに渡す直前だけにします。Windows では、`path` の中身は UTF-16 の `wchar_t` なので、`string()` で変換すると文字化けすることがあります。`u8string()` か、`generic_string()` を使います。

## よくあるミス

??? failure "文字列と `path` を `+` でつなぐ"
    `path + "x"` は文字列の連結ではなく、`path` の末尾に文字が足されるだけです。パスの区切りを入れてつなぐのは `/` 演算子です。`+=` は区切りなしの連結、`/=` は区切りありの連結です。

??? failure "日本語のパスを `string()` で受ける"
    Windows では、`path::string()` は現在のコードページ（日本語環境なら Shift_JIS）に変換します。UTF-8 で扱いたいなら `u8string()` を使います。変換できない文字があると、例外を投げることもあります。

??? failure "`/` の右側に絶対パスを渡す"
    `fs::path("assets") / "/etc/hosts"` は、左側を捨てて `/etc/hosts` になります。右側が絶対パスのときは、左側が無視される仕様です。ユーザー入力のパスをつなぐときは、絶対パスでないかを確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::string`](../../containers/string.md) | パスは `path` で持つ |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] パスは `path` で持つ
    - [x] `/` でつなぐ
    - [x] Windows の日本語に注意

## 関連ページ

- [cpprefjp: std::filesystem::path](https://cpprefjp.github.io/reference/filesystem/path.html)
- [cppreference: std::filesystem::path](https://en.cppreference.com/w/cpp/filesystem/path)
