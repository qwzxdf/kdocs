---
title: Screen-Space Visibility
tags:
  - 描画
---

# Screen-Space Visibility

<strong>AO の式の中の可視性 V（その方向が遮られているか）</strong>を <strong>スクリーン空間の AO では、深度バッファだけから推定</strong>します。見えている面の深度しか分からないので、「画面に写らない裏側」は分からず、推定には限界があります。このページでは、深度バッファから V を求める考え方・限界を説明します。

!!! tip "ポイント"
    - スクリーン空間では、深度バッファが唯一のジオメトリ情報。
    - サンプル点を画面に投影し、その点の深度とバッファの深度を比べる。
    - 限界：画面外・薄い物の裏側・遮蔽物の厚みは分からない。
    - これがハロー・画面端の欠点につながる（[AO Artifacts](../artifacts/index.md)）。

!!! info "このページを読む前に"
    - [AO Theory](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）

## スクリーン空間では、V をどう求めるか

本来の可視性 V(ω) は、点 p から方向 ω にレイを飛ばして、シーンのどこかに当たるかを調べて決まります。レイトレーシングなら、これをそのまま実行できます。しかし、ラスタライズ中心のゲームでは、シーンのジオメトリ全体は GPU のメモリに BVH のような形で用意されておらず、使えるのは<strong>画面に描き終えた深度バッファ</strong>だけです。

深度バッファは、各画素に「カメラから見て一番手前の面までの距離」を記録した画像です。これを「高さ場」のように見立てれば、画面の中の面の形は分かります。そこでスクリーン空間 AO（SSAO）は、次のような手順で V を代用します。

1. p の近くに、サンプル点 s を置く（p から ω 方向にずらした点）。
2. s をカメラの射影で画面に投影し、その画素の深度をバッファから読む。
3. s がその深度より<strong>奥</strong>にあれば、s は「何かの面の裏側に隠れている」ので、その方向は遮られていると数える。手前にあれば遮られていない。

つまり、本来の「方向に遮蔽物があるか」を「サンプル点の位置が見えている面の奥にあるか」という深度の比較に置き換えます。1 回の比較は軽いので、画素あたり十数回でも実行できます。

## この代用が持つ誤差

この近似は便利ですが、深度バッファが<strong>画面から見える一番手前の面しか持たない</strong>ことに由来する、避けられない誤差があります。

第 1 に、<strong>画面に映らない物は遮蔽物になれません</strong>。カメラの後ろにある壁や、画面の外にある物体は、深度バッファに存在しないので、AO には何も寄与しません。そのため、画面の端では AO が不連続になり、カメラを動かしたとき、画面外から現れた物の影響が突然 AO に出て、ちらつきの原因にもなります。

第 2 に、<strong>手前の面の裏側は分かりません</strong>。深度バッファには、柱の表側の深度しかなく、柱の厚みは分かりません。柱の後ろの床の点から見ると、柱は「どこまでも奥へ詰まった厚い壁」に見えて、必要以上に暗く（ハローとして）なります。

第 3 に、<strong>内部や下側の情報がありません</strong>。深度バッファは 1 枚の高さ場なので、橋の下、庇の裏、複雑な室内の奥の構造などは、手前の面に隠れて分かりません。

第 4 に、<strong>解像度が有限</strong>です。細い隙間や小さな物体は、画素の間に落ちて取りこぼされます。

これらの誤差は、スクリーン空間の手法であるかぎり、どの方式（SSAO・HBAO・GTAO）でも共通です。方式の違いは、<strong>この誤差を目立たなくする工夫と、計算を速くする工夫</strong>にあります。誤差を根本から無くすには、シーンのジオメトリそのものを調べる方式が必要です（[レイトレ AO・距離場 AO・ボクセル AO](../world-space/index.md)）。その代わり、必要なメモリと計算が増えます。

具体的な不具合の見え方と対策は、[AO Artifacts](../artifacts/index.md) にまとめています。

## 深度バッファから、サンプル点の可視性を求める

### 再構成：深度から、ビュー空間の位置へ

```hlsl
// 深度（0〜1）と uv から、ビュー空間の位置を復元する（左手系、前は +Z）。
float3 ViewPosition(float2 uv, float depth) {
  float4 clip = float4(uv * float2(2.0, -2.0) + float2(-1.0, 1.0), depth, 1.0);
  float4 view = mul(clip, g_inv_proj);
  return view.xyz / view.w;
}
```

AO の計算は、ほぼすべてビュー空間で行います。カメラが原点で、深度の比較が単純になるからです。

### サンプル点を投影して、深度と比べる

```hlsl
// 点 p の近くのサンプル点 s が、見えている面の奥にあるか。
float3 s = p + offset;                                              // offset は、法線の向きの半球内
float4 clip = mul(float4(s, 1.0), g_proj);
float2 uv = clip.xy / clip.w * float2(0.5, -0.5) + 0.5;
float scene_z = ViewPosition(uv, g_depth.SampleLevel(g_point_clamp, uv, 0)).z;   // その画素で見えている面の、z
bool occluded = scene_z <= s.z - g_bias;                            // +Z が前なので、z が小さいほど手前。面が手前にあれば、遮蔽
```

サンプル点 `s` をカメラの射影で画面に落とし、その画素に見えている面の深度と比べます。面が `s` より手前なら、`s` はその面の裏にあるので、遮られていると数えます。`g_bias` は、同じ面の上の点を自分で遮ってしまわないための、わずかな余裕です。

### 範囲チェック：遠い面を遮蔽に数えない

```hlsl
// 手前にあるのが、ずっと手前の別の物体（柱の向こうの壁など）なら、遮蔽に数えない。
float range = smoothstep(0.0, 1.0, g_radius / abs(p.z - scene_z));
occlusion += occluded ? range : 0.0;
```

深度の差が半径より大きい場合、その面は、`p` の周りの遮蔽物ではなく、ただ手前を横切っているだけです。放置すると、物体の輪郭に沿って、暗いハローが出ます（[Halo](../artifacts/halo.md)）。

## D3D11 での、深度の準備

```cpp
// 深度は、typeless で作り、DSV（書き込み）と SRV（AO の読み込み）の両方から見る。
D3D11_TEXTURE2D_DESC desc = {};
desc.Format = DXGI_FORMAT_R32_TYPELESS;
desc.BindFlags = D3D11_BIND_DEPTH_STENCIL | D3D11_BIND_SHADER_RESOURCE;
// DSV: DXGI_FORMAT_D32_FLOAT、SRV: DXGI_FORMAT_R32_FLOAT
```

AO のパスを走らせる前に深度の DSV を外してから SRV として束ねます（同じリソースを書き込みと読み込みで同時に束ねない）。

## よくあるミス

??? failure "画面端で AO が消える"
    <strong>画面外は情報がない</strong>。<strong>[アーティファクト](../artifacts/index.md)の対策</strong>を参照。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 深度バッファから V を推定
    - [x] 画面外・厚み・裏側は分からない

## 参考

- Mittring, "Finding Next Gen: CryEngine 2", SIGGRAPH 2007, Advances in Real-Time Rendering in 3D Graphics and Games
- Filion, McNaughton, "StarCraft II: Effects & Techniques", SIGGRAPH 2008, Advances in Real-Time Rendering in 3D Graphics and Games（深度バッファによる、SSAO）
- Bavoil, Sainz, Dimitrov, "Image-Space Horizon-Based Ambient Occlusion", SIGGRAPH 2008 Talks
- Reinbothe, Boubekeur, Alexa, "Hybrid Ambient Occlusion", Eurographics 2009 Areas Papers

## 関連ページ

- [AO Theory](index.md)
- [Approximating the Integral](approximation.md)
- [AO Artifacts](../artifacts/index.md)
