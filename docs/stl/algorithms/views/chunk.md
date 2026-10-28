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

タイルマップの 1 次元の配列を 1 行ずつに分けて処理したい。通信するデータを一定のバイト数ずつ送りたい。長い配列を一定の個数ごとに区切る処理は、添え字の計算で書くと、端の扱いを間違えやすくなります。`std::views::chunk(n)` は、範囲を n 個ずつの塊に区切り、塊を範囲として並べるビューです。最後の塊は、余りの分だけ短くなります。

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

### std::ranges::chunk_view <span class="ver ver-23">C++23</span> {#chunk_view data-toc-label="std::ranges::chunk_view"}

```cpp
template <view V>
class chunk_view;
```

- 戻り値: `begin()` / `end()` をもつ view の型
- 計算量: begin / end は定数。要素の取り出しは元の範囲と同じ

n 個ずつの塊に区切って見せる view。`views::chunk(n)` が作ります。

ふつうは `views::chunk` を使って書くので、この型の名前を自分で書くことは少なく、`auto` で受けます。型名が必要なとき（関数の戻り値の型を明示したいときなど）や、CTAD（クラステンプレートの引数推論）で `std::ranges::chunk_view v(r, ...)` と直接作るときにだけ登場します。

## ゲームでの使いどころ

2 次元のタイルマップを 1 次元の `vector` で持っているときに使います。`map | std::views::chunk(width)` と書くと、1 行ずつの範囲になり、`for (auto row : ...)` で行ごとに処理できます。

パケットの分割にも向いています。送信するバイト列を 1400 バイトずつに区切って、順に送ります。ページ送りのリストを 1 ページ分ずつに分ける用途にも使えます。

重ならないのが特徴です。1 つずつずらして重ねたいなら `slide` を使います。

## よくあるミス

??? failure "n が 0"
    `chunk(0)` は未定義動作です。1 以上を渡します。

??? failure "最後の塊が短いことを忘れる"
    要素数が n の倍数でないと、最後の塊は短くなります。固定の長さを仮定して添え字でアクセスすると、範囲外になります。`size()` を確かめます。

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
