---
title: va_arg
summary: "可変引数から、次の引数を指定した型で取り出す。"
order: 900
tags:
  - 入出力・文字列
---

# va_arg

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdarg>`
</div>

`va_start` で読み始める位置を決めたら、あとは `va_arg(ap, 型)` で 1 つずつ取り出します。呼ぶたびに、次の引数が、指定した型として返ってきます。引数が本当にその型だったかどうかは、誰も確かめてくれません。型を間違えると、ゴミの値が出るか、未定義動作になります。

!!! tip "ポイント"
    - 呼ぶたびに目印が 1 つ進む。同じ引数をもう一度読むことはできない
    - 型は、渡した側の型に合わせる。ただし `float` は `double`、`char` や `short` は `int` で取り出す
    - 引数の数は分からない。実際より多く呼ぶと未定義動作
    - 新しいコードでは、可変長テンプレートを使う

!!! info "このページを読む前に"
    [`<cstdarg>`](cstdarg.md) の概要と [`va_start`](va_start.md) を先に読んでください。

## 関数の詳しい説明

### va_arg {#va_arg}

```cpp
T va_arg(va_list ap, T);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ap` | `va_list` | `va_start` で初期化した目印 |
| `T` | 型名 | 取り出す型。マクロなので、値ではなく型を書く |

戻り値は、次の引数を `T` として読んだ値です。呼ぶたびに `ap` が進むので、順番に並んだ引数を、頭から読んでいけます。`va_arg(ap, int)` の次に `va_arg(ap, double)` と、型を変えて読むこともできます。`printf` は、書式文字列の `%d` や `%f` を見ながら、まさにこれをしています。

`T` は、渡された引数の型と一致していなければなりません。`int` を渡したのに `double` で取り出すと、メモリの読み方が違うので、意味のない値になります。例外として、符号の違う整数型（`int` と `unsigned`）は、値が両方の型で表せる範囲なら許されます。ポインタも、`void*` で渡したものを `char*` で取るのは許されます。

もう 1 つの決まりが、引数の型の昇格です。`...` の引数は、渡されるときに、`char` と `short` が `int` に、`float` が `double` に広げられます。そのため、`va_arg(ap, char)`、`va_arg(ap, short)`、`va_arg(ap, float)` は、書いてはいけません。`int` と `double` で取り出して、必要なら自分でキャストします。

落とし穴は、`T` に参照型や、昇格される型を書くことです。コンパイルが通っても、未定義動作です。引数が足りないときも未定義動作で、エラーにはなりません。計算量は定数です。

## 実際に動かしてみる

```cpp
#include <cstdarg>
#include <print>

// 型を変えながら取り出す: 整数 1 つと、double 2 つ
void Show(int id, ...) {
  va_list ap;
  va_start(ap, id);
  int hp = va_arg(ap, int);
  double x = va_arg(ap, double);
  double y = va_arg(ap, double);
  va_end(ap);
  std::println("id={} hp={} pos=({}, {})", id, hp, x, y);
}

int main() {
  // float の 1.5f も、double に昇格して渡される
  Show(7, 30, 1.5f, 2.0);
}
```

```text title="実行結果"
id=7 hp=30 pos=(1.5, 2)
```

`1.5f` は `float` ですが、`...` に渡す段階で `double` になっています。だから `double` で取れます。`va_arg(ap, float)` と書くと、ここで壊れます。

## ゲームでの使いどころ

自作のログ関数の中では、`vsnprintf` に `va_list` を丸ごと渡すので、`va_arg` を直接書くことは少ないです。自分で取り出すのは、「最後に 0 や `nullptr` を置いた引数の並び」を読むような、小さな C 風の API を作るときです。

```cpp
// 最後が nullptr の文字列の並びを読む
void PrintAll(const char* first, ...) {
  va_list ap;
  va_start(ap, first);
  for (const char* s = first; s != nullptr; s = va_arg(ap, const char*)) {
    std::println("{}", s);
  }
  va_end(ap);
}
```

呼ぶ側は `PrintAll("a", "b", "c", nullptr);` と、最後に `nullptr` を忘れずに書きます。忘れると、ゴミの領域を文字列として読みに行きます。

## よくあるミス

??? failure "float や char で取り出す"
    `...` に渡された引数は、`float` が `double`、`char` と `short` が `int` に昇格しています。`va_arg(ap, float)` と書くと、未定義動作です。コンパイラが警告を出すことも多いですが、無視しないでください。

??? failure "渡した型と違う型で取り出す"
    `int` で渡したものを `double` で取り出しても、変換はされません。ビットの並びがそのまま解釈されて、まったく別の値になります。0 を `int` で渡したのに `const char*` で取ると、環境によっては下位 32 ビットだけがゴミです。`nullptr` は、`nullptr` と書いて渡します。

??? failure "引数の数を超えて読む"
    `Sum(3, 1, 2)` と書いて、`count` が 3 のまま 3 回読むと、存在しない引数を読み、未定義動作です。個数と引数の食い違いは、コンパイラには分かりません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`va_start`](va_start.md) | 読み始める |
| [`va_copy`](va_copy.md) | 目印を複製して、同じ引数をもう一度読む |
| 可変長テンプレート | 型安全な書き方 |

## コンパイラ対応

C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `va_arg(ap, 型)` で、次の引数を取り出して、目印を進める
    - [x] `float` は `double`、`char` と `short` は `int` で取り出す
    - [x] 型も数も検査されない。間違えると未定義動作

## 関連ページ

- [cpprefjp: va_arg](https://cpprefjp.github.io/reference/cstdarg/va_arg.html)
- [cppreference: va_arg](https://en.cppreference.com/w/cpp/utility/variadic/va_arg)
