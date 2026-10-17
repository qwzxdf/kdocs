---
title: イテレータ
tags:
  - 基礎
---

# イテレータ

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-11">C++98〜</span>
</div>

**イテレータ**は、**コンテナの中の「今どこを見ているか」を表すもの**です。ポインタのように、`*it` で今の要素を読み、`++it` で次の要素へ進みます。vector でも map でも list でも、同じ書き方で要素をたどれるようにするための共通の仕組みで、範囲 for や `std::ranges::sort` などのアルゴリズムも、中ではイテレータを使って動いています。

!!! tip "ポイント"
    - `begin()` は先頭、`end()` は**最後の次**（要素は無い）を指す。
    - `*it` で中身、`it->member` でメンバ、`++it` で次へ。
    - 「見つからなかった」は `end()` で表される。**`end()` を読むと未定義動作**。
    - **コンテナに追加・削除すると、イテレータが壊れる（無効化される）ことがある**。
    - 今は範囲 for と ranges のおかげで、イテレータを自分で書く場面は減っている。

## 基本

```cpp
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {10, 20, 30};

  for (auto it = v.begin(); it != v.end(); ++it) {
    std::print("{} ", *it);
  }
  std::println("");

  auto second = v.begin() + 1;  // 先頭から 1 つ進んだ位置
  *second = 99;
  std::println("{}", v);
}
```

```text title="実行結果"
10 20 30 
[10, 99, 30]
```

<div class="mem">
<div class="mem-step"><span class="mem-label">v</span><span class="mem-cells"><span class="move">10</span><span>20</span><span>30</span><span class="gone">　</span></span></div>
<div class="mem-step"><span class="mem-label"></span><span class="mem-note">↑ begin()　　　　　　↑ end()（最後の次。中身は無い）</span></div>
</div>

## 詳しく

### イテレータでできること

| 書き方 | 意味 | 使えるコンテナ |
| --- | --- | --- |
| `*it` | 指している要素 | 全部 |
| `it->m` | 要素のメンバ | 全部 |
| `++it` | 次へ | 全部 |
| `--it` | 前へ | vector、deque、list、map、set など（forward_list と unordered 系以外） |
| `it + n` / `it - n` | n 個先・前へ | vector、deque、array、string（ランダムアクセス） |
| `it2 - it1` | 何個離れているか | 同上 |
| `it1 < it2` | どちらが前か | 同上 |
| `std::next(it, n)` / `std::prev(it, n)` | n 個先・前（どのコンテナでも） | 全部（遅いものもある） |
| `std::distance(it1, it2)` | 何個離れているか | 全部（遅いものもある） |

### イテレータの種類

コンテナによって、できる操作が違います。

| 種類 | できること | 代表例 |
| --- | --- | --- |
| ランダムアクセス（連続） | 何でもできる。`+ n` で一気に飛べる | vector、array、string、span |
| ランダムアクセス | `+ n` で飛べる | deque |
| 双方向 | `++` と `--` | list、map、set |
| 前方向 | `++` だけ | forward_list、unordered_map、unordered_set |

`std::ranges::sort` はランダムアクセスが必要なので、list には使えません。

