---
title: std::to_string
summary: "数値を文字列にする。"
order: 60
group: 文字列と数値の変換
tags:
  - コンテナ
---

# std::to_string

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-11">C++11</span>
`#include <string>`
</div>

画面に「Score: 1200」と出すために、数値を文字列に変換して、文字列と連結したい。数値は文字列の `+` で連結できないので、変換が必要になります。`std::to_string` は、整数や小数を `std::string` に変換する関数です。手軽ですが、小数の桁数は 6 桁に固定され、細かい書式は指定できません。書式を整えたいときは `std::format` を使います。

!!! tip "ポイント"
    - 小数は小数点以下 6 桁固定（`1.5f` → `"1.500000"`）。
    - 桁を指定したいなら `std::format("{:.2f}", x)`。
    - 速さが必要なら [`std::to_chars`](../io/to_chars.md)。

!!! info "このページを読む前に"
    書式を整えたいときは、[`std::format`](../utilities/format.md) を使います。このページの `to_string` は、最も単純な変換だけを担当します。

## 関数の詳しい説明

### std::to_string {#to_string}

```cpp
std::string to_string(int value);
std::string to_string(long long value);
std::string to_string(unsigned value);
std::string to_string(float value);
std::string to_string(double value);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `value` | 数値 | 文字列にしたい値 |

- 戻り値: 新しい文字列

```cpp
#include <print>
#include <string>

int main() {
  std::println("{}", std::to_string(42));
  std::println("{}", std::to_string(3.5f));
}
```

```text title="実行結果"
42
3.500000
```

!!! note "実際は"
    浮動小数点は小数点以下 6 桁固定になってしまいます。桁数を指定したいなら `std::format("{:.1f}", 3.5f)` を使います。

## ゲームでの使いどころ

スコアや HP を画面に表示する文字列に変換するのが基本です。`"Score: " + std::to_string(score)` と書けます。

小数は注意が必要です。`std::to_string(1.5f)` は `"1.500000"` で、桁数を指定できません。「1.5」や「1.50」のように見せたいときは、`std::format("{:.2f}", x)` を使います。

毎フレーム大量に呼ぶと、メモリの確保が毎回起きて重くなります。速さが必要なら、`std::to_chars` で用意したバッファに書き込みます。

## よくあるミス

??? failure "小数の桁数を変えようとする"
    `to_string` には桁数の引数がありません。`std::to_string(3.14159)` は `"3.141590"` です。桁数を指定するなら、`std::format("{:.2f}", x)` です。

??? failure "`char` を渡して文字ではなく数値が出る"
    `std::to_string('A')` は `"65"` です。`char` は整数として扱われます。文字を文字列にしたいなら `std::string(1, 'A')` です。

??? failure "毎フレーム大量に呼んで重くなる"
    呼ぶたびに `std::string` を作るので、短い文字列の最適化があっても、数が多いとコストが積み重なります。値が変わったときだけ作り直します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::format`](../utilities/format.md) | 桁数・書式を指定できる |
| [`std::to_chars`](../io/to_chars.md) | 確保なしで速い |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 数値 → 文字列
    - [x] 小数は 6 桁固定
    - [x] 書式を整えるなら format

## 関連ページ

- [cpprefjp: std::to_string](https://cpprefjp.github.io/reference/string/to_string.html)
- [cppreference: std::to_string](https://en.cppreference.com/w/cpp/string/basic_string/to_string)
