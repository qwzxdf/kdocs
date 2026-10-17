---
title: ベクトル
tags:
  - 3Dゲーム
---

# ベクトル

**ベクトル**は、「**向き**と**大きさ**を持つ量」です。3D ゲームでは、**位置**、**移動の速さと向き**、**カメラの向き**、<strong>面の向き（法線）</strong>、**光の向き**など、あらゆるものをベクトルで表します。`(x, y, z)` の 3 つの数字の組で、コードでは [SimpleMath](simplemath.md) の `Vector3` です。ベクトルの計算の中で、ゲームで特によく使うのが、**正規化、内積、外積**の 3 つです。それぞれ「何を調べる道具か」を理解すると、当たり判定、視界、反射、回転の計算が、自然に書けるようになります。

!!! tip "ポイント"
    - <strong>位置</strong>も<strong>向き</strong>も、同じ `(x, y, z)` で表す。<strong>意味が違う</strong>ので、混ぜない。
    - <strong>正規化</strong>（長さ 1 にする）で、<strong>向きだけ</strong>を取り出す。
    - <strong>内積</strong>は「<strong>どれくらい同じ向きか</strong>」。<strong>視界（前にいるか）、明るさ、射影</strong>に使う。
    - <strong>外積</strong>は「<strong>2 つに垂直なベクトル</strong>」。<strong>法線、回転軸、左右の判定</strong>に使う。
    - <strong>長さの比較は、2 乗のまま</strong>（`sqrt` を避ける）。速い。

## 基本 {#basics}

| 計算 | 式 | 意味 |
| --- | --- | --- |
| **足し算** | `a + b` | 移動の合成。「a の後に b」 |
| **引き算** | `a - b` | **b から a へ向かう**ベクトル（b の位置から a の位置へ） |
| **スカラー倍** | `a * k` | 長さを k 倍（向きは同じ。k が負なら逆向き） |
| **長さ** | `‖a‖ = sqrt(x² + y² + z²)` | ベクトルの大きさ |
| **正規化** | `a / ‖a‖` | 長さを 1 にする（向きだけ） |
| **距離** | `‖a - b‖` | 2 点間の距離 |

```cpp
#include <SimpleMath.h>
using namespace DirectX::SimpleMath;

Vector3 player(1.0f, 0.0f, 2.0f);
Vector3 enemy(4.0f, 0.0f, 6.0f);

Vector3 to_enemy = enemy - player;          // プレイヤーから敵へ向かうベクトル
float distance = to_enemy.Length();          // 距離（5.0）
Vector3 direction = to_enemy;
direction.Normalize();                        // 向きだけ（長さ 1）に、その場で変える

// 敵に向かって、速さ 3 で、dt 秒だけ進む
player += direction * (3.0f * dt);
```

### 位置と方向を混ぜない {#position-direction}

| 種類 | 意味 | 変換での扱い（同次座標） |
| --- | --- | --- |
| <strong>位置（点）</strong> | 空間の中の「場所」 | w = 1。**平行移動の影響を受ける**。`Vector3::Transform(v, M)` |
| <strong>方向（ベクトル）</strong> | 向きと大きさ。場所を持たない | w = 0。**平行移動の影響を受けない**。`Vector3::TransformNormal(v, M)` |

「敵の位置」は点、「前方向」は方向です。行列で変換するとき、点は平行移動される、方向は回転だけされる、という違いが出ます（[行列](matrices.md)）。

## 正規化 {#normalize}

<svg class="fig" viewBox="0 0 560 220" role="img" aria-label="正規化の図"><defs><marker id="v3" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs><text x="20" y="20" class="fig-title">正規化：向きはそのまま、長さを 1 にする</text><circle cx="140" cy="160" r="50" fill="none" stroke="currentColor" stroke-dasharray="4 4"/><text x="60" y="220">半径 1 の円</text><line x1="140" y1="160" x2="310" y2="60" stroke="currentColor" stroke-width="2" marker-end="url(#v3)" /><text x="250" y="58">v（長さ 3）</text><line x1="140" y1="160" x2="176" y2="139" stroke="currentColor" stroke-width="4" marker-end="url(#v3)" /><text x="180" y="150"></text><text x="188" y="132">v̂（長さ 1）</text><text x="340" y="100">v̂ ＝ v ÷ |v|</text><text x="340" y="128">向きだけが欲しいとき（方向・移動の向き）</text><text x="340" y="156">ゼロベクトルは割れない（長さ 0 に注意）</text></svg>

