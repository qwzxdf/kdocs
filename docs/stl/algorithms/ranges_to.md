---
title: std::ranges::to
tags:
  - アルゴリズム
  - ranges
---

# std::ranges::to

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-23">C++23</span>
`#include <ranges>`
</div>

`std::ranges::to` は、**範囲（ビューなど）から vector や map などのコンテナを作る**関数です。[`std::views`](views.md) で絞り込んだり変換したりした結果は「見えているだけ」で実体がありませんが、最後に `| std::ranges::to<std::vector>()` を付けると、その結果を持った本物の vector ができます。

!!! tip "ポイント"
    - <strong>ビューの結果を保存したいときは、最後に `| std::ranges::to<std::vector>()`。</strong>
    - 要素の型は推論されるので、`std::vector<int>` と書かずに `std::vector` だけでいい。
    - 別のコンテナにも変換できる（`std::set`、`std::string`、`std::map` など）。
    - 新しいコンテナを作る（メモリ確保が起きる）ので、毎フレーム大量に呼ぶと重い。

!!! info "このページを読む前に"
    [`std::views`](views.md) を先に読むと分かりやすいです。

## 関数一覧

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`std::ranges::to<Container>()`](#to-template) | <span class="rank rank-often">よく使う</span> | 型を推論してコンテナを作る（`std::vector` など） | O(n) |
| [`std::ranges::to<Container<T>>()`](#to-type) | <span class="rank rank-sometimes">たまに</span> | 要素の型まで指定して作る | O(n) |

## よくある使い方

### 1. 絞り込んだ結果を vector にする

```cpp
#include <print>
#include <ranges>
#include <vector>

struct Enemy {
  int id;
  int hp;
};

int main() {
  std::vector<Enemy> enemies = {{1, 0}, {2, 30}, {3, 80}};

  std::vector<int> alive_ids = enemies
      | std::views::filter([](const Enemy& e) { return e.hp > 0; })
      | std::views::transform(&Enemy::id)
      | std::ranges::to<std::vector>();

  std::println("{}", alive_ids);
}
```

```text title="実行結果"
[2, 3]
```

### 2. 連番の vector を作る

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  auto indices = std::views::iota(0, 5) | std::ranges::to<std::vector>();
  std::println("{}", indices);
}
```

```text title="実行結果"
[0, 1, 2, 3, 4]
```

### 3. 重複を除いて並べる（set に変換）

```cpp
#include <print>
#include <ranges>
#include <set>
#include <vector>

int main() {
  std::vector<int> drops = {3, 1, 3, 2, 1};
  auto kinds = drops | std::ranges::to<std::set>();
  std::println("{}", kinds);
}
```

```text title="実行結果"
{1, 2, 3}
```

## 関数の詳しい説明

### std::ranges::to&lt;Container&gt;() {#to-template}

```cpp
template <template <class...> class C, class... Args>
constexpr auto to(Args&&... args);                 // パイプ用: r | to<C>()

template <template <class...> class C, input_range R, class... Args>
constexpr auto to(R&& r, Args&&... args);          // 関数呼び出し用: to<C>(r)
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `C` | テンプレート（`std::vector` など） | 作るコンテナの種類。要素の型は範囲から推論される |
| `r` | 範囲 | 元になる範囲（パイプなら左側） |
| `args` | 何個でも | コンテナのコンストラクタに追加で渡す引数（アロケータなど。普通は無し） |

- 戻り値: 新しいコンテナ
- 計算量: O(n)。大きさが分かる範囲なら、最初に必要な分だけ確保する

```cpp
#include <print>
#include <ranges>
#include <string>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};
  auto doubled = std::ranges::to<std::vector>(v | std::views::transform([](int x) {
                                                return x * 2;
                                              }));
  std::println("{}", doubled);
}
```

```text title="実行結果"
[2, 4, 6]
```

### std::ranges::to&lt;Container&lt;T&gt;&gt;() {#to-type}

```cpp
template <class C, class... Args>
constexpr C to(Args&&... args);

template <class C, input_range R, class... Args>
constexpr C to(R&& r, Args&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `C` | 型（`std::vector<float>` など） | 作るコンテナの型。要素の型を変えたいときに使う |

```cpp
#include <map>
#include <print>
#include <ranges>
#include <string>
#include <utility>
#include <vector>

int main() {
  std::vector<int> ints = {1, 2, 3};
  auto floats = ints | std::ranges::to<std::vector<float>>();  // int → float
  std::println("{}", floats);

  // pair の範囲から map を作る
  std::vector<std::pair<std::string, int>> pairs = {{"hp", 100}, {"mp", 30}};
  auto stats = pairs | std::ranges::to<std::map<std::string, int>>();
  std::println("{}", stats);

  // 文字の範囲から string を作る
  auto upper = std::string("abc")
             | std::views::transform([](char c) { return static_cast<char>(c - 32); })
             | std::ranges::to<std::string>();
  std::println("{}", upper);
}
```

```text title="実行結果"
[1, 2, 3]
{"hp": 100, "mp": 30}
ABC
```

## フラグ・オプション

`to<>` に指定するものです。

| 指定 | 重要度 | 作られるもの |
| --- | --- | --- |
| `std::vector` | <span class="rank rank-must">必須</span> | 要素の型を推論した vector |
| `std::string` | <span class="rank rank-sometimes">たまに</span> | 文字の範囲から文字列 |
| `std::set` / `std::unordered_set` | <span class="rank rank-sometimes">たまに</span> | 重複を除いた集合 |
| `std::map` / `std::unordered_map` | <span class="rank rank-sometimes">たまに</span> | pair の範囲から表 |
| `std::vector<T>` | <span class="rank rank-sometimes">たまに</span> | 要素を `T` に変換した vector |

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    std::vector<int> alive_ids;
    for (const auto& e : enemies) {
      if (e.hp > 0) {
        alive_ids.push_back(e.id);
      }
    }
    ```

=== "今の書き方（C++23）"

    ```cpp
    auto alive_ids = enemies
        | std::views::filter([](const Enemy& e) { return e.hp > 0; })
        | std::views::transform(&Enemy::id)
        | std::ranges::to<std::vector>();
    ```

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| 条件に合う ID のリストを作る | ターゲット候補、選択中のユニット |
| ビューの結果を何度も使う | 一度実体化しておくと、毎回 filter しなくて済む |
| 読み込んだデータを整形 | 文字列を分割して vector にする |

## パフォーマンス

- 新しいコンテナを作るので、メモリ確保が起きます。毎フレーム呼ぶなら、vector を使い回して `clear()` + `append_range()` するほうが確保が減ります。

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| メモリ不足 | `std::bad_alloc` 例外 |

## よくあるミス

??? failure "() を付け忘れる"
    ```cpp
    auto v = r | std::ranges::to<std::vector>;    // コンパイルエラー
    auto v2 = r | std::ranges::to<std::vector>();  // OK
    ```

??? failure "vector<bool> に注意"
    bool の範囲を `to<std::vector>()` すると `std::vector<bool>`（特殊な型）になります。参照が取れないなどの制限があります。

## 理解度チェック

!!! question "Q1. 何が出力される？"
    ```cpp
    auto v = std::views::iota(1, 6)
           | std::views::transform([](int x) { return x * 10; })
           | std::ranges::to<std::vector>();
    std::println("{} {}", v.size(), v.back());
    ```

    <div class="spoiler" markdown>

    **答え:** `5 50`。

    </div>

## 類似

| 名前 | 違い |
| --- | --- |
| `std::vector(std::from_range, r)` | コンストラクタで作る（型は自分で書く） |
| `v.append_range(r)` | 既にある vector の末尾に追加する |
| [`std::ranges::copy`](copy_fill.md) | 既にある場所へコピーする |

## コンパイラ対応

| 機能 | MSVC | GCC | Clang (libc++) |
| --- | --- | --- | --- |
| `std::ranges::to` <span class="ver ver-23">C++23</span> | VS 2022 17.4〜 | 14〜 | 17〜 |

## これだけ覚える

!!! abstract "まとめ"
    - [x] ビューの結果を保存するなら `| std::ranges::to<std::vector>()`
    - [x] `()` を忘れない
    - [x] set / map / string にも変換できる

## 関連ページ

- [cpprefjp: std::ranges::to](https://cpprefjp.github.io/reference/ranges/to.html)
- [cppreference: std::ranges::to](https://en.cppreference.com/w/cpp/ranges/to)
