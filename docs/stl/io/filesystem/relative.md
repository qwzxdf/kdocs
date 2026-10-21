---
title: std::filesystem::relative
summary: "基準のフォルダからの、相対パスにする。"
order: 19
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::relative

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

`std::filesystem::relative` は、**あるフォルダを基準にした相対パス**を返す関数です。アセットの絶対パスから、`assets/` 以下の相対パスを取り出す、といった処理に使います。

!!! tip "ポイント"
    - 基準を省略すると、今の作業フォルダ。
    - 基準と共通部分がないと、空のパスになる（ドライブが違うなど）。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### relative {#relative}

```cpp
path relative(const path& p, const path& base = current_path());
```

- `base` から見た `p` の相対パスを返します。エディタでアセットのパスを保存するときに使えます

```cpp
#include <filesystem>
#include <print>

int main() {
  namespace fs = std::filesystem;
  fs::path asset = fs::current_path() / "assets" / "player.png";
  std::println("{}", fs::relative(asset).generic_string());
  std::println("{}", fs::absolute("x.txt").is_absolute());
}
```

```text title="実行結果"
assets/player.png
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 絶対パスから、アセットルートからの相対パスを取る | `fs::relative(full, asset_root)` |

## よくあるミス

??? failure "ドライブが違う"
    Windows で別のドライブ同士は、空のパスになります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`absolute`](absolute.md) | 絶対パスにする |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 基準からの相対パス
    - [x] 基準を省略すると作業フォルダ
    - [x] ドライブ違いは空

## 関連ページ

- [cpprefjp: std::filesystem::relative](https://cpprefjp.github.io/reference/filesystem/relative.html)
- [cppreference: std::filesystem::relative](https://en.cppreference.com/w/cpp/filesystem/relative)
