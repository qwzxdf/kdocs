---
title: std::views（範囲を加工して見る）
group: ビュー（std::views）
summary: "範囲をコピーせずに絞り込み（`filter`）や変換（`transform`）をして「見る」。"
order: 0
tags:
  - アルゴリズム
  - ranges
---

# std::views（範囲を加工して見る）

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

配列の中から条件に合うものだけを取り出して、変換して、並べ替えて……と処理を重ねると、そのたびに一時的な `vector` を作ることになり、コードもメモリも膨らみます。`std::views` は、元のデータを変えずに「加工して見る」ための部品（ビュー）の集まりです。`v | std::views::filter(条件)` と書くと「条件に合う要素だけが見える範囲」が `| std::views::transform(関数)` と書くと「各要素を変換した結果が見える範囲」ができます。`|` でいくつもつなげられ、実際の計算は取り出すときに初めて行われます。

!!! tip "ポイント"
    - よく使うのは `filter`（絞り込み）、`transform`（変換）、`reverse`（逆順）、`take` / `drop`（先頭 n 個 / n 個飛ばす）、`iota`（連番）、`enumerate`（番号付き）。
    - <strong>新しい vector は作られない。</strong> 欲しければ最後に [`| std::ranges::to<std::vector>()`](ranges_to.md)。
    - 元のデータを参照しているので、**元が消えたり再確保されたりするとビューも壊れる**。ビューは作ったその場で使い切る。
    - 毎フレームの重い処理に何段もつなげると、普通の for ループより読みにくく・遅くなることもある。2〜3 段までが目安。

!!! info "このページを読む前に"
    [ranges とビュー](../../basics/ranges.md)、[ラムダ式](../../basics/lambda.md) を先に読むと分かりやすいです。

## ビュー一覧

1 つずつ、専用のページがあります。

