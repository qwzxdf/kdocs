---
title: 三角関数と角度
tags:
  - ゲーム数学
---

# 三角関数と角度

ゲームで円運動・方向・揺れ・波・扇形の範囲を扱うとき、**sin・cos・atan2** と**ラジアン**は避けて通れません。このページでは、**単位円**というイメージを軸にして、ゲームでよく使う形に絞って説明します。式の証明は書きません。「何を入れると何が出るか」「どこで間違えるか」が中心です。

!!! tip "ポイント"
    - C++ の三角関数は<strong>ラジアン</strong>で受け取る。度のまま渡さない。
    - <strong>cos が x、sin が y</strong>。単位円の上の点 <strong>(cos θ, sin θ)</strong>。
    - 方向 → 角度は<strong>`atan2(y, x)`</strong>。`atan(y / x)` は使わない。
    - 角度は<strong>-π〜π、または 0〜2π に正規化</strong>して扱う。
    - <strong>角度の差</strong>は、そのまま引かない。<strong>最短の回り方</strong>に直す。
    - 距離の比較は、<strong>平方根を取らず、2 乗のまま</strong>比べる。

## ラジアンと度

**ラジアン**は円の半径と同じ長さの弧に対応する角度です。180 度が π ラジアンです。

| 度 | ラジアン | 意味 |
| --- | --- | --- |
| **0°** | 0 | 右（+x） |
| **90°** | π / 2 | 上（+y） |
| **180°** | π | 左（-x） |
| **270°** | 3π / 2 | 下（-y） |
| **360°** | 2π | 1 周 |

```cpp
constexpr float kPi = std::numbers::pi_v<float>;
constexpr float kDegToRad = kPi / 180.0f;
constexpr float kRadToDeg = 180.0f / kPi;
```

| 点 | 説明 |
| --- | --- |
| **`std::numbers::pi_v<float>`** | C++20 で追加された円周率の定数（`<numbers>`） |
| **度とラジアンの変換** | `度 × π / 180 = ラジアン` |
| **ゲームの設定画面や FOV は度** | 人間に見せる値は度、計算はラジアン、と分けると混乱しない |
| **`<cmath>` の関数はラジアン** | `std::sin(90.0f)` は、90 ラジアンの sin（意図した値にならない） |

## 単位円と sin・cos

半径 1 の円（**単位円**）の上で角度 θ の位置にある点の座標が <strong>(cos θ, sin θ)</strong> です。

<svg class="fig illust" viewBox="0 0 710 300" role="img" aria-label="単位円と sin・cos">
<defs><marker id="tr1" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>
<text x="20" y="24" class="fig-title">単位円：角度 θ の点は (cos θ, sin θ)</text>
<line x1="60" y1="160" x2="360" y2="160" stroke="currentColor" stroke-width="1.5" marker-end="url(#tr1)"/>
<line x1="210" y1="290" x2="210" y2="40" stroke="currentColor" stroke-width="1.5" marker-end="url(#tr1)"/>
<text x="364" y="164" style="font-size:12px">x</text><text x="214" y="46" style="font-size:12px">y</text>
<circle cx="210" cy="160" r="100" fill="rgba(76,139,245,0.12)" stroke="currentColor" stroke-width="2"/>
<line x1="210" y1="160" x2="281" y2="89" stroke="#e5484d" stroke-width="3"/>
<circle cx="281" cy="89" r="6" fill="#e5484d"/>
<line x1="281" y1="89" x2="281" y2="160" stroke="#2ea043" stroke-width="2.5" stroke-dasharray="5 3"/>
<line x1="210" y1="160" x2="281" y2="160" stroke="#4c8bf5" stroke-width="2.5"/>
<path d="M240,160 A30,30 0 0 0 231,139" fill="none" stroke="currentColor" stroke-width="1.5"/>
<text x="244" y="150" style="font-size:12px">θ</text>
<text x="296" y="94" style="font-size:12px">(cos θ, sin θ)</text>
<text x="226" y="178" style="font-size:12px;fill:#4c8bf5;font-weight:700">cos θ</text>
<text x="286" y="130" style="font-size:12px;fill:#2ea043;font-weight:700">sin θ</text>
<text x="420" y="80" style="font-weight:700">覚えること</text>
<text x="420" y="106" style="font-size:13px">cos θ ＝ 横（x）の長さ</text>
<text x="420" y="128" style="font-size:13px">sin θ ＝ 縦（y）の長さ</text>
<text x="420" y="160" style="font-size:13px">θ = 0 → (1, 0) 右</text>
<text x="420" y="182" style="font-size:13px">θ = π/2 → (0, 1) 上</text>
<text x="420" y="204" style="font-size:13px">θ = π → (-1, 0) 左</text>
<text x="420" y="236" style="font-size:12px">半径が r なら、全部 r 倍：(r cos θ, r sin θ)</text>
</svg>

