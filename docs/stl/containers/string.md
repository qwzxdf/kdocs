---
title: std::string
summary: "文字列を持つ型。連結・検索・切り出しができる。長さに応じて自動で伸びる。"
order: 3
tags:
  - コンテナ
  - 文字列
---

# std::string

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-11">C++98〜</span>
`#include <string>`
</div>

`std::string` は、**長さが自由に変わる文字列**です。中身は「`char` の vector」のようなもので、足したり、一部を切り出したり、検索したりできます。C の `char` 配列と違って、長さの管理やメモリの確保を自分でする必要がありません。

!!! tip "ポイント"
    - <strong>文字列はとりあえずこれ。</strong> `char*` や `char[]` は使わない。
    - 足すのは `+` か `+=`、数値を混ぜて作るなら [`std::format`](../utilities/format.md)。
    - 関数で**読むだけ**なら引数は [`std::string_view`](../utilities/string_view.md) にする。
    - 毎フレーム作り直すと**メモリ確保が走って重い**。ゲームループ内では作りすぎない。

!!! info "このページを読む前に"
    [参照](../../basics/reference.md) が分かると読みやすいです。vector と共通の関数が多いので、先に [`std::vector`](vector.md) を読んでおくと楽です。

## 宣言

```cpp
template <class CharT, class Traits = std::char_traits<CharT>,
          class Allocator = std::allocator<CharT>>
class basic_string;

using string = basic_string<char>;
using u8string = basic_string<char8_t>;
using wstring = basic_string<wchar_t>;
```

| 型 | 重要度 | 中身 | 使う場面 |
| --- | --- | --- | --- |
| `std::string` | <span class="rank rank-must">必須</span> | `char`（UTF-8 を入れるのが普通） | ほぼすべて |
| `std::wstring` | <span class="rank rank-sometimes">たまに</span> | `wchar_t`（Windows では UTF-16） | Windows API にワイド文字で渡すとき |
| `std::u8string` | <span class="rank rank-rare">知ってるだけ</span> | `char8_t` | UTF-8 を型で区別したいとき。周りが対応しておらず扱いにくい |
| `std::u16string` / `u32string` | <span class="rank rank-rare">知ってるだけ</span> | `char16_t` / `char32_t` | ほぼ使わない |

### 作り方

| 書き方 | 重要度 | 結果 |
| --- | --- | --- |
| `std::string s = "hello";` | <span class="rank rank-must">必須</span> | `hello` |
| `std::string s;` | <span class="rank rank-must">必須</span> | 空文字列 |
| `std::string s = std::format("HP {}", hp);` | <span class="rank rank-must">必須</span> | 数値などを埋め込んで作る |
| `auto s = "hello"s;` | <span class="rank rank-sometimes">たまに</span> | `std::string` リテラル（`using namespace std::literals;` が必要） |
| `std::string s(3, '-');` | <span class="rank rank-sometimes">たまに</span> | `---`（同じ文字を n 個） |
| `std::string s(view);` | <span class="rank rank-sometimes">たまに</span> | `string_view` からコピー |

