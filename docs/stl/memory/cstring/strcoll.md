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

`strcmp` は文字コードの順で比べますが、言語によっては、辞書の順が文字コードの順と違います。`std::strcoll(a, b)` は、現在のロケールの辞書順で 2 つの文字列を比べます。戻り値の規則は `strcmp` と同じです。

!!! tip "ポイント"
    - 現在の C のロケール（`setlocale`）の並び順で比べる
    - "C" ロケールでは `strcmp` と同じ
    - 戻り値は、負・0・正
    - 繰り返し比べるなら、`strxfrm` で先に変換しておく

!!! info "このページを読む前に"
    [`<cstring>`](../cstring.md) の概要を先に読んでください。C の文字列は、終端が `'\0'` の `char` の配列です。

## 関数の詳しい説明

### std::strcoll {#strcoll}

```cpp
int strcoll(const char* lhs, const char* rhs);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `lhs`, `rhs` | `const char*` | 比べる文字列 |

ロケールの設定は `setlocale` で行います。既定のままなら "C" ロケールで、文字コードの順です。

日本語の五十音順のような並びは、環境のロケールの対応に左右されます。ゲームでは、読み仮名のデータを別に持って並べることが多いです。

## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  // 起動直後は "C" ロケール: strcmp と同じ
  const bool same = (std::strcoll("apple", "banana") < 0) == (std::strcmp("apple", "banana") < 0);
  std::println("strcmp と同じ向き: {}", same);
  std::println("同じ文字列: {}", std::strcoll("abc", "abc") == 0);
}
```

```text title="実行結果"
strcmp と同じ向き: true
同じ文字列: true
```

## ゲームでの使いどころ

アイテム名の並べ替えなどで、ロケールの辞書順にしたいときに検討します。

## よくあるミス

??? failure "環境のロケールで結果が変わるのを知らない"
    同じプログラムでも、実行する環境で並びが変わります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strcmp`](strcmp.md) | 文字コードの順 |
| [`strxfrm`](strxfrm.md) | 比較用に変換する |
| [`std::collate`](../../io/locale/collate.md) | C++ のロケールの照合 |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## 関連ページ

- [cpprefjp: std::strcoll](https://cpprefjp.github.io/reference/cstring/strcoll.html)
- [cppreference: std::strcoll](https://en.cppreference.com/w/cpp/string/byte/strcoll)
