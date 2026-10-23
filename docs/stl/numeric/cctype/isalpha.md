---
title: std::isalpha
summary: "英字（A-Z, a-z）かを調べる。"
order: 1
group: <cctype> の文字判定
tags:
  - 数値
---

# std::isalpha

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cctype>`
</div>

`std::isalpha` は、**文字が英字（A〜Z、a〜z）か**を調べる関数です。ASCII 文字だけが対象で、日本語は判定できません。引数は `unsigned char` にして渡します。

!!! tip "ポイント"
    - 日本語（UTF-8 のバイト）は判定できない。
    - 引数の `char` が負だと未定義動作。`static_cast<unsigned char>(c)` を通す。

!!! info "このページを読む前に"
    - [stl/index.md](../../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### std::isalpha {#isalpha}

```cpp
int isalpha(int c);
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
  std::println("{} {}", std::isalpha('a') != 0, std::isalpha('1') != 0);
}
```

```text title="実行結果"
true false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 識別子・コマンド名の検査 | `std::isalpha(static_cast<unsigned char>(c))` |

## よくあるミス

??? failure "char のまま渡す"
    負の `char` は未定義動作です。`unsigned char` に直します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`isdigit`](isdigit.md) | 数字 |
| [`toupper`](toupper.md) | 大文字に |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 英字かを調べる
    - [x] ASCII だけ
    - [x] unsigned char にして渡す

## 関連ページ

- [cpprefjp: std::isalpha](https://cpprefjp.github.io/reference/cctype/isalpha.html)
- [cppreference: std::isalpha](https://en.cppreference.com/w/cpp/string/byte/isalpha)
