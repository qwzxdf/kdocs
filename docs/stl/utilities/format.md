---
title: std::format
summary: "`{}` を使って、文字列を整形する（`printf` の安全版）。書式の書き方を一通りまとめている。"
order: 47
tags:
  - ユーティリティ
  - 文字列
---

# std::format

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-20">C++20</span>
`#include <format>`
</div>

`std::format` は、**`{}` の場所に値を埋め込んで文字列を作る**関数です。同じ書き方でそのまま画面に出すのは [`std::println`](print.md) です。。`printf` のように型ごとの `%d` / `%f` を覚える必要がなく、型の間違いはコンパイル時にエラーになります。桁数・幅・寄せ方・16 進数なども `{:...}` の中で指定できます。

!!! tip "ポイント"
    - <strong>表示は [`std::println`](print.md)、文字列が欲しいときは `std::format(...)`。</strong>
    - 小数の桁は `{:.1f}`、幅をそろえるなら `{:>5}`、0 埋めは `{:03}`、16 進数は `{:x}`。
    - vector や map もそのまま `{}` で出せる（C++23）。
    - 書式の文字列は**コンパイル時に決まっている必要がある**（変数にするなら [`std::vformat`](vformat.md)）。自作の型は [`std::formatter`](formatter.md)。

## 関数一覧

