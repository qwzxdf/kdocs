---
title: strstr
summary: "C 文字列の中から、別の文字列を探す。"
order: 10
group: C の文字列・メモリ関数（<cstring>）
tags:
  - メモリ
---

# strstr

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstring>`
</div>

`strstr` は、**C 文字列の中から、別の文字列（部分文字列）を探す**関数です。見つかれば位置のポインター、なければ `nullptr` を返します。

!!! tip "ポイント"
    - `std::string::find(const char*)` と同じ。
    - 大文字小文字は区別される。

!!! info "このページを読む前に"
    [ポインタ](../../../basics/pointer.md) が分かると読みやすいです。

## 関数の詳しい説明

### strstr {#strstr}

```cpp
const char* strstr(const char* str, const char* substr);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | `const char*` | 探される C 文字列 |
| `substr` | `const char*` | 探す C 文字列 |

- 戻り値: 最初に見つかった位置のポインタ。なければ `nullptr`
- `std::string_view::find` / `contains` を使うほうが、長さを保てて安全です。

## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  const char* s = "hello world";
  std::println("{}", std::strstr(s, "world") - s);
}
```

```text title="実行結果"
6
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ログ行に特定の単語があるか | `strstr(line, "ERROR")` |

## よくあるミス

??? failure "戻り値を bool として使う"
    ポインターなので、`!= nullptr` と明示すると読みやすい。

## 類似

| 名前 | 違い |
| --- | --- |
| `std::string::find` | C++ の同等品 |
| [`std::ranges::search`](../../algorithms/search.md) | 任意の範囲向け |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 部分文字列を探す
    - [x] 無ければ nullptr
    - [x] C++ では `find`

## 関連ページ

- [cpprefjp: strstr](https://cpprefjp.github.io/reference/cstring/strstr.html)
- [cppreference: strstr](https://en.cppreference.com/w/cpp/string/byte/strstr)
