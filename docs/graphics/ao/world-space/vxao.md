---
title: Voxel AO (VXAO)
tags:
  - 描画
---

# Voxel AO (VXAO)

<strong>ボクセル AO はシーンを 3D のボクセル（立方体の格子）に変換し、そのミップで円錐トレース</strong>して、遮蔽を求めます。ボクセル GI と同じ仕組みをAO に使うもので、動く物体も毎フレーム再ボクセル化して扱えます。このページではボクセル化・円錐トレースによる AO・コストを説明します。

!!! tip "ポイント"
    - VXAO ＝ シーンをボクセル化し、ミップで円錐トレース。
    - 動く物体も扱える（毎フレーム再ボクセル化）。
    - ボクセルの解像度で、細部と範囲が決まる。
    - ボクセル GI と仕組みを共有できる（[Voxel GI](../../gi/voxel-gi.md)）。

!!! info "このページを読む前に"
    - [Ray-Traced, Distance-Field and Voxel AO](index.md)（このセクション全体の地図と、読む順番）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## ボクセル AO（VXAO）

シーンをボクセル（3D の小さな箱）の格子に変換し、各ボクセルに<strong>占有度</strong>（どれだけ埋まっているか）を保存します。さらに、ミップマップを作ります。粗いミップのボクセルは広い範囲の平均の占有度を持ちます。AO は点から円錐に沿って、ミップを上げながら占有度を積み上げることで求めます。

### ボクセル化

シーンのメッシュを 3D テクスチャの中に書き込む処理がボクセル化です。典型的な方法は各三角形を面積が最も大きくなる軸（法線の主成分）の方向に向けた正射影で、ラスタライズする方法です。三角形をどの軸から見てもボクセルに穴が開かないようにするためです。ピクセル シェーダーから 3D テクスチャへアトミック操作や UAV への書き込みで、占有度（と GI なら色）を書き込みます。薄い三角形でボクセルを取りこぼさないように 保守的ラスタライズ（三角形が少しでも触れた画素を処理対象にする）を使うこともあります。

動かない背景は 1 回ボクセル化したものを保持しておき動く物体だけを毎フレーム再ボクセル化して合成すると、コストを抑えられます。さらに、カメラの周りだけを細かく遠くを粗くするカスケード（カメラ中心の入れ子のボリューム）にすると、広い範囲を限られたメモリで扱えます。

### 円錐トレース

AO の積分を半球の方向をいくつかの円錐に分けて近似します。法線を中心に真上 1 本と周りの 4〜6 本（開き角は 45〜60 度程度）の円錐で、半球を覆うのが一般的です。円錐の断面は距離が離れるほど広がります。そこで、距離に応じたミップを読みます。近くは細かく遠くは粗くです。占有度は前から順に合成し手前の占有度が奥の寄与を隠します。これはアルファ合成と同じ式です。

<div class="formula">occ ← occ + (1 − occ) · α(位置)　、　（α：その位置のボクセル占有度）</div>

```hlsl
float ConeOcclusion(float3 origin, float3 dir, float aperture) {
  float occlusion = 0.0;
  float t = kStartOffset;
  while (t < max_distance && occlusion < 1.0) {
    float diameter = 2.0 * aperture * t;
    float mip = log2(diameter / voxel_size);
    float alpha = voxel_tex.SampleLevel(linear_sampler, WorldToVoxel(origin + dir * t), mip).a;
    occlusion += (1.0 - occlusion) * alpha * DistanceFalloff(t);
    t += diameter * 0.5;
  }
  return 1.0 - occlusion;
}
```

円錐の直径に応じてミップを選ぶので、`mip = log2(直径 / ボクセル サイズ)` です。距離の減衰を掛けて遠い遮蔽を弱めます（オブスキュランス。[Obscurance](../theory/obscurance.md)）。`kStartOffset` は出発点のボクセル自身を数えて自己遮蔽にならないよう少し進めておく値です。

### 特徴

利点は動的なシーンにも使えること（毎フレーム、ボクセル化を更新）、AO だけでなく間接光・反射・影にも同じ構造が使えること（VXGI。[Voxel GI](../../gi/voxel-gi.md)）、レイトレ ハードウェアが不要なことです。

欠点はボクセルの解像度が粗いこと（細部や薄い物は潰れる）、ボクセル化のコストと 3D テクスチャのメモリが必要なことそしてライト リーク（壁の向こうの明るさが漏れる）やブロック状のアーティファクトが出やすいことです。薄い壁は 1 ボクセルより細いので、占有度が薄まって遮蔽が弱くなります。

### 精度を上げる工夫

占有度を異方性ボクセル（6 方向それぞれの占有度）で持つ方法があります。同じボクセルでも見る方向によって「詰まっている度合い」が違うので、薄い壁を横から見たときと正面から見たときの違いを区別できます。円錐の軸の向きに合わせて 6 方向の値を混ぜて読みます。メモリは 6 倍近くになりますが、ライト リークが大きく減ります。

NVIDIA の VXAO はこの考え方を AO に絞って最適化した実装で、ボクセルに占有度だけを保存し、通常の AO（スクリーン空間）より高品質な接触の暗さを得ています。

