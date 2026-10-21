---
title: std::launder
summary: "オブジェクトの置き換えを、コンパイラに知らせてポインターを取り直す。"
order: 10
group: new / delete まわり
tags:
  - メモリ
---

# std::launder

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <new>`
</div>

`std::launder` は、**同じ場所に別のオブジェクトを作り直したあと、元のポインターを「新しいオブジェクトを指すポインター」として取り直す**ための関数です。コンパイラの最適化に誤解させないために必要になる、ごく限られた場面（配置 new で const メンバを持つ型を作り直す、など）で使います。

!!! tip "ポイント"
    - 普通のコードでは使わない。
    - const メンバや参照メンバを持つ型を、同じ場所に作り直したときに必要。
    - `construct_at` の戻り値を使えば、不要なことが多い。

!!! info "このページを読む前に"
    [ポインタ](../../../basics/pointer.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::launder <span class="ver ver-17">C++17</span> {#launder data-toc-label="std::launder"}

```cpp
template <class T>
[[nodiscard]] constexpr T* launder(T* p) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `T*` | 同じ場所に新しく作ったオブジェクトを指すポインタ |

- 戻り値: その場所にある**新しいオブジェクト**を正しく指すポインタ
- `const` メンバや参照メンバを持つクラスを、同じ場所で作り直したとき、古いポインタをそのまま使うと未定義動作になることがあります。そのときのための関数で、普通のコードでは使いません

## 実際に動かしてみる

```cpp
#include <new>
#include <print>

struct S {
  const int x;
};

int main() {
  alignas(S) unsigned char buffer[sizeof(S)];
  S* first = new (buffer) S{1};
  new (buffer) S{2};  // 同じ場所に作り直す（const メンバがあるので launder が必要）
  std::println("{}", std::launder(first)->x);
}
```

```text title="実行結果"
2
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ほぼ出番なし（低レベルのコンテナ実装など） | 知識として名前だけ |

## よくあるミス

??? failure "使いどころを誤る"
    普通のポインターには不要です。必要な場面を理解してから使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`placement_new`](placement_new.md) | 作り直しの手段 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 作り直したオブジェクトのポインターを取り直す
    - [x] ほぼ使わない
    - [x] 低レベルの実装向け

## 関連ページ

- [cpprefjp: std::launder](https://cpprefjp.github.io/reference/new/launder.html)
- [cppreference: std::launder](https://en.cppreference.com/w/cpp/memory/new/launder)
