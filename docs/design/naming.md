---
title: 命名とコーディング規約
tags:
  - 設計
---

# 命名とコーディング規約

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
</div>

**コーディング規約**は、名前の付け方や書き方のルールをチームでそろえるための決まりです。ルールがそろっていると、他の人のコードも自分のコードのように読めて、「この `count` は変数？関数？定数？」と迷わなくなります。このサイトのサンプルは [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html) に従っているので、その要点をまとめます。

!!! tip "結論"
    - 型は `PascalCase`、関数も `PascalCase`、変数は `snake_case`、メンバ変数は `snake_case_`、定数は `kPascalCase`。
    - 名前は**省略しすぎない**（`e` より `enemy`、`cnt` より `count`）。
    - bool は `is_` / `has_` / `can_` で始めると読みやすい。
    - **一番大事なのはチームでそろえること**。どのスタイルでも、混ざっているのが一番読みにくい。

## 名前の付け方（Google Style）

| 種類 | 書き方 | 例 |
| --- | --- | --- |
| 型（クラス・構造体・enum・型の別名） | `PascalCase` | `Enemy`, `TextureCache`, `EnemyId` |
| 関数 | `PascalCase` | `Update()`, `LoadTexture()` |
| ゲッター・セッター | `snake_case` | `hp()`, `set_hp()` |
| 変数（ローカル・引数） | `snake_case` | `delta_time`, `enemy_count` |
| クラスのメンバ変数 | `snake_case_`（最後に `_`） | `hp_`, `texture_` |
| 構造体のメンバ変数 | `snake_case` | `x`, `y`, `max_hp` |
| 定数（`constexpr` / `const` で値が固定） | `kPascalCase` | `kMaxEnemies`, `kGravity` |
| enum の値 | `kPascalCase` | `EnemyType::kSlime` |
| 名前空間 | `snake_case` | `game`, `render` |
| マクロ | `UPPER_SNAKE_CASE` | `GAME_ASSERT`（なるべく使わない） |
| ファイル名 | `snake_case.cpp` / `.h` | `texture_cache.cpp` |

```cpp
namespace game {

constexpr int kMaxEnemies = 64;

enum class EnemyType { kSlime, kGoblin };

class EnemySpawner {
 public:
  explicit EnemySpawner(int wave_count) : wave_count_(wave_count) {}

  void Update(float delta_time);
  int wave_count() const { return wave_count_; }

 private:
  bool CanSpawn() const;

  int wave_count_;
  float spawn_timer_ = 0.0f;
};

}  // namespace game
```

## 良い名前の付け方

| ポイント | 悪い例 | 良い例 |
| --- | --- | --- |
| 何のためのものか分かる | `data`, `tmp`, `flag` | `save_data`, `previous_position`, `is_grounded` |
| 省略しない | `e`, `cnt`, `pos2` | `enemy`, `count`, `target_position` |
| bool は質問の形 | `dead`, `jump` | `is_dead`, `can_jump`, `has_key` |
| 関数は動詞で始める | `Score()` | `AddScore()`, `CalculateScore()` |
| 単位を付ける | `time`, `angle` | `time_seconds`, `angle_degrees` |
| 否定の名前を避ける | `is_not_visible` | `is_visible`（`!is_visible` で書く） |

短い名前は、スコープが短いときだけ OK です（`for (int i = 0; ...)`、ラムダの `[](const auto& e)`）。

## 書き方のルール（Google Style の要点）

| ルール | 中身 |
| --- | --- |
| インデント | スペース 2 つ |
| 1 行の長さ | 80 文字まで |
| 波かっこ | 関数・クラス・if でも同じ行に `{` |
| `if` が 1 行でも | 波かっこを付ける（付け忘れのバグを防ぐ） |
| クラスの中の順番 | `public` → `protected` → `private` |
| ポインタの `*` | 型の側に付ける（`Enemy* enemy`） |
| `using namespace` | ヘッダには書かない。`.cpp` でも `std` には使わない |
| 引数 1 つのコンストラクタ | `explicit` を付ける |
| `auto` | 型が長くて読み取れるとき（イテレータなど）に使う。何でも auto にしない |

```cpp
// 良い書き方の例
if (enemy.is_dead()) {
  score += enemy.score();
}

for (const auto& [name, texture] : textures) {
  Draw(texture);
}
```

## コメント

| 書くもの | 書かないもの |
| --- | --- |
| **なぜ**そうしているか（理由、注意点） | コードを読めば分かること（`i++; // i を増やす`） |
| 関数の使い方・前提（引数の範囲、戻り値の意味） | 古くなった説明（コードと合わなくなったコメントは害になる） |
| TODO（`// TODO(名前): 〇〇を直す`） | コメントアウトした古いコード（Git に残っている） |

!!! note "このサイトのサンプルについて"
    このサイトのサンプルは解説のためにコメントを多めに書いていますが、実際のコードでは「なぜ」が必要なところだけで十分です。プロジェクトによっては「コメントを書かない（名前で分かるようにする）」というルールのこともあります。

## 自動でそろえる道具

| 道具 | できること |
| --- | --- |
| **clang-format** | インデントや改行を自動でそろえる。`.clang-format` に `BasedOnStyle: Google` と書くだけで Google Style になる |
| **clang-tidy** | 名前の付け方の違反や、よくあるバグの書き方を見つける |
| Visual Studio の「ドキュメントのフォーマット」 | clang-format を使って整形（Ctrl+K, Ctrl+D） |

手でそろえるより、保存したときに自動で整形されるようにしておくと、チームで揉めずに済みます。

## よくある失敗

??? failure "人によってスタイルが違う"
    同じプロジェクトで `enemyCount` と `enemy_count` と `EnemyCount` が混ざっていると、毎回どれだったか確かめる必要があります。最初に規約を決め、clang-format で自動化します。

??? failure "名前を短くしすぎる"
    書く時間はほんの少し増えますが、読む時間（何倍もある）が大きく減ります。

## 理解度チェック

!!! question "Q1. Google Style で書くと？ ①敵の最大数（定数） ②プレイヤーが地面にいるか（メンバ変数） ③テクスチャを読み込む関数"
    <div class="spoiler" markdown>

    **答え:** ① `kMaxEnemies` ② `is_grounded_` ③ `LoadTexture()`。

    </div>

## これだけ覚える

!!! abstract "まとめ"
    - [x] 型・関数は PascalCase、変数は snake_case、メンバは末尾に `_`、定数は kPascalCase
    - [x] 名前は省略しない。bool は is_ / has_ / can_
    - [x] チームでそろえて、clang-format で自動化

## 関連ページ

- [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html)
- [Google C++ Style Guide（日本語訳）](https://ttsuki.github.io/styleguide/cppguide.ja.html)
- [クラス設計](class-design.md)
