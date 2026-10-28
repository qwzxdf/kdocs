---
title: std::filesystem::perm_options
summary: "permissions で権限をどう変更するか（置き換え・追加・削除）を指定する。"
order: 900
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::perm_options

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

権限を変更するとき、「この権限だけを追加したい」「この権限だけを外したい」と、「全部をこれに置き換えたい」は、別の操作です。`std::filesystem::perm_options` は、[`permissions`](permissions.md) に、どちらの動きをするかを伝えるフラグです。

!!! tip "ポイント"
    - `replace`（置き換え）、`add`（追加）、`remove`（削除）のどれか 1 つを選ぶ
    - `nofollow` を足すと、シンボリックリンク自体の権限を変える
    - `replace` は、指定しなかったビットを全部外す
    - 省略すると `replace`

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要と、[`path`](path.md) を先に読んでください。

## 関数の詳しい説明

### perm_options {#perm_options}

<span class="ver ver-17">C++17</span>

```cpp
enum class perm_options : unsigned {
  replace  = 0x1,
  add      = 0x2,
  remove   = 0x4,
  nofollow = 0x8
};
```

| 値 | 意味 |
| --- | --- |
| `replace` | 渡した `perms` で、権限をまるごと置き換える |
| `add` | 今の権限に、渡した `perms` のビットを足す |
| `remove` | 今の権限から、渡した `perms` のビットを外す |
| `nofollow` | シンボリックリンクをたどらず、リンク自体を対象にする |

`replace`、`add`、`remove` は、<strong>どれか 1 つだけ</strong>指定します。2 つ以上、または 0 個だと、`permissions` の動作は未定義です。省略したときの既定値は `replace` です。

`nofollow` は、これらのどれかと組み合わせて、`add | nofollow` のように使います。ただし、多くの環境では、リンク自体の権限を変更する方法がなく、無視されるか失敗します。

`replace` は便利ですが、渡したビット以外が全部消えます。`perms::owner_read` だけを渡して `replace` すると、書き込みも実行も外れ、読み取り専用で実行もできないファイルになります。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  using fs::perms;
  const perms w = perms::owner_write | perms::group_write | perms::others_write;
  std::ofstream("a.dat") << "x";

  auto can_write = [] { return (fs::status("a.dat").permissions() & perms::owner_write) != perms::none; };

  fs::permissions("a.dat", w, fs::perm_options::remove);
  std::println("remove の後: {}", can_write());

  fs::permissions("a.dat", w, fs::perm_options::add);
  std::println("add の後: {}", can_write());

  // replace: 渡したビット以外は全部外れる（読み取りだけにする）
  fs::permissions("a.dat", perms::owner_read | perms::group_read | perms::others_read, fs::perm_options::replace);
  std::println("replace の後: {}", can_write());

  fs::permissions("a.dat", w, fs::perm_options::add);   // 消せるように戻す
}
```

```text title="実行結果"
remove の後: false
add の後: true
replace の後: false
```

## ゲームでの使いどころ

`permissions` を呼ぶときに、ほぼ毎回指定します。読み取り専用にする（`remove` で書き込みを外す）、元に戻す（`add` で書き込みを足す）、という 2 つの操作が、ゲームのツール類で最もよく使われる組み合わせです。

## よくあるミス

??? failure "`replace` のつもりで、`add` を使って権限が残る"
    足すだけなので、既存のビットは残ります。

??? failure "`replace` を省略して、意図せず全部の権限が置き換わる"
    既定は `replace` です。一部だけ変えたいなら、`add` か `remove` を明示します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`permissions`](permissions.md) | この列挙型を受け取る関数 |
| [`perms`](perms.md) | 権限のビットの定義 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 権限の変更の仕方を選ぶフラグ
    - [x] `replace` `add` `remove` のどれか 1 つ
    - [x] 省略は `replace`

## 関連ページ

- [cpprefjp: std::filesystem::perm_options](https://cpprefjp.github.io/reference/filesystem/perm_options.html)
- [cppreference: std::filesystem::perm_options](https://en.cppreference.com/w/cpp/filesystem/perm_options)
