---
title: std::srand
summary: "rand() の乱数の並びを、シードで初期化する。"
order: 900
tags:
  - 数値
---

# std::srand

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

`rand()` は、`srand` に与えたシードから決まる並びを返します。同じシードなら同じ並びなので、再現したいときに便利ですが、本格的な乱数には `<random>` を使います。

!!! tip "ポイント"
    - C 由来の関数。
    - 失敗の知らせ方は関数ごとに違う。
    - 新しいコードでは `std::from_chars` や `std::string` が安全。

!!! info "このページを読む前に"
    [`std::atoi`](atoi.md) を先に読んでください。

## 関数の詳しい説明

### std::srand {#srand}

```cpp
void srand(unsigned seed);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `seed` | unsigned | 初期値 |

- 戻り値: なし
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  std::srand(42);
  int a = std::rand();
  std::srand(42);
  int b = std::rand();
  std::println("{}", a == b);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | テストで同じ乱数を再現する |

## よくあるミス

??? failure "`time(nullptr)` を何度も呼ぶ"
    1 秒に何度も `srand(time(nullptr))` すると同じ値が続きます。起動時に 1 回だけ呼びます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`rand`](rand.md) | 乱数を取る |
| [`std::mt19937`](../../utilities/random/mt19937.md) | 高品質な乱数 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] rand() の乱数の並びを、シードで初期化する
    - [x] C 由来の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::srand](https://cpprefjp.github.io/reference/cstdlib/srand.html)
- [cppreference: std::srand](https://en.cppreference.com/w/cpp/c/srand)
