---
title: std::filesystem::weakly_canonical
summary: "存在しない部分を含むパスも正規化する（canonical の緩い版）。"
order: 29
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::weakly_canonical

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

セーブ データの保存先 `saves/slot1/save.dat` を正規化してログに出したい。でも `slot1` フォルダーも `save.dat` も、まだ作っていない。[`canonical`](canonical.md) は、存在しないパスを渡すと失敗するので、このような場面では使えません。

`std::filesystem::weakly_canonical` は、<strong>パスの前半の「存在する部分」だけを正規化し、残りは文字列の上で整える</strong>関数です。これから作るファイルの場所を、きれいな絶対パスにできます。

!!! tip "ポイント"
    - 存在する最も長い先頭部分に `canonical` を使い、残りは `lexically_normal` で整える
    - 存在しない部分があっても、エラーにならない
    - `..` が存在しない部分の中にあっても、文字列の上で解決される
    - シンボリックリンクの解決は、存在する部分だけ。存在しない部分には効かない

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### weakly_canonical {#weakly_canonical}

<span class="ver ver-17">C++17</span>

```cpp
path weakly_canonical(const path& p);
path weakly_canonical(const path& p, std::error_code& ec);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 正規化するパス。存在しない部分があってもよい |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

動き方は 2 段階です。まず、パスを先頭から調べて、実在する最も長い部分を見つけます。その部分に `canonical` と同じ処理（絶対パス化、`..` の解決、リンクの解決）を行います。残りの、まだ存在しない部分は、文字列の上で `lexically_normal` のように整えて、後ろにつなげます。

そのため、<strong>存在しない部分にあるシンボリックリンクは解決されません</strong>。当たり前ですが、存在しないものはリンクではないからです。

`canonical` が使えない場面（ログ出力、これから作るファイルの重複チェック、保存先が許可された範囲内かの検査）で、代わりに使います。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <print>

int main() {
  namespace fs = std::filesystem;
  fs::create_directory("saves");

  // saves は存在するが、slot1 以降は存在しない
  fs::path p = fs::weakly_canonical("saves/slot1/../slot2/save.dat");
  std::println("絶対パス: {}", p.is_absolute());

  // カレント ディレクトリからの相対にして確かめる
  fs::path rel = fs::relative(p, fs::current_path());
  std::println("{}", rel.generic_string());
}
```

```text title="実行結果"
絶対パス: true
saves/slot2/save.dat
```

## ゲームでの使いどころ

保存先の検査に使います。ユーザーが入力した保存先が、ゲームの保存フォルダーの外に出ていないか（`../../Windows` のような指定）を調べるには、まず `weakly_canonical` で正規化し、保存フォルダーの正規化した結果と、先頭が一致するかを比べます。正規化しないまま文字列で比べると、`..` で簡単にすり抜けられます。

もう 1 つは、ファイルをこれから作るときの、ログの出力です。「どこに書き込むつもりか」を絶対パスで残せます。

## よくあるミス

??? failure "文字列の `..` 処理だけで、安全だと思い込む"
    存在する部分にシンボリックリンクがあると、見た目と実際の場所が違うことがあります。保存先の検査には、`weakly_canonical` で実際の場所に直してから比べます。

??? failure "存在する部分だけが正規化されることを知らない"
    存在しない部分は、大文字小文字の揃え方も、リンクの解決もされません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`canonical`](canonical.md) | 全部が実在している必要がある版 |
| [`absolute`](absolute.md) | 文字列の上で絶対パスにするだけ |

## コンパイラ対応

C++17 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 存在しない部分があってもよい `canonical`
    - [x] 存在する部分だけ実際に解決する
    - [x] 保存先の検査に向く

## 関連ページ

- [cpprefjp: std::filesystem::weakly_canonical](https://cpprefjp.github.io/reference/filesystem/weakly_canonical.html)
- [cppreference: std::filesystem::weakly_canonical](https://en.cppreference.com/w/cpp/filesystem/canonical)
