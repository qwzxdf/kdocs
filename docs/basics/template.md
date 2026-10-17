---
title: テンプレート
tags:
  - 基礎
---

# テンプレート

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">C++98〜</span>
<span class="ver ver-20">C++20</span>
</div>

**テンプレート**は、<strong>型をあとから決められる関数やクラスの「ひな形」</strong>です。「int でも float でも同じ処理をしたい」ときに、型ごとに関数を書く代わりに、型の部分を `T` のような名前にしておいて、使うときにコンパイラに当てはめてもらいます。`std::vector<int>` の `<int>` も、vector というテンプレートに「int」を当てはめて使っている、ということです。

!!! tip "ポイント"
    - **使う側**としては、`std::vector<Enemy>` のように `<>` の中に型を書くだけ。まずはこれが読めれば十分。
    - **作る側**としては、`template <class T>` を関数やクラスの前に付けて、型の部分を `T` にする。
    - C++20 からは引数を `auto` にするだけで関数テンプレートになる（`void Print(const auto& x)`）。
    - 「この型にはこういう操作ができてほしい」という条件は **concepts**（`std::integral` など）で書ける。
    - テンプレートは**ヘッダファイルに全部書く**（.cpp に分けるとリンクエラーになる）。

!!! info "このページを読む前に"
    [参照](reference.md) が分かると、サンプルが読みやすくなります。

## 基本

### 使う側：`<>` に型を書く

```cpp
#include <map>
#include <print>
#include <string>
#include <vector>

int main() {
  std::vector<int> scores = {10, 20};                // int の vector
  std::vector<std::string> names = {"A", "B"};       // string の vector
  std::map<std::string, int> prices = {{"薬", 50}};  // キーが string、値が int
  std::println("{} {} {}", scores, names, prices);
}
```

```text title="実行結果"
[10, 20] ["A", "B"] {"薬": 50}
```

同じ `std::vector` でも、`<>` に入れる型によって「int の配列」にも「string の配列」にもなります。

### 作る側：関数テンプレート

```cpp
#include <print>
#include <string>

// T には呼び出したときの型が入る
template <class T>
T Larger(T a, T b) {
  return a > b ? a : b;
}

int main() {
  std::println("{}", Larger(3, 7));                    // T = int
  std::println("{}", Larger(2.5, 1.5));                // T = double
  std::println("{}", Larger(std::string("a"), std::string("b")));  // T = std::string
}
```

```text title="実行結果"
7
2.5
b
```

コンパイラは呼び出しを見て、`int` 版・`double` 版・`string` 版の `Larger` を自動で作ります。

## 詳しく

### 型の推論と明示

```cpp
#include <print>

template <class T>
T Twice(T x) {
  return x * 2;
}

int main() {
  std::println("{}", Twice(5));          // 引数から T = int と推論される
  std::println("{}", Twice<float>(5));   // T を明示的に float にする
  // Twice(1, 2.0) のように、同じ T に違う型を渡すと推論できずエラー
}
```

```text title="実行結果"
10
10
```

### クラステンプレート

```cpp
#include <print>

template <class T>
struct Vec2 {
  T x;
  T y;

  Vec2 operator+(const Vec2& other) const { return {x + other.x, y + other.y}; }
};

int main() {
  Vec2<int> tile = {3, 4};          // 整数座標（マス目）
  Vec2<float> pos = {1.5f, 2.0f};   // 小数座標（ピクセル）
  auto sum = tile + Vec2<int>{1, 1};
  std::println("({}, {}) ({}, {})", sum.x, sum.y, pos.x, pos.y);

  Vec2 deduced = {1.0, 2.0};  // C++17: <double> を省略しても推論される（CTAD）
  std::println("{}", deduced.x);
}
```

```text title="実行結果"
(4, 5) (1.5, 2)
1
```

### 型以外のテンプレート引数（数値など）

```cpp
#include <array>
#include <print>

// N は型ではなく「コンパイル時に決まる整数」
template <class T, int N>
struct RingBuffer {
  std::array<T, N> data{};
  int head = 0;

  void Push(T value) {
    data[head] = value;
    head = (head + 1) % N;
  }
};

int main() {
  RingBuffer<float, 3> history;
  for (float f : {1.0f, 2.0f, 3.0f, 4.0f}) {
    history.Push(f);
  }
  std::println("{}", history.data);  // 4 が 1 を上書きしている
}
```

