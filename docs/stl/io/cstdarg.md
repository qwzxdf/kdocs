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

ログ関数を `Log("HP=%d name=%s", hp, name)` のように、`printf` と同じ形で呼べるようにしたい。引数の数は、呼ぶたびに違います。C 風にこれを実現する仕組みが、`<cstdarg>` の `va_list` と、`va_start`、`va_arg`、`va_end` の 3 つのマクロです。関数の宣言に `...` と書くと、名前のない引数を何個でも受け取れて、この 3 つで順番に取り出します。

古いコードやライブラリの C 互換の API で、今もよく出会います。ただ、型の検査が一切なく、引数の数も受け取る側には分かりません。新しいコードでは、可変引数テンプレートや `std::format` を使います。

!!! tip "ポイント"
    - 引数の数と型は、呼ぶ側と受ける側が約束しておくしかない。`printf` ではそれが書式文字列
    - 型を間違えて取り出すと未定義動作。コンパイラも気づかない
    - `va_start` と `va_end` は必ず組にする。`va_list` を別の関数へ渡して使い回すなら `va_copy`
    - 新しいコードは、可変引数テンプレート（`template <class... Args>`）か `std::format`

!!! info "このページを読む前に"
    [`printf`](cstdio/printf.md) の使い方を知っていると、書式文字列で引数の型を伝える意味が分かります。`std::vsnprintf` は [`vsnprintf`](cstdio/vsnprintf.md) のページにあります。

## 関数の詳しい説明

### 全体の流れ {#flow}

```cpp
void Log(const char* fmt, ...) {
  va_list args;
  va_start(args, fmt);       // 最後の名前つき引数 fmt の次から読む
  int v = va_arg(args, int); // 次の引数を int として取り出す
  va_end(args);              // 後始末
}
```

`...` の部分は、型も数も、関数の中からは分かりません。`va_list` 型の変数 `args` が、「今どこまで読んだか」を覚える目印になります。`va_start(args, fmt)` で、`fmt` の次の引数に目印を合わせ、`va_arg(args, 型)` を呼ぶたびに、その型として 1 つ取り出して、目印を次に進めます。読み終えたら `va_end(args)` を呼びます。

最後の名前つき引数（`fmt`）が必要なのは、`...` の位置を、その引数のアドレスから決めるからです。

詳しい使い方は、次の 4 つのマクロのページに分けて書いています。

- [`va_start`](va_start.md): 読み取りを始める
- [`va_arg`](va_arg.md): 次の引数を取り出す
- [`va_end`](va_end.md): 後始末をする
- [`va_copy`](va_copy.md): `va_list` を複製する

### 型が自動で変換される（既定の実引数昇格） {#promotion}

`...` で受ける引数は、型が自動で広がります。`char` と `short` は `int` に、`float` は `double` になります。そのため、`va_arg(args, float)` や `va_arg(args, char)` と書くのは未定義動作で、`double` や `int` で取り出します。

## 実際に動かしてみる

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

個数を最初の引数 `count` で教えています。これを実際の引数の数と食い違わせても、コンパイラは何も言いません。

## ゲームでの使いどころ

自作のログ関数を `printf` と同じ書き方にしたいときに使います。中身は、`va_list` を受け取る `vsnprintf` などに渡すだけです。

```cpp
void Log(const char* fmt, ...) {
  char buffer[256];
  va_list args;
  va_start(args, fmt);
  std::vsnprintf(buffer, sizeof(buffer), fmt, args);
  va_end(args);
  // buffer をログに出す
}
```

`printf` の仲間には、`v` のついた版（`vprintf`、`vsnprintf`）があり、`va_list` を直接受け取ります。自分では `va_arg` を呼ばずに、全部これに任せるのが、実際には最も多い使い方です。

C++ だけの新しいコードなら、`template <class... Args> void Log(std::format_string<Args...> fmt, Args&&... args)` と書いて、`std::format` に渡します。型を間違えると、コンパイルエラーになります。

## よくあるミス

??? failure "個数と実際の引数が合わない"
    実際より多く `va_arg` を呼ぶと、存在しない引数を読むことになり、未定義動作です。クラッシュしたり、ゴミの値が出たりします。数を最初の引数で渡すか、`printf` のように書式文字列で決めます。

??? failure "float を渡したのに va_arg(args, float) で取る"
    `float` は `double` に広がって渡されるので、`double` で取り出します。`float` で取ると未定義動作です。

??? failure "std::string をそのまま渡す"
    `Log("%s", name)` に `std::string` を渡すと、中身ではなくオブジェクトそのものが渡されて、壊れた出力になります。`name.c_str()` を渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::format`](../utilities/format.md) | 型安全な書式つき出力 |
| `template <class... Args>` | 可変引数テンプレート。型も数もコンパイル時に分かる |
| [`std::initializer_list`](../containers/initializer_list.md) | 同じ型の値を、数を決めずに受け取る |

## コンパイラ対応

C 由来の機能です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `...` と `va_list` で、数の決まっていない引数を C 風に受け取る
    - [x] `va_start` → `va_arg` → `va_end` の順。`va_end` を忘れない
    - [x] 型は検査されない。`float` は `double`、`char` は `int` で取る
    - [x] 新しいコードは、可変引数テンプレートか `std::format`

## 関連ページ

- [cpprefjp: va_list](https://cpprefjp.github.io/reference/cstdarg/va_list.html)
- [cppreference: va_list](https://en.cppreference.com/w/cpp/utility/variadic/va_list)
