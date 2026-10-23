---
title: std::hardware_destructive_interference_size
summary: "フォルス・シェアリングを避けるためにそろえる、キャッシュラインの大きさ。"
order: 30
tags:
  - メモリ
---

# std::hardware_destructive_interference_size

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <new>`
</div>

`std::hardware_destructive_interference_size` は、**複数のスレッドが別々の変数を触っても、同じキャッシュラインに乗っていると互いに邪魔をする（フォルス・シェアリング）のを避けるために、変数を離す距離**です。多くの環境で 64 バイトです。スレッドごとのカウンターを、この大きさでそろえて置くと、競合しなくなります。

!!! tip "ポイント"
    - スレッドごとの変数は `alignas(std::hardware_destructive_interference_size)` で離す。
    - `hardware_constructive_interference_size` は逆に、「一緒に使うデータをこの中に収めると速い」大きさ。
    - GCC は ABI 警告を出す（`-Winterference-size`）。

!!! info "このページを読む前に"
    - [stl/index.md](../index.md)（STL 全体の地図（どこに何があるか））
    - [所有権（誰が消すのか）](../../basics/ownership.md)（所有権の考え方）

## 関数の詳しい説明

### std::hardware_destructive_interference_size {#hardware_destructive_interference_size}

```cpp
inline constexpr std::size_t hardware_destructive_interference_size = /* 実装定義 */;
```

- 戻り値: 距離（バイト、多くは 64）
- 計算量: コンパイル時

```cpp
#include <new>
#include <print>

struct alignas(std::hardware_destructive_interference_size) Counter {
  int value = 0;  // スレッドごとのカウンター
};

int main() {
  std::println("{}", sizeof(Counter) >= std::hardware_destructive_interference_size);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| スレッドごとの統計カウンターを隣り合わせに置いても、遅くならないようにする | `alignas(std::hardware_destructive_interference_size)` |

## よくあるミス

??? failure "対応していないコンパイラ"
    GCC / Clang の古い版では未実装です。64 を直接書いても実用上は問題ありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::atomic`](../concurrency/atomic.md) | 同じ変数を複数スレッドで触るとき |
| [`max_align_t`](../support/max_align_t.md) | 基本のアラインメント |

## コンパイラ対応

C++17 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] フォルス・シェアリング避けの距離
    - [x] alignas でそろえる
    - [x] 多くは 64 バイト

## 関連ページ

- [cpprefjp: std::hardware_destructive_interference_size](https://cpprefjp.github.io/reference/new/hardware_destructive_interference_size.html)
- [cppreference: std::hardware_destructive_interference_size](https://en.cppreference.com/w/cpp/thread/hardware_destructive_interference_size)
