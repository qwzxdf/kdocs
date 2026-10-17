---
title: ゲームでよく使うベクトル公式
tags:
  - ゲーム数学
---

# ゲームでよく使うベクトル公式

ベクトルの基本（足し算・長さ・内積・外積）は、[3D：ベクトル](vectors.md)で説明しています。このページはそれらを**ゲームの具体的な場面**に使う形でまとめた**レシピ集**です。「敵が視界に入ったか」「弾が壁で跳ね返る」「プレイヤーが壁に沿って滑る」など、毎回出てくる処理を**式とコード**で並べます。2D と 3D のどちらでも、同じ式が使えます。

!!! tip "ポイント"
    - <strong>方向 ＝ (目標 - 自分) を正規化</strong>。<strong>距離 ＝ その長さ</strong>。
    - <strong>内積</strong>は「どれだけ同じ向きか」。<strong>正なら前、負なら後ろ</strong>。
    - <strong>外積（2D はスカラー）</strong>は「どちら側か」。<strong>符号で左右</strong>。
    - <strong>反射</strong>は<strong>r ＝ v - 2(v・n)n</strong>。<strong>壁ずり</strong>は<strong>v - (v・n)n</strong>。
    - 正規化は<strong>長さ 0 で壊れる</strong>。ゼロベクトルを事前に弾く。
    - 近さの比較は<strong>2 乗のまま</strong>。

## 基本の操作

| 目的 | 式 | コード |
| --- | --- | --- |
| **目標への向きベクトル** | `d = target - self` | `Vector3 d = target - self;` |
| **距離** | `|d|` | `d.Length()` |
| <strong>向きだけ（単位ベクトル）</strong> | `d / |d|` | `d.Normalized()` |
| <strong>近づく（速さ s）</strong> | `pos += d̂ × s × dt` | `pos += dir * speed * dt` |
| **速さの制限** | `v × min(1, max / |v|)` | 下記 |

```cpp
Vector3 ClampLength(Vector3 v, float max_length) {
  float length_sq = v.LengthSquared();
  if (length_sq > max_length * max_length) {
    return v * (max_length / std::sqrt(length_sq));
  }
  return v;
}
```

### ゼロベクトルの正規化

長さ 0 のベクトルを正規化すると、**0 で割って NaN** になります。

```cpp
Vector3 SafeNormalize(Vector3 v, Vector3 fallback) {
  float length_sq = v.LengthSquared();
  if (length_sq < 1e-12f) {
    return fallback;
  }
  return v * (1.0f / std::sqrt(length_sq));
}
```

## 内積の使い方

内積 `a・b = |a||b| cos θ` は、**2 つのベクトルの向きの近さ**です。単位ベクトル同士なら `cos θ` そのものになります。

| 内積の値（単位ベクトル） | 意味 |
| --- | --- |
| **1** | 同じ向き |
| **0** | 垂直（直角） |
| **-1** | 反対向き |
| **正** | 90 度未満（前方・同じ側） |
| **負** | 90 度より大きい（後方・反対側） |

### 視野判定（敵が見えるか）

```cpp
bool InViewCone(Vector3 self, Vector3 forward, Vector3 target, float half_angle, float range) {
  Vector3 to_target = target - self;
  float distance_sq = to_target.LengthSquared();
  if (distance_sq > range * range) {
    return false;
  }
  to_target.Normalize();
  return forward.Dot(to_target) >= std::cos(half_angle);
}
```

| 点 | 説明 |
| --- | --- |
| **`cos(half_angle)` をあらかじめ計算** | 毎回 `acos` で角度を求めず、**内積と cos の比較**で済ませる |
| **forward は単位ベクトル** | 正規化されていないと結果がずれる |
| **距離を先に確認** | 範囲外なら、正規化（`sqrt`）をしないで済む |
| **遮蔽物** | 視野に入っても壁の後ろは見えない。さらに**レイキャスト**で確認 |

### 射影（ベクトルを別のベクトルの方向に落とす）

ベクトル v を単位ベクトル n の方向に射影した成分は `(v・n) n` です。

```cpp
Vector3 Project(Vector3 v, Vector3 n) {
  return n * v.Dot(n);
}
```

| 使いどころ | 説明 |
| --- | --- |
| **点から直線への距離** | 点から直線上の最近接点を求める |
| **斜面に沿った速度** | 重力を斜面方向と垂直方向に分ける |
| **スカラー射影** | `v・n` は、「n 方向への長さ」 |

### 射影を引く（成分を取り除く）

`v - (v・n) n` は、**n の方向の成分を取り除いた**ベクトルです。

```cpp
Vector3 RemoveComponent(Vector3 v, Vector3 n) {
  return v - n * v.Dot(n);
}
```

