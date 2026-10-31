---
title: std::wcscpy
summary: "ワイド文字列をコピーする。"
order: 900
tags:
  - 入出力・文字列
---

# std::wcscpy

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

`wchar_t` の文字列を、別の配列にコピーしたい。`char` 版の `strcpy` に当たる関数が `wcscpy` です。終端の `L'\0'` までをコピーし、コピー先の大きさは確かめません。大きさが足りないとバッファ オーバーランになり、セキュリティの穴になります。そのため、新しいコードでは `std::wstring` を使うか、大きさを指定する `wcsncpy` / `wcscpy_s` を使います。

!!! tip "ポイント"
    - 終端の `L'\0'` を含めてコピーする
    - コピー先の大きさは調べない。`src` の長さ + 1 要素以上の領域が必要
    - コピー元とコピー先が重なっていると未定義動作
    - MSVC は `wcscpy` に警告（C4996）を出す。`wcscpy_s` か `std::wstring` に置き換える

!!! info "このページを読む前に"
    [`<cwchar>`](../cwchar.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::wcscpy {#wcscpy}

```cpp
wchar_t* wcscpy(wchar_t* dest, const wchar_t* src);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `dest` | `wchar_t*` | コピー先。`wcslen(src) + 1` 要素以上の領域 |
| `src` | `const wchar_t*` | コピー元。終端のある文字列 |

`src` の先頭から、終端の `L'\0'` までを、`dest` にコピーします。戻り値は `dest` です。連続して呼ぶ書き方（`wcscat(wcscpy(a, b), c)`）に使えます。

コピー先は、`wcslen(src) + 1`（終端の分）要素の領域が必要です。たとえば 16 要素の配列に 20 文字の文字列をコピーすると、配列の外を上書きします。この上書きは、スタックの他の変数や戻りアドレスを壊すので、昔から攻撃の入り口になっています。

領域の大きさを指定できる安全な関数は、環境によって違います。標準の `wcsncpy` は、終端を付けないことがあるため、扱いにくい関数です。MSVC の `wcscpy_s(dest, size, src)` は、大きさを渡し、足りなければ実行時エラーにします。C++ では、`std::wstring` に代入するのが、いちばん簡単で安全です。

```cpp
std::wstring copy = src;   // 大きさの管理は wstring が行う
```

## 実際に動かしてみる

```cpp
#include <cwchar>
#include <print>

int main() {
  const wchar_t* src = L"Hero";
  wchar_t dest[16] = {};  // 十分な大きさを用意する

  std::wcscpy(dest, src);
  std::println("コピーできた: {}", std::wcscmp(dest, L"Hero") == 0);
  std::println("長さ: {}", std::wcslen(dest));
}
```

```text title="実行結果"
コピーできた: true
長さ: 4
```

MSVC では、この `wcscpy` に対して警告（C4996）が出ますが、結果は変わりません。

## ゲームでの使いどころ

Windows API が `wchar_t` の固定長の配列（`wchar_t path[MAX_PATH]`）を要求する場面で、文字列を詰めるときに出てきます。その場合は `wcscpy_s` で大きさを渡すか、`std::wstring` の `c_str()` を直接渡せる API なら、コピー自体を省きます。

## よくあるミス

??? failure "コピー先が小さい"
    `wchar_t name[8]` に 20 文字をコピーすると、領域の外を壊します。クラッシュや、原因の分かりにくい不具合になります。`std::wstring` を使うか、大きさを確かめます。

??? failure "終端の分を数え忘れる"
    10 文字をコピーするには 11 要素必要です。ちょうど 10 要素の配列だと、終端が外に書かれます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`wmemcpy`](wmemcpy.md) | 個数を指定してコピーする。終端を探さない |
| `wcsncpy` | 大きさを指定してコピーする。終端を付けないことがある |
| `strcpy` | `char` 版 |
| [`std::wstring`](../../containers/string.md) | 大きさを自動で管理する。普段はこちら |

## コンパイラ対応

C++98 から使えます。MSVC では `wcscpy_s` への置き換えを促す警告が出ます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `wcscpy` は、終端まで含めてワイド文字列をコピーする
    - [x] コピー先の大きさは調べない。`長さ + 1` 要素が必要
    - [x] 新しいコードは `std::wstring`

## 関連ページ

- [cpprefjp: wcscpy](https://cpprefjp.github.io/reference/cwchar/wcscpy.html)
- [cppreference: wcscpy](https://en.cppreference.com/w/cpp/string/wide/wcscpy)
