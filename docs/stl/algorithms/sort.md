---
title: std::ranges::sort
summary: "要素を小さい順（または指定の順）に並べ替える。比較の関数も渡せる。"
order: 20
tags:
  - アルゴリズム
---

# std::ranges::sort

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

ランキングをスコアの高い順に表示する、敵を距離の近い順に狙う、スプライトを奥から手前の順に描く。ゲームでは「並べ替え」が頻繁に出てきます。昔の `std::sort(v.begin(), v.end())` は、先頭と末尾を毎回書く必要がありました。C++20 の `std::ranges::sort` は、`vector` をそのまま渡せて、さらに「どのメンバで並べるか」を指定できるので、短く書けます。

!!! tip "ポイント"
    - <strong>並べ替えはこれ。</strong> `std::ranges::sort(v);` で小さい順。
    - 大きい順は `std::ranges::sort(v, std::greater{});`。
    - 構造体をメンバで並べるなら `std::ranges::sort(enemies, {}, &Enemy::hp);`（プロジェクション）。
    - 同じ値どうしの順番は**保たれない**。保ちたいなら [`std::ranges::stable_sort`](stable_sort.md)。
    - O(n log n) なので、毎フレーム数千個並べると重い。

!!! info "このページを読む前に"
    [ラムダ式](../../basics/lambda.md)、[ranges とビュー](../../basics/ranges.md) が分かると読みやすいです。

## 宣言

```cpp
namespace std::ranges {
template <random_access_range R, class Comp = ranges::less,
          class Proj = identity>
constexpr borrowed_iterator_t<R> sort(R&& r, Comp comp = {}, Proj proj = {});

template <random_access_iterator I, sentinel_for<I> S, class Comp = ranges::less,
          class Proj = identity>
constexpr I sort(I first, S last, Comp comp = {}, Proj proj = {});
}
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `r` | ランダムアクセスできる範囲 | 並べ替える範囲（vector, array, deque, C 配列, string など） | 省略不可 |
| `first`, `last` | イテレータ | 範囲の始まりと終わり（一部だけ並べたいとき） | |
| `comp` | 比較関数 | 「a を b より前に置くなら true」を返す関数 | `ranges::less`（小さい順） |
| `proj` | プロジェクション | 比べる前に要素を何に変換するか（メンバポインタやラムダ） | `identity`（そのまま） |

- 戻り値: 範囲の終わりのイテレータ（ほぼ使わない）
- 計算量: O(n log n)
- `std::list` は渡せない（ランダムアクセスできないため。`list::sort` を使う）

## よくある使い方

### 1. 小さい順・大きい順

```cpp
#include <algorithm>
#include <functional>
#include <print>
#include <vector>

int main() {
  std::vector<int> scores = {70, 100, 40, 85};

  std::ranges::sort(scores);
  std::println("{}", scores);

  std::ranges::sort(scores, std::greater{});
  std::println("{}", scores);
}
```

```text title="実行結果"
[40, 70, 85, 100]
[100, 85, 70, 40]
```

### 2. 構造体をメンバで並べる（プロジェクション）

```cpp
#include <algorithm>
#include <functional>
#include <print>
#include <string>
#include <vector>

struct Enemy {
  std::string name;
  int hp;
  float distance;
};

int main() {
  std::vector<Enemy> enemies = {
      {"スライム", 10, 5.0f}, {"ドラゴン", 300, 20.0f}, {"ゴブリン", 25, 2.5f}};

  // 距離の近い順（第 2 引数 {} は「比較はデフォルトのまま」という意味）
  std::ranges::sort(enemies, {}, &Enemy::distance);
  for (const auto& e : enemies) {
    std::println("{} {}", e.name, e.distance);
  }

  // HP の多い順
  std::ranges::sort(enemies, std::greater{}, &Enemy::hp);
  std::println("一番強い: {}", enemies.front().name);
}
```

```text title="実行結果"
ゴブリン 2.5
スライム 5
ドラゴン 20
一番強い: ドラゴン
```

### 3. 複数の条件で並べる

「レベルの高い順、同じなら名前順」のように、条件が複数あるときはラムダ式で書きます。`std::tie` を使うと短く書けます。

```cpp
#include <algorithm>
#include <print>
#include <string>
#include <tuple>
#include <vector>

struct Player {
  std::string name;
  int level;
};

