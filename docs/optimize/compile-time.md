---
title: コンパイル時の計算（constexpr）
tags:
  - 最適化
---

# コンパイル時の計算（constexpr）

**実行中にやっている計算を、コンパイル時（ビルド時）に済ませてしまう**と実行時のコストがゼロになります。C++ では`constexpr`（コンパイル時定数・関数）、`consteval`、`constinit`、`if constexpr`、テンプレートでこれを実現します。変換テーブル、ハッシュ値、定数の計算、型による分岐など、ゲームでも使いどころがたくさんあります。このページはそれぞれの意味・書き方・使いどころ・注意点をまとめます。

!!! tip "ポイント"
    - <strong>`constexpr` ＝ 「コンパイル時に計算できる」</strong>。<strong>実行時にも普通に使える</strong>（両対応）。
    - `consteval`（C++20）＝ 必ずコンパイル時。`constinit`（C++20）＝ 定数で初期化されることを、保証。
    - `constexpr` 変数はコンパイル時定数（配列の大きさ・テンプレート引数にも使える）。
    - `if constexpr`（C++17）は、コンパイル時に分岐して、使わない側をコンパイルしない。
    - 使いどころ：ルックアップテーブル、ハッシュ値、定数の計算、型による分岐。
    - コンパイル時間が増える。重い計算はビルドの時間と引き換え。
    - `static_assert` で、コンパイル時に検証できる（サイズ・前提条件）。

## なぜ、コンパイル時に計算するのか

| 利点 | 説明 |
| --- | --- |
| **実行時のコストがゼロ** | 結果がプログラムに定数として埋め込まれる |
| 起動時の初期化が不要 | テーブルの計算をゲーム起動時にやらなくてよい |
| 間違いをビルド時に発見 | `static_assert` で、前提が崩れたら、ビルドエラー |
| 最適化の足がかり | 定数と分かれば、コンパイラがさらに最適化 |
| 型安全・読みやすい | マクロ（`#define`）の代わりになる |

```text
実行時：  ゲーム起動 → テーブルを計算（毎回） → 使う
コンパイル時：  ビルド → テーブルを計算（1 回） → プログラムに埋め込み済み → 使う
```

## constexpr（定数・関数）

### constexpr 変数

```cpp
constexpr int kMaxEnemies = 64;
constexpr float kPi = 3.14159265f;
constexpr float kDegToRad = kPi / 180.0f;

std::array<Enemy, kMaxEnemies> enemies;
```

| 点 | 説明 |
| --- | --- |
| **`constexpr` 変数** | コンパイル時に値が決まる。変更できない（暗黙に `const`） |
| 使える場所 | 配列の大きさ、テンプレート引数、`static_assert`、`case` ラベル |
| `const` との違い | `const int n = f();` は実行時に決まってもよい。`constexpr` は、コンパイル時に決まることを要求 |
| マクロより良い | 型がある・スコープがある・デバッグできる |

### constexpr 関数

```cpp
constexpr int Factorial(int n) {
  return n <= 1 ? 1 : n * Factorial(n - 1);
}

constexpr int kValue = Factorial(5);
static_assert(kValue == 120);

int runtime_input = GetInput();
int result = Factorial(runtime_input);
```

| 点 | 説明 |
| --- | --- |
| コンパイル時にも実行時にも呼べる | 引数がすべて定数なら、コンパイル時に評価できる（`constexpr` 変数の初期化など、定数が必要な場所では、必ずコンパイル時） |
| 実行時の引数なら、普通の関数 | 同じ関数が両方で使える |
| 「コンパイル時に評価される」とは限らない | 普通の変数の初期化で呼んだ場合、コンパイラが実行時に評価することもある（最適化ではたいてい定数畳み込みされる） |

### constexpr 関数の制限

| バージョン | できること |
| --- | --- |
| C++11 | return 文 1 つだけ（再帰で書く） |
| C++14 | ローカル変数・ループ・if・複数の文が使える |
| C++17 | ラムダ式も、constexpr にできる |
| C++20 | `virtual` 関数・`try`・`new` / `delete`（コンパイル時に完結）・`std::vector` / `std::string`（一時的）・`<algorithm>` の多くの関数 |
| C++23 | より多くの標準ライブラリが、constexpr に |

