---
title: std::filesystem::directory_options
summary: "フォルダの走査の動作（権限のないフォルダを飛ばすなど）を指定する型。"
order: 900
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::directory_options

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

フォルダの中身を `directory_iterator` で順に調べるとき、権限のないフォルダに入るとエラーになります。`skip_permission_denied` を指定すると、そのようなフォルダを飛ばして走査を続けられます。

!!! tip "ポイント"
    - `none`: 既定。
    - `skip_permission_denied`: 権限のないフォルダを飛ばす。
    - `follow_directory_symlink`: リンク先のフォルダにも入る。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::filesystem::directory_options {#directory_options}

```cpp
enum class directory_options : unsigned {
  none = 0,
  follow_directory_symlink = 1,
  skip_permission_denied = 2
};
```

- 戻り値: ビットマスク

| 値 | 重要度 | 意味 |
| --- | --- | --- |
| `none` | <span class="rank rank-often">よく使う</span> | デフォルト |
| `skip_permission_denied` | <span class="rank rank-sometimes">たまに</span> | 権限の無いフォルダを飛ばす（エラーにしない） |
| `follow_directory_symlink` | <span class="rank rank-rare">知ってるだけ</span> | リンク先のフォルダにも入る |


## 実際に動かしてみる

```cpp
#include <filesystem>
#include <print>

namespace fs = std::filesystem;

int main() {
  fs::directory_iterator it(fs::current_path(), fs::directory_options::skip_permission_denied);
  std::println("{}", it != fs::directory_iterator{});
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ゲームのデータフォルダを走査する | `fs::recursive_directory_iterator(dir, fs::directory_options::skip_permission_denied)` |

## よくあるミス

??? failure "`follow_directory_symlink` で無限ループ"
    リンクが循環していると、走査が終わりません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`directory_iterator`](directory_iterator.md) | フォルダを走査する |
| [`recursive_directory_iterator`](recursive_directory_iterator.md) | 再帰的に走査する |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 走査の動作を指定する
    - [x] skip_permission_denied
    - [x] | で組み合わせられる

## 関連ページ

- [cpprefjp: std::filesystem::directory_options](https://cpprefjp.github.io/reference/filesystem/directory_options.html)
- [cppreference: std::filesystem::directory_options](https://en.cppreference.com/w/cpp/filesystem/directory_options)
