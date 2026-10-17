---
title: データ構造の配置の実例集
tags:
  - 最適化
---

# データ構造の配置の実例集

CPU は、メモリから<strong>64 バイトのかたまり（キャッシュライン）</strong>ごとにデータを読みます。**使うデータが、近くにまとまっている**と速く、**散らばっている**と遅くなります（[メモリとキャッシュ](memory-cache.md)）。このページは、**構造体の並べ方・サイズの減らし方・配列の持ち方**を、**実例**でまとめます。**よく使うデータだけを、小さく、連続して**置くのが基本です。

!!! tip "ポイント"
    - <strong>AoS（構造体の配列）</strong>は、全部の項目を使うとき。<strong>SoA（配列の構造体）</strong>は、<strong>一部の項目だけ</strong>を大量に回すとき。
    - <strong>ホット（よく使う）データと、コールド（たまにしか使わない）データを分ける</strong>。
    - <strong>構造体のメンバは、大きい順に並べる</strong>（パディングを減らす）。<strong>`sizeof` を確認</strong>する。
    - <strong>ポインタの代わりに、インデックス（32 ビット）</strong>。サイズが半分になり、連続した配列に置ける。
    - <strong>型は、必要な大きさに</strong>（`uint8_t`、`enum class : uint8_t`）。<strong>bool を大量に持たず、ビットにする</strong>。
    - <strong>スレッド間で共有する書き込みデータは、キャッシュラインを分ける</strong>（false sharing）。

## AoS と SoA

<svg class="fig" viewBox="0 0 642 240" role="img" aria-label="AoS と SoA のメモリ配置"><text x="20" y="20" class="fig-title">AoS：1 つの粒子の全項目が、並ぶ</text><rect x="30" y="34" width="26" height="28" fill="rgba(76,139,245,0.55)" stroke="currentColor"/><rect x="56" y="34" width="26" height="28" fill="rgba(76,139,245,0.55)" stroke="currentColor"/><rect x="82" y="34" width="26" height="28" fill="rgba(76,139,245,0.55)" stroke="currentColor"/><rect x="108" y="34" width="26" height="28" fill="rgba(150,150,150,0.25)" stroke="currentColor"/><rect x="134" y="34" width="26" height="28" fill="rgba(150,150,150,0.25)" stroke="currentColor"/><rect x="160" y="34" width="26" height="28" fill="rgba(150,150,150,0.25)" stroke="currentColor"/><rect x="186" y="34" width="26" height="28" fill="rgba(76,139,245,0.55)" stroke="currentColor"/><rect x="212" y="34" width="26" height="28" fill="rgba(76,139,245,0.55)" stroke="currentColor"/><rect x="238" y="34" width="26" height="28" fill="rgba(76,139,245,0.55)" stroke="currentColor"/><rect x="264" y="34" width="26" height="28" fill="rgba(150,150,150,0.25)" stroke="currentColor"/><rect x="290" y="34" width="26" height="28" fill="rgba(150,150,150,0.25)" stroke="currentColor"/><rect x="316" y="34" width="26" height="28" fill="rgba(150,150,150,0.25)" stroke="currentColor"/><rect x="342" y="34" width="26" height="28" fill="rgba(76,139,245,0.55)" stroke="currentColor"/><rect x="368" y="34" width="26" height="28" fill="rgba(76,139,245,0.55)" stroke="currentColor"/><rect x="394" y="34" width="26" height="28" fill="rgba(76,139,245,0.55)" stroke="currentColor"/><rect x="420" y="34" width="26" height="28" fill="rgba(150,150,150,0.25)" stroke="currentColor"/><rect x="446" y="34" width="26" height="28" fill="rgba(150,150,150,0.25)" stroke="currentColor"/><rect x="472" y="34" width="26" height="28" fill="rgba(150,150,150,0.25)" stroke="currentColor"/><text x="30" y="82">青＝位置（使う）、灰＝速度・寿命・色など（今は使わない）。位置の間に、使わないデータが挟まる</text><text x="20" y="120" class="fig-title">SoA：項目ごとに、連続して並ぶ</text><rect x="30" y="134" width="26" height="28" fill="rgba(76,139,245,0.55)" stroke="currentColor"/><rect x="56" y="134" width="26" height="28" fill="rgba(76,139,245,0.55)" stroke="currentColor"/><rect x="82" y="134" width="26" height="28" fill="rgba(76,139,245,0.55)" stroke="currentColor"/><rect x="108" y="134" width="26" height="28" fill="rgba(76,139,245,0.55)" stroke="currentColor"/><rect x="134" y="134" width="26" height="28" fill="rgba(76,139,245,0.55)" stroke="currentColor"/><rect x="160" y="134" width="26" height="28" fill="rgba(76,139,245,0.55)" stroke="currentColor"/><rect x="186" y="134" width="26" height="28" fill="rgba(150,150,150,0.25)" stroke="currentColor"/><rect x="212" y="134" width="26" height="28" fill="rgba(150,150,150,0.25)" stroke="currentColor"/><rect x="238" y="134" width="26" height="28" fill="rgba(150,150,150,0.25)" stroke="currentColor"/><rect x="264" y="134" width="26" height="28" fill="rgba(150,150,150,0.25)" stroke="currentColor"/><rect x="290" y="134" width="26" height="28" fill="rgba(150,150,150,0.25)" stroke="currentColor"/><rect x="316" y="134" width="26" height="28" fill="rgba(150,150,150,0.25)" stroke="currentColor"/><rect x="342" y="134" width="26" height="28" fill="rgba(150,150,150,0.25)" stroke="currentColor"/><rect x="368" y="134" width="26" height="28" fill="rgba(150,150,150,0.25)" stroke="currentColor"/><rect x="394" y="134" width="26" height="28" fill="rgba(150,150,150,0.25)" stroke="currentColor"/><rect x="420" y="134" width="26" height="28" fill="rgba(150,150,150,0.25)" stroke="currentColor"/><rect x="446" y="134" width="26" height="28" fill="rgba(150,150,150,0.25)" stroke="currentColor"/><rect x="472" y="134" width="26" height="28" fill="rgba(150,150,150,0.25)" stroke="currentColor"/><text x="30" y="182">位置だけが連続 → キャッシュを無駄なく使える（SIMD にもしやすい）</text><text x="30" y="215">位置を更新するループは、SoA の方が、読むメモリが少なくて済む</text></svg>

