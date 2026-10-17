---
title: 補間（lerp）
tags:
  - ゲーム数学
---

# 補間（lerp）

**補間**は、2 つの値の**間をなめらかにつなぐ**計算です。ゲームでは移動・色の変化・UI のアニメーション・カメラの追従・音量の変化など、あらゆる場面に出てきます。その中心にあるのが<strong>線形補間（lerp）</strong>です。式は一行ですが**使い方のバリエーション**（逆補間・リマップ・時間に依存しない補間など）を知っているかどうかで、書けるコードが大きく変わります。

!!! tip "ポイント"
    - <strong>lerp(a, b, t) ＝ a + (b - a) × t</strong>。t が 0 なら a、1 なら b。
    - <strong>t は 0〜1 の割合</strong>。範囲外にしたくなければ <strong>clamp</strong> する。
    - 逆の操作は<strong>逆補間（inverse lerp）</strong>。<strong>範囲を別の範囲へ写す</strong>のが<strong>リマップ</strong>。
    - <strong>`lerp(current, target, 0.1f)` を毎フレーム</strong>書く方法は、<strong>フレームレートで挙動が変わる</strong>。<strong>指数減衰</strong>で直す。
    - 滑らかな切り替えには<strong>smoothstep</strong>。もっと自由な形は[イージング](easing.md)。
    - 回転は<strong>slerp</strong>、色は<strong>線形空間で</strong>補間する。

## 線形補間（lerp）

2 つの値 a と b の間を、割合 t で混ぜます。

```text
lerp(a, b, t) = a + (b - a) × t
```

<svg class="fig illust" viewBox="0 0 720 150" role="img" aria-label="線形補間の数直線">
<text x="20" y="24" class="fig-title">a = 10、b = 50 の間を、t で混ぜる</text>
<line x1="60" y1="80" x2="660" y2="80" stroke="currentColor" stroke-width="3"/>
<circle cx="60" cy="80" r="9" fill="#4c8bf5"/><text x="40" y="112" style="font-size:12px">a = 10（t = 0）</text>
<circle cx="660" cy="80" r="9" fill="#e5484d"/><text x="610" y="112" style="font-size:12px">b = 50（t = 1）</text>
<circle cx="360" cy="80" r="9" fill="#2ea043"/><text x="318" y="112" style="font-size:12px">t = 0.5 → 30</text>
<circle cx="210" cy="80" r="7" fill="currentColor"/><text x="180" y="62" style="font-size:12px">t = 0.25 → 20</text>
<circle cx="510" cy="80" r="7" fill="currentColor"/><text x="480" y="62" style="font-size:12px">t = 0.75 → 40</text>
</svg>

```cpp
float Lerp(float a, float b, float t) {
  return a + (b - a) * t;
}
```

C++20 には、標準の **`std::lerp`**（`<cmath>`）があります。浮動小数点の端の扱いが丁寧です。

```cpp
float v = std::lerp(10.0f, 50.0f, 0.5f);
```

### 何でも補間できる

lerp は**足し算・引き算・掛け算ができる型なら何にでも**使えます。

| 補間するもの | 例 |
| --- | --- |
| **数値** | HP バー・音量・不透明度・拡大率 |
| <strong>ベクトル（位置）</strong> | 2 点の間の移動・カメラの位置 |
| **色** | 赤から青への変化（[色の数学](color.md)） |
| **角度** | 向きの変更（最短の差を使う。[三角関数](trigonometry.md)） |
| <strong>回転（クォータニオン）</strong> | **lerp ではなく slerp**（[3D：回転](rotation.md)） |

```cpp
Vector3 position = Vector3::Lerp(start, end, t);
```

### t の使い方

| 場面 | t の作り方 |
| --- | --- |
| **決まった時間で動かす** | `t = 経過時間 / 全体の時間` を、0〜1 に clamp |
| **進行度の演出** | `t = 現在値 / 最大値` |
| <strong>外挿（先を予測）</strong> | `t > 1` を許す（clamp しない） |
| **往復** | `t` を `sin` や三角波で作る |

```cpp
float t = std::clamp(elapsed / duration, 0.0f, 1.0f);
Vector3 position = Vector3::Lerp(start, end, t);
```

## 逆補間（inverse lerp）

lerp の**逆**です。値 v が、a と b の間のどこにあるか（0〜1 の割合）を求めます。