## 関数一覧

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`operator+=`](#plus-eq) | <span class="rank rank-must">必須</span> | 末尾に足す | 償却 O(m) |
| [`operator+`](#plus) | <span class="rank rank-must">必須</span> | つないだ新しい文字列を作る | O(n + m) |
| [`size`](#size) | <span class="rank rank-must">必須</span> | 長さ（**バイト数**） | O(1) |
| [`operator==`](#eq) | <span class="rank rank-must">必須</span> | 等しいか | O(n) |
| [`empty`](#empty) | <span class="rank rank-must">必須</span> | 空かどうか | O(1) |
| [`std::to_string`](to_string.md) | <span class="rank rank-often">よく使う</span> | 数値を文字列に | O(桁数) |
| [`find`](#find) | <span class="rank rank-often">よく使う</span> | 部分文字列を前から探す | O(n·m) |
| [`substr`](#substr) | <span class="rank rank-often">よく使う</span> | 一部を切り出して新しい文字列を作る | O(m) |
| [`starts_with`](#starts_with) | <span class="rank rank-often">よく使う</span> | 先頭が一致するか <span class="ver ver-20">C++20</span> | O(m) |
| [`ends_with`](#ends_with) | <span class="rank rank-often">よく使う</span> | 末尾が一致するか <span class="ver ver-20">C++20</span> | O(m) |
| [`contains`](#contains) | <span class="rank rank-often">よく使う</span> | 含んでいるか <span class="ver ver-23">C++23</span> | O(n·m) |
| [`operator[]`](#operator) | <span class="rank rank-often">よく使う</span> | i バイト目の文字 | O(1) |
| [`clear`](#clear) | <span class="rank rank-often">よく使う</span> | 空にする | O(n) |
| [`std::stoi`](stoi.md) | <span class="rank rank-often">よく使う</span> | 文字列を int に | O(n) |
| [`std::stof`](stof.md) | <span class="rank rank-often">よく使う</span> | 文字列を float に | O(n) |
| [`rfind`](#rfind) | <span class="rank rank-often">よく使う</span> | 部分文字列を後ろから探す | O(n·m) |
| [`c_str`](#c_str) | <span class="rank rank-sometimes">たまに</span> | C の文字列として渡す | O(1) |
| [`push_back`](#push_back) | <span class="rank rank-sometimes">たまに</span> | 1 文字追加 | 償却 O(1) |
| [`pop_back`](#pop_back) | <span class="rank rank-sometimes">たまに</span> | 末尾の 1 文字を削除 | O(1) |
| [`replace`](#replace) | <span class="rank rank-sometimes">たまに</span> | 一部を置き換える | O(n) |
| [`append`](#append) | <span class="rank rank-sometimes">たまに</span> | 末尾に足す（`+=` の関数版） | 償却 O(m) |
| [`insert`](#insert) | <span class="rank rank-sometimes">たまに</span> | 途中に挿入 | O(n) |
| [`erase`](#erase) | <span class="rank rank-sometimes">たまに</span> | 途中を削除 | O(n) |
| [`reserve`](#reserve) | <span class="rank rank-sometimes">たまに</span> | 容量を先に確保 | O(n) |
| [`std::getline`](../io/getline.md) | <span class="rank rank-sometimes">たまに</span> | 1 行読み込む | O(n) |
| [`std::stod`](stod.md) | <span class="rank rank-sometimes">たまに</span> | 文字列を double に | O(n) |
| [`std::stoll`](stoll.md) | <span class="rank rank-sometimes">たまに</span> | 文字列を long long に | O(n) |
| [`data`](#data) | <span class="rank rank-sometimes">たまに</span> | 先頭のポインタ（書き換え可） | O(1) |
| [`find_first_not_of`](#find_first_not_of) | <span class="rank rank-sometimes">たまに</span> | 指定した文字**以外**を前から探す | O(n·m) |
| [`find_last_not_of`](#find_last_not_of) | <span class="rank rank-sometimes">たまに</span> | 指定した文字**以外**を後ろから探す | O(n·m) |
| [`operator<=>`](#spaceship) | <span class="rank rank-sometimes">たまに</span> | 辞書順の大小比較 | O(n) |
| [`length`](#length) | <span class="rank rank-rare">知ってるだけ</span> | `size` と同じ | O(1) |
| [`find_first_of`](#find_first_of) | <span class="rank rank-rare">知ってるだけ</span> | 指定した文字のどれかを前から探す | O(n·m) |
| [`find_last_of`](#find_last_of) | <span class="rank rank-rare">知ってるだけ</span> | 指定した文字のどれかを後ろから探す | O(n·m) |
| [`resize`](#resize) | <span class="rank rank-rare">知ってるだけ</span> | 長さを変える | O(n) |
| [`front`](#front) | <span class="rank rank-rare">知ってるだけ</span> | 先頭の文字 | O(1) |
| [`back`](#back) | <span class="rank rank-rare">知ってるだけ</span> | 末尾の文字 | O(1) |
| [`at`](#at) | <span class="rank rank-rare">知ってるだけ</span> | 範囲チェック付きアクセス | O(1) |
| [`capacity`](#capacity) | <span class="rank rank-rare">知ってるだけ</span> | 確保済みの容量 | O(1) |
| [`shrink_to_fit`](#shrink_to_fit) | <span class="rank rank-rare">知ってるだけ</span> | 余った容量を返す | O(n) |
| [`compare`](#compare) | <span class="rank rank-rare">知ってるだけ</span> | 大小を整数で返す | O(n) |
| [`assign`](#assign) | <span class="rank rank-rare">知ってるだけ</span> | 中身を入れ替える | O(n) |
| [`swap`](#swap) | <span class="rank rank-rare">知ってるだけ</span> | 中身を交換 | O(1) |
| [`copy`](#copy) | <span class="rank rank-rare">知ってるだけ</span> | char 配列にコピー | O(m) |

## よくある使い方

### 1. 組み立てて表示する

```cpp
#include <format>
#include <print>
#include <string>

int main() {
  std::string name = "Alice";
  int level = 12;

  // + でつなぐ（数値はそのまま足せないので to_string）
  std::string a = name + " Lv." + std::to_string(level);

  // format のほうが読みやすい
  std::string b = std::format("{} Lv.{}", name, level);

  // += で後ろに足していく
  std::string log;
  log += "攻撃！";
  log += " 25 ダメージ";

  std::println("{}", a);
  std::println("{}", b);
  std::println("{}", log);
}
```

```text title="実行結果"
Alice Lv.12
Alice Lv.12
攻撃！ 25 ダメージ
```

### 2. 調べる・切り出す

```cpp
#include <print>
#include <string>

int main() {
  std::string path = "assets/textures/player.png";

  if (path.ends_with(".png")) {
    std::println("画像ファイル");
  }

  // 最後の / の位置を探して、その後ろ（ファイル名）を切り出す
  std::size_t slash = path.rfind('/');
  std::string file = path.substr(slash + 1);
  std::println("ファイル名: {}", file);

  // 見つからないときは std::string::npos が返る
  if (path.find("sound") == std::string::npos) {
    std::println("sound は含まれない");
  }
}
```

```text title="実行結果"
画像ファイル
ファイル名: player.png
sound は含まれない
```

### 3. 文字列と数値を変換する

```cpp
#include <print>
#include <string>

int main() {
  std::string text = "1500";
  int gold = std::stoi(text);       // 文字列 → int
  float rate = std::stof("0.25");   // 文字列 → float
  std::string s = std::to_string(gold * 2);  // int → 文字列

  std::println("{} {} {}", gold, rate, s);
}
```

```text title="実行結果"
1500 0.25 3000
```

### 4. カンマで分割する

C++ には `split` 関数がないので、`std::views::split` を使います。

```cpp
#include <print>
#include <ranges>
#include <string>
#include <string_view>
#include <vector>

int main() {
  std::string csv = "sword,shield,potion";

  std::vector<std::string> items;
  for (auto part : csv | std::views::split(',')) {
    items.emplace_back(std::string_view(part));
  }
  std::println("{}", items);
}
```

```text title="実行結果"
["sword", "shield", "potion"]
```

## 関数の詳しい説明

### operator+= {#plus-eq}

```cpp
basic_string& operator+=(const basic_string& str);
basic_string& operator+=(std::string_view sv);
basic_string& operator+=(const CharT* s);
basic_string& operator+=(CharT ch);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` / `sv` / `s` | 文字列 | 末尾に足す文字列 |
| `ch` | `char` | 末尾に足す 1 文字 |

- 戻り値: 自分自身の参照
- 計算量: 償却 O(足す長さ)。容量が足りなければ再確保

```cpp
#include <print>
#include <string>

int main() {
  std::string log;
  log += "攻撃！";
  log += ' ';
  log += std::string("25 ダメージ");
  std::println("{}", log);
}
```

```text title="実行結果"
攻撃！ 25 ダメージ
```

!!! note "実際は"
    文字列を少しずつ組み立てるときの基本です。`+` と違って新しい文字列を作らないので速いです。

### operator+ {#plus}

```cpp
basic_string operator+(const basic_string& lhs, const basic_string& rhs);
basic_string operator+(const basic_string& lhs, const CharT* rhs);
basic_string operator+(const CharT* lhs, const basic_string& rhs);
basic_string operator+(const basic_string& lhs, CharT rhs);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `lhs`, `rhs` | 文字列 / 文字 | つなぐ 2 つ。**どちらかは `std::string` である必要がある** |

- 戻り値: つないだ**新しい文字列**
- 計算量: O(n + m)

```cpp
#include <print>
#include <string>

int main() {
  std::string name = "Alice";
  std::string title = name + " Lv." + std::to_string(12);
  std::println("{}", title);
}
```

```text title="実行結果"
Alice Lv.12
```

!!! note "実際は"
    `a + b + c + d` は途中で一時的な文字列が何個も作られます。たくさんつなぐなら `+=` か `std::format` のほうが速くて読みやすいです。

### size {#size}

```cpp
size_type size() const noexcept;
```

- 戻り値: 長さ。**文字数ではなくバイト数**
- 計算量: O(1)

```cpp
#include <print>
#include <string>

int main() {
  std::string en = "abc";
  std::string ja = "あいう";
  std::println("{} {}", en.size(), ja.size());
}
```

```text title="実行結果"
3 9
```

!!! warning "日本語は 1 文字 3 バイト"
    UTF-8 では日本語 1 文字が 3 バイトなので、`size()` は**見た目の文字数ではありません**。`s[1]` も「2 文字目」ではなく「2 バイト目」です。

### operator== {#eq}

```cpp
bool operator==(const basic_string& lhs, const basic_string& rhs) noexcept;
bool operator==(const basic_string& lhs, const CharT* rhs);
```

- 戻り値: 中身が同じなら `true`。`!=` も使える
- 計算量: O(n)（長さが違えばすぐ終わる）

```cpp
#include <print>
#include <string>

int main() {
  std::string command = "attack";
  if (command == "attack") {
    std::println("攻撃する");
  }
}
```

```text title="実行結果"
攻撃する
```

!!! note "実際は"
    C の文字列（`char*`）同士を `==` で比べるとアドレスの比較になってしまいますが、`std::string` なら中身を比べてくれます。

### empty {#empty}

```cpp
bool empty() const noexcept;
```

- 戻り値: 長さが 0 なら `true`
- 計算量: O(1)

```cpp
#include <print>
#include <string>

int main() {
  std::string input;
  if (input.empty()) {
    std::println("名前を入力してください");
  }
}
```

```text title="実行結果"
名前を入力してください
```

!!! note "実際は"
    `s == ""` や `s.size() == 0` より意図がはっきりします。

### find {#find}

```cpp
size_type find(const basic_string& str, size_type pos = 0) const noexcept;
size_type find(const CharT* s, size_type pos = 0) const;
size_type find(CharT ch, size_type pos = 0) const noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` / `s` / `ch` | 文字列 / 文字 | 探すもの |
| `pos` | `size_type` | 探し始める位置。省略すると先頭から |

- 戻り値: 最初に見つかった位置。**見つからなければ `std::string::npos`**
- 計算量: 最悪 O(n·m)

<div class="anim" data-label="s.find(&quot;cd&quot;)">
a b c d e # s = "abcde"
a b *c *d e # 見つかった位置（2）を返す。見つからなければ npos
</div>

```cpp
#include <print>
#include <string>

int main() {
  std::string text = "HP:100 MP:30";
  std::size_t pos = text.find("MP:");
  std::println("MP は {} バイト目から", pos);

  if (text.find("SP:") == std::string::npos) {
    std::println("SP は無い");
  }
}
```

```text title="実行結果"
MP は 7 バイト目から
SP は無い
```

!!! note "実際は"
    「含んでいるか」だけなら C++23 の [`contains`](#contains) のほうが短く書けます。位置が欲しいときに `find` を使います。

### substr {#substr}

```cpp
basic_string substr(size_type pos = 0, size_type count = npos) const;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pos` | `size_type` | 切り出し開始位置 |
| `count` | `size_type` | 長さ。省略すると最後まで |

- 戻り値: **新しい文字列**（コピー）
- 例外: `pos > size()` なら `std::out_of_range`
- 計算量: O(count)

<div class="anim" data-label="s.substr(2, 3)">
a b c d e f # s = "abcdef"
a b *c *d *e f # 位置 2 から 3 文字
c d e # 新しい文字列としてコピーされる
</div>

```cpp
#include <print>
#include <string>

int main() {
  std::string path = "assets/player.png";
  std::size_t slash = path.find('/');
  std::println("フォルダ: {}", path.substr(0, slash));
  std::println("ファイル: {}", path.substr(slash + 1));
}
```

```text title="実行結果"
フォルダ: assets
ファイル: player.png
```

!!! note "実際は"
    コピーを作るので、読むだけなら `std::string_view` の `substr` のほうが軽いです。

### starts_with <span class="ver ver-20">C++20</span> {#starts_with data-toc-label="starts_with"}

```cpp
bool starts_with(std::string_view sv) const noexcept;
bool starts_with(CharT ch) const noexcept;
```

- 戻り値: 先頭が `sv`（または `ch`）なら `true`
- 計算量: O(sv の長さ)

<div class="anim" data-label="s.starts_with(&quot;ab&quot;)">
a b c d # s = "abcd"
*a *b c d # 先頭が "ab" なら true
</div>

### ends_with <span class="ver ver-20">C++20</span> {#ends_with data-toc-label="ends_with"}

```cpp
bool ends_with(std::string_view sv) const noexcept;
bool ends_with(CharT ch) const noexcept;
```

- 戻り値: 末尾が `sv`（または `ch`）なら `true`
- 計算量: O(sv の長さ)

<div class="anim" data-label="s.ends_with(&quot;cd&quot;)">
a b c d # s = "abcd"
a b *c *d # 末尾が "cd" なら true
</div>

```cpp
#include <print>
#include <string>

int main() {
  std::string file = "stage1.json";
  std::println("JSON？ {}", file.ends_with(".json"));
  std::println("stage？ {}", file.starts_with("stage"));
}
```

```text title="実行結果"
JSON？ true
stage？ true
```

!!! note "実際は"
    拡張子やプレフィックス（`"debug_"` など）の判定に使います。端だけを見るので速いです。

### contains <span class="ver ver-23">C++23</span> {#contains data-toc-label="contains"}

```cpp
bool contains(std::string_view sv) const noexcept;
bool contains(CharT ch) const noexcept;
```

- 戻り値: どこかに `sv`（または `ch`）を含んでいれば `true`
- 計算量: O(n·m)

<div class="anim" data-label="s.contains(&quot;bc&quot;)">
a b c d # s = "abcd"
a *b *c d # どこかに含まれれば true
</div>

```cpp
#include <print>
#include <string>

int main() {
  std::string msg = "[ERROR] file not found";
  std::println("{}", msg.contains("not found"));
}
```

```text title="実行結果"
true
```

!!! note "実際は"
    古いコードの `s.find("x") != std::string::npos` が `s.contains("x")` で済みます。

### operator[] {#operator}

```cpp
reference operator[](size_type pos);
const_reference operator[](size_type pos) const;
```

- 戻り値: `pos` バイト目の `char` の参照
- 計算量: O(1)
- 範囲外は未定義動作（ただし `s[s.size()]` は `'\0'` が読める）

<div class="anim" data-label="s[1]">
a b c d # s
a *b c d # s[1] は 'b'。範囲チェックなし
</div>

```cpp
#include <print>
#include <string>

int main() {
  std::string code = "ABCD";
  code[0] = 'X';
  std::println("{} {}", code, code[3]);
}
```

```text title="実行結果"
XBCD D
```

!!! note "実際は"
    英数字だけの文字列（ID、コマンド）なら便利ですが、日本語には使えません（1 文字が複数バイトのため）。

### clear {#clear}

```cpp
void clear() noexcept;
```

- 長さを 0 にします。**容量（`capacity`）はそのまま**
- 計算量: O(n)（`char` なら実質タダ）

<div class="anim" data-label="s.clear()">
H e l l o # s
xH xe xl xl xo # 文字をすべて消す
_ _ _ _ _ # size 0。capacity は残る
</div>

```cpp
#include <print>
#include <string>

int main() {
  std::string buffer = "前のフレームのログ";
  buffer.clear();
  buffer += "新しいログ";
  std::println("{}", buffer);
}
```

```text title="実行結果"
新しいログ
```

!!! note "実際は"
    使い回す文字列（ログのバッファなど）は、作り直さずに `clear` してから `+=` すると再確保が起きません。

### rfind {#rfind}

```cpp
size_type rfind(const basic_string& str, size_type pos = npos) const noexcept;
size_type rfind(CharT ch, size_type pos = npos) const noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` / `ch` | 文字列 / 文字 | 探すもの |
| `pos` | `size_type` | この位置から**前に向かって**探す。省略すると末尾から |

- 戻り値: 最後に見つかった位置。見つからなければ `npos`

<div class="anim" data-label="s.rfind('a')">
a b a c a # s = "abaca"
a b a c *a # 後ろから探して、最初に見つかった位置（4）
</div>

```cpp
#include <print>
#include <string>

int main() {
  std::string path = "assets/textures/player.png";
  std::size_t dot = path.rfind('.');
  std::println("拡張子: {}", path.substr(dot));
}
```

```text title="実行結果"
拡張子: .png
```

!!! note "実際は"
    パスの最後の `/` や `.` を探すのが定番の使い方です。

### c_str {#c_str}

```cpp
const CharT* c_str() const noexcept;
```

- 戻り値: 末尾に `'\0'` が付いた C の文字列
- 計算量: O(1)

```cpp
#include <cstdio>
#include <string>

int main() {
  std::string name = "Alice";
  std::printf("Hello, %s\n", name.c_str());
}
```

```text title="実行結果"
Hello, Alice
```

!!! warning
    文字列を変更したり破棄したりすると、`c_str()` のポインタは無効になります。保存せずにその場で渡すだけにします。

### push_back {#push_back}

```cpp
void push_back(CharT ch);
```

- 1 文字を末尾に追加します。`s += ch` と同じです
- 計算量: 償却 O(1)

<div class="anim" data-label="s.push_back('!')">
H i # s = "Hi"
H i +! # 末尾に 1 文字足す
</div>

### pop_back {#pop_back}

```cpp
void pop_back();
```

- 末尾の 1 バイトを消します。**空のとき未定義動作**
- 計算量: O(1)

<div class="anim" data-label="s.pop_back()">
H i ! # s = "Hi!"
H i x! # 最後の 1 文字を消す
H i # 完了
</div>

```cpp
#include <print>
#include <string>

int main() {
  std::string input = "abc";
  input.push_back('d');
  std::println("{}", input);
  input.pop_back();  // バックスペース
  input.pop_back();
  std::println("{}", input);
}
```

```text title="実行結果"
abcd
ab
```

!!! note "実際は"
    テキスト入力欄のバックスペース処理などで使います。日本語を消すときは 3 バイト分消す必要があるので注意します。

### replace {#replace}

```cpp
basic_string& replace(size_type pos, size_type count, const basic_string& str);
basic_string& replace(size_type pos, size_type count, size_type count2, CharT ch);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pos` | `size_type` | 置き換え開始位置 |
| `count` | `size_type` | 置き換える長さ |
| `str` | 文字列 | 新しい中身 |
| `count2`, `ch` | | `ch` を `count2` 個にする |

- 計算量: O(n)（長さが変わると後ろをずらす）

<div class="anim" data-label="s.replace(0, 2, &quot;HI&quot;)">
h i ! # s = "hi!"
xh xi ! # 置き換える範囲
+H +I ! # 新しい文字に置き換わる
</div>

```cpp
#include <print>
#include <string>

int main() {
  std::string text = "HP: {hp}";
  std::string key = "{hp}";
  text.replace(text.find(key), key.size(), "120");
  std::println("{}", text);
}
```

```text title="実行結果"
HP: 120
```

!!! note "実際は"
    全部置き換える関数は無いので、`find` と `replace` をループで回します。テンプレート文字列の差し込みなら、最初から `std::format` を使うほうが簡単です。

### append {#append}

```cpp
basic_string& append(const basic_string& str);
basic_string& append(const basic_string& str, size_type pos, size_type count);
basic_string& append(size_type count, CharT ch);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | 文字列 | 足す文字列 |
| `pos`, `count` | `size_type` | `str` の一部だけ足すとき |
| `count`, `ch` | | 同じ文字を `count` 個足す |

<div class="anim" data-label="s.append(&quot;abc&quot;)">
H i # s = "Hi"
H i +a +b +c # 末尾に文字列をつなぐ
</div>

```cpp
#include <print>
#include <string>

int main() {
  std::string bar = "[";
  bar.append(7, '#');
  bar.append(3, '-');
  bar += "]";
  std::println("{}", bar);
}
```

```text title="実行結果"
[#######---]
```

!!! note "実際は"
    普段は `+=` で足ります。「同じ文字を n 個」を足すとき（HP バーなど）に便利です。

### insert {#insert}

```cpp
basic_string& insert(size_type pos, const basic_string& str);
basic_string& insert(size_type pos, size_type count, CharT ch);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pos` | `size_type` | 挿入位置（添字で指定できる） |
| `str` | 文字列 | 挿入する文字列 |
| `count`, `ch` | | 同じ文字を `count` 個 |

- 計算量: O(n)

<div class="anim" data-label="s.insert(1, &quot;ey&quot;)">
H i # s = "Hi"
H _ _ >i # 挿入位置より後ろをずらす
H +e +y i # すき間に入れる
</div>

```cpp
#include <print>
#include <string>

int main() {
  std::string s = "1000000";
  s.insert(4, ",");
  s.insert(1, ",");
  std::println("{}", s);
}
```

```text title="実行結果"
1,000,000
```

### erase {#erase}

```cpp
basic_string& erase(size_type pos = 0, size_type count = npos);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pos` | `size_type` | 消し始める位置 |
| `count` | `size_type` | 消す長さ。省略すると最後まで |

- 計算量: O(n)

<div class="anim" data-label="s.erase(1, 2)">
a b c d # s = "abcd"
a xb xc d # 位置 1 から 2 文字を消す
a >d _ _ # 後ろを詰める
</div>

```cpp
#include <print>
#include <string>

int main() {
  std::string s = "debug_player";
  s.erase(0, 6);  // 先頭 6 文字を消す
  std::println("{}", s);
}
```

```text title="実行結果"
player
```

!!! note "実際は"
    vector と違って位置を**添字**で指定できます。特定の文字を全部消すなら `std::erase(s, ' ')` が使えます。

### reserve {#reserve}

```cpp
void reserve(size_type new_cap);
```

- 長い文字列を少しずつ組み立てる前に呼ぶと、再確保が減ります（[vector の reserve](vector.md#reserve) と同じ）

### data {#data}

```cpp
CharT* data() noexcept;
const CharT* data() const noexcept;
```

- 戻り値: 先頭のポインタ。C++17 からは書き換え可能なポインタが返る
- 末尾の `'\0'` も保証される（`c_str()` と同じ）

!!! note "実際は"
    `std::string s(256, '\0');` で場所を用意して、C の API に `s.data()` で書き込んでもらう、という使い方ができます。

### find_first_not_of {#find_first_not_of}

```cpp
size_type find_first_not_of(const basic_string& chars, size_type pos = 0) const noexcept;
```

- 戻り値: `chars` に**含まれない**文字が最初に出てくる位置

### find_last_not_of {#find_last_not_of}

```cpp
size_type find_last_not_of(const basic_string& chars, size_type pos = npos) const noexcept;
```

- 戻り値: `chars` に含まれない文字が最後に出てくる位置

```cpp
#include <print>
#include <string>

int main() {
  std::string s = "  hello  ";
  std::size_t first = s.find_first_not_of(' ');
  std::size_t last = s.find_last_not_of(' ');
  std::println("[{}]", s.substr(first, last - first + 1));
}
```

```text title="実行結果"
[hello]
```

!!! note "実際は"
    前後の空白を取り除く（trim）ときの定番です。`" \t\r\n"` を渡すと改行やタブもまとめて飛ばせます。

### operator<=> {#spaceship}

```cpp
auto operator<=>(const basic_string& lhs, const basic_string& rhs) noexcept;
```

- 辞書順（文字コード順）で比べます。`<`, `>` などが使えるようになります

```cpp
#include <print>
#include <string>

int main() {
  std::string a = "apple";
  std::string b = "banana";
  std::println("{}", a < b);
}
```

```text title="実行結果"
true
```

!!! note "実際は"
    `std::map<std::string, T>` や `std::ranges::sort` が中で使います。大文字は小文字より前に来る点に注意します（`"Z" < "a"`）。

### length {#length}

```cpp
size_type length() const noexcept;
```

- `size()` とまったく同じです。どちらを使っても構いませんが、他のコンテナとそろえて `size()` を使うのが一般的です。

### find_first_of {#find_first_of}

```cpp
size_type find_first_of(const basic_string& chars, size_type pos = 0) const noexcept;
```

- 戻り値: `chars` の**どれか 1 文字**が最初に出てくる位置

### find_last_of {#find_last_of}

```cpp
size_type find_last_of(const basic_string& chars, size_type pos = npos) const noexcept;
```

- 戻り値: `chars` のどれか 1 文字が最後に出てくる位置

```cpp
#include <print>
#include <string>

int main() {
  // Windows と Unix の区切り文字が混ざったパス
  std::string path = "assets\\enemy/boss.png";
  std::size_t sep = path.find_last_of("/\\");
  std::println("{}", path.substr(sep + 1));
}
```

```text title="実行結果"
boss.png
```

!!! note "実際は"
    「`/` か `\` のどちらか」のように、複数の候補の文字を探したいときに使います。

### resize {#resize}

```cpp
void resize(size_type count);
void resize(size_type count, CharT ch);
```

- 長さを `count` にします。増えた分は `'\0'`（または `ch`）で埋まります

<div class="anim" data-label="s.resize(5, '.')">
H i # s = "Hi"
H i +. +. +. # 足りない分を '.' で埋める
</div>

```cpp
#include <print>
#include <string>

int main() {
  std::string name = "Al";
  name.resize(6, '.');
  std::println("{}", name);
}
```

```text title="実行結果"
Al....
```

### front {#front}

```cpp
CharT& front();
```

- 先頭の 1 バイト。`s[0]` と同じ。空のとき未定義動作

<div class="anim" data-label="s.front()">
a b c # s
*a b c # 先頭の文字
</div>

### back {#back}

```cpp
CharT& back();
```

- 末尾の 1 バイト。`s[s.size() - 1]` と同じ。空のとき未定義動作

<div class="anim" data-label="s.back()">
a b c # s
a b *c # 最後の文字
</div>

```cpp
#include <print>
#include <string>

int main() {
  std::string path = "assets/";
  if (path.back() != '/') {
    path += '/';
  }
  std::println("{}{}", path.front(), path.back());
}
```

```text title="実行結果"
a/
```

### at {#at}

```cpp
CharT& at(size_type pos);
```

- 範囲外なら `std::out_of_range`。使い方は vector の `at` と同じです

<div class="anim" data-label="s.at(1)">
a b c d # s
a *b c d # s.at(1) は 'b'。範囲外なら例外
</div>

### capacity {#capacity}

```cpp
size_type capacity() const noexcept;
```

- 再確保せずに入る長さ。短い文字列は SSO のおかげで最初から 15 などになっています（[パフォーマンス](#パフォーマンス)）

```cpp
#include <print>
#include <string>

int main() {
  std::string s;
  std::println("{}", s.capacity());
}
```

```text title="実行結果（GCC の例）"
15
```

### shrink_to_fit {#shrink_to_fit}

```cpp
void shrink_to_fit();
```

- 余った容量を返すようにお願いします。vector と同じく、ほぼ使いません

<div class="anim" data-label="s.shrink_to_fit()">
a b c _ _ _ # size 3 / capacity 6
a b c # 余った capacity を返す（保証はない）
</div>

### compare {#compare}

```cpp
int compare(const basic_string& str) const noexcept;
```

- 戻り値: 自分が小さければ負、等しければ 0、大きければ正

!!! note "実際は"
    C++20 からは `<=>` や `<`, `==` で書けるので使いません。古いコードで見かける程度です。

### assign {#assign}

```cpp
basic_string& assign(const basic_string& str);
basic_string& assign(size_type count, CharT ch);
```

- 中身を丸ごと入れ替えます。`s = str;` と同じです

### swap {#swap}

```cpp
void swap(basic_string& other) noexcept;
```

- 中身を交換します。長い文字列ならポインタの交換だけなので O(1) です

### copy {#copy}

```cpp
size_type copy(CharT* dest, size_type count, size_type pos = 0) const;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `dest` | `CharT*` | コピー先の char 配列 |
| `count` | `size_type` | コピーする最大の長さ |
| `pos` | `size_type` | コピー元の開始位置 |

- 戻り値: コピーした長さ。**末尾に `'\0'` は付かない**

!!! note "実際は"
    固定長の char 配列（古い構造体、ネットワークのパケット）に詰めるときくらいです。`'\0'` を付け忘れるバグが起きやすいので注意します。

## フラグ・オプション

フラグはありません。よく使う**定数**だけ覚えておきます。

| 値 | 意味 |
| --- | --- |
| `std::string::npos` | 「見つからない」「最後まで」を表す特別な値（`size_type` の最大値） |

## 計算量まとめ

| 操作 | 計算量 |
| --- | --- |
| `size`, `empty`, `[]`, `clear` | O(1) |
| 末尾に追加（`+=`, `push_back`） | 償却 O(m) |
| 比較 | O(n) |
| `find`, `contains` | O(n·m) |
| `substr`, `+`（新しい文字列を作る） | O(m) + 確保 |
| 途中の `insert`, `erase`, `replace` | O(n) |

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    char buf[64];
    sprintf(buf, "HP %d/%d", hp, max_hp);  // バッファあふれの危険

    if (strcmp(cmd, "attack") == 0) {
    }

    if (path.find(".png") != std::string::npos) {
    }
    ```

=== "今の書き方（C++23）"

    ```cpp
    std::string text = std::format("HP {}/{}", hp, max_hp);

    if (cmd == "attack") {
    }

    if (path.contains(".png")) {
    }
    ```

## ゲームでの使いどころ

- **UI の表示テキスト**: スコア、HP、メッセージ。`std::format` で組み立てる
- **ファイルパス**: 読み込むアセットの場所。本格的に扱うなら `std::filesystem::path`
- **設定・セーブデータの読み書き**: `std::getline` で行を読み、分割して `std::from_chars` で数値に
- **ID・名前でのアクセス**: `std::unordered_map<std::string, Texture>` のキー

!!! warning "毎フレーム文字列を作らない"
    `std::format("Score: {}", score)` を毎フレーム実行すると、毎回メモリ確保が起きます。数十個なら問題ありませんが、何百個ものテキストを毎フレーム作るなら「値が変わったときだけ作り直す」ようにします。

## パフォーマンス

- <strong>SSO（Small String Optimization）</strong>: 短い文字列（GCC / MSVC なら 15 文字、Clang なら 22 文字くらいまで）は、ヒープを使わずオブジェクトの中に直接入ります。短い名前や ID はかなり軽いです。
- 長い文字列のコピーはヒープ確保が起きるので、関数の引数は `const std::string&` か `std::string_view` にします。
- 文字列をキーにした検索は、毎回文字列比較やハッシュ計算が走ります。何度も検索するなら、最初に数値の ID に変換しておくと速いです。

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| 範囲外の `[]` | 未定義動作 |
| `c_str()` のポインタを、文字列を変更・破棄したあとに使う | 未定義動作 |
| `substr` で `pos > size()` | `std::out_of_range` 例外 |
| `stoi` に数字でない文字列 | `std::invalid_argument` 例外 |
| `stoi` で int に入らない数 | `std::out_of_range` 例外 |

## よくあるミス

??? failure "文字列リテラル同士を + する"
    ```cpp
    std::string s = "HP: " + "100";  // コンパイルエラー（ポインタ同士の足し算）
    std::string s2 = std::string("HP: ") + "100";  // OK
    std::string s3 = "HP: " + std::to_string(100);  // OK
    ```

??? failure "数値を + で足して文字化け"
    ```cpp
    std::string s = "Lv.";
    s += 5;  // コンパイルは通るが、文字コード 5 の文字が追加される

    s += std::to_string(5);  // OK
    ```

??? failure "find の戻り値を int で受ける・npos と比べない"
    ```cpp
    int pos = s.find("x");  // 見つからないと -1 になるが、型が合っていない
    std::string tail = s.substr(s.find("x"));  // 見つからないと例外

    // OK
    if (std::size_t p = s.find("x"); p != std::string::npos) {
      std::string tail2 = s.substr(p);
    }
    ```

??? failure "日本語を 1 文字ずつ処理しようとする"
    `"あいう"[0]` は「あ」ではなく、「あ」の 3 バイトのうち最初の 1 バイトです。表示が壊れます。[size](#size) を参照してください。

??? failure "c_str() を保存しておく"
    ```cpp
    const char* name = GetName().c_str();  // GetName() が返した一時文字列はすぐ消える
    std::puts(name);                       // 未定義動作
    ```

## 類似クラス

| 名前 | 違い | こっちを使うとき |
| --- | --- | --- |
| [`std::string_view`](../utilities/string_view.md) | 中身を持たず、文字列を「借りる」だけ | 関数の引数（読むだけ） |
| `const char*` | C の文字列。長さを持たない | C の API に渡すとき（`c_str()` で作る） |
| [`std::vector<char>`](vector.md) | 文字列専用の関数がない | バイナリデータ |
| `std::filesystem::path` | パス専用。区切り文字や拡張子を扱える | ファイルパス |

## コンパイラ対応

| 機能 | MSVC | GCC | Clang (libc++) |
| --- | --- | --- | --- |
| `starts_with` / `ends_with` <span class="ver ver-20">C++20</span> | ○ | ○ | ○ |
| `contains` <span class="ver ver-23">C++23</span> | VS 2022 17.0〜 | 11〜 | 12〜 |
| `std::views::split` で string_view に変換 <span class="ver ver-23">C++23</span> | VS 2022 17.2〜 | 12〜 | 16〜 |

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字列は `std::string`。作るときは `std::format`
    - [x] 読むだけの引数は `std::string_view`
    - [x] `find` は見つからないと `std::string::npos`
    - [x] `size()` はバイト数。日本語は 1 文字 3 バイト
    - [x] 毎フレーム大量に作らない

## 関連ページ

- [std::string_view](../utilities/string_view.md)
- [std::format / std::print](../utilities/format.md)
- [cpprefjp: std::basic_string](https://cpprefjp.github.io/reference/string/basic_string.html)
- [cppreference: std::basic_string](https://en.cppreference.com/w/cpp/string/basic_string)
