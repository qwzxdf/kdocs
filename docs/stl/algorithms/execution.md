---
title: 実行ポリシー（std::execution）
summary: "アルゴリズムに「並列に実行してよい」と伝える指定。"
order: 90
tags:
  - アルゴリズム
---

# 実行ポリシー（std::execution）

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <execution>`
</div>

**実行ポリシー**は、アルゴリズムの第 1 引数に渡して、**「並列に実行してよい」と伝える指定**です。`std::sort(std::execution::par, v.begin(), v.end())` のように書くだけで、大きなデータの並べ替えや合計が複数のコアで実行されます。

!!! tip "ポイント"
    - ポリシーは `seq`（順番に）、`par`（並列）、`par_unseq`（並列＋ベクトル化）、`unseq`（C++20、ベクトル化のみ）の 4 つ。
    - **ranges 版のアルゴリズムでは使えない**（C++23 時点）。従来のイテレータ版 `std::sort` などで使う。
    - 小さなデータでは、並列化の準備のほうが重くて遅くなる。数万要素以上から。

!!! info "このページを読む前に"
    [スレッド](../../basics/concurrency.md) の基本が分かると読みやすいです。

## 関数の詳しい説明

### std::execution::par {#par}

```cpp
inline constexpr std::execution::parallel_policy par;
```

- 戻り値: 各アルゴリズムのオーバーロードの第 1 引数に渡す
- 計算量: アルゴリズムによる

```cpp
#include <execution>
#include <numeric>
#include <print>
#include <vector>

int main() {
  std::vector<int> v(1'000'000, 1);

  // 並列に合計を求める
  long long sum = std::reduce(std::execution::par, v.begin(), v.end(), 0LL);
  std::println("合計 {}", sum);
}
```

```text title="実行結果"
合計 1000000
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 巨大な配列の並べ替え・合計・変換を並列化する | `std::sort(std::execution::par, ...)` |
| 大量のオブジェクトの更新を並列にする | `std::for_each(std::execution::par, ...)` |

## よくあるミス

??? failure "並列にすると遅くなる"
    要素が少ないと、スレッドの準備のほうが重くなります。測ってから使います。

??? failure "ポリシー付きの関数の中で例外を投げる"
    並列版では、例外が `std::terminate` になります。例外を外に出さないでください。

??? failure "GCC でリンクエラー"
    GCC は内部で Intel TBB を使います。`-ltbb` をリンクし、TBB を入れておく必要があります。MSVC は標準で使えます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::reduce`](reduce.md) | 並列化できる合計 |
| [`std::thread`](../concurrency/thread.md) | 自分でスレッドを管理する |
| [`std::for_each`](for_each.md) | 各要素に処理（並列版あり） |

## コンパイラ対応

C++17 の機能です。MSVC 19.14 以降で使えます。GCC 9 以降は TBB が必要です。Clang (libc++) は対応が限定的です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] アルゴリズムの第 1 引数に渡す
    - [x] `par` で並列、`seq` で順番
    - [x] ranges 版では使えない

## 関連ページ

- [cpprefjp: 実行ポリシー](https://cpprefjp.github.io/reference/execution.html)
- [cppreference: std::execution](https://en.cppreference.com/w/cpp/algorithm/execution_policy_tag_t)
