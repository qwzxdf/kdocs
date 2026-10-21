---
title: std::fread
summary: "C 由来のバイナリ読み込み。"
order: 3
group: C の入出力（<cstdio>）
tags:
  - 入出力・文字列
---

# std::fread

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cstdio>`
</div>

`std::fread` は、**ファイルから、指定したバイト数のかたまりを読み込む**C 由来の関数です。戻り値が、読めた「個数」です。バイナリファイル（セーブデータ、アセット）を読むのに使います。

!!! tip "ポイント"
    - `fread(buffer, 1 要素のサイズ, 個数, file)` の順。
    - 戻り値は読めた個数。要求より少なければ、終端かエラー。
    - C++ では `ifstream::read`。

## 関数の詳しい説明

### std::fread {#fread}

```cpp
std::size_t fread(void* buffer, std::size_t size, std::size_t count, FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `buffer` | `void*` | 読み込み先 |
| `size` | `size_t` | 1 要素のバイト数 |
| `count` | `size_t` | 要素数 |
| `stream` | `FILE*` | 読み込み元 |

- 戻り値: 読めた要素数
- 計算量: O(入出力量)

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::tmpfile();   // 一時ファイル（閉じると消える）
  int out = 42;
  std::fwrite(&out, sizeof(out), 1, f);
  std::rewind(f);

  int in = 0;
  std::size_t n = std::fread(&in, sizeof(in), 1, f);
  std::println("{} {}", n, in);
  std::fclose(f);
}
```

```text title="実行結果"
1 42
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| バイナリのセーブデータを読む | `std::fread(&data, sizeof(data), 1, f)` |

## よくあるミス

??? failure "サイズと個数を逆にする"
    戻り値の意味が変わります（バイト数でなく個数）。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fwrite`](fwrite.md) | 書き込み |
| [`std::ifstream`](../ifstream.md) | C++ の `read` |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] バイナリを読む
    - [x] 戻り値は読めた個数
    - [x] C++ では ifstream::read

## 関連ページ

- [cpprefjp: std::fread](https://cpprefjp.github.io/reference/cstdio/fread.html)
- [cppreference: std::fread](https://en.cppreference.com/w/cpp/io/c/fread)
