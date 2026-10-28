---
title: std::filesystem::hard_link_count
summary: "ファイルのハードリンクの数を返す。"
order: 900
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::hard_link_count

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

同じファイルに、複数の名前（パス）を付ける仕組みがあります。ハード リンクです。ファイルの実体は 1 つで、名前だけが複数あり、どの名前を消しても、最後の名前が消えるまで実体は残ります。

`std::filesystem::hard_link_count` は、<strong>その実体を指している名前が、いくつあるか</strong>を返します。ふつうのファイルは、名前が 1 つなので 1 です。

!!! tip "ポイント"
    - 戻り値は、ハード リンクの数（`std::uintmax_t`）。ふつうのファイルは 1
    - `create_hard_link` で名前を増やすと、増える
    - リンクを `remove` すると減る。0 になって初めて、データが解放される
    - FAT など、ハード リンクをサポートしないファイルシステムでは、失敗する場合がある

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要と、[`path`](path.md) を先に読んでください。

## 関数の詳しい説明

### hard_link_count {#hard_link_count}

<span class="ver ver-17">C++17</span>

```cpp
std::uintmax_t hard_link_count(const path& p);
std::uintmax_t hard_link_count(const path& p, std::error_code& ec) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 調べるファイル |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

戻り値は、そのファイルの実体を指している名前（ディレクトリ エントリ）の数です。[`create_hard_link`](create_hard_link.md) で別の名前を付けると 2 になり、どちらかの名前を `remove` すると 1 に戻ります。

フォルダーには、ふつう使いません。フォルダーのリンク数の意味は、ファイルシステムによって違います（POSIX では、サブフォルダーの数に関係する値になる）。

存在しないパスや、ハード リンクの数を取得できないファイルシステムでは、例外（または `ec` のエラー）になります。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("orig.dat") << "data";
  std::println("最初: {}", fs::hard_link_count("orig.dat"));

  fs::create_hard_link("orig.dat", "alias.dat");   // 同じ実体に別の名前を付ける
  std::println("リンク後: {}", fs::hard_link_count("orig.dat"));

  fs::remove("alias.dat");                         // 名前を 1 つ消す
  std::println("名前を消した後: {}", fs::hard_link_count("orig.dat"));
}
```

```text title="実行結果"
最初: 1
リンク後: 2
名前を消した後: 1
```

## ゲームでの使いどころ

ゲームの実行中に使うことはほとんどありません。ビルド ツールやインストーラーが、同じアセットを複数の場所に置くとき、コピーではなくハード リンクにしてディスクを節約する場合があります。`hard_link_count` は、そのような仕組みの検査や、削除の安全確認に使えます。

データを消す前に、「他の名前が残っているか」を知りたい、というツール側の用途が中心です。

## よくあるミス

??? failure "コピーとハード リンクを同じものだと思う"
    ハード リンクは実体を共有します。一方の名前から内容を書き換えると、もう一方の名前でも変わります。独立したコピーが必要なら `copy_file` を使います。

??? failure "別のボリュームにハード リンクを作ろうとして失敗する"
    ハード リンクは、同じボリューム（同じファイルシステム）の中でしか作れません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`create_hard_link`](create_hard_link.md) | ハード リンクを作る |
| [`create_symlink`](create_symlink.md) | 別の名前を指す参照を作る。実体を共有するわけではない |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 実体を指す名前の数を返す
    - [x] ふつうは 1
    - [x] 同じボリュームの中だけで作れる

## 関連ページ

- [cpprefjp: std::filesystem::hard_link_count](https://cpprefjp.github.io/reference/filesystem/hard_link_count.html)
- [cppreference: std::filesystem::hard_link_count](https://en.cppreference.com/w/cpp/filesystem/hard_link_count)
