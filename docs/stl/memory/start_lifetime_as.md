---
title: std::start_lifetime_as
summary: "バイト列を、そのままの値で指定した型のオブジェクトとして使い始める。"
order: 900
tags:
  - メモリ
---

# std::start_lifetime_as

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <memory>`
</div>

ファイルやネットワークから読んだバイト列の上に、構造体としてアクセスしたい。`reinterpret_cast` でキャストして読むのは、厳密には、その型のオブジェクトがそこにないので、未定義動作です。C++23 の `std::start_lifetime_as<T>(p)` は、「`p` の領域に、`T` のオブジェクトの寿命を、中身を壊さずに始める」関数で、バイト列を型として扱う正式な方法です。

!!! tip "ポイント"
    - バイト列の上に、`T` のオブジェクトが存在することにする
    - 領域の中身は変わらない（初期化もしない）
    - `T` は、暗黙の寿命を持てる型（トリビアルな型）
    - C++23

!!! info "このページを読む前に"
    [`std::allocator`](allocator.md) など、アロケーターの基本を先に読んでください。

## 関数の詳しい説明

### std::start_lifetime_as {#start_lifetime_as}

<span class="ver ver-23">C++23</span>

```cpp
template <class T> T* start_lifetime_as(void* p) noexcept;
template <class T> const T* start_lifetime_as(const void* p) noexcept;
template <class T> T* start_lifetime_as_array(void* p, std::size_t n) noexcept;
```

`p` の指す領域は、`T` の大きさとアライメントを満たし、`T` のオブジェクトの表現として有効なバイト列を持っているべきです。

配置 new で `T` を作ると、値が初期化される（または不定になる）ため、バイト列の中身を保てません。`start_lifetime_as` だけが、中身を保ったまま、寿命を始めます。

実装は、多くの場合、ポインターを返すだけで、実行時の処理がありません。型の寿命の規則に従うためのものです。

手元の MSVC（Visual Studio 2026）では、まだ使えません。従来は、`std::memcpy` で構造体にコピーするのが、安全な方法でした。

## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

struct Header {
  int magic;
  int version;
};

int main() {
  // C++23 では std::start_lifetime_as<Header>(bytes) と書ける。
  // ここでは、従来の安全な方法の memcpy で読む。
  alignas(Header) unsigned char bytes[sizeof(Header)];
  const Header src{0x4D41474B, 2};
  std::memcpy(bytes, &src, sizeof(Header));

  Header h;
  std::memcpy(&h, bytes, sizeof(Header));
  std::println("magic={:#x} version={}", h.magic, h.version);
}
```

```text title="実行結果"
magic=0x4d41474b version=2
```

## ゲームでの使いどころ

ファイルの先頭のヘッダーや、ネットワークのパケットを、構造体として読むときに使います。

## よくあるミス

??? failure "reinterpret_cast で読む"
    厳密には未定義動作です。`start_lifetime_as` か `memcpy` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`launder`](new_delete/launder.md) | 作り直したオブジェクトを指す |
| [`construct_at`](new_delete/construct_at.md) | 値を初期化して作る |
| `std::bit_cast` | 値を別の型にコピーする |

## コンパイラ対応

C++23 から使えます。手元の MSVC では未対応で、`memcpy` で確かめました。

## 関連ページ

- [cpprefjp: std::start_lifetime_as](https://cpprefjp.github.io/reference/memory/start_lifetime_as.html)
- [cppreference: std::start_lifetime_as](https://en.cppreference.com/w/cpp/memory/start_lifetime_as)