コンパイル時には、できないこと：ファイルの読み込み・ネットワーク・乱数（実行時の状態）・`reinterpret_cast`・未定義動作（コンパイル時に検出されて、エラーになる）。

## consteval（必ずコンパイル時）

```cpp
consteval int Square(int n) {
  return n * n;
}

constexpr int a = Square(4);
int b = Square(5);
int input = GetInput();
int c = Square(input);
```

| 点 | 説明 |
| --- | --- |
| <strong>`consteval`（C++20）</strong> | 即時関数。必ず、コンパイル時に評価される |
| 実行時の引数を渡すとコンパイル エラー | コンパイル時にしか、使えないことを保証したいとき |
| 使いどころ | 文字列のハッシュ（実行時に遅いハッシュ計算をさせない）、設定の検証 |

```cpp
consteval uint64_t Hash(std::string_view s) {
  uint64_t h = 14695981039346656037ull;
  for (char c : s) {
    h ^= static_cast<uint8_t>(c);
    h *= 1099511628211ull;
  }
  return h;
}

constexpr uint64_t kPlayerId = Hash("player");

switch (id) {
  case Hash("player"): ...
  case Hash("enemy"): ...
}
```

文字列のハッシュをコンパイル時に計算しておけば、実行時は整数の比較だけで済みます（[文字列とハッシュ](strings-hash.md)）。

### if consteval（C++23）

コンパイル時の評価か、実行時かで処理を分ける書き方です。

```cpp
constexpr double Sqrt(double x) {
  if consteval {
    return SqrtConstexpr(x);
  } else {
    return std::sqrt(x);
  }
}
```

`std::is_constant_evaluated()`（C++20）も、同じ目的で使います。

## constinit（定数での初期化の保証）

```cpp
constinit int g_counter = 0;
constinit std::atomic<int> g_frame{0};
```

| 点 | 説明 |
| --- | --- |
| <strong>`constinit`（C++20）</strong> | 静的変数が定数で初期化されることを、保証（ビルド時に確定） |
| 変更はできる（`const` ではない） | `constexpr` と違い、実行時に書き換えられる |
| 解決する問題 | 静的初期化順序の問題（static initialization order fiasco）：別の翻訳単位の静的変数の、初期化順序が不定 |

グローバル変数の初期化が、実行時になると他のグローバルがまだ初期化されていないことで壊れる恐れがあります。`constinit` なら、起動前に値が決まっているので、安全です。

## if constexpr（コンパイル時の分岐）

```cpp
template <typename T>
void Print(const T& value) {
  if constexpr (std::is_integral_v<T>) {
    std::println("整数: {}", value);
  } else if constexpr (std::is_floating_point_v<T>) {
    std::println("実数: {:.2f}", value);
  } else {
    std::println("その他");
  }
}
```

| 点 | 説明 |
| --- | --- |
| <strong>`if constexpr (条件)`（C++17）</strong> | 条件がコンパイル時に決まる。偽の側はコンパイルされない（その型では書けないコードも置ける） |
| 普通の `if` との違い | 普通の `if` は、両方の枝がコンパイルできる必要がある |
| 使いどころ | テンプレートで型によって処理を変える（SFINAE の代わり）、機能のスイッチ |

```cpp
template <bool kDebug>
void Log(const char* message) {
  if constexpr (kDebug) {
    std::println("{}", message);
  }
}
```

`kDebug` が `false` なら、ログ呼び出しは、完全に消えます（実行時のチェックなし）。

## ルックアップテーブルを、コンパイル時に作る

**計算が重い関数**（三角関数・ガンマ補正など）を、あらかじめテーブルにしておくと、実行時は配列を引くだけになります。そのテーブルをコンパイル時に作る例です。

```cpp
constexpr size_t kTableSize = 256;

constexpr std::array<float, kTableSize> MakeSinTable() {
  std::array<float, kTableSize> table{};
  for (size_t i = 0; i < kTableSize; ++i) {
    double angle = 2.0 * 3.14159265358979323846 * static_cast<double>(i) / kTableSize;
    table[i] = static_cast<float>(Sin(angle));
  }
  return table;
}

constexpr std::array<float, kTableSize> kSinTable = MakeSinTable();

float FastSin(float radians) {
  int index = static_cast<int>(radians * (kTableSize / 6.2831853f)) & (kTableSize - 1);
  return kSinTable[index];
}
```

