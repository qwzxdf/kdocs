---
title: std::filesystem::remove_all
summary: "フォルダを中身ごと、まとめて消す。"
order: 9
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::remove_all

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

一時フォルダーを、中身ごと片付けたい。`remove` は空のフォルダーしか消せないので、中のファイルとサブフォルダーを、先に全部消す必要があります。それを 1 回の呼び出しでやるのが `std::filesystem::remove_all` です。

<strong>ファイルでもフォルダーでも、中身ごと再帰的に消し</strong>、消した数を返します。

!!! tip "ポイント"
    - フォルダーは、中身（サブフォルダーを含む）ごと消す。ファイルなら、そのファイルだけ
    - 戻り値は、消したファイルとフォルダーの合計数。もともと無ければ 0
    - 存在しないことはエラーではない。後片付けに使いやすい
    - 危険な操作。パスが空やルートだと、意図しない範囲を消す

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### remove_all {#remove_all}

<span class="ver ver-17">C++17</span>

```cpp
std::uintmax_t remove_all(const path& p);
std::uintmax_t remove_all(const path& p, std::error_code& ec);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 消すファイルまたはフォルダー |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

戻り値は、<strong>消したものの数</strong>で、`p` 自身も数に入ります。中に 2 つのファイルがあるフォルダーなら 3 です。`p` が存在しなかったときは 0 を返し、エラーにはなりません。失敗したときは、例外（または `ec`）で、`error_code` の版では、戻り値は `static_cast<std::uintmax_t>(-1)` になります。

途中で失敗する場合があります。他のプロセスが開いているファイルや、権限のないファイルがあると、そこで止まり、それまでに消したぶんは戻りません。「全部消すか、何も消さないか」という保証はありません。

この関数の怖さは、<strong>パスを間違えると、広い範囲を消す</strong>ことです。変数が空文字列のまま `root / ""` で呼ぶと、`root` が丸ごと消えます。ユーザーの入力や設定ファイルから作ったパスは、消す前に、想定した場所の内側にあるかを確かめます。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  fs::create_directories("work/sub");
  std::ofstream("work/a.txt") << "a";
  std::ofstream("work/sub/b.txt") << "b";

  // work, work/a.txt, work/sub, work/sub/b.txt の 4 つ
  std::uintmax_t n = fs::remove_all("work");
  std::println("消した数: {}", n);
  std::println("残っている: {}", fs::exists("work"));

  // もう無いので 0。エラーにはならない
  std::println("2 回目: {}", fs::remove_all("work"));
}
```

```text title="実行結果"
消した数: 4
残っている: false
2 回目: 0
```

## ゲームでの使いどころ

一時作業フォルダーの後片付け、ビルドや変換の出力フォルダーの掃除、アンインストールの処理で使います。起動時に、前回のクラッシュで残った作業フォルダーを消す、といった使い方もあります。

呼ぶ前に、`weakly_canonical` で正規化したパスが、自分の作業フォルダーの下にあるかを検査する習慣をつけます。パスの組み立てのバグで、ユーザーの Documents フォルダーが消える、といった事故を避けるためです。

## よくあるミス

??? failure "空のパスや、ルートを渡して、広い範囲を消す"
    消す前に、パスが空でないこと、想定した場所の内側にあることを確かめます。

??? failure "途中で失敗しても、全部消えたと思う"
    開かれているファイルなどで止まります。戻り値と `ec` を確かめ、残りがないかを `exists` で見ます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`remove`](remove.md) | ファイルか空のフォルダー 1 つだけを消す |
| [`directory_iterator`](directory_iterator.md) | 消す前に中身を数える |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 中身ごと再帰的に消す
    - [x] 戻り値は消した数（`p` 自身を含む）
    - [x] パスの確認が命綱

## 関連ページ

- [cpprefjp: std::filesystem::remove_all](https://cpprefjp.github.io/reference/filesystem/remove_all.html)
- [cppreference: std::filesystem::remove_all](https://en.cppreference.com/w/cpp/filesystem/remove_all)
