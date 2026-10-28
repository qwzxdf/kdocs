---
title: std::puts
summary: "標準出力に文字列と改行を書く。"
order: 900
tags:
  - 入出力・文字列
---

# std::puts

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

デバッグ用に、メッセージを 1 行だけ画面に出したい。`puts` は、<strong>文字列に改行を足して、標準出力に出す</strong>関数です。`printf` のように書式を解釈しないので、`%` が混ざっていても安全です。

!!! tip "ポイント"
    - `puts(文字列)` は、文字列を出したあと、改行も出す
    - `fputs(文字列, stdout)` との違いは、改行が自動で付くこと
    - 書式を解釈しない。`%` はそのまま出る
    - 戻り値は、成功なら非負の値、失敗なら `EOF`

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::puts {#puts}

```cpp
int puts(const char* str);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | `const char*` | 出力する文字列。`\0` で終わっている必要がある |

`str` を標準出力に書き、続けて改行 `\n` を 1 つ書きます。名前が似た [`fputs`](fputs.md) は、改行を足さないので、混同しないようにします。

`printf(str)` と違い、書式の解釈がありません。ユーザーの入力を含む文字列を `printf(input)` で出すと、`%s` や `%n` が解釈されて危険ですが、`puts(input)` は安全です。

C++23 の `std::println("{}", str)` が使える環境では、型安全で書式つきの `std::println` を使うほうが、一貫して書けます。

## 実際に動かしてみる

```cpp
#include <cstdio>

int main() {
  std::puts("HP: 100%");    // % が含まれても、そのまま出る。改行も付く
  std::puts("MP: 50");
}
```

```text title="実行結果"
HP: 100%
MP: 50
```

## ゲームでの使いどころ

簡単なデバッグ出力に使います。ユーザー名やファイル名のような、`%` を含みうる文字列を、そのまま画面に出す場面で安心です。

ログの出力は、`std::println` やロギング ライブラリに任せ、`puts` は、C のコードや、短いスクリプトのようなプログラムで見かける、と考えておきます。

## よくあるミス

??? failure "改行を自分で付けて、空行が増える"
    `puts` は改行を足します。文字列に `\n` を入れると、2 つ出ます。

??? failure "`fputs` と同じだと思って、改行が出ないと悩む"
    `fputs` は改行を足さず、`puts` は足します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fputs`](fputs.md) | 改行を足さない。出力先を選べる |
| [`putchar`](putchar.md) | 1 文字だけ |
| `std::println` | C++23 の書式つき出力 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字列と改行を標準出力に出す
    - [x] 書式を解釈しない
    - [x] `fputs` は改行を足さない

## 関連ページ

- [cpprefjp: std::puts](https://cpprefjp.github.io/reference/cstdio/puts.html)
- [cppreference: std::puts](https://en.cppreference.com/w/cpp/io/c/puts)
