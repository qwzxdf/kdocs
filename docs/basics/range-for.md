---
title: 範囲 for
tags:
  - 基礎
---

# 範囲 for

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">C++11</span>
</div>

**範囲 for** は、**コンテナの要素を先頭から順に 1 つずつ取り出して処理するループ**です。`for (要素の変数 : コンテナ)` と書くだけで、添字やイテレータを自分で管理しなくても全要素を回せます。vector、array、string、map、C の配列、ビューなど、`begin()` と `end()` があるものなら何でも回せます。

!!! tip "ポイント"
    - <strong>読むだけなら `for (const auto& x : v)`、書き換えるなら `for (auto& x : v)`。</strong>
    - `for (auto x : v)` は毎回コピーになる（int など小さい型なら OK）。
    - 番号も欲しいなら C++23 の `std::views::enumerate`。
    - **ループの中で同じコンテナに追加・削除しない**（イテレータが壊れる）。

## 基本

```cpp
#include <print>
#include <vector>

int main() {
  std::vector<int> hp = {30, 50, 80};

  for (int& h : hp) {  // 参照なので元が書き換わる
    h -= 10;
  }
  for (const int& h : hp) {  // 読むだけ
    std::print("{} ", h);
  }
  std::println("");
}
```

```text title="実行結果"
20 40 70 
```

## 詳しく

### 変数の型の使い分け

| 書き方 | 重要度 | 意味 | 使うとき |
| --- | --- | --- | --- |
| `const auto& x` | <span class="rank rank-must">必須</span> | 読むだけ。コピーしない | ほとんどの場合 |
| `auto& x` | <span class="rank rank-must">必須</span> | 書き換える | 要素を更新する |
| `auto x` | <span class="rank rank-often">よく使う</span> | コピーを受け取る | int、float など小さい型、コピーが欲しいとき |
| `auto&& x` | <span class="rank rank-rare">知ってるだけ</span> | 何でも受け取る | `vector<bool>` やビューなど特殊な範囲（テンプレートの中） |

### map を回す（構造化束縛）

```cpp
#include <map>
#include <print>
#include <string>

int main() {
  std::map<std::string, int> stock = {{"potion", 3}, {"ether", 1}};
  for (const auto& [name, count] : stock) {
    std::println("{} x{}", name, count);
  }
}
```

```text title="実行結果"
ether x1
potion x3
```

### 番号付きで回す

```cpp
#include <print>
#include <ranges>
#include <string>
#include <vector>

int main() {
  std::vector<std::string> menu = {"はじめる", "つづき", "設定"};
  for (auto [i, item] : menu | std::views::enumerate) {  // C++23
    std::println("{}: {}", i, item);
  }
}
```

```text title="実行結果"
0: はじめる
1: つづき
2: 設定
```

### 初期化文付き（C++20）

```cpp
#include <print>
#include <vector>

std::vector<int> LoadScores() { return {70, 90}; }

int main() {
  for (auto scores = LoadScores(); int s : scores) {  // ループの前に変数を作れる
    std::println("{}", s);
  }
}
```

```text title="実行結果"
70
90
```

### 中で何が起きているか

```cpp
for (auto& x : v) {
  // 処理
}
```

は、だいたい次と同じ意味です。

```cpp
for (auto it = v.begin(); it != v.end(); ++it) {
  auto& x = *it;
  // 処理
}
```

なので、`begin()` / `end()` を持つ自作のクラスも範囲 for で回せます（[イテレータ](iterator.md)）。

### 後ろから・一部だけ回す

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4, 5};
  for (int x : v | std::views::reverse) {
    std::print("{} ", x);
  }
  std::println("");
  for (int x : v | std::views::drop(1) | std::views::take(3)) {
    std::print("{} ", x);
  }
  std::println("");
}
```

```text title="実行結果"
5 4 3 2 1 
2 3 4 
```

## ゲームでの例

```cpp
for (auto& enemy : enemies) {
  enemy.Update(delta_time);
}
for (const auto& sprite : sprites) {
  renderer.Draw(sprite);
}
```

## よくあるミス

??? failure "auto で受けて書き換わらない"
    ```cpp
    for (auto e : enemies) {
      e.hp -= 10;  // コピーを変えているだけ
    }
    ```

??? failure "ループ中に push_back / erase する"
    ```cpp
    for (auto& e : enemies) {
      if (e.splits) {
        enemies.push_back(Enemy{});  // 再確保でループが壊れる
      }
    }
    ```

    追加するものは別の vector に溜めておき、ループの後で `append_range` します。削除は [`std::erase_if`](../stl/algorithms/erase_if.md) を使います。

??? failure "一時オブジェクトのメンバを回す"
    ```cpp
    for (auto& x : GetPlayer().inventory) {}  // C++20 までは GetPlayer() の結果がすぐ消える
    ```

    C++23 で一時オブジェクトの寿命が延びるように修正されましたが、古いコンパイラでは未定義動作です。いったん変数に受けてから回すと安全です。

## 理解度チェック

!!! question "Q1. string `s = \"abc\"` を範囲 for で回すと、変数には何が入る？"
    <div class="spoiler" markdown>

    **答え:** 1 文字ずつの `char`（`'a'`, `'b'`, `'c'`）。

    </div>

## これだけ覚える

!!! abstract "まとめ"
    - [x] 読むだけ `const auto&`、書き換え `auto&`
    - [x] map は `const auto& [key, value]`
    - [x] ループ中に同じコンテナへ追加・削除しない

## 関連ページ

- [イテレータ](iterator.md)
- [std::views](../stl/algorithms/views.md)
- [cppreference: Range-based for loop](https://en.cppreference.com/w/cpp/language/range-for)
