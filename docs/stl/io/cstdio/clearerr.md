---
title: std::clearerr
summary: "ファイルのエラー状態と終端状態をクリアする。"
order: 900
tags:
  - 入出力・文字列
---

# std::clearerr

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

読み込みでファイルの終わりに達したあと、そのファイルに別のプログラムが追記した。続きを読もうとしても、`feof` の印が残っているので、読み込みが止まったままになる。

`std::clearerr` は、<strong>終わりの印とエラーの印を、消す</strong>関数です。ログを追いかけて読み続ける `tail -f` のような処理で使います。

!!! tip "ポイント"
    - `feof` と `ferror` が示す印を、両方消す
    - ファイルの位置は変わらない。続きから読む
    - エラーの原因が解消していないと、また同じエラーになる
    - 戻り値はない

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::clearerr {#clearerr}

```cpp
void clearerr(std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | `FILE*` | 印を消すファイル |

終わりの印とエラーの印は、読み書きのたびに更新されますが、自動では消えません。一度終わりに達したファイルは、あとからデータが増えても、`clearerr` で印を消さない限り、読み込みが失敗し続けることがあります。

似た関数の [`rewind`](rewind.md) は、位置を先頭に戻したうえで、印も消します。`clearerr` は位置を動かさず、印だけを消すので、「今の位置から続きを読む」場合に使います。

エラーの印を消しても、原因が解決するわけではありません。ディスクの故障のようなエラーは、消してもまた起きます。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* w = std::fopen("grow.log", "w");
  std::fputs("line1\n", w);
  std::fflush(w);

  std::FILE* r = std::fopen("grow.log", "r");
  char buf[32];
  while (std::fgets(buf, sizeof(buf), r)) {}
  std::println("1 回目の終わり: {}", std::feof(r) != 0);

  std::fputs("line2\n", w);              // 別のところで追記された
  std::fflush(w);

  std::clearerr(r);                        // 印を消して、続きを読む
  std::println("clearerr の後: {}", std::feof(r) != 0);
  if (std::fgets(buf, sizeof(buf), r)) std::print("続き: {}", buf);

  std::fclose(r);
  std::fclose(w);
}
```

```text title="実行結果"
1 回目の終わり: true
clearerr の後: false
続き: line2
```

## ゲームでの使いどころ

ログ ビューアーのように、ファイルが伸びるのを追いかけて読むツールで使います。ゲームのログ ファイルを、別のウィンドウで監視する、デバッグ補助ツールの実装などです。

エラーが起きたあと、リトライする処理でも使います。印を消してから、同じ操作をやり直します。

## よくあるミス

??? failure "印を消さずに読み続けて、いつまでも読めない"
    終わりの印が残っていると、続きのデータがあっても、読み込みが止まることがあります。`clearerr` で消します。

??? failure "エラーの原因が残ったまま、`clearerr` だけして無限ループになる"
    原因が解消されていなければ、同じエラーが続きます。リトライの回数に上限を付けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`rewind`](rewind.md) | 位置を先頭に戻して、印も消す |
| [`feof`](feof.md) | 終わりの印を調べる |
| [`ferror`](ferror.md) | エラーの印を調べる |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 終わりとエラーの印を消す
    - [x] 位置は動かさない
    - [x] ログの追いかけ読みに使う

## 関連ページ

- [cpprefjp: std::clearerr](https://cpprefjp.github.io/reference/cstdio/clearerr.html)
- [cppreference: std::clearerr](https://en.cppreference.com/w/cpp/io/c/clearerr)
