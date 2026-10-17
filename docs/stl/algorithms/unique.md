---
title: std::ranges::unique
tags:
  - アルゴリズム
---

# std::ranges::unique

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::unique` は、**連続して並んでいる同じ値を 1 つにまとめる**関数です。「連続して」なので、`{1, 1, 2, 1}` は `{1, 2, 1}` になります。全体の重複を消したいなら、**先にソートしてから** `unique` します。また、`unique` は「残すものを前に詰める」だけで要素数は変えないので、後ろに残ったものは自分で `erase` します。

!!! tip "ポイント"
    - 重複を消す定番は「`sort` → `unique` → `erase`」の 3 点セット。
    - 順番を気にしないなら、`std::set` / `std::unordered_set` に入れるだけでもいい。
    - `unique` 単体では要素数が減らない。戻り値の範囲を `erase` する。

## 関数一覧

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`std::ranges::unique`](#unique) | <span class="rank rank-sometimes">たまに</span> | 連続する重複を前に詰めてまとめる | O(n) |
| [`std::ranges::unique_copy`](#unique_copy) | <span class="rank rank-rare">知ってるだけ</span> | 重複をまとめたものを別の場所にコピー | O(n) |

## よくある使い方

### 重複を全部消す

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> ids = {5, 3, 5, 1, 3, 3};

  std::ranges::sort(ids);                     // [1, 3, 3, 3, 5, 5]
  auto removed = std::ranges::unique(ids);    // 後ろに余りが残る
  ids.erase(removed.begin(), removed.end());  // 余りを消す

  std::println("{}", ids);
}
```

```text title="実行結果"
[1, 3, 5]
```

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

### std::ranges::unique_copy {#unique_copy}

```cpp
template <input_range R, weakly_incrementable O, class Proj = identity, class Comp = ranges::equal_to>
constexpr unique_copy_result<borrowed_iterator_t<R>, O> unique_copy(R&& r, O result, Comp comp = {}, Proj proj = {});
```

- 元はそのままで、連続する重複をまとめたものを `result` に書き込みます

```cpp
#include <algorithm>
#include <iterator>
#include <print>
#include <string>

int main() {
  std::string input = "aaabbbcc";
  std::string compressed;
  std::ranges::unique_copy(input, std::back_inserter(compressed));
  std::println("{}", compressed);
}
```

```text title="実行結果"
abc
```

## フラグ・オプション

| 引数 | 重要度 | 渡すもの | 意味 |
| --- | --- | --- | --- |
| `proj` | <span class="rank rank-sometimes">たまに</span> | `&Type::member` | メンバが同じなら重複とみなす |
| `comp` | <span class="rank rank-rare">知ってるだけ</span> | ラムダ式 | 「近い値なら同じ」など自由な判定 |

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| 重複した ID を除く | 当たった敵のリスト、読み込むアセットのリスト |
| 連続するログをまとめる | 同じエラーが続いたら 1 回だけ表示 |

## よくあるミス

??? failure "ソートせずに使って重複が残る"
    `{1, 2, 1}` に `unique` しても何も変わりません。全体の重複を消すなら先に `sort` します。

??? failure "erase を忘れる"
    `unique` だけでは `size()` は変わらず、後ろに不定な値が残ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::set`](../containers/set.md) | 入れるだけで重複が消えて並ぶ |
| [`std::unordered_set`](../containers/unordered_set.md) | 入れるだけで重複が消える（順番なし） |
| [`std::erase_if`](erase_if.md) | 条件で消す |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 重複を消すのは「sort → unique → erase」
    - [x] unique は「連続する」重複だけ。要素数は減らない

## 関連ページ

- [cpprefjp: std::ranges::unique](https://cpprefjp.github.io/reference/algorithm/ranges_unique.html)
- [cppreference: std::ranges::unique](https://en.cppreference.com/w/cpp/algorithm/ranges/unique)
