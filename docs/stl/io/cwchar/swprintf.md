---
title: std::swprintf
summary: "書式を指定して、ワイド文字の配列に書き込む。"
order: 900
tags:
  - 入出力・文字列
---

# std::swprintf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

数値を含むメッセージを `wchar_t` の文字列に組み立てて、Windows API に渡したい。`swprintf` は、書式を指定した結果を、画面ではなく、ワイド文字の配列に書き込みます。`sprintf` のワイド文字版ですが、`sprintf` と違って、書き込める最大の文字数を渡す点が違います。

!!! tip "ポイント"
    - 第 2 引数 `bufsz` に、配列の要素数（終端を含む）を渡す
    - 入りきらないときは、負の値を返す。`snprintf` のように、必要な長さは返さない
    - 入りきらなかったときの配列の中身は、環境によって違う。使わない
    - 古い MSVC の `swprintf` は、大きさを渡さない別のシグネチャだった。今は標準と同じ

!!! info "このページを読む前に"
    [`std::wprintf`](wprintf.md) を先に読んでください。

## 関数の詳しい説明

### std::swprintf {#swprintf}

```cpp
int swprintf(wchar_t* buffer, std::size_t bufsz, const wchar_t* format, ...);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `buffer` | `wchar_t*` | 書き込み先 |
| `bufsz` | `std::size_t` | 書き込める最大の要素数（終端を含む） |
| `format` | `const wchar_t*` | 書式文字列 |
| `...` | 可変引数 | 書式に対応する値 |

整形した結果を、終端の `L'\0'` も含めて、`bufsz` 要素以内で `buffer` に書き込みます。

戻り値は、終端を除く、書き込んだ文字数です。結果が `bufsz` に収まらないときは、負の値を返します。`snprintf` と違い、本来必要だった長さは教えてくれません。そのため、長さの見積もりは、大きめの配列を用意するか、`_scwprintf` のような環境依存の関数に頼ることになります。

収まらなかったとき、配列の内容は環境によって違います。切り詰められて終端が付く環境もあれば、終端がない環境もあります。戻り値が負のときは、配列を信用せず、自分で `buffer[0] = L'\0';` にするなどして、安全にします。

書式のワイド文字列は、`%ls` と書きます。`%s` は環境ごとに意味が違います。

C++ の新しいコードは、`std::format` や `std::wostringstream` を使います。大きさの管理が要らず、型の間違いもコンパイル時に分かります。

## 実際に動かしてみる

```cpp
#include <cwchar>
#include <print>

int main() {
  wchar_t buffer[32] = {};
  const int n = std::swprintf(buffer, 32, L"%ls HP=%d", L"Hero", 30);
  std::println("書いた文字数: {}", n);
  std::println("一致: {}", std::wcscmp(buffer, L"Hero HP=30") == 0);

  // 小さい配列には入りきらず、負の値になる
  wchar_t small[4] = {};
  const int m = std::swprintf(small, 4, L"%ls", L"Hero HP=30");
  std::println("入りきらない: {}", m < 0);
}
```

```text title="実行結果"
書いた文字数: 10
一致: true
入りきらない: true
```

## ゲームでの使いどころ

Windows API が `wchar_t` の固定長配列（`wchar_t title[64]`）を要求する場所に、数値を含む文字列を詰めるときに使います。

```cpp
wchar_t title[64];
std::swprintf(title, 64, L"Stage %d - %ls", stage, name);
```

収まらないことがありえる入力なら、戻り値を検査します。

## よくあるミス

??? failure "bufsz にバイト数を渡す"
    要素数を渡します。`sizeof(buffer)` ではなく、`sizeof(buffer) / sizeof(buffer[0])` です。バイト数を渡すと、2 倍や 4 倍の大きさを許してしまい、あふれます。

??? failure "戻り値の負の値を無視する"
    入りきらなかったとき、配列の中身は信用できません。検査して、切り詰めるか、大きな配列で作り直します。

??? failure "%s でワイド文字列を渡す"
    環境によって解釈が変わります。`%ls` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`wprintf`](wprintf.md) | 標準出力に出す |
| `snprintf` | `char` 版。必要な長さも返す |
| `std::format` | 大きさの管理が要らない。普段はこちら |

## コンパイラ対応

C++98 から使えます。MSVC の古い版の `swprintf` は、大きさを渡さない形でした。今の MSVC では標準の形です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `swprintf` は、書式の結果をワイド文字の配列に書く
    - [x] `bufsz` は要素数。入りきらないと負の値
    - [x] 新しいコードは `std::format`

## 関連ページ

- [cpprefjp: swprintf](https://cpprefjp.github.io/reference/cwchar/swprintf.html)
- [cppreference: swprintf](https://en.cppreference.com/w/cpp/io/c/swprintf)
