---
title: std::filesystem::absolute
summary: "相対パスを絶対パスにする。"
order: 18
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::absolute

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

相対パス `data/hero.png` は、「今、どのフォルダーで実行しているか」で意味が変わります。ログに出したり、別のプロセスに渡したりするときは、場所がはっきりした絶対パスにしておきたくなります。

`std::filesystem::absolute` は、相対パスの前に<strong>カレント ディレクトリをつなげて</strong>、絶対パスにします。文字列の上の処理だけで、ファイルが存在するかは調べません。

!!! tip "ポイント"
    - 相対パスに、カレント ディレクトリを前置するだけ。ファイルが存在していなくてもよい
    - `..` や `.` を取り除くかは、実装しだい。確実に整えるなら `lexically_normal`、実在するなら `canonical`
    - もともと絶対パスなら、そのまま返す（Windows では、ドライブ文字がない `\foo` などに補う）
    - シンボリックリンクは、たどらない

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### absolute {#absolute}

<span class="ver ver-17">C++17</span>

```cpp
path absolute(const path& p);
path absolute(const path& p, std::error_code& ec);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 絶対パスにしたいパス。存在しなくてもよい |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

内部では、[`current_path`](current_path.md) を取得して、`p` の前につなげています。ファイルシステムに問い合わせるのは、カレント ディレクトリを調べるときだけです。このため、存在しないパスでも使えます。

[`canonical`](canonical.md) との違いは、リンクを解決しないことと、`..` や `.` を<strong>取り除くとは決まっていない</strong>ことです。標準は、絶対パスにすることだけを求めています。実装によっては `absolute("a/../b")` が `カレント/a/../b` のまま残ります。手元の MSVC では、Windows の API を通すので `カレント/b` に整理されました。どの環境でも同じ形にしたいときは、さらに `lexically_normal()` を通します。

Windows では、`"\\foo"`（ドライブ文字なしのルート付きパス）や `"C:foo"`（ドライブごとのカレント ディレクトリからの相対）といった、中途半端なパスも、完全な絶対パスに補います。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <print>
#include <string>

int main() {
  namespace fs = std::filesystem;
  fs::path rel = "data/hero.png";
  fs::path abs = fs::absolute(rel);

  std::println("絶対パスになった: {}", abs.is_absolute());
  std::println("カレントから始まる: {}", abs == fs::current_path() / rel);

  // ファイルが存在しなくてもよい
  std::println("存在する: {}", fs::exists(abs));

  // .. が残るかは実装しだい。確実に消すなら lexically_normal
  fs::path messy = fs::absolute("data/../hero.png");
  std::println("整えた後に .. なし: {}", messy.lexically_normal().generic_string().find("..") == std::string::npos);
}
```

```text title="実行結果"
絶対パスになった: true
カレントから始まる: true
存在する: false
整えた後に .. なし: true
```

## ゲームでの使いどころ

ログやエラー メッセージに、ファイルの場所を出すときに使います。「`data/hero.png` が開けません」より、「`C:\Games\MyGame\data\hero.png` が開けません」のほうが、原因を探しやすくなります。

別のプロセス（外部ツールや、起動するコンバーター）にパスを渡すときも、相対パスのままだと、相手のカレント ディレクトリで解釈されて外れます。渡す前に `absolute` で固定します。

## よくあるミス

??? failure "`absolute` が `..` を消してくれると思う"
    消すかどうかは実装しだいです。比較やキーに使うなら、`canonical`（実在するとき）か、`absolute(p).lexically_normal()` を使います。

??? failure "起動後に `current_path` を変えて、結果がずれる"
    `absolute` は呼んだ時点のカレント ディレクトリを使います。実行中にカレント ディレクトリを変えるコードがあると、同じ相対パスでも結果が変わります。起動直後の位置を保存しておく設計が安全です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`canonical`](canonical.md) | `..` とリンクを解決する。実在が必要 |
| [`relative`](relative.md) | 逆に、基準からの相対パスにする |
| [`current_path`](current_path.md) | 基準になるカレント ディレクトリ |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 相対パスの前にカレントをつなげる
    - [x] 存在しなくてもよい
    - [x] `..` を消すかは実装しだい

## 関連ページ

- [cpprefjp: std::filesystem::absolute](https://cpprefjp.github.io/reference/filesystem/absolute.html)
- [cppreference: std::filesystem::absolute](https://en.cppreference.com/w/cpp/filesystem/absolute)
