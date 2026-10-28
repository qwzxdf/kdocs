---
title: std::filesystem::create_directory
summary: "フォルダを 1 階層だけ作る。"
order: 4
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::create_directory

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

セーブ データの保存先 `saves` フォルダーを、初回の起動で作りたい。ファイルを書き込む前に、置き場所のフォルダーが無いと、書き込みは失敗します。

`std::filesystem::create_directory` は、<strong>フォルダーを 1 つ作る</strong>関数です。すでにあっても失敗せず、戻り値で「新しく作ったか」を教えてくれます。

!!! tip "ポイント"
    - 作るのは、最後の 1 階層だけ。途中のフォルダーが無いとエラー
    - すでにフォルダーがあるときは、エラーではなく `false` を返す
    - 途中の階層もまとめて作るなら `create_directories`
    - 同じ名前のファイルがあるときは、エラー

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### create_directory {#create_directory}

<span class="ver ver-17">C++17</span>

```cpp
bool create_directory(const path& p);
bool create_directory(const path& p, std::error_code& ec) noexcept;
bool create_directory(const path& p, const path& existing_p);
bool create_directory(const path& p, const path& existing_p, std::error_code& ec) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 作るフォルダーのパス |
| `existing_p` | `const path&` | 属性を真似る既存のフォルダー。省略すると既定の属性 |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

戻り値は、<strong>新しく作ったら `true`、すでにフォルダーがあって何もしなかったら `false`</strong> です。「あっても大丈夫」という性質のため、起動時の初期化に便利で、`if (!exists) create` と書く必要がありません。

作れない場合は例外（または `ec`）になります。典型的な原因は、親のフォルダーが存在しない、同じ名前のファイルがある、書き込む権限がない、の 3 つです。

`existing_p` を渡す版は、既存のフォルダーと同じ属性（権限など）で、新しいフォルダーを作ります。あまり使いません。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <print>
#include <system_error>

int main() {
  namespace fs = std::filesystem;

  std::println("1 回目: {}", fs::create_directory("saves"));   // 新しく作った
  std::println("2 回目: {}", fs::create_directory("saves"));   // すでにある

  // 途中のフォルダーが無いと、作れない
  std::error_code ec;
  bool r = fs::create_directory("a/b/c", ec);
  std::println("a/b/c: 作った={} エラー={}", r, static_cast<bool>(ec));
}
```

```text title="実行結果"
1 回目: true
2 回目: false
a/b/c: 作った=false エラー=true
```

## ゲームでの使いどころ

起動時の初期化で、セーブ フォルダーやキャッシュ フォルダーを用意するときに使います。1 階層だけなら `create_directory`、`Saved/Profiles/Player1` のように複数の階層がまとめて必要なら、`create_directories` を使います。

戻り値が `true` のときだけ、初期データを書き込む、という使い方もできます。`false` なら、すでにユーザーのデータがあるので、触らない、という分岐です。

## よくあるミス

??? failure "複数階層を `create_directory` で作ろうとして、エラー"
    途中のフォルダーが無いと失敗します。`create_directories` を使います。

??? failure "同じ名前のファイルがあって失敗する"
    フォルダーを作ろうとした名前に、すでにファイルがあるとエラーです。`is_directory` で確かめてから処理を分けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`create_directories`](create_directories.md) | 途中の階層もまとめて作る |
| [`remove`](remove.md) | 空のフォルダーを消す |
| [`is_directory`](is_directory.md) | フォルダーがあるか確かめる |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] フォルダーを 1 階層だけ作る
    - [x] すでにあれば `false`（エラーではない）
    - [x] 複数階層は `create_directories`

## 関連ページ

- [cpprefjp: std::filesystem::create_directory](https://cpprefjp.github.io/reference/filesystem/create_directory.html)
- [cppreference: std::filesystem::create_directory](https://en.cppreference.com/w/cpp/filesystem/create_directory)
