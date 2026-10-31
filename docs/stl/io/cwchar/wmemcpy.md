---
title: std::wmemcpy
summary: "ワイド文字の配列を、指定した個数だけコピーする。"
order: 900
tags:
  - 入出力・文字列
---

# std::wmemcpy

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

`wcscpy` は終端の `L'\0'` まで探してコピーしますが、途中に `L'\0'` が入っている配列や、終端のない固定長のデータには使えません。`wmemcpy` は、終端を探さず、指定した個数の `wchar_t` を、そのままコピーします。`char` 版の `memcpy` に当たる関数で、要素の個数で数える点が違います。

!!! tip "ポイント"
    - `count` は要素の個数。バイト数ではない（`memcpy` との違い）
    - 終端を探さない。途中に `L'\0'` があっても、`count` 個をそのままコピーする
    - コピー元とコピー先が重なっていると未定義動作。重なるなら `wmemmove`
    - 終端が要る文字列にするときは、自分で `L'\0'` を足す

!!! info "このページを読む前に"
    [`wcscpy`](wcscpy.md) を先に読んでください。

## 関数の詳しい説明

### std::wmemcpy {#wmemcpy}

```cpp
wchar_t* wmemcpy(wchar_t* dest, const wchar_t* src, std::size_t count);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `dest` | `wchar_t*` | コピー先。`count` 要素以上の領域 |
| `src` | `const wchar_t*` | コピー元。`count` 要素以上の領域 |
| `count` | `std::size_t` | コピーする要素の個数 |

`src` の先頭から `count` 個の `wchar_t` を、`dest` にコピーします。戻り値は `dest` です。

`count` が要素の個数である点に注意します。`memcpy(dst, src, 4)` は 4 バイトですが、`wmemcpy(dst, src, 4)` は 4 要素で、Windows では 8 バイト、Linux では 16 バイトです。バイト数の感覚で `count` を書くと、必要以上にコピーしてしまいます。

`count` が 0 のときも、`dest` と `src` は有効なポインタでなければなりません。`nullptr` は渡せません。

重なる領域のコピーは、`wmemmove` を使います。`wmemcpy` で重なりを渡すと、結果が保証されません。

終端を付けるのは自分の仕事です。`count` 個を詰めたあと、`dest[count] = L'\0';` が要るなら、`dest` に `count + 1` 要素ぶんの領域を用意しておきます。

## 実際に動かしてみる

```cpp
#include <cwchar>
#include <print>

int main() {
  const wchar_t src[] = L"ABCDEF";
  wchar_t dest[8] = {};

  std::wmemcpy(dest, src, 3);  // 先頭の 3 要素: "ABC"
  dest[3] = L'\0';             // 終端は自分で付ける

  std::println("{}", std::wcscmp(dest, L"ABC") == 0);
  std::println("長さ: {}", std::wcslen(dest));
}
```

```text title="実行結果"
true
長さ: 3
```

## ゲームでの使いどころ

固定長のワイド文字の配列を、バッファからバッファへ移すときに使います。C++ のコードでは `std::copy` や `std::wstring` のほうが型に合った書き方で、`wmemcpy` を使う場面は多くありません。

## よくあるミス

??? failure "count にバイト数を渡す"
    `wmemcpy(dest, src, sizeof(src))` は、要素数ではなくバイト数です。`sizeof(src) / sizeof(src[0])` を渡します。

??? failure "重なった領域をコピーする"
    同じ配列の中で、ずらしてコピーするときは `wmemmove` です。`wmemcpy` は、結果が保証されません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`wcscpy`](wcscpy.md) | 終端までコピーする |
| `wmemmove` | 重なっていてもよい |
| `memcpy` | バイト単位でコピーする |
| `std::copy` | C++ のアルゴリズム。型に合わせてコピーする |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `wmemcpy` は、`count` 個の `wchar_t` を、終端を探さずにコピーする
    - [x] `count` は要素の個数。バイト数ではない
    - [x] 重なるなら `wmemmove`

## 関連ページ

- [cpprefjp: wmemcpy](https://cpprefjp.github.io/reference/cwchar/wmemcpy.html)
- [cppreference: wmemcpy](https://en.cppreference.com/w/cpp/string/wide/wmemcpy)
