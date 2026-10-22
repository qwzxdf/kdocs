---
title: std::filesystem::proximate
summary: "基準のパスから見た相対パスを返す（作れなければ元のパス）。"
order: 900
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::proximate

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

`relative` は、基準から相対パスを作れないとき、空のパスを返します。`proximate` は、その場合に元のパスをそのまま返します。

!!! tip "ポイント"
    - `std::filesystem` の部品。
    - 例外を避けたいときは、`std::error_code` を渡す版を使う。
    - パスは `std::filesystem::path` で扱う。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要と、[`path`](path.md) を先に読んでください。

## 関数の詳しい説明

### std::filesystem::proximate {#proximate}

```cpp
path proximate(const path& p, const path& base = current_path());
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | path | 変換するパス |
| `base` | path | 省略可。基準のパス（既定は現在のフォルダ） |

- 戻り値: 相対パス。作れなければ `p` そのまま
- 計算量: パスの長さに比例


## 実際に動かしてみる

```cpp
#include <filesystem>
#include <print>

namespace fs = std::filesystem;

int main() {
  std::println("{}", fs::proximate("/a/b/c", "/a/b").generic_string());
}
```

```text title="実行結果"
c
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 基準のフォルダからの相対パスを作る |

## よくあるミス

??? failure "`relative` と取り違える"
    作れないときの戻り値が、`relative` は空、`proximate` は元のパスです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`relative`](relative.md) | 作れなければ空 |
| [`weakly_canonical`](weakly_canonical.md) | 正規化 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 基準のパスから見た相対パスを返す（作れなければ元のパス）
    - [x] `std::filesystem` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::filesystem::proximate](https://cpprefjp.github.io/reference/filesystem/proximate.html)
- [cppreference: std::filesystem::proximate](https://en.cppreference.com/w/cpp/filesystem/proximate)
