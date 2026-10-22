---
title: std::random_device
summary: "OS が用意する、予測しにくい乱数。エンジンの種を作るのに使う。"
order: 2
group: 乱数エンジン
tags:
  - ユーティリティ
---

# std::random_device

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

`std::random_device` は、**OS が用意する、予測しにくい乱数**を出すクラスです。ハードウェアのノイズなどを使うので、質が高い代わりに**遅い**ことがあります。そこで、**エンジンの種を作るときだけ**使い、実際の乱数は [`mt19937`](mt19937.md) などのエンジンに任せます。

!!! tip "ポイント"
    - 定番の書き方は `std::mt19937 rng(std::random_device{}());`。
    - ゲーム中に何度も呼ばない（遅い）。起動時の 1 回だけ。
    - 環境によっては、毎回同じ値を返す古い実装がある（`entropy()` が 0）。現代の GCC / MSVC / Clang では問題ない。

!!! info "このページを読む前に"
    [`<random>`](../random.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::random_device {#random_device}

```cpp
class random_device {
 public:
  using result_type = unsigned int;
  random_device();
  result_type operator()();
  double entropy() const noexcept;
};
```

- 戻り値: `operator()` で `unsigned int` の乱数を 1 つ返す
- 計算量: O(1)（OS による。遅いことがある）

```cpp
#include <print>
#include <random>

int main() {
  std::random_device rd;
  std::println("範囲 {} 〜 {}", rd.min(), rd.max());

  std::mt19937 rng(rd());  // 種として使う
  std::println("{}", rng() <= rng.max());
}
```

```text title="実行結果"
範囲 0 〜 4294967295
true
```

### operator() {#op_call}

```cpp
result_type operator()();
```

- 計算量: OS に依存

非決定的な乱数（ハードウェアや OS のエントロピー源）を 1 つ返します。シード用に使います。実装によっては遅い、あるいは決定的になる環境もあります。

### entropy {#entropy}

```cpp
double entropy() const noexcept;
```

- 計算量: 定数

乱数源のエントロピーの見積もり（ビット数）。決定的な実装では 0 を返します。当てにならないことが多いです。

### min {#min}

```cpp
static constexpr result_type min();
```

- 計算量: 定数

`operator()` が返しうる最小値。

### max {#max}

```cpp
static constexpr result_type max();
```

- 計算量: 定数

`operator()` が返しうる最大値。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 起動時に、毎回違うゲームの乱数を作る | `std::mt19937 rng(std::random_device{}());` |

## よくあるミス

??? failure "毎フレーム random_device から値を取る"
    遅く、OS の乱数源を消費します。エンジンに任せます。

??? failure "種を 32 ビットだけにする"
    `mt19937` の状態は 624 個ありますが、種 1 つだと 32 ビット分の違いしか出ません。たくさんの種が欲しいときは `std::seed_seq` に複数の値を渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::mt19937`](mt19937.md) | 乱数エンジン |
| [`std::seed_seq`](seed_seq.md) | 複数の値から種を作る |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] OS の予測しにくい乱数
    - [x] 種を作るときだけ使う
    - [x] 起動時に 1 回

## 関連ページ

- [cpprefjp: std::random_device](https://cpprefjp.github.io/reference/random/random_device.html)
- [cppreference: std::random_device](https://en.cppreference.com/w/cpp/numeric/random/random_device)
