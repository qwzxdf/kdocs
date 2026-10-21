---
title: std::filesystem::current_path
summary: "今の作業フォルダを取得・変更する。"
order: 16
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::current_path

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

`std::filesystem::current_path` は、**プログラムの「今の作業フォルダ」を取得または変更する**関数です。相対パスの基準になります。起動の仕方（ダブルクリックかIDEか）で変わるので注意が必要です。

!!! tip "ポイント"
    - 引数なしで取得、引数ありで変更。
    - 相対パスは、ここを基準に解決される。
    - Visual Studio では、既定が「プロジェクトのフォルダ」になる。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### current_path {#current_path}

```cpp
path current_path();
void current_path(const path& p);
```

- 今の作業フォルダを取得・変更します。相対パスはここから探されます

!!! note "実際は"
    Visual Studio からデバッグ実行すると作業フォルダが exe の場所と違うことがあり、「ファイルが見つからない」原因になります。表示して確かめると早いです。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <print>

int main() {
  namespace fs = std::filesystem;
  auto old = fs::current_path();
  fs::current_path(fs::temp_directory_path());
  std::println("{}", fs::equivalent(fs::current_path(), fs::temp_directory_path()));
  fs::current_path(old);  // 元に戻す
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 起動時にアセットのフォルダへ移動する | `fs::current_path(exe_dir)` |

## よくあるミス

??? failure "作業フォルダが実行ファイルの場所だと思う"
    起動のしかたで変わります。実行ファイルの場所を基準にしたいなら、その場所を取得して使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`absolute`](absolute.md) | 絶対パスにする |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 作業フォルダを取得・変更
    - [x] 相対パスの基準
    - [x] 起動のしかたで変わる

## 関連ページ

- [cpprefjp: std::filesystem::current_path](https://cpprefjp.github.io/reference/filesystem/current_path.html)
- [cppreference: std::filesystem::current_path](https://en.cppreference.com/w/cpp/filesystem/current_path)
