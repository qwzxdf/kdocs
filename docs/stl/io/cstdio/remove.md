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

一時ファイルを使い終わったので、消したい。C には、ファイル名を渡すだけで、そのファイルを消す関数があります。それが `std::remove` です。

<strong>ファイルを 1 つ消す</strong>関数で、`<cstdio>` に入っています。名前が `<algorithm>` の `std::remove` と同じなので、混同に注意が要ります。

!!! tip "ポイント"
    - `remove("パス")` で、ファイルを消す。戻り値は、成功なら 0、失敗なら 0 以外
    - `<algorithm>` の `std::remove` とは、別の関数。引数の型で区別される
    - フォルダーは、環境によって消せたり消せなかったりする。フォルダーは `std::filesystem::remove`
    - 開いているファイルを消そうとすると、Windows では失敗する

!!! info "このページを読む前に"
    [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::remove {#remove}

```cpp
int remove(const char* filename);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `filename` | `const char*` | 消すファイルのパス |

成功すれば 0 を返し、失敗すれば 0 以外を返して、`errno` に理由を入れます。典型的な失敗は、ファイルが存在しない（`ENOENT`）、権限がない、他で開かれている、などです。

注意したいのは、同じ名前の関数が 2 つあることです。`<cstdio>` の `std::remove(const char*)` はファイルを消し、`<algorithm>` の `std::remove(first, last, value)` は、コンテナーの要素を後ろへ詰める関数です。引数の数と型が違うので、オーバーロードとして区別されますが、`std::remove(vec.begin(), vec.end(), 3)` を書くつもりで、`cstdio` 側を呼んでしまう、といった混乱は起きえます。

C++17 以降のコードでは、[`std::filesystem::remove`](../filesystem/remove.md) のほうが、`path` を使えて、例外やエラー コードで失敗を調べられます。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::fopen("temp.dat", "w");
  std::fclose(f);                         // 閉じてから消す

  std::println("消せた: {}", std::remove("temp.dat") == 0);
  std::println("もう一度: {}", std::remove("temp.dat") == 0);   // もう無いので失敗
}
```

```text title="実行結果"
消せた: true
もう一度: false
```

## ゲームでの使いどころ

一時ファイルの後片付けに使います。ただし、C++17 が使えるなら、`std::filesystem::remove` のほうが、存在しなくてもエラーにならない（`false` が返る）ので、後片付けに向いています。

C の古いコードや、`FILE*` を中心に書かれたコードを読むと、この `std::remove` が出てきます。

## よくあるミス

??? failure "開いたまま消そうとして、Windows で失敗する"
    `fclose` で閉じてから消します。

??? failure "`<algorithm>` の `std::remove` と取り違える"
    コンテナーの要素を消すつもりで呼ぶと、意図と違う関数が選ばれます。引数を確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::filesystem::remove`](../filesystem/remove.md) | C++17 版。`path` を使い、失敗の扱いも柔軟 |
| [`rename`](rename.md) | 名前を変える |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルを消す
    - [x] 成功は 0
    - [x] C++17 以降は `std::filesystem::remove`

## 関連ページ

- [cpprefjp: std::remove（<cstdio>）](https://cpprefjp.github.io/reference/cstdio/remove.html)
- [cppreference: std::remove（<cstdio>）](https://en.cppreference.com/w/cpp/io/c/remove)