```text title="実行結果"
[4, 2, 3]
```

`std::array<int, 4>` の `4` もこの仕組みです。

### デフォルト引数

```cpp
template <class T, class Allocator = std::allocator<T>>
class vector;  // 2 つ目は省略すると std::allocator<T> になる
```

自分で作るときも `template <class T = float>` のようにデフォルトを付けられます。

### auto 引数（C++20 の短い書き方）

```cpp
#include <print>
#include <string>
#include <vector>

// 引数を auto にするだけで関数テンプレートになる
void PrintAll(const auto& container) {
  for (const auto& x : container) {
    std::print("{} ", x);
  }
  std::println("");
}

int main() {
  PrintAll(std::vector<int>{1, 2, 3});
  PrintAll(std::string("abc"));
}
```

```text title="実行結果"
1 2 3 
a b c 
```

`template <class T> void PrintAll(const T& container)` と同じ意味です。

### concepts：型に条件を付ける <span class="ver ver-20">C++20</span> {#concepts型に条件を付ける data-toc-label="concepts：型に条件を付ける"}

テンプレートに「足し算できない型」などを渡すと、普通は長くて読めないエラーが出ます。**concepts** を使うと、受け取れる型の条件を書けて、エラーも分かりやすくなります。

```cpp
#include <concepts>
#include <print>

// 整数だけを受け取る
template <std::integral T>
T Gcd(T a, T b) {
  while (b != 0) {
    T t = a % b;
    a = b;
    b = t;
  }
  return a;
}

// auto 引数にも条件を付けられる
void PrintHalf(std::floating_point auto x) { std::println("{}", x / 2); }

int main() {
  std::println("{}", Gcd(12, 18));
  PrintHalf(3.0f);
  // Gcd(1.5, 2.5);  // コンパイルエラー: double は integral ではない（分かりやすいエラーが出る）
}
```

```text title="実行結果"
6
1.5
```

よく使う標準の concepts です（`<concepts>`）。

| concept | 意味 |
| --- | --- |
| `std::integral` | 整数型（int、long、char など） |
| `std::floating_point` | 浮動小数点型（float、double） |
| `std::same_as<U>` | U と同じ型 |
| `std::convertible_to<U>` | U に変換できる |
| `std::derived_from<Base>` | Base を継承している |
| `std::invocable<Args...>` | その引数で呼び出せる |
| `std::totally_ordered` | `<` などで比べられる |
| `std::ranges::range` | 範囲 for で回せる（`<ranges>`） |

自分で条件を書くこともできます。

```cpp
#include <print>

template <class T>
concept HasHp = requires(T t) {
  t.hp;          // hp というメンバがある
  t.hp -= 1;     // hp から引き算できる
};

struct Enemy {
  int hp = 10;
};

void Damage(HasHp auto& target, int amount) { target.hp -= amount; }

int main() {
  Enemy e;
  Damage(e, 3);
  std::println("{}", e.hp);
}
```

```text title="実行結果"
7
```

### 特殊化：特定の型だけ別の処理にする

```cpp
#include <print>
#include <string>

template <class T>
std::string TypeName() {
  return "不明";
}

template <>
std::string TypeName<int>() {  // int のときだけ
  return "整数";
}

template <>
std::string TypeName<float>() {  // float のときだけ
  return "小数";
}

int main() {
  std::println("{} {} {}", TypeName<int>(), TypeName<float>(), TypeName<char>());
}
```

```text title="実行結果"
整数 小数 不明
```

