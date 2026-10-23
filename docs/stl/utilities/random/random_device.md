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

乱数エンジンは、種（シード）を決めないと、起動のたびに同じ乱数列を出します。毎回違う乱数にしたいなら、種を予測できない値にする必要があります。`std::random_device` は、OS が用意する予測しにくい乱数を出すクラスです。ハードウェアのノイズなどを使うので質が高い反面、遅いことがあります。エンジンの種を作る場面だけで使い、実際の乱数は `mt19937` などに任せます。

!!! tip "ポイント"
    - 定番の書き方は `std::mt19937 rng(std::random_device{}());`。
    - ゲーム中に何度も呼ばない（遅い）。起動時の 1 回だけ。
    - 環境によっては、毎回同じ値を返す古い実装がある（`entropy()` が 0）。現代の GCC / MSVC / Clang では問題ない。

!!! info "このページを読む前に"
    [`std::mt19937`](mt19937.md) の乱数エンジンの役割を先に読んでください。`random_device` は、その種を作る部品です。

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

## しくみ

`random_device` は、OS の乱数源（Windows なら `BCryptGenRandom`、Linux なら `/dev/urandom` や `getrandom`）を呼びます。呼び出しごとにシステムの助けを借りるので、`mt19937` より桁違いに遅くなります。

定番の使い方は、`std::mt19937 rng(std::random_device{}());` です。32 ビットの値を 1 つ取って、それを種にします。この方法だと、種の候補が 40 億通りしかありませんが、ゲームの用途では十分です。

`entropy()` は、乱数源の質を示す値ですが、実装によって意味が違い、当てにならないことがあります。

## ゲームでの使いどころ

ゲームの起動時に、乱数エンジンの種を作るために 1 回だけ使います。ステージやダンジョンを生成するときの種としても使います。生成に使った種をセーブデータに保存しておけば、同じステージを再現できます。

テストやデバッグのときは、種を固定の値にして、毎回同じ乱数列にします。バグが乱数に依存しているときに、再現しやすくなります。

暗号に使う乱数（トークンなど）には、`random_device` を直接使うほうが適切です。ただし、ゲームの通信の認証などは、専用のライブラリに任せるのが安全です。

## よくあるミス

??? failure "ゲーム中に何度も呼んで遅くなる"
    毎フレームの乱数に `random_device` を使うと、OS を呼ぶコストが積み重なります。起動時に 1 回だけ使い、あとはエンジンに任せます。

??? failure "毎回同じ値になる古い実装を知らない"
    MinGW の古い版では、`random_device` が毎回同じ値を返すことがありました。現代の MSVC、GCC、Clang では問題ありませんが、疑わしいときは時刻を併用します。

??? failure "種を 1 つの 32 ビット値だけにする"
    `mt19937` の内部状態は 624 個の値を持ちますが、種が 1 つだと、状態の候補が少なくなります。ゲームの用途では問題ないので、気にするのは暗号などに限られます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`mt19937`](mt19937.md) | 実際の乱数を出すエンジン。種を `random_device` から作る |
| `std::seed_seq` | 複数の値から種を作る。`mt19937` の初期化の質を上げる |
| [`uniform_int_distribution`](uniform_int_distribution.md) | エンジンの出力を範囲に変える |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] エンジンの種を作るときだけ使う。
    - [x] ゲーム中に何度も呼ばない。遅い。
    - [x] 再現したいときは、種を固定してセーブデータに残す。

## 関連ページ

- [cpprefjp: std::random_device](https://cpprefjp.github.io/reference/random/random_device.html)
- [cppreference: std::random_device](https://en.cppreference.com/w/cpp/numeric/random/random_device)
