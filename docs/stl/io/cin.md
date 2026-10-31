---
title: std::cin
summary: "標準入力。キーボードなどから値を読む（>> で読む）。"
order: 71
tags:
  - 入出力・文字列
---

# std::cin

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-11">C++98〜</span>
`#include <iostream>`
</div>

コンソールで動くツールに、レベル番号や名前を打ち込んでもらいたい。ファイルを開くまでもない、ちょっとした入力を受け取りたい。そんなときに使うのが標準入力の `std::cin` です。`std::cin >> level;` と書くと、打ち込まれた文字が、変数の型に合わせて数値などに変換されます。

ゲーム本体が `cin` を使うことはまずありません。練習用のプログラムや、コンソールの小さなツール、競技プログラミングの入力で出会います。便利な反面、入力が想定外だったときの挙動に癖があるので、その仕組みを知っておく必要があります。

!!! tip "ポイント"
    - `>>` は、空白（スペース・タブ・改行）で区切って読む。空白入りの 1 行は [`std::getline`](getline.md)
    - 読み取りに失敗すると `failbit` が立ち、以降の読み込みが全部失敗する。`clear()` で戻す
    - `>>` のあとの改行は入力に残る。直後に `getline` すると、空行が読める
    - 大量に読むなら `std::ios::sync_with_stdio(false)` と `cin.tie(nullptr)` で速くなる

!!! info "このページを読む前に"
    [`std::istream`](istream.md) が入力ストリームの基本です。出力側の [`std::cout`](cout.md) を先に読んでおくと、`<<` と `>>` の対応が分かりやすくなります。

## 関数の詳しい説明

### std::cin {#cin}

```cpp
extern std::istream cin;
```

`<iostream>` を読み込むと使える、グローバルなオブジェクトです。入力元は C の `stdin` と同じ標準入力で、普通はキーボードです。ファイルにリダイレクトして起動すれば（`game.exe < input.txt`）、そのファイルの中身を読みます。

入力は 1 行ごとにまとまってから渡されます。Enter を押すまでは、プログラムは読み込みで止まったままです。

### operator>> {#shift-in}

```cpp
std::istream& operator>>(std::istream& is, int& value);  // 型ごとにある
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `is` | `std::istream&` | 入力元のストリーム。`cin` を左に書くと、これに入る |
| `value` | 各種の型への参照 | 読んだ値を入れる変数 |

先頭の空白を読み飛ばして、次の空白までを 1 つの値として読みます。戻り値はストリーム自身の参照で、`cin >> a >> b` と続けて書けます。`if (std::cin >> n)` のように条件に書くと、読めたかどうかを確かめられます。

読めなかったとき、たとえば数値のつもりが `abc` だったときは、`failbit` が立ちます。この状態では、そのあとの `>>` が全部何もしません。失敗した変数は使わないようにします。

```cpp
#include <iostream>
#include <print>
#include <sstream>

int main() {
  std::istringstream input("10 abc 30");  // キーボードの代わり
  int a = 0;
  int b = 0;
  int c = 0;
  input >> a;
  input >> b;  // "abc" は数値にできないので失敗
  input >> c;  // 失敗状態では何も読まれない
  std::println("a={} b={} c={} fail={}", a, b, c, input.fail());
}
```

```text title="実行結果"
a=10 b=0 c=0 fail=true
```

`b` は 0 になり、その後ろの `30` も読まれませんでした。`c` が 30 にならないことに注意してください。失敗したあとで読み進めたいときは、`clear()` で状態を戻し、`ignore()` で壊れた部分を捨てます。

### std::cin.clear と std::cin.ignore {#recover}

```cpp
void clear(std::ios_base::iostate state = std::ios_base::goodbit);
std::istream& ignore(std::streamsize n = 1, int delim = EOF);
```

`clear()` は、失敗の旗（`failbit`）を下ろします。これだけでは、読めなかった文字が入力に残ったままなので、同じ所でまた失敗します。`ignore(n, delim)` で、最大 `n` 文字、または `delim` を読むまでを捨てます。

入力のやり直しは、この 2 つを組にします。

```cpp
#include <iostream>
#include <limits>
#include <print>
#include <sstream>

