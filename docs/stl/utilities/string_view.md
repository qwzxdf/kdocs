---
title: std::string_view
summary: "文字列をコピーせずに「借りて」見る。引数で文字列を受け取るときの定番。"
order: 53
tags:
  - ユーティリティ
  - 文字列
---

# std::string_view

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="perf perf-4">◎ 速い</span>
<span class="ver ver-17">C++17</span>
`#include <string_view>`
</div>

`std::string_view` は、**どこかにある文字列を「借りて見る」ための型**です。自分では文字列を持たず、「先頭のポインタ」と「長さ」だけを持っています。`std::string` でも `"文字列リテラル"` でも `char` 配列でも、コピーせずに同じ型で受け取れるので、**読むだけの関数の引数**にぴったりです。文字列版の [`std::span`](../containers/span.md) だと考えると分かりやすいです。

!!! tip "ポイント"
    - <strong>文字列を読むだけの関数の引数は `std::string_view` にする。</strong> `const std::string&` より何でも受け取れて、コピーも起きない。
    - 値渡しで OK（16 バイトしかない）。
    - **借りているだけ**なので、メンバ変数に保存したり、関数から返したりしない（元の文字列が消えると壊れる）。
    - **末尾に `'\0'` があるとは限らない**ので、C の関数（`printf("%s")` など）にそのまま渡せない。

!!! info "このページを読む前に"
    [`std::string`](../containers/string.md) を先に読んでください。関数の多くは string と同じです。

## 宣言

```cpp
template <class CharT, class Traits = std::char_traits<CharT>>
class basic_string_view;

using string_view = basic_string_view<char>;
```

### 作り方

| 書き方 | 重要度 | 意味 |
| --- | --- | --- |
| 関数の引数に string / `"..."` を渡す | <span class="rank rank-must">必須</span> | 自動で string_view になる |
| `std::string_view sv = "hello";` | <span class="rank rank-often">よく使う</span> | リテラルを見る（リテラルはずっと残るので安全） |
| `using namespace std::literals; auto sv = "hello"sv;` | <span class="rank rank-sometimes">たまに</span> | string_view リテラル |
| `std::string_view sv(ptr, len);` | <span class="rank rank-sometimes">たまに</span> | ポインタと長さから |

## 関数一覧

