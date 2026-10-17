---
title: オブジェクトプール
tags:
  - ゲームエンジン
---

# オブジェクトプール

**オブジェクトプール**は、**弾やパーティクルのように頻繁に作っては消すオブジェクトを、あらかじめまとめて用意しておき、使い回す仕組み**です。毎回 `new` / `delete`（`make_unique` も同じ）を繰り返すと、メモリ確保のコストがかかり、メモリも細切れになります。最初に 1000 発ぶんの弾を確保しておき、「使っていない弾」を取り出して使い、消えたら「使っていない」に戻すだけにすれば、ゲーム中のメモリ確保はゼロになります。

!!! tip "ポイント"
    - <strong>大量に出たり消えたりするもの（弾、パーティクル、エフェクト、ダメージ数字）に使う。</strong>
    - 一番簡単なのは「固定長の配列 + 使用中フラグ」。
    - 空きを速く見つけたいなら「空きリスト（free list）」を持つ。
    - 外から要素を指すなら、ポインタではなく [ハンドル](../../engine/handle.md)（index + generation）で。
    - 実は「vector に入れて、消すときは swap して pop_back」でも十分速いことが多い。まずはそれで試す。

!!! info "このページを読む前に"
    [`std::vector`](../../stl/containers/vector.md)、[`std::array`](../../stl/containers/array.md)、[キャッシュ効率](../../basics/cache.md) が分かると読みやすいです。

## 基本

### 固定長の配列 + 使用中フラグ

```cpp
#include <array>
#include <print>

struct Bullet {
  bool active = false;
  float x = 0.0f;
  float y = 0.0f;
  float vy = 0.0f;
};

template <std::size_t N>
class BulletPool {
 public:
  // 空いている弾を 1 つ使う（無ければ nullptr）
  Bullet* Spawn(float x, float y, float vy) {
    for (auto& b : bullets_) {
      if (!b.active) {
        b = {true, x, y, vy};
        return &b;
      }
    }
    return nullptr;
  }

  void Update(float dt) {
    for (auto& b : bullets_) {
      if (!b.active) {
        continue;
      }
      b.y += b.vy * dt;
      if (b.y < 0.0f) {
        b.active = false;  // 消す = 使っていない印を付けるだけ
      }
    }
  }

  int ActiveCount() const {
    int n = 0;
    for (const auto& b : bullets_) {
      n += b.active ? 1 : 0;
    }
    return n;
  }

 private:
  std::array<Bullet, N> bullets_{};  // 最初に全部確保。ゲーム中は new しない
};

int main() {
  BulletPool<4> pool;
  pool.Spawn(0, 10, -100);
  pool.Spawn(0, 50, -100);
  pool.Update(0.2f);  // 1 発目は画面外へ
  std::println("使用中 {}", pool.ActiveCount());

  for (int i = 0; i < 5; ++i) {
    if (!pool.Spawn(0, 100, -10)) {
      std::println("満杯で撃てなかった");
    }
  }
}
```

```text title="実行結果"
使用中 1
満杯で撃てなかった
満杯で撃てなかった
```

<div class="anim" data-label="オブジェクトプール：使い回す">
_ _ _ _ # 最初に、4 個ぶんの場所を用意しておく
+弾1 _ _ _ # 借りる：空きを 1 つ使う（新しく確保はしない）
弾1 +弾2 _ _ # もう 1 つ借りる
x弾1 弾2 _ _ # 弾1 が役目を終えた
_ 弾2 _ _ # 返す：場所は空きに戻る（解放はしない）
+弾3 弾2 _ _ # 次に借りるときは、空いた場所を再利用する
</div>

## 詳しく

### 空きリストで速く見つける

上の方法は空きを探すのに O(n) かかります。空いている場所の番号を別に覚えておけば O(1) で取り出せます。

