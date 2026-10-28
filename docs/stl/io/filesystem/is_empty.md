---
title: std::filesystem::is_empty
summary: "ファイルが空（サイズ 0）か、フォルダが空かを調べる。"
order: 28
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::is_empty

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

ゲームの起動時に、設定ファイルが空（0 バイト）なら既定値を使いたい。ゴミ箱代わりの一時フォルダーが空なら、削除したい。「ファイルが空か」と「フォルダーが空か」は、別々の関数で調べなくてはなりません。

`std::filesystem::is_empty` は、<strong>ファイルなら 0 バイトか、フォルダーなら中身がないか</strong>を、1 つの関数で調べます。

!!! tip "ポイント"
    - 通常のファイルは、サイズが 0 なら `true`
    - フォルダーは、直下に何も無ければ `true`（サブフォルダーがあれば `false`）
    - パスが存在しないときは、`false` ではなくエラー（例外）
    - フォルダーの中に空のフォルダーしかないときも `false`。深くたどるわけではない

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### is_empty {#is_empty}

<span class="ver ver-17">C++17</span>

```cpp
bool is_empty(const path& p);
bool is_empty(const path& p, std::error_code& ec);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 調べるパス。ふつうのファイルかフォルダー |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

ふつうのファイルには [`file_size`](file_size.md) が 0 かどうか、フォルダーには [`directory_iterator`](directory_iterator.md) の最初の要素が終端かどうか、を調べています。フォルダーでは、全体を数えるわけではなく、最初の 1 件を見るだけなので、中身が多くても速く終わります。

ここで気をつけるのは、<strong>存在しないパスはエラー</strong>になることです。「空ファイルか、存在しないか」を区別したいので、`false` や `true` を返さず、例外（`ec` の版ではエラー）にしています。存在するかどうかが不確かなら、先に `exists` で確かめます。

ふつうのファイルでもフォルダーでもない特殊なファイル（デバイス ファイルなど）に使うと、失敗することがあります。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>
#include <system_error>

int main() {
  namespace fs = std::filesystem;

  std::ofstream("empty.txt");                // 0 バイトのファイル
  std::ofstream("full.txt") << "data";       // 4 バイトのファイル
  fs::create_directory("emptydir");
  fs::create_directories("fulldir/sub");

  std::println("empty.txt: {}", fs::is_empty("empty.txt"));
  std::println("full.txt: {}", fs::is_empty("full.txt"));
  std::println("emptydir: {}", fs::is_empty("emptydir"));
  std::println("fulldir: {}", fs::is_empty("fulldir"));   // sub がある

  std::error_code ec;
  fs::is_empty("missing", ec);
  std::println("存在しない: エラー={}", static_cast<bool>(ec));
}
```

```text title="実行結果"
empty.txt: true
full.txt: false
emptydir: true
fulldir: false
存在しない: エラー=true
```

## ゲームでの使いどころ

クリーンアップ処理で、中身が空になったフォルダーを消すときに使います。アセットを展開したあとに、空のフォルダーだけが残っていることがあります。`is_empty` で空だと確かめてから `remove` します。

設定ファイルやセーブ データが「0 バイトで壊れている」ケースの検出にも使います。クラッシュで書き込みが途中のまま終わると、空のファイルが残ることがあります。そのときは、バックアップから復元するか、既定値で作り直します。

## よくあるミス

??? failure "存在しないパスで例外が出る"
    `false` が返るのではなく、エラーです。`exists` で確かめるか、`error_code` を受け取る版を使います。

??? failure "サブフォルダーだけが入ったフォルダーを、空だと思う"
    サブフォルダーがあれば、中が空でも `false` です。再帰的に調べたいなら、`recursive_directory_iterator` で走査します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`file_size`](file_size.md) | ファイルのバイト数。0 と比べれば、空ファイルの判定になる |
| [`directory_iterator`](directory_iterator.md) | フォルダーの中身を 1 件ずつ見る |

## コンパイラ対応

C++17 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルは 0 バイト、フォルダーは中身なしで `true`
    - [x] 存在しないとエラー
    - [x] フォルダーは最初の 1 件を見るだけ

## 関連ページ

- [cpprefjp: std::filesystem::is_empty](https://cpprefjp.github.io/reference/filesystem/is_empty.html)
- [cppreference: std::filesystem::is_empty](https://en.cppreference.com/w/cpp/filesystem/is_empty)