**向きだけ**が欲しいときは、長さ 1 に正規化します。

```cpp
Vector3 forward = target - position;
forward.Normalize();                          // その場で正規化

Vector3 n;
(target - position).Normalize(n);             // 結果を、別の変数に受ける
```

| 注意 | 説明 |
| --- | --- |
| **長さ 0 のベクトルは、正規化できない** | 0 で割るので、NaN になる（SimpleMath は、長さ 0 のときは、そのままにする）。事前に、長さを確認する |
| **正規化したベクトルは、長さ 1** | 速さを掛けて使う（`direction * speed`） |
| **移動のとき、斜め移動が速くなる** | `(1, 1)` の長さは 1.41。入力ベクトルを正規化してから、速さを掛ける |
| **毎回の正規化は、少し重い** | `sqrt` と割り算。向きが変わらないなら、キャッシュする |

## 内積（ドット積） {#dot}

<svg class="fig" viewBox="0 0 620 230" role="img" aria-label="内積の図"><defs><marker id="v1" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs><text x="20" y="20" class="fig-title">内積：2 つの向きが、どれだけ揃っているか</text><line x1="60" y1="140" x2="200" y2="140" stroke="currentColor" stroke-width="2" marker-end="url(#v1)" /><text x="205" y="144">a</text><line x1="60" y1="140" x2="140" y2="70" stroke="currentColor" stroke-width="2" marker-end="url(#v1)" /><text x="140" y="62">b</text><path d="M 100 140 A 40 40 0 0 0 92 118" fill="none" stroke="currentColor"/><text x="100" y="128">θ</text><line x1="140" y1="70" x2="140" y2="140" stroke="currentColor" stroke-dasharray="4 4"/><line x1="60" y1="152" x2="140" y2="152" stroke="currentColor" stroke-width="4"/><text x="70" y="172">b を a に落とした長さ</text><text x="60" y="200">a · b ＝ |a| |b| cosθ（正規化していれば cosθ）</text><text x="330" y="60" class="fig-title">正：同じ向き（前方）</text><line x1="350" y1="110" x2="420" y2="110" stroke="currentColor" stroke-width="2" marker-end="url(#v1)" /><line x1="350" y1="110" x2="410" y2="80" stroke="currentColor" stroke-width="2" marker-end="url(#v1)" /><text x="430" y="114">cos > 0</text><text x="330" y="150" class="fig-title">0：直角</text><line x1="350" y1="195" x2="420" y2="195" stroke="currentColor" stroke-width="2" marker-end="url(#v1)" /><line x1="350" y1="195" x2="350" y2="150" stroke="currentColor" stroke-width="2" marker-end="url(#v1)" /><text x="430" y="199">cos = 0</text><text x="500" y="60" class="fig-title">負：逆向き（後方）</text><line x1="560" y1="110" x2="500" y2="110" stroke="currentColor" stroke-width="2" marker-end="url(#v1)" /><line x1="520" y1="110" x2="570" y2="80" stroke="currentColor" stroke-width="2" marker-end="url(#v1)" /><text x="500" y="130">cos < 0</text></svg>

**内積**は、2 つのベクトルが**どれくらい同じ向きを向いているか**を、1 つの数字で表します。

```text
a · b = ax*bx + ay*by + az*bz = ‖a‖ ‖b‖ cos θ
```

2 つが**正規化されている**なら、`a · b = cos θ`（θ は 2 つの間の角度）です。

| 内積の値（正規化済み） | 角度 | 意味 |
| --- | --- | --- |
| **1** | 0° | 完全に同じ向き |
| **0** | 90° | 直角（無関係） |
| **−1** | 180° | 完全に逆向き |
| 正 | 90° 未満 | だいたい同じ向き |
| 負 | 90° より大 | だいたい逆向き |

```cpp
float dot = a.Dot(b);
```

### 内積の使いどころ

| 用途 | 使い方 |
| --- | --- |
| **前にいるか・後ろにいるか** | `前方向.Dot(敵への方向) > 0` なら、敵は前方にいる |
| **視野角（扇形）の判定** | `前方向.Dot(敵への方向) > cos(視野角 / 2)` なら、視野の中（敵を発見） |
| <strong>明るさ（ライティング）</strong> | `max(法線.Dot(光への方向), 0)`（[ライティング](lighting-normals.md)） |
| **射影**（あるベクトルを、別のベクトルに落とす） | `b * a.Dot(b)`（b が正規化済みのとき）。壁に沿った移動 |
| **平面からの距離** | `(点 - 平面上の点).Dot(法線)`（正なら表側、負なら裏側） |
| **向きの近さの比較** | 角度を求めずに、内積の大小で比べる（`acos` は重い） |

