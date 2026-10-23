---
title: std::filesystem::remove_all
summary: "フォルダを中身ごと、まとめて消す。"
order: 9
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::remove_all

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

キャッシュフォルダを中身ごと掃除したい、一時フォルダを丸ごと消したい。`std::filesystem::remove_all` は、フォルダを中身ごと、まとめて消す関数です。取り消せないので、パスを間違えると、大事なデータを失います。戻り値は、消した項目の個数です。

!!! tip "ポイント"
    - 戻り値は消した個数。
    - 誤ったパスを渡すと大惨事になる。事前に確認する。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### remove_all {#remove_all}

```cpp
std::uintmax_t remove_all(const path& p);
```

- フォルダを**中身ごと**消します。戻り値は消したファイル・フォルダの数

!!! warning
    パスを間違えると大事なフォルダを消してしまいます。空のパスや `"/"`、`".."` を渡さないよう、使う前に確認します。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  fs::create_directories("ra_demo/sub");
  std::ofstream("ra_demo/sub/x.txt") << "x";
  std::println("{}", fs::remove_all("ra_demo"));   // x.txt、sub、ra_demo の 3 つ
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

キャッシュや一時フォルダの掃除に使います。ゲームの終了時に、`fs::remove_all(temp_dir)` で、実行中に作った一時ファイルを片付けます。

パスは必ず確かめてから渡します。変数が空文字列やルートになっていると、広い範囲が消えかねません。消す前に、パスの先頭が、想定したフォルダの下にあるかを検査します。

ゴミ箱へは移動せず、完全に削除されます。ユーザーのデータを消す操作は、確認のダイアログを必ず出します。

## よくあるミス

??? failure "パスが空・ルートになっている"
    空のパスや、組み立てに失敗したパスで、意図しない場所を消す事故が起きます。必ずパスを確認します。

??? failure "パスが空やルートになっていて、広範囲を消す"
    変数の中身が想定と違うと、大変な被害になります。消す前に、パスが、想定したフォルダの下にあることを確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`remove`](remove.md) | 1 つだけ |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 中身ごと消す
    - [x] 取り消せない
    - [x] パスを必ず確認

## 関連ページ

- [cpprefjp: std::filesystem::remove_all](https://cpprefjp.github.io/reference/filesystem/remove_all.html)
- [cppreference: std::filesystem::remove_all](https://en.cppreference.com/w/cpp/filesystem/remove_all)
