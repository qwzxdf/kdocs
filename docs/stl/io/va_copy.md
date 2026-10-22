---
title: va_copy
summary: "可変引数の読み取り状態をコピーする。"
order: 900
tags:
  - 入出力・文字列
---

# va_copy

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdarg>`
</div>

`va_list` は、ふつうにコピーできません。同じ引数を 2 回読みたいとき、`va_copy(dst, src)` で複製します。複製した方にも、`va_end` が必要です。

!!! tip "ポイント"
    - C の可変長引数の仕組み。
    - 型の安全性がない（型を間違えると未定義動作）。
    - 新しいコードでは、可変長テンプレート（`Args&&... args`）を使う。

!!! info "このページを読む前に"
    [`<cstdarg>`](cstdarg.md) の概要を先に読んでください。

## 関数の詳しい説明

### va_copy {#va_copy}

```cpp
#define va_copy(/* ... */)
```

- 戻り値: （マクロ）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cstdarg>
#include <print>

int SumTwice(int count, ...) {
  va_list ap, ap2;
  va_start(ap, count);
  va_copy(ap2, ap);
  int sum = 0;
  for (int i = 0; i < count; ++i) sum += va_arg(ap, int);
  for (int i = 0; i < count; ++i) sum += va_arg(ap2, int);
  va_end(ap2);
  va_end(ap);
  return sum;
}

int main() {
  std::println("{}", SumTwice(2, 1, 2));
}
```

```text title="実行結果"
6
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | C の API に合わせた可変引数の関数を書く |

## よくあるミス

??? failure "型を間違えて取り出す"
    `va_arg(ap, double)` で `int` を渡されたものを取ると、未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| 可変長テンプレート | 型安全な書き方 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 可変引数の読み取り状態をコピーする
    - [x] C の可変長引数の仕組み
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: va_copy](https://cpprefjp.github.io/reference/cstdarg/va_copy.html)
- [cppreference: va_copy](https://en.cppreference.com/w/cpp/utility/variadic/va_copy)
