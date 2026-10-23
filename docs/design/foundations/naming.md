---
title: 命名とコーディング規約
tags:
  - 設計
---

# 命名とコーディング規約

**コーディング規約**は、名前の付け方や書き方のルールをチームでそろえるための決まりです。ルールがそろっていると、他の人のコードも自分のコードのように読めて、「この `count` は変数？関数？定数？」と迷わなくなります。このサイトのサンプルは [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html) に従っているので、その要点をまとめます。

!!! tip "ポイント"
    - 型は `PascalCase`、関数も `PascalCase`、変数は `snake_case`、メンバ変数は `snake_case_`、定数は `kPascalCase`。
    - 名前は**省略しすぎない**（`e` より `enemy`、`cnt` より `count`）。
    - bool は `is_` / `has_` / `can_` で始めると読みやすい。
    - **一番大事なのはチームでそろえること**。どのスタイルでも、混ざっているのが一番読みにくい。

!!! info "このページを読む前に"
    - [design/index.md](../index.md)（このセクション全体の地図と、読む順番）
    - [設計の基本原則](principles.md)（設計の基本原則）

## 名前の付け方（Google Style）

名前の形を種類ごとに決めておく目的は、**名前を見ただけで、それが何の仲間かを読み取れるようにする**ことです。たとえば `Update()` は関数（先頭が大文字）、`hp_` はクラスのメンバ変数（末尾が `_`）、`kMaxEnemies` は定数（先頭が `k`）、と、宣言を見に行かなくても分かります。コードを読む時間は、書く時間よりずっと長いので、この「一目で分かる」効果は積み重なります。

ルールそのものに絶対の正解はありません。Google Style の組み合わせは、型と関数が `PascalCase`、変数が `snake_case`、という形ですが、Unreal Engine や標準ライブラリは別の流儀です。大切なのは、**1 つのプロジェクトの中で混ぜない**ことです。

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

名前を付けるとき、迷ったら「**この名前を、半年後の自分が読んで、中身を見に行かずに分かるか**」を考えます。短さより、分かりやすさを優先します。名前が長くなって困るなら、それは多くの場合、関数や型が大きすぎるサインです。

特に効果が大きいのは、次の 3 つです。**bool は質問の形にする**こと（`is_dead` なら `if (is_dead)` が文として読める）、**関数は動詞で始める**こと（動作をするものだと分かる）、**単位を名前に入れる**こと（`time_seconds`。ミリ秒と取り違える事故が防げる）です。

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

## これだけ覚える

!!! abstract "まとめ"
    - [x] 型・関数は PascalCase、変数は snake_case、メンバは末尾に `_`、定数は kPascalCase
    - [x] 名前は省略しない。bool は is_ / has_ / can_
    - [x] チームでそろえて、clang-format で自動化

## 関連ページ

- [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html)
- [Google C++ Style Guide（日本語訳）](https://ttsuki.github.io/styleguide/cppguide.ja.html)
- [クラス設計](class-design.md)
