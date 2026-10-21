---
title: strcmp
summary: "C 文字列どうしを比べる。"
order: 6
group: C の文字列・メモリ関数（<cstring>）
tags:
  - メモリ
---

# strcmp

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <cstring>`
</div>

`strcmp` は、**2 つの C 文字列を辞書順で比べる**関数です。等しければ 0、前が小さければ負、大きければ正を返します。文字列リテラルとの比較で見かけます。

!!! tip "ポイント"
    - 等しいかは `strcmp(a, b) == 0`。**`a == b` はポインターの比較**で、中身ではない。
    - C++ では `std::string` の `==` や `string_view` を使う。

!!! info "このページを読む前に"
    [ポインタ](../../../basics/pointer.md) が分かると読みやすいです。

## 関数の詳しい説明

### strcmp {#strcmp}

```cpp
int strcmp(const char* lhs, const char* rhs);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `lhs`, `rhs` | `const char*` | 比べる 2 つの C 文字列 |

- 戻り値: 等しければ 0、`lhs` が辞書順で前なら負、後ろなら正
- <strong>`==` で比べてはいけません。</strong> `const char*` の `==` は、**文字列の中身ではなく、アドレスを比べる**からです。`std::string_view(a) == b` と書けば、中身で比べられます

## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  std::println("{} {}", std::strcmp("a", "b") < 0, std::strcmp("a", "a") == 0);
}
```

```text title="実行結果"
true true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| C のAPI が返した名前の比較 | `strcmp(name, "player") == 0` |

## よくあるミス

??? failure "== で比べる"
    `a == b` はアドレスの比較です。`strcmp` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strncmp`](strncmp.md) | 先頭 n 文字だけ |
| [`std::string_view`](../../utilities/string_view.md) | `==` で中身を比べられる |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] C 文字列を比べる
    - [x] 等しければ 0
    - [x] == はポインター比較

## 関連ページ

- [cpprefjp: strcmp](https://cpprefjp.github.io/reference/cstring/strcmp.html)
- [cppreference: strcmp](https://en.cppreference.com/w/cpp/string/byte/strcmp)
