---
title: Coordinate Conventions
tags:
  - DirectX
---

# Coordinate Conventions

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

3D の、描画では、<strong>座標系の、約束事</strong>が、いくつも、あり、1 つでも、食い違うと、物が、裏返る、鏡像に、なる、上下が、逆になる、見えない、といった、バグに、なります。このページは、このサイトの、規約と、<strong>DirectX の、既定の、規約</strong>との、差を、まとめます。

!!! tip "ポイント"
    - このサイトの、規約: <strong>右手系・Y が上・前は −Z</strong>。<strong>行ベクトル</strong>（`v * M`、掛け順は、左から右）。<strong>三角形は、反時計回り（CCW）が表</strong>。角度は、ラジアン。
    - DirectX の、クリップ空間は、<strong>x・y が −1〜1、z が 0〜1</strong>（OpenGL は、z が −1〜1）。
    - ピクセル座標と uv は、<strong>左上が、原点、y が、下向き</strong>。クリップ空間は、y が、上向き。
    - DirectX の、既定は、<strong>時計回りが、表</strong>。反時計回りに、するには、`FrontCounterClockwise = TRUE`。
    - 行列は、メモリ上、行優先（DirectXMath）。HLSL の、既定は、列優先なので、`row_major` を、付ける。

## このサイトの、規約

| 項目 | 規約 |
| --- | --- |
| 座標系 | 右手系 |
| 上方向 | +Y |
| 前方向 | −Z（カメラは、−Z を、向く） |
| ベクトル | 行ベクトル（`v * M`）。変換の、掛け順は、左から右（`World * View * Projection`） |
| 三角形の表 | 反時計回り（CCW） |
| 角度 | ラジアン |

## 右手系と、左手系

3 本の軸（X、Y、Z）の、向きの、関係です。

| 座標系 | X が右、Y が上のとき、Z は |
| --- | --- |
| 右手系 | 手前（自分に、向かう）。前（奥）は、−Z |
| 左手系 | 奥。前は、+Z |

DirectX は、右手系も、左手系も、扱えます（DirectXMath には、`XMMatrixLookAtRH` と `XMMatrixLookAtLH` の、両方が、あります）。このサイトは、右手系で、統一します。

## クリップ空間と、ビューポート

頂点シェーダーが、出力する、<strong>クリップ空間</strong>の、座標は、ラスタライザーで、`w` で、割られ、<strong>正規化デバイス座標</strong>（NDC）に、なります。

| 軸 | DirectX の、NDC |
| --- | --- |
| x | −1（左）〜 1（右） |
| y | −1（下）〜 1（上） |
| z | <strong>0（近い）〜 1（遠い）</strong> |

OpenGL は、z が −1〜1 ですが、DirectX は、<strong>0〜1</strong> です。射影行列は、DirectX 用（`XMMatrixPerspectiveFovRH`）を、使います。

```text
クリップ空間（y 上向き）            ピクセル座標（y 下向き）
  (-1, 1)  ─────  (1, 1)             (0, 0)     ────── (width, 0)
     │                │                  │                  │
  (-1,-1)  ─────  (1,-1)             (0, height) ────── (width, height)
```

ビューポート変換で、<strong>y が、上下に、反転</strong>します（クリップ空間は、上が +1、ピクセル座標は、上が 0）。

## uv 座標

テクスチャの、uv は、<strong>左上が (0, 0)</strong>、右下が (1, 1)、v が、下向きです。クリップ空間の、y（上向き）とは、逆なので、フルスクリーン三角形などで、変換します。

```hlsl
// クリップ空間 (−1〜1, y 上) → uv (0〜1, y 下)
float2 uv = float2(clip.x, -clip.y) * 0.5 + 0.5;

// uv (0〜1, y 下) → クリップ空間
float2 clip = float2(uv.x, 1.0 - uv.y) * 2.0 - 1.0;
```

OpenGL（左下が (0, 0)）で、作った、素材を、使うときは、v を、`1 − v` に、反転します。

## 三角形の、表裏（巻き順）

三角形の、頂点が、<strong>画面に、投影されたとき</strong>、反時計回りか、時計回りかで、表裏が、決まります。裏面は、カリングで、捨てられます。

