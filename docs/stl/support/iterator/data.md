---
title: std::data
summary: "先頭の要素へのポインターを返す（配列にも使える）。"
order: 8
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::data

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iterator>`
</div>

C の API や GPU に配列の先頭アドレスを渡すとき、`&v[0]` と書くと、空の `vector` で未定義動作になります。`std::data` は、<strong>連続したメモリの先頭へのポインター</strong>を、配列にもコンテナにも同じ書き方で返します。

!!! tip "ポイント"
    - `std::data(c)` は先頭要素へのポインターを返す
    - `vector`、`array`、`string`、配列に使える
    - 空のコンテナでも安全（有効なポインターを返す）
    - `&v[0]` より安全

!!! info "このページを読む前に"
    [イテレーターの基礎](../../../basics/iterator.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::data {#data}

<span class="ver ver-17">C++17</span>

```cpp
template <class C>
constexpr auto data(C& c) -> decltype(c.data());
template <class T, std::size_t N>
constexpr T* data(T (&array)[N]) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `c` | コンテナまたは配列 | 対象 |

コンテナなら `c.data()` を、配列ならその先頭へのポインターを返します。戻り値を使って、C の関数（`fread`、`memcpy`、Win32 API など）にバッファを渡せます。

空の `vector` に対する `&v[0]` は、範囲外の参照で未定義動作です。`v.data()` / `std::data(v)` は、空でも例外や未定義動作にならず、使える（ただし参照してはいけない）ポインターを返します。

## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};
  const int* p = std::data(v);
  std::println("先頭要素 = {}", p[0]);
  std::println("&v[0] と同じ: {}", p == &v[0]);
}
```

```text title="実行結果"
先頭要素 = 1
&v[0] と同じ: true
```

## ゲームでの使いどころ

C の API に、バッファを渡します。

```cpp
std::vector<char> buffer(1024);
fread(std::data(buffer), 1, buffer.size(), file);
```

## よくあるミス

??? failure "空のコンテナの `data()` を参照する"
    空のときは参照しません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ssize`](ssize.md) | 要素数 |
| [`begin`](begin.md) | 先頭のイテレーター |

## コンパイラ対応

C++17 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::data(c)` は先頭要素へのポインター
    - [x] 空でも安全に取れる（参照はしない）
    - [x] C の API にバッファを渡すときに使う

## 関連ページ

- [cpprefjp: std::data](https://cpprefjp.github.io/reference/iterator/data.html)
- [cppreference: std::data](https://en.cppreference.com/w/cpp/iterator/data)