## ボクセル化を D3D11 で組む

### 3D テクスチャと UAV

```cpp
// 占有度を持つ、ボクセル格子（128³、1 チャンネル）。ピクセル シェーダーから UAV で書き、後でミップを作る。
D3D11_TEXTURE3D_DESC desc = {};
desc.Width = desc.Height = desc.Depth = 128;
desc.MipLevels = 0;                                                    // 全ミップ（円錐トレースで使う）
desc.Format = DXGI_FORMAT_R8_UNORM;
desc.Usage = D3D11_USAGE_DEFAULT;
desc.BindFlags = D3D11_BIND_SHADER_RESOURCE | D3D11_BIND_UNORDERED_ACCESS | D3D11_BIND_RENDER_TARGET;
desc.MiscFlags = D3D11_RESOURCE_MISC_GENERATE_MIPS;
device->CreateTexture3D(&desc, nullptr, &voxel_tex);
```

ピクセル シェーダーから UAV に書き込むためにレンダー ターゲットは、無しにして `OMSetRenderTargetsAndUnorderedAccessViews` で UAV だけを束ねます。ビューポートは格子の解像度（128×128）に合わせます。

### 三角形の向きを選んで、ラスタライズする

```hlsl
// ジオメトリ シェーダー: 三角形の法線が最も大きい軸（X / Y / Z）に向けて、直交投影し直す。面積が最大になる軸で描くと、取りこぼしが少ない。
[maxvertexcount(3)]
void VoxelizeGS(triangle VSOut input[3], inout TriangleStream<GSOut> stream) {
  float3 n = abs(cross(input[1].world - input[0].world, input[2].world - input[0].world));
  uint axis = (n.x > n.y && n.x > n.z) ? 0 : (n.y > n.z ? 1 : 2);
  for (uint i = 0; i < 3; ++i) {
    GSOut o;
    o.world = input[i].world;
    float3 p = (input[i].world - g_voxel_origin) / g_voxel_extent * 2.0 - 1.0;   // 格子の範囲を −1〜1 に
    o.position = float4(axis == 0 ? p.yzx : (axis == 1 ? p.zxy : p.xyz), 1.0);  // 軸ごとに、向きを回す
    stream.Append(o);
  }
}
```

三角形をその面積が最大に見える軸から描くとラスタライザーが三角形をほぼ漏れなく画素（= ボクセル）に分けてくれます。細い三角形の取りこぼしは保守的ラスタライズ（D3D11.3 / D3D12 の機能）で防げます。

```hlsl
// ピクセル シェーダー: 当たったボクセルの占有度を 1 にする。
RWTexture3D<float> g_voxel : register(u1);
void VoxelizePS(GSOut input) {
  int3 voxel = (int3)((input.world - g_voxel_origin) / g_voxel_extent * 128.0);
  g_voxel[voxel] = 1.0;
}
```

ここで書くのは占有度だけです。色や法線まで保存すると GI 用のボクセルになります（[Voxel GI](../../gi/voxel-gi.md)）。

### ミップを作る：占有度の平均

```cpp
context->GenerateMips(voxel_srv.Get());   // 8 つのボクセルの平均。粗いミップほど、「部分的に埋まっている」を表す
```

円錐の直径が大きくなるほど粗いミップを読みます。ミップの値は領域のうち埋まっている割合なので、円錐の中の遮蔽の割合としてそのまま使えます。

!!! info "ここで使われる「積分」をやさしく言うと"
    VXAO の積分は DFAO と同じ <strong>半球を数本の円錐に分けて、円錐ごとの遮られ具合を足す</strong>ことです。

    - 円錐に沿ってボクセル（3D の格子）の 占有度（どれだけ埋まっているか）を読みながら進む。
    - 円錐が進むほど太くなるので、粗いミップを読む。
    - 占有度を前から順に積み重ねて（`occ += (1 − occ) × 占有度`）、円錐がどれだけふさがれたかを求める。

    数式を使わないくわしい説明は [Integrals and Elevation Angles in Plain Words](../theory/integral-intuition.md) です。

## よくあるミス

??? failure "ボクセルが粗くて、AO がブロック状に見える"
    <strong>ボクセルの解像度を上げる・カスケード</strong>にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ボクセル化 ＋ 円錐トレース
    - [x] 動く物体も扱えるが、メモリと再ボクセル化のコスト

## 参考

- Crassin, Neyret, Sainz, Green, Eisemann, "Interactive Indirect Illumination Using Voxel Cone Tracing", Computer Graphics Forum (Pacific Graphics 2011)
- Crassin, Green, "Octree-Based Sparse Voxelization Using the GPU Hardware Rasterizer", OpenGL Insights, Chapter 22, 2012
- NVIDIA, "VXAO"（NVIDIA GameWorks）

## 関連ページ

- [Ray-Traced, Distance-Field and Voxel AO](index.md)
- [Distance Field AO (DFAO)](dfao.md)
- [Voxel GI](../../gi/voxel-gi.md)
