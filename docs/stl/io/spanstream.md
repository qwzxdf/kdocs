---
title: std::spanstream
summary: "メモリ上の既存のバッファを、コピーせずにストリームとして読み書きする。"
order: 94
tags:
  - 入出力・文字列
---

# std::spanstream

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <spanstream>`
</div>

`std::spanstream`（と `ispanstream`、`ospanstream`）は、**すでにあるメモリ上のバッファを、コピーも確保もせずに、ストリームとして読み書きする**クラスです。`stringstream` は内部で文字列を確保しますが、こちらは渡されたバッファをそのまま使います。固定長のバッファに書式つきで書き込みたいとき（`snprintf` の代わり）に向きます。

!!! tip "ポイント"
    - `std::ospanstream out(buffer);` で、`buffer` に書き込む。
    - メモリの確保が起きない。
    - `span()` で、書き込んだ範囲を取り出せる。

!!! info "このページを読む前に"
    - [stl/index.md](../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### std::spanstream {#spanstream}

```cpp
class ospanstream : public std::ostream {
 public:
  explicit ospanstream(std::span<char> buffer);
  std::span<char> span() const noexcept;
};
```

- 戻り値: （クラス）
- 計算量: O(出力量)

```cpp
#include <print>
#include <span>
#include <spanstream>
#include <string_view>

int main() {
  char buffer[32];
  std::ospanstream out{std::span<char>(buffer)};
  out << "HP " << 45 << '/' << 120;   // buffer に直接書き込む（確保なし）

  std::println("{}", std::string_view(out.span().data(), out.span().size()));
}
```

```text title="実行結果"
HP 45/120
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 固定長のバッファに、確保なしで書式つきの文字列を作る | `std::ospanstream out(buffer);` |

## よくあるミス

??? failure "バッファを超えて書く"
    あふれた分は書き込まれず、`failbit` が立ちます。大きさを余裕を持って決めます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ostringstream`](ostringstream.md) | 確保する版 |
| [`std::format_to_n`](../utilities/format_to.md) | 型安全な代わり |

## コンパイラ対応

C++23 の機能です。GCC 12 / MSVC 19.33 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 既存のバッファをストリームにする
    - [x] 確保が起きない
    - [x] C++23

## 関連ページ

- [cpprefjp: std::spanstream](https://cpprefjp.github.io/reference/spanstream/basic_ospanstream.html)
- [cppreference: std::spanstream](https://en.cppreference.com/w/cpp/io/basic_spanstream)
