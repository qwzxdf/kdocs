---
title: <random>（乱数）
group: 乱数（std::random）
summary: "乱数を作る。シードと分布（一様・正規など）を組み合わせて使う。"
order: 56
tags:
  - ユーティリティ
  - 乱数
---

# &lt;random&gt;（乱数）

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

ゲームには、ダメージの幅、アイテムのドロップ、敵の動きなど、乱数が欠かせません。`rand()` は手軽ですが、品質が低く、偏りもあります。`<random>` は、乱数を作るための標準のライブラリです。乱数は 2 つの部品を組み合わせて作ります。1 つは乱数エンジン（`std::mt19937` など）で、でたらめな整数を次々に作る乱数の源です。もう 1 つは分布（`uniform_int_distribution` など）で、エンジンの出力を必要な範囲と形に変えます。

!!! tip "ポイント"
    - <strong>エンジンは `std::mt19937` を 1 つ作って使い回す。</strong> 種（シード）は `std::random_device{}()` か固定値。
    - 整数は `std::uniform_int_distribution<int> dist(1, 6); dist(rng)`（**両端を含む**）。
    - 小数は `std::uniform_real_distribution<float> dist(0.0f, 1.0f); dist(rng)`（上限は含まない）。
    - 確率で当たり外れは `std::bernoulli_distribution(0.3)`、重み付き抽選は `std::discrete_distribution`。
    - `rand() % 6` は使わない（偏りがあり、品質も低い）。

!!! info "このページを読む前に"
    確率の基本（一様に出る、偏りがある）が分かると読みやすいです。

## 主な型

| 型 | 重要度 | 何をする |
| --- | --- | --- |
| [`std::mt19937`](random/mt19937.md) | <span class="rank rank-must">必須</span> | 乱数エンジン（32 ビット、メルセンヌ・ツイスター） |
| [`std::uniform_int_distribution`](random/uniform_int_distribution.md) | <span class="rank rank-must">必須</span> | 範囲内の整数を同じ確率で |
| [`std::uniform_real_distribution`](random/uniform_real_distribution.md) | <span class="rank rank-must">必須</span> | 範囲内の小数を同じ確率で |
| [`std::random_device`](random/random_device.md) | <span class="rank rank-often">よく使う</span> | 本物に近い乱数（種を作る用） |
| [`std::bernoulli_distribution`](random/bernoulli_distribution.md) | <span class="rank rank-often">よく使う</span> | 確率 p で true |
| [`std::discrete_distribution`](random/discrete_distribution.md) | <span class="rank rank-sometimes">たまに</span> | 重み付きで添字を選ぶ（ガチャ・ドロップ） |
| [`std::normal_distribution`](random/normal_distribution.md) | <span class="rank rank-sometimes">たまに</span> | 正規分布（平均付近が出やすい） |
| [`std::mt19937_64`](random/mt19937.md) | <span class="rank rank-rare">知ってるだけ</span> | 64 ビット版エンジン |

## 関数一覧

エンジンと分布の共通の使い方です。

| 関数 | 重要度 | 対象 | 何をする |
| --- | --- | --- | --- |
| `dist(engine)` | <span class="rank rank-must">必須</span> | 分布 | 乱数を 1 つ作る |
| [`engine.seed(s)`](random/mt19937.md) | <span class="rank rank-sometimes">たまに</span> | エンジン | 種を設定し直す |
| `engine()` | <span class="rank rank-sometimes">たまに</span> | エンジン | 生の整数を 1 つ作る |
| `dist.reset()` | <span class="rank rank-rare">知ってるだけ</span> | 分布 | 内部状態をリセット |
| `dist.min()` / `dist.max()` | <span class="rank rank-rare">知ってるだけ</span> | 分布・エンジン | 出る値の範囲 |
| [`engine.discard(n)`](random/mt19937.md) | <span class="rank rank-rare">知ってるだけ</span> | エンジン | n 回ぶん読み飛ばす |

