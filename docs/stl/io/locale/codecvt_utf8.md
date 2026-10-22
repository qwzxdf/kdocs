---
title: std::codecvt_utf8
summary: "UTF-8 と、UCS-2 / UTF-32 を変換するファセット（非推奨）。"
order: 900
tags:
  - 入出力・文字列
---

# std::codecvt_utf8

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <codecvt>`
</div>

UTF-8 と、`char32_t` や `wchar_t` の間で変換するための、標準のファセットです。`wstring_convert` と組み合わせて使われましたが、C++17 で非推奨になりました。新しいコードでは、OS の API（`MultiByteToWideChar`）や ICU を使います。

!!! tip "ポイント"
    - ロケール（言語・地域ごとの規則）の部品。
    - ふつうは `std::locale` 経由で使う。
    - ゲームのローカライズでは、書式（日付・数字）に関わる。

!!! info "このページを読む前に"
    [`std::locale`](../locale.md) を先に読んでください。

## 関数の詳しい説明

### std::codecvt_utf8 {#codecvt_utf8}

```cpp
template <class Elem, unsigned long Maxcode = 0x10ffff, codecvt_mode Mode = codecvt_mode(0)>
class codecvt_utf8 : public codecvt<Elem, char, mbstate_t>;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `Elem` | 型 | メモリ上の文字の型（`char32_t` など） |

- 戻り値: UTF-8 との変換をするファセット
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <codecvt>
#include <locale>
#include <print>
#include <string>

int main() {
  std::wstring_convert<std::codecvt_utf8<char32_t>, char32_t> conv;
  std::string s = conv.to_bytes(U'あ');
  std::println("{}", s.size());
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | （古いコードの保守） |

## よくあるミス

??? failure "新しいコードで使う"
    C++17 で非推奨になり、将来削除されます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`codecvt`](codecvt.md) | 元のファセット |
| [文字コード](../../../encoding/index.md) | 変換の考え方 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] UTF-8 と、UCS-2 / UTF-32 を変換するファセット（非推奨）
    - [x] ロケール（言語・地域ごとの規則）の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::codecvt_utf8](https://cpprefjp.github.io/reference/locale/codecvt_utf8.html)
- [cppreference: std::codecvt_utf8](https://en.cppreference.com/w/cpp/locale/codecvt_utf8)
