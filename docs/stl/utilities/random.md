---
title: <random>（乱数）
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

`<random>` は、**乱数を作るためのライブラリ**です。乱数は 2 つの部品を組み合わせて作ります。1 つは**乱数エンジン**（`std::mt19937` など）で、でたらめな整数を次々に作る「乱数の源」です。もう 1 つは**分布**（`std::uniform_int_distribution` など）で、エンジンの出した整数を「1〜6 のサイコロ」「0.0〜1.0 の小数」のような欲しい形に整えます。

!!! tip "ポイント"
    - <strong>エンジンは `std::mt19937` を 1 つ作って使い回す。</strong> 種（シード）は `std::random_device{}()` か固定値。
    - 整数は `std::uniform_int_distribution<int> dist(1, 6); dist(rng)`（**両端を含む**）。
    - 小数は `std::uniform_real_distribution<float> dist(0.0f, 1.0f); dist(rng)`（上限は含まない）。
    - 確率で当たり外れは `std::bernoulli_distribution(0.3)`、重み付き抽選は `std::discrete_distribution`。
    - `rand() % 6` は使わない（偏りがあり、品質も低い）。

## 主な型

| 型 | 重要度 | 何をする |
| --- | --- | --- |
| [`std::mt19937`](#mt19937) | <span class="rank rank-must">必須</span> | 乱数エンジン（32 ビット、メルセンヌ・ツイスター） |
| [`std::uniform_int_distribution`](#uniform_int) | <span class="rank rank-must">必須</span> | 範囲内の整数を同じ確率で |
| [`std::uniform_real_distribution`](#uniform_real) | <span class="rank rank-must">必須</span> | 範囲内の小数を同じ確率で |
| [`std::random_device`](#random_device) | <span class="rank rank-often">よく使う</span> | 本物に近い乱数（種を作る用） |
| [`std::bernoulli_distribution`](#bernoulli) | <span class="rank rank-often">よく使う</span> | 確率 p で true |
| [`std::discrete_distribution`](#discrete) | <span class="rank rank-sometimes">たまに</span> | 重み付きで添字を選ぶ（ガチャ・ドロップ） |
| [`std::normal_distribution`](#normal) | <span class="rank rank-sometimes">たまに</span> | 正規分布（平均付近が出やすい） |
| [`std::mt19937_64`](#mt19937_64) | <span class="rank rank-rare">知ってるだけ</span> | 64 ビット版エンジン |

## 関数一覧

エンジンと分布の共通の使い方です。

| 関数 | 重要度 | 対象 | 何をする |
| --- | --- | --- | --- |
| [`dist(engine)`](#call) | <span class="rank rank-must">必須</span> | 分布 | 乱数を 1 つ作る |
| [`engine.seed(s)`](#seed) | <span class="rank rank-sometimes">たまに</span> | エンジン | 種を設定し直す |
| [`engine()`](#engine-call) | <span class="rank rank-sometimes">たまに</span> | エンジン | 生の整数を 1 つ作る |
| [`dist.reset()`](#reset) | <span class="rank rank-rare">知ってるだけ</span> | 分布 | 内部状態をリセット |
| [`dist.min()` / `dist.max()`](#minmax) | <span class="rank rank-rare">知ってるだけ</span> | 分布・エンジン | 出る値の範囲 |
| [`engine.discard(n)`](#discard) | <span class="rank rank-rare">知ってるだけ</span> | エンジン | n 回ぶん読み飛ばす |

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

## 型と関数の詳しい説明

### std::mt19937 {#mt19937}

```cpp
using mt19937 = std::mersenne_twister_engine<std::uint_fast32_t, 32, 624, 397, 31, /* ... */>;
```

| コンストラクタ引数 | 意味 |
| --- | --- |
| 種（`unsigned`） | 乱数の出発点。同じ種なら同じ列が出る。省略すると `5489` |

- 品質が良く速い、定番のエンジンです。大きさは約 5KB あるので、**関数のたびに作らない**

```cpp
#include <print>
#include <random>

int main() {
  std::mt19937 a(1);
  std::mt19937 b(1);
  std::println("同じ種なら同じ値？ {}", a() == b());
  std::mt19937 c;  // 種を省略すると 5489
  std::println("{}", c());
}
```

```text title="実行結果"
同じ種なら同じ値？ true
3499211612
```

### std::uniform_int_distribution {#uniform_int}

```cpp
template <class IntType = int>
class uniform_int_distribution {
 public:
  explicit uniform_int_distribution(IntType a, IntType b = std::numeric_limits<IntType>::max());
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `a` | 整数 | 最小値（**含む**） |
| `b` | 整数 | 最大値（**含む**） |

- `a` 〜 `b` の整数が同じ確率で出ます。`a > b` は未定義動作

### std::uniform_real_distribution {#uniform_real}

```cpp
template <class RealType = double>
class uniform_real_distribution {
 public:
  explicit uniform_real_distribution(RealType a, RealType b = 1.0);
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `a` | 浮動小数点 | 最小値（含む） |
| `b` | 浮動小数点 | 最大値（**含まない**） |

```cpp
#include <print>
#include <random>

int main() {
  std::mt19937 rng(7);
  std::uniform_real_distribution<float> angle(0.0f, 360.0f);
  float a = angle(rng);
  std::println("0 以上 360 未満？ {}", a >= 0.0f && a < 360.0f);
}
```

```text title="実行結果"
0 以上 360 未満？ true
```

### std::random_device {#random_device}

```cpp
class random_device {
 public:
  result_type operator()();
};
```

- OS が用意する、予測しにくい乱数です。遅いので、**エンジンの種を作るのにだけ**使います
- `std::mt19937 rng(std::random_device{}());` が定番の書き方です

### std::bernoulli_distribution {#bernoulli}

```cpp
class bernoulli_distribution {
 public:
  explicit bernoulli_distribution(double p = 0.5);
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `double` | true が出る確率（0.0〜1.0） |

```cpp
#include <print>
#include <random>

int main() {
  std::mt19937 rng(3);
  std::bernoulli_distribution always(1.0);
  std::bernoulli_distribution never(0.0);
  std::println("{} {}", always(rng), never(rng));
}
```

```text title="実行結果"
true false
```

!!! note "実際は"
    「30% で会心」「5% でレアドロップ」のような判定は、`uniform_real(0,1) < 0.3f` と書くより、こちらのほうが意図がはっきりします。

### std::discrete_distribution {#discrete}

```cpp
template <class IntType = int>
class discrete_distribution {
 public:
  discrete_distribution(std::initializer_list<double> weights);
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `weights` | 重みのリスト | i 番目が出る確率は「i 番目の重み ÷ 重みの合計」 |

- 戻り値: 選ばれた**添字**（0 始まり）

```cpp
#include <array>
#include <print>
#include <random>
#include <string>

int main() {
  std::array<std::string, 3> rarity = {"ノーマル", "レア", "スーパーレア"};
  std::discrete_distribution<int> gacha({70, 25, 5});  // 70%, 25%, 5%

  std::mt19937 rng(2024);
  std::array<int, 3> counts{};
  for (int i = 0; i < 10000; ++i) {
    ++counts[gacha(rng)];
  }
  std::println("ノーマルが一番多い？ {}", counts[0] > counts[1] && counts[1] > counts[2]);
}
```

```text title="実行結果"
ノーマルが一番多い？ true
```

### std::normal_distribution {#normal}

```cpp
template <class RealType = double>
class normal_distribution {
 public:
  explicit normal_distribution(RealType mean = 0.0, RealType stddev = 1.0);
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `mean` | 浮動小数点 | 平均（一番出やすい値） |
| `stddev` | 浮動小数点 | 標準偏差（ばらつきの大きさ） |

- 平均の近くが出やすく、離れるほど出にくい乱数です。平均 ± 標準偏差の範囲に約 68% が入ります

!!! note "実際は"
    弾のばらつき、ステータスの個体差など、「だいたいこのくらい、たまに外れる」ものに使います。範囲の外の値も出るので、`std::clamp` で収めます。

### std::mt19937_64 {#mt19937_64}

- 64 ビットの整数を出す版です。64 ビットの乱数が直接欲しいとき以外は `mt19937` で十分です

### dist(engine) {#call}

```cpp
template <class URBG>
result_type operator()(URBG& g);
```

- 分布にエンジンを渡して呼ぶと、乱数が 1 つ返ります。エンジンの状態が進みます

### engine.seed(s) {#seed}

```cpp
void seed(result_type value = default_seed);
```

- 種を設定し直します。同じ種を設定すると、また同じ列が最初から出ます（リプレイ用）

```cpp
#include <print>
#include <random>

int main() {
  std::mt19937 rng(100);
  auto first = rng();
  rng.seed(100);  // 巻き戻す
  std::println("{}", first == rng());
}
```

```text title="実行結果"
true
```

### engine() {#engine-call}

```cpp
result_type operator()();
```

- エンジンの生の整数（mt19937 なら 0〜2³²−1）を返します。普通は分布を通して使います

### dist.reset() {#reset}

```cpp
void reset();
```

- 分布が内部に持っている状態（normal_distribution の予備の値など）を捨てます。種を設定し直したあとに呼ぶと、完全に同じ結果を再現できます

### dist.min() / dist.max() {#minmax}

- 分布（またはエンジン）が出しうる値の最小・最大を返します

### engine.discard(n) {#discard}

```cpp
void discard(unsigned long long z);
```

- 乱数を `z` 回ぶん作って捨てます

```cpp
#include <print>
#include <random>

int main() {
  std::uniform_int_distribution<int> d(1, 6);
  std::println("{} {}", d.min(), d.max());

  std::mt19937 a(5);
  std::mt19937 b(5);
  a();
  a();
  b.discard(2);
  std::println("{}", a() == b());
}
```

```text title="実行結果"
1 6
true
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

| 場面 | 使うもの |
| --- | --- |
| ダメージの振れ幅 | `uniform_int_distribution` |
| 会心・回避の判定 | `bernoulli_distribution` |
| ドロップ・ガチャ | `discrete_distribution` |
| パーティクルの方向・速度 | `uniform_real_distribution` |
| 弾のブレ | `normal_distribution` |
| マップ生成 | 種を保存しておけば同じマップを再生成できる |

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
