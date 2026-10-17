---
title: キャッシュ効率
tags:
  - 基礎
  - パフォーマンス
---

# キャッシュ効率

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
</div>

CPU は計算がとても速い一方で、メモリ（RAM）からデータを読むのは遅いです。そこで CPU は、最近使ったデータとその周りを**キャッシュ**という小さくて速い置き場にまとめてコピーしておきます。**データがメモリ上に隙間なく並んでいると、一度読んだときに次の要素もキャッシュに入っている**ので、続けて速く処理できます。逆に、データがあちこちに散らばっていると、毎回遅いメモリまで取りに行くことになります。これが「vector は速く、list は遅い」理由です。

!!! tip "ポイント"
    - <strong>たくさんのデータを毎フレーム回すなら、vector に値で並べて持つ。</strong>
    - ポインタの vector（`vector<Enemy*>`、`vector<unique_ptr<Enemy>>`）は、本体がバラバラに置かれるので回すのが遅くなる。
    - 「よく一緒に使うデータは近くに置く」「使わないデータは分けて置く」と速くなる（ECS や SoA の考え方）。
    - 要素数が少ない（数百個まで）なら、気にしなくてもほとんど差は出ない。

## 基本

### 速さの目安

| 場所 | 読むのにかかる時間（目安） |
| --- | --- |
| CPU のレジスタ | 1 |
| L1 キャッシュ | 約 4 |
| L2 キャッシュ | 約 12 |
| L3 キャッシュ | 約 40 |
| メモリ（RAM） | 約 200 以上 |

メモリから 1 回読む間に、CPU は数百回の計算ができます。

### 連続していると速い

<div class="mem">
<div class="mem-step"><span class="mem-label">vector&lt;Enemy&gt;</span><span class="mem-cells"><span class="move">A</span><span class="move">B</span><span class="move">C</span><span class="move">D</span></span><span class="mem-note">A を読むと、B・C・D も一緒にキャッシュに入る（キャッシュライン = 64 バイト単位）</span></div>
<div class="mem-step"><span class="mem-label">list / ポインタの vector</span><span class="mem-cells"><span class="move">A</span><span class="free">　</span><span class="free">　</span><span class="move">C</span><span class="free">　</span><span class="move">B</span><span class="free">　</span><span class="free">　</span><span class="move">D</span></span><span class="mem-note">1 つ読むたびに別の場所へ飛ぶ。毎回メモリまで取りに行く</span></div>
</div>

## 詳しく

### AoS と SoA

| 方式 | 書き方 | 得意なこと |
| --- | --- | --- |
| AoS（構造体の配列） | `std::vector<Particle>`（各要素に x, y, vx, vy, color...） | 1 つの要素の全部を使う処理 |
| SoA（配列の構造体） | `struct Particles { std::vector<float> x, y, vx, vy; }` | 一部のメンバだけを全要素に対して使う処理 |

```cpp
#include <print>
#include <vector>

// AoS: 位置の更新に使わない color もキャッシュに載ってしまう
struct ParticleAoS {
  float x, y;
  float vx, vy;
  int color[4];
};

// SoA: 位置の更新に必要な配列だけを読む
struct ParticlesSoA {
  std::vector<float> x, y, vx, vy;
  std::vector<int> color;
};

int main() {
  ParticlesSoA p;
  for (int i = 0; i < 4; ++i) {
    p.x.push_back(0.0f);
    p.vx.push_back(static_cast<float>(i));
  }
  for (std::size_t i = 0; i < p.x.size(); ++i) {
    p.x[i] += p.vx[i];  // x と vx だけが並んで読まれる
  }
  std::println("{} / AoS 1 個 {} バイト", p.x, sizeof(ParticleAoS));
}
```

```text title="実行結果"
[0, 1, 2, 3] / AoS 1 個 32 バイト
```

ECS（[エンティティ・コンポーネント・システム](../engine/ecs.md)）は、この考え方をゲーム全体に広げたものです。

### ホットとコールドを分ける

毎フレーム使うデータ（ホット）と、たまにしか使わないデータ（コールド）を分けると、毎フレームの処理で読むメモリが減ります。

```cpp
struct EnemyHot {   // 毎フレーム更新
  float x, y;
  float vx, vy;
};
struct EnemyCold {  // 死んだときや UI 表示のときだけ
  std::string name;
  std::string description;
};
```

### 2 次元配列は横に回す

```cpp
// tiles[y * width + x] の並びなら
for (int y = 0; y < height; ++y) {
  for (int x = 0; x < width; ++x) {  // 内側を x にすると、メモリを順番に読む
    Process(tiles[y * width + x]);
  }
}
```

内側のループを `y` にすると、毎回 `width` 個ぶん離れた場所を読むことになり、遅くなります。

## ゲームでの例

| 場面 | 工夫 |
| --- | --- |
| 大量のパーティクル・弾 | vector に値で持つ。SoA にする |
| ポリモーフィズムで大量のオブジェクト | 種類ごとに vector を分ける |
| 当たり判定 | 位置と大きさだけの配列を別に持つ |
| タイルマップ | 1 本の vector、内側のループは x |

## よくあるミス

??? failure "何でも unique_ptr の vector にする"
    `std::vector<std::unique_ptr<Bullet>>` は、弾 1 発ごとにヒープに置かれるので、全弾の更新がキャッシュミスだらけになります。ポリモーフィズムが要らないなら `std::vector<Bullet>` にします。

??? failure "少ないデータで気にしすぎる"
    敵が 10 体程度なら、どう並べても差はほぼ出ません。読みやすさを優先し、遅いと分かってから測って直します。

## 理解度チェック

!!! question "Q1. 10 万個のパーティクルの位置だけ更新したい。AoS と SoA のどちらが速い？"
    <div class="spoiler" markdown>

    **答え:** たいてい SoA。位置と速度の配列だけを順番に読むので、使わない色やサイズのデータをキャッシュに載せずに済みます。

    </div>

## これだけ覚える

!!! abstract "まとめ"
    - [x] 連続したメモリは速く、バラバラなメモリは遅い
    - [x] 大量のデータは vector に値で並べる
    - [x] よく一緒に使うものを近くに、使わないものは分ける

## 関連ページ

- [計算量](big-o.md)
- [std::vector のパフォーマンス](../stl/containers/vector.md#パフォーマンス)
- [ECS](../engine/ecs.md)
