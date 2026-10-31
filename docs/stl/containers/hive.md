---
title: std::hive
summary: "要素を挿入・削除しても、他の要素の位置が変わらない順序なしコンテナ。"
order: 900
tags:
  - コンテナ
---

# std::hive

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <hive>`
</div>

`std::vector` は、途中の要素を消すと、後ろの要素が詰まり、要素の位置が変わります。ゲームで、敵や弾のように、頻繁に増減し、他から参照されるオブジェクトを持つとき、これは不便です。`std::hive` は、要素の追加と削除を速く行い、要素のアドレスを変えない（イテレーターを無効にしない）コンテナです。

!!! tip "ポイント"
    - 削除しても、他の要素のアドレスとイテレーターが無効にならない
    - 要素の順序は規定されない（挿入順とは限らない）
    - 内部は、複数のブロックと、削除された場所の再利用リスト
    - C++26

!!! info "このページを読む前に"
    [`std::vector`](vector.md) を先に読んでください。

## 関数の詳しい説明

### std::hive {#hive}

<span class="ver ver-26">C++26</span>

```cpp
template <class T, class Allocator = std::allocator<T>>
class hive;
```

主な操作は `insert` / `emplace`（追加）、`erase`（削除）、イテレーターによる走査です。`operator[]` はありません。位置による添字アクセスがないのは、順序が不定だからです。

`erase` は、要素のあった場所を空きとして記録し、次の `insert` が再利用します。そのため、追加と削除が繰り返されても、メモリが増え続けません。

走査は、空きをスキップしながら進みます。`vector` ほど速くはありませんが、連続した領域のブロックを単位にするので、`list` よりずっと速くなります。

この種類のコンテナは、ゲーム業界で「プール」や「スロット マップ」と呼ばれて、長く使われてきたものを、標準にしたものです。

## 使い方の形

手元の MSVC では使えないので、動かさずに、形だけを示します。

```cpp
std::hive<Enemy> enemies;

auto it = enemies.insert(Enemy{100});          // 追加。イテレーターが返る
Enemy* p = &*it;                               // アドレスは、削除されるまで変わらない

enemies.erase(it);                             // 削除。他の要素のアドレスは変わらない
for (Enemy& e : enemies) e.Update();           // 走査（順序は不定）
```

## ゲームでの使いどころ

敵や弾のように、頻繁に増減し、ポインターで参照され続けるオブジェクトを管理します。

## よくあるミス

??? failure "順序に依存する"
    挿入順とは限りません。順序が要るなら `vector` です。

??? failure "添字でアクセスしようとする"
    `operator[]` はありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`vector`](vector.md) | 連続した領域。削除でずれる |
| [`list`](list.md) | 個別のノード。走査が遅い |
| `std::flat_map` | 並びを保つ連想配列 |

## コンパイラ対応

C++26 の機能です。手元の MSVC（Visual Studio 2026）では未対応のため、サンプルは動かしていません。

## 関連ページ

- [cpprefjp: std::hive](https://cpprefjp.github.io/reference/hive/hive.html)
- [cppreference: std::hive](https://en.cppreference.com/w/cpp/container/hive)
