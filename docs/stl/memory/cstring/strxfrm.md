---
title: std::strxfrm
summary: "ロケールの規則での比較用に、文字列を変換する。"
order: 900
tags:
  - メモリ
---

# std::strxfrm

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstring>`
</div>

`strcoll` を何度も呼ぶより、先に比較用の文字列に変換して、あとは `strcmp` で比べるほうが速いことがあります。`strxfrm` は、その変換をします。

!!! tip "ポイント"
    - 終端の `'\0'` を前提にする C 由来の関数。
    - バッファの大きさは自分で確かめる。
    - 新しいコードでは `std::string` / `std::string_view` のほうが安全。

!!! info "このページを読む前に"
    [`<cstring>`](../cstring.md) の概要と [ポインタ](../../../basics/pointer.md) を先に読んでください。

## 関数の詳しい説明

### std::strxfrm {#strxfrm}

```cpp
std::size_t strxfrm(char* dest, const char* src, std::size_t count);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `dest` | char* | 変換結果の書き込み先（`nullptr` も可） |
| `src` | const char* | 変換する文字列 |
| `count` | size_t | 書き込む最大の長さ |

- 戻り値: 変換後の文字列の長さ（終端を除く）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  std::println("{}", std::strxfrm(nullptr, "abc", 0));
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 大量の文字列を何度も比べる前の準備 |

## よくあるミス

??? failure "バッファの大きさを決めずに呼ぶ"
    まず `dest = nullptr, count = 0` で必要な長さを調べてから確保します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strcoll`](strcoll.md) | 直接比べる |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ロケールの規則での比較用に文字列を変換する
    - [x] 終端の `'\0'` を前提にする C 由来の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::strxfrm](https://cpprefjp.github.io/reference/cstring/strxfrm.html)
- [cppreference: std::strxfrm](https://en.cppreference.com/w/cpp/string/byte/strxfrm)
