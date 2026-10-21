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

`std::to_string` は、**数値（整数・小数）を `std::string` に変換する**関数です。表示用の文字列を作るときに使います。ただし、小数は桁数を指定できず（6 桁固定）、確保も起きるので、書式を整えたいときは [`std::format`](../utilities/format.md) を使います。

!!! tip "ポイント"
    - 小数は小数点以下 6 桁固定（`1.5f` → `"1.500000"`）。
    - 桁を指定したいなら `std::format("{:.2f}", x)`。
    - 速さが必要なら [`std::to_chars`](../io/to_chars.md)。

!!! info "このページを読む前に"
    [`std::string`](string.md) を先に読んでください。

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

| 場面 | 書き方 |
| --- | --- |
| 数値を文字列に連結する | `"Lv." + std::to_string(level)` |

## よくあるミス

??? failure "小数の見た目を期待する"
    `std::to_string(0.5f)` は `"0.500000"` です。

??? failure "毎フレーム大量に呼ぶ"
    呼ぶたびに確保が起きます。`to_chars` かバッファの再利用を考えます。

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
