---
title: longjmp
summary: "setjmp で記録した位置まで、途中の関数を飛ばして戻る。"
order: 900
tags:
  - 入出力・文字列
---

# longjmp

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <csetjmp>`
</div>

深く入った関数の奥でエラーが起きたとき、`longjmp` を呼ぶと、途中の関数を 1 つずつ戻らずに、[`setjmp`](setjmp.md) で記録した位置まで一気に戻れます。便利に見えますが、飛び越えた関数にあるオブジェクトのデストラクターは呼ばれません。C++ では、例外（`throw` と `catch`）が、デストラクターを呼びながら同じことをするので、そちらを使います。

!!! tip "ポイント"
    - `longjmp(env, v)` は、`setjmp(env)` の呼び出しに戻り、`v` を返させる。自分自身には戻らない（`[[noreturn]]`）
    - `v` が 0 のときは 1 になる
    - 飛び越えた関数のデストラクターは呼ばれない。C++ のオブジェクトがある所をまたがない
    - `setjmp` を呼んだ関数が終わったあとは、使えない

!!! info "このページを読む前に"
    [`<csetjmp>`](csetjmp.md) の概要と [`setjmp`](setjmp.md) を先に読んでください。

## 関数の詳しい説明

### std::longjmp {#longjmp}

```cpp
[[noreturn]] void longjmp(jmp_buf env, int value);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `env` | [`jmp_buf`](jmp_buf.md) | `setjmp` で記録した場所 |
| `value` | `int` | `setjmp` が返す値。0 を渡すと 1 になる |

`env` に記録された位置に戻り、対応する `setjmp` の呼び出しが `value` を返したように、実行を続けます。`longjmp` 自身は戻ってきません。そのため `[[noreturn]]` が付いています。

`value` が 0 のときに 1 になるのは、`setjmp` の「最初の呼び出し」が 0 を返すためで、0 を返してしまうと区別できないからです。エラーの種類を伝えたいときは、1 以上の値を渡します。

`longjmp` は、途中の関数のスタックの内容を、全部捨てます。ローカルのオブジェクトにデストラクターが書いてあっても、呼ばれません。`std::string` のメモリ、ロックの解放、ファイルのクローズなどが、すべて飛びます。デストラクターが自明でないオブジェクトを飛び越えると、規格では未定義動作です。

条件を守れないと、やはり未定義動作です。`setjmp` を呼んだ関数がすでに終わっていたとき、別のスレッドの `jmp_buf` を渡したとき、一度も `setjmp` していない `jmp_buf` を渡したときがそうです。

計算量は定数です（保存した状態を書き戻すだけ）。

## 実際に動かしてみる

```cpp
#include <csetjmp>
#include <print>

std::jmp_buf g_env;

void Fail() {
  std::longjmp(g_env, 2);
}

int main() {
  const int r = setjmp(g_env);
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

`value` を 0 にすると、1 に置き換わります。次の例で確かめます。

```cpp
#include <csetjmp>
#include <print>

std::jmp_buf g_env;

int main() {
  const int r = setjmp(g_env);
  if (r == 0) {
    std::longjmp(g_env, 0);  // 0 を渡しても…
  }
  std::println("r = {}", r);  // 1 になる
}
```

```text title="実行結果"
r = 1
```

## ゲームでの使いどころ

自分のコードで呼ぶことはありません。C のライブラリのエラー処理を読むときに、`longjmp` が見えたら、その上の呼び出しに C++ のオブジェクトがないかを調べます。あれば、そのライブラリの呼び出しを小さな関数に包み、オブジェクトを外に出します。

## よくあるミス

??? failure "C++ の関数をまたいで longjmp する"
    間にある `std::string` や `std::vector` のデストラクターが呼ばれず、メモリがリークします。ロックを持っていれば、解放されないままデッドロックします。

??? failure "別のスレッドから longjmp する"
    `setjmp` したスレッドとは別のスレッドで `longjmp` すると、別のスタックに飛ぶことになります。未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`setjmp`](setjmp.md) | 戻り先の記録 |
| 例外 | デストラクターを呼びながら戻る。C++ ではこちら |
| [`std::abort`](../numeric/cstdlib/abort.md) | プログラムを強制終了する |

## コンパイラ対応

C 由来の機能です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `longjmp(env, v)` は、`setjmp` の呼び出しに戻って `v` を返させる
    - [x] 途中の関数のデストラクターは呼ばれない
    - [x] C++ の自分のコードでは、例外を使う

## 関連ページ

- [cpprefjp: longjmp](https://cpprefjp.github.io/reference/csetjmp/longjmp.html)
- [cppreference: longjmp](https://en.cppreference.com/w/cpp/utility/program/longjmp)
