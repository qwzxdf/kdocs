---
title: std::codecvt
summary: "文字コードの変換を担当するファセット。"
order: 900
tags:
  - 入出力・文字列
---

# std::codecvt

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <locale>`
</div>

ファイルに書くときは UTF-8 の `char`、メモリの中では `wchar_t` で扱いたい。`std::wofstream` がこの変換をできるのは、ロケールの中にある `std::codecvt` が、2 つの文字コードの間の変換を受け持っているからです。`imbue` で別のロケールを差し込むと、変換のしかたが変わります。

直接使う場面は、ほぼなく、ファイルのストリームの文字コードを変えたいときに、派生クラスを差し込む形で出てきます。

!!! tip "ポイント"
    - 3 つのテンプレート引数は、メモリ上の文字の型、ファイル側の文字の型、変換の途中状態
    - `in` はファイル側からメモリ側へ、`out` は逆方向への変換
    - 戻り値は `ok`、`partial`、`error`、`noconv`
    - `always_noconv()` が `true` なら、何も変換しない（`char` と `char` の組など）

!!! info "このページを読む前に"
    [`std::locale::facet`](facet.md)、[`std::use_facet`](use_facet.md)、[`std::mbstate_t`](../cwchar/mbstate_t.md) を先に読んでください。

## 関数の詳しい説明

### std::codecvt {#codecvt}

```cpp
template <class InternT, class ExternT, class StateT>
class codecvt;
```

| テンプレート引数 | 意味 |
| --- | --- |
| `InternT` | メモリ上の文字の型（`wchar_t`、`char32_t` など） |
| `ExternT` | ファイル側の文字の型（普通は `char`） |
| `StateT` | 変換の途中状態（普通は `mbstate_t`） |

標準で用意されている組は、`codecvt<char, char, mbstate_t>`（何も変換しない）、`codecvt<wchar_t, char, mbstate_t>`（ロケールの文字コードと `wchar_t`）、`codecvt<char16_t, char8_t, mbstate_t>` と `codecvt<char32_t, char8_t, mbstate_t>`（UTF-8 との変換）などです。

### in と out {#in-out}

```cpp
result in(StateT& state, const ExternT* from, const ExternT* from_end,
          const ExternT*& from_next, InternT* to, InternT* to_end,
          InternT*& to_next) const;
```

`in` は、ファイル側の文字列（`from` から `from_end`）を、メモリ側の文字列（`to` から `to_end`）に変換します。どこまで読んだか、どこまで書いたかを、`from_next` と `to_next` に返します。`out` は、逆方向の変換です。

戻り値は、次のとおりです。

| 値 | 意味 |
| --- | --- |
| `ok` | 全部変換できた |
| `partial` | 入力か出力が足りなくて、途中までしか変換できていない |
| `error` | 変換できない文字があった |
| `noconv` | 変換が不要だった（同じ型） |

### always_noconv と max_length {#info}

`always_noconv()` は、どんな入力でも変換しない組なら `true` です。`max_length()` は、1 文字の変換に必要な最大の要素数を返します。UTF-8 なら 4 です。

## 実際に動かしてみる

```cpp
#include <locale>
#include <print>

int main() {
  using CharToChar = std::codecvt<char, char, std::mbstate_t>;
  using WideToChar = std::codecvt<wchar_t, char, std::mbstate_t>;

  const std::locale loc = std::locale::classic();
  const auto& same = std::use_facet<CharToChar>(loc);
  const auto& wide = std::use_facet<WideToChar>(loc);

  std::println("char ↔ char は何も変換しない: {}", same.always_noconv());
  std::println("wchar_t ↔ char は変換が要る: {}", !wide.always_noconv());
}
```

```text title="実行結果"
char ↔ char は何も変換しない: true
wchar_t ↔ char は変換が要る: true
```

`char` から `char` への組は変換が不要で、`wchar_t` と `char` の組は変換が必要です。

## ゲームでの使いどころ

`std::wofstream` で書くファイルの文字コードを、UTF-8 にするために、`imbue` で UTF-8 用の `codecvt` を差し込む方法があります。ただし、C++17 で非推奨になった `codecvt_utf8` を使う方法が昔は定番でした。今は、メモリ内を UTF-8 の `std::string` にそろえ、Windows API の直前で変換するほうが、問題が少なくなります。

## よくあるミス

??? failure "partial を失敗と誤解する"
    `partial` は、入力が途中で終わった場合や出力の領域が足りない場合で、続きを渡せば変換を続けられます。失敗は `error` です。

??? failure "in と out の方向を取り違える"
    `in` は、ファイル側（`ExternT`）からメモリ側（`InternT`）です。ファイルに書くときは `out` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`codecvt_utf8`](codecvt_utf8.md) | UTF-8 と UCS-2 / UTF-32 を変換する派生クラス。非推奨 |
| [`mbrtowc`](../cwchar/mbrtowc.md) | C の関数での同じ変換 |
| `MultiByteToWideChar` | Windows の API。UTF-8 を直接指定できる |

## コンパイラ対応

C++98 から使えます。`char16_t` / `char32_t` の組は C++11 から。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `codecvt` は、メモリ上の文字とファイルの文字の間の変換を担当する部品
    - [x] `in` はファイル側からメモリ側、`out` はその逆。`partial` は続きがある状態
    - [x] 文字コードの変換は、新しいコードでは API 直前の変換にまとめる

## 関連ページ

- [cpprefjp: codecvt](https://cpprefjp.github.io/reference/locale/codecvt.html)
- [cppreference: std::codecvt](https://en.cppreference.com/w/cpp/locale/codecvt)