[`std::string`](../containers/string.md) と同じ名前の関数は同じ意味です。

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`size`](#size) | <span class="rank rank-must">必須</span> | 長さ（バイト数） | O(1) |
| [`operator==`](#eq) | <span class="rank rank-must">必須</span> | 等しいか | O(n) |
| [`substr`](#substr) | <span class="rank rank-often">よく使う</span> | 一部を切り出す（**コピーしない**） | O(1) |
| [`find`](#find) | <span class="rank rank-often">よく使う</span> | 部分文字列を探す | O(n·m) |
| [`starts_with`](#starts_with) | <span class="rank rank-often">よく使う</span> | 先頭が一致するか <span class="ver ver-20">C++20</span> | O(m) |
| [`ends_with`](#ends_with) | <span class="rank rank-often">よく使う</span> | 末尾が一致するか <span class="ver ver-20">C++20</span> | O(m) |
| [`empty`](#empty) | <span class="rank rank-often">よく使う</span> | 空か | O(1) |
| [`remove_prefix`](#remove_prefix) | <span class="rank rank-often">よく使う</span> | 先頭 n 文字を見ないようにする | O(1) |
| [`remove_suffix`](#remove_suffix) | <span class="rank rank-sometimes">たまに</span> | 末尾 n 文字を見ないようにする | O(1) |
| [`contains`](#contains) | <span class="rank rank-sometimes">たまに</span> | 含んでいるか <span class="ver ver-23">C++23</span> | O(n·m) |
| [`operator[]`](#operator) | <span class="rank rank-sometimes">たまに</span> | i 番目の文字 | O(1) |
| [`data`](#data) | <span class="rank rank-sometimes">たまに</span> | 先頭のポインタ（`'\0'` 終端とは限らない） | O(1) |
| [`rfind`](#rfind) | <span class="rank rank-sometimes">たまに</span> | 後ろから探す | O(n·m) |
| [`find_first_of`](#find_first_of) | <span class="rank rank-rare">知ってるだけ</span> | 指定した文字のどれかを探す | O(n·m) |
| [`find_first_not_of`](#find_first_not_of) | <span class="rank rank-rare">知ってるだけ</span> | 指定した文字以外を探す | O(n·m) |
| [`front`](#front) | <span class="rank rank-rare">知ってるだけ</span> | 先頭の文字 | O(1) |
| [`back`](#back) | <span class="rank rank-rare">知ってるだけ</span> | 末尾の文字 | O(1) |
| [`copy`](#copy) | <span class="rank rank-rare">知ってるだけ</span> | char 配列にコピー | O(m) |

## よくある使い方

### 1. 読むだけの関数の引数

```cpp
#include <print>
#include <string>
#include <string_view>

// string でもリテラルでも、コピーなしで受け取れる
bool IsImageFile(std::string_view path) {
  return path.ends_with(".png") || path.ends_with(".jpg");
}

int main() {
  std::string a = "player.png";
  std::println("{} {}", IsImageFile(a), IsImageFile("bgm.ogg"));
}
```

```text title="実行結果"
true false
```

### 2. コピーせずに分解する

```cpp
#include <print>
#include <string_view>

int main() {
  std::string_view line = "hp=120";
  std::size_t eq = line.find('=');
  std::string_view key = line.substr(0, eq);       // コピーしない
  std::string_view value = line.substr(eq + 1);
  std::println("[{}] [{}]", key, value);
}
```

```text title="実行結果"
[hp] [120]
```

## 関数の詳しい説明

### size {#size}

```cpp
constexpr size_type size() const noexcept;
```

- 長さ（バイト数）。`length()` も同じ

### operator== {#eq}

```cpp
constexpr bool operator==(basic_string_view lhs, basic_string_view rhs) noexcept;
```

- 中身が同じなら `true`。string や `"..."` とも比べられます。`<`, `>` なども使えます

```cpp
#include <print>
#include <string>
#include <string_view>

int main() {
  std::string cmd = "jump";
  std::string_view sv = cmd;
  std::println("{} {} {}", sv == "jump", sv.size(), sv < "run");
}
```

```text title="実行結果"
true 4 true
```

### substr {#substr}

```cpp
constexpr basic_string_view substr(size_type pos = 0, size_type count = npos) const;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pos` | `size_type` | 開始位置 |
| `count` | `size_type` | 長さ。省略すると最後まで |

- 戻り値: 同じ文字列の一部を指す新しい string_view。**コピーは起きない**（string の substr との大きな違い）
- 例外: `pos > size()` なら `std::out_of_range`

<div class="anim" data-label="sv.substr(1, 2)">
a b c d # 元の文字列
a *b *c d # 見る範囲だけを返す。コピーはしない
</div>

### find {#find}

```cpp
constexpr size_type find(basic_string_view v, size_type pos = 0) const noexcept;
constexpr size_type find(CharT ch, size_type pos = 0) const noexcept;
```

- 見つかった位置。見つからなければ `std::string_view::npos`

<div class="anim" data-label="sv.find(&quot;bc&quot;)">
a b c d # 元の文字列
a *b *c d # 見つかった位置（1）を返す
</div>

### starts_with <span class="ver ver-20">C++20</span> {#starts_with data-toc-label="starts_with"}

```cpp
constexpr bool starts_with(basic_string_view sv) const noexcept;
```

- 先頭が一致すれば `true`

<div class="anim" data-label="sv.starts_with(&quot;ab&quot;)">
a b c d # 元の文字列
*a *b c d # 先頭が一致すれば true
</div>

### ends_with <span class="ver ver-20">C++20</span> {#ends_with data-toc-label="ends_with"}

```cpp
constexpr bool ends_with(basic_string_view sv) const noexcept;
```

- 末尾が一致すれば `true`

<div class="anim" data-label="sv.ends_with(&quot;cd&quot;)">
a b c d # 元の文字列
a b *c *d # 末尾が一致すれば true
</div>

```cpp
#include <print>
#include <string_view>

int main() {
  std::string_view s = "debug_player.png";
  std::println("{} {} {}", s.find("player"), s.starts_with("debug_"), s.ends_with(".png"));
}
```

```text title="実行結果"
6 true true
```

### empty {#empty}

```cpp
constexpr bool empty() const noexcept;
```

- 長さが 0 なら `true`

### remove_prefix {#remove_prefix}

```cpp
constexpr void remove_prefix(size_type n);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `n` | `size_type` | 先頭から何文字ぶん見る位置を進めるか（`n <= size()`） |

- **元の文字列は変わらない**。「見ている窓」を縮めるだけです

<div class="anim" data-label="sv.remove_prefix(1)">
*a *b *c *d # 元の文字列を全部見ている
a *b *c *d # 見る範囲の先頭だけが進む。元の文字列は変わらない
</div>

### remove_suffix {#remove_suffix}

```cpp
constexpr void remove_suffix(size_type n);
```

- 末尾 n 文字を見ないようにします

<div class="anim" data-label="sv.remove_suffix(1)">
*a *b *c *d # 元の文字列を全部見ている
*a *b *c d # 見る範囲の後ろだけが縮む。元の文字列は変わらない
</div>

```cpp
#include <print>
#include <string_view>

int main() {
  std::string_view s = "  [title]  ";
  while (!s.empty() && s.front() == ' ') {
    s.remove_prefix(1);
  }
  while (!s.empty() && s.back() == ' ') {
    s.remove_suffix(1);
  }
  s.remove_prefix(1);  // [ を外す
  s.remove_suffix(1);  // ] を外す
  std::println("[{}]", s);
}
```

```text title="実行結果"
[title]
```

!!! note "実際は"
    コピーせずに前後を削れるので、テキストの解析（パーサー）を書くときにとても便利です。

### contains <span class="ver ver-23">C++23</span> {#contains data-toc-label="contains"}

```cpp
constexpr bool contains(basic_string_view sv) const noexcept;
```

- どこかに含んでいれば `true`

### operator[] {#operator}

```cpp
constexpr const_reference operator[](size_type pos) const;
```

- `pos` 番目の文字（書き換えはできない）。範囲外は未定義動作

### data {#data}

```cpp
constexpr const_pointer data() const noexcept;
```

- 先頭のポインタ。**末尾に `'\0'` があるとは限らない**ので、`printf("%s", sv.data())` のように C の関数に渡すと、後ろのゴミまで読んでしまうことがあります

```cpp
#include <cstdio>
#include <string_view>

int main() {
  std::string_view s = "player.png";
  std::string_view name = s.substr(0, 6);
  // %.*s なら長さを指定できるので安全
  std::printf("%.*s\n", static_cast<int>(name.size()), name.data());
}
```

```text title="実行結果"
player
```

### rfind {#rfind}

```cpp
constexpr size_type rfind(basic_string_view v, size_type pos = npos) const noexcept;
```

- 後ろから探して、最後に見つかった位置を返します

### find_first_of {#find_first_of}

```cpp
constexpr size_type find_first_of(basic_string_view chars, size_type pos = 0) const noexcept;
```

- `chars` のどれか 1 文字が最初に出てくる位置

### find_first_not_of {#find_first_not_of}

```cpp
constexpr size_type find_first_not_of(basic_string_view chars, size_type pos = 0) const noexcept;
```

- `chars` に含まれない文字が最初に出てくる位置。`find_last_of` / `find_last_not_of` もあります

```cpp
#include <print>
#include <string_view>

int main() {
  std::string_view path = "a/b\\c.txt";
  std::println("{} {} {}", path.rfind('/'), path.find_first_of("/\\"),
               std::string_view("   x").find_first_not_of(' '));
}
```

```text title="実行結果"
1 1 3
```

### front {#front}

```cpp
constexpr const_reference front() const;
```

- 先頭の文字。空のとき未定義動作

### back {#back}

```cpp
constexpr const_reference back() const;
```

- 末尾の文字。空のとき未定義動作

### copy {#copy}

```cpp
constexpr size_type copy(CharT* dest, size_type count, size_type pos = 0) const;
```

- char 配列にコピーします。`'\0'` は付きません

## フラグ・オプション

| 値 | 意味 |
| --- | --- |
| `std::string_view::npos` | 「見つからない」「最後まで」 |
| `sv` リテラル（`"abc"sv`） | `using namespace std::literals;` で使える string_view リテラル |

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    void Print(const std::string& s);  // "abc" を渡すと一時的な string が作られる
    void Print(const char* s);         // 長さが分からない
    ```

=== "今の書き方（C++17）"

    ```cpp
    void Print(std::string_view s);
    ```

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| 読むだけの関数の引数 | ログ出力、ファイルパスの判定、キーの比較 |
| テキストの解析 | 設定ファイル・スクリプトをコピーせずに分解 |
| 定数の表 | `constexpr std::string_view kNames[] = {"火", "水", "風"};` |
| map の検索 | `std::map<std::string, T, std::less<>>` を string_view で検索 |

## パフォーマンス

- ポインタ + 長さの 16 バイトだけなので、**値渡しが一番速い**です。
- `substr` や `remove_prefix` はコピーしないので、string の同名関数よりずっと速いです。

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| 元の string が消えた・変更されたあとに使う | 未定義動作 |
| 一時的な string から string_view を作って保存する | 未定義動作 |
| `data()` を `'\0'` 終端の文字列として C の関数に渡す | 範囲外を読むことがある |

## よくあるミス

??? failure "一時的な string を string_view で受ける"
    ```cpp
    std::string_view name = GetName();  // GetName() が返した string はこの行で消える
    std::println("{}", name);            // 未定義動作

    std::string name2 = GetName();  // OK: 保存したいなら string で持つ
    ```

??? failure "string_view を返す関数でローカルの string を返す"
    ```cpp
    std::string_view MakeTitle(int level) {
      std::string s = std::format("Lv.{}", level);
      return s;  // s は関数を抜けると消える
    }
    ```

??? failure "メンバ変数に保存する"
    クラスのメンバに string_view を持つと、元の文字列の寿命を管理しなければならず、とても壊れやすくなります。保存するなら `std::string` にします。

## 類似クラス

| 名前 | 違い | こっちを使うとき |
| --- | --- | --- |
| [`std::string`](../containers/string.md) | 文字列を持つ（所有） | 保存する、書き換える |
| `const std::string&` | string しか受け取れない | string の機能（`c_str()` など）が必要 |
| `const char*` | 長さを持たない。`'\0'` 終端 | C の API に渡す |
| [`std::span<const char>`](../containers/span.md) | 文字列の機能（find など）が無い | バイト列として扱う |

## コンパイラ対応

C++17 からある機能です。`starts_with` / `ends_with` は C++20、`contains` は C++23 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 読むだけの文字列の引数は `std::string_view`（値渡し）
    - [x] substr / remove_prefix はコピーしない
    - [x] 保存しない・返さない（元が消えると壊れる）
    - [x] `'\0'` 終端とは限らない

## 関連ページ

- [cpprefjp: std::basic_string_view](https://cpprefjp.github.io/reference/string_view/basic_string_view.html)
- [cppreference: std::basic_string_view](https://en.cppreference.com/w/cpp/string/basic_string_view)