| 点 | 説明 |
| --- | --- |
| `MakeSinTable()` | `constexpr` 関数で、テーブルを作る |
| `constexpr` の変数に代入 | コンパイル時に評価される（結果は読み取り専用のデータとして、実行ファイルに埋め込み） |
| `Sin` を自作する必要 | `std::sin` は、C++23 でも `constexpr` と限らない（C++26 で `<cmath>` の constexpr 化が進む）。テイラー展開などで自作する |
| ガンマ補正・イージング・乱数表 | 同じ手法で作れる |

!!! note "テーブルは、本当に速いか"
    現代の CPU は、計算が速く、メモリ（キャッシュミス）のほうが遅いことがあります。テーブルが大きいとかえって遅くなります。測ってから、使います（[メモリとキャッシュ](memory-cache.md)）。

### 少し複雑な例：ビットマスクの表

```cpp
constexpr auto MakeParityTable() {
  std::array<uint8_t, 256> t{};
  for (int i = 0; i < 256; ++i) {
    t[i] = static_cast<uint8_t>(std::popcount(static_cast<unsigned>(i)) & 1);
  }
  return t;
}
constexpr auto kParity = MakeParityTable();
```

`std::popcount`（`<bit>`）も、`constexpr` です。

## static_assert（コンパイル時の検証）

```cpp
static_assert(sizeof(int) == 4, "int は 4 バイトが前提");
static_assert(sizeof(Enemy) <= 64, "Enemy が、キャッシュラインを超えた");
static_assert(std::is_trivially_copyable_v<Vertex>, "Vertex は、memcpy できる型にする");
static_assert(kMaxEnemies > 0 && kMaxEnemies <= 1024);
```

| 用途 | 説明 |
| --- | --- |
| **サイズ・アライメントの検証** | 構造体が意図せず大きくなったら、ビルドエラー（[データ構造の配置](data-layout.md)） |
| 型の性質の検証 | コピーできる型か、ムーブできるか |
| 定数の検証 | 設定値が範囲内か |
| テンプレートの前提 | 「この型はこれを満たすこと」 |

実行時に気づくのでは遅い問題を、ビルドで止められます。

## テンプレートによる、コンパイル時の計算

**型や数値を引数にしたテンプレート**（テンプレートメタプログラミング）も、コンパイル時の計算です。

```cpp
template <size_t N>
struct Fixed {
  std::array<float, N> data{};
  static constexpr size_t kSize = N;
};

Fixed<16> a;
static_assert(Fixed<16>::kSize == 16);
```

| 用途 | 例 |
| --- | --- |
| 固定サイズのコンテナ | `std::array<T, N>`、`Vector<float, 3>` |
| コンパイル時多態（CRTP） | 仮想関数を使わない多態（[CRTP](../design/patterns/crtp-policy.md)） |
| 型リスト・タプル | ECS のコンポーネント集合など |
| `concepts`（C++20） | テンプレート引数の条件を型で表す（[テンプレート](../basics/template.md)） |

現代の C++ では、`constexpr` 関数のほうが、読みやすいので複雑な計算はテンプレートより `constexpr`にします。

## constexpr と標準ライブラリ

| 機能 | バージョン |
| --- | --- |
| **`std::array`**、`std::string_view`、`std::optional`、`std::pair` / `tuple` | C++17 までに多くが constexpr |
| `<algorithm>`（`sort`・`find` など） | C++20 で、constexpr に |
| `std::vector` / `std::string` | C++20：コンパイル時に作って、コンパイル時に壊すならば、使える（実行時に残るデータには、できない） |
| `std::bit_cast`、`<bit>`（`popcount` など） | C++20 |
| `<cmath>`（`sqrt`・`sin` など） | C++23 では、限定的（C++26 で拡大）。GCC は拡張として、すでに可能 |
| `std::format`（コンパイル時の書式チェック） | C++20：書式文字列の間違いをコンパイル時に検出 |

!!! note "constexpr の `std::vector` は、結果を `std::array` にして取り出す"
    コンパイル時に、`std::vector` で計算して、最後に `std::array` にコピーして、`constexpr` 変数に入れる、という書き方が定番です。

## コンパイル時間とのトレードオフ

コンパイル時の計算は、ビルドの時間を増やします。

