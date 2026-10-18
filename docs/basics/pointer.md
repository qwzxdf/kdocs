---
title: ポインタ
tags:
  - 基礎
---

# ポインタ

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">C++98〜</span>
</div>

**ポインタ**は、**変数がメモリのどこにあるか（アドレス）を入れておく変数**です。`int* p = &x;` と書くと、`p` には `x` の場所が入り、`*p` で `x` の中身を読み書きできます。参照と違って「何も指していない」（`nullptr`）状態にでき、あとから別のものを指し直せます。今の C++ では、**持ち主（解放する責任）はスマートポインタ、ただ指すだけなら生ポインタ**と役割を分けて使います。

!!! tip "ポイント"
    - `&x` で場所を取り、`*p` で中身、`p->member` でメンバ。
    - 何も指さないときは `nullptr`。**使う前に必ず `nullptr` チェック**。
    - `new` / `delete` は自分で書かない。持ち主は [`std::unique_ptr`](../stl/utilities/unique_ptr.md)。
    - 生ポインタ `T*` は「持ち主ではない、ただ指しているだけ」の意味で使う。
    - 必ずある相手なら [参照](reference.md) のほうが安全。

## 基本

```cpp
#include <print>

int main() {
  int hp = 100;
  int* p = &hp;  // hp の場所を p に入れる

  *p -= 25;  // p が指している先（hp）を書き換える
  std::println("hp = {}", hp);

  int* none = nullptr;  // 何も指していない
  if (none == nullptr) {
    std::println("何も指していない");
  }
}
```

```text title="実行結果"
hp = 75
何も指していない
```

<div class="mem">
<div class="mem-step"><span class="mem-label">hp（アドレス 1000 番地）</span><span class="mem-cells"><span class="move">75</span></span></div>
<div class="mem-step"><span class="mem-label">p</span><span class="mem-cells"><span>1000</span></span><span class="mem-note">← 中身は「hp の場所」。*p で 1000 番地の中身を読む</span></div>
</div>

## 詳しく

### 記号のまとめ

| 書き方 | 意味 |
| --- | --- |
| `T* p` | T を指すポインタ型の変数 |
| `&x` | x のアドレス（場所） |
| `*p` | p が指している先の中身 |
| `p->m` | p が指している先のメンバ m（`(*p).m` と同じ） |
| `nullptr` | 何も指していない |
| `p + 1` | 次の要素の場所（配列の中でだけ意味がある） |

### 構造体を指す

```cpp
#include <print>
#include <string>

struct Enemy {
  std::string name;
  int hp;
};

int main() {
  Enemy boss = {"ドラゴン", 300};
  Enemy* target = &boss;
  target->hp -= 50;  // -> でメンバにアクセス
  std::println("{} HP {}", target->name, boss.hp);
}
```

```text title="実行結果"
ドラゴン HP 250
```

### 「指すだけ」の使い方

```cpp
#include <print>
#include <vector>

struct Enemy {
  int id;
  int hp;
};

// 見つからなければ nullptr を返す
Enemy* FindById(std::vector<Enemy>& enemies, int id) {
  for (auto& e : enemies) {
    if (e.id == id) {
      return &e;
    }
  }
  return nullptr;
}

int main() {
  std::vector<Enemy> enemies = {{1, 30}, {2, 50}};
  if (Enemy* e = FindById(enemies, 2)) {  // nullptr でなければ
    e->hp = 0;
  }
  std::println("{}", enemies[1].hp);
  std::println("{}", FindById(enemies, 9) == nullptr);
}
```

```text title="実行結果"
0
true
```

### const とポインタ

| 書き方 | 指す先を書き換え | ポインタ自体を付け替え |
| --- | --- | --- |
| `T* p` | できる | できる |
| `const T* p` | **できない** | できる |
| `T* const p` | できる | **できない** |
| `const T* const p` | できない | できない |

読むだけなら `const T*` を使います（`const` が `*` の左にあれば「指す先が const」）。

### 持ち主かどうか

| 型 | 持ち主（解放する責任） | 使う場面 |
| --- | --- | --- |
| [`std::unique_ptr<T>`](../stl/utilities/unique_ptr.md) | ○（1 人） | オブジェクトを作って持つ |
| [`std::shared_ptr<T>`](../stl/utilities/shared_ptr.md) | ○（複数） | 共有するリソース |
| `T*` | × | 指すだけ・使わせるだけ |
| `T&` | × | 必ずある相手を使わせる |

