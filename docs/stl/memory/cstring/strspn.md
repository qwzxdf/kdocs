---
title: std::strspn
summary: "先頭から、指定した文字だけが続く長さを返す。"
order: 900
tags:
  - メモリ
---

# std::strspn

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstring>`
</div>

文字列の先頭が、「数字だけ」「英字だけ」など決まった文字の集まりで何文字続くか知りたいことがあります。`strspn` は、先頭から連続して `accept` の文字に含まれる長さを返します。

!!! tip "ポイント"
    - 終端の `'\0'` を前提にする C 由来の関数。
    - バッファの大きさは自分で確かめる。
    - 新しいコードでは `std::string` / `std::string_view` のほうが安全。

!!! info "このページを読む前に"
    [`<cstring>`](../cstring.md) の概要と [ポインタ](../../../basics/pointer.md) を先に読んでください。

## 関数の詳しい説明

### std::strspn {#strspn}

```cpp
std::size_t strspn(const char* str, const char* accept);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | const char* | 調べる文字列 |
| `accept` | const char* | 許す文字の集まり |

- 戻り値: 先頭から続く長さ
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  std::println("{}", std::strspn("abc123", "abc"));
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 入力の先頭の英字の長さを調べる |

## よくあるミス

??? failure "文字列全体を調べた気になる"
    最初に合わない文字が来た時点で止まります。途中の文字は見ません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strcspn`](strcspn.md) | 逆に、含まない文字が続く長さ |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 先頭から、指定した文字だけが続く長さを返す
    - [x] 終端の `'\0'` を前提にする C 由来の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::strspn](https://cpprefjp.github.io/reference/cstring/strspn.html)
- [cppreference: std::strspn](https://en.cppreference.com/w/cpp/string/byte/strspn)