| | 表 | このサイトで |
| --- | --- | --- |
| DirectX の、既定 | 時計回り（CW） | — |
| このサイトの、規約 | 反時計回り（CCW） | ラスタライザー ステートで、`FrontCounterClockwise = TRUE`（D3D11）、PSO の `RasterizerState.FrontCounterClockwise = TRUE`（D3D12） |

規約と、既定が、食い違うので、<strong>ラスタライザー ステートを、設定</strong>し忘れると、三角形が、裏面として、捨てられ、何も、見えません。

## 行列の、規約

| 項目 | 規約 |
| --- | --- |
| ベクトル | 行ベクトル。頂点は、`v * M`（左から右へ、変換が、重なる） |
| 掛け順 | `World * View * Projection`。`mul(v, M)`（HLSL） |
| メモリ上の、並び | 行優先（DirectXMath の `XMFLOAT4X4`） |
| HLSL の、既定 | 列優先。`row_major` を、付けて、行優先に、そろえる |

```hlsl
// 行ベクトルの規約: v * M（行列は、右に）。
cbuffer PerObject : register(b0) {
  row_major float4x4 world_view_projection;     // C++ の XMFLOAT4X4 と、同じ並び
};
float4 clip = mul(float4(position, 1.0), world_view_projection);
```

DirectXMath の `XMMatrixMultiply(A, B)` は、「A を、先に、B を、後に、適用」の、意味で、`A * B`（左から右）です。列ベクトル（OpenGL、`M * v`）の、書籍の、式は、順序を、逆に、読み替えます（[DirectXMath](../../gamemath/directxmath.md)、[Transforms and MVP](../../3d/transforms-mvp.md)）。

## 深度の、向き

| 方式 | 近い面 | 遠い面 | クリア値 | `DepthFunc` |
| --- | --- | --- | --- | --- |
| 通常 | 0 | 1 | 1.0 | `LESS` |
| reverse-Z | 1 | 0 | 0.0 | `GREATER` |

reverse-Z は、浮動小数点の、深度と、組み合わせると、遠くの、精度が、大きく、上がります（[Projection](../../3d/projection.md)）。

## よくある、食い違い

| 症状 | 原因 |
| --- | --- |
| 三角形が、見えない | 巻き順が、規約と、既定で、食い違う（`FrontCounterClockwise`） |
| 画像が、上下、逆さま | uv の y と、クリップ空間の y が、反転していない |
| 物が、鏡像になる | 右手系・左手系の、混在（`…RH` と `…LH` の、取り違え） |
| 物が、変な位置に、飛ぶ | 行列の、転置の、取り違え（`row_major`、掛け順） |
| 深度が、逆（近い物が、奥） | reverse-Z の、クリア値と、比較関数が、そろっていない |
| 外部の、モデル・素材が、裏返る | 外部ツールの、座標系（左手系、Z 上、など）との、変換忘れ |

## よくあるミス

??? failure "OpenGL の、記事の、行列の、式を、そのまま、使って、おかしくなる"
    OpenGL は、列ベクトル（`M * v`）、z が −1〜1。DirectX（このサイト）は、行ベクトル（`v * M`）、z が 0〜1。掛け順と、射影行列を、読み替える。

??? failure "`XMMatrixPerspectiveFovLH` を、右手系で、使った"
    右手系なら、`…RH` を、使う。LH と RH を、混ぜると、鏡像になる。

??? failure "テクスチャが、上下反転する"
    uv の v の向きが、素材と、違う。インポート時に、`1 − v` に、反転する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] このサイト: 右手系・Y 上・前は −Z、行ベクトル（`v * M`）、反時計回りが表
    - [x] DirectX の、NDC は z が 0〜1。OpenGL は −1〜1
    - [x] ピクセル・uv は、左上が原点（y 下向き）。クリップ空間は y 上向き
    - [x] 三角形の、既定は、時計回りが表。`FrontCounterClockwise = TRUE` で、合わせる
    - [x] 行列は、行優先。HLSL に `row_major`。`RH` と `LH` を、混ぜない

## 関連ページ

- [DirectX Concepts](index.md)
- [DirectXMath](../../gamemath/directxmath.md)
- [Transforms and MVP](../../3d/transforms-mvp.md)
- [Projection](../../3d/projection.md)
- [Rasterizer State](../dx11/rasterizer-state.md)
