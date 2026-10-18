---
title: ハンドルと世代 ID
tags:
  - ゲームエンジン
---

# ハンドルと世代 ID

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
</div>

**ハンドル**は、オブジェクトを**ポインタではなく番号で指す**ための小さな値です。ゲームでは「敵がプレイヤーを狙っている」「弾が撃った人を覚えている」のように、別のオブジェクトを参照することがよくありますが、ポインタで覚えると相手が消えたときに壊れます。ハンドルなら「その番号のオブジェクトがまだいるか」を毎回確かめられます。さらに番号に<strong>世代（generation）</strong>を付けると、消えた番号が再利用されたときに「別人を触ってしまう」事故も防げます。

!!! tip "ポイント"
    - <strong>消えるかもしれない相手は、ポインタではなくハンドル（番号）で覚える。</strong>
    - ハンドル = 「配列の何番目か（index）」+「何代目か（generation）」。
    - スロットを再利用するたびに世代を 1 増やす。ハンドルの世代と一致しなければ「もういない」。
    - ハンドルは小さな整数なので、コピーもセーブも簡単。
    - ECS のエンティティ ID も、この仕組みで作られていることが多い。

!!! info "このページを読む前に"
    [ポインタ](../basics/pointer.md) と [所有権](../basics/ownership.md) を先に読むと、なぜ必要なのかが分かりやすいです。

## 基本

### ポインタで覚えると困ること

```cpp
Enemy* target = &enemies[3];
enemies.erase(enemies.begin() + 3);  // 倒された
target->hp -= 10;                    // 消えたもの（か別の敵）を触ってしまう
```

### 番号だけで覚えても困ること

```text
1. 敵 A を 3 番に入れる。ミサイルは「3 番」を狙う
2. 敵 A が倒されて 3 番が空く
3. 新しい敵 B が 3 番に入る
4. ミサイルは「3 番」= 敵 B に当たってしまう（狙ってもいない相手）
```

### 世代を付ける

<div class="mem">
<div class="mem-step"><span class="mem-label">スロット 3</span><span class="mem-cells"><span class="move">A</span></span><span class="mem-note">世代 1。ミサイルのハンドルは (3, 1)</span></div>
<div class="mem-step"><span class="mem-label">A が消える</span><span class="mem-cells"><span class="gone">A</span></span><span class="mem-note">スロット 3 の世代を 2 に上げる</span></div>
<div class="mem-step"><span class="mem-label">B が入る</span><span class="mem-cells"><span class="new">B</span></span><span class="mem-note">B のハンドルは (3, 2)。ミサイルの (3, 1) とは世代が違うので「もういない」と分かる</span></div>
</div>

## 詳しく

### 世代付きのプールを作る

```cpp
#include <cstdint>
#include <optional>
#include <print>
#include <string>
#include <utility>
#include <vector>

struct Handle {
  std::uint32_t index = 0;
  std::uint32_t generation = 0;
  bool operator==(const Handle&) const = default;
};

template <class T>
class SlotMap {
 public:
  Handle Add(T value) {
    std::uint32_t index;
    if (!free_.empty()) {  // 空いているスロットを再利用
      index = free_.back();
      free_.pop_back();
    } else {
      index = static_cast<std::uint32_t>(slots_.size());
      slots_.push_back({});
    }
    Slot& slot = slots_[index];
    slot.value = std::move(value);
    return {index, slot.generation};
  }

  void Remove(Handle h) {
    if (!IsValid(h)) {
      return;
    }
    Slot& slot = slots_[h.index];
    slot.value.reset();
    ++slot.generation;  // 世代を進める：古いハンドルは全部無効になる
    free_.push_back(h.index);
  }

  bool IsValid(Handle h) const {
    return h.index < slots_.size() && slots_[h.index].generation == h.generation &&
           slots_[h.index].value.has_value();
  }

  // 無効なハンドルなら nullptr
  T* Get(Handle h) { return IsValid(h) ? &*slots_[h.index].value : nullptr; }

 private:
  struct Slot {
    std::optional<T> value;
    std::uint32_t generation = 1;
  };
  std::vector<Slot> slots_;
  std::vector<std::uint32_t> free_;
};

struct Enemy {
  std::string name;
  int hp;
};

int main() {
  SlotMap<Enemy> enemies;
  Handle a = enemies.Add({"スライム", 10});
  Handle missile_target = a;  // ミサイルが狙う

  enemies.Remove(a);                         // スライムが倒された
  Handle b = enemies.Add({"ゴブリン", 30});  // 同じスロットが再利用される

  std::println("スロット同じ？ {} / 世代 {} → {}", a.index == b.index, a.generation,
               b.generation);
  if (Enemy* e = enemies.Get(missile_target)) {
    std::println("命中: {}", e->name);
  } else {
    std::println("ターゲットはもういない");
  }
  std::println("ゴブリンは有効？ {}", enemies.IsValid(b));
}
```

