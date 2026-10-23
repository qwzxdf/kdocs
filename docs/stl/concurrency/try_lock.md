---
title: std::try_lock
summary: "複数のミューテックスを、待たずにまとめてロックしようとする。"
order: 900
tags:
  - 並行処理
---

# std::try_lock

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <mutex>`
</div>

複数のミューテックスを同時にロックするとき、`std::lock` はロックが取れるまで待ちます。`std::try_lock` は待たず、順にロックを試みて、1 つでも取れなければ、取れたものを全部解除して、取れなかった番号を返します。全部取れたら `-1` です。

!!! tip "ポイント"
    - 戻り値が `-1` なら、全部ロックできた。
    - 失敗したら、取れた分は解除される。
    - `std::lock` は待つが、`try_lock` は待たない。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::try_lock {#try_lock}

```cpp
template <class L1, class L2, class... Ln>
int try_lock(L1& l1, L2& l2, Ln&... ln);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `l1, l2, ln...` | ロックできるもの | ロックを試みるミューテックス |

- 戻り値: 全部取れたら `-1`、取れなかったら最初に失敗した番号（0 から）
- 計算量: ミューテックスの数に比例


## 実際に動かしてみる

```cpp
#include <mutex>
#include <print>

int main() {
  std::mutex a;
  std::mutex b;
  int r = std::try_lock(a, b);
  std::println("{}", r);
  if (r == -1) {
    a.unlock();
    b.unlock();
  }
}
```

```text title="実行結果"
-1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 2 つの資源を、取れるときだけ同時に取る |

## よくあるミス

??? failure "失敗したときに解除しようとする"
    失敗したときは、取れた分は自動で解除されています。もう一度 `unlock` しないようにします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`lock`](lock.md) | 取れるまで待つ |
| [`scoped_lock`](scoped_lock.md) | RAII でまとめてロックする |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 複数のミューテックスを、待たずにまとめてロックしようとする
    - [x] 戻り値が `-1` なら、全部ロックできた
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::try_lock](https://cpprefjp.github.io/reference/mutex/try_lock.html)
- [cppreference: std::try_lock](https://en.cppreference.com/w/cpp/thread/try_lock)
