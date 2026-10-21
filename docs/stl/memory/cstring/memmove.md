---
title: memmove
summary: "メモリのバイト列を、別の場所へコピーする（重なっていてもよい）。"
order: 3
group: C の文字列・メモリ関数（<cstring>）
tags:
  - メモリ
---

# memmove

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstring>`
</div>

`memmove` は、[`memcpy`](memcpy.md) と同じバイト列のコピーですが、**コピー元とコピー先が重なっていても正しく動きます**。配列の途中を詰める・ずらすときに使います。

!!! tip "ポイント"
    - 重なる可能性があるなら `memmove`。重ならないと分かっているなら `memcpy`。
    - 内部で重なりを判断して、向きを選んでくれる。

!!! info "このページを読む前に"
    [ポインタ](../../../basics/pointer.md) が分かると読みやすいです。

## 関数の詳しい説明

### memmove {#memmove}

```cpp
void* memmove(void* dest, const void* src, std::size_t count);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `dest` | `void*` | コピー先 |
| `src` | `const void*` | コピー元 |
| `count` | `std::size_t` | コピーする**バイト数** |

- 戻り値: `dest`
- `memcpy` と違い、**`src` と `dest` が重なっていても正しくコピーされます**（元のデータを壊さない順番で動かす）
- 配列の中で、要素をずらすときに使います（`std::vector::insert` の中身がこれです）

<div class="anim" data-label="memmove(a + 1, a, 3 * sizeof(int))  ※重なっている">
1 2 3 4 _ # 配列 a
1 2 3 3 4 # 後ろから順に動かす（元のデータを壊さない）
1 1 2 3 4 # 全部 1 つ後ろへ移った
</div>

## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  int a[5] = {1, 2, 3, 4, 5};
  std::memmove(a + 1, a, 3 * sizeof(int));  // 重なっていても正しくコピーされる
  std::println("{} {} {} {} {}", a[0], a[1], a[2], a[3], a[4]);
}
```

```text title="実行結果"
1 1 2 3 5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| バッファの先頭を消して、残りを前へ詰める | `memmove(buf, buf + n, size - n)` |

## よくあるミス

??? failure "重なるのに memcpy を使う"
    未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`memcpy`](memcpy.md) | 重ならないとき |
| [`std::ranges::copy_backward`](../../algorithms/copy_backward.md) | 型を意識した版 |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 重なってもよいコピー
    - [x] 詰める・ずらすのに使う
    - [x] トリビアルな型だけ

## 関連ページ

- [cpprefjp: memmove](https://cpprefjp.github.io/reference/cstring/memmove.html)
- [cppreference: memmove](https://en.cppreference.com/w/cpp/string/byte/memmove)
