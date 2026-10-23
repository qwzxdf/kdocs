---
title: std::rename
summary: "ファイルの名前を変える（移動もできる）。"
order: 900
tags:
  - 入出力・文字列
---

# std::rename

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

ファイルの名前を変える、または別のフォルダに移動する C の関数です。移動先にすでにファイルがあるときの動作は、環境によって違います（Windows では失敗し、Linux では上書き）。C++17 以降では、`std::filesystem::rename` が、同じ働きでエラーも詳しく分かります。

!!! tip "ポイント"
    - 移動先に同名のファイルがあるときの動作は、環境で違う。
    - 成功すると 0。
    - 新しいコードでは `std::filesystem::rename`。

!!! info "このページを読む前に"
    [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::rename {#rename}

```cpp
int rename(const char* old_filename, const char* new_filename);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `old_filename` | const char* | 元のパス |
| `new_filename` | const char* | 新しいパス |

- 戻り値: 成功なら 0、失敗なら 0 以外
- 計算量: OS に依存


## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::fopen("kdocs_rename_a.txt", "w");
  std::fclose(f);
  std::println("{}", std::rename("kdocs_rename_a.txt", "kdocs_rename_b.txt"));
  std::remove("kdocs_rename_b.txt");
}
```

```text title="実行結果"
0
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 一時ファイルを正式な名前にする | `std::rename("save.tmp", "save.dat");` |

## よくあるミス

??? failure "上書きの挙動を決めつける"
    移動先が存在するときの結果は、実装定義です。先に消すか、`filesystem::rename` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`filesystem::rename`](../filesystem/rename.md) | 新しい書き方 |
| [`remove`](remove.md) | 削除する |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルの名前を変える C の関数
    - [x] 上書きの挙動は環境で違う
    - [x] 新しいコードは filesystem::rename

## 関連ページ

- [cpprefjp: std::rename](https://cpprefjp.github.io/reference/cstdio/rename.html)
- [cppreference: std::rename](https://en.cppreference.com/w/cpp/io/c/rename)
