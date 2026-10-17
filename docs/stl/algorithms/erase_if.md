---
title: std::erase_if / std::erase
tags:
  - アルゴリズム
---

# std::erase_if / std::erase

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-20">C++20</span>
各コンテナのヘッダ（`<vector>`, `<string>`, `<unordered_map>` など）
</div>

`std::erase_if` は、**コンテナから条件に合う要素をまとめて消す**関数です。`std::erase` は「この値と等しいもの」をまとめて消します。C++20 で入った関数で、それまで定番だった「remove-erase イディオム」を 1 行で書けるようになりました。vector だけでなく、ほぼすべての標準コンテナで同じ書き方ができます。

!!! tip "ポイント"
    - <strong>コンテナから要素を消すときの第一候補。</strong> `std::erase_if(v, 条件);` の 1 行で済む。
    - ループの中で 1 個ずつ `erase` するより、安全で速い。
    - メンバ関数ではなく `std::` の関数（`v.erase_if(...)` ではない）。
    - 戻り値は消した数。

!!! info "このページを読む前に"
    [ラムダ式](../../basics/lambda.md) を使って条件を書きます。

## 関数一覧

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`std::erase_if`](#erase_if) | <span class="rank rank-must">必須</span> | 条件に合う要素をすべて消す | O(n) |
| [`std::erase`](#erase) | <span class="rank rank-sometimes">たまに</span> | 値と等しい要素をすべて消す | O(n) |

### 使えるコンテナ

| コンテナ | `erase_if` | `erase` |
| --- | --- | --- |
| [`vector`](../containers/vector.md), [`deque`](../containers/deque.md), [`string`](../containers/string.md) | ○ | ○ |
| [`list`](../containers/list.md), [`forward_list`](../containers/forward_list.md) | ○ | ○ |
| [`map`](../containers/map.md), [`set`](../containers/set.md), [`unordered_map`](../containers/unordered_map.md), [`unordered_set`](../containers/unordered_set.md)（multi 版も） | ○ | ×（キーで消すならメンバの `erase(key)`） |
| [`flat_map`](../containers/flat_map.md), [`flat_set`](../containers/flat_set.md) | ○ | × |
| [`array`](../containers/array.md), [`span`](../containers/span.md) | ×（要素数を変えられない） | × |

## よくある使い方

### 1. 死んだ敵を消す

```cpp
#include <print>
#include <string>
#include <vector>

struct Enemy {
  std::string name;
  int hp;
};

int main() {
  std::vector<Enemy> enemies = {
      {"スライム", 0}, {"ゴブリン", 25}, {"コウモリ", -3}, {"ドラゴン", 300}};

  std::size_t removed =
      std::erase_if(enemies, [](const Enemy& e) { return e.hp <= 0; });

  std::println("{} 体消えた", removed);
  for (const auto& e : enemies) {
    std::println("{}", e.name);
  }
}
```

```text title="実行結果"
2 体消えた
ゴブリン
ドラゴン
```

### 2. map から条件で消す

map 系では、ラムダに `pair<const Key, T>` が渡されます。

```cpp
#include <map>
#include <print>
#include <string>

int main() {
  std::map<std::string, int> buffs = {{"攻撃UP", 3}, {"防御UP", 0}, {"速度UP", 0}};

  // 残りターンが 0 のバフを消す
  std::erase_if(buffs, [](const auto& pair) { return pair.second == 0; });
  std::println("{}", buffs);
}
```

```text title="実行結果"
{"攻撃UP": 3}
```

### 3. 文字列から特定の文字を消す

```cpp
#include <print>
#include <string>

int main() {
  std::string phone = "090-1234-5678";
  std::erase(phone, '-');
  std::println("{}", phone);
}
```

```text title="実行結果"
09012345678
```

## 関数の詳しい説明

### std::erase_if {#erase_if}

```cpp
template <class T, class Alloc, class Pred>
typename std::vector<T, Alloc>::size_type erase_if(std::vector<T, Alloc>& c, Pred pred);
// deque, string, list, map, set などにも同じ形のものがある
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `c` | コンテナの参照 | 対象のコンテナ |
| `pred` | 関数・ラムダ | 要素を 1 つ受け取り、**消すなら `true`** を返す |

- 戻り値: 消した要素の数
- 計算量: O(n)（全要素を 1 回ずつ見る）
- vector / deque / string は、残った要素の順番が保たれる

<div class="mem">
<div class="mem-step"><span class="mem-label">前</span><span class="mem-cells"><span>A</span><span class="gone">×</span><span>C</span><span class="gone">×</span><span>E</span></span><span class="mem-note">× が条件に合う要素</span></div>
<div class="mem-step"><span class="mem-label">後</span><span class="mem-cells"><span>A</span><span class="move">C</span><span class="move">E</span></span><span class="mem-note">残すものを前に詰めて、余った後ろを切る</span></div>
</div>

!!! note "実際は"
    1 フレームに 1 回、リスト全体を掃除する使い方がちょうどいいです。毎フレーム何十回も呼ぶような書き方になっていたら、「死んだフラグを立てておいて最後に 1 回だけ erase_if」にまとめます。

<div class="anim" data-label="std::erase_if(v, is_even)">
1 2 3 4 5 # v
1 x2 3 x4 5 # 条件に合うものを消す
1 >3 >5 _ _ # 残るものを前に詰める
1 3 5 # size が縮む。1 回のパスで終わる
</div>

### std::erase {#erase}

```cpp
template <class T, class Alloc, class U = T>
typename std::vector<T, Alloc>::size_type erase(std::vector<T, Alloc>& c, const U& value);
// deque, string, list, forward_list にも同じ形のものがある
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `c` | コンテナの参照 | 対象のコンテナ |
| `value` | `const U&` | この値と `==` で等しい要素を消す |

- 戻り値: 消した要素の数
- 計算量: O(n)

```cpp
#include <print>
#include <vector>

int main() {
  std::vector<int> slots = {3, 0, 7, 0, 0, 1};
  std::size_t n = std::erase(slots, 0);
  std::println("{} 個消した: {}", n, slots);
}
```

```text title="実行結果"
3 個消した: [3, 7, 1]
```

!!! note "実際は"
    メンバ関数の `v.erase(位置)` とは別物です。名前が似ているので混同しないようにします。

## フラグ・オプション

フラグはありません。

## 古い書き方と今の書き方

=== "古い書き方（remove-erase イディオム）"

    ```cpp
    enemies.erase(
        std::remove_if(enemies.begin(), enemies.end(),
                       [](const Enemy& e) { return e.hp <= 0; }),
        enemies.end());

    // map は手書きのループ
    for (auto it = m.begin(); it != m.end();) {
      if (it->second == 0) {
        it = m.erase(it);
      } else {
        ++it;
      }
    }
    ```

=== "今の書き方（C++20）"

    ```cpp
    std::erase_if(enemies, [](const Enemy& e) { return e.hp <= 0; });

    std::erase_if(m, [](const auto& p) { return p.second == 0; });
    ```

!!! note "remove_if だけでは消えない"
    古い `std::remove_if` は「残すものを前に詰める」だけで、**要素数は変わりません**。後ろに残ったゴミを `erase` で切り落として、初めて消えます。`std::erase_if` はこの 2 つを 1 回でやってくれます。

## ゲームでの使いどころ

| 場面 | 条件 |
| --- | --- |
| 敵・弾・パーティクルの掃除 | HP が 0、画面外、寿命切れ |
| バフ・デバフの期限切れ | 残りターン・残り時間が 0 |
| UI の通知 | 表示時間が過ぎた |
| 当たり判定の候補 | 無効化されたコライダー |

## パフォーマンス

- vector に対しては、「残す要素を前に詰める」だけなので、全体を 1 回なめる O(n) で済みます。ループ中に 1 個ずつ `erase` すると、消すたびに後ろをずらすので O(n²) になります。
- 順番が要らない vector なら、「swap して pop_back」（[vector 参照](../containers/vector.md#順番がどうでもいいならswap-して-pop_back)）のほうがムーブの回数が少なくなることもあります。

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| 条件の関数の中で、同じコンテナに追加・削除する | 未定義動作 |

## よくあるミス

??? failure "メンバ関数だと思って書く"
    ```cpp
    enemies.erase_if([](const Enemy& e) { return e.hp <= 0; });  // コンパイルエラー
    std::erase_if(enemies, [](const Enemy& e) { return e.hp <= 0; });  // OK
    ```

??? failure "条件を逆に書く"
    `pred` は「**消すもの**」で `true` を返します。「残すもの」で `true` を返すと、残したいものが全部消えます。

??? failure "remove_if だけで消えたと思う"
    ```cpp
    std::remove_if(v.begin(), v.end(), pred);  // v.size() は変わっていない
    ```

## 類似

| 名前 | 違い | こっちを使うとき |
| --- | --- | --- |
| メンバの `erase(位置)` | 位置を指定して 1 個（または範囲）消す | 何番目を消すか決まっている |
| メンバの `erase(key)`（map / set） | キーを指定して消す | キーが分かっている |
| `std::ranges::remove_if` | 前に詰めるだけで消さない | array など要素数を変えられないもの |
| `std::views::filter` | 元を変えずに、条件に合うものだけを「見る」 | 消さずに一部だけ処理したい |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 条件で消すなら `std::erase_if(c, 条件)`
    - [x] 値で消すなら `std::erase(c, 値)`
    - [x] 条件は「消すもの」で true
    - [x] ループの中で 1 個ずつ erase しない

## 関連ページ

- [cpprefjp: std::erase_if (vector)](https://cpprefjp.github.io/reference/vector/erase_if_free.html)
- [cppreference: std::erase, std::erase_if (std::vector)](https://en.cppreference.com/w/cpp/container/vector/erase2)
