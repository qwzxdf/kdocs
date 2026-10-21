---
title: std::views::chunk
summary: "範囲を、n 個ずつの塊に区切って見る（重ならない）。"
order: 36
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::chunk

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-23">C++23</span>
`#include <ranges>`
</div>

`std::views::chunk(n)` は、**範囲を n 個ずつの塊に区切って、塊を範囲として並べる**ビューです。最後の塊は、余りの分だけ短くなります。タイルマップを 1 行ずつに分ける、パケットを一定のバイト数ずつ送る、といったときに使います。

!!! tip "ポイント"
    - 塊どうしは重ならない（重ねてずらすなら [`slide`](slide.md)）。
    - 最後の塊は n 個に満たないことがある。
    - `map` を幅で割って 2 次元として見るなら、`chunk(width)`。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)、[ラムダ式](../../../basics/lambda.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### views::chunk {#chunk}

```cpp
r | std::views::chunk(n)
std::views::chunk(r, n)
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `n` | 整数 | 1 つの塊の大きさ（1 以上） |

- 戻り値: 塊（部分範囲）を並べたビュー
- 計算量: O(1)（1 つ進めるたび）

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4, 5, 6, 7};

  auto rows = v | std::views::chunk(3) | std::ranges::to<std::vector<std::vector<int>>>();
  std::println("{}", rows);
}
```

```text title="実行結果"
[[1, 2, 3], [4, 5, 6], [7]]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 1 次元のタイルマップを、行ごとに分けて処理する | `tiles | chunk(width)` |
| パケットを 1024 バイトずつに分けて送る | `bytes | chunk(1024)` |

## よくあるミス

??? failure "n が 0"
    `chunk(0)` は未定義動作です。1 以上を渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::views::slide`](slide.md) | 重ねながらずらす |
| [`std::views::chunk_by`](chunk_by.md) | 条件で区切る |
| [`std::mdspan`](../../containers/mdspan.md) | 1 次元の配列を 2 次元として見る |

## コンパイラ対応

C++23 の機能です。GCC 13 / MSVC 19.34（VS 2022 17.4）以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] n 個ずつに区切る
    - [x] 最後は短くなることがある
    - [x] 重ならない

## 関連ページ

- [cpprefjp: std::ranges::chunk_view](https://cpprefjp.github.io/reference/ranges/chunk_view.html)
- [cppreference: std::ranges::chunk_view](https://en.cppreference.com/w/cpp/ranges/chunk_view)
