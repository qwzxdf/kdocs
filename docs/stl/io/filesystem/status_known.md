---
title: std::filesystem::status_known
summary: "ファイルの状態を取得できたかを調べる。"
order: 900
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::status_known

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

[`status`](status.md) が返した `file_status` が、「ちゃんとした結果」なのか、「調べられなかった」のかを知りたいことがあります。存在しないことは `not_found` として分かります。でも、権限などで調べられなかったときは、`type()` が `none`（不明）になります。

`std::filesystem::status_known` は、<strong>`file_status` の種類が分かっているか</strong>を返す関数です。`type()` が `none` でなければ `true` です。

!!! tip "ポイント"
    - 引数は `file_status`（パスではない）
    - `not_found` も「分かっている」結果なので `true`。`none` のときだけ `false`
    - `error_code` を渡した `status` の結果を調べるときに使う
    - 存在判定の `exists` は、内部でこの判定を含んでいる

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要と、[`path`](path.md) を先に読んでください。

## 関数の詳しい説明

### status_known {#status_known}

<span class="ver ver-17">C++17</span>

```cpp
bool status_known(file_status s) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `s` | `file_status` | 調べる `file_status` の値 |

`s.type() != file_type::none` と同じです。`file_type::none` は、「状態の取得が失敗した」または「まだ何も入っていない」ことを表す値です。

`not_found` は、「調べた結果、存在しなかった」という情報なので、`status_known` は `true` を返します。この関数が `false` になるのは、権限がなくて調べられなかったとき、`error_code` 付きの `status` が失敗したとき、そして、デフォルト構築しただけの `file_status` です。

`exists(s)` は `status_known(s) && s.type() != not_found` として定義されているので、「存在する」と「存在しない」と「不明」の 3 つを区別するときに、この関数を組み合わせます。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("a.txt") << "x";

  // 存在するファイル: 種類が分かっている
  std::println("a.txt: {}", fs::status_known(fs::status("a.txt")));

  // 存在しないファイル: 「存在しない」と分かっているので true
  fs::file_status none = fs::status("missing.txt");
  std::println("missing.txt: 分かっている={} 存在する={}", fs::status_known(none), fs::exists(none));

  // 何も入っていない file_status: 不明
  fs::file_status blank;
  std::println("空の file_status: {}", fs::status_known(blank));
}
```

```text title="実行結果"
a.txt: true
missing.txt: 分かっている=true 存在する=false
空の file_status: false
```

## ゲームでの使いどころ

`error_code` を使って例外を避けるコードで、エラーの原因を分けて処理するときに使います。「存在しない」は正常な結果として扱い、「調べられなかった」だけを警告に回す、という分岐ができます。

ふつうのゲーム コードでは、`exists` や `is_regular_file` で済むので、直接使う機会は多くありません。

## よくあるミス

??? failure "`status_known` を「存在するか」の意味で使う"
    存在しなくても `true` です。存在判定は `exists` です。

??? failure "パスを渡そうとして、コンパイル エラー"
    引数は `file_status` です。`status_known(fs::status(path))` の形で使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`exists`](exists.md) | 存在するかを調べる。内部でこの判定を使う |
| [`status`](status.md) | `file_status` を取得する関数 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `file_status` の種類が分かっているか
    - [x] `not_found` でも `true`
    - [x] `none` のときだけ `false`

## 関連ページ

- [cpprefjp: std::filesystem::status_known](https://cpprefjp.github.io/reference/filesystem/status_known.html)
- [cppreference: std::filesystem::status_known](https://en.cppreference.com/w/cpp/filesystem/status_known)
