---
title: va_start
summary: "可変引数の読み取りを始める。"
order: 900
tags:
  - 入出力・文字列
---

# va_start

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdarg>`
</div>

`...` で受け取った引数は、名前がないので、そのままでは取り出せません。`va_start` は、「名前のある最後の引数の、すぐ次から読む」と宣言して、`va_list` の目印を最初の位置に置くマクロです。可変引数を読む関数は、必ずこれから始まります。

!!! tip "ポイント"
    - 第 2 引数には、`...` の直前にある、名前つきの引数を書く
    - 同じ `va_list` に `va_start` を呼んだら、必ず `va_end` で閉じる
    - `...` の前に名前つきの引数がない関数では使えない（C++ では `void f(...)` は宣言できても、`va_start` の相手がない）
    - 型の検査がない。新しいコードでは、可変引数テンプレートを使う

!!! info "このページを読む前に"
    [`<cstdarg>`](cstdarg.md) の概要を先に読んでください。3 つのマクロの流れが分かります。

## 関数の詳しい説明

### va_start {#va_start}

```cpp
void va_start(va_list ap, parmN);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ap` | `va_list` | 目印を入れる変数。あらかじめ宣言しておく |
| `parmN` | 名前つきの引数 | `...` の直前の引数の名前 |

`ap` は、`va_start` を呼ぶ前に `va_list ap;` と宣言しておきます。初期化は不要で、`va_start` が初期化します。

`parmN` に書くのは、関数の引数のうち、`...` の直前にあるものです。たとえば `void Log(const char* fmt, ...)` なら `fmt` です。別の引数を書くと、読み始める位置がずれて、未定義動作になります。`parmN` が参照型や、配列、関数の型のときも未定義動作です。`printf` のような、`const char*` や `int` を最後に置く形が普通なので、気になることはほとんどありません。

戻り値はありません（マクロです）。計算量は定数です。

落とし穴は、`va_start` を呼ばずに `va_arg` を使うことと、`va_start` を呼んだのに `va_end` を忘れることです。前者は未初期化の目印を使うことになり、後者は環境によってはスタックやメモリの後始末が漏れます。

### 読み始める位置 {#position}

`...` の引数は、名前つきの最後の引数の続きに並んで渡されます。`va_start(ap, count)` は、その並びの、`count` の次の 1 つ目を指すように `ap` を設定します。そのあと `va_arg` を呼ぶたびに、1 つずつ進みます。

## 実際に動かしてみる

```cpp
#include <cstdarg>
#include <print>

int Sum(int count, ...) {
  va_list ap;
  va_start(ap, count);  // count の次の引数から読む
  int sum = 0;
  for (int i = 0; i < count; ++i) sum += va_arg(ap, int);
  va_end(ap);
  return sum;
}

int main() {
  std::println("{}", Sum(3, 1, 2, 3));
  std::println("{}", Sum(0));  // 引数がなくても動く
}
```

```text title="実行結果"
6
0
```

`Sum(0)` は、`...` に何も渡していません。それでも、`va_start` を呼ぶのは問題ありません。読まなければよいだけです。

## ゲームでの使いどころ

`printf` 風のログ関数、デバッグの表示関数、C 言語の API に合わせた可変引数の関数を書くときに使います。ただし、`va_start` で得た `va_list` を、`vsnprintf` に渡すだけの関数がほとんどです。自分で `va_arg` を書く場面は多くありません。

## よくあるミス

??? failure "va_start の第 2 引数を間違える"
    `...` の直前の引数ではなく、先頭の引数を書いてしまうと、読み始める位置がずれます。コンパイラが警告を出すことがありますが、出ないこともあります。

??? failure "va_end を呼ばずに return する"
    途中で `return` する場合も、その前に `va_end` を呼びます。例外が飛ぶ可能性がある関数では、`va_end` が呼ばれない経路ができやすいので、読む部分を小さな関数に切り出します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`va_arg`](va_arg.md) | 取り出す |
| [`va_end`](va_end.md) | 後始末 |
| 可変長テンプレート | 型安全な書き方 |

## コンパイラ対応

C++ のどの版でも使えます。C23 では、`parmN` を省略できますが、C++ にはその書き方はありません。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `va_start(ap, 最後の名前つき引数)` で、読み始める位置に目印を置く
    - [x] 必ず `va_end` と組にする
    - [x] 第 2 引数は `...` の直前の引数

## 関連ページ

- [cpprefjp: va_start](https://cpprefjp.github.io/reference/cstdarg/va_start.html)
- [cppreference: va_start](https://en.cppreference.com/w/cpp/utility/variadic/va_start)
