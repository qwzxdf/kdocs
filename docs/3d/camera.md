---
title: カメラ
tags:
  - 3Dゲーム
---

# カメラ

3D ゲームの**カメラ**は、「3D の世界を、どこから、どの向きで見るか」を決める部品です。実は、3D のカメラは、**描画の世界には存在しません**。実際に動いているのは、**世界のほう**です。カメラが右に動くのは、「世界全体が左に動く」のと同じです。そこで、**ビュー行列**が、「世界を、カメラが原点・正面を向いた座標に直す」変換をします（[MVP 変換](transforms-mvp.md)）。このページは、**ビュー行列の作り方**（LookAt）と、ゲームでよく使う**カメラの動かし方**（FPS カメラ、軌道カメラ、追従カメラ）、**カメラの演出**（揺れ、滑らかな追従）を説明します。

!!! tip "ポイント"
    - <strong>カメラ ＝ 位置と向き</strong>。<strong>ビュー行列 ＝ カメラのワールド行列の逆行列</strong>。
    - 普通は<strong>`Matrix::CreateLookAt(位置, 見る点, 上方向)`</strong> で作る（右手系）。
    - <strong>カメラの向きは、角度（yaw・pitch）で持つ</strong>と、操作しやすい。<strong>pitch は ±89° に制限</strong>する（真上・真下で、上方向が定まらなくなる）。
    - <strong>三人称カメラは、ターゲットの後ろに置いて、補間（`Lerp`）で追従</strong>させる。<strong>壁を通り抜けないように、レイキャスト</strong>で調整。
    - <strong>カメラの更新は、キャラクターの更新のあと</strong>に行う（1 フレーム遅れて、ガタつくのを防ぐ）。
    - <strong>ビュー行列は、1 フレームに 1 回</strong>作って、全オブジェクトで共有する。

## ビュー行列

**カメラの位置・向きを、ワールド行列で表し、その逆行列がビュー行列**です。

<div class="anim" data-type="graph" data-label="ビュー行列：世界を、カメラが原点にいる座標に直す">
n w 世界の座標 0 0
n cam カメラ_位置(0,2,5) 1 0 hit
l cam w - 原点を見ている
---
n w 世界の座標 0 0
n v ビュー行列 1 0 hit
n cs カメラが原点・前は-Z 2 0 new
l w v
l v cs - 直す
</div>

### LookAt で作る

```cpp
// カメラの位置、見る点（注視点）、上方向から、ビュー行列を作る（右手系）
Matrix view = Matrix::CreateLookAt(camera_position, camera_target, Vector3::Up);
```

| 引数 | 意味 |
| --- | --- |
| `camera_position` | カメラの位置（ワールド座標） |
| `camera_target` | **見ている点**（ワールド座標）。向きではなく、点 |
| `Vector3::Up` | 「上」の方向。ほとんどの場合 `(0, 1, 0)` |

**向き（前方向）から作る**ときは、「位置 + 前方向」を、見る点にします。

```cpp
Vector3 forward = ...;   // 正規化した前方向
Matrix view = Matrix::CreateLookAt(position, position + forward, Vector3::Up);
```

### LookAt が内部でやっていること

カメラの 3 本の軸（右・上・前）を作り、行列にします。

<div class="anim" data-type="graph" data-label="ビュー行列を作る手順">
n c0 ①_forward(前) 0 0 hit
---
n c0 ①_forward(前) 0 0
n c1 ②_right(右) 1 0 hit
l c0 c1 hit ×up
---
n c0 ①_forward(前) 0 0
n c1 ②_right(右) 1 0
n c2 ③_up(本当の上) 2 0 hit
l c0 c1 - ×up
l c1 c2 hit right×forward
---
n c0 ①_forward(前) 0 0
n c1 ②_right(右) 1 0
n c2 ③_up(本当の上) 2 0
n c3 ④_世界→カメラ行列 3 0 hit
l c0 c1 - ×up
l c1 c2 - right×forward
l c2 c3 hit 3軸と位置から
</div>

**上方向（`up`）と、前方向が、平行（真上・真下を見る）だと、外積が 0 になり、右方向が決まりません**。これが、真上を見たときに、画面が不安定になる原因です（ジンバルロックに似た現象）。

## FPS カメラ（一人称）

