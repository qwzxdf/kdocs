---
title: std::kill_dependency
summary: "メモリ順序の依存関係をここで断ち切る。"
order: 900
tags:
  - 並行処理
---

# std::kill_dependency

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <atomic>`
</div>

`memory_order_consume` の依存の連鎖をここで終わらせます。実際の実装では `consume` が `acquire` として扱われるので、ほとんど使われません。C++26 では `consume` 自体が非推奨です。

!!! tip "ポイント"
    - `std::atomic` のメンバ関数と同じ働きの、自由関数版。
    - ふつうはメンバ関数のほうが読みやすい。
    - C 言語との互換のためにある。

!!! info "このページを読む前に"
    [`std::atomic`](atomic.md) を先に読んでください。

## 関数の詳しい説明

### std::kill_dependency {#kill_dependency}

```cpp
template <class T>
T kill_dependency(T y) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `y` | T | 依存を断ち切る値 |

- 戻り値: `y` のコピー
- 計算量: 定数（アトミック命令）


## 実際に動かしてみる

```cpp
#include <atomic>
#include <print>

int main() {
  int y = std::kill_dependency(5);
  std::println("{}", y);
}
```

```text title="実行結果"
5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | （実際にはほぼ使われない） |

## よくあるミス

??? failure "新しいコードで使う"
    `consume` が非推奨のため、使う場面がありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`memory_order`](memory_order.md) | 順序の種類 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] メモリ順序の依存関係をここで断ち切る
    - [x] `std::atomic` のメンバ関数と同じ働きの、自由関数版
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::kill_dependency](https://cpprefjp.github.io/reference/atomic/kill_dependency.html)
- [cppreference: std::kill_dependency](https://en.cppreference.com/w/cpp/atomic/kill_dependency)
