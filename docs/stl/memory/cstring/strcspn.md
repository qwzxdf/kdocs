---
title: std::strcspn
summary: "先頭から、指定した文字を含まない部分の長さを返す。"
order: 900
tags:
  - メモリ
---

# std::strcspn

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstring>`
</div>

「最初に区切り文字が現れるまで何文字か」を知りたいとき、`strcspn` を使います。`strspn` の逆で、`reject` の文字が最初に現れる位置までの長さを返します。

!!! tip "ポイント"
    - 終端の `'\0'` を前提にする C 由来の関数。
    - バッファの大きさは自分で確かめる。
    - 新しいコードでは `std::string` / `std::string_view` のほうが安全。

!!! info "このページを読む前に"
    [`<cstring>`](../cstring.md) の概要と [ポインタ](../../../basics/pointer.md) を先に読んでください。

## 関数の詳しい説明

### std::strcspn {#strcspn}

```cpp
std::size_t strcspn(const char* str, const char* reject);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | const char* | 調べる文字列 |
| `reject` | const char* | 現れたら止まる文字の集まり |

- 戻り値: 先頭から続く長さ
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  std::println("{}", std::strcspn("abc123", "0123456789"));
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 最初の数字までの文字数を調べる |

## よくあるミス

??? failure "見つからないときの戻り値"
    見つからなければ、文字列全体の長さ（終端の位置）が返ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strspn`](strspn.md) | 含む文字が続く長さ |
| [`strpbrk`](strpbrk.md) | 位置のポインタを返す |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 先頭から、指定した文字を含まない部分の長さを返す
    - [x] 終端の `'\0'` を前提にする C 由来の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::strcspn](https://cpprefjp.github.io/reference/cstring/strcspn.html)
- [cppreference: std::strcspn](https://en.cppreference.com/w/cpp/string/byte/strcspn)
