---
title: std::bind_front
summary: "関数の先頭の引数をあらかじめ決めた、新しい関数を作る。"
order: 9
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::bind_front

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <functional>`
</div>

関数の最初の引数をあらかじめ決めておいて、残りの引数だけを受け取る関数オブジェクトを作りたい。たとえば、「ダメージ計算で、攻撃力だけ固定して、防御力を後から渡す」。`std::bind_front(f, 引数...)` は、<strong>先頭の引数を固定した関数オブジェクト</strong>を作ります。

!!! tip "ポイント"
    - `std::bind_front(f, a)` は、`f(a, 残り...)` を呼ぶ関数オブジェクトを返す
    - `std::bind` より読みやすく、速い
    - メンバー関数も、先頭にオブジェクトを渡せば使える
    - ラムダ式で書いても同じ（短い場合は `bind_front`）

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::bind_front {#bind_front}

<span class="ver ver-20">C++20</span>

```cpp
template <class F, class... Args>
constexpr /* 関数オブジェクト */ bind_front(F&& f, Args&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `f` | 呼び出し可能なもの | 関数、ラムダ、メンバー関数ポインターなど |
| `args...` | 値 | 先頭に固定する引数 |

返る関数オブジェクトを呼ぶと、固定した引数に続けて、渡した引数が `f` に転送されます。固定した引数はコピー（またはムーブ）されて、オブジェクトの中に保持されます。参照で持たせたいときは `std::ref` を使います。

`std::bind` と違い、プレースホルダー（`_1` など）がなく、引数の順序を入れ替えたりはできません。そのぶん単純で、コンパイル時間と実行時の効率が良いです。後ろの引数を固定したいときは、`std::bind_back`（C++23）を使います。

## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int Damage(int attack, int defense) { return attack - defense; }

int main() {
  auto sword = std::bind_front(Damage, 30);     // attack を 30 に固定
  std::println("防御 10 の敵: {}", sword(10));
  std::println("防御 25 の敵: {}", sword(25));
}
```

```text title="実行結果"
防御 10 の敵: 20
防御 25 の敵: 5
```

## ゲームでの使いどころ

コールバックに、メンバー関数とオブジェクトを結びつけて渡します。

```cpp
button.OnClick(std::bind_front(&Menu::Start, this));   // this を固定
```

## よくあるミス

??? failure "参照で渡したつもりが、コピーされる"
    `std::ref(x)` で包みます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`bind_back`](bind_back.md) | 後ろの引数を固定 |
| [`bind`](bind.md) | 古い汎用の束縛 |
| [`invoke`](invoke.md) | 呼び出し可能なものを呼ぶ |

## コンパイラ対応

C++20 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `bind_front(f, a)` は先頭の引数を固定した関数オブジェクト
    - [x] `std::bind` より単純で速い
    - [x] 参照で持たせるなら `std::ref`

## 関連ページ

- [cpprefjp: std::bind_front](https://cpprefjp.github.io/reference/functional/bind_front.html)
- [cppreference: std::bind_front](https://en.cppreference.com/w/cpp/utility/functional/bind_front)
