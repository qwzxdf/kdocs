---
title: std::atomic_wait
summary: "値が変わるまで、アトミックに待つ。"
order: 900
tags:
  - 並行処理
---

# std::atomic_wait

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <atomic>`
</div>

`atomic` の値が `old` と等しい間、スレッドを眠らせます。ビジーループ（回り続ける）より CPU を使いません。`atomic_notify_one` / `atomic_notify_all` で起こされます。

!!! tip "ポイント"
    - `std::atomic` のメンバ関数と同じ働きの、自由関数版。
    - ふつうはメンバ関数のほうが読みやすい。
    - C 言語との互換のためにある。

!!! info "このページを読む前に"
    [`std::atomic`](atomic.md) を先に読んでください。

## 関数の詳しい説明

### std::atomic_wait {#atomic_wait}

```cpp
template <class T>
void atomic_wait(const std::atomic<T>* obj, T old) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `obj` | const atomic<T>* | 対象 |
| `old` | T | この値と等しい間、待つ |

- 戻り値: なし
- 計算量: 定数（アトミック命令）


## 実際に動かしてみる

```cpp
#include <atomic>
#include <print>

int main() {
  std::atomic<int> a{1};
  std::atomic_wait(&a, 0);  // 値は 0 ではないので待たずに戻る
  std::println("returned");
}
```

```text title="実行結果"
returned
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 別のスレッドの完了を待つ |

## よくあるミス

??? failure "通知を忘れる"
    値を変えたら、`atomic_notify_one` / `atomic_notify_all` で起こす必要があります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`atomic_notify_one`](atomic_notify_one.md) | 1 つ起こす |
| [`atomic_notify_all`](atomic_notify_all.md) | 全部起こす |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 値が変わるまで、アトミックに待つ
    - [x] `std::atomic` のメンバ関数と同じ働きの、自由関数版
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::atomic_wait](https://cpprefjp.github.io/reference/atomic/atomic_wait.html)
- [cppreference: std::atomic_wait](https://en.cppreference.com/w/cpp/atomic/atomic_wait)