| 注意 | 説明 |
| --- | --- |
| 重い計算はビルドが遅くなる | 大きなテーブル・再帰の深い計算は、コンパイラに負担 |
| コンパイラの制限 | 評価の深さ・ステップ数に上限がある。MSVC は `/constexpr:depth<N>`・`/constexpr:steps<N>` で変更できる |
| ヘッダに書くと全員が再評価 | `constexpr` の巨大なテーブルを、ヘッダに書くと、include した全員が、コンパイルする。`.cpp` に置いて、`extern` で共有する（`inline constexpr`（C++17）なら、1 つにまとまる） |
| デバッグしにくい | コンパイル時の評価中は、デバッガーが使えない。実行時に同じ関数を呼んで、確かめる（`constexpr` 関数は、実行時にも呼べる） |

```cpp
inline constexpr std::array<float, 256> kSinTable = MakeSinTable();
```

`inline constexpr`（C++17）は、複数の翻訳単位から include されても、1 つの定義になります。

## どちらを使うか

| 目的 | 使うもの |
| --- | --- |
| 定数（値） | `constexpr` 変数 |
| 計算の関数（実行時にも使う） | `constexpr` 関数 |
| 必ず、コンパイル時に評価したい（ハッシュなど） | `consteval` 関数 |
| グローバル変数の初期化順序問題を避けたい | `constinit` |
| 型・条件で処理を分けたい | `if constexpr`、`concepts` |
| 前提をビルド時に検証したい | `static_assert` |
| コンパイル時にテーブルを作る | `constexpr` 関数 ＋ `std::array` |

## ゲームでの使いどころ

| 場面 | 使い方 |
| --- | --- |
| 文字列 ID | `consteval` のハッシュ（`Hash("player")`）。`switch` の `case` にも使える |
| 変換テーブル | 三角関数・ガンマ・イージング・乱数のシード表 |
| 構造体のサイズ確認 | `static_assert(sizeof(T) == 64)`。パディングの意図しない増加を検出 |
| 設定値の定数 | `constexpr`（最大数・タイルの大きさ・単位） |
| コンポーネントの型 ID | コンパイル時に型ごとの ID を割り当てる |
| デバッグ機能の完全な除去 | `if constexpr (kDebug)` |
| ビット操作・フラグ | `constexpr` 関数で、マスクを作る |

## よくあるミス

??? failure "`constexpr` 関数を呼んだのに、実行時に評価されている"
    定数が必要な場所（`constexpr` 変数・配列の大きさ）で呼ぶと確実にコンパイル時です。確実にしたいなら `consteval`。

??? failure "constexpr の中で、コンパイル時に使えない処理（ファイル・乱数）を書く"
    コンパイル エラーになります。実行時の処理は、別の関数に分けます。

??? failure "巨大な constexpr テーブルを、ヘッダに書いて、ビルドが遅くなる"
    `.cpp` に置く、または `inline constexpr` にして、ヘッダの量を減らします。

??? failure "`constexpr` にしたのに、速くならない"
    実行時の呼び出しは、普通の関数です。コンパイル時に済ませる値を、変数として持って使います。

??? failure "`const` と `constexpr` を、混同する"
    `const` は、変更しないだけ。`constexpr` は、コンパイル時に決まる。

??? failure "テーブルを、大きくしすぎて、キャッシュミスで遅くなる"
    計算のほうが速いこともあります。測ります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `constexpr` ＝ コンパイル時に計算できる（実行時にも使える）。`consteval` ＝ 必ずコンパイル時。`constinit` ＝ 定数で初期化を保証
    - [x] `if constexpr` は、コンパイル時の分岐（偽の側はコンパイルされない）
    - [x] テーブル・ハッシュ・定数をビルド時に済ませて、実行時のコストをゼロにする
    - [x] `static_assert` で、サイズや前提をビルド時に検証
    - [x] コンパイル時間が、増える。巨大なテーブルは、`inline constexpr` か `.cpp`。テーブルは測ってから

## 関連ページ

- [最適化の進め方](index.md)
- [コンパイラの最適化](compiler.md)
- [ベイク（事前計算）](baking.md)
- [文字列とハッシュの最適化](strings-hash.md)
- [テンプレート（基礎）](../basics/template.md)
- [コンパイラとビルドの仕組み](../basics/compiler.md)
- [CRTP とポリシーベース設計](../design/patterns/crtp-policy.md)
