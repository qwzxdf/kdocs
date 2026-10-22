---
title: std::to_wstring
summary: "数値を wstring に変換する。"
order: 900
tags:
  - コンテナ
---

# std::to_wstring

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <string>`
</div>

`std::to_string` の `wstring` 版です。Windows の API に数値を文字列で渡すときなどに使います。整数と浮動小数点のオーバーロードがあります。

!!! tip "ポイント"
    - `to_string` の `wchar_t` 版。
    - 小数は固定小数点の形（`%f` 相当）で出る。
    - 書式を指定したいなら `std::format`。

!!! info "このページを読む前に"
    [`std::string`](string.md) を先に読んでください。

## 関数の詳しい説明

### std::to_wstring {#to_wstring}

```cpp
std::wstring to_wstring(int value);
std::wstring to_wstring(double value);  // ほかの整数・浮動小数点型もある
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `value` | 数値 | 変換する数値 |

- 戻り値: 変換した `wstring`
- 計算量: O(桁数)


## 実際に動かしてみる

```cpp
#include <print>
#include <string>

int main() {
  std::wstring w = std::to_wstring(42);
  std::println("{}", w.size());
}
```

```text title="実行結果"
2
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| Windows API に数値を文字列で渡す | `std::to_wstring(value)` |

## よくあるミス

??? failure "小数の桁数を指定したい"
    `to_wstring(3.5)` は `3.500000` になります。桁数は `std::format` で指定します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`to_string`](to_string.md) | char の版 |
| [`format`](../utilities/format.md) | 書式を指定する |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 数値を wstring に
    - [x] to_string の wchar_t 版
    - [x] 書式は format

## 関連ページ

- [cpprefjp: std::to_wstring](https://cpprefjp.github.io/reference/string/to_wstring.html)
- [cppreference: std::to_wstring](https://en.cppreference.com/w/cpp/string/basic_string/to_wstring)
