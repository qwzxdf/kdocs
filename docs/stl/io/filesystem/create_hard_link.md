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

同じアセットを、2 つのフォルダーに置きたい。コピーするとディスクを 2 倍使いますし、片方を更新したときに、もう片方との差が出ます。ハード リンクなら、ファイルの実体は 1 つのまま、名前だけを増やせます。

`std::filesystem::create_hard_link` は、<strong>既存のファイルに、もう 1 つの名前（パス）を付ける</strong>関数です。どちらの名前から書き換えても、同じ実体が変わります。

!!! tip "ポイント"
    - 実体が共有されるので、片方への書き込みは、もう片方でも見える
    - どちらの名前を消しても、最後の名前が消えるまで、データは残る
    - 同じボリュームの中でだけ作れる。別のドライブとの間では失敗する
    - フォルダーには、ふつう作れない。ファイル用

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要と、[`path`](path.md) を先に読んでください。

## 関数の詳しい説明

### create_hard_link {#create_hard_link}

<span class="ver ver-17">C++17</span>

```cpp
void create_hard_link(const path& target, const path& link);
void create_hard_link(const path& target, const path& link, std::error_code& ec) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `target` | `const path&` | すでに存在するファイル |
| `link` | `const path&` | 新しく付ける名前。すでに存在するとエラー |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

引数の順番は、<strong>「元」が先、「新しい名前」が後</strong>です。`create_symlink` も同じ順なので、`std::filesystem::copy` のように「コピー元、コピー先」と読めば、覚えやすくなります。

成功すると、`link` と `target` は、ディスク上の同じ実体を指します。[`hard_link_count`](hard_link_count.md) が 2 になり、[`equivalent`](equivalent.md) で比べると `true` になります。

シンボリックリンクと違い、`target` の名前を変えたり、消したりしても、`link` は壊れません。実体がある限り、`link` からそのまま読めます。一方、ファイルシステムが対応していないと失敗します（FAT 系など）。NTFS や ext4 などは対応しています。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <iterator>
#include <print>
#include <string>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("orig.txt") << "hello";

  fs::create_hard_link("orig.txt", "alias.txt");
  std::println("同じ実体: {}", fs::equivalent("orig.txt", "alias.txt"));
  std::println("リンク数: {}", fs::hard_link_count("orig.txt"));

  // 元の名前を消しても、別の名前から読める
  fs::remove("orig.txt");
  std::ifstream in("alias.txt");
  std::string text((std::istreambuf_iterator<char>(in)), {});
  std::println("alias.txt の中身: {}", text);
}
```

```text title="実行結果"
同じ実体: true
リンク数: 2
alias.txt の中身: hello
```

## ゲームでの使いどころ

ビルド システムや、パッケージ作成ツールで、同じアセットを複数のフォルダーに置くときに使います。コピーに比べて、ディスクを使わず、作成も速くなります。

ただし、書き換えを「片方だけに反映したい」場面には向きません。実体が 1 つなので、片方への書き込みが、もう片方にも反映されます。独立した複製が欲しいなら、`copy_file` を使います。

## よくあるミス

??? failure "引数の順番を逆にして、既存の名前を上書きしようとする"
    第 1 引数が元のファイル、第 2 引数が新しい名前です。第 2 引数がすでに存在すると、失敗します。

??? failure "別のドライブに作ろうとして失敗する"
    ハード リンクは、同じボリュームの中でしか作れません。ボリュームをまたぐなら `copy_file` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`create_symlink`](create_symlink.md) | 別の名前を指す参照を作る。実体は共有しない |
| [`copy_file`](copy_file.md) | 独立した複製を作る |
| [`hard_link_count`](hard_link_count.md) | 名前の数を調べる |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 同じ実体に別の名前を付ける
    - [x] 引数は「元、新しい名前」の順
    - [x] 同じボリュームの中だけ

## 関連ページ

- [cpprefjp: std::filesystem::create_hard_link](https://cpprefjp.github.io/reference/filesystem/create_hard_link.html)
- [cppreference: std::filesystem::create_hard_link](https://en.cppreference.com/w/cpp/filesystem/create_hard_link)