| 使いどころ | 説明 |
| --- | --- |
| <strong>壁ずり（スライド）</strong> | 壁にぶつかったとき、壁の法線方向の速度を消して、壁に沿って滑る |
| **水平方向の向き** | カメラの向きから、上下成分を取り除いて、**地面と平行な向き**にする |
| **斜面を登る** | 床の法線方向の成分を消す |

## 反射

壁（法線 n）にぶつかった入射ベクトル v が、跳ね返る向きです。

```text
r = v - 2 (v・n) n
```

```cpp
Vector3 Reflect(Vector3 v, Vector3 normal) {
  return v - normal * (2.0f * v.Dot(normal));
}
```

<svg class="fig illust" viewBox="0 0 640 230" role="img" aria-label="反射のベクトル">
<defs><marker id="vr1" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>
<text x="20" y="24" class="fig-title">反射：入射 v が、法線 n の壁で跳ね返る</text>
<line x1="60" y1="180" x2="580" y2="180" stroke="currentColor" stroke-width="5"/>
<line x1="320" y1="180" x2="320" y2="60" stroke="#2ea043" stroke-width="2.5" stroke-dasharray="5 3" marker-end="url(#vr1)"/><text x="328" y="72" style="font-size:12px;fill:#2ea043;font-weight:700">法線 n</text>
<line x1="170" y1="70" x2="316" y2="176" stroke="#e5484d" stroke-width="3" marker-end="url(#vr1)"/><text x="130" y="68" style="font-size:12px;fill:#e5484d;font-weight:700">入射 v</text>
<line x1="324" y1="176" x2="470" y2="70" stroke="#4c8bf5" stroke-width="3" marker-end="url(#vr1)"/><text x="470" y="68" style="font-size:12px;fill:#4c8bf5;font-weight:700">反射 r</text>
<text x="60" y="216" style="font-size:12px">入射角 ＝ 反射角。法線方向の成分だけが反転する</text>
</svg>

| 点 | 説明 |
| --- | --- |
| **法線は単位ベクトル** | 正規化していないと跳ね返る量が狂う |
| **反発係数** | 反射後に法線成分だけ `e` 倍（0〜1）して、エネルギーを失わせる |
| **HLSL にも `reflect`** | `reflect(i, n)`。ライティングの鏡面反射に使う |

```cpp
Vector3 Bounce(Vector3 v, Vector3 normal, float restitution) {
  float vn = v.Dot(normal);
  Vector3 normal_part = normal * vn;
  Vector3 tangent_part = v - normal_part;
  return tangent_part - normal_part * restitution;
}
```

## 外積と「どちら側か」

### 2D：左右の判定

2D の外積は、**スカラー**になります。

```text
cross(a, b) = a.x × b.y - a.y × b.x
```

| 値 | 意味 |
| --- | --- |
| **正** | b は a の**左**（反時計回り側） |
| **負** | b は a の**右** |
| **0** | 同じ直線上（平行） |

```cpp
float Cross2D(Vector2 a, Vector2 b) {
  return a.x * b.y - a.y * b.x;
}

bool IsLeftOf(Vector2 from, Vector2 to, Vector2 point) {
  return Cross2D(to - from, point - from) > 0.0f;
}
```

| 使いどころ | 説明 |
| --- | --- |
| **敵がどちらに旋回するか** | 目標が自分の左なら左へ、右なら右へ |
| **点が多角形の内側か** | 全辺で同じ側にあるか |
| **線分の交差判定** | 各線分の両側に相手の端点があるか |
| <strong>三角形の向き（表裏）</strong> | 頂点順が反時計回りか |
| **面積** | `|cross| / 2` が三角形の面積 |

### 3D：法線と回転軸

3D の外積は**ベクトル**で、**2 つのベクトルに垂直**です。

```cpp
Vector3 normal = (b - a).Cross(c - a).Normalized();
```

| 使いどころ | 説明 |
| --- | --- |
| **三角形の法線** | 2 辺の外積 |
| **カメラの右方向** | `forward × up` |
| **回転軸** | 2 つの向きの間を回す軸 |
| **トルク** | 力と位置から、回す力 |

外積の向き（`a × b` と `b × a` で逆）は、**右手系か左手系か**で変わります（[3D：座標系](coordinate-systems.md)）。

## 垂直なベクトルの作り方

| 場面 | 方法 |
| --- | --- |
| **2D** | `(x, y)` に垂直なのは `(-y, x)`（左回りに 90 度）または `(y, -x)`（右回り） |
| **3D の任意の垂直ベクトル** | 軸のうち、最も垂直に近いものとの外積 |

```cpp
Vector2 Perpendicular(Vector2 v) {
  return Vector2(-v.y, v.x);
}
```

| 使いどころ | 説明 |
| --- | --- |
| <strong>壁・線分の法線（2D）</strong> | 線分の方向を 90 度回す |
| **弾の左右への散らし** | 進行方向に垂直な方向 |
| <strong>横方向の移動（ストレイフ）</strong> | 前方向に垂直な方向 |

