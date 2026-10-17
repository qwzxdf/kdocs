---
title: モジュール境界とレイヤー設計
tags:
  - 設計
---

# モジュール境界とレイヤー設計

ゲームが大きくなると、「描画が入力を知っていて、入力がゲームロジックを知っていて、ゲームロジックが描画を知っていて…」と、**どのクラスもほかのクラスを直接知っている**状態になりがちです。こうなると、1 つ直すと別の場所が壊れ、ビルドも遅くなり、テストもできません。そこで、コードを<strong>モジュール（まとまり）</strong>に分けて、<strong>「どちらがどちらを知ってよいか」の向き（依存の向き）を決める</strong>のが、レイヤー設計です。ポイントは、**依存は一方向にし、循環させない**ことです。

!!! tip "ポイント"
    - コードを<strong>層（レイヤー）</strong>に分け、**上の層が下の層を使う**。**下の層は上の層を知らない**。
    - <strong>循環（A が B を使い、B が A を使う）を作らない。</strong> 作りそうになったら、インターフェースか、イベントで逆向きをなくす。
    - **変わりにくいもの**（数学、コンテナ）を下に、**変わりやすいもの**（ゲームの仕様、UI）を上に置く。
    - 境界には、**小さなインターフェース**を置く（[インターフェース設計](interface-design.md)）。
    - フォルダー（や CMake のターゲット）を、モジュールに合わせて分けて、**依存を機械的にチェック**する。

## 悪い例：全部が全部を知っている

<div class="anim" data-type="graph" data-label="依存が絡み合うと、どれも変更できない">
n g Game 1 0
n p Player 0 1
n e Enemy 1 1
n u UI 2 1
n r Renderer 3 1
n a Audio 1.5 2
l g p
l g e
l g u
l g r
l p e
l e p
l e u
l u e
l u r
l r u
l a p
l a r
l r g
</div>

| 問題 | 説明 |
| --- | --- |
| 1 つ変えると、全部に影響する | どこが何を使っているか分からない |
| ビルドが遅い | 全部が全部を `#include` していて、1 つ変えると全部再ビルド |
| 単体でテストできない | `Player` を動かすのに、`Renderer` と `Audio` まで必要 |
| 循環依存 | `Player` ⇄ `Enemy` のように、お互いを知っていて、ヘッダが `#include` しあう |

## 良い例：レイヤーに分ける

<div class="anim" data-type="graph" data-label="層は、上から下へ、一方向に依存する">
n a アプリ層_（main・起動） 0 0
n g ゲーム層_（敵・ルール） 0 1
n e エンジン層_（描画・ECS・音） 0 2
n b 基盤層_（数学・コンテナ・ログ） 0 3
l a g - 使う
l g e - 使う
l e b - 使う
</div>

| 層 | 中身 | 依存してよい先 |
| --- | --- | --- |
| **アプリ層** | `main`、初期化、ゲームループの組み立て | すべて |
| **ゲーム層** | 敵、アイテム、レベル、ルール | エンジン層、基盤層 |
| **エンジン層** | 描画、音、入力、シーン、ECS、リソース管理 | 基盤層 |
| **基盤層** | 数学（`Vec3`、`Mat4`）、コンテナ、ログ、時間、ファイル | （標準ライブラリだけ） |

<div class="anim" data-type="graph" data-label="依存の向きを一方向にそろえる">
n app アプリ 1 0
n game ゲーム 1 1
n engine エンジン 1 2
n base 基盤 1 3
l app game hit
l game engine hit
l engine base hit
l base app gone 逆向き
# 上から下へだけ依存する
---
n app アプリ 1 0
n game ゲーム 1 1
n engine エンジン 1 2
n base 基盤 1 3
l app game
l game engine
l engine base
l engine game gone 循環
# 下の層が上の層を知ると、循環になる（これを禁止する）
---
n game ゲーム 0 1
n engine エンジン 1 1
n iface イベント 0.5 2 new
l game iface new 通知を受ける
l engine iface new 通知を出す
# どうしても上へ伝えたいときは、イベントやインターフェースを間に置く
</div>

## 依存の向きを守る方法

### 1. 上へ伝えたいときは、イベント・コールバック

エンジン層の `Physics` が「衝突した」とゲーム層に伝えたいとき、`Physics` が `Player` を直接呼ぶと、**下の層が上の層を知る**ことになります。代わりに、**エンジン層が「衝突したら、これを呼んで」と、登録できる口**を作ります。

```cpp
// エンジン層：ゲームを知らない
class Physics {
 public:
  using CollisionCallback = std::function<void(EntityId, EntityId)>;
  void SetOnCollision(CollisionCallback callback) { on_collision_ = std::move(callback); }

  void Step() {
    for (auto [a, b] : DetectCollisions()) {
      if (on_collision_) {
        on_collision_(a, b);  // 誰が受け取るかは知らない
      }
    }
  }

 private:
  CollisionCallback on_collision_;
};

// ゲーム層：エンジンを知っていて、登録する
physics.SetOnCollision([&game](EntityId a, EntityId b) { game.OnHit(a, b); });
```

詳しくは [イベントシステム](../patterns/event.md) を見てください。

### 2. 依存の向きを、インターフェースで逆にする（依存性逆転）

