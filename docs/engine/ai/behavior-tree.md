---
title: ビヘイビア ツリー
tags:
  - ゲームエンジン
---

# ビヘイビア ツリー

ステートマシンで敵を作ると、状態が増えるたびに、遷移の線が増えます。「待機から追跡」「追跡から攻撃」「攻撃から追跡」「追跡から待機」「どこからでも、体力が減ったら逃走」と、線が絡まってくると、どこを直せば何が変わるのか、読み解けなくなります。

ビヘイビア ツリーは、<strong>行動を木の形で組み立て、毎フレーム、木の根から順に「できるか」を試して、最初に成功した行動を実行する</strong>方式です。優先順位は木の並びで表すので、遷移の線を引く必要がありません。

!!! tip "ポイント"
    - 木のノードは、毎回、成功（Success）・失敗（Failure）・実行中（Running）のどれかを返す
    - 枝になるノードは 2 つが基本。Sequence（順に全部成功させる）と、Selector（成功するまで順に試す）
    - 葉になるノードは、条件（敵が見えるか）と行動（歩く、撃つ）
    - 数フレームかかる行動は、Running を返し、次のフレームで続きから再開する
    - 状態を共有する場所として、ブラックボード（共有の変数置き場）を使う

!!! info "このページを読む前に"
    - [ゲーム AI](index.md)
    - [ステートマシン](../../design/patterns/state-machine.md)

## ノードの種類 {#nodes}

木は、根から枝へ枝から葉へと広がります。毎フレーム、根に「実行して」と頼み、根が子に頼み、と、葉まで伝わります。

### Sequence {#sequence}

子を左から順に実行し、<strong>1 つでも失敗したら、そこで失敗</strong>を返します。全部成功したら、成功です。「敵が見える、かつ、射程内、かつ、撃つ」のように、条件と行動を順に並べるときに使います。

### Selector {#selector}

子を左から順に実行し、<strong>1 つでも成功したら、そこで成功</strong>を返します。全部失敗したら、失敗です。「攻撃できれば攻撃、だめなら追跡、それもだめなら巡回」のように、優先順位の高い順に試すときに使います。

### 条件と行動 {#leaf}

葉のノードです。条件は、状況を調べて、成功か失敗を返します。行動は、実際の動きを行い、終わっていれば成功、続いていれば Running を返します。

## 木の例 {#example}

```text
Selector（根）
 ├─ Sequence「逃げる」
 │    ├─ 条件：体力が 20% 以下
 │    └─ 行動：安全な場所へ走る
 ├─ Sequence「攻撃」
 │    ├─ 条件：敵が射程内
 │    └─ 行動：撃つ
 ├─ Sequence「追跡」
 │    ├─ 条件：敵が見えている
 │    └─ 行動：敵に近づく
 └─ 行動：巡回する
```

根の Selector は、上から順に試します。体力が少なければ「逃げる」、そうでなければ「攻撃」を試し、射程外なら失敗して、次の「追跡」を試します。優先順位の高い行動を上に置くだけで、「体力が少ないときは、何よりも逃げる」が表せます。ステートマシンで書くと、全部の状態から「逃走」への線を引く場面です。

## 実装 {#impl}

最小の実装は、数十行です。

```cpp
#include <memory>
#include <vector>

enum class Status { kSuccess, kFailure, kRunning };

// 木のすべてのノードの基底クラス
class Node {
 public:
  virtual ~Node() = default;
  virtual Status Tick() = 0;  // 毎フレーム、1 回呼ばれる
};

// 子を順に実行し、失敗したらそこで失敗
class Sequence : public Node {
 public:
  explicit Sequence(std::vector<std::unique_ptr<Node>> children)
      : children_(std::move(children)) {}

  Status Tick() override {
    for (auto& child : children_) {
      const Status s = child->Tick();
      if (s != Status::kSuccess) return s;  // 失敗か実行中なら、そこで止める
    }
    return Status::kSuccess;
  }

 private:
  std::vector<std::unique_ptr<Node>> children_;
};

// 子を順に実行し、成功したらそこで成功
class Selector : public Node {
 public:
  explicit Selector(std::vector<std::unique_ptr<Node>> children)
      : children_(std::move(children)) {}

  Status Tick() override {
    for (auto& child : children_) {
      const Status s = child->Tick();
      if (s != Status::kFailure) return s;  // 成功か実行中なら、そこで止める
    }
    return Status::kFailure;
  }

 private:
  std::vector<std::unique_ptr<Node>> children_;
};
```

`Tick` は、毎フレーム 1 回、根から呼ばれます。`Sequence` は、子が `kSuccess` を返す間だけ次へ進み、`kFailure` か `kRunning` が出たら、その値をそのまま返します。`Selector` は逆で、`kFailure` の間だけ次へ進みます。

この単純な実装では、`Running` が返ったあとも、次のフレームでは、また最初の子から試します。優先順位の高い条件を毎フレーム評価し直せるので、「逃げる」が途中で割り込めます。ただし、長い行動の途中で、順番を最初からやり直すと、動作が切り替わる揺れが出ることもあります。長い行動は、実行中の子を覚えておいて、そこから再開する作りにします。

### ブラックボード {#blackboard}

ノード同士が「敵の位置」「自分の体力」を共有します。ノードの中に持つと、結びつきが強くなるので、共有の変数置き場（ブラックボード）に集めます。

```cpp
#include <string>
#include <unordered_map>

// 木のノードが読み書きする、共有の変数置き場
struct Blackboard {
  float health = 100.0f;
  float target_distance = 0.0f;
  bool target_visible = false;
};
```

条件と行動のノードは、ブラックボードへの参照を持ちます。キャラクターごとに 1 つ作ると、同じ木を複数のキャラクターで使い回せます。

## ステートマシンとの使い分け {#vs-fsm}

ステートマシンは、状態の中の処理を明確に書けます。状態が少なく、遷移が単純なら、短く書けます。

ビヘイビア ツリーは、優先順位の高い順に条件を試す、という形を素直に表せます。行動の追加や順序の変更が木の編集で済むので、デザイナーが調整するのにも向いています。

両方を組み合わせることもあります。大きな状態の切り替え（戦闘 / 探索）をステートマシンで、状態の中の行動の選び方をビヘイビア ツリーで書く、という形です。

## よくあるミス {#mistakes}

??? failure "行動が毎フレーム最初からやり直されて、足踏みする"
    `Running` を返した行動を次のフレームで続きから再開する仕組みがありません。実行中のノードを覚えておきます。

??? failure "木が大きくなって、どこで何が決まるのか追えない"
    部分木を名前を付けた塊（サブツリー）にします。確認用に実行中のノードを画面に出すデバッグ表示を用意します。

??? failure "全員が毎フレーム、木をたどって重い"
    考える頻度を下げます。遠い敵は数フレームに 1 回にします。

## これだけ覚える {#summary}

- Sequence は全部成功させる、Selector は成功するまで試す
- 優先順位は、木の並びで表す
- 共有の値はブラックボードに置く。実行中のノードは覚えておく

## 関連ページ

- [ゲーム AI](index.md)
- [経路探索](pathfinding.md)
- [ステートマシン](../../design/patterns/state-machine.md)