```text title="実行結果"
スロット同じ？ true / 世代 1 → 2
ターゲットはもういない
ゴブリンは有効？ true
```

### 1 つの整数にまとめる

ハンドルは 64 ビット（または 32 ビット）の整数 1 個に詰めることもよくあります。

```cpp
#include <cstdint>
#include <print>

// 下位 32 ビットが index、上位 32 ビットが generation
constexpr std::uint64_t MakeId(std::uint32_t index, std::uint32_t generation) {
  return (static_cast<std::uint64_t>(generation) << 32) | index;
}
constexpr std::uint32_t IndexOf(std::uint64_t id) { return static_cast<std::uint32_t>(id); }
constexpr std::uint32_t GenerationOf(std::uint64_t id) {
  return static_cast<std::uint32_t>(id >> 32);
}

int main() {
  std::uint64_t id = MakeId(7, 3);
  std::println("{} → index {} / generation {}", id, IndexOf(id), GenerationOf(id));
}
```

```text title="実行結果"
12884901895 → index 7 / generation 3
```

### 型ごとにハンドルを分ける

`Handle` が 1 種類だと、敵のハンドルをテクスチャの関数に渡してしまう間違いが起きます。テンプレートで型を分けると、コンパイラが見つけてくれます。

```cpp
template <class Tag>
struct TypedHandle {
  std::uint32_t index;
  std::uint32_t generation;
};

using EnemyHandle = TypedHandle<struct EnemyTag>;
using TextureHandle = TypedHandle<struct TextureTag>;

void Draw(TextureHandle texture);
// Draw(enemy_handle);  // コンパイルエラー：型が違う
```

## ゲームでの例

| 場面 | ハンドルで覚えるもの |
| --- | --- |
| 追尾・ターゲット | 狙っている敵 |
| 弾 | 撃った人（キルの記録・味方の弾は当たらない） |
| リソース | テクスチャ・サウンド（[リソース管理](resource.md)） |
| ECS | エンティティ ID |
| セーブデータ | オブジェクト同士の関係（ポインタは保存できないが、番号なら保存できる） |

<!-- fig:handle-generation:begin -->

<svg class="fig illust motion" data-fig="handle-generation" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-handle-generation" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">ハンドルの世代番号: 古いハンドルで、別の物を触らない</text>
<rect x="150" y="110" width="120" height="70" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
<text x="210.0" y="102" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">スロット 0</text>
<rect x="280" y="110" width="120" height="70" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
<text x="340.0" y="102" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">スロット 1</text>
<rect x="410" y="110" width="120" height="70" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
<text x="470.0" y="102" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">スロット 2</text>
<rect x="540" y="110" width="120" height="70" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
<text x="600.0" y="102" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">スロット 3</text>
<text x="470.0" y="152" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#64748b" opacity="0">空き  世代 1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1933;0.1935;1.0000" values="1;1;0;0"/></text>
<text x="470.0" y="152" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#2ea043" opacity="0">敵 A  世代 1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1933;0.1935;0.3868;0.3871;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470.0" y="152" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#64748b" opacity="0">空き  世代 2<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3868;0.3871;0.5804;0.5806;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470.0" y="152" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#2563eb" opacity="0">敵 B  世代 2<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5804;0.5806;1.0000" values="0;0;1;1"/></text>
<text x="390" y="280" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">（まだ、ハンドルはない）<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1933;0.1935;1.0000" values="1;1;0;0"/></text>
<text x="390" y="280" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">敵 A を作る → ハンドル hA = (スロット 2, 世代 1)<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1933;0.1935;0.3868;0.3871;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="280" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">A を破壊 → スロット 2 の世代が 2 に上がる<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3868;0.3871;0.5804;0.5806;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="280" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">敵 B を作る → スロット 2 を再利用。hB = (2, 世代 2)<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5804;0.5806;0.7739;0.7742;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="280" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">古い hA = (2, 世代 1) で触ろうとする → 世代が違う → 拒否<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.7739;0.7742;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="390" y="330" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#2ea043" opacity="0">世代が一致しないので、B を壊さずに済む<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.7739;0.7742;1.0000" values="0;0;1;1"/></text>
</svg>

<!-- fig:handle-generation:end -->

## よくあるミス

??? failure "世代を付けずに index だけ使う"
    スロットが再利用されたときに、別のオブジェクトを触ってしまいます。

??? failure "Get したポインタを保存する"
    `Get` で取ったポインタは、そのフレームの中で使い切ります。保存するのはハンドルです（プールの vector が伸びるとポインタは壊れるため）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 消えるかもしれない相手はハンドルで覚える
    - [x] ハンドル = index + generation
    - [x] 消すたびに世代を上げ、使うたびに世代を確かめる

## 関連ページ

- [ECS](../design/patterns/ecs.md)
- [リソース管理](resource.md)
- [オブジェクトプール](../design/patterns/object-pool.md)
