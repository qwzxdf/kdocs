---
title: std::views::take
summary: "先頭から n 個だけが見える範囲を作る。"
order: 3
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::take

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

`std::views::take` は、**先頭から n 個だけが見える範囲**を作るビューです。ランキングの上位 10 件、ログの最新 5 件などに使います。元が n 個より短いなら、全部が見えます。

!!! tip "ポイント"
    - 無限に続く範囲（`views::iota(0)`）に使うと、有限にできる。
    - n 個目より後ろは、評価もされない。
    - 先頭を飛ばすなら [`drop`](drop.md)。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)、[ラムダ式](../../../basics/lambda.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### views::take {#take}

```cpp
v | std::views::take(n)
std::views::take(v, n)
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `n` | 整数 | 見せたい個数（元より多ければ全部） |

- 戻り値: 先頭 n 個のビュー
- 計算量: O(1) で作成。進めるたびに O(1)

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> ranking = {100, 90, 80, 70, 60};

  auto top3 = ranking | std::views::take(3) | std::ranges::to<std::vector>();
  std::println("{}", top3);
}
```

```text title="実行結果"
[100, 90, 80]
```

### std::ranges::take_view <span class="ver ver-20">C++20</span> {#take_view data-toc-label="std::ranges::take_view"}

```cpp
template <view V>
class take_view;
```

- 戻り値: `begin()` / `end()` をもつ view の型
- 計算量: begin / end は定数。要素の取り出しは元の範囲と同じ

先頭から n 個だけを見せる view。`views::take(n)` が作ります。

ふつうは `views::take` を使って書くので、この型の名前を自分で書くことは少なく、`auto` で受けます。型名が必要なとき（関数の戻り値の型を明示したいときなど）や、CTAD（クラステンプレートの引数推論）で `std::ranges::take_view v(r, ...)` と直接作るときにだけ登場します。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ランキング上位 N 件を表示する | `ranking | take(10)` |
| 無限の連番から有限の範囲を切り出す | `iota(0) | take(5)` |

## よくあるミス

??? failure "n が負"
    負の個数は未定義動作です。`std::size_t` や、0 以上を保証した値を渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::views::drop`](drop.md) | 先頭 n 個を飛ばす |
| [`std::views::take_while`](take_while.md) | 条件が続く間だけ |
| [`std::ranges::copy_n`](../copy.md) | 先頭 n 個を別の場所へコピーする |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 先頭 n 個だけを見る
    - [x] 無限の範囲を有限にできる
    - [x] 短ければ全部が見える

## 関連ページ

- [cpprefjp: std::ranges::take_view](https://cpprefjp.github.io/reference/ranges/take_view.html)
- [cppreference: std::ranges::take_view](https://en.cppreference.com/w/cpp/ranges/take_view)