```text
inverse_lerp(a, b, v) = (v - a) / (b - a)
```

```cpp
float InverseLerp(float a, float b, float v) {
  return (v - a) / (b - a);
}
```

| 使いどころ | 説明 |
| --- | --- |
| **距離から割合を出す** | 射程 5〜20 m の間の、14 m は割合いくつか |
| **HP バーの割合** | `InverseLerp(0, max_hp, hp)` |
| **音の距離減衰** | 近い所は 1、遠い所は 0 |

!!! warning "a と b が同じ値のときは、割り算が 0"
    `b - a` が 0 だと NaN になります。範囲が 0 にならないことを確認します。

## リマップ（範囲の変換）

**ある範囲の値を別の範囲の値に写す**操作です。逆補間で割合を出し、lerp で別の範囲に写します。

```cpp
float Remap(float v, float in_min, float in_max, float out_min, float out_max) {
  float t = InverseLerp(in_min, in_max, v);
  return Lerp(out_min, out_max, t);
}
```

| 使いどころ | 例 |
| --- | --- |
| **スティックの値を速度に** | 入力 0〜1 を速度 0〜8 m/s に |
| **距離から音量に** | 距離 2〜30 m を、音量 1〜0 に |
| **体力から色に** | HP 100〜0 % を、緑〜赤に |
| **ワールド座標から UI 座標に** | ミニマップ |
| **スコアからランクに** | 値の範囲を段階に |

範囲の外では、**clamp する版**（`ClampedRemap`）にするかどうかを場面で決めます。

## 補間の種類

| 種類 | 式の形 | 使いどころ |
| --- | --- | --- |
| <strong>線形補間（lerp）</strong> | 直線 | 一定の速さ |
| **バイリニア補間** | 2 方向の lerp | 画像・高さマップ・ノイズ |
| **三線形補間** | 3 方向の lerp | 3D の格子・ミップマップ |
| **smoothstep** | 3t² - 2t³ | 滑らかな切り替え |
| **イージング** | 任意の曲線 | 動きの「感触」（[イージング](easing.md)） |
| **ベジェ・スプライン** | 曲線 | パス・カーブ（[曲線](curves.md)） |
| **slerp** | 球面上 | 回転（[3D：回転](rotation.md)） |

### バイリニア補間

**格子の 4 つの角の値**から、中間の値を求めます。**まず横方向に 2 回 lerp、次に縦方向に 1 回 lerp** します。

```cpp
float Bilerp(float v00, float v10, float v01, float v11, float tx, float ty) {
  float top = Lerp(v00, v10, tx);
  float bottom = Lerp(v01, v11, tx);
  return Lerp(top, bottom, ty);
}
```

| 使いどころ | 説明 |
| --- | --- |
| **高さマップ（地形）の高さ** | 格子の 4 点から、その間の地面の高さ |
| **テクスチャの拡大** | GPU のバイリニアフィルタと同じ |
| **値ノイズ・パーリンノイズ** | 格子点の値から、間を補間する（[乱数](random.md)） |

### smoothstep

**始まりと終わりをなめらかにした**、0 から 1 への切り替えです。

```text
smoothstep(edge0, edge1, x):
  t = clamp((x - edge0) / (edge1 - edge0), 0, 1)
  return t × t × (3 - 2t)
```

```cpp
float SmoothStep(float edge0, float edge1, float x) {
  float t = std::clamp((x - edge0) / (edge1 - edge0), 0.0f, 1.0f);
  return t * t * (3.0f - 2.0f * t);
}
```

| 点 | 説明 |
| --- | --- |
| **端の傾きが 0** | 動き出しと止まりが急にならない |
| **HLSL・GLSL に標準で入っている** | `smoothstep(e0, e1, x)` |
| **smootherstep** | `6t⁵ - 15t⁴ + 10t³`。端の曲がりがさらに滑らか |
| **使いどころ** | フェード・距離による切り替え・ノイズ・マスク |

## 時間に依存しない補間（指数減衰）

**初心者が最もよく書く、危ない補間**があります。

```cpp
position = Lerp(position, target, 0.1f);
```

毎フレーム、目標に 10% ずつ近づく動きです。**簡単に書けて、見た目もそれなりに滑らか**ですが、**フレームレートによって、速さが変わります**。60 FPS と 144 FPS では、1 秒間の更新回数が違うので、**144 FPS のほうが速く追いつきます**。

