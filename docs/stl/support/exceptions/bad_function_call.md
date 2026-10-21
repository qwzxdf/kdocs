---
title: std::bad_function_call
summary: "空の std::function を呼んだときの例外。"
order: 12
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::bad_function_call

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++11</span>
`#include <functional>`
</div>

`std::bad_function_call` は、**何も入っていない（空の）`std::function` を呼び出した**ときに投げられる例外です。コールバックが未設定のときに起こります。呼ぶ前に `if (f)` で確認すれば避けられます。

!!! tip "ポイント"
    - `if (callback) callback();` で確認してから呼ぶ。
    - ゲームで例外を切っているなら、空の呼び出しは未定義動作になることがある。

!!! info "このページを読む前に"
    [標準の例外](../exceptions.md) の概要と合わせて読むと分かりやすいです。

## 関数の詳しい説明

### std::bad_function_call {#bad_function_call}

```cpp
class bad_function_call : public std::exception {
 public:
  const char* what() const noexcept override;
};
```

- 戻り値: （例外クラス）。`what()` でメッセージ
- 計算量: O(1)

```cpp
#include <functional>
#include <print>

int main() {
  std::function<void()> callback;  // 空
  try {
    callback();
  } catch (const std::bad_function_call&) {
    std::println("コールバックが未設定");
  }
}
```

```text title="実行結果"
コールバックが未設定
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 未登録のイベントコールバックを呼んでしまった | `if (on_click) on_click();` |

## よくあるミス

??? failure "確認せずに呼ぶ"
    呼ぶ前に必ず確認します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::function`](../../utilities/function.md) | 本体 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 空の function を呼ぶと投げる
    - [x] 呼ぶ前に `if (f)`
    - [x] 未設定のコールバックで起きる

## 関連ページ

- [cpprefjp: std::bad_function_call](https://cpprefjp.github.io/reference/functional/bad_function_call.html)
- [cppreference: std::bad_function_call](https://en.cppreference.com/w/cpp/utility/functional/bad_function_call)
