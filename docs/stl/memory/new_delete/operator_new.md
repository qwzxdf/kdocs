---
title: operator new / operator delete
summary: "メモリの確保・解放だけを行う関数（new 式の内部で使われる）。"
order: 8
group: new / delete まわり
tags:
  - メモリ
---

# operator new / operator delete

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <new>`
</div>

`operator new` と `operator delete` は、**メモリの確保と解放だけを行う関数**です。`new` 式は、これで確保してからコンストラクターを呼びます。自作のクラスやグローバルで置き換えると、すべての `new` のメモリ管理を変えられます（メモリ計測、独自アロケーター）。

!!! tip "ポイント"
    - 置き換えると、プログラム全体の `new` / `delete` に影響する。
    - メモリリークの追跡、独自アロケーターの導入に使える。
    - 自作するときは、サイズつきの `delete` や配列版も用意する。

!!! info "このページを読む前に"
    [ポインタ](../../../basics/pointer.md) が分かると読みやすいです。

## 関数の詳しい説明

### operator new / operator delete {#operator_new data-toc-label="operator new と operator delete"}

```cpp
void* operator new(std::size_t size);
void* operator new(std::size_t size, std::align_val_t alignment);   // C++17
void* operator new(std::size_t size, const std::nothrow_t&) noexcept;
void  operator delete(void* p) noexcept;
void  operator delete(void* p, std::size_t size) noexcept;          // サイズ付き（C++14）
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `size` | `std::size_t` | 確保するバイト数 |
| `alignment` | `std::align_val_t` | 置き場所の約束 |
| `p` | `T*` | 解放するポインタ |

- 戻り値: 確保した領域の先頭（コンストラクタは呼ばれない）
- `new` 式の「確保の部分」だけです。普通は `malloc` のような動きをします
- <strong>差し替えられます。</strong> ゲームのメモリ計測や、全体のアロケータ変更に使います。

```cpp
// グローバルの new をすべて差し替える（プロジェクトに 1 つだけ）
void* operator new(std::size_t size) {
  g_allocated_bytes += size;
  if (void* p = std::malloc(size)) return p;
  throw std::bad_alloc();
}
void operator delete(void* p) noexcept { std::free(p); }
```

- **クラスごとの `operator new`** も書けます。`class Bullet { static void* operator new(std::size_t); ... };` とすると、`new Bullet` のときだけ、そのクラス用のプールから取れます。
- 差し替えるときは、`new` と `delete` の**両方**を同じ方針で差し替えます（片方だけだと、別のところから確保したものを解放してしまいます）

## 実際に動かしてみる

```cpp
#include <new>
#include <print>

int main() {
  void* p = ::operator new(16);  // メモリを確保するだけ（コンストラクターは呼ばない）
  ::operator delete(p);
  std::println("OK");
}
```

```text title="実行結果"
OK
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| メモリ確保の回数・量を計測する | グローバルの `operator new` を置き換える |

## よくあるミス

??? failure "一部だけ置き換える"
    `new` と `delete` の組を必ず両方置き換えます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`malloc`](../malloc.md) | 置き換えた operator new の中身に使う |
| [`std::pmr`](../pmr.md) | コンテナ単位でリソースを切り替える |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 確保・解放だけの関数
    - [x] 置き換えて計測・独自管理
    - [x] 組で置き換える

## 関連ページ

- [cpprefjp: operator new / operator delete](https://cpprefjp.github.io/reference/new/operator_new.html)
- [cppreference: operator new / operator delete](https://en.cppreference.com/w/cpp/memory/new/new/operator_new)