```cpp
// 視野の判定：敵が、前方の扇形（左右に half_angle ずつ）にいるか
bool InFieldOfView(const Vector3& self_forward, const Vector3& self_pos,
                   const Vector3& target_pos, float half_angle) {
  Vector3 to_target = target_pos - self_pos;
  to_target.Normalize();
  return self_forward.Dot(to_target) > std::cos(half_angle);   // acos を使わず、cos と比べる
}
```

### 角度を求める

```cpp
float angle = std::acos(std::clamp(a.Dot(b), -1.0f, 1.0f));   // ラジアン。誤差で範囲外にならないよう clamp
```

`acos` は重いので、**角度が必要なときだけ**使います。判定だけなら、内積のまま比べます。

## 外積（クロス積） {#cross}

<svg class="fig" viewBox="0 0 560 230" role="img" aria-label="外積の図"><defs><marker id="v2" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs><text x="20" y="20" class="fig-title">外積：2 つのベクトルに、垂直なベクトル</text><polygon points="60,190 260,190 320,130 120,130" fill="rgba(76,139,245,0.2)" stroke="currentColor"/><line x1="150" y1="165" x2="250" y2="165" stroke="currentColor" stroke-width="2" marker-end="url(#v2)" /><text x="255" y="170">a</text><line x1="150" y1="165" x2="200" y2="135" stroke="currentColor" stroke-width="2" marker-end="url(#v2)" /><text x="204" y="132">b</text><line x1="150" y1="165" x2="150" y2="55" stroke="currentColor" stroke-width="3" marker-end="url(#v2)" /><text x="158" y="60">a × b（面に垂直）</text><text x="340" y="80">右手系：a から b へ、右手の指を</text><text x="340" y="100">曲げたとき、親指の向き</text><text x="340" y="140">順番を逆にすると（b × a）</text><text x="340" y="160">向きが逆になる</text><text x="340" y="195" class="fig-title">使いどころ：面の法線、左右の判定</text></svg>

**外積**は、2 つのベクトルの**両方に垂直な**ベクトルを作ります。

```text
a × b = (ay*bz - az*by,  az*bx - ax*bz,  ax*by - ay*bx)
```

| 性質 | 説明 |
| --- | --- |
| **結果は、a と b の両方に垂直** | 面の法線、回転軸に使える |
| **長さは `‖a‖ ‖b‖ sin θ`** | 2 つの作る平行四辺形の面積 |
| **順序で、向きが逆**（`a × b = −(b × a)`） | 右手系と左手系で、向きが逆になる（[座標系](coordinate-systems.md)） |
| **同じ向きなら、ゼロ** | 平行な 2 つの外積は 0 |

```cpp
Vector3 normal = edge1.Cross(edge2);     // 三角形の法線（正規化して使う）
```

### 外積の使いどころ

| 用途 | 使い方 |
| --- | --- |
| **三角形の法線** | `(頂点1 - 頂点0).Cross(頂点2 - 頂点0)`（正規化する） |
| **右方向を求める** | `前方向.Cross(上方向)` で、右方向（右手系）。カメラの 3 軸を作る |
| **回転軸** | `今の向き.Cross(目標の向き)` が、回転軸。内積が回転角の `cos` |
| **左右の判定**（2D） | 外積の Y 成分の符号で、目標が、左にあるか右にあるか |
| **面積** | 三角形の面積 ＝ `edge1.Cross(edge2).Length() / 2` |
| <strong>トルク（物理）</strong> | `腕.Cross(力)` |

```cpp
// 右手系・Y-up：前方向 × 上方向 ＝ 右方向
Vector3 right = Vector3::Forward.Cross(Vector3::Up);   // (0,0,-1) × (0,1,0) = (1,0,0)
```

右手系では、`前 × 上 = 右` になります（左手系では、結果が逆向きです）。

## 反射と射影 {#reflect}