```cpp
#include <cstddef>
#include <print>
#include <vector>

template <class T>
class Pool {
 public:
  explicit Pool(std::size_t capacity) : items_(capacity), used_(capacity, false) {
    free_.reserve(capacity);
    for (std::size_t i = capacity; i > 0; --i) {
      free_.push_back(i - 1);  // 0 番から使われるように逆順に積む
    }
  }

  // 空いている番号を返す（満杯なら -1）
  long Acquire() {
    if (free_.empty()) {
      return -1;
    }
    std::size_t i = free_.back();
    free_.pop_back();
    used_[i] = true;
    items_[i] = T{};
    return static_cast<long>(i);
  }

  void Release(std::size_t i) {
    if (used_[i]) {
      used_[i] = false;
      free_.push_back(i);
    }
  }

  T& operator[](std::size_t i) { return items_[i]; }
  std::size_t FreeCount() const { return free_.size(); }

 private:
  std::vector<T> items_;
  std::vector<bool> used_;
  std::vector<std::size_t> free_;  // 空いている番号のスタック
};

struct Particle {
  float life = 1.0f;
};

int main() {
  Pool<Particle> particles(3);
  long a = particles.Acquire();
  long b = particles.Acquire();
  particles.Release(static_cast<std::size_t>(a));
  long c = particles.Acquire();  // さっき空いた番号が再利用される
  std::println("a={} b={} c={} / 空き {}", a, b, c, particles.FreeCount());
}
```

```text title="実行結果"
a=0 b=1 c=0 / 空き 1
```

### 方式の比較

| 方式 | 取り出し | 全部を回す | 特徴 |
| --- | --- | --- | --- |
| 配列 + 使用中フラグ | O(n) | 使っていないものも見る | 一番簡単。数百個までなら十分 |
| 空きリスト | O(1) | 使っていないものも見る | 取り出しが速い |
| vector + swap して pop_back | O(1)（push_back） | 使用中だけを詰めて回せる | 回すのが一番速い。並び順は変わる。要素の位置が動くので外からはハンドルで指す |
| [SlotMap](../../engine/handle.md)（世代付き） | O(1) | 使っていないものも見る | 外から安全に指せる |

### 満杯になったら？

| 方針 | 例 |
| --- | --- |
| 作らない | 弾が撃てない（シューティングでよくある） |
| 一番古いものを上書きする | パーティクル、足跡、弾痕 |
| プールを大きくする | 確保が起きるが、めったに起きないなら許容 |

## ゲームでの例

| 対象 | 数の目安 |
| --- | --- |
| 弾 | 数百〜数千 |
| パーティクル | 数千〜数万 |
| ダメージの数字、ヒットエフェクト | 数十 |
| 効果音の再生チャンネル | 数十 |
| 敵 | ウェーブごとの最大数 |

## よくあるミス

??? failure "使い回すときに前のデータが残る"
    取り出したときに初期化し直さないと、前の弾の速度や色が残ります。`items_[i] = T{};` のように毎回リセットします。

??? failure "返したあとの要素を使い続ける"
    `Release` したあとに、同じ番号を覚えていた別の場所が触ると、新しく使い始めた別のオブジェクトを壊します。世代付きのハンドルで防ぎます。

??? failure "最初からプールを作る"
    今の PC はメモリ確保もそれなりに速いので、少ない数なら普通に vector に `push_back` / `erase_if` で十分です。測って遅いと分かってから導入します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 大量に作って消すものは、まとめて確保して使い回す
    - [x] 取り出すときに初期化し直す
    - [x] 外から指すならハンドル
    - [x] 少ないなら vector で十分。測ってから導入

## 関連ページ

- [ハンドルと世代 ID](../../engine/handle.md)
- [ECS](ecs.md)
- [Game Programming Patterns: Object Pool](https://gameprogrammingpatterns.com/object-pool.html)
- [メモリ確保（最適化）](../../optimize/allocation.md)
- [プールアロケータ](../../optimize/allocators/pool.md)
