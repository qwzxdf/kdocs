---
title: ヘッダとソースの分け方
tags:
  - 設計
---

# ヘッダとソースの分け方

C++ では、クラスの**宣言**（どんな関数があるか）をヘッダファイル（`.h`）に定義（関数の中身）をソースファイル（`.cpp`）に書くのが基本です。他のファイルはヘッダを `#include` して使います。分け方が悪いと、「1 行直しただけでビルドに 5 分かかる」「お互いを include し合ってコンパイルが通らない」といった問題が起きます。

!!! tip "ポイント"
    - ヘッダの先頭には **`#pragma once`**（または include ガード）。
    - **ヘッダには必要最小限の `#include`**。ポインタや参照で使うだけの型は前方宣言で済ませる。
    - 関数の中身は基本的に `.cpp` に書く。テンプレートと短い関数（ゲッターなど）だけヘッダに書く。
    - 2 つのヘッダがお互いを include したら、前方宣言で循環を切る。
    - ヘッダに `using namespace std;` を書かない。

!!! info "このページを読む前に"
    - [design/index.md](../index.md)（このセクション全体の地図と、読む順番）
    - [設計の基本原則](principles.md)（設計の基本原則）

## 基本の形

```cpp
// player.h ―― 宣言（使う人が見るもの）
#pragma once

#include <string>  // メンバに std::string を持つので必要

class Weapon;  // ポインタで使うだけなので、前方宣言で十分

class Player {
 public:
  explicit Player(std::string name);
  void Equip(Weapon* weapon);
  int Attack() const;

 private:
  std::string name_;
  Weapon* weapon_ = nullptr;
};
```

```cpp
// player.cpp ―― 定義（中身）
#include "player.h"

#include <utility>

#include "weapon.h"  // 中身を使うので、ここで初めて include

Player::Player(std::string name) : name_(std::move(name)) {}

void Player::Equip(Weapon* weapon) { weapon_ = weapon; }

int Player::Attack() const { return weapon_ != nullptr ? weapon_->power() : 1; }
```

## 詳しく

### #pragma once と include ガード

同じヘッダが 2 回 include されると、クラスが 2 回定義されてエラーになります。それを防ぐのが `#pragma once` です。

```cpp
#pragma once  // 主要なコンパイラすべてで使える。短くて間違えにくい
```

Google Style では、マクロを使った include ガードを推奨しています。

```cpp
#ifndef GAME_PLAYER_H_
#define GAME_PLAYER_H_
// ...
#endif  // GAME_PLAYER_H_
```

### 前方宣言で include を減らす

| ヘッダの中での使い方 | include が必要？ |
| --- | --- |
| `Weapon* weapon_;` / `Weapon& weapon` | **不要**（前方宣言 `class Weapon;` で OK） |
| `std::unique_ptr<Weapon> weapon_;` | 不要（ただしデストラクタを .cpp で定義する） |
| 関数の引数・戻り値に `Weapon`（値） | 宣言だけなら不要 |
| `Weapon weapon_;`（値のメンバ） | 必要（大きさが分からないといけない） |
| 継承 `class Sword : public Weapon` | 必要 |
| ヘッダの中で `weapon_->power()` を呼ぶ | 必要 |

include を減らすと、ヘッダを書き換えたときに再コンパイルされるファイルが減り、ビルドが速くなります。

### 循環 include を切る

<div class="anim" data-type="graph" data-label="互いに include すると、循環してエラーになる">
n p player.h 0 0
n e enemy.h 1 0
l p e - include
---
n p player.h 0 0
n e enemy.h 1 0
l p e - include
l e p - include
---
n p player.h 0 0 gone
n e enemy.h 1 0 hit
l p e - include
l e p - 相手がまだ分からずエラー
</div>

どちらか（または両方）を前方宣言に変えます。

```cpp
// enemy.h
#pragma once
class Player;  // include の代わりに前方宣言

class Enemy {
 public:
  void Chase(const Player& target);  // 参照なので前方宣言で足りる
};
```

