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

セーブデータを書き込んでいる最中にゲームが落ちると、ファイルが壊れます。安全に更新するには、一時ファイルに書いてから、名前を変えて置き換える方法が使われます。`std::filesystem::rename` は、ファイルやフォルダの名前を変える関数です。同じドライブ内なら、別のフォルダへ移動する操作にもなります。

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

セーブデータの安全な更新に使います。`save.tmp` に書き込み、書き込みが終わってから `fs::rename("save.tmp", "save.dat")` で置き換えます。書き込み中に落ちても、元の `save.dat` は無傷で残ります。

ファイルの移動にも使えます。同じドライブ内なら、中身をコピーせず名前だけを変えるので、速くなります。

別のドライブへは、失敗することがあります。その場合は、コピーしてから元を消します。置き換え先に同名のファイルがあると、上書きされるかは環境によります。

## よくあるミス

??? failure "ドライブをまたいで失敗する"
    別のドライブへは `copy_file` + `remove` にします。

??? failure "別のドライブへの移動で失敗する"
    `rename` は、同じドライブ内の移動を想定しています。別のドライブには、`copy_file` してから `remove` します。

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
