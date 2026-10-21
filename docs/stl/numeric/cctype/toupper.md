---
title: std::toupper
summary: "英字を大文字にする。"
order: 4
group: <cctype> の文字判定
tags:
  - 数値
---

# std::toupper

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cctype>`
</div>

`std::toupper` は、**英字を大文字にした文字を返す**関数です。英字でない文字はそのまま返します。大文字小文字を区別しない比較のために、両方を同じ形にそろえるときに使います。

!!! tip "ポイント"
    - 戻り値は `int`。`char` に戻して使う。
    - ASCII 以外（日本語、アクセント付き）は変換されない。

## 関数の詳しい説明

### std::toupper {#toupper}

```cpp
int toupper(int c);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `c` | `int` | 判定・変換する文字（`unsigned char` の範囲か EOF） |

- 戻り値: 結果
- 計算量: O(1)

```cpp
#include <cctype>
#include <print>

int main() {
  char c = static_cast<char>(std::toupper('a'));
  std::println("{}", c);
}
```

```text title="実行結果"
A
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| コマンドを大文字にそろえて比べる | `std::toupper` を各文字に |

## よくあるミス

??? failure "Unicode の大文字小文字を期待する"
    ASCII だけです。Unicode には ICU などのライブラリを使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`tolower`](tolower.md) | 小文字に |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 英字を大文字にする
    - [x] ASCII だけ
    - [x] 戻り値は int

## 関連ページ

- [cpprefjp: std::toupper](https://cpprefjp.github.io/reference/cctype/toupper.html)
- [cppreference: std::toupper](https://en.cppreference.com/w/cpp/string/byte/toupper)
