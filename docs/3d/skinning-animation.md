---
title: スキニングとアニメーション
tags:
  - 3Dゲーム
---

# スキニングとアニメーション

人や動物のように**曲がる**モデルは、内部にボーン（ボーン）を持ち、ボーンを動かすと皮膚（メッシュ）が追従します。これがスキニングです。アニメーションは、各ボーンの位置・回転を時間ごとに記録したデータ（キーフレーム）を補間して再生します。このページはボーンの階層、スキンウェイト、スキニング行列、キーフレームの補間、ブレンドをまとめます。

!!! tip "ポイント"
    - <strong>ボーンは階層</strong>（親子）。<strong>子の姿勢は親の姿勢に積み重なる</strong>。
    - 頂点は最大 4 本のボーンに重みつきで影響される（重みの合計は 1）。
    - スキニング行列 ＝ オフセット行列（逆バインドポーズ）× ボーンのワールド行列。行列パレットとして、GPU に渡す。
    - アニメーションはキーフレーム。位置・スケールは線形補間、回転は `Slerp`。
    - 更新は親から子の順（配列を親が先になるように並べる）。
    - 動き（アニメーション）と見た目（メッシュ）は、ボーンでつながる。

!!! info "このページを読む前に"
    - [3d/index.md](index.md)（このセクション全体の地図と、読む順番）
    - [行列](../gamemath/matrices.md)（行列の基礎）
    - [座標系](../gamemath/coordinate-systems.md)（このサイトの座標系の約束）

## スキニングの仕組み

<svg class="fig" viewBox="0 0 670 240" role="img" aria-label="スキニング：ボーンと頂点の重み"><defs><marker id="k1" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs><text x="20" y="20" class="fig-title">肘を曲げると、関節の頂点は、2 本のボーンに影響される</text><line x1="60" y1="130" x2="200" y2="130" stroke="currentColor" stroke-width="5"/><text x="80" y="112">上腕のボーン</text><line x1="200" y1="130" x2="300" y2="60" stroke="currentColor" stroke-width="5"/><text x="260" y="55">前腕のボーン</text><circle cx="200" cy="130" r="9" fill="currentColor"/><circle cx="120" cy="128" r="6" fill="rgba(76,139,245,0.9)"/><text x="100" y="160">重み 1.0 / 0.0</text><circle cx="195" cy="118" r="6" fill="rgba(229,170,40,0.9)"/><text x="150" y="190">重み 0.5 / 0.5</text><circle cx="270" cy="82" r="6" fill="rgba(229,72,77,0.9)"/><text x="280" y="98">重み 0.0 / 1.0</text><text x="350" y="80">頂点の位置 ＝ 重み × (ボーン A で動かした位置)</text><text x="350" y="105">　　　　　　＋ 重み × (ボーン B で動かした位置)</text><text x="350" y="140">関節では、2 つのボーンの動きが、混ざる</text><text x="350" y="165">→ 曲がっても、皮膚が自然につながる</text></svg>

<svg class="fig flow" viewBox="0 0 583 280" role="img" aria-label="ボーンは親子の階層（子の姿勢は親に積み重なる）"><defs><marker id="fl2385" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">ボーンは親子の階層（子の姿勢は親に積み重なる）</text><line x1="106.0" y1="125.0" x2="172.0" y2="87.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl2385)"/><line x1="253.0" y1="64.0" x2="326.5" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl2385)"/><line x1="408.5" y1="64.0" x2="476.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl2385)"/><line x1="107.0" y1="148.0" x2="169.0" y2="148.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl2385)"/><line x1="255.0" y1="148.0" x2="320.5" y2="148.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl2385)"/><line x1="106.0" y1="171.0" x2="172.0" y2="209.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl2385)"/><line x1="259.0" y1="232.0" x2="317.0" y2="232.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl2385)"/><rect x="28.0" y="128.0" width="76" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="66.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">Hips</text><circle cx="30.0" cy="130.0" r="10" fill="#4c8bf5"/><text x="30.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="174.0" y="44.0" width="76" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="212.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">Spine</text><circle cx="176.0" cy="46.0" r="10" fill="#2ea043"/><text x="176.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="329.5" y="44.0" width="76" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="367.5" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">Chest</text><circle cx="331.5" cy="46.0" r="10" fill="#2ea043"/><text x="331.5" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="479.0" y="44.0" width="76" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="517.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">Head</text><circle cx="481.0" cy="46.0" r="10" fill="#2ea043"/><text x="481.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="172.0" y="128.0" width="80" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="212.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">LeftLeg</text><circle cx="174.0" cy="130.0" r="10" fill="#e5a828"/><text x="174.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="323.5" y="128.0" width="88" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="367.5" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">LeftFoot</text><circle cx="325.5" cy="130.0" r="10" fill="#e5a828"/><text x="325.5" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="168.0" y="212.0" width="88" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="212.0" y="232.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">RightLeg</text><circle cx="170.0" cy="214.0" r="10" fill="#e5a828"/><text x="170.0" y="214.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="320.0" y="212.0" width="95" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="367.5" y="232.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">RightFoot</text><circle cx="322.0" cy="214.0" r="10" fill="#e5a828"/><text x="322.0" y="214.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text></svg>

