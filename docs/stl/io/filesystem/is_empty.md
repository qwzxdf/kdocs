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

`std::filesystem::is_empty` は、**ファイルの大きさが 0 か、またはフォルダの中身が空か**を調べる関数です。空のセーブデータを無視する、空のキャッシュフォルダを掃除する、といった判断に使います。

!!! tip "ポイント"
    - ファイルならサイズ 0、フォルダなら中身なし。
    - 存在しないパスは例外（`error_code` 版なら例外なし）。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::filesystem::is_empty {#is_empty}

```cpp
bool is_empty(const path& p);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 調べるパス |

- 戻り値: 空なら `true`
- 計算量: O(1)

```cpp
#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("empty_demo.txt").close();   // 空のファイルを作る
  std::println("{}", fs::is_empty("empty_demo.txt"));
  fs::remove("empty_demo.txt");
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 空のセーブデータを無視する | `if (fs::is_empty(path)) continue;` |

## よくあるミス

??? failure "存在しないパスで例外"
    `exists` で先に確認するか、`error_code` 版を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`file_size`](file_size.md) | 大きさを取得 |
| [`exists`](exists.md) | 存在確認 |

## コンパイラ対応

C++17 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 空のファイル・フォルダか
    - [x] サイズ 0 / 中身なし
    - [x] 存在しないと例外

## 関連ページ

- [cpprefjp: std::filesystem::is_empty](https://cpprefjp.github.io/reference/filesystem/is_empty.html)
- [cppreference: std::filesystem::is_empty](https://en.cppreference.com/w/cpp/filesystem/is_empty)
