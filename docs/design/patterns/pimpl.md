---
title: PImpl（実装の隠蔽）
tags:
  - 設計
---

# PImpl（実装の隠蔽）

**PImpl**（ピンプル、Pointer to Implementation）は、クラスの中身（メンバ変数やプライベートな関数）を `.cpp` の中に隠すためのテクニックです。ヘッダには「実装クラスへのポインタ」1 つだけを置き、本当のメンバは `.cpp` で定義します。そうすると、ヘッダを `#include` する人は、中身で使っているライブラリ（`<windows.h>`、DirectX、FMOD など）を知らなくてよく、中身を変えても、ヘッダを include しているファイルを再コンパイルしなくて済みます。ビルド時間の短縮と、外部ライブラリの影響を閉じ込めるのに役立ちます。

!!! tip "ポイント"
    - ヘッダには **`std::unique_ptr<Impl> impl_;`** だけを置き、`struct Impl;` は**前方宣言**にする。
    - `Impl` の定義と、すべてのメンバ関数の実装は、`.cpp` に書く。
    - デストラクタは、`.cpp` で `= default` と書く（ヘッダに書くと、`Impl` が不完全な型でコンパイルエラーになる）。
    - 代償は、ヒープの確保が 1 回増えることと、間接参照が 1 回増えること。毎フレーム何万個も作るものには向かない。
    - 向いているのは、外部ライブラリを隠したいクラス（サウンド、描画、ファイル）と、ヘッダを頻繁に変更するクラス。

!!! info "このページを読む前に"
    - [デザインパターン早見表](index.md)（このセクション全体の地図と、読む順番）
    - [設計の基本原則](../foundations/principles.md)（設計の基本原則）

## 悪い例：ヘッダに外部ライブラリが見える

```cpp
// audio.h
#include <fmod.hpp>          // ← FMOD のヘッダをここで include してしまっている
#include <string>
#include <unordered_map>

class Audio {
 public:
  void Play(const std::string& name);

 private:
  FMOD::System* system_ = nullptr;                                // FMOD の型が見える
  std::unordered_map<std::string, FMOD::Sound*> sounds_;
  int channel_count_ = 0;
};
```

### 何が困るか

| 問題 | 説明 |
| --- | --- |
| **`audio.h` を include したファイルは、すべて FMOD の `#include` を引き込む** | 無関係なファイルまで、FMOD が必要になる |
| ビルドが遅くなる | 巨大な外部ヘッダが何百回もコンパイルされる |
| メンバを 1 つ足すだけで、全部再ビルド | `audio.h` を include している全ファイルが再コンパイルされる |
| 外部ライブラリの名前が全体に漏れる | マクロや型名が衝突することがある（`<windows.h>` の `min` / `max` など） |

## 良い例：PImpl で隠す

### ヘッダ（`audio.h`）：中身を見せない

```cpp
// audio.h
#include <memory>
#include <string_view>

class Audio {
 public:
  Audio();
  ~Audio();                                   // 宣言だけ（実装は .cpp）

  Audio(const Audio&) = delete;
  Audio& operator=(const Audio&) = delete;
  Audio(Audio&&) noexcept;                    // ムーブも宣言だけ
  Audio& operator=(Audio&&) noexcept;

  void Play(std::string_view name);

 private:
  struct Impl;                                // 前方宣言：中身は .cpp にある
  std::unique_ptr<Impl> impl_;                // ポインタ 1 つだけ
};
```

### ソース（`audio.cpp`）：中身を書く

```cpp
// audio.cpp
#include "audio.h"

#include <fmod.hpp>          // FMOD は、ここだけで include する
#include <string>
#include <unordered_map>

struct Audio::Impl {
  FMOD::System* system = nullptr;
  std::unordered_map<std::string, FMOD::Sound*> sounds;
  int channel_count = 0;
};

Audio::Audio() : impl_(std::make_unique<Impl>()) {
  FMOD::System_Create(&impl_->system);
  impl_->system->init(32, FMOD_INIT_NORMAL, nullptr);
}

Audio::~Audio() = default;                    // Impl が完全な型になった、ここで書く
Audio::Audio(Audio&&) noexcept = default;
Audio& Audio::operator=(Audio&&) noexcept = default;

void Audio::Play(std::string_view name) {
  // impl_->system を使って再生する
}
```

<div class="anim" data-type="graph" data-label="PImpl：ヘッダの依存を切る">
n game ゲーム 0 1
n header audio.h 1 1 hit
n fmod fmod.hpp 2 0 gone
n impl audio.cpp 2 1
l game header hit include
l header fmod gone include
l impl fmod hit include
l impl header hit
# 通常：audio.h が fmod.hpp を include するので、ゲームも FMOD に依存する
---
n game ゲーム 0 1
n header audio.h 1 1 hit
n fmod fmod.hpp 2 0
n impl audio.cpp 2 1 hit
l game header hit include
l impl fmod hit include
l impl header hit
# PImpl：fmod.hpp を include するのは audio.cpp だけ。ゲームは FMOD を知らない
</div>

## PImpl で変わること

