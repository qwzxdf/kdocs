---
title: std::filesystem::perms
summary: "ファイルの権限（読み・書き・実行）を表すビットマスク型。"
order: 900
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::perms

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

ファイルの「読める」「書ける」「実行できる」は、誰に対して許すのかまで含めて、9 個のスイッチで表せます。持ち主、同じグループの人、それ以外の人の 3 者にそれぞれ読み・書き・実行の 3 つです。Unix 系の OS が長年使っている、この考え方を表したのが `std::filesystem::perms` です。

<strong>1 つの権限が 1 つのビット</strong>になっている列挙型で、`|` で組み合わせ `&` で取り出します。

!!! tip "ポイント"
    - `owner_read`、`group_write`、`others_exec` のように「誰が」「何を」の 9 通りが基本
    - `owner_all`、`group_all`、`others_all`、`all` はまとめた値
    - `|` で組み合わせ `&` で取り出す。結果も `perms` 型なので `none` と比べて判定する
    - Windows では実質的に「読み取り専用か」だけ。細かい権限は反映されない

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要と[`path`](path.md) を先に読んでください。

## 関数の詳しい説明

### perms {#perms}

<span class="ver ver-17">C++17</span>

```cpp
enum class perms : unsigned {
  none = 0,
  owner_read = 0400,  owner_write = 0200,  owner_exec = 0100,  owner_all = 0700,
  group_read = 040,   group_write = 020,   group_exec = 010,   group_all = 070,
  others_read = 04,   others_write = 02,   others_exec = 01,   others_all = 07,
  all = 0777,
  set_uid = 04000,    set_gid = 02000,     sticky_bit = 01000,
  mask = 07777,
  unknown = 0xFFFF
};
```

値は 8 進数で `chmod` コマンドの数字と同じです。`0644` なら持ち主は読み書き他は読むだけという意味で、`owner_read | owner_write | group_read | others_read` になります。

`none` は「権限が 1 つもない」、`unknown` は「権限が取得できなかった」ことを表します。この 2 つは別物で `unknown` と `&` を取ると意味のない値になるので、先に `status_known` や `permissions() != unknown` を確かめます。

`set_uid`、`set_gid`、`sticky_bit` は Unix 固有の特別なビットで、Windows では意味を持ちません。

`enum class` なので `|` や `&` は標準が演算子を用意しています。ただし結果が `perms` 型のため `if (st.permissions() & fs::perms::owner_read)` とは書けず `!= fs::perms::none` と比べます。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <print>

int main() {
  namespace fs = std::filesystem;
  using fs::perms;

  // 0644: 持ち主は読み書き、他の人は読むだけ
  perms p = perms::owner_read | perms::owner_write | perms::group_read | perms::others_read;
  std::println("8 進数: {:o}", static_cast<unsigned>(p));

  // 取り出して判定する
  bool owner_can_write = (p & perms::owner_write) != perms::none;
  bool others_can_write = (p & perms::others_write) != perms::none;
  std::println("持ち主が書ける: {}", owner_can_write);
  std::println("他の人が書ける: {}", others_can_write);

  // まとめた値
  std::println("all: {:o}", static_cast<unsigned>(perms::all));
  std::println("owner_all: {:o}", static_cast<unsigned>(perms::owner_all));
}
```

```text title="実行結果"
8 進数: 644
持ち主が書ける: true
他の人が書ける: false
all: 777
owner_all: 700
```

## ゲームでの使いどころ

ファイルの保存先に書き込めるかの判定やセーブ データを読み取り専用にして誤った上書きを防ぐ場面で使います。`permissions` 関数にこの値を渡して権限を変更します。

Windows 中心のゲームでは読み取り専用にするかどうかだけを意識します。書き込みのビット 3 つ（`owner_write | group_write | others_write`）をまとめて外すと Windows では読み取り専用属性になります。

## よくあるミス

??? failure "`if (p & perms::owner_read)` と書いて、コンパイル エラー"
    `perms` は `enum class` なので `bool` に変換できません。`(p & perms::owner_read) != perms::none` と比べます。

??? failure "Windows で `owner_write` だけを外して、読み取り専用にならない"
    Windows は書き込みのビット 3 つを全部外したときだけ読み取り専用として扱います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`permissions`](permissions.md) | 権限を変更する関数 |
| [`perm_options`](perm_options.md) | `permissions` の動かし方（追加、削除、置き換え）を選ぶ |
| [`file_status`](file_status.md) | `permissions()` でこの型の現在値を返す |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 権限を 1 ビットずつ表す列挙型
    - [x] `|` で組み合わせ `& ... != none` で判定
    - [x] Windows は書き込みの有無が中心

## 関連ページ

- [cpprefjp: std::filesystem::perms](https://cpprefjp.github.io/reference/filesystem/perms.html)
- [cppreference: std::filesystem::perms](https://en.cppreference.com/w/cpp/filesystem/perms)
