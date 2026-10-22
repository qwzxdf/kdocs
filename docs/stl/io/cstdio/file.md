---
title: FILE
summary: "ファイルを表す型。"
order: 900
tags:
  - 入出力・文字列
---

# FILE

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

`fopen` が返す `FILE*` の、`FILE` 型です。ファイルの位置、バッファ、エラー状態などをまとめて持ちますが、中身は実装依存なので、触れません。ポインタで受け渡して、`fclose` で閉じます。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### FILE {#file}

```cpp
using FILE = /* 実装定義 */;
```

- 戻り値: なし（型）
- 計算量: 入出力の量に比例


## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::tmpfile();
  std::println("{}", f != nullptr);
  std::fclose(f);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | C のファイル API を使うとき |

## よくあるミス

??? failure "`FILE` をコピーする"
    `FILE` はコピーできません。必ず `FILE*` で扱います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fopen`](fopen.md) | 開く |
| [`fclose`](fclose.md) | 閉じる |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルを表す型
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: FILE](https://cpprefjp.github.io/reference/cstdio/file.html)
- [cppreference: FILE](https://en.cppreference.com/w/cpp/io/c/FILE)
