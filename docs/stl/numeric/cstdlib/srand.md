---
title: std::srand
summary: "rand() の乱数の並びを、シードで初期化する。"
order: 900
tags:
  - 数値
---

# std::srand

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

乱数は、起動のたびに違う並びにしたいこともあれば、デバッグのために毎回同じ並びにしたいこともあります。`std::srand` は、`std::rand` の乱数の並びの出発点（種）を決めます。

!!! tip "ポイント"
    - `std::srand(seed)` で `rand` の種を決める
    - 同じ種からは、同じ並びが出る（再現性がある）
    - 毎回違う並びにするには時刻などを渡す
    - 新しいコードでは `<random>` を使う

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::srand {#srand}

```cpp
void srand(unsigned int seed);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `seed` | `unsigned int` | 乱数の種 |

`std::rand` が返す疑似乱数の列を、`seed` から始まる決まった列に切り替えます。同じ `seed` を与えれば、そのあとの `rand` の戻り値は毎回同じ列になります。種を一度も設定しなかった場合は、`srand(1)` と同じ扱いです。

毎回違う並びにしたいときは、現在時刻などを種にします。`srand(time(nullptr))` が古典的な書き方ですが、1 秒に 2 回起動すると同じ種になる弱点があります。

`rand` / `srand` は、品質が低く（下位のビットに偏りがある環境がある）、スレッドセーフでもなく、範囲を変えるときに偏りを生みやすい、という問題があります。新しいコードでは `<random>` の `std::mt19937` と分布クラスを使います。

## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  std::srand(42);
  const int first = std::rand();

  std::srand(42);                      // 同じ種に戻す
  const int second = std::rand();
  std::println("同じ種なら同じ値: {}", first == second);
}
```

```text title="実行結果"
同じ種なら同じ値: true
```

## ゲームでの使いどころ

テストやリプレイで、同じ乱数列を再現したいときに種を固定します。ただし、`rand` は環境によって列が違うので、環境をまたいで再現するには、`<random>` の `std::mt19937` を使います。

```cpp
std::mt19937 rng(42);                       // 種を固定した乱数エンジン
std::uniform_int_distribution<int> dice(1, 6);
const int roll = dice(rng);
```

## よくあるミス

??? failure "毎フレーム `srand(time(nullptr))` を呼び、同じ値が続く"
    `srand` は起動時に 1 回だけ呼びます。

??? failure "`rand() % n` で偏った乱数を得る"
    `<random>` の分布クラスを使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`rand`](rand.md) | 乱数を 1 つ返す |
| [`mt19937`](../../utilities/random/mt19937.md) | 品質の高い乱数エンジン |

## コンパイラ対応

C++98 から使えます（C 言語由来）。`<cstdlib>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `srand(seed)` は `rand` の種を決める
    - [x] 同じ種なら同じ列。起動時に 1 回だけ呼ぶ
    - [x] 新しいコードでは `<random>`

## 関連ページ

- [cpprefjp: std::srand](https://cpprefjp.github.io/reference/cstdlib/srand.html)
- [cppreference: std::srand](https://en.cppreference.com/w/cpp/c/srand)
