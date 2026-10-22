---
title: va_end
summary: "可変引数の読み取りを終える。"
order: 900
tags:
  - 入出力・文字列
---

# va_end

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdarg>`
</div>

`va_start` で始めた読み取りの後始末です。関数を抜ける前に、必ず対応する `va_end` を呼びます。

!!! tip "ポイント"
    - C の可変長引数の仕組み。
    - 型の安全性がない（型を間違えると未定義動作）。
    - 新しいコードでは、可変長テンプレート（`Args&&... args`）を使う。

!!! info "このページを読む前に"
    [`<cstdarg>`](cstdarg.md) の概要を先に読んでください。

## 関数の詳しい説明

### va_end {#va_end}

```cpp
#define va_end(/* ... */)
```

- 戻り値: （マクロ）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cstdarg>
#include <print>

int Sum(int count, ...) {
  va_list ap;
  va_start(ap, count);
  int sum = 0;
  for (int i = 0; i < count; ++i) sum += va_arg(ap, int);
  va_end(ap);
  return sum;
}

int main() {
  std::println("{}", Sum(3, 1, 2, 3));
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
    - [x] 可変引数の読み取りを終える
    - [x] C の可変長引数の仕組み
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: va_end](https://cpprefjp.github.io/reference/cstdarg/va_end.html)
- [cppreference: va_end](https://en.cppreference.com/w/cpp/utility/variadic/va_end)
