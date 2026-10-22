---
title: std::strpbrk
summary: "文字列の中から、指定した文字のどれかが最初に現れる位置を探す。"
order: 900
tags:
  - メモリ
---

# std::strpbrk

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstring>`
</div>

区切り文字が複数ある文字列（空白かカンマ）で、最初にどれかが現れる場所を見つけたいとき、`strpbrk` を使います。

!!! tip "ポイント"
    - 終端の `'\0'` を前提にする C 由来の関数。
    - バッファの大きさは自分で確かめる。
    - 新しいコードでは `std::string` / `std::string_view` のほうが安全。

!!! info "このページを読む前に"
    [`<cstring>`](../cstring.md) の概要と [ポインタ](../../../basics/pointer.md) を先に読んでください。

## 関数の詳しい説明

### std::strpbrk {#strpbrk}

```cpp
const char* strpbrk(const char* str, const char* breakset);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | const char* | 探す文字列 |
| `breakset` | const char* | 探す文字の集まり |

- 戻り値: 見つかった位置のポインタ。なければ `nullptr`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  const char* s = "hello world";
  std::println("{}", std::strpbrk(s, " ,") - s);
}
```

```text title="実行結果"
5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 最初の区切り文字の位置 |

## よくあるミス

??? failure "見つからない場合を無視する"
    `nullptr` が返るので、引き算や参照の前に確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strcspn`](strcspn.md) | 長さで返す |
| [`strchr`](strchr.md) | 1 文字だけ探す |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字列の中から、指定した文字のどれかが最初に現れる位置を探す
    - [x] 終端の `'\0'` を前提にする C 由来の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::strpbrk](https://cpprefjp.github.io/reference/cstring/strpbrk.html)
- [cppreference: std::strpbrk](https://en.cppreference.com/w/cpp/string/byte/strpbrk)
