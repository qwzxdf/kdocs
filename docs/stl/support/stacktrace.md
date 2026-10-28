---
title: std::stacktrace
summary: "呼び出し履歴（スタックトレース）を取得する。"
order: 2
tags:
  - 型・言語サポート
---

# std::stacktrace

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-23">C++23</span>
`#include <stacktrace>`
</div>

`std::stacktrace` は、**今の呼び出し履歴（どの関数がどの関数を呼んだか）を取得する**クラスです。クラッシュの調査や、想定外の状態に陥ったときのログに使います。`std::stacktrace::current()` で取得し、`std::to_string` や `println` で表示します。

!!! tip "ポイント"
    - 取得のコストは大きい（数十マイクロ秒〜）。毎フレーム取らない。
    - リンクに専用のライブラリが要ることがある（GCC は `-lstdc++exp` など）。
    - C++23 の機能。

!!! info "このページを読む前に"
    - [STL](../index.md)（STL 全体の地図（どこに何があるか））
    - [テンプレート](../../basics/template.md)（テンプレートの基礎）

## 関数の詳しい説明

### std::stacktrace::current {#stacktrace}

<span class="ver ver-23">C++23</span>

```cpp
static basic_stacktrace current(const allocator_type& alloc = allocator_type()) noexcept;
```

- 今までの関数の呼び出し履歴を取得します。`std::println("{}", std::stacktrace::current())` や `std::to_string(trace)` で表示できます
- GCC では `-lstdc++exp`（GCC 13 / 14）や `-lstdc++`（GCC 15 以降）のリンクが必要、MSVC は VS 2022 17.4 以降で使えます

```cpp
// 実行には環境ごとのリンク設定が必要なので、ここでは書き方だけ
#include <print>
#include <stacktrace>

void Crash() {
  std::println("呼び出し履歴:\n{}", std::stacktrace::current());
}
```

## 実際に動かしてみる

```cpp
#include <print>
#include <stacktrace>

int main() {
  std::println("{}", std::stacktrace::current().size() > 0);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 想定外のエラー時に呼び出し履歴をログに残す | `std::println("{}", std::stacktrace::current());` |

## よくあるミス

??? failure "毎フレーム取得して重くなる"
    エラー時だけにします。

??? failure "リリースビルドで関数名が出ない"
    シンボル情報（`/DEBUG` などの設定）が必要です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`source_location`](source_location.md) | 1 か所の位置 |

## コンパイラ対応

C++23 の機能です。GCC 12 / MSVC 19.34 以降で使えます（GCC は別途ライブラリのリンクが必要）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 呼び出し履歴を取得する
    - [x] エラー時だけ取る
    - [x] C++23

## 関連ページ

- [cpprefjp: std::stacktrace](https://cpprefjp.github.io/reference/source_location/stacktrace.html)
- [cppreference: std::stacktrace](https://en.cppreference.com/w/cpp/utility/stacktrace)
