---
title: offsetof
summary: "構造体のメンバが、先頭から何バイト目にあるかを求める。"
order: 24
group: 基本の型（<cstddef>）
tags:
  - 型・言語サポート
---

# offsetof

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cstddef>`
</div>

`offsetof(型, メンバ)` は、**構造体のメンバが、先頭から何バイト目にあるかを返す**マクロです。頂点バッファのレイアウト（`D3D12_INPUT_ELEMENT_DESC` の `AlignedByteOffset`）、バイナリ形式のフィールド位置の確認に使います。**標準レイアウトの型にだけ**使えます。

!!! tip "ポイント"
    - 頂点構造体のメンバの位置を、手書きせずに取れる。
    - 標準レイアウトでない型（仮想関数あり、複雑な継承）には、使えない。
    - パディング（隙間）の分も含めた位置が返る。

!!! info "このページを読む前に"
    - [STL](../index.md)（STL 全体の地図（どこに何があるか））
    - [テンプレート](../../basics/template.md)（テンプレートの基礎）

## 関数の詳しい説明

### offsetof {#offsetof}

```cpp
#define offsetof(type, member) /* 実装定義 */
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `type` | 型 | 構造体の型 |
| `member` | メンバ名 | 位置を知りたいメンバ |

- 戻り値: メンバの位置（`size_t`）
- 計算量: コンパイル時

```cpp
#include <cstddef>
#include <print>

struct Vertex {
  float position[3];
  float uv[2];
};

int main() {
  std::println("{} {}", offsetof(Vertex, position), offsetof(Vertex, uv));
}
```

```text title="実行結果"
0 12
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| DirectX の頂点レイアウトの位置 | `offsetof(Vertex, uv)` |

## よくあるミス

??? failure "標準レイアウトでない型に使う"
    仮想関数を持つ型などでは、結果が不定です。

## 類似

| 名前 | 違い |
| --- | --- |
| `alignof` / `sizeof` | 型の大きさと境界 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] メンバの位置を求める
    - [x] 標準レイアウトの型だけ
    - [x] 頂点レイアウトの確認に

## 関連ページ

- [cpprefjp: offsetof](https://cpprefjp.github.io/reference/cstddef/offsetof.html)
- [cppreference: offsetof](https://en.cppreference.com/w/cpp/types/offsetof)
