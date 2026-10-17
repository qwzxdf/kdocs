---
title: スキニングとアニメーション
tags:
  - 3Dゲーム
---

# スキニングとアニメーション

人や動物のように**曲がる**モデルは、内部に<strong>骨（ボーン）</strong>を持ち、**骨を動かすと、皮膚（メッシュ）が追従**します。これが**スキニング**です。アニメーションは、**各骨の位置・回転を、時間ごとに記録**したデータ（キーフレーム）を、補間して再生します。このページは、骨の階層、スキンウェイト、スキニング行列、キーフレームの補間、ブレンドをまとめます。

!!! tip "ポイント"
    - <strong>骨は階層</strong>（親子）。<strong>子の姿勢は、親の姿勢に、積み重なる</strong>。
    - 頂点は、<strong>最大 4 本の骨</strong>に、<strong>重み</strong>つきで影響される（<strong>重みの合計は 1</strong>）。
    - <strong>スキニング行列 ＝ オフセット行列（逆バインドポーズ）× 骨のワールド行列</strong>。<strong>行列パレット</strong>として、GPU に渡す。
    - アニメーションは<strong>キーフレーム</strong>。<strong>位置・スケールは線形補間、回転は `Slerp`</strong>。
    - 更新は、<strong>親から子の順</strong>（配列を、親が先になるように並べる）。
    - <strong>動き（アニメーション）と見た目（メッシュ）は、骨でつながる</strong>。

## スキニングの仕組み

<svg class="fig" viewBox="0 0 620 240" role="img" aria-label="スキニング：骨と頂点の重み"><defs><marker id="k1" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs><text x="20" y="20" class="fig-title">肘を曲げると、関節の頂点は、2 本の骨に影響される</text><line x1="60" y1="130" x2="200" y2="130" stroke="currentColor" stroke-width="5"/><text x="80" y="112">上腕の骨</text><line x1="200" y1="130" x2="300" y2="60" stroke="currentColor" stroke-width="5"/><text x="260" y="55">前腕の骨</text><circle cx="200" cy="130" r="9" fill="currentColor"/><circle cx="120" cy="128" r="6" fill="rgba(76,139,245,0.9)"/><text x="100" y="160">重み 1.0 / 0.0</text><circle cx="195" cy="118" r="6" fill="rgba(229,170,40,0.9)"/><text x="150" y="190">重み 0.5 / 0.5</text><circle cx="270" cy="82" r="6" fill="rgba(229,72,77,0.9)"/><text x="280" y="98">重み 0.0 / 1.0</text><text x="350" y="80">頂点の位置 ＝ 重み × (骨 A で動かした位置)</text><text x="350" y="105">　　　　　　＋ 重み × (骨 B で動かした位置)</text><text x="350" y="140">関節では、2 つの骨の動きが、混ざる</text><text x="350" y="165">→ 曲がっても、皮膚が自然につながる</text></svg>

<div class="anim" data-type="graph" data-label="骨は親子の階層（子の姿勢は親に積み重なる）">
n h Hips 0 1 hit
---
n h Hips 0 1
n s Spine 1 0 hit
n c Chest 2 0 hit
n hd Head 3 0 hit
l h s hit
l s c hit
l c hd hit
---
n h Hips 0 1
n s Spine 1 0
n c Chest 2 0
n hd Head 3 0
n ll LeftLeg 1 1 hit
n lf LeftFoot 2 1 hit
n rl RightLeg 1 2 hit
n rf RightFoot 2 2 hit
l h s
l s c
l c hd
l h ll hit
l ll lf hit
l h rl hit
l rl rf hit
</div>

各頂点は、近くの骨 1〜4 本と重み（合計 1）を持ちます。骨を動かすと、頂点が重み付きの平均で追従します。

## ボーンの階層

骨は、**親からの相対的な姿勢**（ローカル）を持ちます。**ワールドの姿勢は、親から順にたどって掛け算**で求めます。

```cpp
struct Bone {
  int parent;
  Matrix local;
  Matrix offset;
};

void ComputeWorld(const std::vector<Bone>& bones, std::vector<Matrix>& world) {
  for (size_t i = 0; i < bones.size(); ++i) {
    world[i] = bones[i].parent < 0 ? bones[i].local
                                   : bones[i].local * world[bones[i].parent];
  }
}
```

