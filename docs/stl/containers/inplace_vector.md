---
title: std::inplace_vector
summary: "最大の大きさが決まっていて、ヒープを使わない vector。"
order: 27
tags:
  - コンテナ
---

# std::inplace_vector

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-4">◎ 速い</span>
<span class="ver ver-26">C++26</span>
`#include <inplace_vector>`
</div>

`std::inplace_vector<T, N>` は、**最大 N 個まで入る、ヒープを使わない可変長配列**です。要素は自分自身の中（スタックや、構造体の中）に並びます。`std::array` のように固定サイズで確保済みですが、`push_back` で個数が増減します。ゲームの「最大 8 体の敵」「最大 16 個のコンタクト点」のような、上限が決まった動的な配列にぴったりです。

!!! tip "ポイント"
    - **容量は N で固定**。超えて `push_back` すると例外（`std::bad_alloc`）。例外を使わないなら `try_push_back`。
    - ヒープ確保が一切ないので、毎フレーム作っても遅くならない。
    - 要素は連続したメモリに並ぶ。`std::vector` と同じように使える。

!!! info "このページを読む前に"
    [`std::vector`](vector.md) を先に読んでください。

## 宣言

```cpp
template <class T, std::size_t N>
class inplace_vector;
```

## 関数の詳しい説明

### push_back {#push_back}

```cpp
constexpr void push_back(const T& value);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `value` | `const T&` | 末尾に追加する値 |

- 戻り値: なし。**満杯のとき `std::bad_alloc` を投げる**
- 計算量: O(1)

### try_push_back {#try_push_back}

```cpp
constexpr T* try_push_back(const T& value);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `value` | `const T&` | 末尾に追加する値 |

- 戻り値: 追加した要素へのポインター。**満杯なら `nullptr`**（例外を投げない）
- 計算量: O(1)

```cpp
#include <inplace_vector>
#include <print>

int main() {
  std::inplace_vector<int, 4> hits;  // 最大 4 個

  for (int i = 1; i <= 5; ++i) {
    if (hits.try_push_back(i) == nullptr) {
      std::println("{} は入らなかった（満杯）", i);
    }
  }
  std::println("個数 {} / 容量 {}", hits.size(), hits.capacity());
}
```

```text title="実行結果"
5 は入らなかった（満杯）
個数 4 / 容量 4
```

### capacity, max_size {#capacity}

```cpp
static constexpr size_type capacity() noexcept;
static constexpr size_type max_size() noexcept;
```

- 戻り値: 常に N
- 計算量: O(1)

### そのほかの関数（vector と同じ） {#others}

```cpp
// std::vector と同じ名前の関数
```

- 戻り値: `std::vector` と同じ使い方
- 計算量: vector と同じ

### unchecked_push_back {#unchecked_push_back}

```cpp
constexpr reference unchecked_push_back(const T& value);
```

- 計算量: 定数

容量の確認なしで、末尾に追加します。容量を超えると**未定義動作**です。確実に空きがあるとき（直前に `size() < capacity()` を確かめたなど）だけ使います。

### unchecked_emplace_back {#unchecked_emplace_back}

```cpp
template <class... Args>
constexpr reference unchecked_emplace_back(Args&&... args);
```

- 計算量: 定数

容量の確認なしで、末尾に要素をその場で作ります。容量を超えると未定義動作です。

### try_emplace_back {#try_emplace_back}

```cpp
template <class... Args>
constexpr pointer try_emplace_back(Args&&... args);
```

- 計算量: 定数

空きがあれば末尾に要素を作って、そのポインタを返します。満杯なら例外を投げず、`nullptr` を返します。

### try_append_range {#try_append_range}

```cpp
template <ranges::input_range R>
constexpr ranges::borrowed_iterator_t<R> try_append_range(R&& rg);
```

- 計算量: O(追加数)

範囲の要素を、入るところまで末尾に追加します。入りきらない要素の手前で止まり、そのイテレータを返します。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 1 フレームで当たる敵の一覧（最大 16 体） | `std::inplace_vector<Enemy*, 16> hits;` |
| 衝突の接触点（最大 4 点） | `inplace_vector<Contact, 4>` |
| ヒープを使えない場面（割り込み、リアルタイム処理） | すべて固定メモリ |

## よくあるミス

??? failure "容量を超えて push_back する"
    満杯での `push_back` は例外（`std::bad_alloc`）です。ゲームでは例外を切っていることが多いので、`try_push_back` で戻り値を確認するのが安全です。

??? failure "N を大きくしすぎる"
    要素ごと自分の中に持つので、`sizeof` が N に比例して大きくなります。スタックに置くときは、数 KB までにします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::vector`](vector.md) | 上限なし。ヒープを使う |
| [`std::array`](array.md) | 個数も固定。常に N 個ぶん存在する |
| [`std::pmr::vector`](../memory/pmr.md) | メモリの取り先を切り替えられる vector |

## コンパイラ対応

C++26 の機能です。GCC 15 以降の libstdc++ / MSVC 19.4x 以降で使えます（コンパイラの版に注意）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 最大 N 個、ヒープを使わない可変長配列
    - [x] 満杯のときは `try_push_back` で `nullptr`
    - [x] 毎フレームの一時配列に向く

## 関連ページ

- [cpprefjp: std::inplace_vector](https://cpprefjp.github.io/reference/inplace_vector/inplace_vector.html)
- [cppreference: std::inplace_vector](https://en.cppreference.com/w/cpp/container/inplace_vector)
