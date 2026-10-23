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

`new` で作ったオブジェクトは、使い終わったら自分で片付けなければ、メモリリークになります。`delete` は、`new` で作ったオブジェクトのデストラクターを呼んで、メモリを解放する式です。`nullptr` に対しては何もしないので、確かめずに呼べます。解放したあとのポインターは使えません。現代の C++ では、`unique_ptr` が自動で `delete` してくれます。

!!! tip "ポイント"
    - `new` には `delete`、`new[]` には `delete[]`。
    - 二重に `delete` しない。
    - `unique_ptr` に任せれば、書かなくてよい。

!!! info "このページを読む前に"
    [`new` 式](new.md)を先に読んでください。`delete` は `new` と対になっています。

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

## しくみ

`delete p` は、2 段階で動きます。まず `p` が指すオブジェクトのデストラクターを呼び、次に `operator delete` でメモリを返します。

基底クラスのポインターで派生クラスのオブジェクトを `delete` するとき、基底クラスのデストラクターが `virtual` でないと、派生クラスのデストラクターが呼ばれず、未定義動作になります。継承して使うクラスは、デストラクターを `virtual` にします。

`delete` したあとのポインターは、解放されたメモリを指したままです（ぶら下がりポインター）。再び使うと未定義動作になるので、`p = nullptr;` として、使えない印を付ける習慣があります。

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

通常のゲームのコードでは、`unique_ptr` や `vector` に任せるので、`delete` を直接書く場面は少なめです。

自作のメモリ管理（オブジェクトプールなど）を書くときには、配置 `new` で作ったオブジェクトを `delete` で解放してはいけません。確保したのはプールで、`delete` は `operator delete` を呼んでしまうからです。破棄は、デストラクターだけを呼ぶ `std::destroy_at` で行い、メモリはプールへ返します。

古いコードを引き継ぐときは、`delete` の呼び出し場所から、持ち主の設計を読み取ります。誰が `new` して、誰が `delete` するのかを整理して、`unique_ptr` に置き換えます。

## よくあるミス

??? failure "同じポインターを二重に `delete` する"
    コピーしたポインターを、別々の場所で `delete` すると、二重解放でクラッシュします。持ち主は 1 人にして、他は参照や生ポインターで見るだけにします。

??? failure "`new[]` を `delete` で解放する"
    `new[]` で作った配列は、`delete[]` で解放します。`delete` だと、要素のデストラクターが 1 つ目しか呼ばれないなど、未定義動作になります。

??? failure "基底クラスのデストラクターが `virtual` でない"
    `Base* p = new Derived; delete p;` で、`Base` のデストラクターが `virtual` でないと、`Derived` の後始末が行われません。継承するクラスのデストラクターは `virtual` にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`new` 式](new.md) | オブジェクトを作る。`delete` と対 |
| `std::unique_ptr` | スコープを抜けると自動で `delete` する |
| `std::destroy_at` | デストラクターだけを呼ぶ。配置 `new` で作ったものに使う |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `new` には `delete`、`new[]` には `delete[]`。
    - [x] 二重に `delete` しない。解放後は `nullptr` を入れる。
    - [x] `unique_ptr` に任せれば書かなくてよい。

## 関連ページ

- [cpprefjp: delete 式](https://cpprefjp.github.io/reference/new/delete.html)
- [cppreference: delete 式](https://en.cppreference.com/w/cpp/memory/new/delete)
