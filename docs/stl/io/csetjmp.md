---
title: csetjmp
summary: "setjmp と longjmp。C 由来の、関数をまたいで一気に戻る仕組み。"
order: 98
tags:
  - 入出力・文字列
---

# csetjmp

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <csetjmp>`
</div>

深く入れ子になった関数の奥でエラーが起きたとき、途中の関数を 1 つずつ `return` で戻るのは面倒です。C の時代には、「ここに戻ってくる」と目印（`setjmp`）を付けておき、奥から一気にそこへ飛ぶ（`longjmp`）という方法がありました。`<csetjmp>` は、その道具です。

C++ では、飛び越える途中のオブジェクトのデストラクターが呼ばれません。ロックや確保したメモリが、そのまま残ります。ですから、C++ のコードに自分で書くことはなく、例外（`throw` と `catch`）を使います。このページを読む理由は、libpng や libjpeg のような古い C のライブラリが、エラーを `longjmp` で返す設計になっているときに、それに巻き込まれないためです。

!!! tip "ポイント"
    - `setjmp(env)` で目印を付け、`longjmp(env, 値)` でそこへ飛ぶ。飛んだ先では、`setjmp` が 0 以外の値を返す
    - 飛び越えた関数のデストラクターは呼ばれない。C++ のオブジェクトがある所を、またいで飛ばない
    - 新しいコードでは、例外を使う
    - C のライブラリの `longjmp` が C++ の関数を飛び越えないように、境界で受け止める

!!! info "このページを読む前に"
    「未定義動作」という言葉が出てきます。[未定義動作](../../basics/ub.md)を先に読むと、デストラクターが呼ばれないことの怖さが分かります。

## 関数の詳しい説明

### 全体の流れ {#flow}

```cpp
std::jmp_buf env;                  // 目印の保存先

if (setjmp(env) == 0) {            // 目印を付ける。最初は 0 が返る
  Work();                          // 奥で longjmp(env, 1) が呼ばれるかもしれない
} else {
  // longjmp で飛んできた。setjmp は 0 以外を返している
}
```

[`setjmp`](setjmp.md) は 2 回「返ってくる」関数のように見えます。目印を付けた直後は 0 を返し、あとで [`longjmp`](longjmp.md) が呼ばれると、同じ `setjmp` の呼び出しから、今度は 0 以外の値を返します。`if` の 2 つの枝で、最初の流れと、エラーで飛んできた流れを分けて書きます。

目印の保存先が [`jmp_buf`](jmp_buf.md) です。`setjmp` は、そのときのレジスタやスタックの位置を、ここに書き込みます。

### 使える場所の決まり {#rules}

`setjmp` を呼んだ関数が `return` したあとで、その `jmp_buf` に `longjmp` してはいけません。戻り先の関数がすでに存在しないからで、未定義動作です。また、`setjmp` の呼び出しは、`if (setjmp(env) == 0)` や `switch` の条件のような、単純な形に限られます。`int r = setjmp(env);` のような、式の途中に埋め込む形は、規格では保証されません。

ローカル変数にも決まりがあります。`setjmp` のあとで値を変えたローカル変数は、`longjmp` で戻ってきたときの値が不定になることがあります。その変数が `volatile` なら大丈夫です。

## 実際に動かしてみる

```cpp
#include <csetjmp>
#include <print>

std::jmp_buf g_env;

void Load(int step) {
  if (step == 3) {
    std::longjmp(g_env, step);  // 3 段目でエラー: 一気に戻る
  }
  Load(step + 1);               // 次の段へ（深く入る）
}

int main() {
  const int r = setjmp(g_env);
  if (r == 0) {
    Load(1);
    std::println("最後まで行った");  // 実行されない
  } else {
    std::println("{} 段目で失敗した", r);
  }
}
```

```text title="実行結果"
3 段目で失敗した
```

`Load(1)` から `Load(2)`、`Load(3)` と深く入り、3 段目で `longjmp` したところ、途中の `return` を通らずに `main` の `setjmp` に戻ってきました。`r` には、`longjmp` に渡した 3 が入っています。

## ゲームでの使いどころ

自分のコードで使うことはありません。使われているのを見るのは、PNG や JPEG を読む C のライブラリで、エラーを `longjmp` で返す設計のときです。その場合、ライブラリを呼ぶ関数の中だけで `setjmp` を受け止め、その関数にはデストラクターを持つオブジェクトを置きません。

```cpp
// ライブラリの呼び出しだけを包む関数: 中に C++ のオブジェクトを置かない
bool DecodeImage(Decoder* d, const uint8_t* data, size_t size) {
  if (setjmp(d->error_jump) != 0) {
    return false;   // ライブラリが longjmp してきた
  }
  library_decode(d, data, size);
  return true;
}
```

`std::string` や `std::vector` はこの関数の外に置きます。同じ関数の中に置くと、`longjmp` で飛んだときにデストラクターが呼ばれず、メモリが漏れます。

## よくあるミス

??? failure "デストラクターが呼ばれずにリークする"
    `longjmp` が飛び越えた間の関数にある `std::string`、`std::vector`、ロックなどのデストラクターは呼ばれません。メモリやロックが残ります。デストラクターが自明でない型を飛び越えると、規格では未定義動作です。

??? failure "setjmp を呼んだ関数から戻ったあとで longjmp する"
    戻り先のスタックの領域はもうありません。必ず、`setjmp` を呼んだ関数がまだ動いている間にだけ、`longjmp` します。

??? failure "例外で書けるのに longjmp を選ぶ"
    自分で書くコードのエラー処理は、例外か戻り値（`std::expected`）で書きます。`longjmp` は、C のライブラリの流儀に合わせるときだけです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`setjmp`](setjmp.md) | 目印を付ける |
| [`longjmp`](longjmp.md) | 目印まで飛ぶ |
| [`jmp_buf`](jmp_buf.md) | 目印の保存先 |
| 例外（`throw` / `catch`） | デストラクターを呼びながら戻る、安全な代わり |
| [`std::expected`](../utilities/expected.md) | 例外を使わず、戻り値でエラーを返す |

## コンパイラ対応

C 由来の機能です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `setjmp` で目印、`longjmp` で一気に戻る。デストラクターは呼ばれない
    - [x] C++ のオブジェクトがある関数をまたがない。自分のコードは例外にする
    - [x] C のライブラリが `longjmp` を使うときは、呼び出しを小さな関数に包んで受け止める

## 関連ページ

- [cpprefjp: csetjmp](https://cpprefjp.github.io/reference/csetjmp.html)
- [cppreference: setjmp](https://en.cppreference.com/w/cpp/utility/program/setjmp)
