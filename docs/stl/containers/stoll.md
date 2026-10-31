---
title: std::stoll
summary: "文字列を long long に変換する（失敗すると例外）。"
order: 64
group: 文字列と数値の変換
tags:
  - コンテナ
---

# std::stoll

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++11</span>
`#include <string>`
</div>

`std::stoll(str)` は、文字列を `long long`（64 ビット以上）に変換します。Windows の `long` は 32 ビットなので、大きな数を扱うなら `stoll` を使います。

!!! tip "ポイント"
    - `long long` に変換する
    - `long` が 32 ビットの環境（Windows）でも、64 ビットを読める
    - 例外の規則は `stol` と同じ
    - 第 3 引数 `base` で、進数を指定する

!!! info "このページを読む前に"
    [`std::string`](string.md) を先に読んでください。

## 関数の詳しい説明

### std::stoll {#stoll}

<span class="ver ver-11">C++11</span>

```cpp
long long stoll(const std::string& str, std::size_t* pos = nullptr, int base = 10);
```

引数の意味は `stol` と同じです。範囲を超える値は `std::out_of_range` です。

ID やタイムスタンプ（Unix 時間のミリ秒など）のように、32 ビットに収まらない値は、`stoll` を使います。ファイルサイズのバイト数も同様です。

## 実際に動かしてみる

```cpp
#include <print>
#include <stdexcept>
#include <string>

int main() {
  std::println("{}", std::stoll("9000000000"));  // 32 ビットを超える
  std::println("{}", std::stoll("-123"));

  try {
    std::stoll("99999999999999999999");  // long long にも収まらない
  } catch (const std::out_of_range&) {
    std::println("範囲外: out_of_range");
  }
}
```

```text title="実行結果"
9000000000
-123
範囲外: out_of_range
```

## ゲームでの使いどころ

64 ビットの ID や時刻を、文字列から読むときに使います。

## よくあるミス

??? failure "stol で大きな値を読む"
    Windows では 32 ビットに収まらず、`out_of_range` になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`stol`](stol.md) | `long` |
| [`stoull`](stoull.md) | 符号なし 64 ビット |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::stoll](https://cpprefjp.github.io/reference/string/stoll.html)
- [cppreference: std::stoll](https://en.cppreference.com/w/cpp/string/basic_string/stoll)