| 関数 | 重要度 | 何をする | ヘッダ |
| --- | --- | --- | --- |
| [`std::println`](print.md) | <span class="rank rank-must">必須</span> | 書式に従って出力し、改行する <span class="ver ver-23">C++23</span> | `<print>` |
| [`std::format_to`](format_to.md) | <span class="rank rank-sometimes">たまに</span> | 既にある場所に書き込む | `<format>` |
| [`std::formatter`](formatter.md) | <span class="rank rank-sometimes">たまに</span> | 自作の型を `{}` で出せるようにする | `<format>` |
| [`std::vformat`](vformat.md) | <span class="rank rank-rare">知ってるだけ</span> | 書式を実行時に決める | `<format>` |
| [`std::format`](#format) | <span class="rank rank-must">必須</span> | 書式に従って文字列を作る <span class="ver ver-20">C++20</span> | `<format>` |

## よくある使い方

### 1. 表示する

```cpp
#include <print>
#include <string>

int main() {
  std::string name = "Alice";
  int hp = 45;
  int max_hp = 120;
  float rate = 37.5f;

  std::println("{} HP {}/{}", name, hp, max_hp);
  std::println("命中率 {:.1f}%", rate);
  std::println("{{}} は波かっこそのもの");
}
```

```text title="実行結果"
Alice HP 45/120
命中率 37.5%
{} は波かっこそのもの
```

### 2. 表をそろえて出す

```cpp
#include <print>
#include <string>
#include <vector>

struct Row {
  std::string name;
  int score;
};

int main() {
  std::vector<Row> rows = {{"Alice", 980}, {"Bob", 75}, {"Carol", 1200}};
  for (const auto& r : rows) {
    std::println("{:<8}|{:>6}", r.name, r.score);  // 左寄せ 8 桁、右寄せ 6 桁
  }
}
```

```text title="実行結果"
Alice   |   980
Bob     |    75
Carol   |  1200
```

### 3. UI のテキストを作る

```cpp
#include <format>
#include <print>
#include <string>

int main() {
  int seconds = 125;
  std::string timer = std::format("{:02}:{:02}", seconds / 60, seconds % 60);
  std::string gold = std::format("{:>8} G", 1500);
  std::println("[{}] [{}]", timer, gold);
}
```

```text title="実行結果"
[02:05] [    1500 G]
```

## 関数の詳しい説明

### std::format <span class="ver ver-20">C++20</span> {#format data-toc-label="std::format"}

```cpp
template <class... Args>
std::string format(std::format_string<Args...> fmt, Args&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `fmt` | 書式文字列 | `{}` を含む文字列 |
| `args` | 何個でも | 埋め込む値 |

- 戻り値: 新しい `std::string`
- 書式と引数が合わないとコンパイルエラー

```cpp
#include <format>
#include <print>
#include <string>

int main() {
  std::string path = std::format("stage{:02}.json", 7);
  std::println("{}", path);
}
```

```text title="実行結果"
stage07.json
```

## フラグ・オプション（書式指定）

`{}` の中には、`{番号:書式}` の形で細かい指定が書けます。書式は次の順番で並べます（全部省略できる）。

```text
{ 番号 : 埋め文字 寄せ 符号 # 0 幅 .精度 L 型 }
```

### 番号 {#spec-index}

| 書き方 | 意味 |
| --- | --- |
| `{}` | 引数を先頭から順番に使う |
| `{0}`, `{1}` | 何番目の引数かを指定する（同じ引数を何度も使える）。`{}` と混ぜることはできない |

```cpp
#include <print>

int main() {
  std::println("{0} と {1}、もう一度 {0}", "A", "B");
}
```

```text title="実行結果"
A と B、もう一度 A
```

### 寄せ・埋め文字 {#spec-align}

| 書き方 | 重要度 | 意味 |
| --- | --- | --- |
| `>` | <span class="rank rank-must">必須</span> | 右寄せ（数値のデフォルト） |
| `<` | <span class="rank rank-must">必須</span> | 左寄せ（文字列のデフォルト） |
| `^` | <span class="rank rank-often">よく使う</span> | 中央寄せ |
| 文字 + 寄せ（`*>`、`-^` など） | <span class="rank rank-sometimes">たまに</span> | 空白の代わりにその文字で埋める（`{` `}` 以外なら何でも） |

```cpp
#include <print>

int main() {
  std::println("[{:>6}]", 42);
  std::println("[{:<6}]", 42);
  std::println("[{:^6}]", 42);
  std::println("[{:*^9}]", "GO");
}
```

```text title="実行結果"
[    42]
[42    ]
[  42  ]
[***GO****]
```

### 幅 {#spec-width}

| 書き方 | 重要度 | 意味 |
| --- | --- | --- |
| 数字（`{:5}`） | <span class="rank rank-must">必須</span> | 最低この文字数にする（足りなければ埋める。長い場合は切らない） |
| `{:{}}` | <span class="rank rank-rare">知ってるだけ</span> | 幅を引数で渡す |

### 0 埋め {#spec-zero}

| 書き方 | 重要度 | 意味 |
| --- | --- | --- |
| `0` + 幅（`{:03}`） | <span class="rank rank-must">必須</span> | 数値を 0 で埋める（符号や `0x` の後ろに 0 が入る） |

```cpp
#include <print>

int main() {
  std::println("{:03} {:05} {:08.3f}", 7, -42, 3.14159);
}
```

```text title="実行結果"
007 -0042 0003.142
```

### 精度 {#spec-precision}

| 書き方 | 重要度 | 型 | 意味 |
| --- | --- | --- | --- |
| `.n`（`{:.2f}`） | <span class="rank rank-must">必須</span> | 浮動小数点 | 小数点以下 n 桁（`f` のとき）。四捨五入される |
| `.n`（`{:.3}`） | <span class="rank rank-sometimes">たまに</span> | 文字列 | 先頭 n 文字まで（はみ出しを切る） |
| `.{}` | <span class="rank rank-rare">知ってるだけ</span> | | 精度を引数で渡す |

```cpp
#include <print>

int main() {
  std::println("{:.2f} {:.0f} {:.3}", 1.005, 2.5, "abcdef");
}
```

```text title="実行結果"
1.00 2 abc
```

`1.005` が `1.00` になるのは、浮動小数点では 1.005 がぴったり表せず、少し小さい値になっているためです。`2.5` が `2` になるのは「偶数への丸め」です。

### 符号 {#spec-sign}

| 書き方 | 重要度 | 意味 |
| --- | --- | --- |
| `-`（省略時） | <span class="rank rank-must">必須</span> | マイナスのときだけ `-` を付ける |
| `+` | <span class="rank rank-often">よく使う</span> | プラスのときも `+` を付ける（ダメージ・回復量の表示に便利） |
| 空白（`{: }`） | <span class="rank rank-rare">知ってるだけ</span> | プラスのときは空白を付ける（桁をそろえる） |

```cpp
#include <print>

int main() {
  std::println("{:+} {:+} {: } {: }", 30, -12, 5, -5);
}
```

```text title="実行結果"
+30 -12  5 -5
```

### # （代替形式） {#spec-alt}

| 書き方 | 重要度 | 意味 |
| --- | --- | --- |
| `#x` / `#b` / `#o` | <span class="rank rank-sometimes">たまに</span> | `0x` / `0b` / `0` を前に付ける |
| `#` + 浮動小数点 | <span class="rank rank-rare">知ってるだけ</span> | 小数点が無くても `.` を付ける |

### L （ロケール） {#spec-locale}

| 書き方 | 重要度 | 意味 |
| --- | --- | --- |
| `L` | <span class="rank rank-rare">知ってるだけ</span> | 国ごとの書き方（3 桁区切りなど）にする。ロケールの設定が必要で、ゲームではほぼ使わない |

### 型：整数 {#spec-int}

| 書き方 | 重要度 | 意味 | `255` の例 |
| --- | --- | --- | --- |
| （省略）/ `d` | <span class="rank rank-must">必須</span> | 10 進数 | `255` |
| `x` | <span class="rank rank-often">よく使う</span> | 16 進数（小文字） | `ff` |
| `X` | <span class="rank rank-often">よく使う</span> | 16 進数（大文字） | `FF` |
| `b` | <span class="rank rank-sometimes">たまに</span> | 2 進数 | `11111111` |
| `B` | <span class="rank rank-rare">知ってるだけ</span> | 2 進数（`#B` で `0B` が付く） | `11111111` |
| `o` | <span class="rank rank-rare">知ってるだけ</span> | 8 進数 | `377` |
| `c` | <span class="rank rank-rare">知ってるだけ</span> | その文字コードの文字として出す | （`65` なら `A`） |

```cpp
#include <print>

int main() {
  int color = 0xFF8800;
  std::println("#{:06X} / {:#x} / {:08b} / {:c}", color, 255, 5, 65);
}
```

```text title="実行結果"
#FF8800 / 0xff / 00000101 / A
```

### 型：浮動小数点 {#spec-float}

| 書き方 | 重要度 | 意味 | `1234.5678` の例 |
| --- | --- | --- | --- |
| （省略） | <span class="rank rank-must">必須</span> | 元の値に戻せる一番短い表記 | `1234.5678` |
| `f` | <span class="rank rank-must">必須</span> | 固定小数点（精度省略時は 6 桁） | `1234.567800` |
| `e` | <span class="rank rank-sometimes">たまに</span> | 指数表記 | `1.234568e+03` |
| `g` | <span class="rank rank-sometimes">たまに</span> | `f` と `e` の短いほう（精度省略時は 6 桁） | `1234.57` |
| `F` / `E` / `G` | <span class="rank rank-rare">知ってるだけ</span> | 大文字版（`INF`、`E+03` など） | `1.234568E+03` |
| `a` / `A` | <span class="rank rank-rare">知ってるだけ</span> | 16 進数の浮動小数点 | `1.34a4560418937p+10` |

```cpp
#include <print>

int main() {
  double v = 1234.5678;
  std::println("{} | {:f} | {:.2f} | {:e} | {:g}", v, v, v, v, v);
}
```

```text title="実行結果"
1234.5678 | 1234.567800 | 1234.57 | 1.234568e+03 | 1234.57
```

### 型：文字列・文字・bool・ポインタ {#spec-other}

| 対象 | 書き方 | 重要度 | 意味 |
| --- | --- | --- | --- |
| 文字列 | （省略）/ `s` | <span class="rank rank-must">必須</span> | そのまま |
| 文字列 | `?` | <span class="rank rank-rare">知ってるだけ</span> | `"` で囲み、改行などをエスケープして出す（デバッグ用） <span class="ver ver-23">C++23</span> |
| 文字 | （省略）/ `c` | <span class="rank rank-often">よく使う</span> | 文字として |
| 文字 | `d` / `x` | <span class="rank rank-rare">知ってるだけ</span> | 文字コードの数値として |
| bool | （省略）/ `s` | <span class="rank rank-often">よく使う</span> | `true` / `false` |
| bool | `d` | <span class="rank rank-rare">知ってるだけ</span> | `1` / `0` |
| ポインタ | （省略）/ `p` | <span class="rank rank-sometimes">たまに</span> | アドレスを 16 進数で（`void*` にキャストが必要） |

```cpp
#include <print>

int main() {
  std::println("{} {:d} {:?} {:d}", true, false, "a\tb", 'A');
}
```

```text title="実行結果"
true 0 "a\tb" 65
```

### 範囲（vector・map など） <span class="ver ver-23">C++23</span> {#spec-range data-toc-label="範囲（vector・map など）"}

| 書き方 | 重要度 | 意味 |
| --- | --- | --- |
| `{}` | <span class="rank rank-often">よく使う</span> | `[1, 2, 3]`（map・set は `{...}`、文字列の要素は `"..."` で囲まれる） |
| `{:n}` | <span class="rank rank-sometimes">たまに</span> | 外側の `[]` を付けない |
| `{::書式}` | <span class="rank rank-sometimes">たまに</span> | 要素ごとの書式（`{::02}` で各要素を 0 埋め） |
| `{:s}` | <span class="rank rank-rare">知ってるだけ</span> | char の範囲を文字列として出す |
| `{:m}` | <span class="rank rank-rare">知ってるだけ</span> | pair の範囲を map 形式 `{a: b}` で出す |

```cpp
#include <map>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};
  std::map<int, char> m = {{1, 'a'}};
  std::println("{} | {:n} | {::02} | {}", v, v, v, m);
}
```

```text title="実行結果"
[1, 2, 3] | 1, 2, 3 | [01, 02, 03] | {1: 'a'}
```

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    printf("HP %d/%d\n", hp, max_hp);  // 型を間違えても動いて壊れる
    char buf[64];
    sprintf(buf, "%.1f%%", rate);      // バッファあふれの危険

    std::cout << name << " Lv." << level << std::endl;
    std::cout << std::setw(5) << std::setfill('0') << id << "\n";
    ```

=== "今の書き方（C++23）"

    ```cpp
    std::println("HP {}/{}", hp, max_hp);
    std::string s = std::format("{:.1f}%", rate);

    std::println("{} Lv.{}", name, level);
    std::println("{:05}", id);
    ```

## ゲームでの使いどころ

| 場面 | 書式 |
| --- | --- |
| HP・MP | `"{}/{}"` |
| タイマー | `"{:02}:{:02}"` |
| ダメージ表示 | `"{:+}"` |
| パーセント | `"{:.1f}%"` |
| 色コード | `"#{:06X}"` |
| デバッグ表示 | 自作型の formatter + `std::println` |
| ファイル名 | `"save{:02}.dat"` |

## パフォーマンス

- `std::format` は毎回新しい文字列を作る（メモリ確保が起きることがある）ので、毎フレーム何百回も呼ぶと重くなります。使い回すバッファに `std::format_to` で書くと確保を減らせます。
- `std::println` は内部で書式を整えてから一度に出力します。大量のログを毎フレーム出すとフレームレートが落ちます。

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| `{}` の数と引数が合わない（`std::format`） | コンパイルエラー |
| 型に合わない書式（文字列に `{:d}` など） | コンパイルエラー |
| `std::vformat` で書式が間違っている | `std::format_error` 例外 |

## よくあるミス

??? failure "書式文字列を変数にする"
    ```cpp
    std::string fmt = "HP {}";
    std::println(fmt, hp);  // コンパイルエラー: 書式はコンパイル時の定数でないといけない

    std::println("{}", std::vformat(fmt, std::make_format_args(hp)));  // OK
    ```

??? failure "{ をそのまま出そうとする"
    `{` を文字として出すには `{{`、`}` は `}}` と書きます。

??? failure "ポインタをそのまま渡してエラーになる"
    `std::println("{}", ptr)` は `void*` 以外のポインタだとコンパイルエラーです。`static_cast<const void*>(ptr)` にします。

??? failure "<print> が無い"
    `std::print` / `std::println` は C++23 です。使えない環境では `std::cout << std::format(...)` で代用します。

## 類似

| 名前 | 違い | こっちを使うとき |
| --- | --- | --- |
| `printf` | 型チェックが無い。速い | C の環境、古いコード |
| `std::cout` / `<<` | 書式指定が面倒 | ストリームが必要なとき |
| [`std::to_string`](../containers/to_string.md#to_string) | 数値 → 文字列だけ。書式を指定できない | 数値を 1 つ変換するだけ |

## コンパイラ対応

| 機能 | MSVC | GCC | Clang (libc++) |
| --- | --- | --- | --- |
| `std::format` <span class="ver ver-20">C++20</span> | VS 2019 16.10〜 | 13〜 | 17〜 |
| `std::print` / `println` <span class="ver ver-23">C++23</span> | VS 2022 17.7〜 | 14〜 | 18〜 |
| 範囲の出力（`{}` に vector） <span class="ver ver-23">C++23</span> | VS 2022 17.11〜 | 15〜 | 16〜 |
| `{:?}`（エスケープ出力） <span class="ver ver-23">C++23</span> | VS 2022 17.9〜 | 15〜 | 16〜 |

## これだけ覚える

!!! abstract "まとめ"
    - [x] 出すなら `std::println`、文字列なら `std::format`
    - [x] `{:.1f}` 小数、`{:>5}` 右寄せ、`{:03}` 0 埋め、`{:x}` 16 進、`{:+}` 符号
    - [x] `{` は `{{`
    - [x] 自作の型は `std::formatter` を書くと `{}` で出せる

## 関連ページ

- [cpprefjp: std::format](https://cpprefjp.github.io/reference/format/format.html)
- [cppreference: Standard format specification](https://en.cppreference.com/w/cpp/utility/format/spec)
