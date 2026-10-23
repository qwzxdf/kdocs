---
title: std::ranges::replace
summary: "範囲の中の特定の値（または条件に合う要素）を、別の値に置き換える。"
order: 42
tags:
  - アルゴリズム
---

# std::ranges::replace

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

配列の中の特定の値を、別の値に置き換えたい。たとえば、無効を示す `-1` を `0` にする、特定の色を別の色にする。`for` と `if` で書くと数行になります。`std::ranges::replace` は、範囲の中のある値と等しい要素を、別の値に置き換えます。条件に合う要素を置き換える `replace_if` もあります。要素の数は変わりません。

!!! tip "ポイント"
    - 要素を**消す**のではなく、**書き換える**。消したいなら [`remove`](remove.md) や [`erase_if`](erase_if.md)。
    - 条件で置き換えるなら `replace_if`（`replace` は値が等しいものだけ）。
    - 元を残したまま、置き換えた結果を別の場所へ作るなら [`replace_copy`](replace_copy.md)。

!!! info "このページを読む前に"
    [ラムダ式](../../basics/lambda.md)、[イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::replace {#replace}

```cpp
template <input_range R, class T1, class T2, class Proj = identity>
constexpr borrowed_iterator_t<R> replace(R&& r, const T1& old_value, const T2& new_value,
                                         Proj proj = {});
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | 範囲 | 対象 |
| `old_value` | 値 | この値と等しい要素を |
| `new_value` | 値 | この値に置き換える |
| `proj` | プロジェクション | 比べる前の変換 |

<div class="anim" data-label="std::ranges::replace(v, 2, 9)">
2 1 2 3 # v
*2 1 *2 3 # 値が 2 のものを探す
+9 1 +9 3 # すべて 9 に置き換わる
</div>

### std::ranges::replace_if {#replace_if}

```cpp
template <input_range R, class T, class Proj = identity, class Pred>
constexpr borrowed_iterator_t<R> replace_if(R&& r, Pred pred, const T& new_value, Proj proj = {});
```

- `pred` が `true` の要素を `new_value` に置き換えます

<div class="anim" data-label="std::ranges::replace_if(v, is_even, 0)">
1 2 3 4 # v
1 *2 3 *4 # 条件に合うもの
1 +0 3 +0 # 0 に置き換わる
</div>

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, -1, 3, -1};
  std::ranges::replace(v, -1, 0);   // -1 を 0 に置き換える
  std::println("{}", v);
}
```

```text title="実行結果"
[1, 0, 3, 0]
```

## ゲームでの使いどころ

データのクリーニングに使います。読み込んだ数値の中の無効値 `-1` を `0` に直す、座標の NaN を 0 に直す、といった処理です。`replace_if` を使えば、`NaN` かどうかなど条件で置き換えられます。

要素を消すのではなく、書き換えます。消したいなら `erase_if` を使います。元を残したまま、置き換えた結果を別の場所に作りたいときは、`replace_copy` です。

文字列の特定の文字を置き換えるときにも使えます。ただし、部分文字列の置換は、`replace` ではなく `std::string::replace` や正規表現で行います。

## よくあるミス

??? failure "要素数が変わると思う"
    `replace` は要素を書き換えるだけで、個数は変わりません。

??? failure "要素を消すつもりで使う"
    `replace` は書き換えるだけで、要素数は変わりません。消すなら `erase_if` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::remove`](remove.md) | 条件に合う要素を詰めて消す |
| [`std::ranges::replace_copy`](replace_copy.md) | 置き換えた結果を別の場所へ |
| [`std::ranges::transform`](transform.md) | 全要素を関数で変換する |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 特定の値（または条件）を別の値に置き換える
    - [x] 個数は変わらない
    - [x] 別の場所に作るなら `replace_copy`

## 関連ページ

- [cpprefjp: std::ranges::replace](https://cpprefjp.github.io/reference/algorithm/ranges_replace.html)
- [cppreference: std::ranges::replace](https://en.cppreference.com/w/cpp/algorithm/ranges/replace)