<svg class="fig" viewBox="0 0 620 240" role="img" aria-label="yaw と pitch"><defs><marker id="y1" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs><text x="20" y="20" class="fig-title">yaw（左右）：真上から見た図</text><circle cx="130" cy="130" r="8" fill="currentColor"/><text x="100" y="160">カメラ</text><line x1="130" y1="130" x2="130" y2="50" stroke="currentColor" stroke-width="3" marker-end="url(#y1)" /><text x="138" y="55">yaw = 0（前は -Z）</text><line x1="130" y1="130" x2="190" y2="70" stroke="currentColor" stroke-width="2" marker-end="url(#y1)" stroke-dasharray="4 3"/><text x="194" y="68">yaw が増える</text><path d="M 130 90 A 40 40 0 0 1 158 100" fill="none" stroke="currentColor"/><text x="330" y="20" class="fig-title">pitch（上下）：横から見た図</text><circle cx="400" cy="140" r="8" fill="currentColor"/><text x="370" y="170">カメラ</text><line x1="400" y1="140" x2="520" y2="140" stroke="currentColor" stroke-width="3" marker-end="url(#y1)" /><text x="470" y="160">pitch = 0</text><line x1="400" y1="140" x2="500" y2="80" stroke="currentColor" stroke-width="2" marker-end="url(#y1)" stroke-dasharray="4 3"/><text x="470" y="70">上を向く</text><text x="330" y="215">pitch は ±89° に制限する（真上・真下で、向きが定まらなくなるため）</text></svg>

**マウスで、見る方向を変える**カメラです。向きを、<strong>yaw（左右）と pitch（上下）</strong>の 2 つの角度で持ちます。

```cpp
class FpsCamera {
 public:
  void Rotate(float yaw_delta, float pitch_delta) {
    yaw_ += yaw_delta;
    pitch_ = std::clamp(pitch_ + pitch_delta, -kMaxPitch, kMaxPitch);   // 上下は制限する
  }

  Vector3 Forward() const {
    // yaw=0, pitch=0 で、-Z（右手系の前）を向く。yaw が正なら、左（反時計回り）へ回る
    return Vector3(-std::sin(yaw_) * std::cos(pitch_),
                   std::sin(pitch_),
                   -std::cos(yaw_) * std::cos(pitch_));
  }

  Matrix View() const {
    return Matrix::CreateLookAt(position, position + Forward(), Vector3::Up);
  }

  Vector3 position;

 private:
  static constexpr float kMaxPitch = DirectX::XMConvertToRadians(89.0f);
  float yaw_ = 0.0f;     // 左右（Y 軸まわり）
  float pitch_ = 0.0f;   // 上下（X 軸まわり）
};
```

| ポイント | 説明 |
| --- | --- |
| **yaw と pitch で持つ** | 行列やクォータニオンに累積させるより、角度を持つほうが、傾き（roll）が溜まらず安定する |
| **pitch を ±89° に制限** | 真上・真下（±90°）では、上方向が定まらず、画面が反転する |
| **マウスの移動量 × 感度** | 移動量（ピクセル）を、角度に変える。フレームレートに依存しない（マウスの移動量は、すでに差分） |
| **前方向は、yaw と pitch から計算** | 右手系・前 −Z なら `forward = (−sin y × cos p, sin p, −cos y × cos p)`（座標系で式が変わる） |

### 移動

カメラの**向き**に対して、前後左右に動きます。上下の向き（pitch）は、地面を歩く移動には、**含めません**。

```cpp
Vector3 flat_forward(Forward().x, 0.0f, Forward().z);      // pitch を無視した、水平方向の前
flat_forward.Normalize();
Vector3 right = flat_forward.Cross(Vector3::Up);            // 右手系：前 × 上 ＝ 右

Vector3 move = flat_forward * input.forward + right * input.strafe;
if (move.LengthSquared() > 0.0f) {
  move.Normalize();
  position += move * speed * dt;                           // 斜め移動が速くならないよう、正規化
}
```

## 軌道カメラ（オービット）

<svg class="fig" viewBox="0 0 560 230" role="img" aria-label="軌道カメラ"><defs><marker id="o1" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs><text x="20" y="20" class="fig-title">軌道カメラ：注視点のまわりを回る</text><circle cx="200" cy="130" r="8" fill="currentColor"/><text x="215" y="150">注視点（キャラクター）</text><circle cx="200" cy="130" r="80" fill="none" stroke="currentColor" stroke-dasharray="4 4"/><circle cx="270" cy="90" r="7" fill="rgba(76,139,245,0.8)" stroke="currentColor"/><text x="282" y="86">カメラ</text><line x1="266" y1="92" x2="208" y2="126" stroke="currentColor" stroke-width="2" marker-end="url(#o1)" /><text x="230" y="100"></text><text x="330" y="60" class="fig-title">位置 ＝ 注視点 ＋ 方向 × 距離</text><text x="330" y="90">yaw と pitch で、方向を決める</text><text x="330" y="118">距離 ＝ ズーム</text><text x="330" y="146">常に、注視点を向く</text></svg>

