---
title: std::filesystem::proximate
summary: "基準のパスから見た相対パスを返す（作れなければ元のパス）。"
order: 900
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::proximate

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

[`relative`](relative.md) は便利ですが、ルートが違うパス（`C:` と `D:`）では空のパスを返します。ログの出力やパックのファイル名で、「相対にできるなら相対、できないなら絶対のまま」にしたいとき、空のパスを毎回確かめて分岐するのは面倒です。

`std::filesystem::proximate` は、`relative` と同じ動きで、<strong>相対パスにできないときは、`p` をそのまま返す</strong>関数です。

!!! tip "ポイント"
    - 相対パスにできるなら `relative` と同じ結果
    - できないとき（別のドライブなど）は、空ではなく `p` を返す
    - 「近いほうの表記」を選ぶ関数。表示用途に向く
    - `base` を省略すると、カレント ディレクトリが基準

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要と、[`path`](path.md) を先に読んでください。

## 関数の詳しい説明

### proximate {#proximate}

<span class="ver ver-17">C++17</span>

```cpp
path proximate(const path& p, const path& base = current_path());
path proximate(const path& p, std::error_code& ec);
path proximate(const path& p, const path& base, std::error_code& ec);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 変換するパス |
| `base` | `const path&` | 基準になるフォルダー |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

内部では、まず `relative(p, base)` を試します。その結果が空でなければ、それを返します。空だったときだけ、`weakly_canonical(p)` を返します。つまり、「近く（proximate）に表せるならその表記、無理なら絶対パス」です。

`relative` と違って、結果が空になることがないので、続けてそのまま文字列にして出力できます。ただし、戻り値が相対か絶対かは、パスの組み合わせで変わるので、<strong>返った値を基準のフォルダーに足して使う</strong>ような処理には向きません。表示と記録のための関数です。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <print>

int main() {
  namespace fs = std::filesystem;

  // 相対にできるときは、relative と同じ
  fs::path a = fs::proximate("/game/assets/hero.png", "/game");
  std::println("{}", a.generic_string());

  // 同じ場所なら "."
  fs::path b = fs::proximate("/game", "/game");
  std::println("{}", b.generic_string());

  // relative との違い: 結果が空になることはない
  std::println("空ではない: {}", !fs::proximate("/game/x", "/game/y").empty());
}
```

```text title="実行結果"
assets/hero.png
.
空ではない: true
```

## ゲームでの使いどころ

複数のドライブにまたがる可能性のあるファイルを、ログに出すときに使います。ゲーム フォルダーの中にあるアセットは相対で短く、ユーザーが外部から指定したファイルは絶対パスで、と自動で使い分けられます。

エラー レポートやデバッグ表示のように、見るための文字列を作る場面が中心です。

## よくあるミス

??? failure "戻り値を、必ず相対パスだと思って基準に足す"
    別のドライブなどで絶対パスが返ることがあります。`base / result` にすると、絶対パス同士の結合になり、意図と違う場所になります。

??? failure "`relative` と同じだと思って、空の結果の分岐を残す"
    `proximate` は空を返しません。分岐が不要になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`relative`](relative.md) | 相対にできないと空のパスを返す版 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 相対にできれば `relative` と同じ
    - [x] できないときは `p` を返す
    - [x] 表示や記録のための関数

## 関連ページ

- [cpprefjp: std::filesystem::proximate](https://cpprefjp.github.io/reference/filesystem/proximate.html)
- [cppreference: std::filesystem::proximate](https://en.cppreference.com/w/cpp/filesystem/proximate)
