---
title: setjmp
summary: "いまの実行位置を記録する（あとで longjmp で戻れる）。"
order: 900
tags:
  - 入出力・文字列
---

# setjmp

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <csetjmp>`
</div>

「ここへあとで戻ってきたい」という実行位置を記録するのが `setjmp` です。最初は 0 を返し、あとで `longjmp` で戻ってくると、`longjmp` に渡された値（0 以外）を返します。C のエラー処理で使われた仕組みです。C++ ではデストラクタが呼ばれず危険なので、例外を使います。

!!! tip "ポイント"
    - `setjmp(env)` が位置を記録する（最初は 0 を返す）。
    - `longjmp` で戻ってくると、0 以外の値を返す。
    - C++ では例外を使う。

!!! info "このページを読む前に"
    [`<csetjmp>`](csetjmp.md) の概要を先に読んでください。

## 関数の詳しい説明

### setjmp {#setjmp}

```cpp
int setjmp(jmp_buf env);  // マクロ
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `env` | jmp_buf | 位置を保存する場所 |

- 戻り値: 記録したときは 0、`longjmp` で戻ってきたときは、その値
- 計算量: O(1)


## 実際に動かしてみる

```cpp
#include <csetjmp>
#include <print>

std::jmp_buf g_env;

int main() {
  if (setjmp(g_env) == 0) {
    std::longjmp(g_env, 1);  // setjmp の場所へ戻る
  } else {
    std::println("戻ってきた");
  }
}
```

```text title="実行結果"
戻ってきた
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| C のライブラリのエラー処理の理解 | `longjmp` が使われていたら、C++ の境界を越えない |

## よくあるミス

??? failure "デストラクタが呼ばれない"
    間にあるオブジェクトのデストラクタは呼ばれず、リソースがリークします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`longjmp`](longjmp.md) | 記録した位置に戻る |
| [`std::exception`](../support/exceptions/exception.md) | 安全な代わり |

## コンパイラ対応

C 由来の機能です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 実行位置を記録する
    - [x] 最初は 0、戻ってくると 0 以外
    - [x] C++ では例外

## 関連ページ

- [cpprefjp: setjmp](https://cpprefjp.github.io/reference/csetjmp/setjmp.html)
- [cppreference: setjmp](https://en.cppreference.com/w/cpp/utility/program/setjmp)
