---
title: デコレータ
tags:
  - 設計
---

# デコレータ

**デコレータ**（Decorator、飾り）は、**既存のオブジェクトを「包んで」、機能を足していく**パターンです。元のオブジェクトと**同じインターフェース**を持つ包み（ラッパー）を作り、呼ばれたら、**自分の処理を足してから、中のオブジェクトに処理を渡します**。包みの上に、さらに包みを重ねられるので、機能を**自由に組み合わせられ**ます。ゲームでは、「武器に炎の追加ダメージ・毒・会心率アップを重ねる」「ログを出す・時間を測る・キャッシュする機能を、あとから足す」といった場面で使います。継承で機能を足すと、組み合わせごとにクラスが必要になりますが、デコレータなら**包む順番と数を変えるだけ**です。

!!! tip "ポイント"
    - デコレータは、**包まれる相手と、同じインターフェース**を持つ。だから、包んだあとも、普通に使える。
    - **機能の組み合わせが多い**とき（A、B、C を、好きに組み合わせたい）に向く。継承だと、組み合わせの数だけクラスが必要。
    - 包む順番で、結果が変わる（「攻撃力 +10 してから 2 倍」と「2 倍してから +10」は違う）。
    - **実行時**に、機能を足したり外したりできる（継承では不可能）。
    - 重ねすぎると、**呼び出しが深く**なる。デバッグしにくくなる。

## 悪い例：機能の組み合わせごとにクラスを作る

```cpp
class Weapon { /* 基本の攻撃 */ };
class FireWeapon : public Weapon {};            // 炎
class PoisonWeapon : public Weapon {};          // 毒
class FirePoisonWeapon : public ??? {};         // 炎と毒 → どちらを継承する？
class FirePoisonCritWeapon : public ??? {};     // さらに会心率…
```

機能が 3 つで、組み合わせは 2 × 2 × 2 = 8 通り、4 つなら 16 通りと、**クラスが爆発**します（[継承と合成](../foundations/composition-vs-inheritance.md)）。

## 良い例：デコレータで包む

```cpp
// 共通のインターフェース
class IWeapon {
 public:
  virtual ~IWeapon() = default;
  virtual int Damage() const = 0;
  virtual std::string Name() const = 0;
};

// 基本の武器
class Sword : public IWeapon {
 public:
  int Damage() const override { return 10; }
  std::string Name() const override { return "剣"; }
};

// デコレータ：同じインターフェース + 中の武器を持つ
class WeaponDecorator : public IWeapon {
 public:
  explicit WeaponDecorator(std::unique_ptr<IWeapon> inner) : inner_(std::move(inner)) {}

 protected:
  std::unique_ptr<IWeapon> inner_;   // 包んでいる相手
};

// 炎の追加ダメージ
class FireEnchant : public WeaponDecorator {
 public:
  using WeaponDecorator::WeaponDecorator;
  int Damage() const override { return inner_->Damage() + 5; }        // 中の結果に、足す
  std::string Name() const override { return "炎の" + inner_->Name(); }
};

// 攻撃力 2 倍
class Doubled : public WeaponDecorator {
 public:
  using WeaponDecorator::WeaponDecorator;
  int Damage() const override { return inner_->Damage() * 2; }
  std::string Name() const override { return "強化された" + inner_->Name(); }
};
```

```cpp
// 組み合わせは、包む順番で決める（新しいクラスはいらない）
std::unique_ptr<IWeapon> weapon = std::make_unique<Sword>();
weapon = std::make_unique<FireEnchant>(std::move(weapon));   // 剣 → 炎の剣
weapon = std::make_unique<Doubled>(std::move(weapon));        // → 強化された炎の剣

std::println("{}: {}", weapon->Name(), weapon->Damage());
```

```text title="実行結果"
強化された炎の剣: 30
```

**計算の順番:** 剣（10）→ 炎（+5 = 15）→ 2 倍（30）。順番を入れ替えて、`Doubled` を先に包むと、`(10 × 2) + 5 = 25` になります。

<div class="anim" data-type="graph" data-label="デコレータ：包むごとに、機能が足される">
n sword 剣 0 0 hit
n d1 ダメージ10 1 0
# 基本：剣のダメージは 10
---
n sword 剣 0 0
n fire 炎 1 0 new
n d2 ダメージ15 2 0 hit
l fire sword new 包む
# 炎で包む：中の結果（10）に +5 して 15
---
n sword 剣 0 0
n fire 炎 1 0
n twice 2倍 2 0 new
n d3 ダメージ30 3 0 hit
l fire sword
l twice fire new 包む
# 2 倍で包む：15 × 2 で 30
</div>

### 呼び出しの流れ

<div class="anim" data-type="graph" data-label="デコレータは、外側から順に呼び、結果が内側から戻ってくる">
n w weapon->Damage() 0 0 hit
n d Doubled 1 0
n f FireEnchant 2 0
n s Sword 3 0
l w d hit 呼ぶ
---
n w weapon->Damage() 0 0
n d Doubled 1 0 hit
n f FireEnchant 2 0
n s Sword 3 0
l w d
l d f hit inner_を呼ぶ
---
n w weapon->Damage() 0 0
n d Doubled 1 0
n f FireEnchant 2 0 hit
n s Sword_=_10 3 0 hit
l w d
l d f
l f s hit inner_を呼ぶ
---
n w weapon->Damage() 0 0
n d Doubled 1 0
n f FireEnchant_10+5=15 2 0 hit
n s Sword_=_10 3 0
l w d
l d f
l s f hit 10_を返す
---
n w weapon->Damage()_=_30 0 0 hit
n d Doubled_15*2=30 1 0 hit
n f FireEnchant_=_15 2 0
n s Sword_=_10 3 0
l d w hit 30_を返す
l f d hit 15_を返す
</div>