### 直し方

**経過時間（delta time）を使った式**に変えます。

```cpp
float t = 1.0f - std::exp(-rate * delta_time);
position = Lerp(position, target, t);
```

| 点 | 説明 |
| --- | --- |
| **`rate`** | 追従の速さ（大きいほど速い。10 なら約 0.1 秒で 63%、約 0.3 秒で 95% 近づく） |
| **`1 - exp(-rate × dt)`** | フレーム数が違っても**同じ時間では同じだけ近づく**ことを保証する式 |
| **別の書き方** | `pow(残りの割合, dt)`。`残りの割合` は 1 秒後に残る割合（例 0.01） |

```cpp
float Damp(float current, float target, float rate, float delta_time) {
  return Lerp(current, target, 1.0f - std::exp(-rate * delta_time));
}
```

**カメラの追従・UI の値の追いかけ・HP バーの遅れて減る表示**などで使います（[スムージング](smoothing.md)）。

!!! note "なぜ `0.1 × dt` ではいけないのか"
    `lerp(a, b, 0.1 × dt)` は、フレームレートの影響は**少なくなりますが、完全には消えません**。例えば dt が大きい（落ちたフレーム）とき、`t` が 1 を超えて、目標を**通り過ぎます**。指数の式なら、**t は必ず 0〜1** に収まります。

## 重心座標による補間

**三角形の中の点**の値を、3 つの頂点の値から補間する方法です。三角形の頂点 A, B, C の値が a, b, c のとき、点 P の**重心座標** (u, v, w)（合計 1）を使って、次のように求めます。

```text
値(P) = u × a + v × b + w × c
```

| 使いどころ | 説明 |
| --- | --- |
| **GPU のピクセル補間** | 頂点の色・UV・法線をピクセルへ |
| **光線と三角形の交差** | 当たった点の UV・法線を求める |
| **ナビメッシュの高さ** | 三角形の上の足場の高さ |

詳しくは[交差判定](intersection.md)。

## 補間の落とし穴

| 落とし穴 | 説明と対策 |
| --- | --- |
| **t が範囲外** | `t < 0` や `t > 1` で、値が飛び出す。`clamp` する（意図した外挿を除く） |
| **終端で止まらない** | 指数減衰は**永遠に目標に近づき続ける**。十分近づいたら、目標へ**スナップ**する |
| **角度の補間** | `lerp(350, 10, 0.5)` は 180 になる。**最短の差で**補間する |
| **回転の補間** | クォータニオンは slerp。成分ごとの lerp は、速さが一定にならない |
| **色の補間** | sRGB のまま補間すると、暗くにごる。線形空間で（[色の数学](color.md)） |
| **整数の補間** | 丸め誤差。いったん `float` にして補間する |
| **精度** | `a + (b - a) × t` は、`t = 1` で `b` に**ぴったり一致しない**ことがある。気になるなら `std::lerp` |

## よくあるミス

??? failure "`lerp(current, target, 0.1f)` を毎フレーム書いて、フレームレートで速さが変わる"
    `1 - exp(-rate × dt)` を使います。

??? failure "`t` を clamp せず、目標を行き過ぎる"
    `std::clamp(t, 0.0f, 1.0f)` を通します。

??? failure "角度を単純な lerp で補間して、逆回りする"
    最短の差で補間します。

??? failure "指数減衰が、いつまでも目標に着かず、微小な動きが残る"
    距離が十分小さくなったら、目標にスナップします。

??? failure "逆補間で、`b - a` が 0 のとき NaN になる"
    範囲が 0 でないことを確認します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>lerp(a, b, t) ＝ a + (b - a) × t</strong>。<strong>t は 0〜1 を clamp</strong>
    - [x] <strong>逆補間</strong>で割合を出し、<strong>リマップ</strong>で範囲を変換
    - [x] <strong>smoothstep</strong> で、なめらかな切り替え
    - [x] 追従は<strong>`1 - exp(-rate × dt)`</strong>。毎フレームの固定 t は避ける
    - [x] <strong>角度は最短で、回転は slerp、色は線形空間で</strong>

## 関連ページ

- [ゲーム数学](index.md)
- [イージング](easing.md)
- [曲線とパス](curves.md)
- [スムージングとフィルタ](smoothing.md)
- [色の数学](color.md)
- [3D：回転（slerp）](rotation.md)
