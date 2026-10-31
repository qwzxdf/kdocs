---
title: std::cout
summary: "標準出力。画面に文字や値を出す（<< でつなぐ）。"
order: 70
tags:
  - 入出力・文字列
---

# std::cout

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-11">C++98〜</span>
`#include <iostream>`
</div>

敵の HP を画面に出して確かめたい。座標がおかしいので、とりあえず値を見たい。そんなとき、昔から C++ で最初に覚えるのが `std::cout << "HP " << hp << "\n";` という書き方です。`<<` で値をつなげていくだけで、整数も小数も文字列も、型を気にせず出せます。

C++23 の `std::println` のほうが書式が見やすく、型の安全も高いので、新しいコードではそちらが向いています。それでも `cout` は、既存のコードや古い資料のほとんどに出てくるので、読めるようにしておく必要があります。

!!! tip "ポイント"
    - 改行は `"\n"` を使う。`std::endl` は毎回 `flush` するので、大量に出すと遅い
    - 桁数や幅は [`setw`](setw.md) と [`setprecision`](setprecision.md) で指定する。ただし `setw` 以外は、指定が次の出力にも残る
    - 自作の型は `operator<<` を作れば、`cout` にそのまま流せる
    - 新しいコードは `std::println`。`cout` は古いコードを読むために知っておく

!!! info "このページを読む前に"
    [`std::ostream`](ostream.md) が出力ストリームの基本です。`cout` は、その標準出力につながった 1 つのオブジェクトです。

## 関数の詳しい説明

### std::cout {#cout}

```cpp
extern std::ostream cout;
```

`<iostream>` を読み込むと使える、グローバルなオブジェクトです。出力先は C の `stdout` と同じ標準出力で、普通はコンソールの画面です。`main` が始まる前から使えます。

デフォルトでは C の `printf` と同期していて、`cout` と `printf` を混ぜて書いても、書いた順に出ます。この同期が、`cout` が遅いと言われる理由の 1 つです。`std::ios::sync_with_stdio(false)` で同期をやめると速くなりますが、そのあとは `printf` と混ぜられません。

出力は、内部のバッファに溜まってから、まとめて書き出されます。`"\n"` を出しただけでは、画面に出るとは限りません。プログラムが途中で異常終了すると、バッファに残っていた分が出ないことがあります。ログを確実に残したいときは、`std::cerr` か `std::flush` を使います。

### operator<< {#shift-out}

```cpp
std::ostream& operator<<(std::ostream& os, int value);  // 型ごとにある
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `os` | `std::ostream&` | 出力先のストリーム。`cout` を左に書くと、これに入る |
| `value` | 各種の型 | 出す値。整数、浮動小数点数、文字列、ポインタなど |

値を文字にして、ストリームに書き込みます。戻り値は引数に渡したのと同じストリームの参照なので、`cout << a << b << c` と続けて書けます。左から右に、順番に評価されます。

`char` を渡すと 1 文字として、`char` の配列や `const char*` は文字列として出ます。`bool` は、何も指定しなければ `1` と `0` で出ます。`true` と `false` で出したいときは、[`boolalpha`](boolalpha.md) を流します。

落とし穴は、`const char*` 以外のポインタを渡すと、アドレスが出ることです。`unsigned char*` や `signed char*` も、文字列としては扱われません。`nullptr` の `const char*` を渡すと、ストリームが失敗状態になり、以降の出力が全部無視されます。

### 自作の型を出す {#custom}

自分の構造体に `operator<<` を作ると、`cout` にそのまま流せます。第 1 引数と戻り値を `std::ostream&` にするのが決まりです。

```cpp
std::ostream& operator<<(std::ostream& os, const Vec2& v) {
  return os << '(' << v.x << ", " << v.y << ')';
}
```

ここで `std::cout` ではなく、引数の `os` に書くのが大切です。`cout` に直接書くと、ファイルや `ostringstream` に出したいときに使えません。戻り値を忘れると、`cout << v << '\n'` のように続けて書けなくなります。

```cpp
#include <iostream>