詳しくは [所有権](ownership.md) を参照してください。

### 配列とポインタ

```cpp
#include <print>

int main() {
  int scores[] = {10, 20, 30};
  int* p = scores;  // 配列の名前は先頭のポインタになる
  std::println("{} {} {}", *p, *(p + 1), p[2]);
}
```

```text title="実行結果"
10 20 30
```

今は配列に `std::vector` / `std::array`、関数に渡すなら `std::span` を使うので、ポインタの足し算を書くことはほぼありません。

## ゲームでの例

| 場面 | 例 |
| --- | --- |
| ターゲット | `Enemy* target_ = nullptr;`（持ち主ではない） |
| 親子関係 | `Transform* parent_;` |
| 検索結果 | 見つからなければ `nullptr` |
| C の API | `SDL_Window*`、`FILE*`（解放は Deleter 付き unique_ptr に任せる） |

<!-- fig:pointer-deref:begin -->

<svg class="fig illust motion" data-fig="pointer-deref" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-pointer-deref" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">ポインタ = 住所を入れた変数。*p で、その住所の中身を読み書きする</text>
<rect x="100" y="140" width="150" height="80" fill="#ffffff" stroke="#2563eb" stroke-width="2.5"/>
<text x="175" y="130" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#2563eb">int hp（住所 0x100）</text>
<text x="175" y="192" text-anchor="middle" style="font-size:30px;font-weight:700;fill:#1f2937" opacity="0">30<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5159;0.5161;1.0000" values="1;1;0;0"/></text>
<text x="175" y="192" text-anchor="middle" style="font-size:30px;font-weight:700;fill:#e5484d" opacity="0">50<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5159;0.5161;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1933;0.1935;1.0000" values="0;0;1;1"/><rect x="440" y="140" width="190" height="80" fill="#ffffff" stroke="#2ea043" stroke-width="2.5"/>
<text x="535" y="130" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#2ea043">int* p（住所 0x200）</text>
<text x="535" y="190" text-anchor="middle" style="font-size:26px;font-weight:700;fill:#1f2937">0x100</text>
</g>
<line x1="436" y1="180" x2="256" y2="180" stroke="#2ea043" stroke-width="3" marker-end="url(#arr-pointer-deref)" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2578;0.2581;1.0000" values="0;0;1;1"/></line>
<text x="390" y="300" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">int hp = 30;  hp という箱に 30 が入っている<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1933;0.1935;1.0000" values="1;1;0;0"/></text>
<text x="390" y="300" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">int* p = &amp;hp;  p の箱には、hp の住所 0x100 を入れる<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1933;0.1935;0.3868;0.3871;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="300" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">p は hp を「指している」<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3868;0.3871;0.5159;0.5161;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="300" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">*p = 50;  p が指す先(hp)の中身が 50 になる<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5159;0.5161;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:pointer-deref:end -->

## よくあるミス

??? failure "nullptr チェックを忘れる"
    ```cpp
    Enemy* e = FindById(enemies, 9);
    e->hp = 0;  // 見つからなければ nullptr を読んで落ちる
    ```

??? failure "消えたものを指し続ける（ダングリングポインタ）"
    ```cpp
    Enemy* target = &enemies[0];
    enemies.erase(enemies.begin());  // target が指していた要素は無くなった
    target->hp = 0;                  // 未定義動作
    ```

    相手が消えるかもしれないなら、ID で覚えるか [`std::weak_ptr`](../stl/utilities/shared_ptr.md) を使います。

??? failure "new したものを delete し忘れる"
    `new` を自分で書くと、途中で `return` したときなどに `delete` を忘れがちです。`std::make_unique` を使えば自動で消えます。

??? failure "初期化していないポインタを使う"
    `Enemy* p;` だけだと中身はゴミです。必ず `= nullptr` か実際の場所で初期化します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `&x` で場所、`*p` で中身、`p->m` でメンバ
    - [x] 使う前に `nullptr` チェック
    - [x] 生ポインタは「指すだけ」。持ち主は unique_ptr
    - [x] 消えたものを指し続けない

## 関連ページ

- [参照](reference.md)
- [所有権](ownership.md)
- [cppreference: Pointer declaration](https://en.cppreference.com/w/cpp/language/pointer)
