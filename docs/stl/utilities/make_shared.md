---
title: std::make_shared
summary: "オブジェクトを作って shared_ptr にする。普通はこれで shared_ptr を作る。"
order: 51
tags:
  - ユーティリティ
---

# std::make_shared

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">C++11</span>
`#include <memory>`
</div>

`std::make_shared` は、**オブジェクトを作って、それを持つ `shared_ptr` を返す**関数です。`std::shared_ptr<T>(new T(...))` と書くより、短くて、例外に対して安全で、メモリの確保も 1 回で済んで速くなります。`shared_ptr` を作るときは、まずこれを使います。

!!! tip "ポイント"
    - `new` を直接書かず、`std::make_shared<T>(コンストラクタの引数)`。
    - 本体と参照カウントを**1 回のメモリ確保**で作るので、速い。
    - 自作のデリーターを渡したいときや、配列を指定したいときは `shared_ptr<T>(new ..., deleter)` を使う。

## 関数の詳しい説明

### std::make_shared {#make_shared}

```cpp
template <class T, class... Args>
std::shared_ptr<T> make_shared(Args&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `args` | 何個でも | `T` のコンストラクタ引数 |

- オブジェクトと参照カウントを**1 回の確保**でまとめて作ります（`new` してから shared_ptr に渡すより速い）

<div class="anim" data-label="auto p = std::make_shared<Enemy>()">
_ # p は空
+A:1 # 作って、参照数は 1
</div>

### std::make_shared_for_overwrite <span class="ver ver-20">C++20</span> {#make_shared_for_overwrite data-toc-label="std::make_shared_for_overwrite"}

```cpp
template <class T>
shared_ptr<T> make_shared_for_overwrite();
template <class T>
shared_ptr<T> make_shared_for_overwrite(size_t n);  // T[] 用
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `n` | size_t | 配列の要素数（`T[]` のとき） |

- 戻り値: `shared_ptr<T>`
- 計算量: 確保 1 回 + 初期化（なし）

`make_shared<int[]>(n)` は全要素を 0 で値初期化します。`make_shared_for_overwrite` は**初期化せず**確保だけします。あとで全部上書きする大きな配列で、0 埋めを省くために使います。

## 実際に動かしてみる

```cpp
#include <memory>
#include <print>

int main() {
  auto p = std::make_shared<int>(5);
  auto q = p;   // 持ち主が 2 人になる
  std::println("{} {}", *p, p.use_count());
}
```

```text title="実行結果"
5 2
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 共有するリソース（テクスチャ、メッシュ）の作成 | `auto tex = std::make_shared<Texture>(path);` |

## よくあるミス

??? failure "new を直接 shared_ptr に渡す"
    `std::shared_ptr<T> p(new T(...))` は、メモリ確保が 2 回になります。例外にも弱くなります。

??? failure "make_shared で作ったものが、weak_ptr のせいで解放されない"
    `make_shared` は本体と参照カウントを同じメモリに置くので、`weak_ptr` が残っている間は、**メモリそのもの**は解放されません（デストラクターは呼ばれます）。巨大なオブジェクトでは気になる場合があります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::make_unique`](make_unique.md) | `unique_ptr` を作る |
| [`std::shared_ptr`](shared_ptr.md) | 本体 |
| [`std::allocate_shared`](allocate_shared.md) | アロケータを指定して作る |

## コンパイラ対応

C++11 から使えます。配列版（`make_shared<T[]>`）は C++20 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `shared_ptr` は `make_shared` で作る
    - [x] メモリ確保が 1 回で済む
    - [x] `new` を直接書かない

## 関連ページ

- [cpprefjp: std::make_shared](https://cpprefjp.github.io/reference/memory/make_shared.html)
- [cppreference: std::make_shared](https://en.cppreference.com/w/cpp/memory/shared_ptr/make_shared)
