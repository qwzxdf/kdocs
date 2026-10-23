---
title: 依存性の注入
tags:
  - 設計
---

# 依存性の注入

**依存性の注入**（Dependency Injection、DI）は、**クラスが使う相手（依存先）を、クラスの中で作ったり探したりせず、外から渡してもらう**設計です。難しそうな名前ですが、やっていることは「コンストラクタや引数で渡す」だけです。渡す相手をインターフェース（抽象クラス）にしておくと、本物の代わりにテスト用のものや別の実装に差し替えられるようになります。

!!! tip "ポイント"
    - クラスの中で `new` したり `Instance()` で探したりせず、**コンストラクタで受け取る**。
    - 受け取る型を抽象クラス（インターフェース）にすると、差し替えられる。
    - 一番うれしいのは**テストのしやすさ**と、**プラットフォームごとの差し替え**（PC / 家庭用機の入力・保存先）。
    - 何でもインターフェースにする必要はない。差し替えたいものだけ。

!!! info "このページを読む前に"
    - [デザインパターン早見表](index.md)（このセクション全体の地図と、読む順番）
    - [設計の基本原則](../foundations/principles.md)（設計の基本原則）

## 悪い例：中で作る・探す

```cpp
class SaveSystem {
 public:
  void Save(const SaveData& data) {
    FileStorage storage;                 // 中で作る → 保存先を変えられない
    storage.Write("save.dat", Serialize(data));
    Audio::Instance().Play("save.wav");  // 中で探す → 依存が見えない
  }
};
```

- テストしたいだけなのに、本物のファイルに書き込まれる
- Steam のクラウドセーブや家庭用機の保存先に変えるには、SaveSystem を書き直す必要がある

## 良い例：外から渡す

```cpp
#include <map>
#include <print>
#include <string>

// 保存先のインターフェース
class IStorage {
 public:
  virtual ~IStorage() = default;
  virtual void Write(const std::string& key, const std::string& data) = 0;
  virtual std::string Read(const std::string& key) = 0;
};

// テスト用：メモリに保存するだけ
class MemoryStorage : public IStorage {
 public:
  void Write(const std::string& key, const std::string& data) override { files_[key] = data; }
  std::string Read(const std::string& key) override { return files_[key]; }

 private:
  std::map<std::string, std::string> files_;
};

class SaveSystem {
 public:
  explicit SaveSystem(IStorage& storage) : storage_(storage) {}  // 外から受け取る

  void Save(int level) { storage_.Write("save", std::to_string(level)); }
  int Load() { return std::stoi(storage_.Read("save")); }

 private:
  IStorage& storage_;
};

int main() {
  MemoryStorage storage;  // 本番では FileStorage や CloudStorage を渡す
  SaveSystem save(storage);
  save.Save(12);
  std::println("ロード: Lv.{}", save.Load());
}
```

```text title="実行結果"
ロード: Lv.12
```

<div class="anim" data-type="graph" data-label="依存性の注入：中で作る → 外から渡す">
n player プレイヤー 0 1
n audio 音の実装 2 1 gone
l player audio gone 中で作る
# 中で作ると、相手を差し替えられない（実装が固定）
---
n main 組み立て役 0 1 new
n player プレイヤー 1 0 new
n audio 音の実装 2 1
l main player new 渡す
l main audio new 作る
l player audio hit 使う
# 組み立て役が、実装を作ってプレイヤーに渡す。プレイヤーは作らない
---
n main 組み立て役 0 1
n player プレイヤー 1 0
n audio 音の実装 2 1
n fake 偽物 2 2 new
l main player
l main fake new 作る
l player fake hit 使う
# テストでは、渡すものを偽物に替えるだけ
</div>

## 渡し方の種類

| 渡し方 | 書き方 | 向いているとき |
| --- | --- | --- |
| コンストラクタで渡す | `explicit SaveSystem(IStorage& storage)` | ずっと使う相手（一番よく使う） |
| 関数の引数で渡す | `void Update(float dt, Input& input)` | その処理の間だけ使う相手 |
| テンプレートで渡す | `template <class Storage> class SaveSystem` | 実行中に差し替えない。仮想関数のコストも避けたい |
| `std::function` で渡す | `SaveSystem(std::function<void(std::string)> write)` | 関数 1 つだけ差し替えたい |

## 誰が作って渡すのか

「みんな外から受け取る」なら、誰かが最初に全部作って渡す必要があります。それは `main`（またはゲームの一番上のクラス）の役目です。

```cpp
// main から呼ばれる「組み立て係」
void StartGame() {
  FileStorage storage("saves/");
  ConsoleAudio audio;
  SaveSystem save(storage);
  Game game(save, audio);  // 必要なものを組み立てて渡す
  game.Run();
}
```

この「組み立てる場所」を 1 か所にまとめると、何が何を使っているかが一目で分かります。

## ゲームでの例

| 差し替えたいもの | 本番 | テスト・別環境 |
| --- | --- | --- |
| 保存先 | ファイル | メモリ、クラウド |
| 入力 | キーボード・パッド | 記録した入力の再生（リプレイ・自動テスト） |
| 乱数 | 種がランダム | 種が固定（毎回同じ結果） |
| 時間 | 本物の時計 | 自由に進められる時計（タイマーのテスト） |
| サウンド | 本物の再生 | 何もしない（音なしモード） |

## よくある失敗

??? failure "全部のクラスにインターフェースを作る"
    差し替える予定の無いものまで抽象クラスにすると、ファイルとコードが倍になるだけです。差し替えたいものだけにします（[YAGNI](../foundations/principles.md#5-yagni--kiss)）。

??? failure "受け取った参照の相手が先に消える"
    `IStorage&` で受け取った相手が、SaveSystem より先に消えると壊れます。作る順番と消える順番（逆順）に注意し、渡す側のほうが長生きするようにします。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 使う相手は中で作らず、外から渡す
    - [x] 差し替えたいものだけインターフェースにする
    - [x] 組み立ては main など 1 か所で

## 関連ページ

- [シングルトンとグローバル](singleton.md)
- [設計の基本原則](../foundations/principles.md)
