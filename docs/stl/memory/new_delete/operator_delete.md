---
title: operator delete
summary: "new 式の「解放の部分」だけを行う関数（デストラクタは呼ばない）。"
order: 900
group: new / delete まわり
tags:
  - メモリ
---

# operator delete

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <new>`
</div>

`delete p` は、デストラクタを呼んでから、メモリを解放します。この**メモリの解放だけ**を担当するのが `operator delete` です。`operator new` と対にして差し替えると、メモリの使用量の計測や、独自のアロケータへの切り替えができます。

!!! tip "ポイント"
    - `operator new` と対にする。
    - `size` つきの版（C++14）は、確保した大きさが分かる。
    - 差し替えは、プロジェクトに 1 組だけ。

!!! info "このページを読む前に"
    [`operator new`](operator_new.md) を先に読んでください。

## 関数の詳しい説明

### operator delete {#operator_delete}

```cpp
void operator delete(void* p) noexcept;
void operator delete(void* p, std::size_t size) noexcept;  // サイズ付き（C++14）
void operator delete(void* p, std::align_val_t alignment) noexcept;  // C++17
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | void* | 解放するポインタ |
| `size` | size_t | 確保したバイト数（サイズ付き版） |

- 戻り値: なし
- 計算量: アロケータに依存


## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <new>
#include <print>

int g_freed = 0;

void* operator new(std::size_t size) {
  if (void* p = std::malloc(size)) return p;
  throw std::bad_alloc();
}

void operator delete(void* p) noexcept {
  ++g_freed;
  std::free(p);
}

int main() {
  int* p = new int(1);
  delete p;
  std::println("{}", g_freed);
}
```

```text title="実行結果"
1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 全体のメモリ使用量を計測する | `operator new` / `operator delete` を差し替えて、確保量を数える |

## よくあるミス

??? failure "`new` と `delete` の対応を崩す"
    差し替えるときは、`new` と `delete` の両方を、同じ方式にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`operator new`](operator_new.md) | 確保の部分 |
| [`delete`](delete.md) | delete 式 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 解放だけを行う関数
    - [x] operator new と対にする
    - [x] 差し替えて計測に使う

## 関連ページ

- [cpprefjp: operator delete](https://cpprefjp.github.io/reference/new/operator_delete.html)
- [cppreference: operator delete](https://en.cppreference.com/w/cpp/memory/new/operator_delete)
