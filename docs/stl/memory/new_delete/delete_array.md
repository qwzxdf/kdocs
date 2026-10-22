---
title: delete[]
summary: "new[] で確保した配列を解放する。"
order: 900
group: new / delete まわり
tags:
  - メモリ
---

# delete[]

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <new>`
</div>

`new T[n]` で確保した配列は、必ず `delete[] p` で解放します。`delete p`（`[]` なし）だと、先頭の 1 個のデストラクタしか呼ばれず、未定義動作です。配列の大きさはポインタからは取れませんが、`delete[]` が内部で覚えている個数ぶんのデストラクタを呼びます。ほぼ使わず、`std::vector` や `std::unique_ptr<T[]>` を使います。

!!! tip "ポイント"
    - `new[]` と必ず対にする。
    - `delete`（`[]` なし）で消すと未定義動作。
    - `nullptr` に使っても安全。

!!! info "このページを読む前に"
    [`new[]`](new_array.md) を先に読んでください。

## 関数の詳しい説明

### delete[] {#delete_array}

```cpp
void operator delete[](void* ptr) noexcept;  // delete[] p; の中身
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | T* | `new[]` で確保したポインタ |

- 戻り値: なし
- 計算量: O(要素数)


## 実際に動かしてみる

```cpp
#include <print>

struct Tracer {
  static inline int alive = 0;
  Tracer() { ++alive; }
  ~Tracer() { --alive; }
};

int main() {
  Tracer* p = new Tracer[3];
  std::println("{}", Tracer::alive);
  delete[] p;
  std::println("{}", Tracer::alive);
}
```

```text title="実行結果"
3
0
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| （古い C++ のコードの保守） | `delete[] p;` |

## よくあるミス

??? failure "`delete` で消す"
    配列を `delete`（`[]` なし）で消すと未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`new[]`](new_array.md) | 確保する |
| [`std::unique_ptr<T[]>`](../../utilities/unique_ptr.md) | 自動で解放 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] new[] で確保した配列を消す
    - [x] 必ず delete[]
    - [x] unique_ptr<T[]> を使う

## 関連ページ

- [cpprefjp: delete[]](https://cpprefjp.github.io/reference/new/operator_delete.html)
- [cppreference: delete[]](https://en.cppreference.com/w/cpp/memory/delete_array)
