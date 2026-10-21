---
title: assert
summary: "デバッグ中だけ「ここは必ず真」と確かめる。偽ならプログラムを止める。"
order: 96
tags:
  - 入出力・文字列
---

# assert

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++98〜</span>
`#include <cassert>`
</div>

`assert(条件)` は、**「ここでは条件が必ず真のはず」と確かめる**マクロです。偽だとメッセージ（ファイル名・行番号・式）を出して `abort` します。**リリースビルド（`NDEBUG` 定義時）では何も実行されません**。プログラマーのミス（前提条件の違反）の検出に使います。ユーザー入力のような、起こりうるエラーの処理には使いません。

!!! tip "ポイント"
    - リリースでは消える。**条件の中に副作用のある式を書かない**（`assert(Init())` はリリースで初期化が消える）。
    - `static_assert` はコンパイル時の確認。
    - ユーザー入力の検証は、`assert` ではなくエラー処理で。

## 関数の詳しい説明

### assert {#assert}

```cpp
#define assert(condition) /* 実装定義 */
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `condition` | 式 | 真であるはずの条件 |

- 戻り値: （なし）。偽なら異常終了
- 計算量: O(1)

```cpp
#include <cassert>
#include <print>

int main() {
  int hp = 10;
  assert(hp >= 0 && "HP は 0 以上のはず");   // 文字列を足すとメッセージになる
  std::println("OK");
}
```

```text title="実行結果"
OK
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 関数の前提条件の確認（nullptr でないか、範囲内か） | `assert(ptr != nullptr);` |

## よくあるミス

??? failure "assert の中に副作用を書く"
    `assert(Load())` は、リリースビルドで `Load()` ごと消えます。

## 類似

| 名前 | 違い |
| --- | --- |
| `static_assert` | コンパイル時の確認 |
| [`std::abort`](../numeric/cstdlib/abort.md) | 失敗時に呼ばれる |

## コンパイラ対応

C 由来の機能です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 前提条件の確認
    - [x] リリースでは消える
    - [x] 副作用を書かない

## 関連ページ

- [cpprefjp: assert](https://cpprefjp.github.io/reference/cassert/assert.html)
- [cppreference: assert](https://en.cppreference.com/w/cpp/error/assert)
