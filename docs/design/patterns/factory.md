---
title: ファクトリとデータ駆動
tags:
  - 設計
---

# ファクトリとデータ駆動

**ファクトリ**は、**オブジェクトを作る処理を 1 か所にまとめる**設計です。「`"slime"` という文字列からスライムを作る」「ステージファイルに書かれた敵を全部作る」のように、作る種類が実行時に決まる場面で使います。そしてファクトリと組み合わせて使うのが**データ駆動**（データドリブン）で、敵の HP や速さ、配置などをプログラムではなく**データファイル**に書いておき、プログラムはそれを読んで動くだけにする考え方です。プランナーやデザイナーがプログラムを書き換えずにゲームを調整できるようになります。

!!! tip "ポイント"
    - 作り方が複雑・種類が実行時に決まる → **ファクトリ関数**にまとめる。
    - 文字列から作るなら「名前 → 作る関数」の表（`std::unordered_map<std::string, std::function<...>>`）。
    - 数値（HP、速さ、出現位置）は**データファイルに出す**。コードに直接書かない。
    - 失敗しうる生成（データが壊れている）は `std::expected` / `std::optional` で返す。

!!! info "このページを読む前に"
    - [デザインパターン早見表](index.md)（このセクション全体の地図と、読む順番）
    - [設計の基本原則](../foundations/principles.md)（設計の基本原則）

## 悪い例：作る処理があちこちにある

```cpp
// stage1.cpp
auto e = std::make_unique<Enemy>();
e->hp = 30; e->speed = 1.5f; e->texture = LoadTexture("slime.png");
// stage2.cpp にも同じようなコード。HP を変えるには全部直す
```

## 良い例 1：ファクトリ関数

```cpp
#include <memory>
#include <optional>
#include <print>
#include <string>

struct Enemy {
  std::string name;
  int hp;
  float speed;
};

// 作り方はここにまとめる
std::optional<Enemy> CreateEnemy(const std::string& type) {
  if (type == "slime") {
    return Enemy{"スライム", 30, 1.5f};
  }
  if (type == "goblin") {
    return Enemy{"ゴブリン", 60, 2.0f};
  }
  return std::nullopt;  // 知らない種類
}

int main() {
  for (std::string type : {"slime", "dragon"}) {
    if (auto e = CreateEnemy(type)) {
      std::println("{} HP {}", e->name, e->hp);
    } else {
      std::println("{} は作れない", type);
    }
  }
}
```

```text title="実行結果"
スライム HP 30
dragon は作れない
```

## 良い例 2：登録式のファクトリ

if の連続をやめて、「名前 → 作る関数」の表にすると、種類を増やすときに表へ登録するだけで済みます。

```cpp
#include <functional>
#include <memory>
#include <print>
#include <string>
#include <unordered_map>
#include <utility>

class GameObject {
 public:
  virtual ~GameObject() = default;
  virtual void Describe() const = 0;
};

class Chest : public GameObject {
 public:
  void Describe() const override { std::println("宝箱"); }
};

class Door : public GameObject {
 public:
  void Describe() const override { std::println("ドア"); }
};

class ObjectFactory {
 public:
  using Creator = std::function<std::unique_ptr<GameObject>()>;

  void Register(const std::string& name, Creator creator) { creators_[name] = std::move(creator); }

  std::unique_ptr<GameObject> Create(const std::string& name) const {
    auto it = creators_.find(name);
    return it != creators_.end() ? it->second() : nullptr;
  }

 private:
  std::unordered_map<std::string, Creator> creators_;
};

int main() {
  ObjectFactory factory;
  factory.Register("chest", [] { return std::make_unique<Chest>(); });
  factory.Register("door", [] { return std::make_unique<Door>(); });

  // ステージファイルから読んだ名前だとする
  for (const char* name : {"door", "chest", "unknown"}) {
    if (auto obj = factory.Create(name)) {
      obj->Describe();
    } else {
      std::println("{} は未登録", name);
    }
  }
}
```

```text title="実行結果"
ドア
宝箱
unknown は未登録
```

## データ駆動

数値や組み合わせをデータファイルに出します。

```json
// enemies.json
{
  "slime":  { "name": "スライム", "hp": 30, "speed": 1.5, "texture": "slime.png" },
  "goblin": { "name": "ゴブリン", "hp": 60, "speed": 2.0, "texture": "goblin.png" }
}
```

```cpp
// 読み込んで「種類名 → パラメータ」の表を作っておき、ファクトリはそれを使って作る
struct EnemyParams {
  std::string name;
  int hp;
  float speed;
  std::string texture;
};
std::unordered_map<std::string, EnemyParams> LoadEnemyTable(const std::string& path);
```

| データにするもの | 例 |
| --- | --- |
| パラメータ | HP、攻撃力、速さ、価格、ドロップ率 |
| 配置 | 敵・アイテム・ギミックの位置（ステージエディタで作る） |
| 組み合わせ | 敵が持つコンポーネントの一覧（プレハブ） |
| テキスト | 会話、アイテムの説明（翻訳もしやすい） |
| 進行 | クエストの条件、ウェーブの出現順 |

| データ駆動の利点 | |
| --- | --- |
| 調整にビルドが要らない | ファイルを書き換えて再読み込みするだけ（[ホットリロード](../../engine/resource.md#ホットリロード)） |
| プログラマー以外が触れる | プランナーがバランスを調整できる |
| コードが短くなる | 種類ごとのクラスを作らずに済む |

## プロトタイプ（コピーして作る）

「基本の敵」を 1 つ作っておき、それをコピーして少しだけ変える方法もあります（プロトタイプパターン）。Unity のプレハブがこれです。

```cpp
Enemy base = table.at("slime");
Enemy elite = base;  // コピーして
elite.hp *= 3;       // 少しだけ変える
```

## ゲームでの例

| 場面 | 方法 |
| --- | --- |
| ステージの読み込み | ファイルの種類名 → 登録式ファクトリで生成 |
| 敵のバランス調整 | パラメータを JSON / CSV に |
| エディタで置いたオブジェクト | 種類名 + 位置を保存し、読み込み時にファクトリで作る |
| ガチャ・ドロップ | 確率表をデータに |

## よくある失敗

??? failure "知らない種類名で落ちる"
    データのタイプミス（`"slmie"`）で nullptr が返り、それを使って落ちます。必ず失敗を確かめて、ログを出します。

??? failure "データとコードで同じ値を二重に持つ"
    データファイルにも HP を書き、コードにもデフォルトの HP を書くと、どちらが正しいか分からなくなります。

??? failure "何でもデータにする"
    動きの複雑なルールまで無理にデータで表そうとすると、データが独自のプログラミング言語のようになって、かえって扱いにくくなります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 作る処理は 1 か所に
    - [x] 文字列から作るなら「名前 → 作る関数」の表
    - [x] 数値はデータファイルへ
    - [x] 失敗（知らない種類）を必ず確かめる

## 関連ページ

- [ストラテジー](strategy.md)
- [シリアライズ](../../engine/serialization/index.md)
- [Game Programming Patterns: Prototype](https://gameprogrammingpatterns.com/prototype.html)