それでも切れないなら、設計を見直すサインです（[疎結合](principles.md#2-疎結合依存を減らす)）。

### ヘッダに書くもの・ソースに書くもの

| 書くもの | 場所 |
| --- | --- |
| クラスの宣言、関数の宣言 | ヘッダ |
| 関数の中身 | ソース |
| テンプレートの中身 | ヘッダ（[テンプレート](../../basics/template.md#テンプレートはヘッダに書く)） |
| 短いゲッター（1 行） | ヘッダでも OK |
| `constexpr` / `inline` の定数・関数 | ヘッダ |
| そのファイルの中だけで使う関数・定数 | ソースの無名名前空間 |

```cpp
// enemy.cpp
#include "enemy.h"

namespace {  // このファイルの中だけで使える（他のファイルと名前がぶつからない）

constexpr float kChaseSpeed = 2.5f;

float Distance(float a, float b) { return a > b ? a - b : b - a; }

}  // namespace
```

### include の順番（Google Style）

```cpp
#include "player.h"     // 1. 対応するヘッダ（自分自身）を最初に

#include <string>       // 2. C++ 標準ライブラリ
#include <vector>

#include "SDL.h"        // 3. 外部ライブラリ

#include "weapon.h"     // 4. 自分のプロジェクトのヘッダ
```

対応するヘッダを最初に書くと、そのヘッダが「自分だけで必要なものを include できているか」を確かめられます。

### PImpl（実装を隠す）

ヘッダから private メンバまで全部隠したいときの方法です。外部ライブラリの型をヘッダに出したくないときに使います。

```cpp
// audio.h
#pragma once
#include <memory>

class Audio {
 public:
  Audio();
  ~Audio();  // .cpp で定義する（Impl の中身がそこで分かるため）
  void Play(const char* name);

 private:
  struct Impl;                  // 中身はヘッダでは見せない
  std::unique_ptr<Impl> impl_;
};
```

```cpp
// audio.cpp
#include "audio.h"
#include "fmod.hpp"  // 外部ライブラリはここでだけ include

struct Audio::Impl {
  FMOD::System* system = nullptr;
};

Audio::Audio() : impl_(std::make_unique<Impl>()) {}
Audio::~Audio() = default;
void Audio::Play(const char* name) { /* impl_->system を使う */ }
```

## ゲームでの例

| 状況 | 対策 |
| --- | --- |
| ゲーム全体のヘッダ `Game.h` を全ファイルが include していて、変更のたびに全部再ビルド | 必要なヘッダだけを include、前方宣言を使う |
| Player と Enemy がお互いを include | 前方宣言、またはイベントで依存を切る |
| DirectX や SDL のヘッダがあちこちに漏れている | PImpl やラッパークラスで 1 か所に閉じ込める |

## よくある失敗

??? failure "ヘッダに using namespace std; を書く"
    そのヘッダを include した全ファイルに広がり、名前のぶつかり（`std::count` と自分の `count` など）が起きます。

??? failure "ヘッダで関数を定義して、リンクエラー（多重定義）"
    普通の関数の中身をヘッダに書くと、include した .cpp の数だけ定義ができてリンクエラーになります。ヘッダに書くなら `inline` を付けます。

??? failure "何でも include する"
    「念のため」に include を増やすと、ビルドが遅くなり、依存関係も分かりにくくなります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ヘッダには `#pragma once`
    - [x] ポインタ・参照だけなら前方宣言
    - [x] 中身は .cpp、テンプレートはヘッダ
    - [x] ヘッダに `using namespace` を書かない

## 関連ページ

- [テンプレート](../../basics/template.md)
- [Google C++ Style Guide: Header Files](https://google.github.io/styleguide/cppguide.html#Header_Files)
- [コンパイラの最適化（ビルド時間）](../../optimize/compiler.md)
- [Include What You Use（IWYU）](../../optimize/build-time.md#iwyu)
