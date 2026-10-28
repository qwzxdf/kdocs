---
title: 配置 new（placement new）
summary: "用意したメモリの上に、オブジェクトを作る。"
order: 5
group: new / delete まわり
tags:
  - メモリ
---

# 配置 new（placement new）

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <new>`
</div>

**配置 new** は、**確保済みのメモリの上にオブジェクトを作る**書き方です。`new (ptr) T(args)` と書きます。メモリの確保はせず、コンストラクターだけを呼びます。自作のアロケーター、メモリプール、`std::vector` の内部で使われています。

!!! tip "ポイント"
    - メモリは自分で用意する（サイズ・アラインメントに注意）。
    - 壊すときは、`delete` ではなく、**デストラクターを直接呼ぶ**（`p->~T()`）。
    - C++20 の `std::construct_at` が簡単で安全。

!!! info "このページを読む前に"
    [ポインタ](../../../basics/pointer.md) が分かると読みやすいです。

## 関数の詳しい説明

### 配置 new {#placement_new data-toc-label="配置 new"}

```cpp
void* place = /* 確保済みの領域 */;
T* p = new (place) T(args...);   // place の場所に T を作る
p->~T();                         // 後始末は、デストラクタを自分で呼ぶ
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `place` | `void*` | オブジェクトを作る場所。**大きさと、アラインメントが足りている**必要がある |
| `args...` | `Args&&...` | コンストラクタの引数 |

- 戻り値: 作ったオブジェクトへのポインタ
- **メモリは確保しません**。すでにある領域の中でコンストラクタを呼ぶだけです
- 後始末は `delete` ではなく、**デストラクタを直接呼ぶ**（`p->~T();`）。そのあと、領域は自分で返します。
- コンテナ、プール、アロケータの内部で使われています。通常のコードでは不要です

```cpp
#include <cstddef>
#include <new>
#include <print>

struct Bullet {
  Bullet(float x, float y) : x(x), y(y) {}
  float x, y;
};

int main() {
  // Bullet 2 個ぶんの領域を先にまとめて確保しておく（まだ Bullet ではない）
  alignas(Bullet) std::byte storage[sizeof(Bullet) * 2];

  Bullet* a = new (storage) Bullet(1.0f, 2.0f);                       // 1 個目の場所
  Bullet* b = new (storage + sizeof(Bullet)) Bullet(3.0f, 4.0f);      // 2 個目の場所
  std::println("{} {} / {} {}", a->x, a->y, b->x, b->y);

  a->~Bullet();  // デストラクタを呼ぶ（領域 storage は配列なので、自動で戻る）
  b->~Bullet();
}
```

```text title="実行結果"
1 2 / 3 4
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| メモリプールの上にオブジェクトを作る | `new (slot) Enemy(args);` |

## よくあるミス

??? failure "delete で解放する"
    配置 new で作ったものを `delete` するのは未定義動作です。デストラクターを直接呼びます。

??? failure "アラインメントが足りない"
    メモリが `T` に必要な境界にそろっていないと未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`construct_at`](construct_at.md) | 配置 new の安全な書き方 |
| [`destroy_at`](destroy_at.md) | デストラクターを呼ぶ |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 用意したメモリの上に作る
    - [x] 壊すのはデストラクターの直接呼び出し
    - [x] `construct_at` が簡単

## 関連ページ

- [cpprefjp: 配置 new（placement new）](https://cpprefjp.github.io/reference/new/new.html)
- [cppreference: 配置 new（placement new）](https://en.cppreference.com/w/cpp/memory/new/new)
