---
title: std::atomic_flag_clear
summary: "atomic_flag を下ろす。"
order: 900
tags:
  - 並行処理
---

# std::atomic_flag_clear

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <atomic>`
</div>

`atomic_flag_test_and_set` で立てた旗を、`clear` で下ろします。スピンロックの解除に使います。

!!! tip "ポイント"
    - `std::atomic` のメンバ関数と同じ働きの、自由関数版。
    - ふつうはメンバ関数のほうが読みやすい。
    - C 言語との互換のためにある。

!!! info "このページを読む前に"
    [`std::atomic`](atomic.md) を先に読んでください。

## 関数の詳しい説明

### std::atomic_flag_clear {#atomic_flag_clear}

```cpp
void atomic_flag_clear(std::atomic_flag* obj) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `obj` | atomic_flag* | 対象の旗 |

- 戻り値: なし
- 計算量: 定数（アトミック命令）


## 実際に動かしてみる

```cpp
#include <atomic>
#include <print>

int main() {
  std::atomic_flag f = ATOMIC_FLAG_INIT;
  std::atomic_flag_test_and_set(&f);
  std::atomic_flag_clear(&f);
  std::println("{}", std::atomic_flag_test_and_set(&f));
}
```

```text title="実行結果"
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 自作のスピンロックを解除する |

## よくあるミス

??? failure "解除し忘れる"
    旗を下ろさないと、待っているスレッドがずっと待ち続けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`atomic_flag_test_and_set`](atomic_flag_test_and_set.md) | 旗を立てる |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] atomic_flag を下ろす
    - [x] `std::atomic` のメンバ関数と同じ働きの、自由関数版
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::atomic_flag_clear](https://cpprefjp.github.io/reference/atomic/atomic_flag_clear.html)
- [cppreference: std::atomic_flag_clear](https://en.cppreference.com/w/cpp/atomic/atomic_flag_clear)
