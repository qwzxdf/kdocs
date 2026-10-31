---
title: std::mersenne_twister_engine
summary: "メルセンヌ・ツイスタの乱数エンジンのテンプレート（`mt19937` の元）。"
order: 900
group: 乱数エンジン
tags:
  - ユーティリティ
---

# std::mersenne_twister_engine

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <chrono>`
</div>

`std::mt19937` は、ゲームで最もよく使われる乱数エンジンです。その中身が、13 個のパラメータを持つこの `std::mersenne_twister_engine` です。通常は、パラメータが決まった別名の `mt19937` か `mt19937_64` を使い、このテンプレートを直接書くことはありません。パラメータを読み解いておくと、状態の大きさや周期の根拠が分かります。

!!! tip "ポイント"
    - `mt19937` は 32 ビット版、`mt19937_64` は 64 ビット版。普段はこの 2 つを使う
    - 周期は 2^19937 - 1 で、実質的に使い切れない
    - 状態は `n` 個の `w` ビット整数。`mt19937` は 624 個（約 2.5 KB）
    - 暗号用ではない。出力から状態を推測できる

!!! info "このページを読む前に"
    [`std::mt19937`](mt19937.md) を先に読んでください。

## 関数の詳しい説明

### std::mersenne_twister_engine {#mersenne_twister_engine}

<span class="ver ver-11">C++11</span>

```cpp
template <class UIntType, size_t w, size_t n, size_t m, size_t r,
          UIntType a, size_t u, UIntType d, size_t s, UIntType b,
          size_t t, UIntType c, size_t l, UIntType f>
class mersenne_twister_engine;
```

### パラメータの意味 {#params}

| 引数 | 意味 |
| --- | --- |
| `w` | 1 語のビット数（32 または 64） |
| `n` | 状態の語数。`mt19937` は 624 |
| `m` | 状態の更新で参照する、離れた位置（397） |
| `r` | 上位と下位に分けるビット数（31） |
| `a` | 変換の係数（0x9908b0df） |
| `u`, `d`, `s`, `b`, `t`, `c`, `l` | 出力を整えるためのビット操作（テンパリング）の定数 |
| `f` | 種から状態を初期化するときの係数（1812433253） |

実際に使うには、定評のある値の組み合わせをそのまま使います。自分で選ぶと、周期が短くなる、品質が落ちる、といった問題が起きやすいです。

### 状態と周期 {#state}

状態は、`n` 個の `w` ビットの整数です。`mt19937` は 624 個の 32 ビットなので、約 2.5 KB です。エンジンをコピーすると、この状態も全部コピーされます。関数の引数に値渡しすると、毎回 2.5 KB のコピーが起きるので、参照で渡します。

周期は 2^19937 - 1 です。1 秒に 10 億個を使っても、宇宙の年齢の何桁も上の時間がかかります。

### 種 {#seed}

既定の種は 5489 です。`seed(値)` で 1 つの整数から初期化するほか、`std::seed_seq` で複数の値から初期化できます。32 ビットの 1 つの種から作れる列は、約 43 億通りです。それ以上の多様性が欲しいときは、`seed_seq` に `random_device` の値を複数渡します。

## 実際に動かしてみる

```cpp
#include <cstdint>
#include <print>
#include <random>

int main() {
  // mt19937 と同じパラメータ
  using MT = std::mersenne_twister_engine<std::uint_fast32_t, 32, 624, 397, 31, 0x9908b0df, 11,
                                          0xffffffff, 7, 0x9d2c5680, 15, 0xefc60000, 18,
                                          1812433253>;
  MT e;
  e.discard(9999);
  std::println("{}", e());  // 10000 回目の値（標準で決まっている）

  std::println("語のビット数: {} 状態の語数: {}", MT::word_size, MT::state_size);
  std::println("mt19937 と同じ型の動き: {}", MT{}() == std::mt19937{}());
}
```

```text title="実行結果"
4123659995
語のビット数: 32 状態の語数: 624
mt19937 と同じ型の動き: true
```

10000 回目の値 `4123659995` は、規格が決めている値です。

## ゲームでの使いどころ

テンプレートを直接使うことは、まずありません。`std::mt19937` を使います。

## よくあるミス

??? failure "パラメータを自分で選ぶ"
    周期や品質が保証されません。`mt19937` / `mt19937_64` を使います。

??? failure "エンジンを値渡しする"
    2.5 KB のコピーが起き、さらに呼び出し側のエンジンが進みません。参照で渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`mt19937`](mt19937.md) | 32 ビット版の別名 |
| [`mt19937_64`](mt19937_64.md) | 64 ビット版の別名 |
| [`linear_congruential_engine`](linear_congruential_engine.md) | 軽いが、品質は劣る |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::mersenne_twister_engine](https://cpprefjp.github.io/reference/random/mersenne_twister_engine.html)
- [cppreference: std::mersenne_twister_engine](https://en.cppreference.com/w/cpp/numeric/random/mersenne_twister_engine)
