---
title: std::cout / std::cin（iostream）
tags:
  - 入出力
---

# std::cout / std::cin（iostream）

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-2">△ やや重い</span>
<span class="ver ver-11">C++98〜</span>
`#include <iostream>` / `#include <iomanip>`
</div>

`<iostream>` は、**画面への出力（`std::cout`）とキーボードからの入力（`std::cin`）**のためのライブラリです。`<<` で値を流し込んで出力し、`>>` で値を読み込みます。昔からある C++ の入出力の方法で、教科書や古いコードでよく見かけます。C++23 では出力に [`std::println`](../utilities/format.md) が使えるので、**出力は println、入力は cin** と使い分けるのが今の書き方です。

!!! tip "結論"
    - 出力は C++23 なら `std::println` のほうが短くて速い。`std::cout` は古いコードを読むために知っておく。
    - `std::endl` は改行 + **flush（毎回書き出し）**で遅い。改行だけなら `'\n'`。
    - 入力は `std::cin >> x;`、1 行まるごとなら `std::getline(std::cin, line);`。
    - 桁数や 16 進数などの書式は、`std::format` の書式指定のほうが分かりやすい。iostream ではマニピュレータ（`std::setw` など）を使う。

## 主なオブジェクト

| 名前 | 重要度 | 何をする |
| --- | --- | --- |
| [`std::cout`](#cout) | <span class="rank rank-often">よく使う</span> | 標準出力（画面） |
| [`std::cin`](#cin) | <span class="rank rank-often">よく使う</span> | 標準入力（キーボード） |
| [`std::cerr`](#cerr) | <span class="rank rank-sometimes">たまに</span> | エラー出力（すぐ出る） |
| [`std::clog`](#clog) | <span class="rank rank-rare">知ってるだけ</span> | ログ出力 |

## 関数一覧

| 関数 | 重要度 | 何をする |
| --- | --- | --- |
| [`operator<<`](#shift-out) | <span class="rank rank-must">必須</span> | 出力する |
| [`operator>>`](#shift-in) | <span class="rank rank-often">よく使う</span> | 入力を読む |
| [`std::getline`](#getline) | <span class="rank rank-often">よく使う</span> | 1 行読む |
| [`std::endl`](#endl) | <span class="rank rank-often">よく使う</span> | 改行して flush |
| [`std::setw`](#setw) | <span class="rank rank-sometimes">たまに</span> | 次の値の幅 |
| [`std::setprecision`](#setprecision) | <span class="rank rank-sometimes">たまに</span> | 小数の桁数 |
| [`std::setfill`](#setfill) | <span class="rank rank-sometimes">たまに</span> | 埋める文字 |
| [`std::ios::sync_with_stdio`](#sync_with_stdio) | <span class="rank rank-sometimes">たまに</span> | C の入出力との同期を切って速くする |
| [`std::cin.tie`](#tie) | <span class="rank rank-rare">知ってるだけ</span> | 入力の前に出力を flush する設定 |
| [`std::cin.ignore`](#ignore) | <span class="rank rank-rare">知ってるだけ</span> | 入力を読み飛ばす |
| [`std::flush`](#flush) | <span class="rank rank-rare">知ってるだけ</span> | 改行せずに flush |

## よくある使い方

```cpp
#include <iomanip>
#include <iostream>
#include <string>

int main() {
  std::string name = "Alice";
  int hp = 45;
  double rate = 37.456;

  std::cout << name << " HP " << hp << '\n';
  std::cout << std::fixed << std::setprecision(1) << rate << "%\n";
  std::cout << '[' << std::setw(5) << std::setfill('0') << 42 << "]\n";
  std::cout << std::hex << 255 << std::dec << ' ' << 255 << '\n';
}
```

```text title="実行結果"
Alice HP 45
37.5%
[00042]
ff 255
```

同じことを `std::println` で書くと次のようになります。

```cpp
std::println("{} HP {}", name, hp);
std::println("{:.1f}%", rate);
std::println("[{:05}]", 42);
std::println("{:x} {}", 255, 255);
```

## 関数の詳しい説明

### std::cout {#cout}

```cpp
extern std::ostream cout;
```

- 標準出力（コンソール画面）。`<<` で値を流し込みます

### std::cin {#cin}

```cpp
extern std::istream cin;
```

- 標準入力（キーボード）。`>>` で読みます。ゲーム本体ではなく、練習用のプログラムやツールで使います

### std::cerr {#cerr}

```cpp
extern std::ostream cerr;
```

- エラー用の出力。バッファにためずに**すぐ**出るので、落ちる直前のメッセージも残ります

### std::clog {#clog}

```cpp
extern std::ostream clog;
```

- ログ用の出力。cerr と同じ出力先ですが、バッファにためます

### operator<< {#shift-out}

```cpp
std::ostream& operator<<(std::ostream& os, int value);  // 型ごとにある
```

- 値を文字にして出力します。戻り値が同じストリームなので、`<<` を続けて書けます
- 自作の型も `operator<<` を定義すれば出力できます

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

### std::getline {#getline}

```cpp
std::istream& getline(std::istream& in, std::string& str, char delim = '\n');
```

- 空白を含めて 1 行読みます。名前の入力などに使います

### std::endl {#endl}

```cpp
std::ostream& endl(std::ostream& os);
```

- 改行して、**flush**（たまった出力をすぐ書き出す）します。flush は遅いので、ループの中で毎回使うと大量の出力が遅くなります

!!! note "実際は"
    普段は `'\n'` で改行し、すぐ出したいときだけ `std::flush` を使います。

### std::setw {#setw}

```cpp
/* unspecified */ setw(int n);  // <iomanip>
```

- **次の 1 つだけ**、最低 `n` 文字の幅で出力します（右寄せ）

### std::setprecision {#setprecision}

```cpp
/* unspecified */ setprecision(int n);  // <iomanip>
```

- 浮動小数点の桁数。`std::fixed` と一緒に使うと「小数点以下 n 桁」、単独だと「全体で n 桁」。**以後ずっと**効きます

### std::setfill {#setfill}

```cpp
/* unspecified */ setfill(char c);  // <iomanip>
```

- `setw` で余った部分を埋める文字。以後ずっと効きます

### std::ios::sync_with_stdio {#sync_with_stdio}

```cpp
static bool sync_with_stdio(bool sync = true);
```

- `false` にすると、C の `printf` / `scanf` との同期をやめて、cin / cout が速くなります。その後は C の関数と混ぜて使ってはいけません

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

### std::flush {#flush}

```cpp
std::ostream& flush(std::ostream& os);
```

- 改行せずに、たまった出力をすぐ書き出します

## フラグ・オプション（書式フラグとマニピュレータ）

`std::cout << マニピュレータ` の形で、以後の出力の書き方を変えます（`setw` 以外は**ずっと効く**）。よく使う順です。

| マニピュレータ | 重要度 | 意味 | 元に戻すには |
| --- | --- | --- | --- |
| `std::fixed` | <span class="rank rank-often">よく使う</span> | 小数を固定小数点で（`setprecision` と組み合わせる） | `std::defaultfloat` |
| `std::setprecision(n)` | <span class="rank rank-often">よく使う</span> | 小数の桁数 | もう一度指定 |
| `std::setw(n)` | <span class="rank rank-often">よく使う</span> | 次の 1 つの幅 | （次で自動的に戻る） |
| `std::setfill(c)` | <span class="rank rank-sometimes">たまに</span> | 埋める文字 | `std::setfill(' ')` |
| `std::hex` / `std::dec` / `std::oct` | <span class="rank rank-sometimes">たまに</span> | 整数を 16 / 10 / 8 進数で | `std::dec` |
| `std::left` / `std::right` | <span class="rank rank-sometimes">たまに</span> | 左寄せ / 右寄せ | `std::right` |
| `std::boolalpha` | <span class="rank rank-sometimes">たまに</span> | bool を `true` / `false` で（普段は `1` / `0`） | `std::noboolalpha` |
| `std::showpos` | <span class="rank rank-rare">知ってるだけ</span> | 正の数にも `+` | `std::noshowpos` |
| `std::uppercase` | <span class="rank rank-rare">知ってるだけ</span> | 16 進数や指数を大文字で | `std::nouppercase` |
| `std::showbase` | <span class="rank rank-rare">知ってるだけ</span> | `0x` などを付ける | `std::noshowbase` |
| `std::scientific` | <span class="rank rank-rare">知ってるだけ</span> | 指数表記 | `std::defaultfloat` |
| `std::showpoint` | <span class="rank rank-rare">知ってるだけ</span> | 整数値の小数にも `.` を付ける | `std::noshowpoint` |
| `std::internal` | <span class="rank rank-rare">知ってるだけ</span> | 符号と数字の間を埋める | `std::right` |
| `std::ws` | <span class="rank rank-sometimes">たまに</span> | （入力）空白を読み飛ばす | |
| `std::skipws` / `std::noskipws` | <span class="rank rank-rare">知ってるだけ</span> | （入力）`>>` で空白を飛ばすか | |
| `std::put_money` / `std::put_time` など | <span class="rank rank-rare">知ってるだけ</span> | 通貨・時刻の書式 | |

```cpp
#include <iomanip>
#include <iostream>

int main() {
  std::cout << std::boolalpha << true << ' ' << std::showpos << 5 << std::noshowpos << '\n';
  std::cout << std::left << std::setw(6) << "HP" << '|' << '\n';
  std::cout << std::showbase << std::uppercase << std::hex << 255 << '\n';
}
```

```text title="実行結果"
true +5
HP    |
0XFF
```

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    std::cout << "HP " << hp << "/" << max_hp << std::endl;
    std::cout << std::fixed << std::setprecision(2) << rate << std::endl;
    ```

=== "今の書き方（C++23）"

    ```cpp
    std::println("HP {}/{}", hp, max_hp);
    std::println("{:.2f}", rate);
    ```

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| デバッグ出力 | `std::println` のほうがおすすめ。古いコードでは cout |
| コンソールのツール | コンバータ、データチェッカーの入力に cin |
| 自作型の出力 | `operator<<` を定義すると、ログやテストで使える |

## よくあるミス

??? failure "endl を大量に使って遅くなる"
    1 万行のログを `std::endl` で出すと、1 万回 flush が起きて遅くなります。

??? failure "マニピュレータが戻らない"
    `std::hex` や `std::setprecision` はずっと効くので、あとの出力まで 16 進数になってしまいます。使い終わったら戻します。

??? failure "cin の失敗を放置する"
    数値を入れるところに文字を入れると、`cin` が失敗状態になり、そのあとの入力が全部無視されます。`std::cin.clear()` と `ignore` で回復します。

## 理解度チェック

!!! question "Q1. `std::cout << std::setw(4) << 7 << 8;` の出力は？"
    <div class="spoiler" markdown>

    **答え:** `   78`。`setw` は次の 1 つ（7）にだけ効きます。

    </div>

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::print` / `std::println`](../utilities/format.md) | C++23。書式が分かりやすく速い |
| `printf` | C の関数。型のチェックが無い |
| [`std::stringstream`](sstream.md) | 文字列に対して同じ書き方をする |

## コンパイラ対応

C++98 からある機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 出力は C++23 なら println。cout は読めれば OK
    - [x] 改行は `'\n'`。endl は flush するので遅い
    - [x] マニピュレータはずっと効く（setw 以外）

## 関連ページ

- [std::format / std::print](../utilities/format.md)
- [cppreference: Input/output manipulators](https://en.cppreference.com/w/cpp/io/manip)