## よくある使い方

### 1. サイコロと小数

```cpp
#include <print>
#include <random>

int main() {
  std::mt19937 rng(42);  // 種を固定（毎回同じ結果。デバッグ・リプレイ用）

  std::uniform_int_distribution<int> dice(1, 6);
  std::uniform_real_distribution<float> unit(0.0f, 1.0f);

  int roll = dice(rng);
  float r = unit(rng);
  std::println("サイコロは 1〜6？ {} / 小数は 0〜1？ {}", roll >= 1 && roll <= 6,
               r >= 0.0f && r < 1.0f);
}
```

```text title="実行結果"
サイコロは 1〜6？ true / 小数は 0〜1？ true
```

同じ種でも、**分布の結果は標準ライブラリ（コンパイラ）によって違う**ことがあります。エンジンの生の値（`rng()`）は規格で決まっていて、どこでも同じです。

### 2. 乱数をまとめたクラス

```cpp
#include <print>
#include <random>

class Random {
 public:
  explicit Random(unsigned seed) : engine_(seed) {}

  int Range(int min, int max) {  // min〜max（両端を含む）
    return std::uniform_int_distribution<int>(min, max)(engine_);
  }
  float Unit() { return std::uniform_real_distribution<float>(0.0f, 1.0f)(engine_); }
  bool Chance(double p) { return std::bernoulli_distribution(p)(engine_); }

 private:
  std::mt19937 engine_;
};

int main() {
  Random random(std::random_device{}());
  int damage = random.Range(8, 12);
  bool critical = random.Chance(0.0);  // 確率 0 なので必ず false
  std::println("ダメージ 8〜12？ {} / 会心 {}", damage >= 8 && damage <= 12, critical);
}
```

```text title="実行結果"
ダメージ 8〜12？ true / 会心 false
```

## フラグ・オプション（エンジンと分布の一覧）

### エンジン

| 型 | 重要度 | 特徴 |
| --- | --- | --- |
| `std::mt19937` | <span class="rank rank-must">必須</span> | 定番。品質が良く速い。約 5KB |
| `std::random_device` | <span class="rank rank-often">よく使う</span> | OS の乱数。遅い。種用 |
| `std::mt19937_64` | <span class="rank rank-rare">知ってるだけ</span> | 64 ビット版 |
| `std::minstd_rand` | <span class="rank rank-rare">知ってるだけ</span> | とても小さく速いが品質は低い |
| `std::default_random_engine` | <span class="rank rank-rare">知ってるだけ</span> | 実装によって中身が違う。使わない |
| `std::ranlux24` / `ranlux48` | <span class="rank rank-rare">知ってるだけ</span> | 品質は高いが遅い |
| `std::knuth_b` | <span class="rank rank-rare">知ってるだけ</span> | 古いエンジン |

### 分布