!!! note "親が、必ず先に並ぶ"
    骨の配列は、**親が子より前**に並べます。1 回のループで、**親のワールド行列が、先に計算済み**になります。読み込み時に、並べ替えて保証します。

## スキンウェイト

**1 つの頂点は、複数の骨**に影響されます（肘の曲げで、上腕と前腕の間が、滑らかにつながる）。

```cpp
struct SkinnedVertex {
  Vector3 position;
  Vector3 normal;
  Vector2 uv;
  uint8_t bone_indices[4];
  float bone_weights[4];
};
```

| 項目 | 説明 |
| --- | --- |
| **骨の番号** | 影響を受ける骨（最大 4 つが、標準） |
| **重み** | 影響の強さ。**合計が 1**になるよう正規化 |
| **4 本までにする理由** | シェーダーの計算量・頂点のサイズ。**ほとんどの場合、4 で十分** |

## スキニング行列

**バインドポーズ**（モデルを作ったときの、基準の姿勢）の頂点を、**骨の空間に戻して**から、**現在の骨の姿勢**で動かします。

```text
スキニング行列(i) = オフセット行列(i) × 骨のワールド行列(i)
                    ↑ バインドポーズの逆行列      ↑ 今の姿勢

動いた頂点 = Σ ( 重み_k × 頂点 × スキニング行列(骨_k) )
```

| 行列 | 意味 |
| --- | --- |
| **オフセット行列**（逆バインド行列） | **バインドポーズでの、骨のワールド行列の逆**。**モデルから読み込む**（変わらない） |
| **骨のワールド行列** | **今の姿勢**（アニメーションで毎フレーム変わる） |
| **スキニング行列** | 頂点を、バインドポーズの位置から、**今の姿勢の位置へ**動かす |

!!! warning "掛け順に注意（行ベクトル規約）"
    `頂点 × オフセット × ワールド` の順です。**行ベクトル規約**（[行列](matrices.md)）。ライブラリが、列ベクトルなら逆順です。

## 行列パレット

全骨の**スキニング行列**を、配列（**行列パレット**）にして、**定数バッファ**で GPU に渡します。

```cpp
constexpr int kMaxBones = 128;

struct BoneCB {
  Matrix palette[kMaxBones];
};

BoneCB cb;
for (size_t i = 0; i < bones.size(); ++i) {
  cb.palette[i] = bones[i].offset * world[i];
}
```

| 制限 | 説明 |
| --- | --- |
| **骨の最大数** | 定数バッファ 64KB 以下（`Matrix` は 64 バイト、**1024 個まで**）。普通は、128〜256 個 |
| **更新の頻度** | **キャラクターごと、毎フレーム** |
| **多数のキャラ** | 骨の行列を、**構造化バッファ**・テクスチャにして、インスタンシング |

### 頂点シェーダー（HLSL、DX11）

```hlsl
cbuffer Bones : register(b2) {
  row_major float4x4 palette[128];
};

struct VsInput {
  float3 position : POSITION;
  float3 normal : NORMAL;
  float2 uv : TEXCOORD0;
  uint4 bone_indices : BLENDINDICES;
  float4 bone_weights : BLENDWEIGHT;
};

VsOutput VSMain(VsInput input) {
  float4x4 skin =
      palette[input.bone_indices.x] * input.bone_weights.x +
      palette[input.bone_indices.y] * input.bone_weights.y +
      palette[input.bone_indices.z] * input.bone_weights.z +
      palette[input.bone_indices.w] * input.bone_weights.w;

  float4 skinned = mul(float4(input.position, 1.0f), skin);
  float3 skinned_normal = mul(input.normal, (float3x3)skin);

  VsOutput output;
  output.position = mul(mul(skinned, world), view_proj);
  output.normal = mul(skinned_normal, (float3x3)world_inverse_transpose);
  output.uv = input.uv;
  return output;
}
```

**4 本の骨の行列を、重みで足し合わせて**、**1 つのスキニング行列**にしてから、頂点を変換します。**法線も、同じスキニング行列で**動かします。

