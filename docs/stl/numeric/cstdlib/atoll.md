---
title: std::atoll
summary: "文字列を long long に変換する。"
order: 900
tags:
  - 数値
---

# std::atoll

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

`atoi` の `long long` 版です。失敗しても 0 を返します。

!!! tip "ポイント"
    - C 由来の関数。
    - 失敗の知らせ方は関数ごとに違う。
    - 新しいコードでは `std::from_chars` や `std::string` が安全。

!!! info "このページを読む前に"
    [`std::atoi`](atoi.md) を先に読んでください。

## 関数の詳しい説明

### std::atoll {#atoll}

```cpp
long long atoll(const char* str);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | const char* | 変換する文字列 |

- 戻り値: 変換した値（失敗したら 0）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  std::println("{}", std::atoll("9000000000"));
}
```

```text title="実行結果"
9000000000
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 大きな ID の読み取り |

## よくあるミス

??? failure "失敗を 0 と区別できない"
    エラーを知りたいなら `strtoll` や `std::from_chars`。

## 類似

| 名前 | 違い |
| --- | --- |
| [`atoi`](atoi.md) | int の版 |
| [`strtoll`](strtoll.md) | エラーが分かる版 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字列を long long に変換する
    - [x] C 由来の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::atoll](https://cpprefjp.github.io/reference/cstdlib/atoll.html)
- [cppreference: std::atoll](https://en.cppreference.com/w/cpp/c/atoll)
