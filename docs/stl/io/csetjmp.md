---
title: <csetjmp>（setjmp と longjmp）
summary: "離れた場所へ一気に戻る（C 由来・C++ では危険）。"
order: 100
tags:
  - 入出力・文字列
---

# &lt;csetjmp&gt;（setjmp と longjmp）

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <csetjmp>`
</div>

`setjmp` で「戻り先」を記録し、`longjmp` で一気にそこへ飛ぶ、C 由来の仕組みです。**C++ のデストラクターが呼ばれずに飛ぶ**ため、リソースがリークし、未定義動作になることがあります。C++ では、**例外**を使います。古い C のライブラリ（libpng、libjpeg のエラー処理）とやりとりするときに、出会うことがあります。

!!! tip "ポイント"
    - C++ のオブジェクトがある関数をまたいで `longjmp` しない。
    - 例外のほうが安全。
    - C のライブラリが `longjmp` でエラーを返す設計のとき、境界を越えないようにする。

## 関数の詳しい説明

### &lt;csetjmp&gt;（setjmp と longjmp） {#csetjmp}

```cpp
int setjmp(jmp_buf env);
[[noreturn]] void longjmp(jmp_buf env, int value);
```

- 戻り値: `setjmp` は 0（記録した時）か、`longjmp` の値（飛んできた時）
- 計算量: O(1)

```cpp
#include <csetjmp>
#include <print>

std::jmp_buf g_env;

int main() {
  if (setjmp(g_env) == 0) {
    longjmp(g_env, 1);    // setjmp の場所へ戻る
  } else {
    std::println("戻ってきた");
  }
}
```

```text title="実行結果"
戻ってきた
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| C のライブラリのエラー処理の理解 | `longjmp` が使われていたら、C++ の境界を越えない |

## よくあるミス

??? failure "デストラクターが呼ばれずにリークする"
    間にあるオブジェクトのデストラクターは呼ばれません。例外を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::exception`](../support/exceptions/exception.md) | 安全な代わり |

## コンパイラ対応

C 由来の機能です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 離れた場所へ飛ぶ（C 由来）
    - [x] デストラクターが呼ばれない
    - [x] C++ では例外

## 関連ページ

- [cpprefjp: setjmp / longjmp](https://cpprefjp.github.io/reference/csetjmp/longjmp.html)
- [cppreference: setjmp / longjmp](https://en.cppreference.com/w/cpp/utility/program/longjmp)
