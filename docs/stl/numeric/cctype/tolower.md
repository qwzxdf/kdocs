---
title: std::tolower
summary: "英字を小文字にする。"
order: 5
group: <cctype> の文字判定
tags:
  - 数値
---

# std::tolower

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cctype>`
</div>

`std::tolower` は、**英字を小文字にした文字を返す**関数です。大文字小文字を区別しない比較（ファイル名、コマンド）でよく使います。

!!! tip "ポイント"
    - 戻り値は `int`。`char` に戻して使う。
    - ASCII 以外は変換されない。

## 関数の詳しい説明

### std::tolower {#tolower}

```cpp
int tolower(int c);
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
  char c = static_cast<char>(std::tolower('Q'));
  std::println("{}", c);
}
```

```text title="実行結果"
q
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 大文字小文字を区別しない比較の準備 | `std::tolower` を各文字に |

## よくあるミス

??? failure "Unicode の小文字を期待する"
    ASCII だけです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`toupper`](toupper.md) | 大文字に |
| [`weak_ordering`](../../support/weak_ordering.md) | 大文字小文字無視の比較の例 |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 英字を小文字にする
    - [x] ASCII だけ
    - [x] 戻り値は int

## 関連ページ

- [cpprefjp: std::tolower](https://cpprefjp.github.io/reference/cctype/tolower.html)
- [cppreference: std::tolower](https://en.cppreference.com/w/cpp/string/byte/tolower)