## ステアリング（AI の移動）

敵やエージェントを**動かすときの基本パターン**です。**目標の速度**を決め、**現在の速度との差**を**操舵力**にします。

| 行動 | 目標の速度 |
| --- | --- |
| <strong>Seek（追う）</strong> | 目標へ向かう最大速度 |
| <strong>Flee（逃げる）</strong> | 目標から離れる最大速度 |
| <strong>Arrive（到着）</strong> | 近づくほど減速（距離に比例） |
| <strong>Pursuit（先回り）</strong> | 目標の**未来の位置**へ向かう |
| <strong>Wander（うろつく）</strong> | 前方の円周上のランダムな点へ |
| <strong>Avoid（避ける）</strong> | 障害物から離れる向きを足す |
| **Separation・Alignment・Cohesion** | 群れ（Boids）：離れる・向きを合わせる・中心へ寄る |

```cpp
Vector2 Seek(Vector2 position, Vector2 velocity, Vector2 target, float max_speed, float max_force) {
  Vector2 desired = SafeNormalize(target - position, Vector2::Zero) * max_speed;
  Vector2 steer = desired - velocity;
  return ClampLength(steer, max_force);
}

Vector2 Arrive(Vector2 position, Vector2 velocity, Vector2 target, float max_speed, float max_force, float slow_radius) {
  Vector2 to_target = target - position;
  float distance = to_target.Length();
  float speed = distance < slow_radius ? max_speed * (distance / slow_radius) : max_speed;
  Vector2 desired = SafeNormalize(to_target, Vector2::Zero) * speed;
  return ClampLength(desired - velocity, max_force);
}
```

結果の力を**加速度として速度に足し**、速度を位置に足します（[運動](motion.md)）。

## 距離と最近接点

| 目的 | 式 |
| --- | --- |
| **点から直線への最近接点** | 直線上の点 A、方向 d（単位）のとき、`A + d × ((P - A)・d)` |
| **点から線分への最近接点** | 上の `t` を 0〜1 に clamp する |
| **点から平面への距離** | `(P - 平面上の点)・n`（正負で表裏） |

```cpp
Vector2 ClosestPointOnSegment(Vector2 a, Vector2 b, Vector2 p) {
  Vector2 ab = b - a;
  float length_sq = ab.LengthSquared();
  if (length_sq < 1e-12f) {
    return a;
  }
  float t = std::clamp((p - a).Dot(ab) / length_sq, 0.0f, 1.0f);
  return a + ab * t;
}
```

**円とカプセル・線分の判定**にもこの「線分上の最近接点」が使われます（[交差判定](intersection.md)）。

## 3 次元の向き（ビルボード・ルックアット）

| 目的 | 方法 |
| --- | --- |
| <strong>目標を向く（ルックアット）</strong> | forward ＝ 目標への単位ベクトル。right ＝ `up × forward`。up ＝ `forward × right` |
| **水平だけ向く** | 目標へのベクトルから、**上下成分を消して**正規化 |
| **ビルボード** | カメラの right・up をスプライトの軸にする |

## よくあるミス

??? failure "ゼロベクトルを正規化して NaN になる"
    長さを調べて、小さすぎるときは別の値を返します。

??? failure "内積の判定で、片方が正規化されていない"
    両方を単位ベクトルにしてから、`cos` と比較します。

??? failure "反射の法線が、壁の向きでなく、壁に平行になっている"
    法線は**壁に垂直**で**ぶつかった側を向く**ベクトルです。

??? failure "壁ずりの式で、壁の中へ潜り込む"
    速度から、法線方向の**接近成分**（`v・n < 0` のとき）だけを消します。

??? failure "距離の比較で、毎回 `Length()` を使う"
    `LengthSquared()` と、2 乗した値を比べます。

??? failure "2D の外積の正負（左右）が、画面で逆に見える"
    画面の Y が下向きの座標系では、左右が逆になります。符号を確認します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 方向 ＝ <strong>(目標 - 自分) を正規化</strong>。<strong>ゼロベクトルは事前に弾く</strong>
    - [x] <strong>内積</strong>：前後・視野判定（<strong>`dot ≥ cos(半角)`</strong>）・射影
    - [x] <strong>外積</strong>：左右（2D）・法線（3D）・面積
    - [x] <strong>反射 ＝ v - 2(v・n)n</strong>。<strong>壁ずり ＝ v - (v・n)n</strong>
    - [x] <strong>ステアリング ＝ 目標の速度 - 現在の速度</strong>。力を制限する
    - [x] 近さの比較は<strong>2 乗のまま</strong>

## 関連ページ

- [ゲーム数学](index.md)
- [三角関数と角度](trigonometry.md)
- [交差判定の公式集](intersection.md)
- [運動と物理の数学](motion.md)
- [3D：ベクトル](vectors.md)
