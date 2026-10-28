---
title: std::fputs
summary: "ファイルに文字列を書く（改行は付かない）。"
order: 900
tags:
  - 入出力・文字列
---

# std::fputs

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

ログやテキスト ファイルに、文字列を書き出したい。`fprintf` は書式を解釈するので、文字列に `%` が含まれていると、予期しない動きをします。<strong>文字列をそのまま書き出す</strong>には、`std::fputs` が安全です。

!!! tip "ポイント"
    - `fputs(文字列, ファイル)` で、`\0` の手前までを書き出す
    - 改行は自動では付かない。`puts` との違い
    - 書式を解釈しないので、`%` を含んでいても、そのまま出る
    - 戻り値は、成功なら 0 以上、失敗なら `EOF`

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::fputs {#fputs}

```cpp
int fputs(const char* str, std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | `const char*` | 書き出す文字列。`\0` で終わっている必要がある |
| `stream` | `FILE*` | 書き出す先のファイル。`stdout` や `stderr` も渡せる |

`str` の `\0` の手前までを書き出します。<strong>終端の `\0` や、改行は書き出しません</strong>。同じ仲間の `puts` は、改行を自動で足しますが、`fputs` は足しません。行にしたければ、文字列に `\n` を入れます。

`fprintf(f, str)` との違いは、書式の解釈です。ユーザー入力のような、`%` を含みうる文字列を `fprintf` の書式として渡すと、`%s` や `%n` が解釈され、クラッシュや脆弱性の原因になります。`fputs` なら、その心配がありません。

文字列の長さを `strlen` で数えて書くので、バイナリ データには向きません。`\0` を含むデータは `fwrite` を使います。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::fopen("log.txt", "w");
  std::fputs("HP: 100%\n", f);   // % が含まれていても、そのまま出る
  std::fputs("MP: 50", f);        // 改行は付かない
  std::fclose(f);

  std::FILE* in = std::fopen("log.txt", "r");
  char buf[64];
  while (std::fgets(buf, sizeof(buf), in)) std::print("{}", buf);
  std::println("");
  std::fclose(in);
}
```

```text title="実行結果"
HP: 100%
MP: 50
```

## ゲームでの使いどころ

ログ ファイルに、1 行ずつ書き込むときに使います。メッセージに `%` が含まれうる（ユーザー名やファイル名など）場面で、`fprintf` より安全です。

C++ では、`std::ofstream` と `<<`、または `std::print(FILE*, ...)`（C++23）でも書けます。`FILE*` を扱う C のライブラリとの連携では、`fputs` が手軽です。

## よくあるミス

??? failure "改行が付くと思って、ログが 1 行につながる"
    `fputs` は改行を足しません。`puts` と混同しないようにします。

??? failure "ユーザー入力を `fprintf` の書式にして、クラッシュ"
    `fprintf(f, input)` の形は危険です。`fputs(input, f)` か、`fprintf(f, "%s", input)` にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`puts`](puts.md) | `stdout` に書いて、改行を足す |
| [`fprintf`](fprintf.md) | 書式つきで書く |
| [`fwrite`](fwrite.md) | バイト列を書く。`\0` を含んでもよい |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字列をそのまま書き出す
    - [x] 改行は付かない
    - [x] 書式を解釈しないので安全

## 関連ページ

- [cpprefjp: std::fputs](https://cpprefjp.github.io/reference/cstdio/fputs.html)
- [cppreference: std::fputs](https://en.cppreference.com/w/cpp/io/c/fputs)
