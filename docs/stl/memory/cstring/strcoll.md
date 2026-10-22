---
title: std::strcoll
summary: "ロケールの規則で、2 つの文字列を比べる。"
order: 900
tags:
  - メモリ
---

# std::strcoll

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstring>`
</div>

`strcmp` は文字コードの順で比べます。辞書の順番（五十音、アルファベットの大文字小文字の扱い）は、言語によって違います。`strcoll` は、現在のロケールの規則で比べます。

!!! tip "ポイント"
    - 終端の `'\0'` を前提にする C 由来の関数。
    - バッファの大きさは自分で確かめる。
    - 新しいコードでは `std::string` / `std::string_view` のほうが安全。

!!! info "このページを読む前に"
    [`<cstring>`](../cstring.md) の概要と [ポインタ](../../../basics/pointer.md) を先に読んでください。

## 関数の詳しい説明

### std::strcoll {#strcoll}

```cpp
int strcoll(const char* lhs, const char* rhs);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `lhs, rhs` | const char* | 比べる 2 つの文字列 |

- 戻り値: `lhs < rhs` なら負、等しければ 0、大きければ正
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  std::println("{}", std::strcoll("a", "b") < 0);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 言語ごとの順序で名前を並べる |

## よくあるミス

??? failure "ロケールを設定せずに使う"
    既定の `"C"` ロケールでは `strcmp` と同じ結果です。`std::setlocale` で設定します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strcmp`](strcmp.md) | 文字コード順の比較 |
| [`strxfrm`](strxfrm.md) | 比較用に変換する |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ロケールの規則で、2 つの文字列を比べる
    - [x] 終端の `'\0'` を前提にする C 由来の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::strcoll](https://cpprefjp.github.io/reference/cstring/strcoll.html)
- [cppreference: std::strcoll](https://en.cppreference.com/w/cpp/string/byte/strcoll)