| ビュー | 重要度 | 何をする | 追加 |
| --- | --- | --- | --- |
| [`views::filter`](views/filter.md) | <span class="rank rank-must">必須</span> | 条件に合う要素だけ | <span class="ver ver-20">C++20</span> |
| [`views::transform`](views/transform.md) | <span class="rank rank-must">必須</span> | 各要素を変換 | <span class="ver ver-20">C++20</span> |
| [`views::iota`](views/iota.md) | <span class="rank rank-often">よく使う</span> | 連番 `0, 1, 2, ...` | <span class="ver ver-20">C++20</span> |
| [`views::reverse`](views/reverse.md) | <span class="rank rank-often">よく使う</span> | 逆順 | <span class="ver ver-20">C++20</span> |
| [`views::enumerate`](views/enumerate.md) | <span class="rank rank-often">よく使う</span> | `(番号, 要素)` の組 | <span class="ver ver-23">C++23</span> |
| [`views::take`](views/take.md) | <span class="rank rank-often">よく使う</span> | 先頭 n 個 | <span class="ver ver-20">C++20</span> |
| [`views::drop`](views/drop.md) | <span class="rank rank-often">よく使う</span> | 先頭 n 個を飛ばす | <span class="ver ver-20">C++20</span> |
| [`views::zip`](views/zip.md) | <span class="rank rank-often">よく使う</span> | 複数の範囲を組にして並べる | <span class="ver ver-23">C++23</span> |
| [`views::keys`](views/keys.md) | <span class="rank rank-sometimes">たまに</span> | map などのキーだけ | <span class="ver ver-20">C++20</span> |
| [`views::values`](views/values.md) | <span class="rank rank-sometimes">たまに</span> | map などの値だけ | <span class="ver ver-20">C++20</span> |
| [`views::split`](views/split.md) | <span class="rank rank-sometimes">たまに</span> | 区切りで分割 | <span class="ver ver-20">C++20</span> |
| [`views::take_while`](views/take_while.md) | <span class="rank rank-sometimes">たまに</span> | 条件を満たす間だけ | <span class="ver ver-20">C++20</span> |
| [`views::drop_while`](views/drop_while.md) | <span class="rank rank-sometimes">たまに</span> | 条件を満たす間は飛ばす | <span class="ver ver-20">C++20</span> |
| [`views::chunk`](views/chunk.md) | <span class="rank rank-sometimes">たまに</span> | n 個ずつに区切る | <span class="ver ver-23">C++23</span> |
| [`views::chunk_by`](views/chunk_by.md) | <span class="rank rank-sometimes">たまに</span> | 条件で区切る | <span class="ver ver-23">C++23</span> |
| [`views::slide`](views/slide.md) | <span class="rank rank-sometimes">たまに</span> | n 個ずつずらしながら見る | <span class="ver ver-23">C++23</span> |
| [`views::stride`](views/stride.md) | <span class="rank rank-sometimes">たまに</span> | n 個おきに | <span class="ver ver-23">C++23</span> |
| [`views::join`](views/join.md) | <span class="rank rank-sometimes">たまに</span> | 入れ子の範囲を 1 本につなげる | <span class="ver ver-20">C++20</span> |
| [`std::ranges::subrange`](views/subrange.md) | <span class="rank rank-sometimes">たまに</span> | 2 つのイテレータを 1 つの範囲に | <span class="ver ver-20">C++20</span> |
| [`views::cartesian_product`](views/cartesian_product.md) | <span class="rank rank-rare">知ってるだけ</span> | 全部の組み合わせ | <span class="ver ver-23">C++23</span> |
| [`views::adjacent`](views/adjacent.md) | <span class="rank rank-rare">知ってるだけ</span> | 隣り合う n 個の組 | <span class="ver ver-23">C++23</span> |
| [`views::adjacent_transform`](views/adjacent_transform.md) | <span class="rank rank-rare">知ってるだけ</span> | 隣り合う n 個に関数を適用 | <span class="ver ver-23">C++23</span> |
| [`views::zip_transform`](views/zip_transform.md) | <span class="rank rank-rare">知ってるだけ</span> | 同じ位置どうしに関数を適用 | <span class="ver ver-23">C++23</span> |
| [`views::join_with`](views/join_with.md) | <span class="rank rank-rare">知ってるだけ</span> | 区切りを挟んでつなげる | <span class="ver ver-23">C++23</span> |
| [`views::lazy_split`](views/lazy_split.md) | <span class="rank rank-rare">知ってるだけ</span> | 入力範囲にも使える分割 | <span class="ver ver-20">C++20</span> |
| [`views::repeat`](views/repeat.md) | <span class="rank rank-rare">知ってるだけ</span> | 同じ値の繰り返し | <span class="ver ver-23">C++23</span> |
| [`views::single`](views/single.md) | <span class="rank rank-rare">知ってるだけ</span> | 1 つの値だけの範囲 | <span class="ver ver-20">C++20</span> |
| [`views::empty`](views/empty.md) | <span class="rank rank-rare">知ってるだけ</span> | 空の範囲 | <span class="ver ver-20">C++20</span> |
| [`views::counted`](views/counted.md) | <span class="rank rank-rare">知ってるだけ</span> | 先頭と個数から範囲 | <span class="ver ver-20">C++20</span> |
| [`views::common`](views/common.md) | <span class="rank rank-rare">知ってるだけ</span> | begin と end の型をそろえる | <span class="ver ver-20">C++20</span> |
| [`views::all`](views/all.md) | <span class="rank rank-rare">知ってるだけ</span> | 範囲をビューにする | <span class="ver ver-20">C++20</span> |
| [`std::ranges::ref_view`](views/ref_view.md) | <span class="rank rank-rare">知ってるだけ</span> | 範囲への参照 | <span class="ver ver-20">C++20</span> |
| [`std::ranges::owning_view`](views/owning_view.md) | <span class="rank rank-rare">知ってるだけ</span> | 右辺値を所有 | <span class="ver ver-20">C++20</span> |
| [`views::elements`](views/elements.md) | <span class="rank rank-rare">知ってるだけ</span> | tuple の N 番目だけ | <span class="ver ver-20">C++20</span> |
| [`views::as_const`](views/as_const.md) | <span class="rank rank-rare">知ってるだけ</span> | 読み取り専用にして見る | <span class="ver ver-23">C++23</span> |
| [`views::as_rvalue`](views/as_rvalue.md) | <span class="rank rank-rare">知ってるだけ</span> | 右辺値として見る（ムーブ） | <span class="ver ver-23">C++23</span> |
| [`views::istream_view`](views/istream_view.md) | <span class="rank rank-rare">知ってるだけ</span> | ストリームから値を読む | <span class="ver ver-20">C++20</span> |

## よくある使い方

### 1. 絞り込んで、変換して、回す

```cpp
#include <print>
#include <ranges>
#include <string>
#include <vector>

struct Enemy {
  std::string name;
  int hp;
};

int main() {
  std::vector<Enemy> enemies = {{"スライム", 0}, {"ゴブリン", 25}, {"ドラゴン", 300}};

  // 生きている敵の名前だけ
  auto alive_names = enemies
                   | std::views::filter([](const Enemy& e) { return e.hp > 0; })
                   | std::views::transform(&Enemy::name);

  for (const auto& name : alive_names) {
    std::println("{}", name);
  }
}
```

```text title="実行結果"
ゴブリン
ドラゴン
```

### 2. 番号付きで回す

```cpp
#include <print>
#include <ranges>
#include <string>
#include <vector>

int main() {
  std::vector<std::string> ranking = {"Alice", "Bob", "Carol"};
  for (auto [i, name] : ranking | std::views::enumerate) {
    std::println("{}位 {}", i + 1, name);
  }
}
```

```text title="実行結果"
1位 Alice
2位 Bob
3位 Carol
```

### 3. 2 つの配列を同時に回す

```cpp
#include <print>
#include <ranges>
#include <string>
#include <vector>

int main() {
  std::vector<std::string> names = {"剣", "盾", "薬"};
  std::vector<int> prices = {300, 200, 50};
  for (auto [name, price] : std::views::zip(names, prices)) {
    std::println("{}: {} G", name, price);
  }
}
```

