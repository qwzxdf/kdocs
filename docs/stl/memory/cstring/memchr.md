---
title: memchr
summary: "メモリの中から、1 バイトの値を探す。"
order: 8
group: C の文字列・メモリ関数（<cstring>）
tags:
  - メモリ
---

# memchr

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstring>`
</div>

`memchr` は、**メモリの先頭から、指定したバイトを探す**関数です。見つかればその位置のポインター、なければ `nullptr` を返します。バイナリデータから区切りを探すときに使います。

!!! tip "ポイント"
    - 範囲（バイト数）を渡すので、`\0` を含むデータにも使える。
    - 文字列用の [`strchr`](strchr.md) は `\0` で止まる。

!!! info "このページを読む前に"
    [ポインタ](../../../basics/pointer.md) が分かると読みやすいです。

## 関数の詳しい説明

### memchr {#memchr}

```cpp
const void* memchr(const void* ptr, int ch, std::size_t count);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ptr` | `const void*` | 探す領域の先頭 |
| `ch` | `int` | 探すバイトの値 |
| `count` | `std::size_t` | 探す範囲のバイト数 |

- 戻り値: 最初に見つかった場所のポインタ。なければ `nullptr`
- バイナリデータの中から、区切りのバイトを探すときに使います

## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  const char s[] = "hello";
  auto* p = static_cast<const char*>(std::memchr(s, 'l', 5));
  std::println("{}", p - s);
}
```

```text title="実行結果"
2
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 受信データの区切りバイトを探す | `memchr(buf, 0x0A, size)` |

## よくあるミス

??? failure "戻り値を調べずに使う"
    `nullptr` のことがあります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strchr`](strchr.md) | 文字列用 |
| [`std::ranges::find`](../../algorithms/find.md) | 型を意識した探索 |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] バイトを探す
    - [x] 無ければ nullptr
    - [x] `\0` を含むデータに使える

## 関連ページ

- [cpprefjp: memchr](https://cpprefjp.github.io/reference/cstring/memchr.html)
- [cppreference: memchr](https://en.cppreference.com/w/cpp/string/byte/memchr)