<svg class="fig" viewBox="0 0 560 230" role="img" aria-label="反射の図"><defs><marker id="v4" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs><text x="20" y="20" class="fig-title">反射：壁に当たって跳ね返る向き</text><line x1="40" y1="180" x2="320" y2="180" stroke="currentColor" stroke-width="3"/><text x="330" y="184">壁</text><line x1="180" y1="180" x2="180" y2="90" stroke="currentColor" stroke-width="2" marker-end="url(#v4)" /><text x="188" y="98">n（法線）</text><line x1="70" y1="80" x2="176" y2="176" stroke="currentColor" stroke-width="3" marker-end="url(#v4)" /><text x="40" y="70">v（入る向き）</text><line x1="184" y1="176" x2="290" y2="80" stroke="currentColor" stroke-width="3" marker-end="url(#v4)" /><text x="250" y="70">r（反射した向き）</text><text x="340" y="100">r ＝ v − 2 (v · n) n</text><text x="340" y="128">入射角と、反射角が等しい</text></svg>

| 計算 | 式（`n` は正規化した法線） | 使いどころ |
| --- | --- | --- |
| **反射** | `r = v − 2 (v · n) n` | 壁で跳ね返る弾、鏡面反射 |
| **射影**（`n` 方向の成分） | `(v · n) n` | 斜面に沿った速度の成分 |
| **平面への射影**（`n` 方向の成分を引く） | `v − (v · n) n` | 壁に沿って滑る（壁ずり） |

```cpp
// 反射ベクトル
Vector3 reflected = Vector3::Reflect(velocity, wall_normal);

// 壁ずり：壁の法線方向の成分を引く
Vector3 slide = velocity - wall_normal * velocity.Dot(wall_normal);
```

## 補間 {#lerp}

<svg class="fig" viewBox="0 0 560 200" role="img" aria-label="線形補間の図"><defs><marker id="v5" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs><text x="20" y="20" class="fig-title">線形補間：a から b へ、t の割合だけ進む</text><line x1="60" y1="110" x2="480" y2="110" stroke="currentColor" stroke-width="2"/><circle cx="60" cy="110" r="6" fill="currentColor"/><text x="48" y="138">t=0</text><circle cx="165" cy="110" r="6" fill="currentColor"/><text x="153" y="138">t=0.25</text><circle cx="270" cy="110" r="6" fill="currentColor"/><text x="258" y="138">t=0.5</text><circle cx="480" cy="110" r="6" fill="currentColor"/><text x="468" y="138">t=1</text><text x="60" y="90">a</text><text x="470" y="90">b</text><text x="60" y="175">Lerp(a, b, t) ＝ a ＋ (b − a) × t　　t を 0 → 1 に動かすと、なめらかに移動する</text></svg>

| 方法 | 式 | 使いどころ |
| --- | --- | --- |
| <strong>線形補間（lerp）</strong> | `a + (b - a) * t`（t は 0〜1） | 位置・色・値のなめらかな変化 |
| <strong>正規化付き線形補間（nlerp）</strong> | lerp してから正規化 | 向きの簡易補間（速いが、速度が一定にならない） |
| <strong>球面線形補間（slerp）</strong> | 球面上を一定の速さで | 向き（クォータニオン）の補間（[回転](rotation.md)） |

```cpp
Vector3 p = Vector3::Lerp(a, b, t);   // 位置の補間
```

`t` を、毎フレーム少しずつ増やすと、アニメーションになります。**`Lerp(current, target, 0.1f)` を毎フレーム呼ぶ**と、ターゲットに指数的に近づく（カメラの追従で定番。ただしフレームレートに依存するので、`1 - exp(-k * dt)` を `t` に使うのがより正確です）。

## 要素ごとの演算（Min / Max / Clamp） {#componentwise}

`Min`・`Max`・`Clamp` は、ベクトルの **x、y、z を、別々に**計算します（**要素ごと**）。長さや向きで比べるのではありません。

```cpp
Vector3 a(1, 5, 3);
Vector3 b(4, 2, 6);

Vector3 lo = Vector3::Min(a, b);          // (1, 2, 3)  各成分の小さい方
Vector3 hi = Vector3::Max(a, b);          // (4, 5, 6)  各成分の大きい方
Vector3 c = Vector3::Clamp(a, Vector3(0, 0, 0), Vector3(3, 3, 3));   // (1, 3, 3)  各成分を範囲に収める
```

