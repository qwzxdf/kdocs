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

`std::bind_front(f, a)` は、**関数 `f` の最初の引数を `a` に決めた、新しい呼び出し可能オブジェクト**を作ります。コールバックにオブジェクトを結び付ける（`this` を渡す）ときなどに使います。`std::bind` より単純で、読みやすいです。

!!! tip "ポイント"
    - `std::bind_front(&Player::OnHit, this)` で、メンバ関数をコールバックにできる。
    - `std::bind` の `_1` のような特別な記号が要らない。
    - ラムダ式でも同じことができる。

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。[ラムダ式](../../../basics/lambda.md) も関係します。

## 関数の詳しい説明

### std::bind_front {#bind_front}

<span class="ver ver-20">C++20</span>

```cpp
template <class F, class... Args>
constexpr auto bind_front(F&& f, Args&&... args);
```

- `f` の前のほうの引数を固定した、新しい関数を作ります。メンバ関数とオブジェクトを組にして、コールバックに渡すのに便利です

```cpp
#include <functional>
#include <print>

class Score {
 public:
  void Add(int points) { total_ += points; }
  int total() const { return total_; }

 private:
  int total_ = 0;
};

int main() {
  Score score;
  std::function<void(int)> on_kill = std::bind_front(&Score::Add, &score);  // score.Add(...)
  on_kill(100);
  on_kill(50);
  std::println("{}", score.total());
}
```

```text title="実行結果"
150
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| イベントのコールバックにメンバ関数を渡す | `events.Subscribe(std::bind_front(&Player::OnHit, this))` |

## よくあるミス

??? failure "this を渡し忘れる"
    メンバ関数ポインターの最初の引数はオブジェクトです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`bind_back`](bind_back.md) | 後ろの引数を決める |
| [`bind`](bind.md) | 古い、一般的な版 |
| [ラムダ式](../../../basics/lambda.md) | 同じことが書ける |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 先頭の引数を決めた関数を作る
    - [x] this の結び付けに
    - [x] bind より単純

## 関連ページ

- [cpprefjp: std::bind_front](https://cpprefjp.github.io/reference/functional/bind_front.html)
- [cppreference: std::bind_front](https://en.cppreference.com/w/cpp/utility/functional/bind_front)
