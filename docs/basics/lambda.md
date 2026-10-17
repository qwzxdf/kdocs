---
title: ラムダ式
tags:
  - 基礎
---

# ラムダ式

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">C++11</span>
</div>

**ラムダ式**は、**その場で書ける名前の無い小さな関数**です。`[](int x) { return x * 2; }` のように書きます。`std::ranges::sort` の並べ方、`std::erase_if` の消す条件、ボタンを押したときの処理など、「関数を渡す」場面で、わざわざ別の場所に関数を定義せずに済みます。外の変数を取り込んで（キャプチャして）使えるのが、普通の関数との大きな違いです。

!!! tip "ポイント"
    - 形は `[キャプチャ](引数) { 処理 }`。
    - 外の変数を使うなら `[&]`（参照で取り込む）か `[=]`（コピーで取り込む）。**変数名を個別に書く（`[&score]`）のがおすすめ**。
    - その場で使うなら参照キャプチャで OK。**あとで呼ばれる（保存される）なら、参照キャプチャした変数が消えていないか注意**。
    - 引数を `auto` にすると、どんな型でも受け取れる（ジェネリックラムダ）。

!!! info "このページを読む前に"
    [参照](reference.md) を先に読むと、キャプチャの違いが分かりやすいです。

## 基本

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  // 変数に入れて呼ぶ
  auto twice = [](int x) { return x * 2; };
  std::println("{}", twice(21));

  // アルゴリズムに直接渡す
  std::vector<int> hp = {30, 0, 50, -5};
  std::erase_if(hp, [](int h) { return h <= 0; });
  std::println("{}", hp);
}
```

```text title="実行結果"
42
[30, 50]
```

## 詳しく

### 書き方の部品

```text
[キャプチャ](引数) 指定子 -> 戻り値の型 { 処理 }
```

| 部品 | 省略 | 意味 |
| --- | --- | --- |
| `[キャプチャ]` | 不可（空なら `[]`） | 外の変数をどう取り込むか |
| `(引数)` | 引数が無ければ省略可 | 普通の関数の引数と同じ |
| 指定子 | 可 | `mutable`（コピーしたものを書き換える）、`constexpr` など |
| `-> 戻り値の型` | 可（推論される） | 戻り値の型を明示したいとき |
| `{ 処理 }` | 不可 | 中身 |

### キャプチャの種類

| 書き方 | 重要度 | 意味 |
| --- | --- | --- |
| `[]` | <span class="rank rank-must">必須</span> | 何も取り込まない |
| `[&x]` | <span class="rank rank-must">必須</span> | x を**参照**で取り込む（中で変えると外も変わる） |
| `[x]` | <span class="rank rank-often">よく使う</span> | x を**コピー**で取り込む（作った時点の値） |
| `[this]` | <span class="rank rank-often">よく使う</span> | メンバ関数の中で、メンバを使う |
| `[&]` | <span class="rank rank-often">よく使う</span> | 使った変数を全部参照で |
| `[=]` | <span class="rank rank-sometimes">たまに</span> | 使った変数を全部コピーで |
| `[x = 式]` | <span class="rank rank-sometimes">たまに</span> | 新しい名前で取り込む（`[p = std::move(ptr)]` でムーブ） <span class="ver ver-14">C++14</span> |
| `[*this]` | <span class="rank rank-rare">知ってるだけ</span> | オブジェクト全体をコピーで <span class="ver ver-17">C++17</span> |

```cpp
#include <print>

int main() {
  int score = 0;
  int bonus = 10;

  auto add = [&score, bonus](int base) { score += base + bonus; };  // score は参照、bonus はコピー
  bonus = 999;  // ラムダの中の bonus は 10 のまま
  add(5);
  add(5);
  std::println("{}", score);
}
```

```text title="実行結果"
30
```

### ジェネリックラムダ（auto 引数）

```cpp
#include <print>
#include <string>

int main() {
  auto show = [](const auto& x) { std::println("[{}]", x); };
  show(1);
  show(2.5);
  show(std::string("text"));
}
```

```text title="実行結果"
[1]
[2.5]
[text]
```

### mutable

コピーで取り込んだ変数は、普通は中で書き換えられません。`mutable` を付けると書き換えられます（ラムダごとに自分の値を持つ）。

```cpp
#include <print>

int main() {
  auto counter = [count = 0]() mutable { return ++count; };
  counter();
  counter();
  std::println("{}", counter());
}
```

```text title="実行結果"
3
```

### メンバ関数の中で使う

```cpp
#include <algorithm>
#include <print>
#include <vector>

class Spawner {
 public:
  void RemoveFar(std::vector<float>& distances) const {
    // this を取り込むとメンバ（max_distance_）が使える
    std::erase_if(distances, [this](float d) { return d > max_distance_; });
  }

 private:
  float max_distance_ = 50.0f;
};

int main() {
  std::vector<float> d = {10.0f, 80.0f, 40.0f};
  Spawner().RemoveFar(d);
  std::println("{}", d);
}
```

```text title="実行結果"
[10, 40]
```

### 変数に入れる・保存する

| 入れ物 | 使うとき |
| --- | --- |
| `auto f = [...]` | その場で使う。一番速い |
| [`std::function<R(Args)>`](../stl/utilities/function.md) | メンバ変数に保存する、vector に入れる |
| 関数ポインタ `R(*)(Args)` | キャプチャが無いラムダだけ変換できる。C の API に渡す |

## ゲームでの例

| 場面 | 例 |
| --- | --- |
| 並べ替えの基準 | `std::ranges::sort(units, [](const auto& a, const auto& b) { ... })` |
| 削除の条件 | `std::erase_if(bullets, [](const Bullet& b) { return b.dead; })` |
| コールバック | `button.OnClick([this] { OpenMenu(); })` |
| 遅延実行 | `timer.After(2s, [id] { Explode(id); })` |

## よくあるミス

??? failure "参照キャプチャした変数が先に消える"
    ```cpp
    std::function<void()> MakeTimerCallback() {
      int count = 0;
      return [&count] { ++count; };  // count は関数を抜けると消える
    }
    ```

    保存されるラムダでは、ローカル変数はコピーで取り込みます。

??? failure "[&] / [=] で何を取り込んだか分からなくなる"
    `[&]` は便利ですが、長いラムダだと「何に依存しているか」が見えにくくなります。取り込む変数を明示すると読みやすく、間違いも減ります。

??? failure "[=] で this が取り込まれる"
    メンバ関数の中の `[=]` は、メンバ変数を使うと `this`（ポインタ）を取り込みます。オブジェクトが消えたあとに呼ばれると壊れます。C++20 では `[=]` での暗黙の this キャプチャは非推奨です。

## 理解度チェック

!!! question "Q1. 何が出力される？"
    ```cpp
    int x = 1;
    auto a = [x] { return x; };
    auto b = [&x] { return x; };
    x = 5;
    std::println("{} {}", a(), b());
    ```

    <div class="spoiler" markdown>

    **答え:** `1 5`。a は作ったときの値（1）のコピー、b は x そのものを参照しています。

    </div>

## これだけ覚える

!!! abstract "まとめ"
    - [x] `[キャプチャ](引数) { 処理 }`
    - [x] 参照 `[&x]`、コピー `[x]`、メンバは `[this]`
    - [x] 保存されるラムダの参照キャプチャに注意
    - [x] 引数を `auto` にすると何でも受け取れる

## 関連ページ

- [std::function](../stl/utilities/function.md)
- [cpprefjp: ラムダ式](https://cpprefjp.github.io/lang/cpp11/lambda_expressions.html)
