---
title: std::stoull
summary: "文字列を unsigned long long に変換する（失敗すると例外）。"
order: 900
tags:
  - コンテナ
---

# std::stoull

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <string>`
</div>

`std::stoull(str)` は、文字列を `unsigned long long` に変換します。ハッシュ値や 64 ビットの ID を、16 進の文字列から読むときによく使います。

!!! tip "ポイント"
    - `unsigned long long` に変換する
    - `base` に 16 を指定して、16 進の文字列を読める
    - `"-1"` は巻き戻った巨大な値になる
    - 例外の規則は `stol` と同じ

!!! info "このページを読む前に"
    [`std::string`](string.md) を先に読んでください。

## 関数の詳しい説明

### std::stoull {#stoull}

<span class="ver ver-11">C++11</span>

```cpp
unsigned long long stoull(const std::string& str, std::size_t* pos = nullptr, int base = 10);
```

16 進のハッシュ値（`"cbf29ce484222325"` のような 16 桁）は、`stoull(s, nullptr, 16)` で読めます。`0x` の接頭辞は、`base` が 16 か 0 のとき、読み飛ばされます。

`stoul` と同じく、負の数の文字列は、エラーにならず巻き戻ります。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>

int main() {
  std::println("{}", std::stoull("18446744073709551615"));  // 64 ビットの最大値
  std::println("{:x}", std::stoull("cbf29ce484222325", nullptr, 16));
  std::println("0x つき: {}", std::stoull("0xff", nullptr, 16));
}
```

```text title="実行結果"
18446744073709551615
cbf29ce484222325
0x つき: 255
```

## ゲームでの使いどころ

アセットの ID のハッシュ値を、テキストのデータから読み込むときに使います。

## よくあるミス

??? failure "負の数を渡す"
    巻き戻ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`stoul`](stoul.md) | `unsigned long` |
| [`stoll`](stoll.md) | 符号つき 64 ビット |
| `std::from_chars` | 例外なし |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::stoull](https://cpprefjp.github.io/reference/string/stoull.html)
- [cppreference: std::stoull](https://en.cppreference.com/w/cpp/string/basic_string/stol)
