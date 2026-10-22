---
title: std::filesystem::create_hard_link
summary: "ハードリンク（同じ実体への別の名前）を作る。"
order: 900
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::create_hard_link

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

ファイルの実体は 1 つのまま、名前だけを増やします。どちらの名前から編集しても、同じ中身を指します。最後の名前を消すまで、実体は残ります。

!!! tip "ポイント"
    - `std::filesystem` の部品。
    - 例外を避けたいときは、`std::error_code` を渡す版を使う。
    - パスは `std::filesystem::path` で扱う。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要と、[`path`](path.md) を先に読んでください。

## 関数の詳しい説明

### std::filesystem::create_hard_link {#create_hard_link}

```cpp
void create_hard_link(const path& target, const path& link);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `target` | path | リンク先（既存のファイル） |
| `link` | path | 作るリンクの名前 |

- 戻り値: なし
- 計算量: OS に依存


## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>

namespace fs = std::filesystem;

int main() {
  fs::path a = fs::temp_directory_path() / "kdocs_a.txt";
  fs::path b = fs::temp_directory_path() / "kdocs_b.txt";
  std::ofstream(a) << "x";
  fs::create_hard_link(a, b);
  std::println("{}", fs::exists(b));
  fs::remove(a);
  fs::remove(b);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 同じファイルに別の名前をつける |

## よくあるミス

??? failure "別のドライブにリンクを作る"
    ハードリンクは同じファイルシステム内だけです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`hard_link_count`](hard_link_count.md) | リンクの数 |
| [`create_symlink`](create_symlink.md) | シンボリックリンク |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ハードリンク（同じ実体への別の名前）を作る
    - [x] `std::filesystem` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::filesystem::create_hard_link](https://cpprefjp.github.io/reference/filesystem/create_hard_link.html)
- [cppreference: std::filesystem::create_hard_link](https://en.cppreference.com/w/cpp/filesystem/create_hard_link)