int main() {
  std::istringstream input("abc 7");
  int level = 0;
  while (!(input >> level)) {
    input.clear();  // 失敗状態を戻す
    // 次の空白まで捨てる
    input.ignore(std::numeric_limits<std::streamsize>::max(), ' ');
  }
  std::println("level = {}", level);
}
```

```text title="実行結果"
level = 7
```

`abc` で失敗して、`clear` と `ignore` で `abc ` を捨て、次の読み込みで `7` が読めました。`ignore` に `numeric_limits` の最大値を渡すのは、「区切りが出るまで何文字でも」という意味の決まり文句です。実際の `cin` では、区切りに `'\n'` を使って、その行をまるごと捨てます。

### std::cin.tie {#tie}

```cpp
std::ostream* tie(std::ostream* os);
```

`cin` は普段、`cout` と結び付いています。`cin` で読む前に `cout` が `flush` されるので、「名前を入力してください:」のような質問文が、先に画面に出ます。この結び付きをやめるのが `std::cin.tie(nullptr)` で、大量に読むときの無駄な `flush` がなくなります。そのかわり、質問文を出してから読むような、対話の入力では、質問が遅れて出ることがあります。

### std::ios::sync_with_stdio {#sync_with_stdio}

```cpp
static bool sync_with_stdio(bool sync = true);
```

`false` にすると、C の `printf` や `scanf` との同期をやめて、`cin` と `cout` が速くなります。最初の入出力の前に、1 回だけ呼びます。そのあとは、C の関数と混ぜて使ってはいけません。順番が入れ替わります。

## ゲームでの使いどころ

コンソールのツールで、コマンドを 1 行ずつ受け取るのが典型です。

```cpp
std::string line;
while (std::getline(std::cin, line)) {   // EOF まで 1 行ずつ
  // line を解析して処理する
}
```

`>>` で読むのは、数値だけが並んだ入力のときです。名前のような、空白が入るかもしれない文字列は、`getline` で 1 行読んでから、必要なら `istringstream` で分けます。1 行まるごと読んでから解析すると、失敗したときにやり直しやすくなります。

## よくあるミス

??? failure "数値の入力に文字を打たれて、無限ループになる"
    `failbit` が立つと、`>>` は何も読みません。ループの中で `clear()` だけして、`ignore()` を忘れると、同じ文字でまた失敗して、永遠に回ります。2 つを組にして呼びます。

??? failure ">> のあとに getline すると空行が読める"
    `>>` は、値の後ろの改行を入力に残します。直後の `getline` は、その改行までの空文字列を読んで返します。間に `std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n')` を挟みます。

??? failure "EOF のあとも読もうとする"
    入力が終わると、`eofbit` と `failbit` が立ちます。`while (!cin.eof())` で回すと、最後の 1 回が空振りになります。`while (std::cin >> x)` や `while (std::getline(std::cin, line))` のように、読み込みそのものを条件にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::getline`](getline.md) | 1 行まるごと読む。空白入りの文字列向き |
| [`std::cout`](cout.md) | 標準出力 |
| [`std::ifstream`](ifstream.md) | ファイルから読む |
| [`std::wcin`](wcin.md) | `wchar_t` 版 |

## コンパイラ対応

C++98 から使えます。手元の MSVC（Visual Studio 2026）で動作を確かめました。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `cin` は標準入力のストリーム。`>>` で空白区切りに読む
    - [x] 失敗したら `failbit` が立ち、`clear()` と `ignore()` の組で戻す
    - [x] `>>` のあとに `getline` するなら、間に改行を捨てる
    - [x] 読み込みそのものをループの条件にする

## 関連ページ

- [cpprefjp: std::cin](https://cpprefjp.github.io/reference/iostream/cin.html)
- [cppreference: std::cin](https://en.cppreference.com/w/cpp/io/cin)
