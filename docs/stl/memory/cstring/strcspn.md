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

文字列の先頭から、指定した文字のどれかが初めて現れるまでの長さを知りたい。`std::strcspn(s, reject)` は、`reject` に含まれる文字が現れる直前までの長さを返します。`strspn` の逆の働きです。

!!! tip "ポイント"
    - 先頭から、`reject` の文字が現れるまでの長さ
    - 現れなければ、文字列全体の長さ
    - 区切り文字の位置を探すのに使える
    - 位置そのものが欲しいなら `strpbrk`

!!! info "このページを読む前に"
    [`<cstring>`](../cstring.md) の概要を先に読んでください。C の文字列は、終端が `'\0'` の `char` の配列です。

## 関数の詳しい説明

### std::strcspn {#strcspn}

```cpp
std::size_t strcspn(const char* dest, const char* src);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `dest` | `const char*` | 調べる文字列 |
| `src` | `const char*` | 探す文字の集まり |

先頭の文字がいきなり `src` に含まれるなら 0 です。

`fgets` で読んだ行の末尾の改行を取り除く定番の書き方が、`line[strcspn(line, "\n")] = '\0';` です。改行があればそこを終端にし、なければ元の終端を上書きするだけです。

## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  const char* s = "key=value";
  std::println("= までの長さ: {}", std::strcspn(s, "=:"));
  std::println("なければ全体の長さ: {}", std::strcspn("abc", "xyz"));

  // 末尾の改行を取り除く
  char line[16] = "hello\n";
  line[std::strcspn(line, "\n")] = '\0';
  std::println("{} ({} 文字)", line, std::strlen(line));
}
```

```text title="実行結果"
= までの長さ: 3
なければ全体の長さ: 3
hello (5 文字)
```

## ゲームでの使いどころ

`fgets` で読んだ行から改行を取り除くときに使います。

## よくあるミス

??? failure "位置と長さを取り違える"
    戻り値は先頭からの長さです。ポインタではありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strspn`](strspn.md) | 逆。許す文字が続く長さ |
| [`strpbrk`](strpbrk.md) | 位置をポインタで返す |
| [`strchr`](strchr.md) | 1 文字を探す |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## 関連ページ

- [cpprefjp: std::strcspn](https://cpprefjp.github.io/reference/cstring/strcspn.html)
- [cppreference: std::strcspn](https://en.cppreference.com/w/cpp/string/byte/strcspn)
