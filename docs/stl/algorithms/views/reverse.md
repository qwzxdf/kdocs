---
title: std::views::reverse
summary: "逆順に並んで見える範囲を作る（コピーも書き換えもしない）。"
order: 7
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::reverse

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

最新のログを新しい順に表示したい、リストを後ろから探したい。`vector` を後ろから回す `for` を書くと、`size_t` の符号なしの減算で、`i >= 0` が常に真になる無限ループというバグを生みやすくなります。`std::views::reverse` は、要素が逆順に並んで見える範囲を作るビューです。元の `vector` は変わらず、コピーも作られません。

!!! tip "ポイント"
    - 元が**双方向**にたどれる範囲（vector、list、deque など）である必要がある。
    - 並びそのものを書き換えるなら [`ranges::reverse`](../reverse.md)。
    - `reverse | take(3)` で「最後の 3 個」を取れる。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)と、[ラムダ式](../../../basics/lambda.md)が分かると読みやすいです。

## 関数の詳しい説明

### views::reverse {#reverse}

```cpp
v | std::views::reverse
std::views::reverse(v)
```

- 戻り値: 逆順のビュー
- 計算量: O(1)

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> history = {1, 2, 3};

  auto newest_first = history | std::views::reverse | std::ranges::to<std::vector>();
  std::println("{}", newest_first);

  // 最後の 2 個だけ
  auto last2 = history | std::views::reverse | std::views::take(2) | std::ranges::to<std::vector>();
  std::println("{}", last2);
}
```

```text title="実行結果"
[3, 2, 1]
[2, 1]
```

### std::ranges::reverse_view <span class="ver ver-20">C++20</span> {#reverse_view data-toc-label="std::ranges::reverse_view"}

```cpp
template <view V>
class reverse_view;
```

- 戻り値: `begin()` / `end()` をもつ view の型
- 計算量: begin / end は定数。要素の取り出しは元の範囲と同じ

逆順に見せる view。`views::reverse` が作ります。

ふつうは `views::reverse` を使って書くので、この型の名前を自分で書くことは少なく、`auto` で受けます。型名が必要なとき（関数の戻り値の型を明示したいときなど）や、CTAD（クラステンプレートの引数推論）で `std::ranges::reverse_view v(r, ...)` と直接作るときにだけ登場します。

## ゲームでの使いどころ

ログやチャットを新しい順に表示する場面で使います。`for (auto& msg : messages | std::views::reverse)` と書けば、最新のメッセージから順に処理されます。`take` と組み合わせて、`reverse | take(5)` とすれば、最新の 5 件を取り出せます。

描画の順番では、奥から手前に描く配列を、逆に手前から調べたい場面で使います。クリックしたときの当たり判定は、いちばん手前（最後に描いたもの）から調べたいので、逆順で回します。

並びそのものを書き換えたいなら、`std::ranges::reverse` を使います。こちらは元の `vector` の並びが入れ替わります。

## よくあるミス

??? failure "`forward_list` などに使ってコンパイルエラーになる"
    `reverse` には、双方向に進める範囲（`vector`、`list`、`deque` など）が必要です。`forward_list` や入力ストリームは、後ろに戻れないので使えません。

??? failure "元の並びが変わったと思う"
    ビューは見え方を変えるだけで、元のコンテナは変わりません。並びを入れ替えたいなら `std::ranges::reverse(v)` です。

??? failure "一時オブジェクトに使ってぶら下がる"
    `MakeVec() | std::views::reverse` は、`MakeVec()` が返す一時的な値が行の終わりで消えるので、以降の参照が壊れます。いったん変数に受けてから使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::reverse`](../reverse.md) | 並びを実際に逆にする |
| [`std::ranges::find_last`](../find_last.md) | 最後の一致を探す |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 逆順で「見る」
    - [x] 元は変わらない
    - [x] 双方向の範囲が必要

## 関連ページ

- [cpprefjp: std::ranges::reverse_view](https://cpprefjp.github.io/reference/ranges/reverse_view.html)
- [cppreference: std::ranges::reverse_view](https://en.cppreference.com/w/cpp/ranges/reverse_view)