### ゲームでの使い方

| 使い方 | 式 |
| --- | --- |
| **角度から方向ベクトル** | `direction = (cos θ, sin θ)` |
| **円運動** | `position = center + radius × (cos ωt, sin ωt)` |
| **扇状に弾を撃つ** | 基準の角度に `i × 間隔` を足して、`(cos, sin)` を速度にする |
| **上下に揺れる** | `y = base + amplitude × sin(ωt)` |
| **点滅・呼吸** | `alpha = 0.5 + 0.5 × sin(ωt)`（0〜1 に収める） |

```cpp
Vector2 DirectionFromAngle(float radians) {
  return Vector2(std::cos(radians), std::sin(radians));
}

Vector2 OnCircle(Vector2 center, float radius, float angular_speed, float time) {
  float a = angular_speed * time;
  return center + Vector2(std::cos(a), std::sin(a)) * radius;
}
```

### sin 波のパラメータ

`y = A × sin(ω t + φ) + C` の 4 つで波の形が決まります。

| 記号 | 名前 | 意味 |
| --- | --- | --- |
| **A** | 振幅 | 揺れの大きさ |
| **ω** | 角周波数 | 速さ。`2π × 周波数`（周波数は 1 秒あたりの往復回数） |
| **φ** | 位相 | ずらし（複数の物体をずらして揺らす） |
| **C** | 中心 | 揺れの中心の高さ |

**周期 T（秒）が決まっているなら、ω = 2π / T**です。

## atan2：方向を角度にする

**ベクトル (x, y) の向きの角度**を求めるのが `atan2(y, x)` です。**引数の順番が y, x** である点に注意します。

```cpp
float angle = std::atan2(target.y - self.y, target.x - self.x);
```

| 点 | 説明 |
| --- | --- |
| **戻り値の範囲** | -π 〜 π（-180° 〜 180°） |
| **`atan(y / x)` を使わない** | x が 0 のとき割り算で壊れる。象限（どの方向か）が分からなくなる |
| <strong>引数の順番は (y, x)</strong> | (x, y) と逆に書きやすい |
| **3D の場合** | 水平面の向きは `atan2(dz, dx)`（XZ 平面）。仰角は `atan2(dy, 水平距離)` |
| **2D の回転の向き** | 数学では反時計回りが正。画面の Y が下向きだと、見た目が逆になる |

## 角度の扱い

### 正規化

角度は何周でも足せてしまうので、**範囲を決めて扱います**。

```cpp
float WrapAngle(float radians) {
  constexpr float kTwoPi = 2.0f * std::numbers::pi_v<float>;
  radians = std::fmod(radians + std::numbers::pi_v<float>, kTwoPi);
  if (radians < 0.0f) {
    radians += kTwoPi;
  }
  return radians - std::numbers::pi_v<float>;
}
```

| 点 | 説明 |
| --- | --- |
| **範囲を決める** | -π〜π、または 0〜2π |
| **`fmod` は負の数に注意** | 結果が負になるので`+ 2π` で補正する |
| **`%` は整数だけ** | 浮動小数点では `std::fmod` |

### 角度の差（最短の回り方）

角度 350° から 10° へ向きを変えるとき、`10 - 350 = -340` と引くと、**340° 逆回り**になってしまいます。**最短は +20°** です。

```cpp
float AngleDifference(float from, float to) {
  return WrapAngle(to - from);
}

float RotateToward(float current, float target, float max_step) {
  float diff = AngleDifference(current, target);
  diff = std::clamp(diff, -max_step, max_step);
  return current + diff;
}
```

| 使いどころ | 説明 |
| --- | --- |
| **敵がプレイヤーへ向く** | 目標の角度へ、1 フレームに `max_step` だけ回す（急に振り向かない） |
| **砲台の旋回** | 同じ。回転速度を制限する |
| **向きの補間** | 角度の `lerp` も同じく最短の差を使う |

## 2D の回転

ベクトル (x, y) を、角度 θ だけ**反時計回りに回転**させる式です。

```text
x' = x cos θ - y sin θ
y' = x sin θ + y cos θ
```

```cpp
Vector2 Rotate(Vector2 v, float radians) {
  float c = std::cos(radians);
  float s = std::sin(radians);
  return Vector2(v.x * c - v.y * s, v.x * s + v.y * c);
}
```

