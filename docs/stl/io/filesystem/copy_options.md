---
title: std::filesystem::copy_options
summary: "copy / copy_file の動作（上書き・再帰など）を指定するビットマスク型。"
order: 900
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::copy_options

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

ファイルをコピーするとき、「すでにあったら上書きするか」「フォルダの中身も全部コピーするか」といった動作を選びたくなります。それを指定するのが `copy_options` で、`fs::copy(from, to, オプション)` の第 3 引数に渡します。`|` で組み合わせられます。

!!! tip "ポイント"
    - `overwrite_existing`: すでにあれば上書き。
    - `recursive`: フォルダの中身も全部コピー。
    - オプションを省略すると、すでにあるとエラー。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::filesystem::copy_options {#copy_options}

```cpp
enum class copy_options : unsigned {
  none = 0,
  skip_existing = 1, overwrite_existing = 2, update_existing = 4,
  recursive = 8,
  copy_symlinks = 16, skip_symlinks = 32,
  directories_only = 64, create_symlinks = 128, create_hard_links = 256
};
```

- 戻り値: ビットマスク

| 値 | 重要度 | 意味 |
| --- | --- | --- |
| `none` | <span class="rank rank-often">よく使う</span> | 何もしない（すでにあるとエラー） |
| `overwrite_existing` | <span class="rank rank-often">よく使う</span> | すでにあれば上書き |
| `recursive` | <span class="rank rank-sometimes">たまに</span> | フォルダの中身も全部コピー |
| `skip_existing` | <span class="rank rank-sometimes">たまに</span> | すでにあれば何もしない |
| `update_existing` | <span class="rank rank-sometimes">たまに</span> | コピー元のほうが新しければ上書き |
| `directories_only` | <span class="rank rank-rare">知ってるだけ</span> | フォルダの構造だけコピー |
| `copy_symlinks` / `skip_symlinks` | <span class="rank rank-rare">知ってるだけ</span> | シンボリックリンクの扱い |
| `create_symlinks` / `create_hard_links` | <span class="rank rank-rare">知ってるだけ</span> | コピーの代わりにリンクを作る |

`|` で組み合わせられます（`recursive | overwrite_existing`）。


## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>

namespace fs = std::filesystem;

int main() {
  fs::path a = fs::temp_directory_path() / "kdocs_co_a.txt";
  fs::path b = fs::temp_directory_path() / "kdocs_co_b.txt";
  std::ofstream(a) << "x";
  std::ofstream(b) << "y";
  fs::copy_file(a, b, fs::copy_options::overwrite_existing);
  std::println("{}", fs::file_size(b));
  fs::remove(a);
  fs::remove(b);
}
```

```text title="実行結果"
1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| セーブデータのフォルダをバックアップ | `fs::copy("saves", "backup", fs::copy_options::recursive | fs::copy_options::overwrite_existing);` |

## よくあるミス

??? failure "省略して上書きを期待する"
    オプションを省略すると、コピー先があるときにエラーになります。`overwrite_existing` を付けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`copy`](copy.md) | コピーする |
| [`copy_file`](copy_file.md) | ファイル 1 つのコピー |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] コピーの動作を指定する
    - [x] | で組み合わせる
    - [x] overwrite_existing / recursive

## 関連ページ

- [cpprefjp: std::filesystem::copy_options](https://cpprefjp.github.io/reference/filesystem/copy_options.html)
- [cppreference: std::filesystem::copy_options](https://en.cppreference.com/w/cpp/filesystem/copy_options)