外側から内側へ呼び、結果が内側から外側へ戻りながら、**包みごとに加工されます**。

## デコレータの特徴

| 項目 | 説明 |
| --- | --- |
| **組み合わせが自由** | 包む順番と数で、いろいろな機能を作れる |
| **実行時に変えられる** | ゲームの途中で、武器に効果を足す・外す（解除は、包みを剥がす） |
| **元のクラスを変えない** | 既存の `Sword` に手を入れずに、機能を足せる（開放閉鎖の原則） |
| **小さな部品で作れる** | 1 つの包みは、1 つの機能だけ |
| 注意：包みの数が増えると | 呼び出しが深くなる。デバッグで追いにくい |
| 注意：中身を取り出しにくい | 一番内側の剣の情報（`Sword` 型）を、外から取るのは大変 |

## 別の書き方

### 関数（ラムダ）でのデコレータ

クラスにしなくても、**関数を関数で包む**ことで、同じことができます。

```cpp
using DamageFunc = std::function<int()>;

// 関数を受け取って、加工した関数を返す
DamageFunc WithBonus(DamageFunc base, int bonus) {
  return [base = std::move(base), bonus] { return base() + bonus; };
}
DamageFunc Doubled(DamageFunc base) {
  return [base = std::move(base)] { return base() * 2; };
}

DamageFunc damage = [] { return 10; };
damage = WithBonus(std::move(damage), 5);
damage = Doubled(std::move(damage));
std::println("{}", damage());   // 30
```

### ログや計測を、あとから足す

```cpp
// どんなインターフェースの呼び出しにも、ログを足すデコレータ
class LoggedAudio : public IAudio {
 public:
  explicit LoggedAudio(std::unique_ptr<IAudio> inner) : inner_(std::move(inner)) {}
  void Play(std::string_view name) override {
    std::println("[log] Play {}", name);   // 足した処理
    inner_->Play(name);                    // 中に渡す
  }
  // ...他の関数も同様

 private:
  std::unique_ptr<IAudio> inner_;
};
```

デバッグのときだけ `LoggedAudio` で包めば、**本体のコードを変えずに**ログが取れます。

## 似たパターンとの違い

| パターン | 目的 | 違い |
| --- | --- | --- |
| **デコレータ** | **機能を足す**（同じインターフェースのまま） | 包んで、重ねられる |
| [ストラテジー](strategy.md) | **やり方を差し替える** | 中の部品を、**取り替える**（重ねない） |
| **アダプター** | **インターフェースを合わせる** | 違うインターフェースを、期待された形に変換する |
| **プロキシ** | **代理**（アクセスの制御・遅延作成・キャッシュ） | 同じインターフェースで、本体の代わりをする |
| **コンポーネント** | 機能を**持たせる** | 包まず、**横に並べる**（[コンポーネント指向](../../engine/component.md)） |

## ゲームでの使いどころ

| 場面 | 使い方 |
| --- | --- |
| **武器・防具の強化、バフ・デバフ** | 基本の値を包んで、効果を重ねる。効果が切れたら、包みを外す |
| **ダメージ計算の補正** | 属性、クリティカル、防御力を、順に重ねる |
| **サウンド・描画のデバッグ** | ログや計測のデコレータを、あとから包む |
| **入力の加工** | 生の入力 → デッドゾーン → 感度 → 反転、と包む |
| **ファイル読み込み** | 生ファイル → 圧縮解除 → 暗号解除 → キャッシュ、と包む |

## よくあるミス

??? failure "インターフェースが大きすぎて、デコレータが大変"
    インターフェースの関数が 20 個あると、デコレータごとに 20 個を転送する必要があります。インターフェースを小さくします（[インターフェース設計](../foundations/interface-design.md)）。

??? failure "包む順番を気にしない"
    「+10 してから 2 倍」と「2 倍してから +10」で結果が違います。順番が意味を持つことを、設計で決めておきます。

??? failure "バフの解除で、包みを剥がせない"
    `unique_ptr` で包むと、途中の包みだけを外すのが大変です。**効果のリスト**（`vector<Effect>`）を持って、順に適用するほうが、解除しやすいことが多いです（データとして持つ）。

??? failure "デコレータの中で、状態を持ちすぎる"
    包みごとに状態（残り時間など）を持つと、管理が複雑になります。効果の管理は、別のクラスに任せます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 同じインターフェースの「包み」で、既存のオブジェクトに機能を足す
    - [x] 包みを重ねて、機能を自由に組み合わせる（クラスが爆発しない）
    - [x] 実行時に足せる。包む順番で結果が変わる
    - [x] バフ・デバフは、「包む」より「効果のリスト」のほうが管理しやすいことも多い
    - [x] 取り替えるならストラテジー、足すならデコレータ

## 関連ページ

- [継承と合成](../foundations/composition-vs-inheritance.md)
- [インターフェース設計](../foundations/interface-design.md)
- [ストラテジー](strategy.md)
- [コンポーネント指向](../../engine/component.md)
