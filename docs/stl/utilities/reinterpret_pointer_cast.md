---
title: std::reinterpret_pointer_cast
summary: "shared_ptr の指す先を、reinterpret_cast で別の型に見せる（持ち主は共有）。"
order: 900
tags:
  - ユーティリティ
---

# std::reinterpret_pointer_cast

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <memory>`
</div>

`std::shared_ptr<char>` で確保したバイト列を、`std::shared_ptr<int>` として扱いたい、といった場面で、ビット列の解釈を変える変換が `std::reinterpret_pointer_cast<T>(sp)` です。`reinterpret_cast` の `shared_ptr` 版で、所有権を共有したまま、別の型として見られるようにします。C++17 から使えます。

!!! tip "ポイント"
    - 関係のない型どうしの変換。ビット列をそのまま別の型として読む
    - 所有権を共有する。参照カウントが増える
    - アライメントと別名規則（strict aliasing）を、自分で守る
    - 使う場面は限られる。バイト バッファの扱いなど

!!! info "このページを読む前に"
    [`std::static_pointer_cast`](static_pointer_cast.md) を先に読んでください。

## 関数の詳しい説明

### std::reinterpret_pointer_cast {#reinterpret_pointer_cast}

<span class="ver ver-17">C++17</span>

```cpp
template <class T, class U>
std::shared_ptr<T> reinterpret_pointer_cast(const std::shared_ptr<U>& r) noexcept;
```

`reinterpret_cast<T*>(r.get())` の結果を、`r` と所有権を共有する `shared_ptr` として返します。

変換は、メモリの中身をそのまま読み替えるだけです。変換先の型のアライメントを満たしていない位置を指すと、未定義動作です。また、別の型として読み書きすることは、C++ の別名規則（strict aliasing）に違反する場合があります。`unsigned char`、`char`、`std::byte` を経由する読み書きは、例外として許されます。

`static_pointer_cast` で足りる変換（継承の上下、`void*` との変換）には、`reinterpret_pointer_cast` を使いません。

## 実際に動かしてみる

```cpp
#include <cstddef>
#include <memory>
#include <print>

int main() {
  // バイト列として確保したものを、別の型の shared_ptr として共有する
  std::shared_ptr<std::byte[8]> raw = std::make_shared<std::byte[8]>();
  std::shared_ptr<unsigned char> bytes = std::reinterpret_pointer_cast<unsigned char>(raw);

  bytes.get()[0] = 0x41;
  std::println("先頭のバイト: {}", static_cast<int>(bytes.get()[0]));
  std::println("use_count = {}", raw.use_count());
}
```

```text title="実行結果"
先頭のバイト: 65
use_count = 2
```

## ゲームでの使いどころ

ネットワークのパケットや、ファイルから読んだバイト列を、`shared_ptr` で所有したまま、構造体として読むような場面で使います。

## よくあるミス

??? failure "アライメントを考えずに解釈する"
    変換先の型のアライメントに満たない位置では、未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`static_pointer_cast`](static_pointer_cast.md) | 継承などの、関係のある型の変換 |
| `reinterpret_cast` | 生ポインタ版 |
| `std::bit_cast` | 値のビット列を別の型にコピーする。安全 |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::reinterpret_pointer_cast](https://cpprefjp.github.io/reference/memory/reinterpret_pointer_cast.html)
- [cppreference: std::reinterpret_pointer_cast](https://en.cppreference.com/w/cpp/memory/reinterpret_pointer_cast)
