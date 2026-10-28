---
title: リソース管理
tags:
  - ゲームエンジン
---

# リソース管理

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
</div>

**リソース**は、テクスチャ、サウンド、フォント、モデルのような**ファイルから読み込む大きなデータ**のことです。同じ画像を敵 100 体がそれぞれ読み込むと、メモリも時間も 100 倍かかってしまいます。**リソースマネージャ**（キャッシュ）を 1 つ作り、「同じファイルは 1 回だけ読み込んで、みんなで使い回す」ようにするのが基本です。

!!! tip "ポイント"
    - <strong>リソースはマネージャが持ち主になり、他は参照・ポインタ・ハンドルで借りる。</strong>
    - 名前（パス）をキーにした `std::unordered_map` でキャッシュする。
    - 解放のタイミングは「シーンの切り替え時にまとめて」が分かりやすい。
    - 使われなくなったら自動で消したいなら `std::shared_ptr` / `std::weak_ptr` で数える方法もある。
    - 読み込みは重いので、ロード画面や別スレッドで行う。

!!! info "このページを読む前に"
    [`std::unordered_map`](../stl/containers/unordered_map.md)、[所有権](../basics/ownership.md)、[ハンドル](handle.md) を使います。

## 基本

```cpp
#include <memory>
#include <print>
#include <string>
#include <unordered_map>

struct Texture {
  explicit Texture(const std::string& path) : path(path) {
    std::println("読み込み: {}", path);  // 本当はファイルを読んで GPU に送る
  }
  ~Texture() { std::println("解放: {}", path); }
  std::string path;
};

class TextureManager {
 public:
  // 同じパスなら 2 回目以降は読み込まずに返す
  const Texture& Load(const std::string& path) {
    auto [it, inserted] = textures_.try_emplace(path, nullptr);
    if (inserted) {
      it->second = std::make_unique<Texture>(path);
    }
    return *it->second;
  }

  void Clear() { textures_.clear(); }

 private:
  std::unordered_map<std::string, std::unique_ptr<Texture>> textures_;
};

int main() {
  TextureManager textures;
  const Texture& a = textures.Load("slime.png");
  const Texture& b = textures.Load("slime.png");  // 読み込まない
  textures.Load("bat.png");
  std::println("同じもの？ {}", &a == &b);
  textures.Clear();  // シーンの切り替えでまとめて解放
}
```

```text title="実行結果"
読み込み: slime.png
読み込み: bat.png
同じもの？ true
解放: bat.png
解放: slime.png
```

（`unordered_map` なので、解放の順番は実装によって変わることがあります。）

<div class="anim" data-type="graph" data-label="リソースの共有：使っている間だけ残す">
n a シーンA 0 0
n b シーンB 0 2
n tex テクスチャ 2 1 gone
# 最初は、まだ読み込まれていない
---
n a シーンA 0 0 hit
n b シーンB 0 2
n tex テクスチャ 2 1 new
l a tex new 使う
# シーン A が使うと、1 回だけ読み込まれる
---
n a シーンA 0 0 hit
n b シーンB 0 2 hit
n tex テクスチャ 2 1
l a tex
l b tex new 使う
# シーン B も使う。読み直さず、同じものを共有する
---
n a シーンA 0 0 gone
n b シーンB 0 2
n tex テクスチャ 2 1
l a tex gone 手放す
l b tex
# A が終わっても、B が使っているので残る
---
n a シーンA 0 0 dim
n b シーンB 0 2 gone
n tex テクスチャ 2 1 gone
l b tex gone 手放す
# 全員が手放したとき、はじめて解放される
</div>

## 詳しく

### 借り方の選び方

| 借り方 | 特徴 | 向いているとき |
| --- | --- | --- |
| `const Texture&` / `const Texture*` | 速い。マネージャより先に消えないことが前提 | シーン単位でまとめて解放する設計 |
| ハンドル（ID） | 解放後に使っても安全に検出できる。セーブもできる | 大きなエンジン、エディタ |
| `std::shared_ptr<Texture>` | 使っている人がいなくなったら自動で解放 | 寿命がバラバラなリソース |

### 参照カウントで自動解放する

```cpp
#include <memory>
#include <print>
#include <string>
#include <unordered_map>
#include <utility>

struct Sound {
  explicit Sound(std::string p) : path(std::move(p)) {}
  ~Sound() { std::println("解放: {}", path); }
  std::string path;
};

class SoundCache {
 public:
  std::shared_ptr<Sound> Load(const std::string& path) {
    if (auto alive = cache_[path].lock()) {  // まだ誰かが使っていれば使い回す
      return alive;
    }
    auto sound = std::make_shared<Sound>(path);
    cache_[path] = sound;  // キャッシュは weak_ptr で持つ（持ち主にならない）
    return sound;
  }

 private:
  std::unordered_map<std::string, std::weak_ptr<Sound>> cache_;
};

int main() {
  SoundCache cache;
  {
    auto a = cache.Load("jump.wav");
    auto b = cache.Load("jump.wav");
    std::println("同じもの？ {} / 使用中 {}", a == b, a.use_count());
  }  // 誰も使わなくなったので自動で解放される
  std::println("ブロックの外");
}
```

```text title="実行結果"
同じもの？ true / 使用中 2
解放: jump.wav
ブロックの外
```

### 読み込みのタイミング

| タイミング | 特徴 |
| --- | --- |
| 起動時に全部 | 簡単。起動が遅くなり、メモリも食う |
| シーンの開始時（ロード画面） | 一番よく使う。シーンで使うものだけ読む |
| 必要になった瞬間 | メモリは少ないが、読み込みでカクつく |
| 別スレッドで先読み | カクつかないが、スレッドの扱いが必要 |

### ホットリロード

開発中は、画像やパラメータのファイルを書き換えたら、ゲームを再起動せずに反映されると便利です。`std::filesystem::last_write_time` で更新日時を見て、変わっていたら読み込み直します。ハンドルで借りる設計にしておくと、中身だけ差し替えても他のコードは変えずに済みます。

## ゲームでの例

| リソース | マネージャ |
| --- | --- |
| 画像 | `TextureManager`（パス → テクスチャ） |
| 音 | `SoundManager` |
| フォント | `FontManager`（フォント名 + サイズ → フォント） |
| データ | `MasterData`（アイテム表などを起動時に読む） |

## よくあるミス

??? failure "オブジェクトごとに読み込む"
    敵のコンストラクタで毎回 `LoadTexture("slime.png")` すると、敵の数だけ読み込みが走ります。

??? failure "マネージャを先に消して、借りていた参照を使う"
    シーンが持っている参照がマネージャの `Clear()` の後に使われるとクラッシュします。解放の順番（シーンを消してからリソースを消す）を決めておきます。

??? failure "パスの書き方の違いで別物になる"
    `"img/a.png"` と `"img\\a.png"` と `"./img/a.png"` は、文字列としては別なので 2 回読み込まれます。`std::filesystem::path` で正規化してからキーにします。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 同じファイルは 1 回だけ読み込んで使い回す
    - [x] 持ち主はマネージャ、他は借りる
    - [x] 解放はシーンの切り替えでまとめて、が分かりやすい

## 関連ページ

- [シーン管理](scene.md)
- [ハンドルと世代 ID](handle.md)
- [std::shared_ptr / weak_ptr](../stl/utilities/shared_ptr.md)
