---
title: <functional>（関数オブジェクト・invoke・hash など）
tags:
  - 型・言語サポート
---

# &lt;functional&gt;（関数オブジェクト・invoke・hash など）

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++11</span>
`#include <functional>`
</div>

`<functional>` は、**関数を扱うための道具**をまとめたヘッダです。関数を入れておく [`std::function`](../utilities/function.md) のほかに、足し算や比較を表す**関数オブジェクト**（`std::plus`、`std::greater` など）、何でも呼び出せる `std::invoke`、引数を一部固定する `std::bind_front`、参照を値のように渡す `std::ref`、ハッシュ値を作る `std::hash` などがあります。

!!! tip "ポイント"
    - 並べ替えの比較には `std::greater{}`、合計には `std::plus{}` を渡す。
    - 自作の型を unordered_map のキーにするなら `std::hash` を使ってハッシュを作る。
    - スレッドや bind に**参照で**渡したいときは `std::ref(x)`。
    - 引数の一部を固定した関数を作るなら、`std::bind` ではなくラムダか `std::bind_front`。

## 関数一覧

| 名前 | 重要度 | 何をする |
| --- | --- | --- |
| [`std::function`](../utilities/function.md) | <span class="rank rank-often">よく使う</span> | 関数を変数に入れる（別ページ） |
| [`std::greater`](#greater) | <span class="rank rank-often">よく使う</span> | `a > b` を表す関数オブジェクト |
| [`std::less`](#less) | <span class="rank rank-often">よく使う</span> | `a < b` を表す関数オブジェクト |
| [`std::hash`](#hash) | <span class="rank rank-sometimes">たまに</span> | ハッシュ値を作る |
| [`std::ref`](#ref) | <span class="rank rank-sometimes">たまに</span> | 参照を値のように渡す |
| [`std::plus`](#plus) | <span class="rank rank-sometimes">たまに</span> | `a + b` を表す関数オブジェクト |
| [`std::invoke`](#invoke) | <span class="rank rank-sometimes">たまに</span> | 関数・メンバ関数・メンバ変数を同じ書き方で呼ぶ <span class="ver ver-17">C++17</span> |
| [`std::bind_front`](#bind_front) | <span class="rank rank-sometimes">たまに</span> | 前の引数を固定した関数を作る <span class="ver ver-20">C++20</span> |
| [`std::cref`](#cref) | <span class="rank rank-rare">知ってるだけ</span> | const 参照を値のように渡す |
| [`std::equal_to`](#equal_to) | <span class="rank rank-rare">知ってるだけ</span> | `a == b` を表す関数オブジェクト |
| [`std::multiplies`](#multiplies) | <span class="rank rank-rare">知ってるだけ</span> | `a * b` を表す関数オブジェクト |
| [`std::identity`](#identity) | <span class="rank rank-rare">知ってるだけ</span> | 受け取ったものをそのまま返す <span class="ver ver-20">C++20</span> |
| [`std::bind_back`](#bind_back) | <span class="rank rank-rare">知ってるだけ</span> | 後ろの引数を固定 <span class="ver ver-23">C++23</span> |
| [`std::not_fn`](#not_fn) | <span class="rank rank-rare">知ってるだけ</span> | 条件の結果を反転した関数を作る <span class="ver ver-17">C++17</span> |
| [`std::bind`](#bind) | <span class="rank rank-rare">知ってるだけ</span> | 古い引数の固定（使わない） |
| [`std::mem_fn`](#mem_fn) | <span class="rank rank-rare">知ってるだけ</span> | メンバ関数を普通の関数のように呼べるようにする |

## よくある使い方

```cpp
#include <algorithm>
#include <functional>
#include <print>
#include <vector>

int main() {
  std::vector<int> scores = {70, 100, 40};
  std::ranges::sort(scores, std::greater{});  // 大きい順

  auto damage = [](int base, int bonus) { return base + bonus; };
  auto sword = std::bind_front(damage, 50);   // base を 50 に固定
  std::println("{} / {} {}", scores, sword(5), sword(20));
}
```

```text title="実行結果"
[100, 70, 40] / 55 70
```

## 関数の詳しい説明

### std::greater {#greater}

```cpp
template <class T = void>
struct greater {
  constexpr bool operator()(const T& a, const T& b) const;  // a > b
};
```

- `a > b` を返す関数オブジェクト。`std::greater{}`（型を省略した版）がおすすめです。大きい順のソート、[priority_queue](../containers/priority_queue.md) の小さい順、map の逆順に使います

### std::less {#less}

```cpp
template <class T = void>
struct less;  // a < b
```

- `a < b`。sort や map のデフォルトです。`std::less<>`（型なし）にすると、型の違う値（`std::string` と `const char*`）でも比べられます（透過比較）

```cpp
#include <functional>
#include <map>
#include <print>
#include <string>
#include <string_view>

int main() {
  std::map<std::string, int, std::less<>> prices = {{"potion", 50}};
  std::string_view key = "potion";
  std::println("{} {}", prices.find(key)->second, std::greater{}(3, 1));  // string を作らず検索
}
```

```text title="実行結果"
50 true
```

### std::hash {#hash}

```cpp
template <class Key>
struct hash {
  std::size_t operator()(const Key& key) const;
};
```

- 値からハッシュ値（整数）を作ります。int、string、ポインタなどには最初から用意されています
- 自作の型には、メンバのハッシュを組み合わせて作ります（[unordered_map の例](../containers/unordered_map.md#4-自作の型をキーにする)）

```cpp
#include <cstddef>
#include <functional>
#include <print>
#include <string>

struct GridPos {
  int x;
  int y;
};

struct GridPosHash {
  std::size_t operator()(const GridPos& p) const {
    std::size_t h = std::hash<int>{}(p.x);
    return h ^ (std::hash<int>{}(p.y) + 0x9e3779b9 + (h << 6) + (h >> 2));  // 組み合わせる定番の式
  }
};

int main() {
  std::println("同じ文字列は同じハッシュ？ {}",
               std::hash<std::string>{}("slime") == std::hash<std::string>{}("slime"));
  std::println("違う座標は違うハッシュ？ {}", GridPosHash{}({1, 2}) != GridPosHash{}({2, 1}));
}
```

```text title="実行結果"
同じ文字列は同じハッシュ？ true
違う座標は違うハッシュ？ true
```

### std::ref {#ref}

```cpp
template <class T>
std::reference_wrapper<T> ref(T& t) noexcept;
```

- 値渡しされる場所（スレッドの引数、`std::bind`、コンテナ）に、**参照として**渡したいときに使います

```cpp
#include <functional>
#include <print>
#include <thread>
#include <vector>

void Fill(std::vector<int>& v) { v.assign(3, 7); }

int main() {
  std::vector<int> data;
  std::jthread(Fill, std::ref(data)).join();  // ref が無いとコピーが渡ってコンパイルエラー
  std::println("{}", data);
}
```

```text title="実行結果"
[7, 7, 7]
```

### std::plus {#plus}

```cpp
template <class T = void>
struct plus;  // a + b
```

- `a + b`。[`std::ranges::fold_left`](../algorithms/accumulate.md#fold_left) に合計の方法として渡します

### std::invoke {#invoke}

<span class="ver ver-17">C++17</span>

```cpp
template <class F, class... Args>
constexpr std::invoke_result_t<F, Args...> invoke(F&& f, Args&&... args);
```

- 普通の関数、ラムダ、**メンバ関数のポインタ**、**メンバ変数のポインタ**を、同じ書き方で呼びます。ranges のプロジェクション（`&Enemy::hp`）はこの仕組みで動いています

```cpp
#include <functional>
#include <print>

struct Enemy {
  int hp = 30;
  int Attack(int bonus) const { return 10 + bonus; }
};

int main() {
  Enemy e;
  std::println("{} {} {}", std::invoke(&Enemy::hp, e), std::invoke(&Enemy::Attack, e, 5),
               std::invoke(std::plus{}, 2, 3));
}
```

```text title="実行結果"
30 15 5
```

### std::bind_front {#bind_front}

<span class="ver ver-20">C++20</span>

```cpp
template <class F, class... Args>
constexpr auto bind_front(F&& f, Args&&... args);
```

- `f` の前のほうの引数を固定した、新しい関数を作ります。メンバ関数とオブジェクトを組にして、コールバックに渡すのに便利です

```cpp
#include <functional>
#include <print>

class Score {
 public:
  void Add(int points) { total_ += points; }
  int total() const { return total_; }

 private:
  int total_ = 0;
};

int main() {
  Score score;
  std::function<void(int)> on_kill = std::bind_front(&Score::Add, &score);  // score.Add(...)
  on_kill(100);
  on_kill(50);
  std::println("{}", score.total());
}
```

```text title="実行結果"
150
```

### std::cref {#cref}

```cpp
template <class T>
std::reference_wrapper<const T> cref(const T& t) noexcept;
```

- `std::ref` の const 版。読むだけの参照を渡します

### std::equal_to {#equal_to}

```cpp
template <class T = void>
struct equal_to;  // a == b
```

- `a == b`。unordered_map のデフォルトのキー比較です

### std::multiplies {#multiplies}

```cpp
template <class T = void>
struct multiplies;  // a * b
```

- `a * b`。ほかに `minus`、`divides`、`modulus`、`negate`、`logical_and` / `logical_or` / `logical_not`、`bit_and` / `bit_or` / `bit_xor`、`not_equal_to`、`greater_equal`、`less_equal` があります

### std::identity {#identity}

<span class="ver ver-20">C++20</span>

```cpp
struct identity {
  template <class T>
  constexpr T&& operator()(T&& t) const noexcept;
};
```

- 受け取ったものをそのまま返します。ranges のアルゴリズムの「プロジェクション無し」のデフォルトです

### std::bind_back {#bind_back}

<span class="ver ver-23">C++23</span>

```cpp
template <class F, class... Args>
constexpr auto bind_back(F&& f, Args&&... args);
```

- 後ろのほうの引数を固定します

### std::not_fn {#not_fn}

<span class="ver ver-17">C++17</span>

```cpp
template <class F>
constexpr auto not_fn(F&& f);
```

- 結果を反転した関数を作ります（`IsDead` から「生きている」を作る）

```cpp
#include <algorithm>
#include <functional>
#include <print>
#include <vector>

bool IsDead(int hp) { return hp <= 0; }

int main() {
  std::vector<int> hp = {0, 20, -5, 40};
  auto alive = std::ranges::count_if(hp, std::not_fn(IsDead));
  auto half = std::bind_back(std::divides{}, 2);  // x / 2
  std::println("{} {} {}", alive, half(10), std::multiplies{}(3, 4));
}
```

```text title="実行結果"
2 5 12
```

### std::bind {#bind}

```cpp
template <class F, class... Args>
/* unspecified */ bind(F&& f, Args&&... args);
```

- 引数の固定や並べ替えをする古い関数（`std::placeholders::_1` を使う）。読みにくいので、ラムダか `bind_front` を使います

### std::mem_fn {#mem_fn}

```cpp
template <class M, class T>
/* unspecified */ mem_fn(M T::* pm) noexcept;
```

- メンバ関数のポインタを、`f(obj, 引数...)` の形で呼べる関数オブジェクトにします。今は `std::invoke` やプロジェクションで足ります

## フラグ・オプション

フラグはありません。

## ゲームでの使いどころ

| 場面 | 道具 |
| --- | --- |
| 大きい順に並べる | `std::greater{}` |
| 自作の座標を unordered_map のキーに | `std::hash` で組み合わせる |
| メンバ関数をコールバックに | `std::bind_front(&Class::Func, this)` |
| スレッドに参照を渡す | `std::ref` |

## よくあるミス

??? failure "std::bind で読めないコードになる"
    `std::bind(&F, _2, 10, _1)` は何をしているか分かりにくいです。ラムダで書きます。

??? failure "ハッシュの組み合わせを x ^ y にする"
    `(1, 2)` と `(2, 1)`、`(3, 3)` と `(0, 0)` が同じハッシュになり、衝突が増えます。上の例のようにずらして混ぜます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 比較は std::greater{} / std::less{}
    - [x] 自作の型のハッシュは std::hash を組み合わせる
    - [x] 参照を渡すなら std::ref
    - [x] 引数の固定はラムダか bind_front

## 関連ページ

- [std::function](../utilities/function.md)
- [cppreference: Function objects](https://en.cppreference.com/w/cpp/utility/functional)
