---
title: std::remove（<cstdio>）
summary: "ファイルを削除する（C の関数）。"
order: 900
tags:
  - 入出力・文字列
---

# std::remove（<cstdio>）

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

`<cstdio>` の `std::remove` は、ファイル名を渡して、ファイルを削除する C の関数です。`<algorithm>` の `std::remove`（要素を後ろへ詰める）とは別物なので、混同しないようにします。C++17 以降では、`std::filesystem::remove` のほうが、フォルダも扱えて、エラーも詳しく分かります。

!!! tip "ポイント"
    - `<algorithm>` の `std::remove` とは別物。
    - 成功すると 0、失敗すると 0 以外。
    - 新しいコードでは `std::filesystem::remove`。

!!! info "このページを読む前に"
    [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::remove（<cstdio>） {#remove}

```cpp
int remove(const char* filename);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `filename` | const char* | 削除するファイルのパス |

- 戻り値: 成功なら 0、失敗なら 0 以外
- 計算量: OS に依存


## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::fopen("kdocs_remove_demo.txt", "w");
  std::fclose(f);
  std::println("{}", std::remove("kdocs_remove_demo.txt"));
}
```

```text title="実行結果"
0
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 一時ファイルを消す | `std::remove("tmp.dat");` |

## よくあるミス

??? failure "`algorithm` の `remove` と混同する"
    `<cstdio>` の `remove` は文字列を受け取るファイル削除、`<algorithm>` の `remove` はイテレータの範囲を受け取る要素の移動です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`filesystem::remove`](../filesystem/remove.md) | 新しい書き方 |
| [`rename`](rename.md) | 名前を変える |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルを削除する C の関数
    - [x] algorithm の remove とは別物
    - [x] 新しいコードは filesystem::remove

## 関連ページ

- [cpprefjp: std::remove（<cstdio>）](https://cpprefjp.github.io/reference/cstdio/remove.html)
- [cppreference: std::remove（<cstdio>）](https://en.cppreference.com/w/cpp/io/c/remove)