### AoS（Array of Structs：構造体の配列）

```cpp
struct Particle {
  Vector3 position;
  Vector3 velocity;
  float life;
  Color color;
  float size;
};

std::vector<Particle> particles;

for (Particle& p : particles) {
  p.position += p.velocity * dt;
}
```

**位置の更新**には、`position` と `velocity` しか使いません。しかし、`Particle` 全体（`life`、`color`、`size`）が、**キャッシュに載ります**。**使わないデータで、キャッシュが埋まる**ので、無駄です。

### SoA（Struct of Arrays：配列の構造体）

```cpp
struct Particles {
  std::vector<Vector3> position;
  std::vector<Vector3> velocity;
  std::vector<float> life;
  std::vector<Color> color;
  std::vector<float> size;
};

for (size_t i = 0; i < particles.position.size(); ++i) {
  particles.position[i] += particles.velocity[i] * dt;
}
```

**使う項目だけ**が、**連続して並ぶ**ので、キャッシュを**無駄なく**使え、**SIMD**にもしやすくなります。

| 項目 | AoS | SoA |
| --- | --- | --- |
| **全項目を使う処理** | **速い**（1 つのかたまり） | やや遅い（複数の配列を読む） |
| **一部の項目だけ回す処理** | 遅い（無駄が多い） | **速い** |
| **SIMD** | やりにくい | **やりやすい** |
| **要素の追加・削除** | **簡単** | 各配列を、全部更新（手間） |
| **コードの書きやすさ** | **自然** | 面倒 |
| **ランダムアクセスで、全項目** | 速い（近くにある） | 遅い（配列ごとに、離れている） |

**まずは AoS で書き、プロファイラーで、キャッシュミスが多いループ**だけ、SoA にします（[データ指向設計](../design/patterns/data-oriented.md)）。

### AoSoA（ハイブリッド）

<strong>小さなかたまり（4・8 要素）</strong>ごとに SoA にする方法です。SIMD の幅に合わせます。**実装が複雑**なので、**SIMD を本格的に使う所**だけです。

## ホットとコールドの分割

**よく使う（ホット）項目と、たまにしか使わない（コールド）項目**を、別の構造体にします。

```cpp
struct EnemyHot {
  Vector3 position;
  Vector3 velocity;
  float health;
  uint8_t state;
};

struct EnemyCold {
  std::string name;
  std::string description;
  Vector3 spawn_point;
  int reward;
};

std::vector<EnemyHot> hot;
std::vector<EnemyCold> cold;
```

**毎フレーム回すホットデータは、小さく・連続**にして、**名前・説明のようなコールドデータ**は、別の配列に追い出します。**同じインデックス**で、対応させます。

## 構造体のサイズとパディング

CPU は、**型の大きさの倍数の位置**にあるデータを、速く読みます。コンパイラは、そのために、<strong>メンバの間に、隙間（パディング）</strong>を入れます。

