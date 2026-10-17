---
title: テスト容易性の設計
tags:
  - 設計
---

# テスト容易性の設計

**テスト**は、プログラムが期待どおりに動くことを、**コードで自動的に確認する**ことです。ゲームは「実際に遊んで確かめる」ことが多いですが、ダメージ計算、アイテムの合成、セーブデータの読み込みのような**ルールの部分**は、自動テストにすると、あとで直したときに壊していないかをすぐに確かめられます。ただし、**テストしやすいコードは、設計の時点で作る必要があります**。描画や音やファイルに直接つながったコードは、テストしにくいからです。テスト容易性の設計は、実は**疎結合な設計**（[レイヤー](layers.md)、[依存性の注入](../patterns/dependency-injection.md)）と同じ話です。

!!! tip "ポイント"
    - <strong>ルール（計算・判定）と、外とのやり取り（描画・音・ファイル）を分ける。</strong> ルールは、**入力から出力が決まる関数**にする。
    - 外とのやり取りは、**インターフェース**（`IAudio` など）の裏に置き、テストでは<strong>偽物（モック・スタブ）</strong>に差し替える。
    - 必要なものは、**引数やコンストラクタで渡す**（依存性の注入）。中で `new` したり、シングルトンを呼んだりしない。
    - 時間・乱数・ファイルなど**毎回変わるもの**は、外から渡せるようにする。
    - テストは **小さく、速く、独立して**。1 つのテストは 1 つのことだけ確かめる。

## テストしやすいコードと、しにくいコード

### しにくい例

```cpp
class Player {
 public:
  void Attack(Enemy& enemy) {
    int damage = attack_ - enemy.defense();
    if (std::rand() % 100 < 10) {          // 乱数に直接依存（毎回結果が変わる）
      damage *= 2;
    }
    enemy.TakeDamage(damage);
    Audio::Instance().Play("hit.wav");     // シングルトンの音（テストで音が鳴る）
    Renderer::Instance().ShowDamage(damage);  // 描画に直接依存
  }
};
```

| 問題 | 説明 |
| --- | --- |
| **乱数**で結果が変わる | テストが、ときどき失敗する（不安定なテスト） |
| **音と描画**に直接つながっている | テストのたびに、音を鳴らす・ウィンドウを開く必要がある |
| 結果を**確かめにくい** | ダメージの計算が、効果の呼び出しに混ざっている |

### しやすい例：ルールを取り出し、外を渡す

```cpp
// ① ルール：入力から出力が決まる関数（乱数も、結果も、引数）
struct DamageResult {
  int damage;
  bool critical;
};

DamageResult CalcDamage(int attack, int defense, bool critical_roll) {
  int damage = std::max(0, attack - defense);
  if (critical_roll) {
    damage *= 2;
  }
  return {damage, critical_roll};
}

// ② 外とのやり取りは、インターフェースで渡す
class Player {
 public:
  Player(IRandom& random, IAudio& audio, IEffects& effects)
      : random_(random), audio_(audio), effects_(effects) {}

  void Attack(Enemy& enemy) {
    DamageResult result = CalcDamage(attack_, enemy.defense(), random_.Chance(0.1f));
    enemy.TakeDamage(result.damage);
    audio_.Play("hit.wav");
    effects_.ShowDamage(result.damage);
  }

 private:
  IRandom& random_;
  IAudio& audio_;
  IEffects& effects_;
  int attack_ = 10;
};
```

```cpp
// テスト：ルールの関数は、乱数なしで、そのまま確かめられる
TEST(DamageTest, CriticalDoublesDamage) {
  EXPECT_EQ(CalcDamage(10, 3, false).damage, 7);
  EXPECT_EQ(CalcDamage(10, 3, true).damage, 14);
  EXPECT_EQ(CalcDamage(2, 5, false).damage, 0);   // 負にならない
}
```

