---
title: std::exchange
summary: "新しい値を入れて、古い値を返す。"
order: 53
tags:
  - ユーティリティ
---

# std::exchange

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-14">C++14</span>
`#include <utility>`
</div>

ムーブコンストラクターを書くとき、元のオブジェクトのポインターを自分に移して、元は `nullptr` にしたい。「古い値を取り出して、新しい値を入れる」処理は、一時変数を使って 3 行になります。`std::exchange` は、変数に新しい値を入れて、元の値を返す関数です。この 3 行が 1 行になります。

!!! tip "ポイント"
    - `old = std::exchange(x, new_value);` は「`old = x; x = new_value;`」と同じ。
    - ムーブコンストラクタで、`ptr_(std::exchange(other.ptr_, nullptr))` のように使うと短い。
    - ゲームの「保留中のダメージを取り出して 0 に戻す」のような処理にも。

!!! info "このページを読む前に"
    [ムーブ](../../basics/move.md) の考え方を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::exchange <span class="ver ver-14">C++14</span> {#exchange data-toc-label="std::exchange"}

```cpp
template <class T, class U = T>
constexpr T exchange(T& obj, U&& new_value);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `obj` | `T&` | 書き換える変数 |
| `new_value` | 値 | 新しく入れる値 |

- 戻り値: `obj` の**古い値**

<div class="anim" data-label="std::exchange(a, 9)">
5 # a = 5
*5 # 古い値（5）を返す
+9 # a に新しい値 9 を入れる
</div>

```cpp
#include <print>
#include <utility>

int main() {
  int pending_damage = 25;
  int applied = std::exchange(pending_damage, 0);  // 取り出して 0 にリセット
  std::println("{} {}", applied, pending_damage);
}
```

```text title="実行結果"
25 0
```

!!! note "実際は"
    「溜まっていたものを取り出してリセット」「前の状態を覚えつつ新しい状態にする」を 1 行で書けます。ムーブコンストラクタの実装でもよく使います。

## ゲームでの使いどころ

自作のリソースクラスのムーブコンストラクターで使います。`Texture(Texture&& other) : handle_(std::exchange(other.handle_, nullptr)) {}` と書けば、ハンドルを移して、元を空にします。元のデストラクターが二重に解放しません。

「保留中の値を取り出して、0 に戻す」処理にも向いています。保留中のダメージを `int dmg = std::exchange(pending_damage_, 0);` と書けば、取り出しと初期化が一度に済みます。

フラグを立てて、前の値を調べる用途もあります。`bool was_dirty = std::exchange(dirty_, false);` です。

## よくあるミス

??? failure "戻り値を捨てる"
    戻り値（古い値）を使わないなら、ただの代入で足ります。

??? failure "古い値と新しい値の順序を取り違える"
    `std::exchange(x, new)` は、新しい値を入れて、古い値を返します。引数の順が逆だと、意図しない値が入ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::swap`](swap.md) | 2 つの値を入れ替える |
| [`std::move`](move.md) | ムーブ可能にする |

## コンパイラ対応

C++14 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 新しい値を入れて、古い値を返す
    - [x] ムーブコンストラクタで便利
    - [x] C++14

## 関連ページ

- [cpprefjp: std::exchange](https://cpprefjp.github.io/reference/utility/exchange.html)
- [cppreference: std::exchange](https://en.cppreference.com/w/cpp/utility/exchange)