```cpp
struct Bad {
  char a;
  double b;
  char c;
  int d;
};

struct Good {
  double b;
  int d;
  char a;
  char c;
};
```

| 構造体 | サイズ | 内訳 |
| --- | --- | --- |
| `Bad` | **24 バイト** | `a`(1) + 隙間(7) + `b`(8) + `c`(1) + 隙間(3) + `d`(4) |
| `Good` | **16 バイト** | `b`(8) + `d`(4) + `a`(1) + `c`(1) + 隙間(2) |

**メンバを、大きい順（8 → 4 → 2 → 1 バイト）に並べる**と、隙間が減ります。

```cpp
static_assert(sizeof(Good) == 16);
static_assert(alignof(Good) == 8);
```

**`static_assert(sizeof(...))`** で、**意図したサイズ**を保証します。**メンバを足して、いつの間にか大きくなる**のを防げます。

### 確認する方法

| 方法 | 説明 |
| --- | --- |
| **`sizeof` / `alignof` / `offsetof`** | 実際のサイズ・位置を確認 |
| **MSVC：`/d1reportSingleClassLayoutName`** | クラスのレイアウトを、**ビルドの出力**に表示（`/d1reportSingleClassLayoutEnemy`） |
| **デバッガーのメモリ表示** | 実際の並びを、見る |

## 型を小さくする

| 変更 | 効果 |
| --- | --- |
| **`int` → `uint8_t` / `uint16_t`** | 値の範囲が小さいなら、サイズが 1/2〜1/4 |
| **`enum class State : uint8_t`** | 列挙型が、**1 バイト**で済む（既定は `int` = 4 バイト） |
| **`double` → `float`** | ゲームの座標・時間は、`float` で十分なことが多い（精度に注意） |
| <strong>ポインタ（8 バイト）→ インデックス（4 バイト）</strong> | **半分**。配列の中の位置で参照する |
| **`bool` を大量に → ビットフラグ** | `bool` 8 個 = 8 バイト、ビットなら **1 バイト** |

```cpp
enum class EnemyFlag : uint8_t {
  kAlive = 1 << 0,
  kVisible = 1 << 1,
  kAggro = 1 << 2,
};

struct Enemy {
  uint8_t flags;
};

bool alive = (enemy.flags & static_cast<uint8_t>(EnemyFlag::kAlive)) != 0;
```

!!! warning "小さくしすぎない"
    **`uint8_t` の演算は、整数の昇格**で、コードが読みにくくなります。**数万個以上**持つデータで、**キャッシュに効くとき**だけ小さくします。1 個しかないものは、`int` で十分です。

### ビットフィールド

```cpp
struct Flags {
  uint32_t alive : 1;
  uint32_t visible : 1;
  uint32_t team : 4;
  uint32_t state : 8;
};
```

**ビットフィールド**は、**複数の値を 1 つの整数に詰める**書き方です。**並びと配置は、実装依存**なので、**ファイルへの保存・通信には使いません**。

## ポインタをインデックスにする

```cpp
struct Node {
  Node* parent;
  Node* first_child;
  Node* next_sibling;
};

struct NodeCompact {
  uint32_t parent;
  uint32_t first_child;
  uint32_t next_sibling;
};
```

| 項目 | ポインタ | インデックス |
| --- | --- | --- |
| サイズ | **8 バイト** | **4 バイト**（半分） |
| <strong>配列の拡大（再確保）</strong> | **ポインタが無効に**なる | **無効にならない** |
| **保存・読み込み** | 使えない（アドレスが変わる） | **そのまま保存できる** |
| 無効値 | `nullptr` | `0xFFFFFFFF` など |

**インデックスなら、構造体全体を、`memcpy` でコピー・保存**できます（[ハンドル](../engine/handle.md)）。

## ポインタの追跡を避ける

<strong>ポインタを辿る（pointer chasing）</strong>たびに、**キャッシュミス**になる可能性があります。

<div class="anim" data-type="graph" data-label="リストはあちこちに散らばり、配列は連続している">
n a A 0 0
n b B 1 2
n c C 2 0
n d D 3 2
l a b
l b c
l c d
---
n a A 0 0 hit
n b B 1 0 hit
n c C 2 0 hit
n d D 3 0 hit
</div>

| 遅い | 速い |
| --- | --- |
| `std::list<T>` | **`std::vector<T>`** |
| `std::vector<T*>`（ポインタの配列） | **`std::vector<T>`**（値の配列） |
| `std::map<K, V>`（木） | **`std::flat_map<K, V>`**、ソート済み `vector` |
| 親子の関係をポインタで持つ | **配列 + インデックス**、深さ優先順に並べる |
| `std::unique_ptr<T>` のコンテナ | **値で持つ**（ポリモーフィズムが必要なときだけ、ポインタ） |

