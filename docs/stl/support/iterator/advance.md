---
title: std::advance
summary: "イテレータそのものを n 個進める（戻り値なし）。"
order: 3
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::advance

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iterator>`
</div>

`std::advance(it, n)` は、**イテレータ `it` 自身を n 個進める**関数です。`std::next` と違い、`it` が書き換わります。ランダムアクセスできない範囲では、n 回ぶんたどるので O(n) です。

!!! tip "ポイント"
    - 新しい位置が欲しいなら `next`。
    - n が負なら戻る（双方向イテレータ）。

!!! info "このページを読む前に"
    [`<iterator>`](../iterator.md) の概要を先に読むと分かりやすいです。[イテレータ](../../../basics/iterator.md) の基本が前提です。

## 関数の詳しい説明

### std::advance {#advance}

```cpp
template <class InputIt, class Distance>
void advance(InputIt& it, Distance n);
```

- `it` **そのもの**を n 個進めます（戻り値なし）。新しいイテレータが欲しいなら `std::next`

<div class="anim" data-label="std::advance(it, 2)">
*a b c d # it は a を指す
a b *c d # 2 つ進む（it が書き換わる）
</div>

```cpp
#include <algorithm>
#include <iterator>
#include <map>
#include <print>

int main() {
  std::map<int, char> m = {{10, 'a'}, {20, 'b'}, {30, 'c'}};
  auto it = m.begin();
  std::advance(it, 2);  // it 自体が動く
  std::println("{} / 距離 {}", it->first, std::distance(m.begin(), it));
}
```

```text title="実行結果"
30 / 距離 2
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ループ内で位置を飛ばす | `std::advance(it, 2);` |

## よくあるミス

??? failure "戻り値があると思う"
    `void` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`next`](next.md) | 新しい位置を返す |
| [`distance`](distance.md) | 距離を測る |

## コンパイラ対応

C++11 から使えます。`ssize` は C++20 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] イテレータを進める
    - [x] `it` が書き換わる
    - [x] list は O(n)

## 関連ページ

- [cpprefjp: std::advance](https://cpprefjp.github.io/reference/iterator/advance.html)
- [cppreference: std::advance](https://en.cppreference.com/w/cpp/iterator/advance)
