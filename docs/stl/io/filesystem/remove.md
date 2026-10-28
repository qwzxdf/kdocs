---
title: std::filesystem::remove
summary: "ファイルか空のフォルダを 1 つ消す。"
order: 8
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::remove

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

一時ファイルを使い終わったので消したい。セーブ データを削除したい。ファイルやフォルダーを消す処理は、うっかり使うと大事なデータを失うので、振る舞いをよく知っておきたい関数です。

`std::filesystem::remove` は、<strong>ファイル 1 つ、または空のフォルダー 1 つ</strong>を消します。中身のあるフォルダーは消せません。

!!! tip "ポイント"
    - 消せたら `true`、もともと存在しなかったら `false`（エラーではない）
    - フォルダーは、空のときだけ消せる。中身があるとエラー
    - 中身ごと消すなら `remove_all`
    - シンボリックリンクは、リンクだけを消す。指し先は消さない

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### remove {#remove}

<span class="ver ver-17">C++17</span>

```cpp
bool remove(const path& p);
bool remove(const path& p, std::error_code& ec) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 消すファイルまたは空のフォルダー |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

戻り値は、<strong>実際に消したなら `true`、もともと無かったなら `false`</strong> です。存在しないものを消そうとしても、エラーにはなりません。「消えた状態にする」という目的は達成されているからです。一時ファイルの後片付けのように、あってもなくてもよい物に向きます。

中身のあるフォルダーを渡すと、エラー（例外または `ec`）になります。フォルダーの中身が消える危険のある操作なので、`remove` では許されていません。

Windows では、他のプロセスが開いているファイルは消せません。読み取り専用属性のファイルも、そのままでは消せない場合があります。その場合は、`permissions` で書き込み権限を戻してから消します。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>
#include <system_error>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("temp.txt") << "x";
  fs::create_directories("full/sub");
  fs::create_directory("empty");

  std::println("temp.txt を消した: {}", fs::remove("temp.txt"));
  std::println("もう一度: {}", fs::remove("temp.txt"));       // もう無いので false
  std::println("空のフォルダー: {}", fs::remove("empty"));

  // 中身のあるフォルダーは、消せない
  std::error_code ec;
  fs::remove("full", ec);
  std::println("中身のあるフォルダー: エラー={} 残っている={}", static_cast<bool>(ec), fs::exists("full"));
}
```

```text title="実行結果"
temp.txt を消した: true
もう一度: false
空のフォルダー: true
中身のあるフォルダー: エラー=true 残っている=true
```

## ゲームでの使いどころ

一時ファイルの後片付けに使います。終了時に `remove(tmp)` を呼んでおけば、あってもなくても安全に終わります。セーブ データの削除（「このスロットを消す」）にも使います。

フォルダーごと消すときは `remove_all` を使いますが、これは危険な操作です。パスの組み立てを間違えると、意図しない場所を丸ごと消します。呼ぶ前に、消す対象が自分の作業フォルダーの内側かを、`weakly_canonical` などで確かめるのが安全です。

## よくあるミス

??? failure "中身のあるフォルダーを `remove` で消そうとして失敗する"
    空でないフォルダーは消せません。`remove_all` を使います。

??? failure "存在しないものを消して、エラーになると思い、try-catch を書く"
    存在しないだけなら、エラーではなく `false` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`remove_all`](remove_all.md) | フォルダーを中身ごと消す |
| [`rename`](rename.md) | 名前を変える。ゴミ箱へ移す代わりに使うこともある |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルまたは空のフォルダーを消す
    - [x] 存在しなければ `false`
    - [x] 中身ごとなら `remove_all`

## 関連ページ

- [cpprefjp: std::filesystem::remove](https://cpprefjp.github.io/reference/filesystem/remove.html)
- [cppreference: std::filesystem::remove](https://en.cppreference.com/w/cpp/filesystem/remove)
