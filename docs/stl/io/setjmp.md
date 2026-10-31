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

「エラーになったら、ここまで戻ってきたい」という位置に、しおりを挟むのが `setjmp` です。しおりを挟んだ直後は 0 を返します。のちに奥の関数が [`longjmp`](longjmp.md) を呼ぶと、同じ `setjmp` の呼び出しから、`longjmp` に渡された 0 以外の値が返ってきます。つまり、1 回の呼び出しが 2 回返る、変わった関数です。

!!! tip "ポイント"
    - 最初に呼んだときは 0 を返す。`longjmp` で戻ると、0 以外を返す
    - `if (setjmp(env) == 0)` の形で使う。式の途中に埋め込まない
    - `setjmp` を呼んだ関数が終わったあとで、`longjmp` してはいけない
    - 戻ってきたあと、`setjmp` のあとで変更した普通のローカル変数は、値が不定になることがある
    - C++ のコードでは、例外を使う

!!! info "このページを読む前に"
    [`<csetjmp>`](csetjmp.md) の概要を先に読んでください。

## 関数の詳しい説明

### setjmp {#setjmp}

```cpp
int setjmp(jmp_buf env);  // マクロ
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `env` | [`jmp_buf`](jmp_buf.md) | 位置を保存する場所。`longjmp` で同じものを渡す |

`env` に、呼び出した時点の実行の状態（戻り先のアドレス、スタックの位置、レジスタの一部）を保存します。保存が終わったときは、0 を返します。

のちに [`longjmp(env, v)`](longjmp.md) が呼ばれると、実行は保存した位置に戻り、`setjmp` が `v` を返したかのように続きます。`v` が 0 のときは、1 に置き換えられます。0 を返すと「最初の呼び出し」と区別できなくなるからです。戻り値の 0 は最初、0 以外はエラーで戻ってきた、と読み分けます。

`setjmp` は、規格では関数ではなくマクロです。そのため、`std::setjmp` のように名前空間を付けず、`setjmp(env)` と書きます。関数のアドレスを取ることもできません。

使える場所に決まりがあります。`if (setjmp(env) == 0)`、`switch (setjmp(env))`、`setjmp(env);` の単独の文のような、単純な形に限られます。`int r = setjmp(env);` のように代入に使うのは、多くの環境では動きますが、規格上は保証されません。

落とし穴は、<strong>`setjmp` を呼んだ関数が終わったあとの `longjmp` は未定義動作</strong>だということです。しおりを挟んだ関数が、もうないからです。また、`setjmp` のあとで値を変えたローカル変数は、戻ってきたときに古い値が見えることがあります。戻ってきたあとにも使う変数には、`volatile` を付けます。

計算量は定数です。

## 実際に動かしてみる

```cpp
#include <csetjmp>
#include <print>

std::jmp_buf g_env;

void Fail(int code) {
  std::longjmp(g_env, code);  // setjmp の位置へ戻る
}

int main() {
  const int r = setjmp(g_env);  // 最初は 0。longjmp 後は code
  if (r == 0) {
    std::println("しおりを挟んだ");
    Fail(5);
    std::println("ここは実行されない");
  } else {
    std::println("エラー {} で戻ってきた", r);
  }
}
```

```text title="実行結果"
しおりを挟んだ
エラー 5 で戻ってきた
```

`setjmp` は 2 回返っています。1 回目は 0 で、`if` の中へ入り、`Fail(5)` で `longjmp` します。2 回目は 5 で、`else` に入っています。

## ゲームでの使いどころ

自分のコードで書くことはありません。古い C の画像ライブラリが、エラーのときに `longjmp` で戻ってくる設計の場合に、呼び出しを包む関数の中で `setjmp` を呼ぶ形に出会います。その関数の中には、デストラクターを持つ C++ のオブジェクトを置きません。

## よくあるミス

??? failure "setjmp のあとで変えた変数が、戻ると古い値になる"
    `setjmp` のあとで `int count = 1;` を `count = 2;` に変え、`longjmp` で戻ると、`count` は 1 のままに見えることがあります。レジスタに置かれた値が、保存時のものに戻るためです。`volatile int count` にします。

??? failure "setjmp した関数から戻ったあとで longjmp する"
    しおりを挟んだスタックの領域は、もう別の関数に使われています。クラッシュや、予測できない動作になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`longjmp`](longjmp.md) | 記録した位置に戻る |
| [`jmp_buf`](jmp_buf.md) | 保存先 |
| 例外 | デストラクターを呼びながら戻る。C++ ではこちら |

## コンパイラ対応

C 由来の機能です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `setjmp` は最初は 0、`longjmp` で戻ると 0 以外を返す
    - [x] `if (setjmp(env) == 0)` の形で使う
    - [x] 戻ってきたあとに使う変数は `volatile`
    - [x] C++ のコードでは例外を使う

## 関連ページ

- [cpprefjp: setjmp](https://cpprefjp.github.io/reference/csetjmp/setjmp.html)
- [cppreference: setjmp](https://en.cppreference.com/w/cpp/utility/program/setjmp)
