---
title: realloc
summary: "確保したメモリの大きさを変える。"
order: 23
group: C の確保関数（<cstdlib>）
tags:
  - メモリ
---

# realloc

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

`realloc` は、**確保済みのメモリの大きさを変える**関数です。場所が移ることがあり、古いポインターは使えなくなります。**失敗すると元のメモリはそのまま**なので、戻り値を別の変数で受けて確認します。

!!! tip "ポイント"
    - `p = realloc(p, n)` と書かない（失敗すると元のポインターを失う）。
    - `new` で確保したものには使えない。
    - C++ では `std::vector` が同じことをする。

!!! info "このページを読む前に"
    [ポインタ](../../basics/pointer.md) が分かると読みやすいです。

## 関数の詳しい説明

### realloc {#realloc}

```cpp
void* realloc(void* ptr, std::size_t new_size);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ptr` | `void*` | 以前に確保したポインタ。`nullptr` なら `malloc(new_size)` と同じ |
| `new_size` | `std::size_t` | 新しいバイト数 |

- 戻り値: 新しい領域の先頭。**元のポインタと同じとは限らない**（引っ越すことがある）。失敗したら `nullptr`（元の領域はそのまま残る）
- 中身は、小さい方の大きさまでコピーされます。**広げた部分は未初期化**です
- 引っ越したときは、古いポインタ（や、その中を指していたポインタ）は**無効**になります。[`vector` の再確保](../containers/vector.md#realloc)と同じ考え方です
- **コンストラクタを持つ型には使えません**。ビット単位でコピーされるだけで、ムーブコンストラクタが呼ばれないためです

```cpp
// × 失敗すると、元の領域を指すポインタを失ってリークする
data = static_cast<int*>(std::realloc(data, new_count * sizeof(int)));

// ○ 別の変数で受けてから、成功したら置き換える
void* bigger = std::realloc(data, new_count * sizeof(int));
if (bigger == nullptr) {
  std::free(data);  // 元の領域は残っているので、自分で返す
  return false;
}
data = static_cast<int*>(bigger);
```

## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  int* p = static_cast<int*>(std::malloc(2 * sizeof(int)));
  p[0] = 1;
  p[1] = 2;

  void* q = std::realloc(p, 4 * sizeof(int));  // 失敗に備えて別の変数で受ける
  if (q) {
    p = static_cast<int*>(q);
    p[2] = 3;
    std::println("{}", p[0] + p[1] + p[2]);
  }
  std::free(p);
}
```

```text title="実行結果"
6
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| C 風のバッファを伸ばす | `void* q = realloc(p, new_size); if (q) p = q;` |

## よくあるミス

??? failure "戻り値で元の変数を上書きする"
    失敗して `nullptr` が返ると、元のメモリが解放できなくなります（リーク）。

## 類似

| 名前 | 違い |
| --- | --- |
| [`malloc`](malloc.md) | 新しく確保する |
| [`std::vector`](../containers/vector.md) | 自動で伸びる |

## コンパイラ対応

C 由来の関数です。`aligned_alloc` は C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 大きさを変える
    - [x] 場所が移ることがある
    - [x] 戻り値を別の変数で受ける

## 関連ページ

- [cpprefjp: realloc](https://cpprefjp.github.io/reference/cstdlib/realloc.html)
- [cppreference: realloc](https://en.cppreference.com/w/cpp/memory/c/realloc)