| 使いどころ | 説明 |
| --- | --- |
| **弾の拡散** | 正面の方向を少しずつ回して複数発 |
| **視野の端の方向** | 正面を ±half_fov だけ回す |
| **敵の周りを回る** | 相対位置を回す |

`cos` と `sin` を**毎回計算せず**、同じ角度を何度も使うなら、**先に 1 回だけ計算して使い回す**と速くなります。

## 逆三角関数

| 関数 | 入力 | 出力 | 使いどころ |
| --- | --- | --- | --- |
| **`asin(x)`** | -1〜1 | -π/2〜π/2 | 高さから角度（斜面の角度など） |
| **`acos(x)`** | -1〜1 | 0〜π | **内積から、2 つのベクトルの間の角度** |
| **`atan2(y, x)`** | 任意 | -π〜π | 方向の角度 |

```cpp
float AngleBetween(Vector2 a, Vector2 b) {
  float d = a.Dot(b) / (a.Length() * b.Length());
  return std::acos(std::clamp(d, -1.0f, 1.0f));
}
```

!!! warning "acos の引数は、必ず clamp する"
    浮動小数点の誤差で内積が 1.0000001 のような値になると、`acos` が **NaN** を返します。`std::clamp(d, -1.0f, 1.0f)` で、範囲に収めてから渡します（[数値の注意](numeric.md)）。

## 距離と「2 乗のまま比べる」

2 点の距離は、**ピタゴラスの定理**（`√(dx² + dy²)`）で求めます。

```cpp
float distance = std::sqrt(dx * dx + dy * dy);
```

`sqrt`（平方根）は、足し算・掛け算に比べると**重い**ので、**距離を比べるだけ**なら 2 乗のまま比較します。

```cpp
bool InRange(Vector2 a, Vector2 b, float range) {
  Vector2 d = b - a;
  return d.x * d.x + d.y * d.y <= range * range;
}
```

| 点 | 説明 |
| --- | --- |
| <strong>「射程内か」は 2 乗で</strong> | `距離 <= 射程` は `距離² <= 射程²` と同じ |
| <strong>「どちらが近いか」も 2 乗で</strong> | 大小の順序は、2 乗しても変わらない |
| **実際の距離が必要なときだけ `sqrt`** | ダメージの距離減衰など |
| **DirectXMath** | `XMVector3LengthSq` や、SimpleMath の `LengthSquared()` |

## 三角関数のコスト

| 点 | 説明 |
| --- | --- |
| **`sin`・`cos` は重め** | 数万回なら問題ないが毎フレーム数十万回は重い |
| <strong>`sincos`（同時計算）</strong> | `sin` と `cos` を同時に出す関数は、別々に呼ぶより速いことが多い |
| **テーブル・近似式** | 精度が低くてよいなら、テーブル引きや多項式の近似 |
| **SIMD** | DirectXMath の `XMVectorSinCos` などで、まとめて計算 |

## よくあるミス

??? failure "度のまま `std::sin` に渡す"
    ラジアンに変換します（`度 × π / 180`）。

??? failure "`atan2(x, y)` と、引数の順番を逆にする"
    <strong>(y, x)</strong> の順です。

??? failure "角度の差を、引き算だけで求めて、遠回りする"
    `WrapAngle(to - from)` で、最短の差にします。

??? failure "`acos` に 1.0000001 を渡して NaN になる"
    `clamp` で-1〜1 に収めます。

??? failure "距離の比較で、毎回 `sqrt` を呼ぶ"
    2 乗のまま比べます。

??? failure "画面の Y が下向きで、回転が逆になる"
    2D の画面座標は Y が下向きなので、数学の反時計回りが画面では時計回りに見えます。符号を意識します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>ラジアンが基本</strong>。度は人間に見せる値だけ
    - [x] <strong>(cos θ, sin θ)</strong> が、角度 θ の方向。半径をかければ円運動
    - [x] <strong>`atan2(y, x)`</strong> で、方向を角度に。<strong>(y, x) の順</strong>
    - [x] 角度は<strong>正規化</strong>し、差は<strong>最短の回り方</strong>で
    - [x] <strong>`acos` の引数は clamp</strong>
    - [x] 距離の比較は<strong>2 乗のまま</strong>

## 関連ページ

- [ゲーム数学](index.md)
- [補間（lerp）](interpolation.md)
- [ゲームでよく使うベクトル公式](vector-recipes.md)
- [浮動小数点と数値の注意](numeric.md)
- [3D：ベクトル](vectors.md)
- [3D：回転](rotation.md)
