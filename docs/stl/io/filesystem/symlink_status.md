---
title: std::filesystem::symlink_status
summary: "シンボリックリンクをたどらずに、そのファイル自身の状態を返す。"
order: 900
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::symlink_status

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

[`status`](status.md) は、シンボリックリンクがあると、その指し先の情報を返します。リンクのファイルそのものがどんな状態なのかを知りたいときには、先をたどってしまう `status` は役に立ちません。

`std::filesystem::symlink_status` は、<strong>リンクをたどらずに</strong>、パスそのものの種類と権限を [`file_status`](file_status.md) として返します。

!!! tip "ポイント"
    - `status` と同じ使い方で、リンクだけを「たどらない」
    - パスがリンクなら `type()` が `symlink` になる
    - リンクの先が存在しなくても、リンクがあれば取得できる
    - リンク以外のパスでは、`status` と同じ結果になる

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要と、[`path`](path.md) を先に読んでください。

## 関数の詳しい説明

### symlink_status {#symlink_status}

<span class="ver ver-17">C++17</span>

```cpp
file_status symlink_status(const path& p);
file_status symlink_status(const path& p, std::error_code& ec) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 調べるパス |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

`status` との違いは、パスの最後の部分がシンボリックリンクのときだけです。`status` は先をたどり、`symlink_status` はたどりません。パスの途中にあるリンク（`dir_link/file` の `dir_link` など）は、どちらも通常どおり先をたどって解決されます。

リンクの先が存在しない場合、`status` は `not_found` を返しますが、`symlink_status` は `symlink` を返します。この差が、リンク切れの検出に使えます。

パスが存在しなければ、`status` と同じく、`not_found` が返ります（例外ではありません）。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("plain.txt") << "x";

  // リンクではないパスでは、status と同じ結果
  fs::file_status a = fs::status("plain.txt");
  fs::file_status b = fs::symlink_status("plain.txt");
  std::println("通常のファイルでは同じ: {}", a.type() == b.type());
  std::println("リンクではない: {}", b.type() != fs::file_type::symlink);

  // 存在しないパスは not_found
  std::println("存在しない: {}", fs::symlink_status("missing").type() == fs::file_type::not_found);
}
```

```text title="実行結果"
通常のファイルでは同じ: true
リンクではない: true
存在しない: true
```

## ゲームでの使いどころ

ファイルの走査やコピーのツールで、リンクを実体として扱うか、リンクのまま扱うかを分けるときに使います。ディレクトリ ツリーを再帰的にたどるとき、リンクをたどると、リンクが親を指していた場合に無限ループになります。`symlink_status` でリンクかどうかを見て、たどらないようにします。

`recursive_directory_iterator` は、既定でリンクをたどりません。自分で再帰を書くときに、この関数が必要になります。

## よくあるミス

??? failure "リンク切れを `status` で検出しようとして、普通の「存在しない」と区別できない"
    `status` はどちらも `not_found` です。`symlink_status` が `symlink` で、`status` が `not_found` なら、リンク切れです。

??? failure "自分で再帰してリンクをたどり、無限ループになる"
    フォルダーへのリンクが親を指すと、ぐるぐる回ります。リンクをたどらない設計にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`status`](status.md) | リンクをたどる版 |
| [`is_symlink`](is_symlink.md) | リンクかどうかだけを返す補助関数 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] リンクをたどらない `status`
    - [x] リンクなら `symlink` を返す
    - [x] リンク切れの検出に使える

## 関連ページ

- [cpprefjp: std::filesystem::symlink_status](https://cpprefjp.github.io/reference/filesystem/symlink_status.html)
- [cppreference: std::filesystem::symlink_status](https://en.cppreference.com/w/cpp/filesystem/symlink_status)
