---
title: memcpy
summary: "メモリのバイト列を、別の場所へコピーする（重なっていてはいけない）。"
order: 1
group: C の文字列・メモリ関数（<cstring>）
tags:
  - メモリ
---

# memcpy

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <cstring>`
</div>

`memcpy` は、**メモリのバイト列を別の場所へそのままコピーする**C 由来の関数です。構造体や配列を丸ごとバイト単位でコピーするときに使います。**コピー元とコピー先が重なっていると未定義動作**です（重なるなら `memmove`）。

!!! tip "ポイント"
    - 型が「トリビアルにコピーできる」ものだけに使う（`std::string` や `vector` は NG）。
    - 引数は `(コピー先, コピー元, バイト数)` の順。
    - C++ では、まず `std::copy` や代入を考える。

!!! info "このページを読む前に"
    [ポインタ](../../../basics/pointer.md) が分かると読みやすいです。

## 関数の詳しい説明

### memcpy {#memcpy}

```cpp
void* memcpy(void* dest, const void* src, std::size_t count);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `dest` | `void*` | コピー先 |
| `src` | `const void*` | コピー元 |
| `count` | `std::size_t` | コピーする**バイト数** |

- 戻り値: `dest`
- 計算量: O(count)。とても速い（CPU の命令でまとめてコピーされる）
- **`dest` と `src` が重なっていると未定義動作**です。重なる可能性があるなら `memmove` を使います
- **`dest` / `src` が `nullptr` は `count` が 0 でも未定義動作**です
- コピーする型は **trivially copyable**（コンストラクタ・デストラクタ・コピーの処理が単純なもの）に限ります。`std::string`、`std::vector`、`std::unique_ptr`、仮想関数を持つクラスは**壊れます**

<div class="anim" data-label="memcpy(dst, src, 3 * sizeof(int))">
1 2 3 4 | _ _ _ _ # src と dst
1 2 3 4 | +1 _ _ _ # 先頭から順にコピーされる
1 2 3 4 | +1 +2 +3 _ # 指定したバイト数だけ。それ以降は変わらない
</div>

## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  int src[3] = {1, 2, 3};
  int dst[3] = {};
  std::memcpy(dst, src, sizeof(src));
  std::println("{} {} {}", dst[0], dst[1], dst[2]);
}
```

```text title="実行結果"
1 2 3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 頂点バッファへ頂点配列を転送する | `memcpy(mapped, vertices, size)` |

## よくあるミス

??? failure "引数の順番を逆にする"
    `memcpy(dst, src, n)` です。`src` を先に書くと逆向きにコピーします。

??? failure "std::string や vector に使う"
    内部のポインターごとコピーされて、二重解放になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`memmove`](memmove.md) | 重なっていてもよい |
| [`std::ranges::copy`](../../algorithms/copy.md) | 型を意識したコピー |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] バイト列をコピーする
    - [x] 重なってはいけない
    - [x] 非トリビアルな型には使わない

## 関連ページ

- [cpprefjp: memcpy](https://cpprefjp.github.io/reference/cstring/memcpy.html)
- [cppreference: memcpy](https://en.cppreference.com/w/cpp/string/byte/memcpy)
