---
title: std::atomic_flag_test_and_set
summary: "atomic_flag を立て、立てる前の状態を返す。"
order: 900
tags:
  - 並行処理
---

# std::atomic_flag_test_and_set

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <atomic>`
</div>

`atomic_flag` は、最も単純な `atomic` の旗です。`test_and_set` は、旗を立てて、立てる前に立っていたかを返します。スピンロックの基本部品です。

!!! tip "ポイント"
    - `std::atomic` のメンバ関数と同じ働きの、自由関数版。
    - ふつうはメンバ関数のほうが読みやすい。
    - C 言語との互換のためにある。

!!! info "このページを読む前に"
    [`std::atomic`](atomic.md) を先に読んでください。

## 関数の詳しい説明

### std::atomic_flag_test_and_set {#atomic_flag_test_and_set}

```cpp
bool atomic_flag_test_and_set(std::atomic_flag* obj) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `obj` | atomic_flag* | 対象の旗 |

- 戻り値: 立てる前に立っていたか
- 計算量: 定数（アトミック命令）


## 実際に動かしてみる

```cpp
#include <atomic>
#include <print>

int main() {
  std::atomic_flag f = ATOMIC_FLAG_INIT;
  std::println("{}", std::atomic_flag_test_and_set(&f));
  std::println("{}", std::atomic_flag_test_and_set(&f));
}
```

```text title="実行結果"
false
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 自作のスピンロック |

## よくあるミス

??? failure "初期化を忘れる"
    C++20 より前は、`ATOMIC_FLAG_INIT` で初期化しないと、状態が不定でした。

## 類似

| 名前 | 違い |
| --- | --- |
| [`atomic_flag_clear`](atomic_flag_clear.md) | 旗を下ろす |
| [`atomic_flag`](atomic_flag.md) | 旗のクラス |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] atomic_flag を立て、立てる前の状態を返す
    - [x] `std::atomic` のメンバ関数と同じ働きの、自由関数版
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::atomic_flag_test_and_set](https://cpprefjp.github.io/reference/atomic/atomic_flag_test_and_set.html)
- [cppreference: std::atomic_flag_test_and_set](https://en.cppreference.com/w/cpp/atomic/atomic_flag_test_and_set)