| 使いどころ | 例 |
| --- | --- |
| **箱（AABB）の範囲を求める** | 全頂点の `Min` と `Max` が、箱の両端になる（[3D の衝突判定](collision-3d.md)） |
| **位置を、範囲内に収める** | `Clamp(position, world_min, world_max)` で、マップの外に出さない |
| **色の範囲を収める** | `Clamp(color, 0, 1)` |

## 長さの比較は 2 乗で {#distance}

距離を**比べるだけ**なら、`sqrt` を避けて、**2 乗のまま**比べます。

```cpp
// 遅い：sqrt が入る
if (Vector3::Distance(a, b) < 5.0f) { ... }

// 速い：2 乗のまま比べる（5 の 2 乗は 25）
if (Vector3::DistanceSquared(a, b) < 5.0f * 5.0f) { ... }
```

当たり判定や、範囲判定のように、**何度も呼ぶ**場所では、効果があります（[アルゴリズムとデータ構造](../optimize/algorithms.md)）。

## 浮動小数点の誤差

| 注意 | 説明 |
| --- | --- |
| **`==` で比べない** | `1.0f` と `0.1f * 10` が、ちょうど等しいとは限らない。<strong>差が小さい（イプシロン以内）</strong>かで判定 |
| **長さ 0 の正規化** | NaN が出る（または、そのまま）。長さを確認 |
| **正規化し直す** | 計算を重ねると、長さが 1 からずれる。回転ベクトル・クォータニオンは、ときどき正規化する |
| **大きな座標で精度が落ちる** | `float` は、原点から遠いほど、粗くなる。広い世界では、原点を動かす（フローティング オリジン）か、`double` |

## ゲームでの使いどころ

| 場面 | 計算 |
| --- | --- |
| 敵が、プレイヤーを追いかける | `normalize(player - enemy) * speed * dt` |
| 敵の視界 | 内積と視野角の `cos`（＋距離は 2 乗比較）＋レイキャスト |
| 壁にぶつかって、滑る | 壁の法線方向の成分を引く |
| 弾が壁で跳ね返る | 反射ベクトル |
| 斜面の向きに、キャラを合わせる | 法線から、外積で右方向を作る |
| カメラの右・上・前方向 | 外積で、互いに垂直な 3 方向を作る |
| 範囲内の敵を探す | 距離の 2 乗の比較 |

## よくあるミス

??? failure "位置と方向を、同じ扱いにする"
    点（位置）を方向のように、平行移動なしで変換すると、位置がずれます。方向を点のように変換すると、向きが狂います。`Transform`（位置）と `TransformNormal`（方向）を使い分けます。

??? failure "正規化していないベクトルで、内積を `cos` として使う"
    内積が `cos θ` になるのは、**両方が長さ 1** のときだけです。長さがあると、値が大きくなり、判定がずれます。

??? failure "長さ 0 のベクトルを正規化して、NaN になる"
    停止中の速度、同じ位置の 2 点の差などで起きます。NaN は、ほかの値にも伝染し、画面が消えます。事前に長さを確認します。

??? failure "斜め移動が、速い"
    `(1, 0)` と `(1, 1)` で、長さが違います。入力を正規化してから、速さを掛けます。

??? failure "外積の順序を逆にして、法線が裏向きになる"
    `a.Cross(b)` と `b.Cross(a)` は、逆向きです。座標系（右手 / 左手）でも向きが変わります。結果を見て、反転する必要があります。

??? failure "`Normalize()` の戻り値を使おうとする"
    SimpleMath の `Normalize()` は、その場で書き換え、戻り値はありません。別の変数に受けるなら、`v.Normalize(result)` です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>正規化</strong> ＝ 向きだけ。長さ 0 に注意。斜め移動は<strong>正規化してから</strong>速さを掛ける
    - [x] <strong>内積</strong> ＝ 同じ向きの度合い（正規化すれば `cos`）。<strong>前後・視野・明るさ・射影</strong>
    - [x] <strong>外積</strong> ＝ 両方に垂直なベクトル。<strong>法線・右方向・回転軸</strong>
    - [x] <strong>位置は `Transform`、方向は `TransformNormal`</strong>。混ぜない
    - [x] 距離の比較は<strong>2 乗のまま</strong>。`==` で比べず、誤差を考える

## 関連ページ

- [3D ゲーム（目次）](index.md)
- [SimpleMath](simplemath.md)
- [座標系](coordinate-systems.md)
- [行列](matrices.md)
- [法線とライティング](lighting-normals.md)
