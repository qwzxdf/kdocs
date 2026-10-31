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

`va_start` で始めた読み取りは、読み終えたら閉じる決まりです。その閉じる側が `va_end` です。多くの環境では、`va_end` は何もしないマクロに展開されるので、書き忘れても動いてしまいます。それが逆に危険で、`va_end` を呼ばない書き方が、別の環境（引数の読み取りに後始末が要る環境）で初めて問題を起こします。

!!! tip "ポイント"
    - `va_start` や `va_copy` を呼んだ `va_list` のそれぞれに、1 回ずつ `va_end` を呼ぶ
    - `return` や `break` で途中で抜けるときも、その前に呼ぶ
    - `va_end` のあとの `va_list` は使えない。もう一度読むなら `va_start` からやり直す
    - 書き忘れても多くの環境で動くが、規格では未定義動作

!!! info "このページを読む前に"
    [`<cstdarg>`](cstdarg.md) の概要と [`va_start`](va_start.md) を先に読んでください。

## 関数の詳しい説明

### va_end {#va_end}

```cpp
void va_end(va_list ap);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ap` | `va_list` | 後始末をする目印。`va_start` か `va_copy` で初期化したもの |

戻り値はありません（マクロです）。計算量は定数です。

呼ぶ相手は、`va_start` を呼んだ `va_list` と、`va_copy` で作った `va_list` の両方です。`va_copy` で複製を作ったなら、複製にも、元にも、それぞれ `va_end` が要ります。数を合わせるのが決まりで、`va_start` と `va_copy` の呼び出しの数と、`va_end` の数は一致させます。

`va_end` を呼んだ `va_list` は、そのあと使えません。再び読みたいときは、もう一度 `va_start` から始めます。

落とし穴は、<strong>`va_start` と `va_end` を、同じ関数の中で組にしなければならない</strong>ことです。`va_list` を別の関数に渡した場合、受け取った側は `va_end` を呼びません。呼ぶのは、`va_start` した側です。また、受け取った側が `va_arg` で読み進めたあとの `va_list` は、呼んだ側から見ると、値が不定になります。そのあとは `va_end` 以外、何もしないようにします。

## 実際に動かしてみる

```cpp
#include <cstdarg>
#include <print>

// 負の値が出たら、そこで読むのをやめる
int SumUntilNegative(int first, ...) {
  va_list ap;
  va_start(ap, first);
  int sum = 0;
  for (int v = first; v >= 0; v = va_arg(ap, int)) {
    sum += v;
  }
  va_end(ap);  // 途中で抜けても、ここを必ず通る形にする
  return sum;
}

int main() {
  std::println("{}", SumUntilNegative(10, 20, 30, -1));
}
```

```text title="実行結果"
60
```

`-1` を目印にして、そこで読み終えています。ループを抜けたあとに `va_end` を置いているので、どの経路でも後始末が通ります。ループの中に `return` を書くなら、その前に `va_end` が必要です。

## ゲームでの使いどころ

`va_start` を書いたら、すぐ下の行に `va_end` の位置を決めて、間に読み取りを挟む、という書き方をします。ゲームのコードでは、ログ関数のなかで `va_start` と `vsnprintf` と `va_end` を 3 行並べる形になるのが、ほとんどです。

## よくあるミス

??? failure "途中の return で va_end を飛ばす"
    入力の検査で早めに `return` する関数に、あとから `va_start` を追加すると、早い `return` の経路だけ `va_end` が呼ばれなくなります。`va_start` はなるべく読む直前に呼び、`va_end` までの間に `return` を置かないようにします。

??? failure "別の関数に渡した va_list を、そのあと使う"
    `vsnprintf(buf, n, fmt, ap)` に渡した `ap` は、呼んだあとは不定です。もう一度読むなら、渡す前に `va_copy` で複製しておきます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`va_start`](va_start.md) | 読み取りを始める。対になる |
| [`va_copy`](va_copy.md) | 複製。複製にも `va_end` が要る |

## コンパイラ対応

C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `va_start` と `va_copy` のそれぞれに、`va_end` を 1 つずつ組にする
    - [x] 途中で抜ける経路でも、`va_end` を通す
    - [x] `va_end` の後の `va_list` は使わない

## 関連ページ

- [cpprefjp: va_end](https://cpprefjp.github.io/reference/cstdarg/va_end.html)
- [cppreference: va_end](https://en.cppreference.com/w/cpp/utility/variadic/va_end)
