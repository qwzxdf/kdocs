---
title: std::getenv
summary: "環境変数の値を取得する。"
order: 7
group: <cstdlib> の関数
tags:
  - 数値
---

# std::getenv

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cstdlib>`
</div>

環境変数は、プログラムの外から設定を渡す手段です。ゲームでは、デバッグ用のフラグ、データの置き場所の指定、CI での動作の切り替えに使います。`std::getenv` は、環境変数の値を取り出します。

!!! tip "ポイント"
    - `std::getenv("PATH")` で `PATH` の値を取る
    - 設定されていなければ `nullptr`
    - 返された文字列は書き換えない。次の呼び出しで無効になりうる
    - MSVC は安全版の `getenv_s` を勧めている（警告 C4996）

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::getenv {#getenv}

```cpp
char* getenv(const char* name);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `name` | `const char*` | 環境変数の名前 |

戻り値は、環境変数 `name` の値を指す文字列です。設定されていなければ `nullptr` を返します。`nullptr` のまま文字列として使うと落ちるので、必ず検査します。

返された文字列は、処理系が管理しているものです。書き換えてはいけません。`setenv` などで環境が変わったり、`getenv` を再度呼んだりすると、前の戻り値が無効になることがあるため、使う前に `std::string` へコピーしておくのが安全です。

Windows の MSVC では、`getenv` が非推奨扱い（C4996）の警告になります。警告を避けるには `getenv_s`、または `_dupenv_s` を使います。マルチスレッドで環境を書き換える場合の安全性が理由です。

名前の大文字・小文字は、Windows では区別されません。Linux では区別されます。

## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>
#include <string>

int main() {
  const char* value = std::getenv("NO_SUCH_VARIABLE_XYZ");
  if (value == nullptr) {
    std::println("設定されていない");
  } else {
    std::println("値 = {}", std::string(value));   // コピーして使う
  }
}
```

```text title="実行結果"
設定されていない
```

## ゲームでの使いどころ

デバッグ用の機能を、環境変数で切り替えるときに使います。

```cpp
// 環境変数 GAME_DEBUG が設定されていればデバッグ表示を有効にする
const bool debug = std::getenv("GAME_DEBUG") != nullptr;
```

## よくあるミス

??? failure "`nullptr` を検査せずに使い、落ちる"
    設定されていない場合を必ず扱います。

??? failure "戻り値を保持して、あとで壊れた値を読む"
    `std::string` にコピーします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`system`](system.md) | コマンドを実行する |

## コンパイラ対応

C++98 から使えます（C 言語由来）。`<cstdlib>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `getenv(name)` は環境変数の値を返す
    - [x] 未設定なら `nullptr`
    - [x] 戻り値は書き換えず、コピーして使う

## 関連ページ

- [cpprefjp: std::getenv](https://cpprefjp.github.io/reference/cstdlib/getenv.html)
- [cppreference: std::getenv](https://en.cppreference.com/w/cpp/utility/program/getenv)