| 項目 | 通常 | PImpl |
| --- | --- | --- |
| ヘッダが引き込む `#include` | 外部ライブラリが入る | **最小**（`<memory>` だけ） |
| メンバを変えたときの再コンパイル | ヘッダを include した全ファイル | `audio.cpp` だけ |
| 外部ライブラリの型の漏れ | ヘッダから見える | 隠れる |
| オブジェクトの作成 | スタックに置ける | ヒープ確保が 1 回増える |
| 実行時の速さ | 直接アクセス | 間接参照が 1 回増える（ほぼ無視できる） |
| ABI（バイナリの互換性） | クラスの大きさが変わると壊れる | クラスの大きさが変わらない（DLL の公開に向く） |

## 注意点

### 1. デストラクタとムーブは、`.cpp` で `= default`

`std::unique_ptr<Impl>` は、**`Impl` が完全な型でないと、デストラクタをコンパイルできません**（破棄のコードで `Impl` の大きさが必要）。ヘッダに `~Audio() = default;` と書くと、`Impl` がまだ前方宣言のままなので、エラーになります。ヘッダには宣言だけ、`.cpp` で `= default` と書きます。

### 2. const の伝わり方

`const` メンバ関数の中でも、`impl_`（ポインタ）自体は const でも、指す先の `Impl` は const になりません。const 正しさが、自動では守られません。

```cpp
void Audio::Query() const {
  impl_->channel_count = 3;   // const 関数なのに、書き換えられてしまう（エラーにならない）
}
```

意識して、const 関数の中では、`Impl` を変更しないようにします。

### 3. 代わりの隠し方

| 方法 | 説明 | 向いている場面 |
| --- | --- | --- |
| PImpl | ポインタで中身を隠す | 外部ライブラリを隠したい、ヘッダの変更を減らしたい |
| インターフェース + ファクトリ | 抽象クラスだけを公開し、`CreateAudio()` で実装を返す | 実装を差し替えたいとき（[インターフェース設計](../foundations/interface-design.md)） |
| 前方宣言 | ヘッダでは、`class Enemy;` と宣言して、ポインタ・参照だけで使う | クラスの間の依存を減らす（[ヘッダとソース](../foundations/header-source.md)） |

PImpl は「1 つの具体的なクラスを隠す」、インターフェースは「実装を差し替えられる」と使い分けます。

## 使うか迷ったら

| 質問 | はい → PImpl を検討 |
| --- | --- |
| そのクラスのヘッダが重い外部ヘッダ（`<windows.h>`、DirectX、FMOD）を必要とするか | はい |
| そのヘッダを多くのファイルが include しているか | はい |
| そのクラスは、頻繁に（メンバ追加などで）変更されるか | はい |
| DLL として公開し、ABI を保ちたいか | はい |
| 毎フレーム、大量に作って壊すか | **いいえ**（ヒープ確保が増えるので向かない） |
| 小さくて、シンプルなクラスか | いいえ（効果が小さい） |

## ゲームでの使いどころ

| 場面 | 使い方 |
| --- | --- |
| サウンド・描画・入力のラッパー | OS や外部ライブラリの型（`HWND`、`ID3D11Device*`、`FMOD::System*`）をヘッダに出さない |
| ビルド時間が長くなってきたとき | 重い `#include` を `.cpp` に追い出す |
| ライブラリを作って配るとき | 公開ヘッダを小さく安定させる |
| プラットフォームごとの実装（Windows と Linux） | 同じヘッダで、`Impl` だけをプラットフォームごとに切り替える |

## よくあるミス

??? failure "`~Audio() = default;` をヘッダに書く"
    `std::unique_ptr<Impl>` の破棄に `Impl` の完全な型が必要で、`error: invalid application of 'sizeof' to an incomplete type` のようなエラーになります。デストラクタは、ヘッダに宣言だけ、`.cpp` で `= default` と書きます。

??? failure "ムーブを宣言し忘れる"
    デストラクタを宣言すると、ムーブが自動では作られなくなります。必要なら、ヘッダに宣言して、`.cpp` で `= default` にします。

??? failure "小さなクラスまで、全部 PImpl にする"
    `Vec3` や `Timer` のような、小さくて軽いクラスに PImpl を使うと、ヒープ確保が無駄に増えて、遅くなります。重い依存があるクラスだけにします。

??? failure "`Impl` を `.h` に定義してしまう"
    `struct Audio::Impl { ... };` をヘッダに書くと、隠す意味がありません。`.cpp` に書きます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ヘッダには `struct Impl;` と `std::unique_ptr<Impl> impl_;` だけ
    - [x] `Impl` とメンバ関数は `.cpp`。デストラクタとムーブも `.cpp` で `= default`
    - [x] 外部ライブラリを隠し、ビルドを速くする。代償はヒープ確保が 1 回
    - [x] 毎フレーム大量に作るものには向かない
    - [x] 実装を差し替えたいなら、インターフェースのほうが向いている

## 関連ページ

- [ヘッダとソースの分け方](../foundations/header-source.md)
- [インターフェース設計](../foundations/interface-design.md)
- [ビルドと CMake の構成](../practice/build-cmake.md)
- [std::unique_ptr](../../stl/utilities/unique_ptr.md)
- [コンパイラの最適化（ビルド時間）](../../optimize/compiler.md)
