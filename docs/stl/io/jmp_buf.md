---
title: jmp_buf
summary: "setjmp が実行位置を保存する入れ物の型。"
order: 900
tags:
  - 入出力・文字列
---

# jmp_buf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <csetjmp>`
</div>

`setjmp` が「ここに戻ってくる」という位置を覚えておくには、入れ物が要ります。その型が `jmp_buf` です。戻り先のアドレス、スタックの位置、いくつかのレジスタの値が、この中に書き込まれます。`setjmp` と `longjmp` の両方に、同じ `jmp_buf` を渡します。

!!! tip "ポイント"
    - 中身は処理系ごとに違う。見ない、触らない
    - 配列型として定義されることが多く、関数に渡すと参照のように振る舞う
    - `setjmp` を呼んだ関数が終わったあとの `jmp_buf` は使えない
    - グローバル変数やメンバー変数に置く。複数のスレッドで共有しない

!!! info "このページを読む前に"
    [`<csetjmp>`](csetjmp.md) の概要と [`setjmp`](setjmp.md) を先に読んでください。

## 関数の詳しい説明

### jmp_buf {#jmp_buf}

```cpp
using jmp_buf = /* 配列型 */;
```

`jmp_buf` の大きさと中身は、処理系によって違います。x64 の MSVC では、レジスタを保存する領域として、数百バイトほどあります。中を読んだり書き換えたりしても、意味がありません。

規格が `jmp_buf` を配列型にしているので、関数の引数に渡すと、先頭のアドレスに変わります。そのため、`void Fail(jmp_buf env)` に渡した `env` は、呼び出し元の `jmp_buf` を指していて、コピーされません。`longjmp(env, 1)` が、呼び出し元に保存された内容を読めるのは、このためです。

もう 1 つ、`jmp_buf` は他の変数と同じように、コピーで使い回せるとは限りません。コピーした `jmp_buf` で `longjmp` した結果は、保証されていません。`setjmp` したその場所の変数を、そのまま `longjmp` に渡します。

保存先の寿命も問題です。`setjmp` を呼んだ関数のローカル変数に `jmp_buf` を置いたまま、その関数が終わったあとで、別の関数から `longjmp` するのは、未定義動作です。ふつうは、グローバル変数にするか、構造体のメンバーとして持たせます。

## 実際に動かしてみる

```cpp
#include <csetjmp>
#include <print>

// jmp_buf を構造体に持たせて、エラー処理をまとめる
struct ErrorContext {
  std::jmp_buf jump;
  int code = 0;
};

ErrorContext g_ctx;

void Fail(int code) {
  g_ctx.code = code;
  std::longjmp(g_ctx.jump, 1);
}

int main() {
  if (setjmp(g_ctx.jump) == 0) {
    Fail(42);
  } else {
    std::println("エラーコード {}", g_ctx.code);
  }
}
```

```text title="実行結果"
エラーコード 42
```

`longjmp` で渡せる値は 1 つの `int` だけなので、エラーの詳しい内容は、`jmp_buf` と一緒の構造体に入れておきます。C のライブラリでも、同じ作りがよく使われます。

## ゲームでの使いどころ

自分で使う場面はほとんどありません。C のライブラリが、自分の構造体の中に `jmp_buf` を持っているのを見るくらいです。その構造体を、`std::unique_ptr` などで管理しているなら、`longjmp` で飛び越えないよう、境界を小さくします。

## よくあるミス

??? failure "jmp_buf をコピーして使う"
    `jmp_buf b = a;` は配列の初期化になるので、書けません。構造体に入れてコピーすると書けますが、そのコピーに `longjmp` しても保証されません。

??? failure "ローカルの jmp_buf を持ったまま関数を出る"
    `setjmp` した関数の終了後は、その `jmp_buf` へ `longjmp` できません。寿命を考えて置き場所を決めます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`setjmp`](setjmp.md) | `jmp_buf` に記録する |
| [`longjmp`](longjmp.md) | `jmp_buf` の位置へ戻る |
| [`sig_atomic_t`](sig_atomic_t.md) | シグナルハンドラーと共有できる整数型 |

## コンパイラ対応

C 由来の型です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `jmp_buf` は、`setjmp` が実行位置を記録する入れ物
    - [x] 中身は処理系ごとに違うので、触らない
    - [x] `setjmp` した関数が終わったら、その `jmp_buf` は使わない

## 関連ページ

- [cpprefjp: jmp_buf](https://cpprefjp.github.io/reference/csetjmp/jmp_buf.html)
- [cppreference: jmp_buf](https://en.cppreference.com/w/cpp/utility/program/jmp_buf)
