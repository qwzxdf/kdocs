---
title: std::views::keys
summary: "map などから、キーだけが見える範囲を作る。"
order: 13
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::keys

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

`std::views::keys` は、**`map` のような「(キー, 値) の組」の範囲から、キーだけが見える範囲**を作るビューです。`elements<0>` の別名です。

!!! tip "ポイント"
    - `map` の一覧表示、キーだけの集合の作成に使う。
    - 値だけなら [`values`](values.md)。
    - `| std::ranges::to<std::vector>()` でキーの `vector` が作れる。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)、[ラムダ式](../../../basics/lambda.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### views::keys {#keys}

```cpp
m | std::views::keys
std::views::keys(m)
```

- 戻り値: キーだけのビュー
- 計算量: O(1)

```cpp
#include <map>
#include <print>
#include <ranges>
#include <string>
#include <vector>

int main() {
  std::map<std::string, int> items = {{"gold", 100}, {"potion", 3}};

  auto names = items | std::views::keys | std::ranges::to<std::vector>();
  std::println("{}", names);
}
```

```text title="実行結果"
["gold", "potion"]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 所持アイテムの名前だけを一覧表示する | `inventory | keys` |
| 設定の項目名の一覧 | `config | keys` |

## よくあるミス

??? failure "unordered_map の順序を期待する"
    `unordered_map` のキーの順序は不定です。整列した一覧が欲しいなら `std::map` か、取り出したあとに `sort` します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::views::values`](values.md) | 値だけを見る |
| [`std::views::elements`](elements.md) | 任意の番号を取る |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `map` のキーだけを見る
    - [x] `elements<0>` の別名
    - [x] キーの `vector` は `to<vector>` で

## 関連ページ

- [cpprefjp: std::ranges::keys_view](https://cpprefjp.github.io/reference/ranges/keys_view.html)
- [cppreference: std::ranges::keys_view](https://en.cppreference.com/w/cpp/ranges/keys_view)
