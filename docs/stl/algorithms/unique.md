---
title: std::ranges::unique
summary: "隣り合う重複を 1 つにまとめる（並べ替えておくと全体の重複を除ける）。"
order: 39
tags:
  - アルゴリズム
---

# std::ranges::unique

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

重複を取り除いた一覧が欲しい。たとえば、読み込んだタグの一覧から、同じタグを 1 つにまとめたい。`std::ranges::unique` は、隣り合っている同じ値を 1 つにまとめて、前に詰めるアルゴリズムです。離れた同じ値は残るので、全体の重複を取り除くには、先に `sort` して同じ値を隣り合わせにします。`remove` と同じく、大きさは変わらないので、`erase` で後ろを消します。

!!! tip "ポイント"
    - 全体の重複を消す手順は **`sort` → `unique` → `erase`**。
    - `unique` だけでは、離れた同じ値は消えない。
    - 戻り値の範囲（後ろのゴミ）を `erase` で消す。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::unique {#unique}

```cpp
template <forward_range R, class Proj = identity, class Comp = ranges::equal_to>
constexpr borrowed_subrange_t<R> unique(R&& r, Comp comp = {}, Proj proj = {});
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `r` | 範囲 | まとめる範囲 | 省略不可 |
| `comp` | 比較関数 | 「同じ」とみなす条件 | `==` |
| `proj` | プロジェクション | 比べる前の変換 | そのまま |

- 戻り値: **余った部分**（消すべき部分）の範囲。`.begin()` から `.end()` を `erase` する
- 計算量: O(n)

<div class="mem">
<div class="mem-step"><span class="mem-label">前</span><span class="mem-cells"><span>1</span><span>1</span><span>2</span><span>2</span><span>3</span></span></div>
<div class="mem-step"><span class="mem-label">unique の後</span><span class="mem-cells"><span>1</span><span class="move">2</span><span class="move">3</span><span class="gone">?</span><span class="gone">?</span></span><span class="mem-note">? の部分が戻り値の範囲。中身は不定なので erase する</span></div>
</div>

<div class="anim" data-label="std::ranges::unique(v)">
1 1 2 2 2 3 # 連続した重複がある
1 x1 2 x2 x2 3 # 連続する同じ値を消す対象にする
1 >2 >3 _ _ _ # 残りを前に詰める
1 2 3 # erase で後ろを切り捨てて完成。離れた重複は消えない
</div>

```cpp
#include <algorithm>
#include <print>
#include <string>
#include <vector>

struct Log {
  std::string message;
};

int main() {
  // 同じメッセージが連続したら 1 つにまとめる
  std::vector<Log> logs = {{"接続"}, {"接続"}, {"切断"}, {"接続"}};
  auto rest = std::ranges::unique(logs, {}, &Log::message);
  logs.erase(rest.begin(), rest.end());
  for (const auto& log : logs) {
    std::println("{}", log.message);
  }
}
```

```text title="実行結果"
接続
切断
接続
```

## ゲームでの使いどころ

重複の除去に、`sort` → `unique` → `erase` の 3 点セットで使います。

```cpp
std::ranges::sort(tags);
auto dup = std::ranges::unique(tags);
tags.erase(dup.begin(), dup.end());
```

順番を保ったまま重複を除きたいなら、`unordered_set` で「すでに出た」を覚えながら、`copy_if` で集める方法があります。

連続した重複だけを取りたい場面（同じ入力が連続した場合に 1 つにまとめる）では、`sort` せず、`unique` だけを使います。

## よくあるミス

??? failure "並べ替えずに使って、重複が残る"
    `{1, 2, 1}` に `unique` を使っても何も消えません。先に `sort` します。

??? failure "erase を忘れる"
    `unique` は後ろに不定の要素を残します。戻り値から `erase` で消します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::unique_copy`](unique_copy.md) | 結果を別の場所へ作る |
| `std::set` / `std::unordered_set` | そもそも重複を持たないコンテナ |
| [`std::ranges::adjacent_find`](adjacent_find.md) | 隣り合う重複を見つける |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 隣り合う重複をまとめる
    - [x] 全体の重複は `sort` → `unique` → `erase`
    - [x] erase を忘れない

## 関連ページ

- [cpprefjp: std::ranges::unique](https://cpprefjp.github.io/reference/algorithm/ranges_unique.html)
- [cppreference: std::ranges::unique](https://en.cppreference.com/w/cpp/algorithm/ranges/unique)