入力レイアウトでは、骨の番号は `DXGI_FORMAT_R8G8B8A8_UINT`、重みは `DXGI_FORMAT_R32G32B32A32_FLOAT`（または `R8G8B8A8_UNORM`）にします（[メッシュとテクスチャ](mesh-textures.md)）。

## アニメーション（キーフレーム）

アニメーションは、**各骨について、ある時刻の姿勢**（キーフレーム）を記録したデータです。**間は、補間**します。

```cpp
struct Keyframe {
  float time;
  Vector3 position;
  Quaternion rotation;
  Vector3 scale;
};

struct BoneTrack {
  std::vector<Keyframe> keys;
};

struct AnimationClip {
  float duration;
  std::vector<BoneTrack> tracks;
};
```

### 補間

```cpp
Matrix SampleTrack(const BoneTrack& track, float time) {
  size_t next = 1;
  while (next < track.keys.size() - 1 && track.keys[next].time < time) ++next;
  const Keyframe& a = track.keys[next - 1];
  const Keyframe& b = track.keys[next];

  float t = (time - a.time) / (b.time - a.time);
  t = std::clamp(t, 0.0f, 1.0f);

  Vector3 position = Vector3::Lerp(a.position, b.position, t);
  Quaternion rotation = Quaternion::Slerp(a.rotation, b.rotation, t);
  Vector3 scale = Vector3::Lerp(a.scale, b.scale, t);

  return Matrix::CreateScale(scale) * Matrix::CreateFromQuaternion(rotation) *
         Matrix::CreateTranslation(position);
}
```

| 要素 | 補間 |
| --- | --- |
| **位置・スケール** | **`Lerp`**（線形） |
| **回転** | **`Slerp`**（球面線形）。**オイラー角では補間しない**（[回転](rotation.md)） |

### 再生

```cpp
void Update(float dt) {
  time_ += dt * speed_;
  if (loop_) time_ = std::fmod(time_, clip_.duration);
  else time_ = std::min(time_, clip_.duration);

  for (size_t i = 0; i < bones_.size(); ++i) {
    bones_[i].local = SampleTrack(clip_.tracks[i], time_);
  }
  ComputeWorld(bones_, world_);
}
```

**時間は、`dt` で進める**（フレームレート非依存）。ループは、**`fmod`** で巻き戻します。

## アニメーションのブレンド

**歩き → 走り**のように、**2 つのアニメーションを、なめらかにつなぐ**には、**姿勢（骨ごとの位置・回転）を、ブレンド**します。

```cpp
Pose Blend(const Pose& a, const Pose& b, float t) {
  Pose result;
  for (size_t i = 0; i < a.bones.size(); ++i) {
    result.bones[i].position = Vector3::Lerp(a.bones[i].position, b.bones[i].position, t);
    result.bones[i].rotation = Quaternion::Slerp(a.bones[i].rotation, b.bones[i].rotation, t);
    result.bones[i].scale = Vector3::Lerp(a.bones[i].scale, b.bones[i].scale, t);
  }
  return result;
}
```

| 種類 | 説明 | 例 |
| --- | --- | --- |
| **クロスフェード** | 切り替え時に、**一定時間**で、前の姿勢から次の姿勢へ | 待機 → 走り（0.2 秒） |
| **ブレンドツリー** | **パラメーター**（速度）で、複数を混ぜる | 速度 0〜1：歩き、1〜2：歩き↔走り |
| **レイヤー** | **骨の一部**だけ、別のアニメ | 上半身は射撃、下半身は走り |
| **加算ブレンド** | ある動きに、**差分**を足す | 傾き、呼吸、被弾の反応 |

**行列のまま補間**すると、**回転が歪む**ので、**位置・回転・スケールに分解して**ブレンドします。

## ステートマシン

**どのアニメーションを再生するか**は、**状態**（待機・歩き・攻撃・死亡）で決めます。

<div class="anim" data-type="graph" data-label="アニメーションのステートマシン">
n idle 待機 0 1 hit
n walk 歩き 1 1
n run 走り 2 1
l idle walk - 速度>0
l walk run - 速度>3
---
n idle 待機 0 1
n walk 歩き 1 1
n run 走り 2 1 hit
l idle walk - 速度>0
l walk run - 速度>3
l run idle - 速度=0
---
n any 任意の状態 0 0
n hit 被弾 1 0 hit
n idle 待機 2 0
l any hit - ダメージ
l hit idle - 終了
</div>

