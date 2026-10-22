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

`std::cin` は、**標準入力（キーボードなど）から値を読む**ストリームです。`std::cin >> x;` のように、`>>` で型に合わせて読みます。空白で区切られます。ゲームでは、コンソールのツールや、競技プログラミング的な入力を扱うときに使います。

!!! tip "ポイント"
    - `>>` は空白（スペース・改行）で区切って読む。1 行まるごとなら [`std::getline`](getline.md)。
    - 読み取りに失敗すると `failbit` が立ち、以降の読み込みが全部失敗する（`clear()` が必要）。
    - 大量に読むなら `std::ios::sync_with_stdio(false)` で高速化できる。

## 関数の詳しい説明

### std::cin {#cin}

```cpp
extern std::istream cin;
```

- 標準入力（キーボード）。`>>` で読みます。ゲーム本体ではなく、練習用のプログラムやツールで使います

### operator>> {#shift-in}

```cpp
std::istream& operator>>(std::istream& is, int& value);  // 型ごとにある
```

- 空白・改行を飛ばして、次の値を読みます。読めなければ失敗状態になり、そのあとの `>>` は全部何もしなくなります

```cpp
#include <iostream>
#include <sstream>

int main() {
  std::istringstream input("10 abc 30");  // キーボードの代わり
  int a = 0;
  int b = 0;
  input >> a;
  input >> b;  // "abc" は数値にできないので失敗
  std::cout << a << ' ' << b << ' ' << input.fail() << '\n';
}
```

```text title="実行結果"
10 0 1
```

### std::cin.tie {#tie}

```cpp
std::ostream* tie(std::ostream* os);
```

- 普段は cin で読む前に cout が flush されます（質問文が先に出るように）。`std::cin.tie(nullptr)` でやめると速くなります

### std::cin.ignore {#ignore}

```cpp
std::istream& ignore(std::streamsize n = 1, int delim = EOF);
```

- 入力を `n` 文字（または `delim` まで）読み飛ばします。`>>` のあとに残った改行を捨てるのに使います

### std::ios::sync_with_stdio {#sync_with_stdio}

```cpp
static bool sync_with_stdio(bool sync = true);
```

- `false` にすると、C の `printf` / `scanf` との同期をやめて、cin / cout が速くなります。その後は C の関数と混ぜて使ってはいけません

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| コンソールツールの入力 | `std::cin >> command;` |

## よくあるミス

??? failure "数値の入力に文字を打たれる"
    `failbit` が立ち、以降が読めなくなります。`if (!(std::cin >> n))` で確認し、`clear()` と `ignore()` で復帰します。

??? failure ">> のあとに getline すると空行が読める"
    `>>` は改行を残すので、直後の `getline` は空文字を読みます。間に `std::cin.ignore()` を挟みます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::getline`](getline.md) | 1 行読む |
| [`std::cout`](cout.md) | 標準出力 |
| [`std::ifstream`](ifstream.md) | ファイルから読む |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 標準入力のストリーム
    - [x] 空白区切りで読む
    - [x] 失敗したら `clear()` が必要

## 関連ページ

- [cpprefjp: std::cin](https://cpprefjp.github.io/reference/iostream/cin.html)
- [cppreference: std::cin](https://en.cppreference.com/w/cpp/io/cin)
