---
title: std::filesystem::rename
summary: "ファイルやフォルダの名前を変える（移動もできる）。"
order: 10
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::rename

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

`std::filesystem::rename` は、**ファイルやフォルダの名前を変える**関数です。同じドライブ内なら、別のフォルダへ**移動**することにもなります。セーブデータを安全に更新するとき、一時ファイルに書いてから `rename` で入れ替える、という使い方が定番です。

!!! tip "ポイント"
    - 同じドライブ内の移動は速い。別のドライブへは失敗することがある（コピーして消す）。
    - すでに同名のファイルがあると、上書きされる（環境による）。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### rename {#rename}

```cpp
void rename(const path& old_p, const path& new_p);
void rename(const path& old_p, const path& new_p, std::error_code& ec) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `old_p` | `const path&` | 元のパス |
| `new_p` | `const path&` | 新しいパス（別のフォルダなら移動になる） |

- `new_p` にファイルがあると**上書き**されます（壊れない保存に使える。[ファイル入出力](../../../basics/file-io.md#壊れない保存一時ファイル--rename)）

```cpp
#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("slot.tmp") << "new data";
  fs::rename("slot.tmp", "slot.dat");  // 書き終わってから置き換える
  std::println("{} {}", fs::exists("slot.tmp"), fs::exists("slot.dat"));
  fs::remove("slot.dat");
  std::println("{}", fs::exists("slot.dat"));
}
```

```text title="実行結果"
false true
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| セーブの安全な更新 | `tmp` に書いてから `rename` |

## よくあるミス

??? failure "ドライブをまたいで失敗する"
    別のドライブへは `copy_file` + `remove` にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`copy_file`](copy_file.md) | コピー |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 名前を変える・移動する
    - [x] 一時ファイル → rename でセーブ
    - [x] ドライブをまたぐと失敗しうる

## 関連ページ

- [cpprefjp: std::filesystem::rename](https://cpprefjp.github.io/reference/filesystem/rename.html)
- [cppreference: std::filesystem::rename](https://en.cppreference.com/w/cpp/filesystem/rename)