各頂点は近くのボーン 1〜4 本と重み（合計 1）を持ちます。ボーンを動かすと頂点が重み付きの平均で追従します。

## ボーンの階層

ボーンは**親からの相対的な姿勢**（ローカル）を持ちます。ワールドの姿勢は、親から順にたどって掛け算で求めます。

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

!!! note "親が必ず先に並ぶ"
    ボーンの配列は、親が子より前に並べます。1 回のループで親のワールド行列が先に計算済みになります。読み込み時に並べ替えて保証します。

## スキンウェイト

**1 つの頂点は、複数のボーン**に影響されます（肘の曲げで上腕と前腕の間が滑らかにつながる）。

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
| ボーンの番号 | 影響を受けるボーン（最大 4 つが標準） |
| 重み | 影響の強さ。合計が 1になるよう正規化 |
| 4 本までにする理由 | シェーダーの計算量・頂点のサイズ。ほとんどの場合、4 で十分 |

## スキニング行列

**バインドポーズ**（モデルを作ったときの基準の姿勢）の頂点をボーンの空間に戻してから、現在のボーンの姿勢で動かします。

```text
スキニング行列(i) = オフセット行列(i) × ボーンのワールド行列(i)
                    ↑ バインドポーズの逆行列      ↑ 今の姿勢

動いた頂点 = Σ ( 重み_k × 頂点 × スキニング行列(ボーン_k) )
```

| 行列 | 意味 |
| --- | --- |
| オフセット行列（逆バインド行列） | バインドポーズでのボーンのワールド行列の逆。モデルから読み込む（変わらない） |
| ボーンのワールド行列 | 今の姿勢（アニメーションで毎フレーム変わる） |
| スキニング行列 | 頂点をバインドポーズの位置から、今の姿勢の位置へ動かす |

!!! warning "掛け順に注意（行ベクトル規約）"
    `頂点 × オフセット × ワールド` の順です。行ベクトル規約（[行列](../gamemath/matrices.md)）。ライブラリが列ベクトルなら逆順です。

## 行列パレット

全ボーンの**スキニング行列**を配列（行列パレット）にして、定数バッファで GPU に渡します。

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
| ボーンの最大数 | 定数バッファ 64KB 以下（`Matrix` は 64 バイト、1024 個まで）。普通は、128〜256 個 |
| 更新の頻度 | キャラクターごと毎フレーム |
| 多数のキャラ | ボーンの行列を構造化バッファ・テクスチャにして、インスタンシング |

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

4 本のボーンの行列を重みで足し合わせて、1 つのスキニング行列にしてから、頂点を変換します。法線も同じスキニング行列で動かします。

入力レイアウトでは、ボーンの番号は `DXGI_FORMAT_R8G8B8A8_UINT`、重みは `DXGI_FORMAT_R32G32B32A32_FLOAT`（または `R8G8B8A8_UNORM`）にします（[メッシュとテクスチャ](mesh-textures.md)）。

## アニメーション（キーフレーム）

アニメーションは、**各ボーンについて、ある時刻の姿勢**（キーフレーム）を記録したデータです。間は補間します。

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
| 位置・スケール | `Lerp`（線形） |
| 回転 | `Slerp`（球面線形）。オイラー角では補間しない（[回転](../gamemath/rotation.md)） |

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

時間は、`dt` で進める（フレームレート非依存）。ループは、`fmod` で巻き戻します。

