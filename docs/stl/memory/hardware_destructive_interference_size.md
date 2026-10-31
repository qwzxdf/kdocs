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

複数のスレッドが、別々の変数を書き換えているのに、それらが同じキャッシュ ラインにあると、お互いにキャッシュを無効にし合って、遅くなります。これが偽共有です。`std::hardware_destructive_interference_size` は、<strong>「この間隔以上離せば、別のキャッシュ ラインになる」</strong>という大きさで、偽共有を避けるために、スレッドごとの変数の間に空ける距離に使います。

!!! tip "ポイント"
    - スレッドごとのデータを、この大きさ以上離して置く
    - `alignas(std::hardware_destructive_interference_size)` で境界に合わせる
    - アトミック カウンターを配列で持つとき、特に効く
    - `<new>` の定数。C++17。典型は 64 バイト

!!! info "このページを読む前に"
    [`hardware_constructive_interference_size`](hardware_constructive_interference_size.md) を先に読んでください。

## 関数の詳しい説明

### std::hardware_destructive_interference_size {#hardware_destructive_interference_size}

<span class="ver ver-17">C++17</span>

```cpp
inline constexpr std::size_t hardware_destructive_interference_size = /* 実装定義 */;
```

「破壊的な干渉」、つまり、同じキャッシュ ラインにあると、スレッド間で足を引っ張り合う距離です。

ワーカー スレッドごとのカウンターを `std::atomic<int> counters[8]` と並べると、8 個が同じキャッシュ ラインに載り、書き込みのたびに、全スレッドのキャッシュが無効になります。各カウンターを `alignas(この定数)` で包めば、別々のキャッシュ ラインになります。

この定数は、メモリの使用量を増やします（カウンター 1 つに 64 バイト）。本当に競合する変数だけに使います。

## 実際に動かしてみる

```cpp
#include <atomic>
#include <new>
#include <print>

// スレッドごとのカウンターを、別のキャッシュ ラインに置く
struct alignas(std::hardware_destructive_interference_size) PaddedCounter {
  std::atomic<int> value{0};
};

int main() {
  PaddedCounter counters[4];
  std::println("1 つの大きさ: {}", sizeof(PaddedCounter));
  std::println("隣と離れている: {}",
               sizeof(PaddedCounter) >= std::hardware_destructive_interference_size);
  std::println("4 つ並べた大きさ: {}", sizeof(counters));
}
```

```text title="実行結果"
1 つの大きさ: 64
隣と離れている: true
4 つ並べた大きさ: 256
```

## ゲームでの使いどころ

ジョブ システムで、ワーカー スレッドごとに持つ統計のカウンターや、キューの先頭と末尾のインデックスを、別のキャッシュ ラインに置くときに使います。

## よくあるミス

??? failure "全部の変数に付ける"
    メモリを浪費します。競合するものだけに使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`hardware_constructive_interference_size`](hardware_constructive_interference_size.md) | まとめて載せたい大きさ |
| `std::atomic` | スレッド間で共有する変数 |
| `alignas` | アライメント指定 |

## コンパイラ対応

C++17 から使えます。手元の MSVC では 64 でした。

## 関連ページ

- [cpprefjp: std::hardware_destructive_interference_size](https://cpprefjp.github.io/reference/new/hardware_destructive_interference_size.html)
- [cppreference: std::hardware_destructive_interference_size](https://en.cppreference.com/w/cpp/thread/hardware_destructive_interference_size)
