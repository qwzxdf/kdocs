---
title: std::atomic_fetch_sub
summary: "アトミックに減算し、減算前の値を返す。"
order: 900
tags:
  - 並行処理
---

# std::atomic_fetch_sub

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <atomic>`
</div>

参照カウントを 1 減らして、0 になったら解放する。このとき、「減らす」と「0 かどうかを調べる」の間に別のスレッドが割り込むと、二重に解放される危険があります。`fetch_sub(n)` は、減算を不可分に行い、減算前の値を返すので、「前の値が 1 だったか」で判定できます。

!!! tip "ポイント"
    - 減算を不可分に行い、減算前の値を返す
    - 参照カウントの解放判定に使う（前の値が 1 なら、最後の 1 つ）
    - メンバー関数 `a.fetch_sub(n)` と同じ
    - メモリ順序の指定版は `atomic_fetch_sub_explicit`

!!! info "このページを読む前に"
    [`std::atomic`](atomic.md) を先に読んでください。

## 関数の詳しい説明

### std::atomic_fetch_sub {#atomic_fetch_sub}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
T atomic_fetch_sub(std::atomic<T>* obj, typename std::atomic<T>::difference_type arg) noexcept;
```

戻り値は、減算する前の値です。

参照カウントの解放は、次の形が定番です。

```cpp
if (refs.fetch_sub(1, std::memory_order_acq_rel) == 1) {
  delete this;   // 最後の参照が消えた
}
```

`memory_order_acq_rel` にするのは、解放の前に、他のスレッドがそのオブジェクトに行った書き込みが見えるようにするためです。`relaxed` のままだと、順序の入れ替えで、解放後のメモリを読む可能性があります。

符号なし整数では、0 から減らすと巻き戻って巨大な値になります。0 になる前に止めるのは、呼び出し側の責任です。

## 実際に動かしてみる

```cpp
#include <atomic>
#include <print>

int main() {
  std::atomic<int> refs{3};

  // 前の値が 1 になった瞬間が、最後の参照
  for (int i = 0; i < 3; ++i) {
    const int before = std::atomic_fetch_sub(&refs, 1);
    std::println("減算前 {} 最後の参照か {}", before, before == 1);
  }
  std::println("残り: {}", refs.load());
}
```

```text title="実行結果"
減算前 3 最後の参照か false
減算前 2 最後の参照か false
減算前 1 最後の参照か true
残り: 0
```

## ゲームでの使いどころ

自作の参照カウント付きリソースで、最後の所有者を判定するときに使います。標準なら `std::shared_ptr` です。

## よくあるミス

??? failure "減算してから、別に値を読んで判定する"
    その間に割り込まれます。戻り値で判定します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`atomic_fetch_add`](atomic_fetch_add.md) | 加算 |
| [`atomic`](atomic.md) | 本体 |
| [`memory_order`](memory_order.md) | 順序の指定 |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::atomic_fetch_sub](https://cpprefjp.github.io/reference/atomic/atomic_fetch_sub.html)
- [cppreference: std::atomic_fetch_sub](https://en.cppreference.com/w/cpp/atomic/atomic_fetch_sub)
