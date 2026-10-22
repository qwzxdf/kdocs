---
title: std::views::stride
summary: "n 個おきに要素を取って見る。"
order: 38
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::stride

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-23">C++23</span>
`#include <ranges>`
</div>

`std::views::stride(n)` は、**n 個おきに（n 番目ごとに）要素を取って並べる**ビューです。`stride(3)` なら、0 番目、3 番目、6 番目…。間引き表示、1 つおきの処理、画像の縮小（間引き）に使います。

!!! tip "ポイント"
    - 先頭の要素は必ず含まれる。
    - n が 1 なら、全部の要素。
    - n は 1 以上の整数。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)、[ラムダ式](../../../basics/lambda.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### views::stride {#stride}

```cpp
r | std::views::stride(n)
std::views::stride(r, n)
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `n` | 整数 | 何個おきに取るか（1 以上） |

- 戻り値: n 個おきの要素を並べたビュー
- 計算量: ランダムアクセスできる範囲なら O(1)

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

  auto every3 = v | std::views::stride(3) | std::ranges::to<std::vector>();
  std::println("{}", every3);
}
```

```text title="実行結果"
[1, 4, 7, 10]
```

### std::ranges::stride_view <span class="ver ver-23">C++23</span> {#stride_view data-toc-label="std::ranges::stride_view"}

```cpp
template <input_range V>
class stride_view;
```

- 戻り値: `begin()` / `end()` をもつ view の型
- 計算量: begin / end は定数。要素の取り出しは元の範囲と同じ

n 個おきに要素を見せる view。`views::stride(n)` が作ります。

ふつうは `views::stride` を使って書くので、この型の名前を自分で書くことは少なく、`auto` で受けます。型名が必要なとき（関数の戻り値の型を明示したいときなど）や、CTAD（クラステンプレートの引数推論）で `std::ranges::stride_view v(r, ...)` と直接作るときにだけ登場します。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ログ表示を間引く（10 件に 1 件） | `logs | stride(10)` |
| 画像を縦横 1/2 に間引いて縮小する | `rows | stride(2)` と `cols | stride(2)` |

## よくあるミス

??? failure "n が 0"
    `stride(0)` は未定義動作です。1 以上を渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::views::chunk`](chunk.md) | n 個ずつの塊に区切る |
| [`std::views::take`](take.md) | 先頭 n 個 |

## コンパイラ対応

C++23 の機能です。GCC 13 / MSVC 19.34（VS 2022 17.4）以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] n 個おきに取る
    - [x] 先頭は含まれる
    - [x] n は 1 以上

## 関連ページ

- [cpprefjp: std::ranges::stride_view](https://cpprefjp.github.io/reference/ranges/stride_view.html)
- [cppreference: std::ranges::stride_view](https://en.cppreference.com/w/cpp/ranges/stride_view)
