---
title: std::ranges::generate
summary: "範囲の各要素を、関数を呼んだ結果で埋める。"
order: 47
tags:
  - アルゴリズム
---

# std::ranges::generate

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

配列をランダムな値で埋めたい、連続する ID を振りたい。毎回違う値で配列を埋めるには、`for` の中で関数を呼んで代入することになります。`std::ranges::generate` は、範囲の各要素を関数を呼んだ結果で埋めるアルゴリズムです。先頭から n 個だけ埋める `generate_n` もあります。

!!! tip "ポイント"
    - 関数は**要素ごとに 1 回ずつ**呼ばれる（引数なし、戻り値が要素の値）。
    - 乱数で埋めるなら、乱数エンジンを**参照でキャプチャ**するか、`std::ref` で渡す（コピーされると毎回同じ値になる）。
    - 同じ値で埋めるなら [`fill`](fill.md)、連番なら [`iota`](iota.md)。

!!! info "このページを読む前に"
    [ラムダ式](../../basics/lambda.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::generate {#generate}

```cpp
template <class R, copy_constructible F>
constexpr borrowed_iterator_t<R> generate(R&& r, F gen);
```

- 各要素に `gen()` の戻り値を入れます。呼ぶたびに違う値を返す関数（乱数など）と組み合わせます

<div class="anim" data-label="std::generate(v.begin(), v.end(), next)">
_ _ _ _ # v
+3 _ _ _ # 関数を呼んで入れる
+3 +6 _ _ # 次の呼び出し
+3 +6 +9 +12 # 全部入る
</div>

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  int n = 1;
  std::vector<int> powers(5);
  std::ranges::generate(powers, [&n] {
    int current = n;
    n *= 2;
    return current;
  });
  std::println("{}", powers);
}
```

```text title="実行結果"
[1, 2, 4, 8, 16]
```


### generate_n の使い方

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> v(5, 0);
  int next = 10;

  // 先頭から 3 個だけ、10, 20, 30 で埋める
  std::ranges::generate_n(v.begin(), 3, [&next] {
    int value = next;
    next += 10;
    return value;
  });
  std::println("{}", v);
}
```

```text title="実行結果"
[10, 20, 30, 0, 0]
```

## フラグ・オプション

| 関数 | 重要度 | 意味 |
| --- | --- | --- |
| `generate` | <span class="rank rank-sometimes">たまに</span> | 全要素を埋める |
| `generate_n` | <span class="rank rank-rare">知ってるだけ</span> | 先頭から n 個だけ埋める |

## ゲームでの使いどころ

テスト用のデータや、ステージの初期配置をランダムに作るときに使います。`std::ranges::generate(v, [&] { return dist(rng); })` で、乱数エンジンの結果を並べられます。

乱数エンジンは、参照でキャプチャします。値でキャプチャ（コピー）すると、毎回同じ状態から始まり、全要素が同じ値になります。

連番を作るなら、`std::iota` のほうが簡単です。`generate` は、要素ごとに違う処理が必要なときに使います。

## よくあるミス

??? failure "乱数エンジンがコピーされて、毎回同じ値になる"
    `std::ranges::generate(v, [rng] { return rng(); })` のように値でキャプチャすると、ラムダの中の `rng` がコピーで、毎回同じ並びになります。`[&rng]` と参照でキャプチャします。

??? failure "乱数エンジンがコピーされて、全要素が同じ値になる"
    ラムダが乱数エンジンを値でキャプチャすると、呼ぶたびに同じコピーから始まります。`[&rng, &dist]` と参照でキャプチャします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::fill`](fill.md) | 同じ値で埋める |
| [`std::ranges::iota`](iota.md) | 連番で埋める |
| [`std::ranges::transform`](transform.md) | 既存の要素を変換して書き出す |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 関数を呼んだ結果で埋める
    - [x] 乱数エンジンは参照でキャプチャ
    - [x] 個数指定は `generate_n`

## 関連ページ

- [cpprefjp: std::ranges::generate](https://cpprefjp.github.io/reference/algorithm/ranges_generate.html)
- [cppreference: std::ranges::generate](https://en.cppreference.com/w/cpp/algorithm/ranges/generate)
