---
title: EXIT_FAILURE
summary: "失敗を表す終了コードのマクロ。"
order: 900
tags:
  - 数値
---

# EXIT_FAILURE

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

プログラムが失敗したことを呼び出した側（シェル、ビルドの仕組み、CI）に伝えるには、0 以外の終了コードを返します。`EXIT_FAILURE` は、<strong>異常終了を表す終了コード</strong>を名前で表すマクロです。

!!! tip "ポイント"
    - `EXIT_FAILURE` は異常終了を表す終了コード（普通は 1）
    - `std::exit(EXIT_FAILURE)` や、`main` の戻り値に使う
    - 正常終了は `EXIT_SUCCESS`
    - 呼び出し側が失敗を検出できる

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### EXIT_FAILURE {#exit_failure}

```cpp
#define EXIT_FAILURE /* 実装定義 */
```

`EXIT_FAILURE` は、異常終了を表す整数の定数です。多くの環境で 1 に展開されます。0 以外の値は「失敗」と解釈されるのが一般的ですが、規格上、移植性があるのは `EXIT_SUCCESS` と `EXIT_FAILURE` の 2 つだけです。

ビルド ツールが外部のコマンド（アセットの変換ツールなど）を呼ぶとき、終了コードが 0 以外だと、ビルドを失敗として止めます。自作のツールが失敗したことを知らせるために、確実に `EXIT_FAILURE` を返します。

## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  std::println("EXIT_FAILURE = {}", EXIT_FAILURE);
  return EXIT_SUCCESS;     // 実際の失敗は、この行を EXIT_FAILURE にする
}
```

```text title="実行結果"
EXIT_FAILURE = 1
```

## ゲームでの使いどころ

アセット変換ツールが入力に失敗したときに返します。

```cpp
if (!ConvertTexture(input, output)) {
  std::println(stderr, "変換に失敗しました");
  return EXIT_FAILURE;   // ビルドが失敗として止まる
}
```

## よくあるミス

??? failure "失敗しても 0 を返し、ビルドが止まらない"
    失敗したときは `EXIT_FAILURE` を返します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`EXIT_SUCCESS`](exit_success.md) | 正常終了の終了コード |
| [`exit`](exit.md) | プログラムを終了する |

## コンパイラ対応

C++98 から使えます（C 言語由来）。`<cstdlib>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `EXIT_FAILURE` は異常終了を表す終了コード
    - [x] 呼び出し側が失敗を検出できる
    - [x] 正常終了は `EXIT_SUCCESS`

## 関連ページ

- [cpprefjp: EXIT_FAILURE](https://cpprefjp.github.io/reference/cstdlib/EXIT_FAILURE.html)
- [cppreference: EXIT_FAILURE](https://en.cppreference.com/w/cpp/c/EXIT_FAILURE)
