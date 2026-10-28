---
title: std::filesystem::equivalent
summary: "2 つのパスが同じファイルを指すか調べる。"
order: 22
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::equivalent

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

ゲームのアセット管理で、`Data/hero.png` と `./Data/../Data/hero.png` と `C:\Game\Data\hero.png` が、実は同じファイルだった、ということが起きます。文字列で比べると全部別のものに見えるので、同じ画像を 3 回読み込んでしまいます。

`std::filesystem::equivalent` は、<strong>パスの文字列ではなく、指している実体</strong>が同じかどうかを調べます。ファイルシステムに問い合わせるので、相対パスでも、`..` を含んでいても、リンク経由でも、同じものなら `true` が返ります。

!!! tip "ポイント"
    - 比べるのは文字列ではなく、ファイルシステム上の実体。表記の違いに左右されない
    - 両方のパスが存在している必要がある。存在しないパスを渡すと、例外（または `error_code`）になる
    - 文字列だけで比べたいなら `path::operator==`。ファイルシステムに問い合わせないので軽い
    - シンボリックリンクとその指し先は、同じ実体として `true` になる

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### equivalent {#equivalent}

<span class="ver ver-17">C++17</span>

```cpp
bool equivalent(const path& p1, const path& p2);
bool equivalent(const path& p1, const path& p2, std::error_code& ec) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p1`, `p2` | `const path&` | 比べる 2 つのパス。文字列から暗黙に変換できる |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先。渡すと例外を投げない |

内部では、両方のパスについてファイルのボリュームと識別番号（Windows ではボリューム シリアル番号とファイル インデックス、POSIX では `st_dev` と `st_ino`）を取り出して比べています。パスの文字列の組み立てを見ているわけではないので、`.` や `..` の扱いを自分で考える必要はありません。

戻り値は、同じ実体なら `true`、別の実体なら `false` です。ここで間違えやすいのは、<strong>両方が存在しないときは `false` ではなくエラー</strong>になることです。片方だけが存在しないときは `false` が返ります。「存在しない 2 つのパスは、どちらも同じ『無』だから等しい」とは扱われません。例外を避けたいときは `error_code` を受け取る版を使い、`ec` を見て判断します。

ハード リンクで同じ実体に 2 つの名前を付けたときも、`true` になります。名前が違っても、ディスク上の実体が 1 つなら同じ物として扱う、という考え方です。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>
#include <system_error>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("a.txt") << "x";
  std::ofstream("b.txt") << "y";

  // 表記が違っても、同じファイルなら true
  std::println("a.txt と ./a.txt: {}", fs::equivalent("a.txt", "./a.txt"));
  std::println("a.txt と 絶対パス: {}", fs::equivalent("a.txt", fs::absolute("a.txt")));
  std::println("a.txt と b.txt: {}", fs::equivalent("a.txt", "b.txt"));

  // 両方が存在しないときは、エラーになる
  std::error_code ec;
  bool r = fs::equivalent("none1.txt", "none2.txt", ec);
  std::println("両方なし: 結果={} エラー={}", r, static_cast<bool>(ec));
}
```

```text title="実行結果"
a.txt と ./a.txt: true
a.txt と 絶対パス: true
a.txt と b.txt: false
両方なし: 結果=false エラー=true
```

## ゲームでの使いどころ

アセットの二重読み込みを防ぐときに使います。読み込み済みのファイルの一覧に新しいパスを足す前に、すでにある物と `equivalent` で比べれば、表記の違いで重複することがありません。

ただし、比べるたびにファイルシステムへ問い合わせるので、数千のアセットと総当たりで比べると遅くなります。普通は、`canonical` で正規化したパスの文字列をキーにして `unordered_set` に入れるほうが速く、`equivalent` は「怪しいときの最終確認」に使います。

セーブ データの保存先と、読み込み元が同じファイルかどうかを確かめて、上書きの警告を出す場面にも向いています。

## よくあるミス

??? failure "存在しないパスを渡して、例外で落ちる"
    ファイルを作る前や消した後に比べると、`std::filesystem::filesystem_error` が投げられます。先に `exists` で確かめるか、`error_code` を受け取る版を使います。

??? failure "文字列が同じだから、同じファイルだと思い込む"
    相対パスは、実行中のカレント ディレクトリに依存します。`"a.txt"` という同じ文字列でも、別のカレント ディレクトリなら別のファイルです。`equivalent` は、その時点で解決される実体を比べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`canonical`](canonical.md) | パスを正規化して返す。比べる前の下ごしらえに使う |
| `path::operator==` | 文字列として比べるだけ。ファイルシステムに問い合わせない |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 実体が同じかを調べる
    - [x] 表記が違ってもよい
    - [x] 両方の存在が必要（なければエラー）

## 関連ページ

- [cpprefjp: std::filesystem::equivalent](https://cpprefjp.github.io/reference/filesystem/equivalent.html)
- [cppreference: std::filesystem::equivalent](https://en.cppreference.com/w/cpp/filesystem/equivalent)
