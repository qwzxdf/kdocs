---
title: データ指向設計
tags:
  - 設計
  - パフォーマンス
---

# データ指向設計

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
</div>

**データ指向設計**（Data-Oriented Design、DOD）は、**「オブジェクトが何をするか」ではなく「データがどう並び、どう流れるか」から設計する**考え方です。普通のオブジェクト指向では「敵というオブジェクトが自分を更新する」と考えますが、データ指向では「全部の敵の位置の配列に、全部の敵の速度を足す」と考えます。CPU のキャッシュを無駄なく使えるので、大量のオブジェクトを扱うゲームで何倍も速くなることがあります。[ECS](../engine/ecs.md) はこの考え方から生まれた設計です。

!!! tip "結論"
    - **同じ処理をたくさんのデータに対して行う**なら、そのデータを連続した配列に並べる。
    - 1 つずつ仮想関数を呼ぶより、**種類ごとにまとめて**普通の関数で処理する。
    - 一緒に使うデータは近くに、使わないデータは別の場所に（ホット / コールドの分離）。
    - オブジェクトが数百程度なら気にしなくていい。**測ってから**適用する。

!!! info "このページを読む前に"
    [キャッシュ効率](../basics/cache.md) を先に読んでください。

## オブジェクト指向とデータ指向

=== "オブジェクト指向的"

    ```cpp
    class GameObject {
     public:
      virtual void Update(float dt) = 0;  // 1 つずつ仮想関数
    };

    std::vector<std::unique_ptr<GameObject>> objects;  // 本体はバラバラ
    for (auto& obj : objects) {
      obj->Update(dt);
    }
    ```

=== "データ指向的"

    ```cpp
    struct Particles {
      std::vector<float> x, y;    // 位置だけが並んだ配列
      std::vector<float> vx, vy;  // 速度だけが並んだ配列
    };

    void UpdatePositions(Particles& p, float dt) {  // 全部まとめて 1 回で
      for (std::size_t i = 0; i < p.x.size(); ++i) {
        p.x[i] += p.vx[i] * dt;
        p.y[i] += p.vy[i] * dt;
      }
    }
    ```

| | オブジェクト指向的 | データ指向的 |
| --- | --- | --- |
| 考え方の中心 | 1 つのオブジェクト | データの配列と、それへの処理 |
| メモリ | オブジェクトごとにバラバラ | 種類ごとに連続 |
| 処理の呼び方 | 1 つずつ（仮想関数） | まとめて（普通のループ） |
| 得意 | 種類が多く、数が少ないもの（UI、ボス） | 種類が少なく、数が多いもの（弾、パーティクル、群衆） |

## 実践のテクニック

### 1. 種類ごとに配列を分ける

```cpp
#include <print>
#include <vector>

struct Bullet {
  float x;
  float y;
  float vy;
};
struct Missile {
  float x;
  float y;
  float speed;
  int target;
};

struct Projectiles {
  std::vector<Bullet> bullets;    // 種類ごとに vector
  std::vector<Missile> missiles;
};

void Update(Projectiles& p, float dt) {
  for (auto& b : p.bullets) {     // 仮想関数を使わず、型ごとにまとめて回す
    b.y += b.vy * dt;
  }
  for (auto& m : p.missiles) {
    m.x += m.speed * dt;
  }
}

int main() {
  Projectiles p;
  p.bullets.push_back({0, 0, 10});
  p.missiles.push_back({0, 0, 5, 1});
  Update(p, 0.5f);
  std::println("{} {}", p.bullets[0].y, p.missiles[0].x);
}
```

```text title="実行結果"
5 2.5
```

### 2. ホットとコールドを分ける

```cpp
struct EnemyMotion {  // 毎フレーム使う（ホット）
  float x, y, vx, vy;
};
struct EnemyInfo {    // たまにしか使わない（コールド）
  std::string name;
  std::string description;
  int drop_table_id;
};

std::vector<EnemyMotion> motions;  // 毎フレームはこれだけを回す
std::vector<EnemyInfo> infos;      // 同じ添字で対応
```

### 3. 「生きているもの」だけを詰めておく

`if (!alive) continue;` で飛ばしながら回すより、生きているものだけを配列の前に詰めておく（死んだら swap して pop_back）ほうが、分岐もなくなり速くなります（[vector](../stl/containers/vector.md#順番がどうでもいいならswap-して-pop_back)）。

### 4. まとめて処理する（バッチ）

| 1 つずつ | まとめて |
| --- | --- |
| 敵 1 体ごとに `DrawSprite()` | 同じ画像の敵を全部集めて 1 回で描く |
| 弾 1 発ごとに当たり判定の関数を呼ぶ | 全弾の位置の配列を一度に調べる |
| オブジェクトごとにファイルを読む | 起動時に全部まとめて読む |

## いつ使うか

| 使う | 使わない |
| --- | --- |
| 弾、パーティクル、群衆など数千〜数万 | プレイヤー、ボス、UI など数が少ないもの |
| 毎フレーム同じ処理をする | たまにしか動かない処理 |
| 実際に測って遅かった | 遅いかどうか分からない（まず測る） |

データ指向とオブジェクト指向は「どちらか一方」ではなく、**数が多くて重いところだけデータ指向にする**のが現実的です。

## よくある失敗

??? failure "全部をデータ指向で書こうとする"
    数が少ないものまで配列の構造体にすると、コードが読みにくくなるだけで速くもなりません。

??? failure "測らずに最適化する"
    遅い原因は描画やファイル読み込みだった、ということもよくあります。プロファイラで測ってから直します。

## 理解度チェック

!!! question "Q1. パーティクルの「色」は生まれたときに決まり、毎フレームは「位置」と「寿命」だけ更新する。どう並べると速い？"
    <div class="spoiler" markdown>

    **答え:** 位置・速度・寿命（ホット）と、色（コールド）を別々の配列にします。毎フレームの更新ではホットな配列だけを回すので、色のぶんのメモリを読まずに済みます。描画のときだけ色の配列を使います。

    </div>

## これだけ覚える

!!! abstract "まとめ"
    - [x] 数が多いものは、データを配列に並べてまとめて処理する
    - [x] 種類ごとに分ける、ホットとコールドを分ける
    - [x] 数が少ないものはオブジェクト指向のままでいい
    - [x] 測ってから適用する

## 関連ページ

- [キャッシュ効率](../basics/cache.md)
- [ECS](../engine/ecs.md)
- [Data-Oriented Design（Richard Fabian）](https://www.dataorienteddesign.com/dodbook/)
