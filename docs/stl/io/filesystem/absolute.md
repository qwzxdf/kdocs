---
title: std::filesystem::absolute
summary: "相対パスを絶対パスにする。"
order: 18
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::absolute

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

`std::filesystem::absolute` は、**相対パスを、今の作業フォルダを基準にした絶対パスにする**関数です。ファイルがなくても使えます。`.` や `..` は消さずに残ります（消すのは [`canonical`](canonical.md)）。

!!! tip "ポイント"
    - ファイルが存在しなくても使える。
    - `..` を整理したいなら `lexically_normal()` か `canonical`。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### absolute {#absolute}

```cpp
path absolute(const path& p);
```

- 作業フォルダを先頭に付けた絶対パスにします（ファイルが無くてもいい）

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::println("{}", fs::absolute("a/b").is_absolute());
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ログに、読み込んだファイルの絶対パスを出す | `fs::absolute(path)` |

## よくあるミス

??? failure "canonical と取り違える"
    `absolute` は存在確認をしません。シンボリックリンクも解決しません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`canonical`](canonical.md) | 存在確認つきで正規化 |
| [`relative`](relative.md) | 相対パスにする |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 相対 → 絶対
    - [x] 存在しなくてもよい
    - [x] `..` は残る

## 関連ページ

- [cpprefjp: std::filesystem::absolute](https://cpprefjp.github.io/reference/filesystem/absolute.html)
- [cppreference: std::filesystem::absolute](https://en.cppreference.com/w/cpp/filesystem/absolute)
