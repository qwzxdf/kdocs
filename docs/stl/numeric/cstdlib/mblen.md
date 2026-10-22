---
title: std::mblen
summary: "マルチバイト文字の 1 文字目のバイト数を返す。"
order: 900
tags:
  - 数値
---

# std::mblen

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

UTF-8 や Shift_JIS のような可変長の文字列で、「先頭の 1 文字が何バイトか」を知りたいことがあります。`mblen` はそれを返します。ロケールによって結果が変わります。

!!! tip "ポイント"
    - C 由来の関数。
    - 失敗の知らせ方は関数ごとに違う。
    - 新しいコードでは `std::from_chars` や `std::string` が安全。

!!! info "このページを読む前に"
    [`std::atoi`](atoi.md) を先に読んでください。

## 関数の詳しい説明

### std::mblen {#mblen}

```cpp
int mblen(const char* s, std::size_t n);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `s` | const char* | 調べるバイト列 |
| `n` | size_t | 調べる最大のバイト数 |

- 戻り値: 1 文字のバイト数。終端文字なら 0。不正なら -1
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  std::println("{}", std::mblen("A", 1));
}
```

```text title="実行結果"
1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 文字コードの変換（ただし新しいコードは UTF-8 に統一する） |

## よくあるミス

??? failure "ロケールを設定せずに使う"
    既定は `"C"` ロケールで、ASCII しか変換できません。`std::setlocale` で設定します。

## 類似

| 名前 | 違い |
| --- | --- |
| [文字コード](../../../encoding/index.md) | 変換の考え方 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] マルチバイト文字の 1 文字目のバイト数を返す
    - [x] C 由来の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::mblen](https://cpprefjp.github.io/reference/cstdlib/mblen.html)
- [cppreference: std::mblen](https://en.cppreference.com/w/cpp/c/mblen)
