---
title: std::hexfloat
summary: "浮動小数点数を、16 進の指数表記で出力する。"
order: 900
tags:
  - 入出力・文字列
---

# std::hexfloat

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <ios>`
</div>

`0.1` を 10 進数で書くと、0.1 ちょうどに見えます。ところが、コンピューターが持っている 0.1 は 2 進数の近似値で、10 進数の文字に直すときには丸めが入ります。そのため、書き出した文字を読み戻しても、同じ値にならないことがあります。`std::hexfloat` は、値を 16 進数の浮動小数点表記で出力する設定で、丸めなしに、ビットそのままの値を文字にできます。

!!! tip "ポイント"
    - `0x1.999999999999ap-4` のような、16 進の仮数と、2 のべき乗の指数で出力する
    - 10 進では誤差が出る値も、正確に書き出して、読み戻せる
    - 桁数や書き方は、処理系で違う（MSVC は `0x1.0000000000000p+0`、GCC は `0x1p+0`）
    - 戻すには `defaultfloat`

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::hexfloat {#hexfloat}

```cpp
std::ios_base& hexfloat(std::ios_base& str);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | `ios_base&` | 設定を変えるストリーム |

`str.setf(std::ios_base::fixed | std::ios_base::scientific, std::ios_base::floatfield)` を呼びます。`fixed` と `scientific` の両方を立てる、というのが、`hexfloat` を表す特別な組み合わせです。設定は残り続けるので、戻すには [`defaultfloat`](defaultfloat.md) を呼びます。

出力の形は、`0x1.8p+1` のようになります。`0x` のあとの `1.8` が 16 進の仮数（1 と 8/16 で 1.5）、`p+1` が 2 の 1 乗を掛けるという意味で、この例は 1.5 × 2 = 3 です。

## 実際に動かしてみる

```cpp
#include <iostream>
#include <print>
#include <sstream>
#include <string>

int main() {
  std::cout << std::hexfloat << 1.0 << ' ' << 0.5 << ' ' << 3.5 << '\n';
  std::cout << 0.1 << '\n';

  // 10 進数の 0.1 は、2 進数では割り切れない
  std::ostringstream os;
  os << std::hexfloat << 0.1;
  double back = std::stod(os.str());
  std::println("{} → {}", os.str(), back == 0.1);

  // 10 進で桁数を決めて書くと、元に戻らないことがある
  std::ostringstream os2;
  os2.precision(6);
  os2 << 0.1 + 0.2;
  std::println("{} → {}", os2.str(), std::stod(os2.str()) == 0.1 + 0.2);

  std::ostringstream os3;
  os3 << std::hexfloat << 0.1 + 0.2;
  std::println("{} → {}", os3.str(), std::stod(os3.str()) == 0.1 + 0.2);
}
```

```text title="実行結果"
0x1.0000000000000p+0 0x1.0000000000000p-1 0x1.c000000000000p+1
0x1.999999999999ap-4
0x1.999999999999ap-4 → true
0.3 → false
0x1.3333333333334p-2 → true
```

1 行目は、MSVC が仮数を 13 桁の 16 進数にそろえて出した形です。GCC の libstdc++ なら `0x1p+0 0x1p-1 0x1.cp+1` のように、末尾のゼロを省きます。値は同じで、出力の桁数が処理系で変わります。

`0.1 + 0.2` を 6 桁の 10 進数にすると `0.3` になり、読み戻した値は元の `0.1 + 0.2` と等しくありません。`hexfloat` で書いた場合は、読み戻すと等しい値になります。

読み戻すのに、ここでは `std::stod` を使いました。`stod` は、`0x` から始まる 16 進の浮動小数点表記も読めます。ストリームの `>> std::hexfloat` で読む方法は、処理系によって読めない実装があるので、`stod` か、`std::from_chars(…, std::chars_format::hex)` を使うほうが確実です。

## ゲームでの使いどころ

浮動小数点の値を、テキストで保存し、読み戻したときに 1 ビットも変わってはいけない場面です。物理シミュレーションのリプレイ データ、決定的な動きを要求されるネットワーク対戦の状態保存などです。10 進数で保存すると、ごくわずかなずれが積み重なって、再現した動きが変わることがあります。

人が読んで直す設定ファイルには向きません。値が `0x1.8p+1` では、何の数か見当がつかないからです。人が読むなら 10 進数で、桁数を `std::numeric_limits<double>::max_digits10`（17）にしておくと、読み戻しても元に戻ります。

## よくあるミス

??? failure "出力の文字が、環境によって違うと言われた"
    仮数の桁数が処理系で違うためです。文字列そのものの一致ではなく、読み戻した値を比べてください。

??? failure "`defaultfloat` に戻し忘れて、あとの出力がすべて 16 進になった"
    `hexfloat` の設定は残り続けます。必要な出力が終わったら、`std::defaultfloat` を流します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fixed`](fixed.md) | 小数点表記。桁数は小数点以下の桁数 |
| [`scientific`](scientific.md) | 10 進の指数表記（`1.5e+00`） |
| [`defaultfloat`](defaultfloat.md) | 既定の形式に戻す |
| [`chars_format`](chars_format.md) | `to_chars`・`from_chars` で 16 進を選ぶ列挙型 |

## コンパイラ対応

C++11 から使えます。手元の MSVC（Visual Studio 2026）で動作を確かめました。出力の桁数は処理系で違います。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `hexfloat` は、浮動小数点を 16 進の指数表記で出力する設定
    - [x] 丸めが入らないので、書き出した文字から、元の値を正確に読み戻せる
    - [x] 桁数は処理系で違う。読み戻すには `stod` か `from_chars` を使う

## 関連ページ

- [cpprefjp: std::hexfloat](https://cpprefjp.github.io/reference/ios/hexfloat.html)
- [cppreference: std::hexfloat](https://en.cppreference.com/w/cpp/io/manip/hexfloat)
