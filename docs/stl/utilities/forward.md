---
title: std::forward
summary: "テンプレートで受け取った引数を、左辺値・右辺値のまま次の関数へ渡す（完全転送）。"
order: 52
tags:
  - ユーティリティ
---

# std::forward

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++11</span>
`#include <utility>`
</div>

引数を受け取って、別の関数へそのまま渡すラッパー関数を書くとき、受け取った引数を渡すだけだと、右辺値で渡されたものも、左辺値として渡されてしまい、ムーブが働きません。`std::forward` は、テンプレートで受け取った引数を「受け取ったときの形のまま」次の関数へ渡すための関数です（完全転送）。左辺値で来たものは左辺値、右辺値で来たものは右辺値のまま転送します。

!!! tip "ポイント"
    - **転送参照（`T&&` のテンプレート引数）** とセットで使う。
    - 普段のコードでは使わない。自作の `Create(Args&&... args)` のようなラッパー関数を書くときだけ。
    - `std::move` との違い: `move` は常に右辺値にする。`forward` は渡された形のまま。

!!! info "このページを読む前に"
    [ムーブ](../../basics/move.md) の考え方を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::forward {#forward}

```cpp
template <class T>
constexpr T&& forward(std::remove_reference_t<T>& t) noexcept;
```

| テンプレート引数 | 意味 |
| --- | --- |
| `T` | 受け取ったときのテンプレート引数（`Args` など）をそのまま書く |

- 「左辺値で渡されたら左辺値のまま、右辺値で渡されたら右辺値のまま」次へ渡します（完全転送）
- `template <class... Args> void F(Args&&... args)` の中で使います

```cpp
#include <memory>
#include <print>
#include <string>
#include <utility>
#include <vector>

struct Enemy {
  Enemy(std::string n, int h) : name(std::move(n)), hp(h) {}
  std::string name;
  int hp;
};

class EnemyPool {
 public:
  // 引数をそのまま Enemy のコンストラクタへ転送する
  template <class... Args>
  Enemy& Spawn(Args&&... args) {
    return enemies_.emplace_back(std::forward<Args>(args)...);
  }

 private:
  std::vector<Enemy> enemies_;
};

int main() {
  EnemyPool pool;
  std::string name = "スライム";
  pool.Spawn(name, 10);          // name は左辺値 → コピーされる（name は残る）
  pool.Spawn(std::string("ゴブリン"), 30);  // 右辺値 → ムーブされる
  std::println("{}", name);
}
```

```text title="実行結果"
スライム
```

!!! note "実際は"
    自分でラッパー関数（`emplace` のようなもの）を作るとき以外は使いません。

## ゲームでの使いどころ

`emplace_back` や `make_unique` のように、引数をコンストラクターへそのまま渡すラッパーを自作するときに使います。

```cpp
template <class T, class... Args>
std::unique_ptr<T> Create(Args&&... args) {
  return std::unique_ptr<T>(new T(std::forward<Args>(args)...));
}
```

エンジンのイベント送信や、コンポーネントの生成関数で、引数をそのまま渡したいときに登場します。普段のコードでは使いません。自作のラッパー関数を書くときだけです。

## よくあるミス

??? failure "forward を二度使う"
    同じ引数に `std::forward` を 2 回書くと、右辺値が 2 回ムーブされて、2 回目は中身が空です。転送は 1 回だけにします。

??? failure "転送参照でない引数に使う"
    `void f(std::string&& s)` のような、具体的な型の右辺値参照には `std::move` を使います。`forward` は `T&&` のテンプレート引数のときだけです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::move`](move.md) | 常に右辺値にする |
| [`std::make_unique`](make_unique.md) | 内部で `forward` を使っている |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 引数を受け取った形のまま転送する
    - [x] テンプレートの `T&&` とセット
    - [x] 同じ引数に 2 回使わない

## 関連ページ

- [cpprefjp: std::forward](https://cpprefjp.github.io/reference/utility/forward.html)
- [cppreference: std::forward](https://en.cppreference.com/w/cpp/utility/forward)
