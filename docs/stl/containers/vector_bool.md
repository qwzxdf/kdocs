---
title: std::vector<bool>
summary: "bool を 1 ビットずつに詰める、vector の特殊版。ふつうの vector とは別物。"
order: 24
tags:
  - コンテナ
---

# std::vector<bool>

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="perf perf-4">◎ 速い</span>
<span class="ver ver-11">C++98〜</span>
`#include <vector>`
</div>

`std::vector<bool>` は、**bool を 1 要素 1 ビットで詰めて持つ**特殊な `vector` です。メモリは 1/8 で済みますが、ふつうの `vector` とは**振る舞いが違います**。`[]` が返すのは `bool&` ではなく、ビットを指す代理オブジェクト（プロキシ）です。標準ライブラリの有名な落とし穴の 1 つです。

!!! tip "ポイント"
    - <strong>使うのは避ける。</strong> フラグが多いなら [`std::bitset`](bitset.md)（固定長）か `std::vector<char>` / `std::vector<uint8_t>` のほうが安全。
    - `auto& x = v[0];` は**コンパイルエラー**になる（`bool&` を返さないため）。
    - メモリは 1/8。数百万個のフラグ（訪問済み表など）では意味がある。

!!! info "このページを読む前に"
    [`std::vector`](vector.md) を先に読んでください。

## 宣言

```cpp
template <class Allocator>
class vector<bool, Allocator>;   // vector<T> の特殊化
```

## 関数の詳しい説明

### operator[] {#operator_at}

```cpp
reference operator[](size_type pos);
bool operator[](size_type pos) const;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pos` | `size_type` | 位置 |

- 戻り値: 非 const 版は**プロキシ**（代入でビットを書き換えられる）。const 版は `bool` の値
- 計算量: O(1)

### flip {#flip}

```cpp
void flip();
```

- 戻り値: なし。全ビットを反転する
- 計算量: O(n / 64)

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<bool> visited(5, false);  // 訪問済みフラグ
  visited[2] = true;

  visited.flip();  // 全ビットを反転する
  std::println("true の数: {}", std::ranges::count(visited, true));
}
```

```text title="実行結果"
true の数: 4
```

### push_back {#push_back}

```cpp
void push_back(bool value);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `value` | `bool` | 追加する値 |

- 戻り値: なし
- 計算量: 償却 O(1)

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 広いマップの「訪問済み」表（数百万マス） | `std::vector<bool> visited(w * h)` |

## よくあるミス

??? failure "auto& で参照を取る"
    ```cpp
    std::vector<bool> v(3);
    auto& r = v[0];   // NG: コンパイルエラー
    auto  r2 = v[0];  // これはプロキシ（元の vector が消えると壊れる）
    bool  b  = v[0];  // 値を取り出したいときはこう
    ```

??? failure "ポインターを取ろうとする"
    `&v[0]` は `bool*` ではなく、プロキシへのポインターになります。`v.data()` も存在しません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::bitset`](bitset.md) | 固定長のビット列。サイズがコンパイル時に決まるなら、こちら |
| `std::vector<char>` / `vector<uint8_t>` | 1 要素 1 バイト。ふつうの `vector` と同じ扱い |
| [`std::vector`](vector.md) | ふつうの `vector` |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] bool を 1 ビットで詰める特殊版
    - [x] `[]` はプロキシを返す。`auto&` は使えない
    - [x] 普通は `bitset` か `vector<char>`

## 関連ページ

- [cpprefjp: std::vector<bool>](https://cpprefjp.github.io/reference/vector/vector_bool.html)
- [cppreference: std::vector<bool>](https://en.cppreference.com/w/cpp/container/vector_bool)
