---
title: std::filesystem::temp_directory_path
summary: "一時ファイル用のフォルダの場所を返す。"
order: 20
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::temp_directory_path

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

ダウンロードしたファイルを一時的に置きたい。圧縮ファイルを展開する作業場所が欲しい。クラッシュ レポートを書き出したい。こうした「あとで消えてよいファイル」の置き場は、アプリが勝手にフォルダーを決めるより、OS が用意している一時フォルダーを使うのが作法です。

`std::filesystem::temp_directory_path` は、<strong>その OS の一時フォルダーのパス</strong>を返します。Windows では `C:\Users\<名前>\AppData\Local\Temp`、Linux では `/tmp` です。

!!! tip "ポイント"
    - 戻り値は、OS が決めた一時フォルダーの絶対パス。実在するフォルダーを指す
    - 環境変数（Windows は `TMP`、`TEMP` など、POSIX は `TMPDIR` など）で場所が変わる
    - フォルダー自体は共有されている。ファイル名がぶつからないよう、自分用のサブフォルダーを作って使う
    - ここに置いたファイルは、自動で消えるとは限らない。使い終わったら、自分で消す

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### temp_directory_path {#temp_directory_path}

<span class="ver ver-17">C++17</span>

```cpp
path temp_directory_path();
path temp_directory_path(std::error_code& ec);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先。渡すと例外を投げない |

引数なしの版は、失敗すると `filesystem_error` を投げます。`ec` を渡す版は、失敗したときに空のパスを返し、`ec` にエラーを入れます。

返されるパスは、実在するフォルダーです。ただし、<strong>誰でも書ける共有の場所</strong>なので、`temp_directory_path() / "save.tmp"` のような決まった名前を使うと、他のプログラムや、同じゲームの別のプロセスと衝突します。自分専用のサブフォルダー（`temp_directory_path() / "MyGame"` など）を作り、その中に置くのが基本です。

名前がぶつからない一時ファイル名が欲しいときは、プロセス番号や乱数、時刻を名前に混ぜます。C++ の標準には、一時ファイルの名前を作る関数がないので、自分で組み立てます。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <print>

int main() {
  namespace fs = std::filesystem;
  fs::path tmp = fs::temp_directory_path();

  std::println("空ではない: {}", !tmp.empty());
  std::println("実在するフォルダー: {}", fs::is_directory(tmp));
  std::println("絶対パス: {}", tmp.is_absolute());

  // 自分専用のサブフォルダーを作って使う
  fs::path work = tmp / "MyGameWork";
  fs::create_directories(work);
  std::println("作業フォルダーを作れた: {}", fs::is_directory(work));
  fs::remove_all(work);   // 使い終わったら消す
}
```

```text title="実行結果"
空ではない: true
実在するフォルダー: true
絶対パス: true
作業フォルダーを作れた: true
```

## ゲームでの使いどころ

ダウンロードしたパッチの一時保存、圧縮ファイルの展開、クラッシュ ダンプの書き出しなど、<strong>消えても困らないデータ</strong>の置き場所に使います。

セーブ データや設定のように、残したいものを置いてはいけません。OS やクリーナー ソフトが、一時フォルダーを掃除することがあるからです。残したい物は、ユーザー データ用のフォルダー（Windows なら `%APPDATA%` や `Saved Games`）に置きます。

## よくあるミス

??? failure "決まった名前のファイルを直接置いて、他のプロセスとぶつかる"
    `temp / "work.tmp"` のような名前は、複数起動で上書きし合います。プロセス番号や乱数を混ぜるか、自分用のサブフォルダーを作ります。

??? failure "置いたファイルを消さず、一時フォルダーがゲームのデータで一杯になる"
    OS は自動で消すとは限りません。終了時に `remove_all` で片付けます。クラッシュに備えて、起動時に古い作業フォルダーを消す処理も入れておくと安心です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`current_path`](current_path.md) | カレント ディレクトリ。一時フォルダーではない |
| [`create_directories`](create_directories.md) | サブフォルダーを作る |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] OS の一時フォルダーを返す
    - [x] 共有の場所なので、サブフォルダーを作って使う
    - [x] 使い終わったら消す

## 関連ページ

- [cpprefjp: std::filesystem::temp_directory_path](https://cpprefjp.github.io/reference/filesystem/temp_directory_path.html)
- [cppreference: std::filesystem::temp_directory_path](https://en.cppreference.com/w/cpp/filesystem/temp_directory_path)