**注視点のまわりを、回るカメラ**です。モデルの鑑賞（ビューアー）、エディターのシーン ビュー、三人称ゲームの基本形です。**角度（yaw、pitch）と距離**で持ちます。

```cpp
class OrbitCamera {
 public:
  Matrix View() const {
    // 球座標：注視点のまわりに、距離 distance_ で、角度 yaw_, pitch_ の位置に置く
    Vector3 offset(distance_ * std::cos(pitch_) * std::sin(yaw_),
                   distance_ * std::sin(pitch_),
                   distance_ * std::cos(pitch_) * std::cos(yaw_));
    return Matrix::CreateLookAt(target + offset, target, Vector3::Up);
  }

  void Rotate(float yaw_delta, float pitch_delta) {
    yaw_ += yaw_delta;
    pitch_ = std::clamp(pitch_ + pitch_delta, -kMaxPitch, kMaxPitch);
  }
  void Zoom(float delta) { distance_ = std::max(kMinDistance, distance_ - delta); }

  Vector3 target;                        // 注視点

 private:
  static constexpr float kMaxPitch = DirectX::XMConvertToRadians(89.0f);
  static constexpr float kMinDistance = 0.5f;
  float yaw_ = 0.0f;
  float pitch_ = 0.3f;
  float distance_ = 8.0f;
};
```

| 操作 | 実装 |
| --- | --- |
| **回転**（マウス ドラッグ） | yaw、pitch を増減 |
| **ズーム**（ホイール） | distance を増減（最小・最大を制限） |
| **パン**（平行移動） | カメラの右・上方向に、注視点を動かす |

## 三人称カメラ（追従）

**キャラクターの後ろから、追いかける**カメラです。軌道カメラの注視点を、キャラの位置（少し上）にします。

```cpp
void ThirdPersonCamera::Update(float dt, const Vector3& player_position) {
  // 注視点を、プレイヤーの少し上（頭の高さ）に、滑らかに追従させる
  Vector3 desired_target = player_position + Vector3(0.0f, 1.5f, 0.0f);
  float t = 1.0f - std::exp(-kFollowSpeed * dt);          // フレームレートに依存しない補間
  target = Vector3::Lerp(target, desired_target, t);
}
```

### 滑らかな追従

カメラが、キャラに**ぴったりくっつく**と、動きが硬く、酔いやすくなります。**少し遅れて追いかける**と、滑らかに見えます。

| 方法 | 式 | 特徴 |
| --- | --- | --- |
| **指数補間** | `pos = Lerp(pos, target, 1 − exp(−k × dt))` | **フレームレートに依存しない**。簡単で、定番 |
| 単純な Lerp | `pos = Lerp(pos, target, 0.1f)` | フレームレートで、追従の速さが変わる（避ける） |
| <strong>スプリング（バネ）</strong> | バネと減衰で、速度を持たせる | オーバーシュート（行き過ぎ）で、弾む動き |
| **SmoothDamp** | 目標に、滑らかに近づく（Unity の関数） | 速度の上限を指定できる |

### 壁をすり抜けない

カメラが壁の後ろに回ると、**壁の内側が映ったり、キャラが隠れたり**します。**注視点からカメラ位置へ、レイキャスト**して、壁に当たったら、その手前にカメラを置きます。

```cpp
// 注視点からカメラの理想の位置に向かって、レイを飛ばす
Vector3 ideal = target + offset;
Vector3 dir = ideal - target;
float length = dir.Length();
dir.Normalize();

float hit_distance;
if (RaycastWorld(target, dir, length, &hit_distance)) {
  position = target + dir * std::max(0.3f, hit_distance - 0.2f);   // 壁の少し手前に置く
} else {
  position = ideal;
}
```

[ピッキングとレイキャスト](picking-raycast.md)、物理エンジン（[Jolt](../libs/jolt/index.md)）のレイキャストを使います。

## カメラの演出

| 演出 | 方法 |
| --- | --- |
| **画面の揺れ**（爆発・被ダメージ） | カメラの位置・向きに、<strong>減衰するランダム（ノイズ）</strong>を足す。`shake *= exp(-decay * dt)` |
| **ズーム** | FOV を変える（[投影](projection.md)）、または、距離を変える |
| **ヘッド ボブ**（歩くときの上下の揺れ） | 位置に、`sin(時間 × 歩く速さ)` を足す。控えめに（酔いやすい） |
| **ロック オン**（敵を注視） | 注視点を、敵の位置に補間する |
| **カット シーン** | スプライン（曲線）に沿って動かす。キーフレームを補間（[回転](rotation.md)） |
| **スローモーション** | `dt` を小さくする（カメラは、実時間の `dt` で動かすこともある） |

