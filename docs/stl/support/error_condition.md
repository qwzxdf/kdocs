---
title: std::error_condition
summary: "環境に依存しない「エラーの種類」を表す。error_code と比べる相手。"
order: 31
group: エラーコード（<system_error>）
tags:
  - 型・言語サポート
---

# std::error_condition

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <system_error>`
</div>

`std::error_code` は、OS ごとの具体的なエラーです。同じ「ファイルがない」でも、Windows と Linux では番号が違います。`std::error_condition` は、<strong>環境によらない、エラーの種類</strong>を表します。`error_code` を `error_condition` と比べると、環境の違いを吸収できます。

!!! tip "ポイント"
    - `std::error_condition` はエラーの種類を表す（環境によらない）
    - `std::errc` の値から暗黙に作れる
    - `error_code == error_condition` で、種類が一致するか判定できる
    - 値はカテゴリーとセット

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::error_condition {#error_condition}

<span class="ver ver-11">C++11</span>

```cpp
class error_condition {
 public:
  int value() const noexcept;
  const std::error_category& category() const noexcept;
};
```

`error_code` は「何が起きたか（OS が報告した番号）」、`error_condition` は「それは移植性のある種類のどれにあたるか」を表します。

`ec == std::errc::no_such_file_or_directory` と書くと、`std::errc` から `error_condition` が作られ、`error_code` の持つカテゴリーが、その種類に一致するかを判定してくれます。環境ごとの違いは、カテゴリーが吸収します。

## 実際に動かしてみる

```cpp
#include <print>
#include <system_error>

int main() {
  const std::error_condition cond = std::errc::timed_out;
  const std::error_code ec = std::make_error_code(std::errc::timed_out);
  std::println("種類が一致: {}", ec == cond);
}
```

```text title="実行結果"
種類が一致: true
```

## ゲームでの使いどころ

環境によらず、エラーの種類で処理を分けます。

```cpp
if (ec == std::errc::permission_denied) { ShowMessage("権限がありません"); }
```

## よくあるミス

??? failure "`error_code` どうしを比べて、環境で結果が違う"
    種類で判断するなら `error_condition` と比べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`errc`](errc.md) | エラーの種類の列挙型 |
| [`error_code`](error_code.md) | 具体的なエラー |

## コンパイラ対応

C++11 から使えます。`<system_error>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `error_condition` は環境によらないエラーの種類
    - [x] `error_code` と `==` で比べる
    - [x] `errc` から作れる

## 関連ページ

- [cpprefjp: std::error_condition](https://cpprefjp.github.io/reference/system_error/error_condition.html)
- [cppreference: std::error_condition](https://en.cppreference.com/w/cpp/error/error_condition)
