---
title: std::ranges::equal
summary: "2 つの範囲の中身が、全部同じかを調べる。型が違う範囲どうしでも比べられる。"
order: 41
tags:
  - アルゴリズム
---

# std::ranges::equal

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::equal` は、**2 つの範囲の中身が全部同じか**を調べるアルゴリズムです。vector どうしなら `==` で比べられますが、vector と配列、list と vector のように**型の違う範囲どうし**でも比べられるのが利点です。

!!! tip "ポイント"
    - 同じコンテナ同士なら `a == b` で十分。型が違う範囲どうしなら `std::ranges::equal(a, b)`。
    - **長さが違えば、中身を見ずに `false`** になる（ranges 版）。
    - どこが違うか知りたいなら [`std::ranges::mismatch`](mismatch.md)。

## 関数の詳しい説明

### std::ranges::equal {#equal}

```cpp
template <input_range R1, input_range R2, class Pred = ranges::equal_to,
          class Proj1 = identity, class Proj2 = identity>
constexpr bool equal(R1&& r1, R2&& r2, Pred pred = {}, Proj1 proj1 = {}, Proj2 proj2 = {});
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `r1`, `r2` | 範囲 | 比べる 2 つ（型が違ってもいい） | 省略不可 |
| `pred` | 関数 | 「等しい」の判定 | `==` |
| `proj1`, `proj2` | プロジェクション | それぞれの比べる前の変換 | そのまま |

- 戻り値: 長さが同じで、全部の要素が等しければ `true`

<div class="anim" data-label="std::ranges::equal(a, b)">
1 2 3 | 1 2 3 # a と b
*1 2 3 | *1 2 3 # 先頭から順に比べる
*1 *2 3 | *1 *2 3 # 同じ
*1 *2 *3 | *1 *2 *3 # すべて同じなら true
</div>


## よくある使い方

### 隠しコマンドの判定

```cpp
#include <algorithm>
#include <array>
#include <print>
#include <vector>

enum class Key { kUp, kDown, kLeft, kRight, kA, kB };

int main() {
  // 隠しコマンドの正解（配列）と、入力された履歴（vector）
  constexpr std::array kSecret = {Key::kUp, Key::kUp, Key::kDown, Key::kDown, Key::kA};
  std::vector<Key> input = {Key::kUp, Key::kUp, Key::kDown, Key::kDown, Key::kA};

  // 型が違っても比べられる
  std::println("成功？ {}", std::ranges::equal(input, kSecret));
}
```

```text title="実行結果"
成功？ true
```

### 比べ方を変える（大文字小文字を無視）

```cpp
#include <algorithm>
#include <cctype>
#include <print>
#include <string>

int main() {
  std::string a = "Title";
  std::string b = "TITLE";

  // pred に「等しい」の定義を渡す
  bool same = std::ranges::equal(a, b, [](char x, char y) {
    return std::tolower(static_cast<unsigned char>(x)) == std::tolower(static_cast<unsigned char>(y));
  });
  std::println("{}", same);
}
```

```text title="実行結果"
true
```

## フラグ・オプション

| 引数 | 重要度 | 渡すもの | 意味 |
| --- | --- | --- | --- |
| `pred` | <span class="rank rank-sometimes">たまに</span> | ラムダ式 | 「等しい」の判定を変える（既定は `==`） |
| `proj1` / `proj2` | <span class="rank rank-rare">知ってるだけ</span> | `&Type::member` | 比べる前に、メンバを取り出す |

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    // b が短いと範囲外を読む
    bool same = std::equal(a.begin(), a.end(), b.begin());
    ```

=== "今の書き方（C++20）"

    ```cpp
    // 長さも比べるので安全
    bool same = std::ranges::equal(a, b);
    ```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| コマンド入力・パスワードの照合 | `equal(input, secret)` |
| パズルの完成判定 | `equal(board, goal)` |
| セーブデータの比較（変更があるか） | `equal(current, saved)` |

## よくあるミス

??? failure "長さの違う範囲を古い std::equal で比べる"
    古い `std::equal(a.begin(), a.end(), b.begin())` は、b が短いと範囲外を読みます。ranges 版は長さも比べるので安全です。

??? failure "浮動小数点数を equal で比べる"
    `float` の `==` は誤差で一致しないことがあります。誤差を許したいなら、`pred` に「差が小さいか」を渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::mismatch`](mismatch.md) | 最初に違う位置を返す |
| [`std::ranges::lexicographical_compare`](lexicographical_compare.md) | 辞書順で大小を比べる |
| `a == b`（コンテナ） | 同じ型のコンテナどうしなら、これで十分 |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 型の違う範囲どうしの比較は `std::ranges::equal`
    - [x] 長さが違えば `false`
    - [x] 比べ方は `pred` で変えられる

## 関連ページ

- [cpprefjp: std::ranges::equal](https://cpprefjp.github.io/reference/algorithm/ranges_equal.html)
- [cppreference: std::ranges::equal](https://en.cppreference.com/w/cpp/algorithm/ranges/equal)
