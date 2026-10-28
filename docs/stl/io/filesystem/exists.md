---
title: std::filesystem::exists
summary: "ファイルやフォルダがあるか調べる。"
order: 2
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::exists

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

ゲームの起動時に設定ファイルがあるかを確かめて、なければ初期値で作り直したい。セーブデータを読む前にファイルが存在するかを調べたい。こうした「あるか、ないか」の確認に使うのが `std::filesystem::exists` です。ファイルを開いて失敗するかを見るより、意図がはっきり読み取れます。

!!! tip "ポイント"
    - ファイルとフォルダの区別はしない。区別したいときは `is_regular_file` や `is_directory` を使う。
    - 例外を避けたいときは、`std::error_code` を渡す版を使う。
    - 「あるか調べてから開く」の間に消されることがある。確実に読むなら、開いて失敗を確かめる。

!!! info "このページを読む前に"
    [`std::filesystem::path`](path.md) の書き方を先に読んでください。

## 関数の詳しい説明

### exists {#exists}

```cpp
bool exists(const path& p);
bool exists(const path& p, std::error_code& ec) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 調べるパス |
| `ec` | `std::error_code&` | 失敗したときにエラーが入る（例外を投げない版） |

`p` は調べるパスです。存在すれば `true` を返します。相対パスは、実行時のカレントディレクトリから見た位置になります。IDE から実行したときと、exe を直接ダブルクリックしたときで、カレントディレクトリが違うことがあります。

`ec` を渡す版は、権限のないフォルダなどでエラーになっても、例外を投げずに `ec` に結果を入れます。`ec` を渡さない版は、パスの確認自体に失敗したとき（アクセス権がないなど）、`filesystem_error` 例外を投げます。ただし、「パスが存在しない」だけでは例外になりません。`false` を返します。

シンボリックリンクは、リンク先を調べます。リンク切れのリンクは、`false` になります。

- 戻り値: ファイルかフォルダがあれば `true`

```cpp
#include <filesystem>
#include <print>

int main() {
  namespace fs = std::filesystem;
  if (!fs::exists("config.json")) {
    std::println("設定ファイルが無いのでデフォルトを使う");
  }
}
```

```text title="実行結果"
設定ファイルが無いのでデフォルトを使う
```

## しくみ

`exists` は、内部で `status(p)` を呼んで、結果が `file_type::not_found` でないかを調べているだけです。ファイルの種類や権限も知りたいなら、`status` を 1 回呼んで、その結果を使い回すほうが、システムへの問い合わせが減ります。

「あるか調べて、あれば開く」という 2 段階の書き方には、調べたあと開く前に別のプログラムがファイルを消すかもしれない、という問題があります。これを TOCTOU（調べた時点と使う時点のずれ）と呼びます。ゲームのセーブデータ程度では気にしなくてよいですが、ファイルを開く操作そのものが成功したかを見るほうが確実です。

## ゲームでの使いどころ

起動時の設定ファイルの確認が代表例です。`if (!fs::exists("config.json")) { WriteDefaultConfig(); }` と書いて、ない場合だけ初期値を書き出します。

セーブデータのスロットが使用中かの判定にも使います。`fs::exists(SlotPath(i))` で、「データあり」と「空き」を表示し分けます。

アセットの読み込みでは、拡張子の違う候補（`.png` と `.dds`）を順に調べて、あるものを使う、という書き方があります。

## よくあるミス

??? failure "相対パスで、実行場所が違って見つからない"
    IDE のデバッグ実行では、プロジェクトのフォルダがカレントディレクトリになりますが、exe を直接起動するとその exe のあるフォルダになるなど、環境によって変わります。ファイルを確実に見つけたいときは、`std::filesystem::current_path()` を表示して確かめるか、exe の位置を基準にしたパスを作ります。

??? failure "フォルダとファイルを区別しない"
    `exists("saves")` が `true` でも、それがファイルかフォルダかは分かりません。フォルダに書き込むつもりが、同じ名前のファイルがあって失敗する、ということが起こります。`is_directory` で種類も確かめます。

??? failure "調べたあとにファイルが消える"
    `exists` が `true` でも、開く時点では消えているかもしれません。ファイルを開く操作の戻り値（`ifstream` の状態）を必ず確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_regular_file`](is_regular_file.md) | 通常のファイルかを調べる。フォルダは `false` |
| [`is_directory`](is_directory.md) | フォルダかを調べる |
| [`status`](status.md) | 種類と権限をまとめて取る。`exists` はこの結果を使っている |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルもフォルダも区別せず、あれば `true`。
    - [x] 相対パスはカレントディレクトリが基準。
    - [x] 「調べてから開く」より、開いて失敗を確かめるほうが確実。

## 関連ページ

- [cpprefjp: std::filesystem::exists](https://cpprefjp.github.io/reference/filesystem/exists.html)
- [cppreference: std::filesystem::exists](https://en.cppreference.com/w/cpp/filesystem/exists)