## アニメーションのブレンド

**歩き → 走り**のように、2 つのアニメーションをなめらかにつなぐには、姿勢（ボーンごとの位置・回転）をブレンドします。

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
| クロスフェード | 切り替え時に一定時間で前の姿勢から次の姿勢へ | 待機 → 走り（0.2 秒） |
| ブレンドツリー | パラメーター（速度）で、複数を混ぜる | 速度 0〜1：歩き、1〜2：歩き↔走り |
| レイヤー | ボーンの一部だけ、別のアニメ | 上半身は射撃、下半身は走り |
| 加算ブレンド | ある動きに差分を足す | 傾き、呼吸、被弾の反応 |

行列のまま補間すると回転が歪むので位置・回転・スケールに分解してブレンドします。

## ステートマシン

**どのアニメーションを再生するか**は、状態（待機・歩き・攻撃・死亡）で決めます。

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

アニメーションに**キャラクター自体の移動**（歩いた距離）が含まれているものです。

| 方式 | 説明 | 向いているもの |
| --- | --- | --- |
| その場アニメ | 位置はゲームのコードで動かす。アニメは足踏みするだけ | アクション、操作性重視（普通はこちら） |
| ルートモーション | ルートボーンの動きを実際の移動に使う | 攻撃のモーションで前進する距離を正確に |

その場アニメで足が滑る（移動速度と足踏みの速さが合わない）ときはアニメの再生速度を移動速度に合わせます。

## 最適化

| 方法 | 効果 |
| --- | --- |
| **GPU スキニング** | 頂点シェーダーで計算（上の例）。標準 |
| ボーンの数を減らす | 計算・定数バッファが減る |
| LOD で遠くはボーンを減らす | 遠くのキャラ |
| 画面外は更新しない / 頻度を下げる | 見えないキャラのアニメ更新を省く |
| アニメのデータを圧縮 | キーフレームを減らす・量子化 |
| 多数のキャラ（群衆） | GPU インスタンシング、アニメ情報をテクスチャに焼く（頂点アニメーションテクスチャ） |

## ライブラリ

| ライブラリ | 内容 |
| --- | --- |
| Assimp | 多くの 3D 形式の読み込み（ボーン・アニメを含む） |
| tinygltf / fastgltf | glTF の読み込み（ボーン・アニメ対応） |
| ozz-animation | アニメーションのランタイム（サンプリング・ブレンド・最適化）。高速でよく使われる |
| DirectXTK の `Model`・SDKMESH | DX 向け。スキニング対応のエフェクト（`SkinnedEffect`） |

## よくあるミス

??? failure "モデルがぐちゃぐちゃに潰れる・伸びる"
    オフセット行列（逆バインド）を掛けていません。または掛け順が逆です。

??? failure "ボーンの重みの合計が 1 でなく、モデルが縮む・膨らむ"
    重みを正規化します（合計 1）。

??? failure "親の姿勢が子に反映されない"
    ボーンの配列が親が先の順序になっていません。親から順にワールドを計算します。

??? failure "回転の補間で、ねじれる・遠回りする"
    オイラー角を補間しています。クォータニオンの `Slerp` を使います。

??? failure "アニメーションが速度によって変わる"
    `dt` を使わず、フレームごとに時間を進めています。

??? failure "足が地面を滑る"
    移動速度とアニメの速さが合っていません。再生速度を移動に合わせます。

??? failure "ボーンの数が多く、定数バッファがあふれる"
    ボーンの最大数を確認します。多いときは構造化バッファを使います。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ボーンは階層。親が先に並ぶ。ワールド ＝ ローカル × 親のワールド
    - [x] 頂点は最大 4 ボーン + 重み（合計 1）
    - [x] スキニング行列 ＝ オフセット（逆バインド）× ワールド。行列パレットで GPU へ
    - [x] アニメはキーフレーム。位置・スケールは `Lerp`、回転は `Slerp`
    - [x] 切り替えはクロスフェード。行列でなく、位置・回転・スケールに分解してブレンド
    - [x] 状態はステートマシン。時間は `dt` で進める

## 関連ページ

- [3D ゲーム（目次）](index.md)
- [回転とクォータニオン](../gamemath/rotation.md)
- [メッシュとテクスチャ](mesh-textures.md)
- [ステートマシン](../design/patterns/state-machine.md)
