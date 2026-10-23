---
title: std::fopen
summary: "C 由来のファイルを開く関数。"
order: 2
group: C の入出力（<cstdio>）
tags:
  - 入出力・文字列
---

# std::fopen

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cstdio>`
</div>

`std::fopen` は、**ファイルを開いて `FILE*` を返す**C 由来の関数です。開けなかったときは `nullptr` を返します。使い終わったら `fclose` で閉じる必要があります。C++ では `std::ifstream` / `std::ofstream` が、閉じ忘れの心配がないので、普通はそちらを使います。

!!! tip "ポイント"
    - モードは `"r"`（読む）、`"w"`（書く）、`"a"`（追記）、`"rb"` / `"wb"`（バイナリ）。
    - 開けなかったら `nullptr`。必ず確認する。
    - 閉じ忘れると、ファイルが読み書きできないままになる。

!!! info "このページを読む前に"
    - [STL](../../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### std::fopen {#fopen}

```cpp
FILE* fopen(const char* filename, const char* mode);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `filename` | `const char*` | ファイル名 |
| `mode` | `const char*` | 開き方（`"r"`、`"wb"` など） |

- 戻り値: `FILE*`（開けなければ `nullptr`）
- 計算量: O(入出力量)

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::fopen("this_file_does_not_exist.bin", "rb");
  std::println("{}", f == nullptr);
  if (f) {
    std::fclose(f);
  }
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| C のライブラリが FILE* を要求するとき | `std::fopen` + `std::fclose` |

## よくあるミス

??? failure "fclose を忘れる"
    `unique_ptr<FILE, decltype(&fclose)>` で自動に閉じます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ifstream`](../ifstream.md) | C++ の読み込み |
| [`std::ofstream`](../ofstream.md) | C++ の書き込み |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] C 由来のファイルを開く
    - [x] 開けなければ nullptr
    - [x] fclose で閉じる

## 関連ページ

- [cpprefjp: std::fopen](https://cpprefjp.github.io/reference/cstdio/fopen.html)
- [cppreference: std::fopen](https://en.cppreference.com/w/cpp/io/c/fopen)