状態遷移の作り方は、[ステートマシン](../design/patterns/state-machine.md)で解説しています。

## ルートモーション

アニメーションに、**キャラクター自体の移動**（歩いた距離）が、含まれているものです。

| 方式 | 説明 | 向いているもの |
| --- | --- | --- |
| **その場アニメ** | 位置は、**ゲームのコードで動かす**。アニメは、足踏みするだけ | **アクション、操作性重視**（普通はこちら） |
| **ルートモーション** | ルート骨の動きを、**実際の移動**に使う | 攻撃のモーションで、前進する距離を正確に |

その場アニメで、**足が滑る**（移動速度と、足踏みの速さが合わない）ときは、**アニメの再生速度を、移動速度に合わせます**。

## 最適化

| 方法 | 効果 |
| --- | --- |
| **GPU スキニング** | 頂点シェーダーで計算（上の例）。**標準** |
| **骨の数を減らす** | 計算・定数バッファが減る |
| **LOD で、遠くは骨を減らす** | 遠くのキャラ |
| **画面外は、更新しない / 頻度を下げる** | 見えないキャラの、アニメ更新を省く |
| **アニメのデータを圧縮** | キーフレームを減らす・量子化 |
| <strong>多数のキャラ（群衆）</strong> | **GPU インスタンシング**、アニメ情報をテクスチャに焼く（頂点アニメーションテクスチャ） |

## ライブラリ

| ライブラリ | 内容 |
| --- | --- |
| **Assimp** | 多くの 3D 形式の読み込み（骨・アニメを含む） |
| **tinygltf / fastgltf** | **glTF** の読み込み（骨・アニメ対応） |
| **ozz-animation** | **アニメーションのランタイム**（サンプリング・ブレンド・最適化）。**高速で、よく使われる** |
| **DirectXTK の `Model`・SDKMESH** | DX 向け。スキニング対応のエフェクト（`SkinnedEffect`） |

## よくあるミス

??? failure "モデルが、ぐちゃぐちゃに潰れる・伸びる"
    **オフセット行列**（逆バインド）を、掛けていません。または、掛け順が逆です。

??? failure "骨の重みの合計が 1 でなく、モデルが、縮む・膨らむ"
    重みを**正規化**します（合計 1）。

??? failure "親の姿勢が、子に反映されない"
    骨の配列が、**親が先**の順序になっていません。親から順にワールドを計算します。

??? failure "回転の補間で、ねじれる・遠回りする"
    オイラー角を補間しています。**クォータニオンの `Slerp`** を使います。

??? failure "アニメーションが、速度によって変わる"
    `dt` を使わず、**フレームごとに**時間を進めています。

??? failure "足が、地面を滑る"
    移動速度と、アニメの速さが、合っていません。**再生速度を、移動に合わせます**。

??? failure "骨の数が多く、定数バッファがあふれる"
    骨の最大数を確認します。多いときは、**構造化バッファ**を使います。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>骨は階層</strong>。<strong>親が先に並ぶ</strong>。ワールド ＝ <strong>ローカル × 親のワールド</strong>
    - [x] 頂点は<strong>最大 4 骨 + 重み（合計 1）</strong>
    - [x] <strong>スキニング行列 ＝ オフセット（逆バインド）× ワールド</strong>。<strong>行列パレット</strong>で GPU へ
    - [x] アニメは<strong>キーフレーム</strong>。<strong>位置・スケールは `Lerp`、回転は `Slerp`</strong>
    - [x] 切り替えは<strong>クロスフェード</strong>。<strong>行列でなく、位置・回転・スケールに分解して</strong>ブレンド
    - [x] 状態は<strong>ステートマシン</strong>。<strong>時間は `dt` で進める</strong>

## 関連ページ

- [3D ゲーム（目次）](index.md)
- [回転とクォータニオン](rotation.md)
- [メッシュとテクスチャ](mesh-textures.md)
- [ステートマシン](../design/patterns/state-machine.md)
