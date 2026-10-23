---
title: std::fwrite
summary: "C 由来のバイナリ書き込み。"
order: 4
group: C の入出力（<cstdio>）
tags:
  - 入出力・文字列
---

# std::fwrite

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cstdio>`
</div>

`std::fwrite` は、**メモリのかたまりをファイルに書き込む**C 由来の関数です。構造体をそのままバイナリで書き出すときに使います。戻り値は書けた個数で、要求より少なければエラーです（ディスクが満杯など）。

!!! tip "ポイント"
    - `fwrite(データ, 1 要素のサイズ, 個数, file)` の順。
    - 構造体を書くときは、パディングや環境依存に注意する。
    - C++ では `ofstream::write`。

!!! info "このページを読む前に"
    - [STL](../../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### std::fwrite {#fwrite}

```cpp
std::size_t fwrite(const void* buffer, std::size_t size, std::size_t count, FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `buffer` | `const void*` | 書き出すデータ |
| `size` | `size_t` | 1 要素のバイト数 |
| `count` | `size_t` | 要素数 |
| `stream` | `FILE*` | 書き出し先 |

- 戻り値: 書けた要素数
- 計算量: O(入出力量)

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::tmpfile();
  int value = 42;
  std::size_t n = std::fwrite(&value, sizeof(value), 1, f);
  std::println("{}", n);
  std::fclose(f);
}
```

```text title="実行結果"
1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| バイナリのセーブデータを書き出す | `std::fwrite(&data, sizeof(data), 1, f)` |

## よくあるミス

??? failure "戻り値を確認しない"
    ディスクが満杯でも気づきません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fread`](fread.md) | 読み込み |
| [`std::ofstream`](../ofstream.md) | C++ の `write` |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] バイナリを書く
    - [x] 戻り値は書けた個数
    - [x] C++ では ofstream::write

## 関連ページ

- [cpprefjp: std::fwrite](https://cpprefjp.github.io/reference/cstdio/fwrite.html)
- [cppreference: std::fwrite](https://en.cppreference.com/w/cpp/io/c/fwrite)