```text title="実行結果"
剣: 300 G
盾: 200 G
薬: 50 G
```

## フラグ・オプション

ビューは `|` でつなげて使います。左から順に適用されます。

```cpp
v | std::views::filter(f) | std::views::transform(g) | std::views::take(3)
// 「f で絞り込み → g で変換 → 先頭 3 個」
```

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    for (std::size_t i = 0; i < ranking.size(); ++i) {
      std::cout << i + 1 << "位 " << ranking[i] << "\n";
    }

    for (std::size_t i = 0; i < names.size() && i < prices.size(); ++i) {
      std::cout << names[i] << ": " << prices[i] << "\n";
    }
    ```

=== "今の書き方（C++23）"

    ```cpp
    for (auto [i, name] : ranking | std::views::enumerate) {
      std::println("{}位 {}", i + 1, name);
    }

    for (auto [name, price] : std::views::zip(names, prices)) {
      std::println("{}: {}", name, price);
    }
    ```

## ゲームでの使いどころ

「生きている敵だけ」「画面内にあるものだけ」といった絞り込み、そのあとの変換や取り出しを一時的な `vector` を作らずに書くときに使います。`enemies | views::filter(&Enemy::alive) | views::transform(&Enemy::position)` なら、生きている敵の位置だけがつながって見えます。

番号付きで回すなら `enumerate`、2 つの配列を同時に回すなら `zip` です。ランキングの上位だけを切り出すには `take`、先頭を飛ばすには `drop` を使います。

ビューは元のデータを参照しているので、元が消えたり再確保されたりすると壊れます。結果を保存して長く使うなら、最後に `std::ranges::to<std::vector>()` で実体のあるコンテナに変換します。毎フレーム作り直す処理では、保存せずビューのまま使うほうが軽くなります。

## パフォーマンス

- ビュー自体はほぼタダで作れます（コピーも確保も無し）。
- `filter` は「次に合う要素まで進む」処理が取り出すたびに走ります。同じビューを何度も回すなら、一度 `to<std::vector>()` で実体化したほうが速いこともあります。
- `transform` の関数は取り出すたびに呼ばれます。重い計算なら結果をキャッシュします。
- Debug ビルドではビューの階層がそのまま関数呼び出しになるので、普通のループよりかなり遅く見えることがあります。

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| 元のコンテナが消えた・再確保されたあとでビューを使う | 未定義動作 |
| `filter` の条件で要素を書き換える | 未定義動作になることがある |
| 一時的な vector からビューを作って変数に保存する | コンパイルエラーか未定義動作 |

## よくあるミス

??? failure "ビューを保存して、あとで元が変わる"
    ```cpp
    auto alive = enemies | std::views::filter(IsAlive);
    enemies.push_back(Enemy{});  // 再確保が起きるかもしれない
    for (auto& e : alive) {}     // 未定義動作の可能性
    ```

    ビューは作ったその場で使い切ります。

??? failure "ビューを vector だと思う"
    ビューに `push_back` や `[]`（filter の場合）はありません。vector が欲しいなら `| std::ranges::to<std::vector>()`。

??? failure "filter したビューの size() を呼ぶ"
    `filter` のビューは、全部見ないと個数が分からないので `size()` がありません。`std::ranges::distance(view)` で数えます（O(n)）。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::to`](ranges_to.md) | ビューを vector などの実体に変える |
| [`std::erase_if`](erase_if.md) | 本当に消す |
| [`std::ranges::copy`](copy.md) | 別のコンテナにコピーする |

## コンパイラ対応

| 機能 | MSVC | GCC | Clang (libc++) |
| --- | --- | --- | --- |
| `filter` / `transform` / `take` など <span class="ver ver-20">C++20</span> | ○ | ○ | ○ |
| `enumerate` <span class="ver ver-23">C++23</span> | ○ | 13〜 | 未対応（21 時点） |
| `zip` <span class="ver ver-23">C++23</span> | ○ | 13〜 | 17〜 |
| `adjacent` <span class="ver ver-23">C++23</span> | ○ | 13〜 | 未対応（21 時点） |
| `chunk` / `slide` / `stride` / `cartesian_product` <span class="ver ver-23">C++23</span> | ○ | 13〜 | 未対応（21 時点） |
| `repeat` <span class="ver ver-23">C++23</span> | ○ | 13〜 | 17〜 |
| ビューを `println` で出力 <span class="ver ver-23">C++23</span> | VS 2022 17.11〜 | 15〜 | 16〜 |

## これだけ覚える

!!! abstract "まとめ"
    - [x] `|` でつなげて「加工して見る」。元は変わらない
    - [x] `filter`・`transform`・`enumerate`・`zip`・`take` を覚える
    - [x] vector が欲しければ `| std::ranges::to<std::vector>()`
    - [x] ビューはその場で使い切る

## 関連ページ

- [cpprefjp: <ranges>](https://cpprefjp.github.io/reference/ranges.html)
- [cppreference: Ranges library](https://en.cppreference.com/w/cpp/ranges)
