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

`new T[n]` で作った配列は、`delete[] p` で解放します。`delete p` と書くと、先頭の 1 要素だけにデストラクターを呼ぶ（またはメモリ管理が壊れる）ので、未定義動作です。

!!! tip "ポイント"
    - `new[]` で確保したものは、必ず `delete[]` で解放する
    - 全要素のデストラクターを、逆順に呼ぶ
    - `nullptr` に使っても安全（何もしない）
    - スマート ポインタ（`unique_ptr<T[]>`）なら自動で `delete[]`

!!! info "このページを読む前に"
    [`new[]`](new_array.md) を先に読んでください。

## 関数の詳しい説明

### delete[] 式 {#delete_array}

```cpp
delete[] p;
```

`delete[]` は、配列の要素数を実装の記録から得て、末尾の要素から順にデストラクターを呼び、最後に `operator delete[]` でメモリを返します。

要素のデストラクターが自明な型（`int` など）では、デストラクターの呼び出しは省かれますが、`delete` と取り違えると、メモリ管理の記録がずれて、壊れることがあります。

`std::unique_ptr<T[]>` は、`T[]` の特殊化で、デストラクターが `delete[]` を呼びます。`unique_ptr<T>` に `new T[n]` を渡すと、`delete` が呼ばれて、未定義動作になります。

## 実際に動かしてみる

```cpp
#include <memory>
#include <new>
#include <print>

struct Tracer {
  static inline int alive = 0;
  Tracer() { ++alive; }
  Tracer(const Tracer&) { ++alive; }
  Tracer(Tracer&&) noexcept { ++alive; }
  ~Tracer() { --alive; }
};

struct Item {
  Item() { ++Tracer::alive; }
  ~Item() { --Tracer::alive; }
};

int main() {
  Item* items = new Item[4];
  std::println("作った: {}", Tracer::alive);
  delete[] items;
  std::println("全部壊した: {}", Tracer::alive);

  int* none = nullptr;
  delete[] none;  // nullptr は安全
  std::println("nullptr でも問題ない");
}
```

```text title="実行結果"
作った: 4
全部壊した: 0
nullptr でも問題ない
```

## ゲームでの使いどころ

古いコードのメモリ リークや、二重解放の調査で、`new[]` / `delete[]` の対応を確かめます。

## よくあるミス

??? failure "delete で解放する"
    先頭の要素だけが壊されるなど、未定義動作です。

??? failure "二重に解放する"
    `delete[]` したあと、ポインタを `nullptr` にしないと、二重解放の危険があります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`new[]`](new_array.md) | 対になる確保 |
| `std::unique_ptr<T[]>` | 自動で `delete[]` |

## コンパイラ対応

C++98 から使えます。

## 関連ページ

- [cpprefjp: delete[]](https://cpprefjp.github.io/reference/new/operator_delete.html)
- [cppreference: delete[]](https://en.cppreference.com/w/cpp/memory/delete_array)
