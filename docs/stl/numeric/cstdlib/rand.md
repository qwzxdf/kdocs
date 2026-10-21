---
title: std::rand
summary: "乱数を作る古い関数（品質が低いので使わない）。"
order: 4
group: <cstdlib> の関数
tags:
  - 数値
---

# std::rand

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cstdlib>`
</div>

`std::rand` は、**0〜`RAND_MAX` の乱数を返す**C 由来の関数です。`srand` で種を設定します。**品質が低く、`% n` で偏りが出る**ので、ゲームでは使わず、[`std::mt19937`](../../utilities/random/mt19937.md) と分布を使います。

!!! tip "ポイント"
    - `rand() % 6` は偏る。
    - `RAND_MAX` が小さい環境（Windows は 32767）がある。
    - 新しいコードでは `<random>`。

## 関数の詳しい説明

### std::rand {#rand}

```cpp
int rand();
void srand(unsigned seed);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `seed` | `unsigned` | 乱数の種 |

- 戻り値: 0 以上 `RAND_MAX` 以下の整数
- 計算量: O(1)

```cpp
#include <cstdlib>
#include <print>

int main() {
  std::srand(1);
  int v = std::rand();
  std::println("{}", v >= 0 && v <= RAND_MAX);   // 値そのものは環境で違う
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 古いコードの読解 | `std::mt19937` + `uniform_int_distribution` に置き換える |

## よくあるミス

??? failure "rand() % n で範囲を作る"
    偏ります。`uniform_int_distribution` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::mt19937`](../../utilities/random/mt19937.md) | 良い乱数エンジン |
| [`uniform_int_distribution`](../../utilities/random/uniform_int_distribution.md) | 範囲の整数 |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 古い乱数。使わない
    - [x] `% n` は偏る
    - [x] 新しいコードは <random>

## 関連ページ

- [cpprefjp: std::rand](https://cpprefjp.github.io/reference/cstdlib/rand.html)
- [cppreference: std::rand](https://en.cppreference.com/w/cpp/numeric/math/rand)
