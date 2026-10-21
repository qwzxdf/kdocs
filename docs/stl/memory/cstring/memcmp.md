---
title: memcmp
summary: "2 つのメモリを、バイト単位で比べる。"
order: 4
group: C の文字列・メモリ関数（<cstring>）
tags:
  - メモリ
---

# memcmp

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstring>`
</div>

`memcmp` は、**2 つのメモリ領域をバイト単位で比べる**関数です。等しければ 0、違えば正または負を返します。構造体の比較に使うと、**パディング（隙間）の中身まで比べて**しまうので注意が必要です。

!!! tip "ポイント"
    - 等しいかの判定だけなら、`== 0`。
    - 構造体にはパディングがあり、中身が不定。構造体の比較に使うのは危険。
    - 浮動小数点の比較には向かない（`-0.0` と `0.0` が違うと出る）。

!!! info "このページを読む前に"
    [ポインタ](../../../basics/pointer.md) が分かると読みやすいです。

## 関数の詳しい説明

### memcmp {#memcmp}

```cpp
int memcmp(const void* lhs, const void* rhs, std::size_t count);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `lhs`, `rhs` | `const void*` | 比べる 2 つの領域 |
| `count` | `std::size_t` | 比べる**バイト数** |

- 戻り値: 等しければ 0。最初に違うバイトが `lhs` の方が小さければ負、大きければ正（**値の大きさは決まっていない**。符号だけ見る）
- バイトを 1 つずつ比べるだけです。**数値としての大小の比較にはなりません**（リトルエンディアンの `int` では、バイトの順番が逆になるため）
- 構造体の比較に使うのは危険です。**パディング**（隙間のバイト）に不定な値が入っていると、メンバが同じでも「違う」と判定されます。`float` も、`0.0` と `-0.0`、`NaN` で結果が変わります。`operator==`（`= default` でよい）を使います

## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  std::println("{} {}", std::memcmp("abc", "abd", 3) < 0, std::memcmp("abc", "abc", 3) == 0);
}
```

```text title="実行結果"
true true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| バイナリデータの一致確認（ハッシュ値、ID） | `memcmp(a, b, 16) == 0` |

## よくあるミス

??? failure "構造体の比較に使う"
    パディングの値が違うと、見た目が同じでも不一致になります。メンバごとに比べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::equal`](../../algorithms/equal.md) | 型を意識した比較 |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] バイト単位で比べる
    - [x] 等しければ 0
    - [x] 構造体の比較には使わない

## 関連ページ

- [cpprefjp: memcmp](https://cpprefjp.github.io/reference/cstring/memcmp.html)
- [cppreference: memcmp](https://en.cppreference.com/w/cpp/string/byte/memcmp)