| 型 | 重要度 | 出る値 | 使う場面 |
| --- | --- | --- | --- |
| `uniform_int_distribution` | <span class="rank rank-must">必須</span> | a〜b の整数（両端含む） | サイコロ、ランダムな添字 |
| `uniform_real_distribution` | <span class="rank rank-must">必須</span> | a 以上 b 未満の小数 | 角度、位置、0〜1 |
| `bernoulli_distribution` | <span class="rank rank-often">よく使う</span> | 確率 p で true | 会心、命中、ドロップ判定 |
| `discrete_distribution` | <span class="rank rank-sometimes">たまに</span> | 重みに従って添字 | ガチャ、ドロップテーブル、AI の行動選択 |
| `normal_distribution` | <span class="rank rank-sometimes">たまに</span> | 平均付近が出やすい小数 | 弾のばらつき、個体差 |
| `exponential_distribution` | <span class="rank rank-rare">知ってるだけ</span> | 待ち時間 | 次の敵が出るまでの時間 |
| `poisson_distribution` | <span class="rank rank-rare">知ってるだけ</span> | 一定時間に起きる回数 | 1 分間に出現する敵の数 |
| `binomial_distribution` | <span class="rank rank-rare">知ってるだけ</span> | n 回中の当たり回数 | 10 連続攻撃の命中数 |
| `geometric_distribution` | <span class="rank rank-rare">知ってるだけ</span> | 初めて当たるまでの失敗回数 | |
| `piecewise_constant_distribution` / `piecewise_linear_distribution` | <span class="rank rank-rare">知ってるだけ</span> | 区間ごとに確率を変えた小数 | |
| `lognormal_distribution` / `gamma_distribution` / `weibull_distribution` など | <span class="rank rank-rare">知ってるだけ</span> | 統計用の分布 | ほぼ使わない |

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    srand(time(nullptr));
    int dice = rand() % 6 + 1;              // 偏りがある、品質が低い
    float r = rand() / (float)RAND_MAX;     // RAND_MAX が 32767 の環境もある
    ```

=== "今の書き方"

    ```cpp
    std::mt19937 rng(std::random_device{}());
    int dice = std::uniform_int_distribution<int>(1, 6)(rng);
    float r = std::uniform_real_distribution<float>(0.0f, 1.0f)(rng);
    ```

## ゲームでの使いどころ

ダメージの幅やドロップは、整数の一様分布（`uniform_int_distribution`）で作ります。会心などの判定は `bernoulli_distribution`、重みのある抽選は `discrete_distribution` です。ばらつきのある値（敵の個体差）には `normal_distribution` を使います。

エンジンは 1 つ作って使い回します。種を固定すれば、同じ乱数列が出て、リプレイやバグの再現に役立ちます。戦闘用と見た目用でエンジンを分けると、見た目の乱数の使い方が変わっても、戦闘の結果は変わりません。

種を作るには `random_device` を使います。エンジンを毎回作り直したり、`rand() % n` で範囲を作ったりしないことが基本です。

## パフォーマンス

- `mt19937` は 1 回の生成がとても速いですが、作るのは重い（約 5KB の初期化）ので使い回します。
- 分布オブジェクトは軽いので、その場で作っても問題ありません。
- `random_device` は遅い（OS に問い合わせる）ことがあるので、種を作るときにだけ使います。

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| `uniform_int_distribution(a, b)` で `a > b` | 未定義動作 |
| `uniform_real_distribution(a, b)` で `a >= b` | 未定義動作 |
| `bernoulli_distribution(p)` で p が 0〜1 の外 | 未定義動作 |

## よくあるミス

??? failure "関数の中で毎回エンジンを作る"
    ```cpp
    int RollDice() {
      std::mt19937 rng(std::random_device{}());  // 毎回 5KB の初期化。遅い
      return std::uniform_int_distribution<int>(1, 6)(rng);
    }
    ```

    エンジンはメンバ変数や `static` にして使い回します。

??? failure "uniform_int_distribution の上限を含まないと思う"
    `uniform_int_distribution<int>(0, 10)` は 0〜10（11 通り）です。添字に使うなら `(0, size - 1)` にします。

??? failure "マルチプレイ・リプレイで結果がずれる"
    分布の結果はコンパイラによって違うことがあります。完全に同じ結果が必要なら、エンジンの生の値から自分で範囲を作るか、乱数ライブラリを固定します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::shuffle`](../algorithms/shuffle.md) | 範囲全体をランダムに並べ替える |
| `rand()` | C の乱数。使わない |

## コンパイラ対応

C++11 からある機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] エンジン `std::mt19937` を 1 つ作って使い回す
    - [x] 整数は `uniform_int_distribution(a, b)`（両端含む）
    - [x] 小数は `uniform_real_distribution(a, b)`（上限含まない）
    - [x] 確率判定は `bernoulli`、重み付きは `discrete`

## 関連ページ

- [cpprefjp: <random>](https://cpprefjp.github.io/reference/random.html)
- [cppreference: Pseudo-random number generation](https://en.cppreference.com/w/cpp/numeric/random)
