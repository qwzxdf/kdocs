---
title: std::function_ref
summary: "呼び出せるものを借りて参照するだけの、軽い関数ラッパー。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::function_ref

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <functional>`
</div>

関数の引数にコールバックを受けたいとき、`std::function` だとコピーのコストやヒープ確保が気になります。呼び出しの間だけ使えれば十分なら、中身をコピーせず**借りるだけ**の `function_ref` が軽く済みます。

!!! tip "ポイント"
    - 持ち主にはならない。呼び出し中に元の関数オブジェクトが生きている必要がある。
    - 関数の引数として受け取る使い方が向く。メンバ変数に保存するのは危険。
    - ヒープ確保は起きない。

!!! info "このページを読む前に"
    [<functional>](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::function_ref {#function_ref}

```cpp
template <class... Sigs> class function_ref;  // Sigs の例: R(Args...) const noexcept
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `R(Args...)` | シグネチャ | 戻り値と引数 |

- 戻り値: 呼び出し演算子で呼ぶ
- 計算量: 間接呼び出し 1 回


## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

void Each(std::function_ref<void(int)> f) {
  for (int i = 0; i < 3; ++i) f(i);
}

int main() {
  int sum = 0;
  Each([&](int x) { sum += x; });
  std::println("{}", sum);
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| `for_each` 風の自作関数でコールバックを受ける | `void Each(std::function_ref<void(int)> f);` |

## よくあるミス

??? failure "ラムダの一時オブジェクトを保存する"
    `function_ref` は参照なので、元のラムダが消えたあとに呼ぶと未定義動作です。関数の引数としてだけ使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::function`](../../utilities/function.md) | 持ち主になる（コピーする） |
| [`move_only_function`](../../utilities/move_only_function.md) | ムーブ専用の持ち主 |

## コンパイラ対応

C++26 の機能です。対応は新しい標準ライブラリに限られます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 呼び出せるものを借りる関数ラッパー
    - [x] ヒープ確保なし
    - [x] 保存せずに引数として使う

## 関連ページ

- [cpprefjp: std::function_ref](https://cpprefjp.github.io/reference/functional/function_ref.html)
- [cppreference: std::function_ref](https://en.cppreference.com/w/cpp/utility/functional/function_ref)