## 削除の方法（連続を保つ）

**配列の途中を消す**と、**後ろを詰める**のが重いです。**順序が不要**なら、**最後の要素と入れ替えて、末尾を消す**（swap-and-pop）。

```cpp
void Remove(std::vector<Enemy>& v, size_t index) {
  v[index] = std::move(v.back());
  v.pop_back();
}
```

| 方法 | コスト |
| --- | --- |
| `erase(it)` | 後ろを全部ずらす（O(n)） |
| **swap-and-pop** | <strong>O(1)</strong>。順序は、変わる |
| **フラグを立てて、あとでまとめて削除** | 反復中の削除が、安全（`erase_if`） |

**インデックスで参照している**場合、swap-and-pop で、**最後の要素のインデックスが変わる**ので、**世代付きのハンドル**にします（[ハンドル](../engine/handle.md)、[ECS](../design/patterns/ecs.md)）。

## スパースセット

**ID が飛び飛び**（大きな ID を持つ、少数のエンティティ）で、**連続した配列**で回したいときの構造です。

| 配列 | 引く / 持つもの |
| --- | --- |
| `sparse[ID]` | dense の位置 |
| `dense[i]` | ID |
| `data[i]` | データ |

| 操作 | コスト |
| --- | --- |
| **ID から、データを探す** | <strong>O(1)</strong>（`sparse` を引く） |
| **全部を回す** | <strong>O(n)</strong>、`dense` を**連続**で |
| **追加・削除** | <strong>O(1)</strong>（削除は、最後と入れ替え） |

**ECS のコンポーネントの保存**に、よく使われます（[ECS](../design/patterns/ecs.md)）。

## false sharing

**複数のスレッド**が、<strong>同じキャッシュライン（64 バイト）</strong>の、**別々の変数**に書き込むと、**キャッシュラインの取り合い**で、遅くなります。

```cpp
struct Counters {
  alignas(std::hardware_destructive_interference_size) std::atomic<int> a;
  alignas(std::hardware_destructive_interference_size) std::atomic<int> b;
};
```

| 項目 | 説明 |
| --- | --- |
| **起きる条件** | 別々のスレッドが、**近くにある変数**に、書く |
| **対策** | **`alignas(64)`** で、キャッシュラインを分ける。**スレッドごとのデータを、まとめる** |
| **`std::hardware_destructive_interference_size`** | **キャッシュラインを分ける**のに、適したサイズ（C++17） |

（[マルチスレッド化](multithreading.md)）

## よくあるミス

??? failure "メンバの並びが適当で、パディングで、サイズが倍になる"
    **大きい順**に並べ、**`static_assert(sizeof(...))`** で確認します。

??? failure "使わないデータが多い構造体を、毎フレーム全部回している"
    **ホット・コールド分割**、または **SoA** にします。

??? failure "`std::vector<Enemy*>` で、ポインタを辿って遅い"
    **値の配列**（`std::vector<Enemy>`）にします。

??? failure "型を小さくしすぎて、キャストだらけになる"
    **大量に持つデータだけ**、小さくします。

??? failure "ビットフィールドを、ファイルに保存した"
    並びが、実装依存です。**固定幅の整数と、明示的なビット演算**にします。

??? failure "別スレッドの書き込む変数が、隣り合っていて、遅い"
    **false sharing** です。`alignas(64)` で分けます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>一部の項目だけ回す大量データは SoA</strong>。<strong>ホット・コールドを分ける</strong>
    - [x] <strong>メンバは大きい順</strong>。<strong>`static_assert(sizeof(...))`</strong> でサイズを守る
    - [x] <strong>型を必要な大きさに</strong>。<strong>ポインタ → 32 ビットのインデックス</strong>。<strong>`enum class : uint8_t`</strong>
    - [x] <strong>ポインタを辿らない</strong>（`list` → `vector`、`vector<T*>` → `vector<T>`）。<strong>削除は swap-and-pop</strong>
    - [x] <strong>スレッドが書く変数は、キャッシュラインを分ける</strong>（false sharing）

## 関連ページ

- [最適化の進め方](index.md)
- [メモリとキャッシュ](memory-cache.md)
- [メモリ使用量](memory-usage.md)
- [SIMD](simd.md)
- [データ指向設計](../design/patterns/data-oriented.md)
- [ECS](../design/patterns/ecs.md)
- [ハンドル](../engine/handle.md)
