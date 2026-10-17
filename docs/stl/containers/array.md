---
title: std::array
tags:
  - コンテナ
---

# std::array

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="perf perf-4">◎ 速い</span>
<span class="ver ver-11">C++11</span>
`#include <array>`
</div>

`std::array` は、**要素数がコンパイル時に決まっている固定長の配列**です。中身は C の配列（`int a[4]`）とまったく同じで、速さもメモリも変わりません。そのうえで `size()` が使える、コピーや比較ができる、関数から返せる、といった「普通の値」としての便利さが足されています。

!!! tip "ポイント"
    - <strong>個数が決まっているなら C の配列ではなくこれを使う。</strong> 4 方向、装備スロット、キー設定など。
    - 書き方は `std::array<int, 4> a = {1, 2, 3, 4};`。型と個数をテンプレート引数に書く。
    - 個数が変わるなら [`std::vector`](vector.md)。
    - **ヒープを使わない**ので、vector よりさらに軽い。

!!! info "このページを読む前に"
    [テンプレート](../../basics/template.md)、[範囲 for](../../basics/range-for.md) が分かると読みやすいです。

## 宣言

```cpp
template <class T, std::size_t N>
struct array;
```

| テンプレート引数 | 意味 | 指定する？ |
| --- | --- | --- |
| `T` | 要素の型 | 必ず |
| `N` | 要素数。**コンパイル時に決まる定数**でないといけない | 必ず |

### 作り方

| 書き方 | 重要度 | 結果 |
| --- | --- | --- |
| `std::array<int, 3> a = {1, 2, 3};` | <span class="rank rank-must">必須</span> | `1, 2, 3` |
| `std::array<int, 3> a{};` | <span class="rank rank-must">必須</span> | 全部 `0` |
| `std::array a = {1, 2, 3};` | <span class="rank rank-often">よく使う</span> | 型と個数を推論（`std::array<int, 3>`） |
| `std::array<int, 3> a;` | <span class="rank rank-sometimes">たまに</span> | **中身はゴミ**（初期化されない） |
| `auto a = std::to_array({1, 2, 3});` | <span class="rank rank-rare">知ってるだけ</span> | C の配列や初期化リストから作る <span class="ver ver-20">C++20</span> |

!!! warning "`{}` を忘れると中身が初期化されない"
    `std::array<int, 3> a;` は C の配列と同じく**中身が不定**です。必ず `{}` を付けるか、値を書きます。

```cpp
#include <array>
#include <print>

int main() {
  std::array<int, 3> a = {1, 2, 3};
  std::array<int, 3> b{};       // 全部 0
  std::array<int, 5> c = {7};   // 足りない分は 0
  std::array d = {1.5f, 2.5f};  // std::array<float, 2>

  std::println("a = {}", a);
  std::println("b = {}", b);
  std::println("c = {}", c);
  std::println("d = {}", d);
}
```

```text title="実行結果"
a = [1, 2, 3]
b = [0, 0, 0]
c = [7, 0, 0, 0, 0]
d = [1.5, 2.5]
```

## 関数一覧

