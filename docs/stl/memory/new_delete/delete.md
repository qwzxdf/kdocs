---
title: delete 式
summary: "new で作ったオブジェクトを壊して、メモリを解放する式。"
order: 2
group: new / delete まわり
tags:
  - メモリ
---

# delete 式

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-11">C++98〜</span>
`#include <new>`
</div>

`delete` は、**`new` で作ったオブジェクトのデストラクターを呼んで、メモリを解放する**式です。`nullptr` に対しては何もしません。解放後のポインターは使えません。

!!! tip "ポイント"
    - `new` には `delete`、`new[]` には `delete[]`。
    - 二重に `delete` しない。
    - `unique_ptr` に任せれば、書かなくてよい。

!!! info "このページを読む前に"
    [ポインタ](../../../basics/pointer.md) が分かると読みやすいです。

## 関数の詳しい説明

### delete 式 {#delete data-toc-label="delete 式"}

```cpp
delete p;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `T*` | `new` で得たポインタ。`nullptr` なら何もしない |

- 戻り値: なし
- デストラクタを呼んでから、メモリを返します
- **同じポインタを 2 回 `delete` する<strong>（二重解放）、</strong>`new[]` で作ったものを `delete` する<strong>、</strong>`malloc` したものを `delete` する**のは、どれも未定義動作です
- `delete` したあとのポインタは使えません（ダングリング）。`p = nullptr;` としておくと、うっかり使ったときに気づけます（unique_ptr ならこの心配自体がありません）
- 基底クラスのポインタで `delete` するなら、基底クラスのデストラクタは **`virtual`** にします（[継承と仮想関数](../../../basics/virtual.md)）

## 実際に動かしてみる

```cpp
#include <print>

int main() {
  int* p = new int(1);
  delete p;
  p = nullptr;  // 解放後は nullptr にしておく
  std::println("{}", p == nullptr);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 古いコードの読解 | `delete p; p = nullptr;` |

## よくあるミス

??? failure "二重 delete"
    2 回目は未定義動作です。

??? failure "new[] で作ったものに delete"
    未定義動作です。`delete[]` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`new`](new.md) | 作る |
| [`std::unique_ptr`](../../utilities/unique_ptr.md) | 自動で delete |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] new したものを解放
    - [x] nullptr には何もしない
    - [x] 二重解放しない

## 関連ページ

- [cpprefjp: delete 式](https://cpprefjp.github.io/reference/new/delete.html)
- [cppreference: delete 式](https://en.cppreference.com/w/cpp/memory/new/delete)
