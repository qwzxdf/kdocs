---
title: 所有権とライフタイム設計
tags:
  - 設計
---

# 所有権とライフタイム設計

C++ のバグで一番多いのは、<strong>「もう無いものを触る」</strong>ことです。`delete` したポインタを使う、消えたローカル変数の参照を持ち続ける、`vector` が引っ越したあとに古いポインタを使う、などです。これを防ぐ設計の考え方が所有権（誰が消す責任を持つか）とライフタイム（そのものがいつまで生きているか）です。[基礎の所有権](../../basics/ownership.md) で仕組みを学んだら、このページで「設計としてどう決めるか」を考えます。

!!! tip "ポイント"
    - <strong>すべてのオブジェクトに「持ち主」を 1 人決める。</strong> 持ち主が消えるときに、持たれているものも消える。
    - **借りる側（参照・生ポインタ）は、持ち主より長く生きない**ようにする。これがライフタイム設計。
    - 持ち主は `std::unique_ptr` か、`vector` などのコンテナ、またはメンバ変数。共有（`shared_ptr`）は最後の手段。
    - 「消えるかもしれない相手」を指すときは、ポインタではなく [ハンドル](../../engine/handle.md)（番号 + 世代） にする。
    - 関数の引数や戻り値の型で、所有権が移るのか、借りるだけなのかを表現する。

!!! info "このページを読む前に"
    - [design/index.md](../index.md)（このセクション全体の地図と、読む順番）
    - [設計の基本原則](principles.md)（設計の基本原則）

## 持ち主と借りる側

<div class="anim" data-type="graph" data-label="持ち主が消えると、借りている側は使えなくなる">
n o 持ち主 0 0
n x オブジェクト 1 0
n b 借りる側 2 0
l o x - 持つ（消す責任）
l b x - 借りる
---
n o 持ち主 0 0 gone
n x オブジェクト 1 0 gone
n b 借りる側 2 0 hit
l b x - ぶら下がり
</div>

| 立場 | 型の例 | 責任 |
| --- | --- | --- |
| **持ち主**（1 人だけ） | メンバ変数、`std::vector<T>`、`std::unique_ptr<T>` | 作る、消す |
| 借りる側 | `T&`、`const T&`、`T*`（生ポインタ）、`std::span<T>`、`std::string_view` | 使うだけ。消さない。持ち主より長生きしない |
| 共有の持ち主 | `std::shared_ptr<T>` | 最後の 1 人が消える |
| 弱い参照 | `std::weak_ptr<T>`、ハンドル | 相手が消えたかを確認してから使う |

## 悪い例：持ち主が決まっていない

```cpp
class Enemy;

class Bullet {
 public:
  Bullet(Enemy* owner) : owner_(owner) {}  // 撃った敵を覚えておく
  void OnHit() { owner_->AddScore(10); }   // 敵が先に倒されていたら…？

 private:
  Enemy* owner_;  // 持ち主？ 借りているだけ？ いつ消えるか分からない
};
```

### 何が困るか

- `Enemy` が倒されて消えたあとに、弾が当たると、**消えた敵を触って**クラッシュする（ダングリングポインタ）
- 「誰が `Enemy` を消すのか」がコードから読めない
- 弾を管理している人は、敵がいつ消えるかを知らない

## 良い例 1：持ち主を 1 人に決める

敵を持っているのは**ステージ**（`std::vector<std::unique_ptr<Enemy>>`）の 1 人だけ、と決めます。

```cpp
class Stage {
 public:
  Enemy& Spawn() {
    enemies_.push_back(std::make_unique<Enemy>());
    return *enemies_.back();
  }
  void Update() {
    std::erase_if(enemies_, [](const auto& e) { return e->IsDead(); });  // 持ち主が消す
  }

 private:
  std::vector<std::unique_ptr<Enemy>> enemies_;  // ここだけが持ち主
};
```

## 良い例 2：消えるかもしれない相手は「番号」で覚える

弾が敵を「いつまでも覚えている」必要があるなら、ポインタではなく <strong>ハンドル（番号 + 世代）</strong> で覚えます。

```cpp
class Bullet {
 public:
  Bullet(EnemyHandle owner) : owner_(owner) {}
  void OnHit(Stage& stage) {
    if (Enemy* owner = stage.Find(owner_)) {  // 生きているか、使うたびに確認する
      owner->AddScore(10);
    }
  }

 private:
  EnemyHandle owner_;  // 番号。相手が消えても壊れない
};
```

詳しくは [ハンドルと世代 ID](../../engine/handle.md) を見てください。

<div class="anim" data-type="graph" data-label="持ち主が消えたとき（ポインタとハンドル）">
n stage ステージ 0 0
n enemy 敵 2 0
n bullet 弾 4 0
l stage enemy hit 所有
l bullet enemy dim 生ポインタ
# 敵は、ステージが持っている。弾は生ポインタで借りているだけ
---
n stage ステージ 0 0
n enemy 敵 2 0 gone
n bullet 弾 4 0
l stage enemy gone 所有
l bullet enemy gone 生ポインタ
# 敵が倒されて消えた。弾のポインタは、消えた場所を指したまま
---
n stage ステージ 0 0
n bullet 弾 4 0 hit
l bullet stage hit ハンドルで問い合わせ
# ハンドルなら、弾が「もういない」と確認できる
</div>