上の層の都合で下の層を使いたいとき、**上の層がインターフェースを持ち、下の層がそれを実装する**と、依存の向きが逆になります。

<div class="anim" data-type="graph" data-label="依存性の逆転：インターフェースを、使う側が持つ">
n g ゲーム層 0 0
n f ファイル保存_（具体的な実装） 1 0
l g f - 使う
---
n g ゲーム層 0 0
n i ISaveStorage_（ゲーム層が持つ） 1 0 new
n f FileSaveStorage_（下の層） 2 1 hit
l g i - 使う
l f i - 実装する
</div>

### 3. 循環を、共通の部品にまとめて切る

`Player` と `Enemy` が、お互いを使っているなら、**共通の部分（`Health`、`Transform`）を別のモジュールに出して**、どちらもそれを使うようにします。

## ヘッダの循環を防ぐ

クラスの循環は、ヘッダの循環（`a.h` が `b.h` を、`b.h` が `a.h` を `#include`）として現れます。

| 方法 | 説明 |
| --- | --- |
| **前方宣言** | `class Enemy;` と宣言だけして、`#include` しない（[ヘッダとソースの分け方](header-source.md)） |
| **`.cpp` で `#include` する** | ヘッダには宣言だけ、実装の `.cpp` で必要なものを include する |
| **インターフェースを挟む** | 具体的なクラスではなく、`IEnemy` に依存する |
| **ID（ハンドル）で持つ** | ポインタの代わりに ID で持てば、型を知らなくてよい（[ハンドル](../../engine/handle.md)） |

## フォルダー構成とモジュール

フォルダーとビルドの単位を、レイヤーに合わせます。

```text
src/
├── base/       … 基盤層（math、container、log）  → 何にも依存しない
├── engine/     … エンジン層（render、audio、scene、ecs）→ base に依存
├── game/       … ゲーム層（enemy、player、level）→ engine、base に依存
└── app/        … アプリ層（main.cpp）→ すべてに依存
```

| 工夫 | 説明 |
| --- | --- |
| **フォルダーごとに別の静的ライブラリ**（Visual Studio のプロジェクト / CMake のターゲット） | 逆向きの `#include` が、**リンクエラーやコンパイルエラーで見つかる** |
| **`#include` のルール** | 「`engine/` は `game/` を include しない」を、コードレビューやスクリプトで確認する |
| **公開ヘッダと内部ヘッダを分ける** | `include/` に外へ出すもの、`src/` に内部のものを置く |

## 境界を作るときの判断

| 質問 | 答えが「はい」なら |
| --- | --- |
| それは、ゲームを変えても使い回せるか | エンジン層に置く |
| それは、数学やコンテナのように、何にも依存しないか | 基盤層に置く |
| 2 つのモジュールが、お互いを必要としているか | 共通部分を切り出す、または、片方向にして、逆はイベントで |
| 同じ人・同じ理由で変更されるか | 同じモジュールにまとめる |

## ゲームでの使いどころ

| 場面 | 設計 |
| --- | --- |
| 描画エンジンと、ゲームの切り離し | 描画は、`DrawCommand` のような**データ**を受け取るだけ。ゲームの型を知らない |
| 入力 | OS の入力を、「ジャンプ」「攻撃」のような**ゲームの操作**に変換する層を挟む |
| 保存と読み込み | ゲーム層は `ISaveStorage` だけ知る。ファイル・クラウドは下で実装 |
| ツールとゲームで共通のコード | 基盤層・エンジン層を、ツールのプロジェクトからも使う |
| 描画のスレッド | ゲームの更新と、描画で、共有するデータを**境界で受け渡す**（[並行処理の設計](../practice/concurrency-design.md)） |

## よくあるミス

??? failure "「便利だから」と、下の層から上の層の関数を呼ぶ"
    1 か所だけの例外が、あとから全体を絡ませます。必要なら、イベント・コールバックで逆向きを作ります。

??? failure "`common.h` に何でも入れる"
    全部が `common.h` を `#include` すると、`common.h` が全部のものに依存してしまい、レイヤーが崩れます。小さな部品ごとにヘッダを分けます。

??? failure "層が多すぎる"
    学生のゲームで、10 層も作ると、何をどの層に置くかで迷うだけです。<strong>3〜4 層（基盤・エンジン・ゲーム・アプリ）</strong>で十分です。

??? failure "グローバル変数・シングルトンで、層を飛び越えて呼ぶ"
    `GameManager::Instance()` を、どこからでも呼べると、依存の向きが見えなくなります（[シングルトン](../patterns/singleton.md)）。必要なものは、引数やコンストラクタで渡します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] コードを層に分けて、依存は**上から下への一方向**だけにする
    - [x] 循環しそうになったら、イベント、インターフェース、共通部品の切り出しで切る
    - [x] 変わりにくいものを下、変わりやすいものを上に置く
    - [x] フォルダーとビルドの単位を、層に合わせる
    - [x] 層は 3〜4 つで十分

## 関連ページ

- [ヘッダとソースの分け方](header-source.md)
- [インターフェース設計](interface-design.md)
- [依存性の注入](../patterns/dependency-injection.md)
- [イベントシステム](../patterns/event.md)
- [ビルドと CMake の構成](../practice/build-cmake.md)
