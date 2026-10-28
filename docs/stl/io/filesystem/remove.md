---
title: std::filesystem::remove
summary: "ファイルか空のフォルダを 1 つ消す。"
order: 8
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::remove

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

一時ファイルを消したい、不要になったセーブデータを削除したい。`std::filesystem::remove` は、ファイルか空のフォルダを 1 つ消す関数です。消せたら `true`、元から無ければ `false` を返します。中身のあるフォルダは消せません。丸ごと消すには `remove_all` を使います。

!!! tip "ポイント"
    - 存在しなくてもエラーにならない（`false`）。
    - 空でないフォルダは消せない（例外）。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### remove {#remove}

```cpp
bool remove(const path& p);
bool remove(const path& p, std::error_code& ec) noexcept;
```

- ファイルか**空の**フォルダを消します。戻り値は消したら `true`、無かったら `false`
- 中身のあるフォルダは消せない（例外）。[`remove_all`](remove_all.md) を使う

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("rm_demo.txt") << "x";
  std::println("{}", fs::remove("rm_demo.txt"));   // 消した
  std::println("{}", fs::remove("rm_demo.txt"));   // もう無い
}
```

```text title="実行結果"
true
false
```

## ゲームでの使いどころ

一時ファイルの後始末に使います。ダウンロードやコピー用の一時ファイルを処理が終わったら `fs::remove(temp)` で消します。

セーブデータのスロットを削除する処理にも使います。ユーザーが誤って押す可能性があるので、確認のダイアログを出してから呼びます。取り消せません。

存在しなくてもエラーにはならず、`false` を返すだけです。空でないフォルダを渡すと例外になるので、フォルダごと消すなら `remove_all` です。

## よくあるミス

??? failure "空でないフォルダを消そうとする"
    `remove_all` を使います。

??? failure "空でないフォルダを消そうとして例外になる"
    `remove` は、中身のあるフォルダを消せません。`remove_all` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`remove_all`](remove_all.md) | 中身ごと消す |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルか空のフォルダを消す
    - [x] 無くてもエラーでない
    - [x] 中身ごとは remove_all

## 関連ページ

- [cpprefjp: std::filesystem::remove](https://cpprefjp.github.io/reference/filesystem/remove.html)
- [cppreference: std::filesystem::remove](https://en.cppreference.com/w/cpp/filesystem/remove)