## 関数の引数と戻り値で、所有権を表す

| 書き方 | 意味 |
| --- | --- |
| `void Use(const Enemy& e)` | **借りるだけ**。読むだけ。持ち主は変わらない（ほとんどの場合これ） |
| `void Edit(Enemy& e)` | 借りて、書き換える |
| `void Use(Enemy* e)` | 借りる。`nullptr` もありうることを表す（なければ参照にする） |
| `void Take(std::unique_ptr<Enemy> e)` | 所有権をもらう。呼ぶ側は `std::move` で渡す |
| `std::unique_ptr<Enemy> Create()` | 所有権を渡す（新しく作ったものを返す） |
| `Enemy& Find(int id)` | 借りて返す。持ち主（コンテナ）より長く使わない |
| `void Share(std::shared_ptr<Enemy> e)` | 共有の持ち主になる。本当に共有が必要なときだけ |

型を見るだけで「この関数は消す責任を持つのか」が分かるようにするのが、設計の目標です。

## ライフタイムを守るためのルール

| ルール | 理由 |
| --- | --- |
| **ローカル変数の参照・ポインタを関数の外に返さない** | 関数が終わると消える |
| コンテナの要素へのポインタ・参照を長く持たない | `push_back` で引っ越したら無効になる（[イテレータの無効化](../../basics/iterator.md)） |
| `string_view` / `span` は「借りもの」。元の文字列・配列より長生きさせない | 元が消えると、中身が消える |
| ラムダで `[&]` キャプチャしたものは、ラムダを実行するまで生きているものだけにする | あとで呼ぶラムダが消えたローカル変数を触る |
| スレッドに渡す参照は、スレッドが終わるまで生きているものだけ | スレッドが後から動くことがある |
| 持ち主が消える順番をメンバ変数の宣言順で考える | 宣言の逆順に消える。後に宣言したものが先に消える |

```cpp
// ダメな例：ローカル変数への参照を返している
const std::string& MakeName() {
  std::string name = "enemy";
  return name;  // 関数を出ると name は消える
}

// ダメな例：ラムダがすぐに消える変数を借りている
void Setup(EventBus& bus) {
  int count = 0;
  bus.Subscribe([&count] { ++count; });  // Setup が終わると count は消える
}
```

## 設計のパターン

| パターン | 使い方 |
| --- | --- |
| **ツリー型の所有** | 親が子を `unique_ptr` や `vector` で持つ。親が消えれば子も消える。参照は上から下だけ |
| 所有者のコンテナ + ID・ハンドルで参照 | ゲームのエンティティ。`vector` が持ち主、外からは ID で指す |
| オブジェクトプール | プールが全部持ち主。使う側は借りて、返す（[オブジェクトプール](../patterns/object-pool.md)） |
| 共有と弱い参照 | リソース（テクスチャ）を `shared_ptr` で共有し、キャッシュは `weak_ptr` で持つ |
| スコープ付きの借り | 関数の中だけ使う参照。関数が終わったら捨てる |

## よくあるミス

??? failure "「とりあえず shared_ptr」にする"
    持ち主がはっきりしないので `shared_ptr` にすると、**誰がいつ消すのか**が余計に分からなくなります。循環参照（お互いを `shared_ptr` で持つ）でメモリが解放されなくなることもあります。まず「持ち主は誰か」を決めます。

??? failure "親が子を子が親を `unique_ptr` で持つ"
    どちらかが借りる側です。子から親は生の参照 / ポインタ（親は子より長生きするので）にします。

??? failure "コンテナの要素へのポインタをシーンの間ずっと持つ"
    `vector` に要素を足すたびに引っ越しが起きるかもしれません。番号（添字・ID）で持つか、`std::deque` / `std::list`（引っ越さない）、`unique_ptr` の `vector` にします。

??? failure "ポインタが `nullptr` でないことだけで、生きていると思う"
    消えたあとのポインタは `nullptr` にならず、古いアドレスのままです（ダングリング）。生きているかを確認できるのは、ハンドルや `weak_ptr` だけです。

## これだけ覚える

!!! abstract "まとめ"
    - [x] すべてのオブジェクトに持ち主を 1 人決める
    - [x] 借りる側は、持ち主より長生きさせない
    - [x] 引数・戻り値の型で、所有権の移動と借りるだけを区別する
    - [x] 消えるかもしれない相手は、ハンドルか `weak_ptr` で指す
    - [x] 迷ったら `unique_ptr` と `vector`。`shared_ptr` は最後の手段

## 関連ページ

- [所有権（基礎）](../../basics/ownership.md)
- [RAII とスマートポインタ](../patterns/raii.md)
- [ハンドルと世代 ID](../../engine/handle.md)
- [std::unique_ptr](../../stl/utilities/unique_ptr.md) / [std::shared_ptr](../../stl/utilities/shared_ptr.md)
