---
title: std::filesystem::permissions
summary: "ファイルの権限（読み書きの許可）を取得・変更する。"
order: 26
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::permissions

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

セーブ データを読み取り専用にして、誤った上書きを防ぎたい。スクリプトに実行権限を付けたい。ファイルの権限を変更するのが `std::filesystem::permissions` です。

!!! tip "ポイント"
    - `permissions(パス, 権限, オプション)`。権限は [`perms`](perms.md) のビットの組み合わせ
    - オプションで、置き換え（`replace`）、追加（`add`）、削除（`remove`）を選ぶ。省略は置き換え
    - Windows では、読み取り専用かどうかだけが反映される
    - シンボリックリンクは、既定で指し先を変える。リンク自体は `nofollow`

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### permissions {#permissions}

<span class="ver ver-17">C++17</span>

```cpp
void permissions(const path& p, perms prms, perm_options opts = perm_options::replace);
void permissions(const path& p, perms prms, std::error_code& ec) noexcept;
void permissions(const path& p, perms prms, perm_options opts, std::error_code& ec);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 権限を変えるファイルまたはフォルダー |
| `prms` | [`perms`](perms.md) | 設定するビット |
| `opts` | [`perm_options`](perm_options.md) | `replace`（全部を置き換え）、`add`（追加）、`remove`（削除）。`nofollow` を足せる |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

最も使うのは、`add` と `remove` です。`replace` は、渡したビットで権限をまるごと置き換えるので、書き込み権限を残したいのに、`prms` に入れ忘れると、読み取り専用になります。

<strong>Windows では、書き込みのビット 3 つ（`owner_write`、`group_write`、`others_write`）を全部外したときだけ、読み取り専用属性になります</strong>。1 つだけ外しても、変化しません。読み取り専用のファイルは、`remove` で消せないことがあるので、消す前に `add` で書き込みを戻します。

POSIX では、持ち主以外が権限を変更しようとすると、失敗します。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  using fs::perms;
  const perms all_write = perms::owner_write | perms::group_write | perms::others_write;

  std::ofstream("save.dat") << "x";

  // 書き込みを全部外して、読み取り専用にする
  fs::permissions("save.dat", all_write, fs::perm_options::remove);
  bool writable = (fs::status("save.dat").permissions() & perms::owner_write) != perms::none;
  std::println("書き込める: {}", writable);

  // 元に戻す
  fs::permissions("save.dat", all_write, fs::perm_options::add);
  writable = (fs::status("save.dat").permissions() & perms::owner_write) != perms::none;
  std::println("戻した後: {}", writable);
}
```

```text title="実行結果"
書き込める: false
戻した後: true
```

## ゲームでの使いどころ

完成したセーブ データを読み取り専用にして、誤って上書きしないようにする、MOD が配布データを書き換えないようにする、といった場面で使います。

バージョン管理から取り出したファイルが読み取り専用で、更新や削除ができない、というトラブルでも、`add` で書き込みを戻す処理が役に立ちます。

## よくあるミス

??? failure "書き込みのビットを 1 つだけ外して、Windows で変化しない"
    3 つとも外します。

??? failure "`replace` で権限をまるごと上書きして、意図しない権限になる"
    一部だけ変えたいなら、`add` か `remove` を指定します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`perms`](perms.md) | 権限のビットの定義 |
| [`perm_options`](perm_options.md) | この関数の動きを決めるフラグ |
| [`status`](status.md) | 今の権限を調べる |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルの権限を変更する
    - [x] 一部だけ変えるなら `add` / `remove`
    - [x] Windows は書き込みビット 3 つが全部外れたときだけ読み取り専用

## 関連ページ

- [cpprefjp: std::filesystem::permissions](https://cpprefjp.github.io/reference/filesystem/permissions.html)
- [cppreference: std::filesystem::permissions](https://en.cppreference.com/w/cpp/filesystem/permissions)
