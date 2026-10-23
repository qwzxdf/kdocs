---
title: va_list
summary: "引数の数が決まっていない関数（C 風の可変長引数）を書く。"
order: 99
tags:
  - 入出力・文字列
---

# va_list

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cstdarg>`
</div>

`va_list` は、**引数の数が決まっていない C 風の関数（`printf` のような）の、引数を取り出すための仕組み**です。`va_start`、`va_arg`、`va_end` の 3 つのマクロで取り出します。**型の安全がなく、引数の数も分からない**ので、新しいコードでは、可変引数テンプレート（`template <class... Args>`）を使います。

!!! tip "ポイント"
    - 引数の数や型は、呼ぶ側と受ける側で約束しておく必要がある。
    - 型の安全がない。間違えると未定義動作。
    - 新しいコードでは可変引数テンプレート。

!!! info "このページを読む前に"
    - [stl/index.md](../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### va_list {#cstdarg}

```cpp
va_list args;
va_start(args, last_named_param);
T value = va_arg(args, T);
va_end(args);
```

- 戻り値: （マクロ）
- 計算量: O(1)

```cpp
#include <cstdarg>
#include <print>

// 最初の引数 count に続く count 個の int を合計する
int Sum(int count, ...) {
  va_list args;
  va_start(args, count);
  int total = 0;
  for (int i = 0; i < count; ++i) {
    total += va_arg(args, int);
  }
  va_end(args);
  return total;
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
| 古いコードの読解（ログ関数など） | 可変引数テンプレートや `std::format` に置き換える |

## よくあるミス

??? failure "個数と実際の引数が合わない"
    余計に読むと未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::format`](../utilities/format.md) | 型安全な書式つき出力 |
| `template <class... Args>` | 可変引数テンプレート |

## コンパイラ対応

C 由来の機能です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] C 風の可変長引数
    - [x] 型の安全がない
    - [x] 新しいコードはテンプレート

## 関連ページ

- [cpprefjp: va_list](https://cpprefjp.github.io/reference/cstdarg/va_list.html)
- [cppreference: va_list](https://en.cppreference.com/w/cpp/utility/variadic/va_list)