struct Vec2 {
  float x;
  float y;
};

std::ostream& operator<<(std::ostream& os, const Vec2& v) {
  return os << '(' << v.x << ", " << v.y << ')';
}

int main() {
  std::cout << Vec2{1.5f, -2.0f} << '\n';
}
```

```text title="実行結果"
(1.5, -2)
```

`-2.0f` が `-2` と出ています。既定の書式では、小数部が 0 のときに末尾の 0 を省きます。桁をそろえたいときは、[`fixed`](fixed.md) と [`setprecision`](setprecision.md) を使います。

### 出力先を差し替える {#rdbuf}

`cout` のバッファを入れ替えると、画面に出るはずの内容を、文字列で受け取れます。テストで出力を確かめたいときに便利です。

```cpp
#include <iostream>
#include <print>
#include <sstream>

int main() {
  std::ostringstream sink;
  auto* old = std::cout.rdbuf(sink.rdbuf());  // 出力先を sink に向ける
  std::cout << "HP " << 30 << '\n';
  std::cout.rdbuf(old);                       // 元に戻す

  std::println("受け取った内容: {:?}", sink.str());
}
```

```text title="実行結果"
受け取った内容: "HP 30\n"
```

`rdbuf` は、差し替える前のバッファを返します。必ず元に戻してください。戻さないまま `sink` が破棄されると、`cout` が壊れたバッファを指したままになります。

## ゲームでの使いどころ

古いコードやサンプルを読むときに必ず出会います。デバッグ表示に `std::cout << "x = " << x << '\n';` と書くのが典型です。

ゲーム本体のログは、ふつうゲーム用のログ機能にまとめて、`cout` を直接は使いません。コンソールのない Windows アプリ（`WinMain`）では、`cout` に書いても何も見えないので、Visual Studio の出力ウィンドウに出す `OutputDebugString` を使います。

新しく書くなら、`std::println("x = {}", x);` が短く、桁数の指定も書式文字列に書けます。

## よくあるミス

??? failure "endl を多用して遅くなる"
    `std::endl` は改行と `flush` を毎回行います。大量の行をファイルへリダイレクトして出すときは、`"\n"` との差がはっきり出ます。普通の改行は `"\n"` にして、確実に出したい所だけ `flush` を呼びます。

??? failure "setprecision の指定が、あとの出力にも効いてしまう"
    `setw` 以外の操作子は、次の出力で自動では戻りません。表示のためだけに `fixed` や `setprecision` を流したら、同じ関数の中で元に戻すか、`std::format` や `println` で書式を 1 回ごとに指定します。

??? failure "printf と混ぜて順序が乱れる"
    `std::ios::sync_with_stdio(false)` を呼ぶと、`printf` との順序が保証されなくなります。呼ぶなら、プログラムの最初に 1 回だけにして、以降は `cout` だけ（または `printf` だけ）にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::println`](../utilities/print.md) | 書式つき出力。新しいコードはこちら |
| [`std::cerr`](cerr.md) | 標準エラー出力。バッファなしで、すぐ出る |
| [`std::clog`](clog.md) | 標準エラー出力。バッファあり |
| [`std::wcout`](wcout.md) | `wchar_t` 版 |
| [`std::cin`](cin.md) | 標準入力 |

## コンパイラ対応

C++98 から使えます。手元の MSVC（Visual Studio 2026）で動作を確かめました。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `cout` は標準出力のストリーム。`<<` で値をつなげて出す
    - [x] 改行は `"\n"`。`endl` は毎回 `flush` するので、大量に出す所では避ける
    - [x] 自作の型は、`std::ostream&` を受け取って返す `operator<<` を作る
    - [x] 新しいコードは `std::println`

## 関連ページ

- [cpprefjp: std::cout](https://cpprefjp.github.io/reference/iostream/cout.html)
- [cppreference: std::cout](https://en.cppreference.com/w/cpp/io/cout)