標準ライブラリでは `std::hash<T>` や `std::formatter<T>` を自作の型向けに特殊化して使います（[unordered_map](../stl/containers/unordered_map.md#4-自作の型をキーにする)、[format](../stl/utilities/format.md#formatter)）。

### 可変長テンプレート（引数をいくつでも）

```cpp
#include <print>

// Args... は「型の並び」、args... は「値の並び」
template <class... Args>
void Log(const Args&... args) {
  ((std::print("[{}]", args)), ...);  // 全部の引数に同じ処理をする（fold 式）
  std::println("");
}

int main() {
  Log(1, "abc", 2.5);
}
```

```text title="実行結果"
[1][abc][2.5]
```

`std::make_unique<T>(args...)` や `emplace_back(args...)` は、この仕組みで「何個の引数でも受け取ってコンストラクタに渡す」を実現しています。

### if constexpr：型によって処理を分ける <span class="ver ver-17">C++17</span> {#if-constexpr型によって処理を分ける data-toc-label="if constexpr：型によって処理を分ける"}

```cpp
#include <print>
#include <string>
#include <type_traits>

template <class T>
std::string Describe(const T& value) {
  if constexpr (std::is_integral_v<T>) {
    return "整数 " + std::to_string(value);
  } else if constexpr (std::is_floating_point_v<T>) {
    return "小数 " + std::to_string(value);
  } else {
    return "その他";
  }
}

int main() {
  std::println("{} / {} / {}", Describe(3), Describe(1.5), Describe("x"));
}
```

```text title="実行結果"
整数 3 / 小数 1.500000 / その他
```

`if constexpr` はコンパイル時に分岐するので、選ばれなかった側はコンパイルされません。

### テンプレートはヘッダに書く

テンプレートは「使われたときに型を当てはめて作られる」ので、使う側からテンプレートの中身（定義）が見えている必要があります。

```text
math.h      ← template <class T> T Larger(T a, T b) { ... } を全部ここに書く
main.cpp    ← #include "math.h" して使う
```

宣言だけをヘッダに書いて中身を .cpp に書くと、**リンクエラー**（「未解決の外部シンボル」）になります。

## ゲームでの例

| 場面 | 例 |
| --- | --- |
| 数学の型 | `Vec2<T>`、`Rect<T>`（int 版と float 版を 1 つのコードで） |
| リソース管理 | `ResourceCache<Texture>`、`ResourceCache<Sound>` |
| オブジェクトプール | `Pool<Bullet, 1024>` |
| ECS | `registry.GetComponent<Transform>(entity)`（[ECS](../engine/ecs.md)） |
| ユーティリティ | `Clamp<T>`、`Lerp<T>` |

## よくあるミス

??? failure "テンプレートの中身を .cpp に書いてリンクエラー"
    上の「テンプレートはヘッダに書く」を参照してください。

??? failure "エラーメッセージが長すぎて読めない"
    テンプレートのエラーは、中の中の中で起きた問題が全部表示されるので長くなります。**一番最初のエラー**と、「required from here（ここから呼ばれた）」と書かれた自分のコードの行を探します。concepts で条件を付けておくと、ずっと短くなります。

??? failure "推論できずにエラー"
    `Larger(1, 2.0)` は T が int か double か決められずエラーになります。`Larger<double>(1, 2.0)` と明示するか、引数の型をそろえます。

??? failure "何でもテンプレートにする"
    テンプレートはコンパイル時間を延ばし、エラーも読みにくくします。型が 1 つしかないなら普通の関数で十分です。

## 理解度チェック

!!! question "Q1. `std::vector<std::vector<int>>` は何を表す？"
    <div class="spoiler" markdown>

    **答え:** 「int の vector」の vector（2 次元の可変長配列）。テンプレートの引数にテンプレートを入れることもできます。

    </div>

!!! question "Q2. 次の関数を auto 引数で書き直すと？"
    ```cpp
    template <class T>
    void Show(const T& value) { std::println("{}", value); }
    ```

    <div class="spoiler" markdown>

    **答え:** `void Show(const auto& value) { std::println("{}", value); }`

    </div>

## これだけ覚える

!!! abstract "まとめ"
    - [x] `<>` に型を入れて使う（`std::vector<int>`）
    - [x] 作るなら `template <class T>`、または `auto` 引数
    - [x] 型に条件を付けるなら concepts（`std::integral` など）
    - [x] テンプレートはヘッダに全部書く

## 関連ページ

- [cpprefjp: コンセプト](https://cpprefjp.github.io/lang/cpp20/concepts.html)
- [cppreference: Templates](https://en.cppreference.com/w/cpp/language/templates)
