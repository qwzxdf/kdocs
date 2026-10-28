---
title: EXIT_SUCCESS
summary: "成功を表す終了コードのマクロ。"
order: 900
tags:
  - 数値
---

# EXIT_SUCCESS

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

プログラムの終了コードに 0 を直接書くと、「0 は成功」と知らない人には意味が通じません。`EXIT_SUCCESS` は、<strong>正常終了を表す終了コード</strong>を名前で表すマクロです。

!!! tip "ポイント"
    - `EXIT_SUCCESS` は正常終了を表す終了コード（普通は 0）
    - `std::exit(EXIT_SUCCESS)` や、`main` の戻り値に使う
    - 異常終了は `EXIT_FAILURE`
    - `main` は何も返さなくても、正常終了（0）になる

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### EXIT_SUCCESS {#exit_success}

```cpp
#define EXIT_SUCCESS /* 実装定義 */
```

`EXIT_SUCCESS` は、`std::exit` や `main` の戻り値に使える、正常終了を表す整数の定数です。多くの環境で 0 に展開されますが、規格上は実装定義です。

0 と書いても動きますが、`EXIT_SUCCESS` と書くと、終了コードであることがはっきりします。特に、`EXIT_FAILURE` と並べて書くと読みやすくなります。

終了コードは、プログラムを呼び出したシェルや、ビルドの仕組み、CI が成功か失敗かを判断するのに使います。

## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  std::println("EXIT_SUCCESS = {}", EXIT_SUCCESS);
  return EXIT_SUCCESS;
}
```

```text title="実行結果"
EXIT_SUCCESS = 0
```

## ゲームでの使いどころ

処理の結果に応じて、終了コードを返し分けます。

```cpp
int main() {
  if (!LoadConfig()) return EXIT_FAILURE;
  Run();
  return EXIT_SUCCESS;
}
```

## よくあるミス

??? failure "終了コードに任意の数を使い、環境で意味が変わる"
    成功と失敗は、この 2 つのマクロを使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`EXIT_FAILURE`](exit_failure.md) | 異常終了の終了コード |
| [`exit`](exit.md) | プログラムを終了する |

## コンパイラ対応

C++98 から使えます（C 言語由来）。`<cstdlib>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `EXIT_SUCCESS` は正常終了を表す終了コード
    - [x] `main` の戻り値と `exit` に使う
    - [x] 異常終了は `EXIT_FAILURE`

## 関連ページ

- [cpprefjp: EXIT_SUCCESS](https://cpprefjp.github.io/reference/cstdlib/EXIT_SUCCESS.html)
- [cppreference: EXIT_SUCCESS](https://en.cppreference.com/w/cpp/c/EXIT_SUCCESS)
