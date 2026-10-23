---
title: std::isdigit
summary: "数字（0-9）かを調べる。"
order: 2
group: <cctype> の文字判定
tags:
  - 数値
---

# std::isdigit

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cctype>`
</div>

`std::isdigit` は、**文字が数字（0〜9）か**を調べる関数です。文字列の解析で、数字の連なりを読み取るときに使います。

!!! tip "ポイント"
    - 全角数字は判定できない。
    - 引数は `unsigned char` にして渡す。

!!! info "このページを読む前に"
    - [stl/index.md](../../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### std::isdigit {#isdigit}

```cpp
int isdigit(int c);
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
  std::println("{} {}", std::isdigit('7') != 0, std::isdigit('x') != 0);
}
```

```text title="実行結果"
true false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 簡易パーサーで数字の連なりを読む | `while (std::isdigit(s[i])) ++i;` |

## よくあるミス

??? failure "char のまま渡す"
    負の `char` は未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`isalpha`](isalpha.md) | 英字 |
| [`std::from_chars`](../../io/from_chars.md) | 数値への変換 |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 数字かを調べる
    - [x] ASCII の 0〜9 だけ
    - [x] unsigned char にして渡す

## 関連ページ

- [cpprefjp: std::isdigit](https://cpprefjp.github.io/reference/cctype/isdigit.html)
- [cppreference: std::isdigit](https://en.cppreference.com/w/cpp/string/byte/isdigit)