```cpp
// 画面の揺れ：強さが、時間で減衰する
void Camera::AddShake(float intensity) { shake_ = std::max(shake_, intensity); }

Vector3 Camera::ShakeOffset(float dt) {
  Vector3 offset(random.Range(-1.0f, 1.0f), random.Range(-1.0f, 1.0f), 0.0f);
  offset *= shake_;
  shake_ *= std::exp(-8.0f * dt);       // 指数的に減衰
  return offset;
}
```

## カメラの更新順序

| 順番 | 処理 |
| --- | --- |
| 1 | 入力を受け取る |
| 2 | **キャラクター・物理の更新** |
| 3 | **カメラの更新**（キャラの新しい位置を使う） |
| 4 | ビュー行列を作る（1 回） |
| 5 | 描画 |

カメラの更新が、**キャラクターの更新より前**だと、**1 フレーム遅れた位置**を追うので、キャラが、画面の中で、**ぶるぶる震えて**見えます。必ず**後**に更新します。

## カメラのクラス設計

| 部品 | 内容 |
| --- | --- |
| <strong>`Camera`（基本）</strong> | 位置、向き（クォータニオン）、FOV、near、far。`View()` と `Proj()` を返す |
| **カメラの制御**（FPS、軌道、追従） | `Camera` を、毎フレーム動かす。**制御の種類を、差し替えられる**（[ストラテジー](../design/patterns/strategy.md)） |
| **カメラのデータ** | ビュー行列、プロジェクション行列、`view * proj`、位置、視錐台（カリング用）。**1 フレームに 1 回計算して、共有** |

```cpp
struct CameraData {
  Matrix view;
  Matrix proj;
  Matrix view_proj;
  Vector3 position;
};
```

## ゲームでの使いどころ

| 場面 | カメラ |
| --- | --- |
| FPS | FPS カメラ（yaw、pitch）。マウス感度の設定 |
| 三人称アクション | 軌道カメラ + 追従 + 壁のすり抜け防止 + ロック オン |
| 見下ろし型（ARPG・RTS） | 固定角度のカメラ。キャラを追従。パン・ズーム |
| 2D 横スクロール（3D で表示） | 横に固定した、正射投影か、遠近感の弱いカメラ |
| エディター（シーン ビュー） | 軌道カメラ + パン + ズーム + フライ（右クリックで WASD） |
| カット シーン | スプラインとキーフレーム |

## よくあるミス

??? failure "pitch を制限せず、真上を見たら画面が反転する"
    上方向と前方向が平行になり、外積が 0 になります。pitch を ±89° に制限します。

??? failure "追従を、`Lerp(pos, target, 0.1f)` にして、フレームレートで速さが変わる"
    60 FPS と 144 FPS で、追従の速さが違います。`1 - exp(-k * dt)` を使います。

??? failure "カメラの更新が、キャラクターの更新より前で、震える"
    カメラが、1 フレーム前のキャラの位置を追っています。キャラの更新のあとに、カメラを更新します。

??? failure "壁の裏にカメラが回って、何も見えない"
    カメラの位置を、注視点から壁へのレイキャストで、手前に調整します。

??? failure "斜め移動が、速くなる"
    前後と左右の入力を足したベクトルを、正規化してから、速さを掛けます。

??? failure "向きを、オイラー角の累積だけで管理して、傾く"
    回転を、行列やクォータニオンに累積すると、roll（傾き）が溜まります。FPS カメラは yaw と pitch を別々に持ち、毎回作り直します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>ビュー行列 ＝ カメラのワールド行列の逆</strong>。<strong>`CreateLookAt(位置, 見る点, Up)`</strong> で作る
    - [x] FPS・軌道カメラは<strong>yaw と pitch</strong>で持つ。<strong>pitch は ±89° に制限</strong>
    - [x] 追従は<strong>`1 - exp(-k * dt)`</strong> で補間（フレームレート非依存）。壁は<strong>レイキャスト</strong>で避ける
    - [x] カメラの更新は<strong>キャラクターの更新のあと</strong>。ビュー行列は 1 フレーム 1 回
    - [x] 演出（揺れ・ズーム・ボブ）は<strong>控えめに</strong>。酔いやすい

## 関連ページ

- [3D ゲーム（目次）](index.md)
- [MVP 変換](transforms-mvp.md)
- [投影（プロジェクション）](projection.md)
- [回転とクォータニオン](rotation.md)
- [ピッキングとレイキャスト](picking-raycast.md)
