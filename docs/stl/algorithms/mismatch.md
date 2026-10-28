---
title: std::ranges::mismatch
summary: "2 つの範囲を先頭から比べて、最初に違うところを探す。"
order: 42
tags:
  - アルゴリズム
---

# std::ranges::mismatch

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

入力されたコマンドが正解の列のどこまで合っているか。`equal` は同じか違うかだけを答えるので、どこから違うのかは分かりません。`std::ranges::mismatch` は、2 つの範囲を先頭から比べて、最初に違う位置を返します。最後まで同じなら、短いほうの範囲の終わりが返ります。

!!! tip "ポイント"
    - 戻り値は**位置の組**（`.in1` と `.in2`）。どちらも同じ長さ進んだ位置になる。
    - 最後まで同じなら、短いほうの範囲の終わりが返る。
    - 「入力が正解のどこまで合っているか」を調べたいときに便利。

!!! info "このページを読む前に"
    [`equal`](equal.md) を先に読んでください。`mismatch` は、違う位置まで教えてくれる版です。

## 関数の詳しい説明

### std::ranges::mismatch {#mismatch}

```cpp
template <input_range R1, input_range R2, class Pred = ranges::equal_to,
          class Proj1 = identity, class Proj2 = identity>
constexpr mismatch_result<borrowed_iterator_t<R1>, borrowed_iterator_t<R2>>
mismatch(R1&& r1, R2&& r2, Pred pred = {}, Proj1 proj1 = {}, Proj2 proj2 = {});
```

- 戻り値: `.in1` と `.in2`（最初に違った位置。全部同じなら短いほうの終わり）

<div class="anim" data-label="std::ranges::mismatch(a, b)">
1 2 3 | 1 9 3 # a と b
*1 2 3 | *1 9 3 # 同じ
1 *2 3 | 1 *9 3 # 違う。最初に違う位置の組を返す
</div>

```cpp
#include <algorithm>
#include <print>
#include <string>

int main() {
  std::string answer = "dragon";
  std::string input = "drag0n";
  auto [a, b] = std::ranges::mismatch(answer, input);
  std::println("{} 文字目が違う（正解 {} / 入力 {}）", a - answer.begin() + 1, *a, *b);
}
```

```text title="実行結果"
5 文字目が違う（正解 o / 入力 0）
```


## フラグ・オプション

| 引数 | 重要度 | 渡すもの | 意味 |
| --- | --- | --- | --- |
| `pred` | <span class="rank rank-rare">知ってるだけ</span> | ラムダ式 | 「等しい」の判定を変える |
| `proj1` / `proj2` | <span class="rank rank-rare">知ってるだけ</span> | `&Type::member` | 比べる前にメンバを取り出す |

## ゲームでの使いどころ

入力の照合に使います。隠しコマンドの途中まで入力されているかを `mismatch` の位置から求めて、画面に進行度を出すことができます。

テストコードでは、期待した配列と実際の結果を比べて、最初に違った場所を報告する用途に向いています。

文字列の共通の先頭部分を求めるのにも使えます。2 つのパスを比べて、共通するフォルダの深さを求める、といった場面です。

## よくあるミス

??? failure "最後まで同じとき、位置を読んでしまう"
    全部同じなら、`.in1` は `r1` の終わり（`end()` 相当）です。`*a` のように読むと未定義動作なので、`a != answer.end()` を確かめてから使います。

??? failure "戻り値が 1 つのイテレーターだと思う"
    戻り値は、2 つの範囲それぞれの位置の組（`.in1` と `.in2`）です。構造化束縛で受けると読みやすくなります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::equal`](equal.md) | 同じか違うかだけを返す |
| [`std::ranges::find`](find.md) | 値や条件で 1 つの範囲を探す |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 最初に違う位置が欲しいなら `mismatch`
    - [x] 戻り値は `.in1` と `.in2` の組
    - [x] 全部同じなら、短いほうの終わり

## 関連ページ

- [cpprefjp: std::ranges::mismatch](https://cpprefjp.github.io/reference/algorithm/ranges_mismatch.html)
- [cppreference: std::ranges::mismatch](https://en.cppreference.com/w/cpp/algorithm/ranges/mismatch)