### 「見つからない」は end()

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {3, 5, 7};
  auto it = std::ranges::find(v, 5);
  if (it != v.end()) {
    std::println("{} 番目にあった", it - v.begin());
  }
}
```

```text title="実行結果"
1 番目にあった
```

### const_iterator

`const` なコンテナ、または `cbegin()` / `cend()` から得られるイテレータは `const_iterator` で、指している要素を書き換えられません。

### イテレータの無効化 {#invalidation}

コンテナの中身が動くと、それを指していたイテレータ（と参照・ポインタ）が**壊れたものを指す**ようになります。壊れたイテレータを使うと未定義動作です。

<div class="mem">
<div class="mem-step"><span class="mem-label">push_back 前</span><span class="mem-cells"><span class="move">10</span><span>20</span><span>30</span></span><span class="mem-note">it は 10 を指している</span></div>
<div class="mem-step"><span class="mem-label">再確保の後</span><span class="mem-cells"><span class="gone">10</span><span class="gone">20</span><span class="gone">30</span></span><span class="mem-note">中身は別の場所に引っ越した。it は解放された古い場所を指したまま</span></div>
</div>

| コンテナ | 追加すると | 削除すると |
| --- | --- | --- |
| vector / string | 再確保が起きれば**全部**、起きなくても追加位置より後ろ | 削除位置より後ろ |
| deque | 両端ならイテレータは全部（参照は無事）、途中なら全部 | 両端なら消した要素だけ、途中なら全部 |
| list / forward_list | 壊れない | 消した要素だけ |
| map / set | 壊れない | 消した要素だけ |
| unordered_map / set | 再ハッシュが起きればイテレータは全部（参照は無事） | 消した要素だけ |

詳しくは各コンテナのページ（[vector](../stl/containers/vector.md#イテレータ参照が壊れる条件) など）を見てください。

### erase の戻り値を使う

ループしながら消すなら、`erase` が返す「次の要素」のイテレータを使います（ただし今は `std::erase_if` で済むことがほとんどです）。

```cpp
#include <map>
#include <print>

int main() {
  std::map<int, int> hp = {{1, 30}, {2, 0}, {3, 50}};
  for (auto it = hp.begin(); it != hp.end();) {
    if (it->second <= 0) {
      it = hp.erase(it);  // 消した次の要素が返る
    } else {
      ++it;
    }
  }
  std::println("{}", hp);
}
```

```text title="実行結果"
{1: 30, 3: 50}
```

### 自作クラスを範囲 for で回せるようにする

`begin()` と `end()` を用意するだけで、範囲 for やアルゴリズムで使えます。

```cpp
#include <print>
#include <vector>

class Inventory {
 public:
  void Add(int id) { items_.push_back(id); }
  auto begin() const { return items_.begin(); }
  auto end() const { return items_.end(); }

 private:
  std::vector<int> items_;
};

int main() {
  Inventory inv;
  inv.Add(3);
  inv.Add(7);
  for (int id : inv) {
    std::print("{} ", id);
  }
  std::println("");
}
```

```text title="実行結果"
3 7 
```

## ゲームでの例

| 場面 | 例 |
| --- | --- |
| 検索結果 | `auto it = map.find(id); if (it != map.end())` |
| 位置の指定 | `v.insert(v.begin() + i, x)`、`v.erase(v.begin() + i)` |
| 自作コンテナ | インベントリ、シーン内のオブジェクト一覧を範囲 for で回せるようにする |

## よくあるミス

??? failure "end() を読む"
    ```cpp
    auto it = std::ranges::find(v, 99);
    std::println("{}", *it);  // 見つからなければ end() を読んで未定義動作
    ```

??? failure "ループ中に erase して ++ する"
    ```cpp
    for (auto it = v.begin(); it != v.end(); ++it) {
      if (*it == 0) {
        v.erase(it);  // it は壊れている。次の ++it で未定義動作
      }
    }
    ```

??? failure "別のコンテナのイテレータと比べる"
    `a.begin() != b.end()` のように、違うコンテナのイテレータ同士を比べるのは未定義動作です。

## 理解度チェック

!!! question "Q1. `std::vector<int> v = {1, 2, 3};` で `*(v.end() - 1)` は？"
    <div class="spoiler" markdown>

    **答え:** `3`。end() は最後の次なので、1 つ戻ると最後の要素です（`v.back()` と同じ）。

    </div>

## これだけ覚える

!!! abstract "まとめ"
    - [x] `begin()` は先頭、`end()` は最後の次
    - [x] 見つからないは `end()`。読まない
    - [x] 追加・削除でイテレータが壊れることがある

## 関連ページ

- [範囲 for](range-for.md)
- [ranges とビュー](ranges.md)
- [cppreference: Iterator library](https://en.cppreference.com/w/cpp/iterator)