vector と同じ名前の関数は同じ意味です。

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`operator[]`](#operator) | <span class="rank rank-must">必須</span> | i 番目にアクセス（範囲チェックなし） | O(1) |
| [`size`](#size) | <span class="rank rank-must">必須</span> | 要素数（= N） | O(1) |
| [`begin`](#begin) | <span class="rank rank-must">必須</span> | 先頭のイテレータ | O(1) |
| [`end`](#end) | <span class="rank rank-must">必須</span> | 最後の次のイテレータ | O(1) |
| [`fill`](#fill) | <span class="rank rank-often">よく使う</span> | 全要素を同じ値にする | O(N) |
| [`operator==`](#eq) | <span class="rank rank-sometimes">たまに</span> | 全要素が等しいか | O(N) |
| [`operator<=>`](#spaceship) | <span class="rank rank-sometimes">たまに</span> | 辞書順の大小比較 | O(N) |
| [`data`](#data) | <span class="rank rank-sometimes">たまに</span> | 先頭のポインタ | O(1) |
| [`front`](#front) | <span class="rank rank-sometimes">たまに</span> | 先頭の要素 | O(1) |
| [`back`](#back) | <span class="rank rank-sometimes">たまに</span> | 末尾の要素 | O(1) |
| [`at`](#at) | <span class="rank rank-sometimes">たまに</span> | i 番目にアクセス（範囲チェックあり） | O(1) |
| [`swap`](#swap) | <span class="rank rank-rare">知ってるだけ</span> | 全要素を交換 | <strong>O(N)</strong> |
| [`empty`](#empty) | <span class="rank rank-rare">知ってるだけ</span> | `N == 0` かどうか | O(1) |
| [`max_size`](#max_size) | <span class="rank rank-rare">知ってるだけ</span> | 常に N | O(1) |
| [`std::get`](#get) | <span class="rank rank-rare">知ってるだけ</span> | コンパイル時の添字でアクセス | O(1) |
| [`rbegin`](#rbegin) | <span class="rank rank-rare">知ってるだけ</span> | 逆順の先頭イテレータ | O(1) |
| [`rend`](#rend) | <span class="rank rank-rare">知ってるだけ</span> | 逆順の終わりイテレータ | O(1) |
| [`cbegin`](#cbegin) | <span class="rank rank-rare">知ってるだけ</span> | const の先頭イテレータ | O(1) |
| [`cend`](#cend) | <span class="rank rank-rare">知ってるだけ</span> | const の終わりイテレータ | O(1) |

`push_back` や `erase` など**要素数を変える関数はありません**。

## よくある使い方

### 1. 固定の表を持つ

```cpp
#include <array>
#include <print>

enum class Direction { kUp, kRight, kDown, kLeft };

struct Offset {
  int dx;
  int dy;
};

// 方向ごとの移動量。添字は Direction の値
constexpr std::array<Offset, 4> kOffsets = {{
    {0, -1},  // kUp
    {1, 0},   // kRight
    {0, 1},   // kDown
    {-1, 0},  // kLeft
}};

int main() {
  int x = 5;
  int y = 5;
  Offset o = kOffsets[static_cast<int>(Direction::kRight)];
  x += o.dx;
  y += o.dy;
  std::println("({}, {})", x, y);
}
```

```text title="実行結果"
(6, 5)
```

`constexpr` を付けるとコンパイル時に作られるので、実行時のコストはゼロです。

### 2. 回して集計する

```cpp
#include <array>
#include <print>

int main() {
  std::array<int, 5> scores = {80, 95, 60, 70, 100};

  int total = 0;
  for (int score : scores) {
    total += score;
  }
  std::println("合計 {} / 平均 {}", total, total / static_cast<int>(scores.size()));
}
```

```text title="実行結果"
合計 405 / 平均 81
```

### 3. 関数から複数の値を返す・コピーする

C の配列は関数から返せず、`=` でコピーもできませんが、`std::array` はできます。

```cpp
#include <array>
#include <print>

std::array<int, 3> MakeRgb(int gray) { return {gray, gray, gray}; }

int main() {
  std::array<int, 3> color = MakeRgb(128);
  std::array<int, 3> backup = color;  // 丸ごとコピー
  color[0] = 255;

  std::println("color = {} / backup = {}", color, backup);
  std::println("同じ？ {}", color == backup);
}
```

```text title="実行結果"
color = [255, 128, 128] / backup = [128, 128, 128]
同じ？ false
```

## 関数の詳しい説明

### operator[] {#operator}

```cpp
constexpr reference operator[](size_type pos);
constexpr const_reference operator[](size_type pos) const;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pos` | `size_type` | 0 始まりの位置 |

- 戻り値: `pos` 番目の要素の参照
- 計算量: O(1)
- 例外: なし。**範囲外は未定義動作**

<div class="anim" data-label="a[1]">
10 20 30 40 # 添字は 0 から
10 *20 30 40 # a[1] は 20。範囲チェックなし
</div>

```cpp
#include <array>
#include <print>

int main() {
  std::array<int, 4> hp = {100, 80, 60, 40};
  hp[2] -= 10;
  std::println("{}", hp[2]);
}
```

```text title="実行結果"
50
```

!!! note "実際は"
    C の配列の `a[i]` と同じ速さです。一番よく使うアクセス方法です。

### size {#size}

```cpp
constexpr size_type size() const noexcept;
```

- 戻り値: 要素数。常に `N`
- 計算量: O(1)（コンパイル時に決まっている）

```cpp
#include <array>
#include <print>

int main() {
  std::array<float, 16> matrix{};
  std::println("{}", matrix.size());
}
```

```text title="実行結果"
16
```

!!! note "実際は"
    C の配列だと `sizeof(a) / sizeof(a[0])` と書く必要がありましたが、`a.size()` で済みます。C の配列でも `std::size(a)` なら使えます。

### begin {#begin}

```cpp
constexpr iterator begin() noexcept;
constexpr const_iterator begin() const noexcept;
```

- 戻り値: 先頭の要素を指すイテレータ
- 計算量: O(1)

### end {#end}

```cpp
constexpr iterator end() noexcept;
constexpr const_iterator end() const noexcept;
```

- 戻り値: 最後の要素の**次**を指すイテレータ
- 計算量: O(1)

```cpp
#include <algorithm>
#include <array>
#include <print>

int main() {
  std::array<int, 5> a = {5, 3, 1, 4, 2};

  // 範囲 for や ranges のアルゴリズムが中で begin / end を使っている
  std::ranges::sort(a);
  std::println("{}", a);

  // 見つからないと end() が返る
  bool found = std::ranges::find(a, 9) != a.end();
  std::println("9 はある？ {}", found);
}
```

```text title="実行結果"
[1, 2, 3, 4, 5]
9 はある？ false
```

!!! note "実際は"
    [vector の begin / end](vector.md#begin) と同じです。直接書くのは「見つからなかった」の判定くらいです。

### fill {#fill}

```cpp
constexpr void fill(const T& value);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `value` | `const T&` | 全要素に入れる値 |

- 計算量: O(N)

<div class="anim" data-label="a.fill(0)">
1 2 3 4 # a = {1, 2, 3, 4}
+0 +0 +0 +0 # 全要素が 0 になる。大きさは変わらない
</div>

```cpp
#include <array>
#include <print>

int main() {
  std::array<int, 6> slots{};
  slots.fill(-1);  // -1 = 空きスロット
  std::println("{}", slots);
}
```

```text title="実行結果"
[-1, -1, -1, -1, -1, -1]
```

!!! note "実際は"
    「全部リセット」に使います。0 に戻すだけなら `a = {};` でも同じです。

### operator== {#eq}

```cpp
template <class T, std::size_t N>
constexpr bool operator==(const array<T, N>& lhs, const array<T, N>& rhs);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `lhs`, `rhs` | 同じ型・同じ大きさの array | 比べる 2 つ |

- 戻り値: 全要素が等しければ `true`。`!=` も使える
- 計算量: O(N)

```cpp
#include <array>
#include <print>

int main() {
  std::array<int, 3> answer = {1, 2, 3};
  std::array<int, 3> input = {1, 2, 3};
  std::println("正解？ {}", input == answer);
}
```

```text title="実行結果"
正解？ true
```

!!! note "実際は"
    パズルの答え合わせ、コマンド入力の一致判定などに使えます。C の配列は `==` で比べるとアドレスの比較になってしまいますが、array は中身を比べてくれます。

### operator<=> {#spaceship}

```cpp
template <class T, std::size_t N>
constexpr auto operator<=>(const array<T, N>& lhs, const array<T, N>& rhs);
```

- 戻り値: 先頭から順に比べた結果（辞書順）。`<`, `>`, `<=`, `>=` が使えるようになる
- 計算量: O(N)

```cpp
#include <array>
#include <print>

int main() {
  // バージョン番号 {メジャー, マイナー, パッチ}
  std::array<int, 3> save_version = {1, 2, 9};
  std::array<int, 3> game_version = {1, 3, 0};
  std::println("古いセーブ？ {}", save_version < game_version);
}
```

```text title="実行結果"
古いセーブ？ true
```

!!! note "実際は"
    `std::map` のキーにしたり、`std::ranges::sort` で並べたりするときに自動で使われます。直接書くことはあまりありません。

### data {#data}

```cpp
constexpr T* data() noexcept;
constexpr const T* data() const noexcept;
```

- 戻り値: 先頭要素へのポインタ
- 計算量: O(1)

```cpp
// シェーダーに 4x4 行列を渡す（OpenGL の例）
std::array<float, 16> mvp = BuildMatrix();
glUniformMatrix4fv(location, 1, GL_FALSE, mvp.data());
```

!!! note "実際は"
    C の API にポインタで渡すときに使います。

### front {#front}

```cpp
constexpr reference front();
constexpr const_reference front() const;
```

- 戻り値: 先頭の要素の参照（`a[0]` と同じ）
- 計算量: O(1)
- `N == 0` のときは未定義動作

<div class="anim" data-label="a.front()">
10 20 30 # a
*10 20 30 # 先頭の要素
</div>

### back {#back}

```cpp
constexpr reference back();
constexpr const_reference back() const;
```

- 戻り値: 末尾の要素の参照（`a[N - 1]` と同じ）
- 計算量: O(1)
- `N == 0` のときは未定義動作

<div class="anim" data-label="a.back()">
10 20 30 # a
10 20 *30 # 最後の要素
</div>

```cpp
#include <array>
#include <print>

int main() {
  std::array<int, 4> checkpoints = {0, 120, 300, 500};
  std::println("スタート {} / ゴール {}", checkpoints.front(),
               checkpoints.back());
}
```

```text title="実行結果"
スタート 0 / ゴール 500
```

!!! note "実際は"
    `a[0]` / `a[a.size() - 1]` と書くより意図がはっきりします。

### at {#at}

```cpp
constexpr reference at(size_type pos);
constexpr const_reference at(size_type pos) const;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pos` | `size_type` | 0 始まりの位置 |

- 例外: 範囲外なら `std::out_of_range`
- 計算量: O(1)

<div class="anim" data-label="a.at(1)">
10 20 30 40 # 添字は 0 から
10 *20 30 40 # a.at(1) は 20。範囲外なら例外
</div>

```cpp
#include <array>
#include <print>
#include <stdexcept>

int main() {
  std::array<int, 3> a = {1, 2, 3};
  try {
    a.at(5) = 0;
  } catch (const std::out_of_range&) {
    std::println("範囲外");
  }
}
```

```text title="実行結果"
範囲外
```

!!! note "実際は"
    ゲームでは例外を使わないことが多いので、`[]` と事前のチェックで済ませるのが普通です。

### swap {#swap}

```cpp
constexpr void swap(array& other) noexcept(/* T の swap が noexcept なら */);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `other` | `array&` | 交換する相手（同じ型・同じ大きさ） |

- 計算量: <strong>O(N)</strong>

<div class="anim" data-label="a.swap(b)">
1 2 3 | 7 8 9 # a と b
>7 >8 >9 | >1 >2 >3 # 要素を 1 つずつ入れ替える。O(n)
</div>

```cpp
#include <array>
#include <print>

int main() {
  std::array<int, 3> a = {1, 2, 3};
  std::array<int, 3> b = {7, 8, 9};
  a.swap(b);
  std::println("a = {} / b = {}", a, b);
}
```

```text title="実行結果"
a = [7, 8, 9] / b = [1, 2, 3]
```

!!! warning "vector の swap とは速さが違う"
    `std::vector::swap` はポインタを交換するだけで O(1) ですが、`std::array` は中身が本体に直接入っているので全要素の交換になります。

### empty {#empty}

```cpp
constexpr bool empty() const noexcept;
```

- 戻り値: `N == 0` なら `true`。array の大きさは変わらないので、結果は常に同じ
- 計算量: O(1)

!!! note "実際は"
    使いません。テンプレートで「vector でも array でも動く」コードを書くときに、名前がそろっていると便利、というだけのものです。

### max_size {#max_size}

```cpp
constexpr size_type max_size() const noexcept;
```

- 戻り値: 常に `N`（`size()` と同じ）
- 計算量: O(1)

!!! note "実際は"
    使いません。`empty` と同じく、他のコンテナと名前をそろえるためにあります。

### std::get {#get}

```cpp
template <std::size_t I, class T, std::size_t N>
constexpr T& get(array<T, N>& a) noexcept;
```

| テンプレート引数 | 意味 |
| --- | --- |
| `I` | 位置。**コンパイル時の定数** |

- 戻り値: `I` 番目の要素の参照
- 範囲外は**コンパイルエラー**になる（実行時の未定義動作にならない）

```cpp
#include <array>
#include <print>

int main() {
  std::array<float, 3> pos = {1.0f, 2.0f, 3.0f};
  std::println("y = {}", std::get<1>(pos));

  // 構造化束縛でも分解できる（中で std::get が使われている）
  auto [x, y, z] = pos;
  std::println("{} {} {}", x, y, z);
}
```

```text title="実行結果"
y = 2
1 2 3
```

!!! note "実際は"
    直接書くことはまずなく、`auto [x, y, z] = pos;` の形で間接的に使います。

### rbegin {#rbegin}

```cpp
constexpr reverse_iterator rbegin() noexcept;
```

- 戻り値: 最後の要素を指す逆向きのイテレータ
- 計算量: O(1)

### rend {#rend}

```cpp
constexpr reverse_iterator rend() noexcept;
```

- 戻り値: 最初の要素の 1 つ前を指す逆向きのイテレータ
- 計算量: O(1)

```cpp
#include <array>
#include <print>

int main() {
  std::array<int, 3> a = {1, 2, 3};
  for (auto it = a.rbegin(); it != a.rend(); ++it) {
    std::print("{} ", *it);
  }
  std::println("");
}
```

```text title="実行結果"
3 2 1 
```

!!! note "実際は"
    `std::views::reverse` で足ります。直接書くことはまずありません。

### cbegin {#cbegin}

```cpp
constexpr const_iterator cbegin() const noexcept;
```

- 戻り値: 先頭を指す const イテレータ（要素を書き換えられない）

### cend {#cend}

```cpp
constexpr const_iterator cend() const noexcept;
```

- 戻り値: 最後の次を指す const イテレータ

!!! note "実際は"
    `const auto&` の範囲 for で足りるので使いません。

## フラグ・オプション

フラグはありません。

## 計算量まとめ

| 操作 | 計算量 |
| --- | --- |
| `[]`, `at`, `front`, `back`, `size` | O(1) |
| `fill`, 比較, コピー | O(N) |
| `swap` | O(N) |

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    int scores[5] = {80, 95, 60, 70, 100};
    int count = sizeof(scores) / sizeof(scores[0]);

    // 関数に渡すとポインタになり、個数が分からなくなる
    void Print(int* values, int count);
    ```

=== "今の書き方"

    ```cpp
    std::array<int, 5> scores = {80, 95, 60, 70, 100};
    std::size_t count = scores.size();

    // span で受ければ個数ごと渡せる
    void Print(std::span<const int> values);
    ```

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| 方向・隣接マス | `std::array<Offset, 4>` / `std::array<Offset, 8>` |
| 装備・アイテムスロット | `std::array<ItemId, 10>` |
| キー設定 | `std::array<KeyCode, kActionCount>` |
| 座標・色・行列 | `std::array<float, 3>`、`std::array<float, 16>` |
| 小さい固定の盤面 | `std::array<std::array<int, 8>, 8>`（オセロなど） |

!!! note "2 次元は array の array でも OK"
    vector の vector は行ごとにメモリがバラバラになりますが、array の array は**全部が 1 本に連続して並ぶ**ので速いです。サイズが固定なら素直にこれで書けます。

## パフォーマンス

- 中身は**オブジェクトの中に直接**入ります。ヒープ確保はゼロです。
- その代わり、**大きい array をローカル変数にするとスタックを食います**。`std::array<int, 1000000>` をローカルに置くとスタックオーバーフローします。大きいものは vector にするか、`static` / メンバ変数にします。
- 関数に値渡しすると**全要素がコピー**されます。`const std::array<T, N>&` か `std::span<const T>` で渡します。

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| 範囲外の `[]` | 未定義動作 |
| `{}` を付けずに作って読む | 不定値（未定義動作） |
| `N == 0` で `front()` / `back()` | 未定義動作 |
| `at()` で範囲外 | `std::out_of_range` 例外 |

## よくあるミス

??? failure "初期化を忘れる"
    ```cpp
    std::array<int, 4> hp;      // 中身はゴミ
    std::array<int, 4> hp2{};   // OK: 全部 0
    ```

??? failure "要素数に変数を使う"
    ```cpp
    int n = 10;
    std::array<int, n> a;  // コンパイルエラー: n は定数ではない

    constexpr int kN = 10;
    std::array<int, kN> b{};  // OK
    ```

    実行時に個数が決まるなら `std::vector` を使います。

??? failure "構造体の配列で `{}` が足りない"
    ```cpp
    // 古いコンパイラや警告設定によってはエラー・警告になる
    std::array<Offset, 2> a = {{0, 1}, {1, 0}};

    // 外側に {} を 1 つ足すと確実
    std::array<Offset, 2> b = {{{0, 1}, {1, 0}}};
    ```

    `std::array` は「C の配列を 1 つ持った構造体」なので、外側にもう 1 組 `{}` が必要になることがあります。

## 類似クラス

| 名前 | 違い | こっちを使うとき |
| --- | --- | --- |
| [`std::vector`](vector.md) | 要素数が変わる。ヒープを使う | 個数が実行時に決まる・変わる |
| C の配列 `T[N]` | 同じ速さだが、コピー・比較・返り値にできない | 使わない（古いコードとの互換くらい） |
| [`std::span`](span.md) | 中身を持たない「借りる」だけの型 | 関数の引数 |
| [`std::bitset`](bitset.md) | bool を 1 ビットずつ詰めた固定長 | フラグの集まり |

## コンパイラ対応

C++11 からある機能なので、すべてのコンパイラで使えます。`std::to_array`（C++20）と範囲の `println` 出力（C++23）だけ新しめのコンパイラが必要です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 個数が決まっているなら C の配列ではなく `std::array<T, N>`
    - [x] 必ず `{}` で初期化する
    - [x] 個数が変わるなら `std::vector`
    - [x] 大きい array をローカル変数にしない（スタックが溢れる）

## 関連ページ

- [cpprefjp: std::array](https://cpprefjp.github.io/reference/array/array.html)
- [cppreference: std::array](https://en.cppreference.com/w/cpp/container/array)
