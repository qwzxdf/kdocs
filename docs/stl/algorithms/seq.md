---
title: std::execution::seq
summary: "並列化せず、順番に実行するポリシー。"
order: 900
tags:
  - アルゴリズム
---

# std::execution::seq

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <execution>`
</div>

`std::execution::seq` を第 1 引数に渡すと、アルゴリズムは**1 つのスレッドで順番に**実行されます。ポリシーなしと同じ動作ですが、「並列にしない」ことを明示できます。例外が出たら `std::terminate` になる点が、ポリシーなしと違います。

!!! tip "ポイント"
    - アルゴリズムの第 1 引数に渡して使う。
    - 実装の対応はコンパイラごとに違う（GCC は TBB が必要なことがある）。
    - 処理の中で、データ競合を起こさないようにする。

!!! info "このページを読む前に"
    [実行ポリシー](execution.md) を先に読んでください。

## 関数の詳しい説明

### std::execution::seq {#seq}

```cpp
inline constexpr /* 実装定義 */ std::execution::seq;
```

- 戻り値: なし（ポリシーの定数）
- 計算量: アルゴリズムに依存


## 実際に動かしてみる

```cpp
#include <algorithm>
#include <execution>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {3, 1, 2};
  std::sort(std::execution::seq, v.begin(), v.end());
  std::println("{}", v);
}
```

```text title="実行結果"
[1, 2, 3]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 大量のデータの整列や変換を速くする | `std::sort(std::execution::seq, v.begin(), v.end());` |

## よくあるミス

??? failure "データ競合を起こす"
    ポリシーを付けると、要素ごとの処理が並行・同時に走ることがあります。共有する変数への書き込みは、`atomic` などで守ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`execution`](execution.md) | 実行ポリシーの全体 |

## コンパイラ対応

C++17 の機能です。GCC では TBB（`-ltbb`）が必要なことがあります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 並列化せず、順番に実行するポリシー
    - [x] アルゴリズムの第 1 引数に渡す
    - [x] データ競合に注意

## 関連ページ

- [cpprefjp: std::execution::seq](https://cpprefjp.github.io/reference/execution/execution_policy.html)
- [cppreference: std::execution::seq](https://en.cppreference.com/w/cpp/algorithm/execution_policy_tag)
