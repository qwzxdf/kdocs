---
title: std::atol
summary: "文字列を long に変換する。"
order: 900
tags:
  - 数値
---

# std::atol

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

`atoi` の `long` 版です。失敗しても例外を出さず 0 を返すので、失敗が区別できません。

!!! tip "ポイント"
    - C 由来の関数。
    - 失敗の知らせ方は関数ごとに違う。
    - 新しいコードでは `std::from_chars` や `std::string` が安全。

!!! info "このページを読む前に"
    [`std::atoi`](atoi.md) を先に読んでください。

## 関数の詳しい説明

### std::atol {#atol}

```cpp
long atol(const char* str);
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
  std::println("{}", std::atol("123456"));
}
```

```text title="実行結果"
123456
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 古い C のコードの数値の読み取り |

## よくあるミス

??? failure "失敗を 0 と区別できない"
    `"abc"` も `"0"` も 0 になります。エラーを知りたいなら `strtol` や `std::from_chars`。

## 類似

| 名前 | 違い |
| --- | --- |
| [`atoi`](atoi.md) | int の版 |
| [`strtol`](strtol.md) | エラーが分かる版 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字列を long に変換する
    - [x] C 由来の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::atol](https://cpprefjp.github.io/reference/cstdlib/atol.html)
- [cppreference: std::atol](https://en.cppreference.com/w/cpp/c/atol)
