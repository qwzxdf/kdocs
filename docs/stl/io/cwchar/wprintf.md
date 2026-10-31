---
title: std::wprintf
summary: "書式を指定して、ワイド文字で標準出力に出す。"
order: 900
tags:
  - 入出力・文字列
---

# std::wprintf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

`printf` の `wchar_t` 版が `wprintf` です。書式文字列も `L"..."` のワイド文字列で、`%d` や `%f` の使い方は `printf` と同じです。ワイド文字列を出すときの書式指定に、環境ごとの違いがあることを、特に知っておく必要があります。

C++ の新しいコードでは `std::println` や `std::wcout` を使います。`wprintf` は、古いコードを読むときのために押さえておく関数です。

!!! tip "ポイント"
    - 書式も出力もワイド文字。`wprintf(L"HP=%d\n", hp)` のように書く
    - ワイド文字列は `%ls`、`char` の文字列は `%hs` と書くと、環境によらず意味が決まる
    - `%s` は、MSVC ではワイド文字列、標準では `char` の文字列。移植性のために避ける
    - 標準出力は、ワイド向きか `char` 向きのどちらかに固定される。`printf` と混ぜない

!!! info "このページを読む前に"
    [`<cwchar>`](../cwchar.md) の概要と、`printf`（[`<cstdio>`](../cstdio/printf.md)）を先に読んでください。

## 関数の詳しい説明

### std::wprintf {#wprintf}

```cpp
int wprintf(const wchar_t* format, ...);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `format` | `const wchar_t*` | 書式文字列。`L"..."` |
| `...` | 可変引数 | 書式に対応する値 |

書式文字列の `%d`、`%f`、`%x` などの扱いは `printf` と同じです。幅（`%5d`）、精度（`%.2f`）、ゼロ詰め（`%03d`）も使えます。

違いが出るのは、文字列を出す `%s` と `%c` です。標準では、`wprintf` の `%s` は <strong>`char` の文字列</strong>、`%ls` が<strong>ワイド文字列</strong>です。ところが MSVC の従来の動作では、逆に `%s` がワイド文字列を意味します。そこで、どちらの環境でも同じ意味になる `%ls`（ワイド）と `%hs`（`char`）を使います。

戻り値は、出力した文字数です。エラーが起きると負の値を返します。

標準出力には「向き」があります。最初に `printf` のような `char` の関数を呼ぶと `char` 向き、`wprintf` のようなワイド文字の関数を呼ぶと、ワイド向きに固定されます。逆の関数を呼ぶと、環境によってはエラーになり、出力されません。MSVC は緩い扱いですが、Linux の glibc では失敗します。

ワイド文字を、画面に正しく出すには、ロケールかコンソールの設定が要ります。日本語を出すには、環境ごとの設定が必要で、うまく出ないことがよくあります。

## 実際に動かしてみる

```cpp
#include <cwchar>

int main() {
  const int hp = 30;
  const wchar_t* name = L"Hero";

  // %ls でワイド文字列、%d で整数、%.1f で小数
  std::wprintf(L"%ls HP=%d x=%.1f\n", name, hp, 1.25);
}
```

```text title="実行結果"
Hero HP=30 x=1.2
```

`%.1f` の `1.25` は、2 進数で正確に表せる値の、ちょうど中間なので、偶数に寄せられて `1.2` になります。環境による違いが出るので、丸め方が重要なときは、値を工夫します。

## ゲームでの使いどころ

Windows API の関数が返す `wchar_t` のメッセージを、コンソールに出すデバッグ出力で見かけます。新しく書くなら、`std::println` と UTF-8 の文字列にそろえます。

## よくあるミス

??? failure "%s にワイド文字列を渡す"
    MSVC では動きますが、Linux では `char` として解釈され、1 文字目だけが出るなどの壊れた出力になります。`%ls` と書きます。

??? failure "printf と wprintf を混ぜる"
    標準出力の向きが固定されて、片方が無視されることがあります。どちらかにそろえます。

??? failure "書式文字列を char の文字列で渡す"
    `wprintf("HP=%d", hp)` は、型が違うのでコンパイルエラーです。`L"..."` にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fwprintf`](fwprintf.md) | 出力先のファイルを指定する |
| [`swprintf`](swprintf.md) | 文字の配列に書き込む |
| [`printf`](../cstdio/printf.md) | `char` 版 |
| [`std::println`](../../utilities/print.md) | 新しい書式つき出力。型安全 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `wprintf` は、ワイド文字の書式で標準出力に出す
    - [x] ワイド文字列は `%ls`、`char` の文字列は `%hs`
    - [x] `printf` と混ぜない。新しいコードは `std::println`

## 関連ページ

- [cpprefjp: wprintf](https://cpprefjp.github.io/reference/cwchar/wprintf.html)
- [cppreference: wprintf](https://en.cppreference.com/w/cpp/io/c/wprintf)