int main() {
  std::vector<Player> players = {{"Carol", 5}, {"Alice", 9}, {"Bob", 5}};

  std::ranges::sort(players, [](const Player& a, const Player& b) {
    // レベルは大きい順にしたいので、b と a を逆に書く
    return std::tie(b.level, a.name) < std::tie(a.level, b.name);
  });

  for (const auto& p : players) {
    std::println("{} Lv.{}", p.name, p.level);
  }
}
```

```text title="実行結果"
Alice Lv.9
Bob Lv.5
Carol Lv.5
```

### 4. 描画順（Z ソート）

2D ゲームで、奥のものから先に描くために y 座標や z 値で並べる定番の使い方です。

```cpp
std::ranges::sort(sprites, {}, &Sprite::z);
for (const auto& sprite : sprites) {
  Draw(sprite);
}
```

## フラグ・オプション

`comp`（比較関数）に渡すものです。

| 値 | 重要度 | 並び順 | 使う場面 |
| --- | --- | --- | --- |
| 省略（`std::ranges::less`） | <span class="rank rank-must">必須</span> | 小さい順 | 普通はこれ |
| `std::greater{}` | <span class="rank rank-must">必須</span> | 大きい順 | スコアの高い順など |
| `{}` | <span class="rank rank-often">よく使う</span> | 小さい順（明示的にデフォルト） | プロジェクションだけ指定したいとき |
| ラムダ式 | <span class="rank rank-often">よく使う</span> | 自由 | 条件が複数ある |
| `std::ranges::greater{}` | <span class="rank rank-rare">知ってるだけ</span> | 大きい順 | `std::greater{}` とほぼ同じ |

`proj`（プロジェクション）に渡すものです。

| 値 | 重要度 | 意味 |
| --- | --- | --- |
| `&Type::member` | <span class="rank rank-must">必須</span> | メンバ変数で比べる |
| `&Type::Function` | <span class="rank rank-sometimes">たまに</span> | メンバ関数の戻り値で比べる（引数なしの関数） |
| ラムダ式 | <span class="rank rank-sometimes">たまに</span> | 計算した値で比べる（例: `[](const V& v) { return v.x * v.x + v.y * v.y; }`） |

!!! warning "比較関数のルール"
    比較関数は「**a を b より前に置くべきなら true**」を返します。`<=` のように「等しいときも true」を返すと、ルール違反で**未定義動作**（落ちることもある）になります。必ず `<` か `>` で書きます。

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    std::sort(v.begin(), v.end());
    std::sort(v.begin(), v.end(), std::greater<int>());
    std::sort(enemies.begin(), enemies.end(),
              [](const Enemy& a, const Enemy& b) { return a.hp < b.hp; });
    ```

=== "今の書き方（C++20）"

    ```cpp
    std::ranges::sort(v);
    std::ranges::sort(v, std::greater{});
    std::ranges::sort(enemies, {}, &Enemy::hp);
    ```

## ゲームでの使いどころ

描画順の整理は、並べ替えが最もよく使われる場面です。2D のスプライトは、画面の奥にあるものから先に描かないと、前後関係が壊れます。Z の値や y 座標で `sort` してから描画します。半透明のオブジェクトは、カメラから遠い順に描く必要があるので、毎フレーム距離でソートします。

ランキング表示では、スコアの高い順に `sort` して、上位 10 件を切り出します。全部を並べ替えるより、上位だけが欲しい場合は、`partial_sort` のほうが速くなります。

ターゲット選択では、敵を距離の近い順に並べて、先頭を狙います。1 体だけ欲しいなら `min_element` で足ります。ターン制バトルの行動順（素早さ順）にも `sort` を使います。同じ素早さの順番を固定したいなら `stable_sort` です。

## パフォーマンス

- 計算量は O(n log n)。1000 個なら 1 万回くらいの比較で、数十マイクロ秒程度です。
- 要素が大きい構造体だと、並べ替えのたびにムーブが起きます。重いなら「添字の配列」や「ポインタの配列」を並べる方法があります。
- **ほとんど並んでいる**データ（毎フレーム少しだけ動く描画順など）なら、挿入ソートのほうが速いこともあります。
- 上位 N 件だけ欲しいなら [`std::ranges::partial_sort`](partial_sort.md) のほうが速いです。

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| 比較関数が `<=` など「等しいときも true」 | 未定義動作（範囲外アクセスで落ちることがある） |
| 比較関数の結果が呼ぶたびに変わる（乱数など） | 未定義動作 |
| float の NaN を含む範囲を `<` で並べる | 未定義動作（NaN はどれとも比較が false） |

## よくあるミス

??? failure "比較関数に <= を使う"
    ```cpp
    // NG: 等しいときに true を返す
    std::ranges::sort(v, [](int a, int b) { return a <= b; });

    // OK
    std::ranges::sort(v, [](int a, int b) { return a < b; });
    ```

??? failure "同じ値の順番が保たれると思い込む"
    `sort` は同じ値どうしの順番を保証しません。「同じスコアなら先に達成した人が上」にしたいなら `stable_sort` を使うか、達成時刻も比較条件に入れます。

??? failure "大きい順のつもりで greater を第 3 引数に書く"
    ```cpp
    std::ranges::sort(enemies, &Enemy::hp, std::greater{});  // コンパイルエラー

    std::ranges::sort(enemies, std::greater{}, &Enemy::hp);  // OK: 比較 → プロジェクションの順
    ```

## 類似

| 名前 | 違い | こっちを使うとき |
| --- | --- | --- |
| [`std::ranges::stable_sort`](stable_sort.md) | 同じ値の順番を保つ | 同点の順番が大事 |
| [`std::ranges::partial_sort`](partial_sort.md) | 先頭 N 個だけ並べる | 上位 N 件だけ欲しい |
| [`std::ranges::nth_element`](partial_sort.md) | N 番目だけ正しい位置に | 中央値、N 番目の値 |
| [`std::map`](../containers/map.md) / [`std::set`](../containers/set.md) | 常に並んだ状態を保つ | 追加・削除しながらずっと並べておきたい |
| `std::ranges::is_sorted` | 並んでいるか調べる | デバッグ |

## コンパイラ対応

`std::ranges::sort`（C++20）は主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::ranges::sort(v)` で小さい順、`std::greater{}` で大きい順
    - [x] メンバで並べるなら `std::ranges::sort(v, {}, &T::member)`
    - [x] 比較関数は `<` か `>`。`<=` はダメ
    - [x] 同点の順番を保つなら `stable_sort`

## 関連ページ

- [cpprefjp: std::ranges::sort](https://cpprefjp.github.io/reference/algorithm/ranges_sort.html)
- [cppreference: std::ranges::sort](https://en.cppreference.com/w/cpp/algorithm/ranges/sort)
