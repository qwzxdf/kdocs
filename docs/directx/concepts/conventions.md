---
title: Coordinate Conventions
tags:
  - DirectX
---

# Coordinate Conventions

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

3D の描画では <strong>座標系の約束事</strong>が、いくつもあり 1 つでも食い違うと物が裏返る鏡像になる上下が、逆になる見えないといったバグになります。このページはこのサイトの規約と <strong>DirectX の既定の規約</strong>との差をまとめます。

!!! tip "ポイント"
    - このサイトの規約: <strong>右手系・Y が上・前は −Z</strong>。<strong>行ベクトル</strong>（`v * M`、掛け順は左から右）。<strong>三角形は反時計回り（CCW）が表</strong>。角度はラジアン。
    - DirectX のクリップ空間は <strong>x・y が −1〜1、z が 0〜1</strong>（OpenGL は z が −1〜1）。
    - ピクセル座標と uv は、<strong>左上が原点、y が下向き</strong>。クリップ空間は y が上向き。
    - DirectX の既定は、<strong>時計回りが表</strong>。反時計回りにするには `FrontCounterClockwise = TRUE`。
    - 行列はメモリ上、行優先（DirectXMath）。HLSL の既定は列優先なので `row_major` を付ける。

## このサイトの規約

| 項目 | 規約 |
| --- | --- |
| 座標系 | 右手系 |
| 上方向 | +Y |
| 前方向 | −Z（カメラは−Z を向く） |
| ベクトル | 行ベクトル（`v * M`）。変換の掛け順は左から右（`World * View * Projection`） |
| 三角形の表 | 反時計回り（CCW） |
| 角度 | ラジアン |

## 右手系と左手系

3 本の軸（X、Y、Z）の向きの関係です。

| 座標系 | X が右、Y が上のとき Z は |
| --- | --- |
| 右手系 | 手前（自分に向かう）。前（奥）は−Z |
| 左手系 | 奥。前は+Z |

DirectX は右手系も左手系も扱えます（DirectXMath には、`XMMatrixLookAtRH` と `XMMatrixLookAtLH` の両方があります）。このサイトは右手系で統一します。

## クリップ空間とビューポート

頂点シェーダーが出力する <strong>クリップ空間</strong>の座標は、ラスタライザーで `w` で割られ <strong>正規化デバイス座標</strong>（NDC）になります。

| 軸 | DirectX の NDC |
| --- | --- |
| x | −1（左）〜 1（右） |
| y | −1（下）〜 1（上） |
| z | <strong>0（近い）〜 1（遠い）</strong> |

OpenGL は z が −1〜1 ですが、DirectX は <strong>0〜1</strong> です。射影行列は DirectX 用（`XMMatrixPerspectiveFovRH`）を使います。

```text
クリップ空間（y 上向き）            ピクセル座標（y 下向き）
  (-1, 1)  ─────  (1, 1)             (0, 0)     ────── (width, 0)
     │                │                  │                  │
  (-1,-1)  ─────  (1,-1)             (0, height) ────── (width, height)
```

ビューポート変換で <strong>y が上下に反転</strong>します（クリップ空間は、上が +1、ピクセル座標は上が 0）。

## uv 座標

テクスチャの uv は <strong>左上が (0, 0)</strong>、右下が (1, 1)、v が下向きです。クリップ空間の y（上向き）とは逆なのでフルスクリーン三角形などで、変換します。

```hlsl
// クリップ空間 (−1〜1, y 上) → uv (0〜1, y 下)
float2 uv = float2(clip.x, -clip.y) * 0.5 + 0.5;

// uv (0〜1, y 下) → クリップ空間
float2 clip = float2(uv.x, 1.0 - uv.y) * 2.0 - 1.0;
```

OpenGL（左下が (0, 0)）で作った素材を使うときは v を `1 − v` に反転します。

## 三角形の表裏（巻き順）

三角形の頂点が <strong>画面に投影されたとき</strong>、反時計回りか時計回りかで表裏が、決まります。裏面はカリングで捨てられます。

