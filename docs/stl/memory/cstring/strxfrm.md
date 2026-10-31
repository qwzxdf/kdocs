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

`strcoll` は、比べるたびにロケールの規則を適用するので、大量の文字列を並べ替えるときに遅くなります。`std::strxfrm(dst, src, n)` は、文字列を「`strcmp` で比べるだけでロケールの辞書順になる」文字列に変換します。先に変換して、あとは `strcmp` で並べ替えれば速くなります。

!!! tip "ポイント"
    - 変換後の文字列を `strcmp` で比べると、`strcoll` と同じ結果になる
    - 戻り値は、変換後の長さ（終端を除く）
    - `dst` を `nullptr`、`n` を 0 にすると、必要な長さだけを返す
    - "C" ロケールでは、変換しても同じ文字列

!!! info "このページを読む前に"
    [`<cstring>`](../cstring.md) の概要を先に読んでください。C の文字列は、終端が `'\0'` の `char` の配列です。

## 関数の詳しい説明

### std::strxfrm {#strxfrm}

```cpp
std::size_t strxfrm(char* dest, const char* src, std::size_t count);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `dest` | `char*` | 変換結果の書き込み先。`nullptr` なら長さだけ求める |
| `src` | `const char*` | 変換する文字列 |
| `count` | `std::size_t` | `dest` に書ける最大の文字数 |

戻り値が `count` 以上なら、変換結果が入りきらなかったということで、`dest` の中身は不定です。長さを先に求めて、領域を確保してから変換します。

変換後の長さは、元の長さと違うことがあります。

## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>
#include <string>

int main() {
  const char* src = "banana";

  // 必要な長さを先に求める
  const std::size_t n = std::strxfrm(nullptr, src, 0);
  std::string key(n, '\0');
  std::strxfrm(key.data(), src, n + 1);

  std::println("変換後の長さ: {}", n);
  std::println("内容: {}", key);
}
```

```text title="実行結果"
変換後の長さ: 6
内容: banana
```

## ゲームでの使いどころ

大量の名前を、ロケールの辞書順に並べるときに、先にキーを作っておく用途です。

## よくあるミス

??? failure "長さを確かめずに書き込む"
    `n` を渡して、戻り値が `n` 以上でないかを確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strcoll`](strcoll.md) | 変換せずに直接比べる |
| [`strcmp`](strcmp.md) | 変換後の比較に使う |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## 関連ページ

- [cpprefjp: std::strxfrm](https://cpprefjp.github.io/reference/cstring/strxfrm.html)
- [cppreference: std::strxfrm](https://en.cppreference.com/w/cpp/string/byte/strxfrm)
