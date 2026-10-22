---
title: std::make_unique
summary: "オブジェクトを作って unique_ptr にする。普通はこれで unique_ptr を作る。"
order: 47
tags:
  - ユーティリティ
---

# std::make_unique

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-14">C++14</span>
`#include <memory>`
</div>

`std::make_unique` は、**オブジェクトを作って、それを持つ `unique_ptr` を返す**関数です。`std::unique_ptr<T>(new T(...))` と書くより短く、`new` を書かずに済み、例外にも安全です。`unique_ptr` を作るときは、まずこれを使います。

!!! tip "ポイント"
    - `new` を直接書かず、`std::make_unique<T>(コンストラクタの引数)`。
    - 配列版は `std::make_unique<T[]>(個数)`。要素は値初期化（0 など）される。
    - C++14 で追加された。C++11 では `new` を書いていた。

## 関数の詳しい説明

### std::make_unique <span class="ver ver-14">C++14</span> {#make_unique data-toc-label="std::make_unique"}

```cpp
template <class T, class... Args>
std::unique_ptr<T> make_unique(Args&&... args);

template <class T>
std::unique_ptr<T> make_unique(std::size_t size);  // T が配列 U[] のとき
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `args` | 何個でも | `T` のコンストラクタにそのまま渡す引数 |
| `size` | `std::size_t` | 配列版の要素数 |

- 戻り値: 新しく作ったオブジェクトを持つ unique_ptr
- 例外: メモリ不足なら `std::bad_alloc`

<div class="anim" data-label="auto p = std::make_unique<Enemy>()">
_ # p は空
+A # Enemy を作り、p が所有する
</div>

```cpp
#include <memory>
#include <print>

struct Vec2 {
  float x;
  float y;
};

int main() {
  auto pos = std::make_unique<Vec2>(1.0f, 2.0f);
  std::println("({}, {})", pos->x, pos->y);
}
```

```text title="実行結果"
(1, 2)
```

!!! note "実際は"
    `new` を書く場面は、ほぼすべて `make_unique` に置き換えられます。

### std::make_unique_for_overwrite <span class="ver ver-20">C++20</span> {#make_unique_for_overwrite data-toc-label="std::make_unique_for_overwrite"}

```cpp
template <class T>
unique_ptr<T> make_unique_for_overwrite();
template <class T>
unique_ptr<T> make_unique_for_overwrite(size_t n);  // T[] 用
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `n` | size_t | 配列の要素数（`T[]` のとき） |

- 戻り値: `unique_ptr<T>`
- 計算量: 確保 1 回 + 初期化（なし）

`make_unique<int[]>(n)` は全要素を 0 で値初期化します。`make_unique_for_overwrite` は**初期化せず**確保だけします（`int` なら中身は不定）。あとで全部上書きすると分かっている大きな配列で、0 埋めの時間を省けます。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 敵・弾・コンポーネントの生成 | `enemies.push_back(std::make_unique<Slime>());` |

## よくあるミス

??? failure "make_unique で作れないもの"
    デリーターを指定したいときは `std::unique_ptr<T, Deleter>(new T, deleter)` と書きます。

??? failure "初期化しない版が欲しい"
    `std::make_unique_for_overwrite<T[]>(n)`（C++20）は初期化を省略します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::make_shared`](make_shared.md) | `shared_ptr` を作る |
| [`std::unique_ptr`](unique_ptr.md) | 本体 |

## コンパイラ対応

C++14 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `unique_ptr` は `make_unique` で作る
    - [x] `new` を直接書かない
    - [x] C++14

## 関連ページ

- [cpprefjp: std::make_unique](https://cpprefjp.github.io/reference/memory/make_unique.html)
- [cppreference: std::make_unique](https://en.cppreference.com/w/cpp/memory/unique_ptr/make_unique)