<svg class="fig flow" viewBox="0 0 444 280" role="img" aria-label="本番とテストで、つなぐ相手を差し替える"><defs><marker id="fl57391" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">本番とテストで、つなぐ相手を差し替える</text><line x1="118.7" y1="125.0" x2="191.0" y2="86.1" stroke="currentColor" stroke-width="2" marker-end="url(#fl57391)"/><line x1="127.0" y1="148.0" x2="189.0" y2="148.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl57391)"/><line x1="118.7" y1="171.0" x2="189.3" y2="209.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl57391)"/><line x1="273.0" y1="64.0" x2="337.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl57391)"/><line x1="272.0" y1="87.0" x2="338.0" y2="125.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl57391)"/><line x1="275.0" y1="148.0" x2="337.0" y2="148.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl57391)"/><line x1="272.0" y1="209.0" x2="338.0" y2="171.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl57391)"/><rect x="28.0" y="128.0" width="96" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="76.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">プレイヤー</text><circle cx="30.0" cy="130.0" r="10" fill="#4c8bf5"/><text x="30.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="194.0" y="44.0" width="76" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="232.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">IAudio</text><circle cx="196.0" cy="46.0" r="10" fill="#4c8bf5"/><text x="196.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="192.0" y="128.0" width="80" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="232.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">IRandom</text><circle cx="194.0" cy="130.0" r="10" fill="#4c8bf5"/><text x="194.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="188.0" y="212.0" width="88" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="232.0" y="232.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">IEffects</text><circle cx="190.0" cy="214.0" r="10" fill="#4c8bf5"/><text x="190.0" y="214.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="340.0" y="44.0" width="76" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="378.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">本物</text><circle cx="342.0" cy="46.0" r="10" fill="#4c8bf5"/><text x="342.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="340.0" y="128.0" width="76" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="378.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">偽物</text><circle cx="342.0" cy="130.0" r="10" fill="#2ea043"/><text x="342.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text></svg>

## テスト用の偽物の種類

| 名前 | 何をするか | 例 |
| --- | --- | --- |
| **スタブ**（Stub） | 決まった値を返す | `FixedRandom`（いつも `Chance` が `true`） |
| **モック**（Mock） | 呼ばれたことを**記録**して、あとで確認する | 「`Play("hit.wav")` が 1 回呼ばれたか」 |
| **フェイク**（Fake） | 簡易版の本物 | メモリ上だけで動く `FakeFileSystem` |
| **Null オブジェクト** | 何もしない | `NullAudio`（音を出さない） |

```cpp
// 呼ばれた回数を記録するモック
class MockAudio : public IAudio {
 public:
  void Play(std::string_view name) override { played.emplace_back(name); }
  void Stop(std::string_view) override {}
  void SetVolume(float) override {}

  std::vector<std::string> played;  // 呼ばれた名前の記録
};

TEST(PlayerTest, AttackPlaysHitSound) {
  FixedRandom random(false);
  MockAudio audio;
  NullEffects effects;
  Player player(random, audio, effects);
  Enemy enemy;

  player.Attack(enemy);

  ASSERT_EQ(audio.played.size(), 1u);
  EXPECT_EQ(audio.played[0], "hit.wav");
}
```

## テストしやすくする設計のルール

| ルール | 理由 |
| --- | --- |
| **計算・判定は、純粋な関数にする**（引数だけで結果が決まる） | 準備なしでテストできる |
| **時間は、`dt` や時計を引数・インターフェースで渡す** | `std::chrono::now()` を直接呼ぶと、結果が毎回変わる |
| **乱数は、乱数生成器を渡す**（シード固定） | 結果が毎回同じになる（再現できる） |
| **ファイル・ネットワークは、インターフェースの裏に置く** | テストが、環境（ファイルの有無）に左右されない |
| **グローバル変数・シングルトンを使わない** | テスト間で状態が残り、順番で結果が変わる |
| **`private` を、テストのために `public` にしない** | 公開された振る舞いをテストする。中身をテストしたくなったら、別のクラスに分ける |
| **1 つのクラスが持つ依存を、3〜4 個までにする** | 偽物が多すぎるとテストを書くのが大変。依存が多いのは、責任が多すぎるサイン |

## テストの書き方

### 何をテストするか

| 優先度 | 対象 |
| --- | --- |
| **高い** | ルール（ダメージ計算、経験値、アイテム合成、スコア）、データの変換（セーブ・ロード）、状態遷移（[ステートマシン](../patterns/state-machine.md)） |
| 中 | ゲームのロジックの流れ（「敵が倒れたら、アイテムが出る」） |
| 低い | 描画、音、物理の見た目（実際に遊んで確認する） |

### テストの形（AAA）

| 段階 | 内容 |
| --- | --- |
| **Arrange**（準備） | テストする対象と、必要な偽物を用意する |
| **Act**（実行） | 確かめたい操作を 1 つ実行する |
| **Assert**（確認） | 結果が期待どおりか確かめる |

```cpp
TEST(InventoryTest, AddItemIncreasesCount) {
  Inventory inventory;                    // Arrange
  inventory.Add(Item{"potion"});          // Act
  EXPECT_EQ(inventory.CountOf("potion"), 1);   // Assert
}
```

## テストの道具

| ライブラリ | 特徴 |
| --- | --- |
| **GoogleTest** | 一番有名。`TEST`、`EXPECT_EQ`、モック機能（GoogleMock）あり。vcpkg: `gtest` |
| **Catch2** | ヘッダが少なく、書きやすい。`TEST_CASE`、`REQUIRE`。vcpkg: `catch2` |
| **doctest** | 軽い。ヘッダ 1 つ。コンパイルが速い |
| <strong>Visual Studio の「ネイティブ単体テスト」</strong> | Visual Studio だけで、プロジェクトのテスト エクスプローラーから実行できる |

## ゲームでの使いどころ

| 場面 | テストの方法 |
| --- | --- |
| ダメージ・成長のバランス計算 | 純粋な関数のテスト。計算式の変更で壊れていないかをすぐ確認 |
| セーブとロード | 「保存して読むと、同じになる」テスト。古いバージョンのデータを読むテストも |
| ステートマシン | 「この状態でこの入力なら、次はこの状態」の表をテストにする |
| アイテム・レシピのデータ | データファイル（JSON）を読んで、整合性（存在しない ID がない）を確認 |
| AI の判断 | 偽の世界（敵の位置）を作って、「この状況では逃げる」を確かめる |

## よくあるミス

??? failure "実装の中身をテストして、変更のたびに壊れる"
    `private` の関数や、内部の変数をテストすると、実装を変えるだけで、テストが壊れます。<strong>外から見える振る舞い（入力と出力）</strong>をテストします。

??? failure "1 つのテストで、たくさんのことを確かめる"
    失敗したときに、どこが悪いのか分かりません。1 つのテストは 1 つのことだけ確かめます。

??? failure "テスト同士が影響しあう"
    グローバル変数や、ファイルの残りで、テストの順番によって結果が変わります。テストごとに、新しいオブジェクトを作ります。

??? failure "テストのためだけに、本体を汚す"
    `#ifdef TEST` だらけになるのは、設計が間違っているサインです。依存を外から渡せるようにして、本体は変えずにテストします。

??? failure "全部に偽物を作って、疲れる"
    偽物が必要なのは、**外とのやり取り**（音、描画、ファイル、時間、乱数）だけです。普通のクラスは、本物をそのまま使います。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ルール（計算・判定）と、外とのやり取り（音・描画・ファイル）を分ける
    - [x] 外とのやり取りはインターフェースにして、引数・コンストラクタで渡す
    - [x] 時間・乱数は、外から渡す（結果を毎回同じにする）
    - [x] テストは小さく、速く、独立して、AAA の形で
    - [x] グローバル・シングルトンは、テストを難しくする

## 関連ページ

- [依存性の注入](../patterns/dependency-injection.md)
- [インターフェース設計](interface-design.md)
- [モジュール境界とレイヤー設計](layers.md)
- [ステートマシン](../patterns/state-machine.md)
- [シングルトンとグローバル](../patterns/singleton.md)
