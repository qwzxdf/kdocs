---
title: new[] と delete[]
summary: "配列をヒープに作り、解放する式。"
order: 3
group: new / delete まわり
tags:
  - メモリ
---

# new[] と delete[]

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <new>`
</div>

`new[]` は、**要素が複数の配列をヒープに作る**式で、解放は `delete[]` です。要素ごとにコンストラクター・デストラクターが呼ばれます。配列の大きさは実行時に決められますが、`std::vector` のほうが安全で便利です。

!!! tip "ポイント"
    - `new[]` の解放は **`delete[]`**。`delete` ではない。
    - 大きさは覚えていない。自分で管理する。
    - 普通は `std::vector` や `std::make_unique<T[]>`。

!!! info "このページを読む前に"
    [ポインタ](../../../basics/pointer.md) が分かると読みやすいです。

## 関数の詳しい説明

### new[] / delete[] {#new_array data-toc-label="new[] と delete[]"}

```cpp
T* p = new T[n];       // n 個。各要素はデフォルトコンストラクタ
T* p = new T[n]{};     // 値で初期化（基本型は 0）
delete[] p;            // 配列は必ず delete[]
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `n` | `size_t` | 要素の数 |

- 戻り値: 先頭の要素へのポインタ
- **`delete[]` で消す**ことが大事です。`delete`（`[]` なし）だと、先頭の 1 個のデストラクタしか呼ばれず、未定義動作です
- 配列の大きさはポインタからは取れません。自分で覚えておく必要があります
- ほぼ使いません。`std::vector<T>` や `std::unique_ptr<T[]>`、`std::array<T, N>` を使います

## 実際に動かしてみる

```cpp
#include <print>

int main() {
  int* a = new int[3]{1, 2, 3};
  std::println("{}", a[0] + a[1] + a[2]);
  delete[] a;  // new[] には delete[]
}
```

```text title="実行結果"
6
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 古いコードの読解 | `int* a = new int[n]; ... delete[] a;` |

## よくあるミス

??? failure "delete と delete[] を取り違える"
    未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::vector`](../../containers/vector.md) | 大きさを覚えていて安全 |
| [`std::make_unique`](../../utilities/make_unique.md) | `make_unique<T[]>(n)` |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 配列を作る・解放する
    - [x] `new[]` には `delete[]`
    - [x] `vector` を使う

## 関連ページ

- [cpprefjp: new[] と delete[]](https://cpprefjp.github.io/reference/new/new.html)
- [cppreference: new[] と delete[]](https://en.cppreference.com/w/cpp/memory/new/new)
