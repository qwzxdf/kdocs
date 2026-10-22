---
title: std::longjmp
summary: "setjmp で記録した位置へ、一気に戻る。"
order: 900
tags:
  - 入出力・文字列
---

# std::longjmp

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <csetjmp>`
</div>

`setjmp` で記録した位置まで、途中の関数を全部飛ばして戻ります。途中のオブジェクトのデストラクタは呼ばれないので、C++ では例外（`throw` / `catch`）を使うのが安全です。

!!! tip "ポイント"
    - `setjmp` で記録した位置に戻る。
    - 戻らない関数（`[[noreturn]]`）。
    - `value` が 0 だと、`setjmp` は 1 を返す。

!!! info "このページを読む前に"
    [`<csetjmp>`](csetjmp.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::longjmp {#longjmp}

```cpp
[[noreturn]] void longjmp(jmp_buf env, int value);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `env` | jmp_buf | `setjmp` で記録した場所 |
| `value` | int | `setjmp` が返す値（0 なら 1 になる） |

- 戻り値: 戻らない
- 計算量: O(1)


## 実際に動かしてみる

```cpp
#include <csetjmp>
#include <print>

std::jmp_buf g_env;

void Fail() {
  std::longjmp(g_env, 2);
}

int main() {
  int r = setjmp(g_env);
  if (r == 0) {
    Fail();
  } else {
    std::println("エラー {}", r);
  }
}
```

```text title="実行結果"
エラー 2
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| C のライブラリのエラー処理の理解 | C のライブラリが `longjmp` でエラーを返す設計のとき、境界を越えないようにする |

## よくあるミス

??? failure "C++ のオブジェクトがある関数をまたぐ"
    デストラクタが呼ばれずリークします。例外を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`setjmp`](setjmp.md) | 位置を記録する |

## コンパイラ対応

C 由来の機能です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 記録した位置へ飛ぶ
    - [x] 戻らない
    - [x] デストラクタが呼ばれない

## 関連ページ

- [cpprefjp: std::longjmp](https://cpprefjp.github.io/reference/csetjmp/longjmp.html)
- [cppreference: std::longjmp](https://en.cppreference.com/w/cpp/utility/program/longjmp)
