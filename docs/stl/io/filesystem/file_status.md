---
title: std::filesystem::file_status
summary: "ファイルの種類と権限を持つクラス。"
order: 900
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::file_status

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

ファイルについて知りたい情報は、種類（通常のファイル、フォルダー、リンク…）と、権限（読める、書ける…）の 2 つに大きく分かれます。この 2 つをひとまとめにして持つのが、`std::filesystem::file_status` です。[`status`](status.md) や [`symlink_status`](symlink_status.md) の戻り値であり、[`directory_entry`](directory_entry.md) からも取り出せます。

!!! tip "ポイント"
    - `type()` で [`file_type`](file_type.md)、`permissions()` で [`perms`](perms.md) を読む
    - `status` や `symlink_status` の戻り値として手に入る。自分で作ることはあまりない
    - コピーが軽い小さな値型。引数は値渡しでよい
    - `exists`、`is_directory` などの補助関数は、`file_status` を直接受け取る版もある

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要と、[`path`](path.md) を先に読んでください。

## 関数の詳しい説明

### file_status {#file_status}

<span class="ver ver-17">C++17</span>

```cpp
class file_status {
 public:
  explicit file_status(file_type ft = file_type::none, perms prms = perms::unknown) noexcept;

  file_type type() const noexcept;
  perms permissions() const noexcept;

  void type(file_type ft) noexcept;
  void permissions(perms prms) noexcept;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ft` | `file_type` | ファイルの種類。省略すると `none` |
| `prms` | `perms` | 権限。省略すると `unknown` |

`type()` は、`regular`（通常のファイル）、`directory`、`symlink`、`not_found`、`none` などを返します。`permissions()` は、`owner_read`、`owner_write` などのビットの組み合わせです。

Windows では、POSIX ほど細かい権限がないため、読み取り専用かどうかを中心に、ほぼ全員に同じ権限が付いた値になります。権限の細かさは OS に依存すると考えます。

デフォルト構築した値は、種類が `none`、権限が `unknown` で、[`status_known`](status_known.md) が `false` になります。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("hero.dat") << "x";

  fs::file_status st = fs::status("hero.dat");
  std::println("通常のファイル: {}", st.type() == fs::file_type::regular);

  // 権限ビットを調べる
  bool can_read = (st.permissions() & fs::perms::owner_read) != fs::perms::none;
  std::println("所有者が読める: {}", can_read);

  // 自分で作ることもできる
  fs::file_status custom(fs::file_type::directory, fs::perms::owner_all);
  std::println("directory: {}", custom.type() == fs::file_type::directory);
  custom.type(fs::file_type::regular);
  std::println("変更後 regular: {}", custom.type() == fs::file_type::regular);
}
```

```text title="実行結果"
通常のファイル: true
所有者が読める: true
directory: true
変更後 regular: true
```

## ゲームでの使いどころ

ファイルを走査するコードで、種類と権限をまとめて受け取って判定するときに使います。ゲームでは、MOD フォルダーのスキャンなどで、読み取れるふつうのファイルだけを対象にする、といった場面で出てきます。

1 つのファイルに対して種類を何度も調べるなら、`status` の戻り値を変数に取っておいて、`fs::is_regular_file(st)`、`fs::is_directory(st)` のように使い回します。呼ぶたびにファイルシステムへ問い合わせる無駄が省けます。

## よくあるミス

??? failure "権限のビットを `&` だけで判定して、型エラーになる"
    `perms` は列挙型のビット フラグで、`&` の結果は `perms` です。`!= fs::perms::none` と比べて判定します。

??? failure "Windows でも POSIX と同じ細かい権限が取れると思う"
    Windows では、読み取り専用かどうかが中心です。権限のコードを OS をまたいで共有するときは、細かい差に頼りません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`status`](status.md) | この型を返す関数 |
| [`file_type`](file_type.md) | 種類を表す列挙型 |
| [`perms`](perms.md) | 権限を表す列挙型 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 種類と権限をまとめた値
    - [x] `type()` と `permissions()` で読む
    - [x] `status` の結果を使い回す

## 関連ページ

- [cpprefjp: std::filesystem::file_status](https://cpprefjp.github.io/reference/filesystem/file_status.html)
- [cppreference: std::filesystem::file_status](https://en.cppreference.com/w/cpp/filesystem/file_status)