| | 表 | このサイトで |
| --- | --- | --- |
| DirectX の既定 | 時計回り（CW） | — |
| このサイトの規約 | 反時計回り（CCW） | ラスタライザー ステートで、`FrontCounterClockwise = TRUE`（D3D11）、PSO の `RasterizerState.FrontCounterClockwise = TRUE`（D3D12） |

規約と既定が食い違うので <strong>ラスタライザー ステートを設定</strong>し忘れると三角形が裏面として、捨てられ何も見えません。

## 行列の規約

| 項目 | 規約 |
| --- | --- |
| ベクトル | 行ベクトル。頂点は `v * M`（左から右へ変換が重なる） |
| 掛け順 | `World * View * Projection`。`mul(v, M)`（HLSL） |
| メモリ上の並び | 行優先（DirectXMath の `XMFLOAT4X4`） |
| HLSL の既定 | 列優先。`row_major` を付けて行優先にそろえる |

```hlsl
// 行ベクトルの規約: v * M（行列は、右に）。
cbuffer PerObject : register(b0) {
  row_major float4x4 world_view_projection;     // C++ の XMFLOAT4X4 と、同じ並び
};
float4 clip = mul(float4(position, 1.0), world_view_projection);
```

DirectXMath の `XMMatrixMultiply(A, B)` は「A を先に B を後に適用」の意味で、`A * B`（左から右）です。列ベクトル（OpenGL、`M * v`）の書籍の式は順序を逆に読み替えます（[DirectXMath](../../gamemath/directxmath.md)、[Transforms and MVP](../../3d/transforms-mvp.md)）。

## 深度の向き

| 方式 | 近い面 | 遠い面 | クリア値 | `DepthFunc` |
| --- | --- | --- | --- | --- |
| 通常 | 0 | 1 | 1.0 | `LESS` |
| reverse-Z | 1 | 0 | 0.0 | `GREATER` |

reverse-Z は浮動小数点の深度と組み合わせると遠くの精度が大きく、上がります（[Projection](../../3d/projection.md)）。

## よくある食い違い

| 症状 | 原因 |
| --- | --- |
| 三角形が見えない | 巻き順が規約と既定で、食い違う（`FrontCounterClockwise`） |
| 画像が上下、逆さま | uv の y とクリップ空間の y が反転していない |
| 物が鏡像になる | 右手系・左手系の混在（`…RH` と `…LH` の取り違え） |
| 物が変な位置に飛ぶ | 行列の転置の取り違え（`row_major`、掛け順） |
| 深度が逆（近い物が奥） | reverse-Z のクリア値と比較関数がそろっていない |
| 外部のモデル・素材が裏返る | 外部ツールの座標系（左手系、Z 上、など）との変換忘れ |

## よくあるミス

??? failure "OpenGL の記事の行列の式をそのまま使っておかしくなる"
    OpenGL は列ベクトル（`M * v`）、z が −1〜1。DirectX（このサイト）は行ベクトル（`v * M`）、z が 0〜1。掛け順と射影行列を読み替える。

??? failure "`XMMatrixPerspectiveFovLH` を右手系で使った"
    右手系なら `…RH` を使う。LH と RH を混ぜると鏡像になる。

??? failure "テクスチャが、上下反転する"
    uv の v の向きが素材と違う。インポート時に `1 − v` に反転する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] このサイト: 右手系・Y 上・前は −Z、行ベクトル（`v * M`）、反時計回りが表
    - [x] DirectX の NDC は z が 0〜1。OpenGL は −1〜1
    - [x] ピクセル・uv は、左上が原点（y 下向き）。クリップ空間は y 上向き
    - [x] 三角形の既定は時計回りが表。`FrontCounterClockwise = TRUE` で合わせる
    - [x] 行列は行優先。HLSL に `row_major`。`RH` と `LH` を混ぜない

## 関連ページ

- [DirectX Concepts](index.md)
- [DirectXMath](../../gamemath/directxmath.md)
- [Transforms and MVP](../../3d/transforms-mvp.md)
- [Projection](../../3d/projection.md)
- [Rasterizer State](../dx11/rasterizer-state.md)
