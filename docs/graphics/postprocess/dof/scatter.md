---
title: スキャッター方式
tags:
  - 描画
---

# スキャッター方式

<strong>スキャッター（Scatter）</strong>は、**ギャザーの逆**で、<strong>「各画素が自分の色を、CoC の円盤として周りに広げる（散らす）」</strong>方式の DOF です。<strong>特に明るい小さな点が大きな円盤（ボケ）</strong>として**広がる様子**を**ギャザーより正確に**表現できます。**映画のような、光の玉ボケ**が**得られる**反面、**重い**ため、**使い所を絞り**ます。このページでは、<strong>ギャザーとの違い・スプライトで散らす方法・明るさの扱い・コスト・使い分け（ハイブリッド）</strong>を説明します。

!!! tip "ポイント"
    - スキャッター ＝ <strong>各画素が、自分の色を CoC の大きさの円盤として周りに足し込む</strong>。
    - <strong>ギャザー</strong>は<strong>小さなボケは得意</strong>、<strong>大きな明るいボケの形（玉ボケ）</strong>は<strong>苦手</strong>。<strong>スキャッターは玉ボケが得意</strong>。
    - 実装は<strong>画素ごとにスプライト（板ポリ）を描き、加算ブレンド</strong>。<strong>ジオメトリ数が画素数</strong>になり<strong>重い</strong>。
    - <strong>ボケが大きい（CoC が閾値以上）画素だけ</strong>を<strong>スキャッター</strong>し、<strong>残りはギャザー</strong>にする（<strong>ハイブリッド</strong>）。
    - <strong>明るさ</strong>：<strong>円盤は面積で割って、エネルギーを保存</strong>する。
    - <strong>描画順（奥から手前）</strong>が<strong>重要</strong>。

## ギャザーとの違い

| 項目 | ギャザー（集める） | スキャッター（散らす） |
| --- | --- | --- |
| **発想** | **自分が周りから集める** | **自分が周りへ広げる** |
| **処理の単位** | **出力画素** | <strong>入力画素（スプライト）</strong> |
| **大きな明るいボケ** | **サンプルが足りず、ざらつく・形が出にくい** | **円盤として、正確に出る** |
| **重なりの順序** | **扱いにくい** | **奥から描けば、自然** |
| **コスト** | **サンプル数 × 画素数** | <strong>画素数 × 円盤の面積（描画）</strong> |

<strong>光源が円盤として広がる「玉ボケ」</strong>は、**スキャッターがもっとも得意**です。

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="スキャッター">
<text x="20" y="26" class="fig-title">スキャッター：明るい点が、円盤として広がる</text>
<g transform="translate(40,50)">
<rect x="0" y="0" width="200" height="160" fill="#0f172a"/>
<circle cx="60" cy="60" r="3" fill="#fff7d1"/><circle cx="140" cy="100" r="3" fill="#fff7d1"/><circle cx="90" cy="130" r="3" fill="#fff7d1"/>
<text x="0" y="182" style="font-size:12px">入力：小さな明るい点</text>
</g>
<g transform="translate(300,50)">
<rect x="0" y="0" width="200" height="160" fill="#0f172a"/>
<circle cx="60" cy="60" r="32" fill="#fff7d1" fill-opacity="0.5"/><circle cx="140" cy="100" r="26" fill="#fff7d1" fill-opacity="0.5"/><circle cx="90" cy="130" r="38" fill="#fff7d1" fill-opacity="0.4"/>
<text x="0" y="182" style="font-size:12px">スキャッター：円盤（玉ボケ）</text>
</g>
<g transform="translate(560,50)">
<rect x="0" y="0" width="200" height="160" fill="#0f172a"/>
<circle cx="60" cy="60" r="30" fill="#fff7d1" fill-opacity="0.12"/><circle cx="140" cy="100" r="24" fill="#fff7d1" fill-opacity="0.12"/><circle cx="90" cy="130" r="36" fill="#fff7d1" fill-opacity="0.1"/>
<text x="0" y="182" style="font-size:12px">ギャザー：薄くにじむだけ</text>
</g>
</svg>

## 実装：スプライトで散らす

**各画素について、CoC の大きさの四角形（スプライト）を描き、円盤状のマスクで色を加算**します。

### 方式 1：ジオメトリ シェーダー／メッシュ シェーダー

**画素をポイントとして描き**、**ジオメトリ シェーダー（またはメッシュ シェーダー）で、CoC の大きさの四角形に拡大**します。

```hlsl
struct VSOutput {
  float4 position : SV_POSITION;
  float2 uv : TEXCOORD0;
  float3 color : COLOR0;
  float radius : TEXCOORD1;
};

[maxvertexcount(4)]
void GSMain(point VSInput input[1], inout TriangleStream<VSOutput> stream) {
  float2 center = input[0].position_ndc;
  float radius_ndc = input[0].coc_pixels * texel_ndc;
  float area = 3.14159265 * input[0].coc_pixels * input[0].coc_pixels;
  float3 color = input[0].color / max(area, 1.0);
  VSOutput v;
  v.color = color;
  v.radius = 1.0;
  float2 corners[4] = { float2(-1, -1), float2(-1, 1), float2(1, -1), float2(1, 1) };
  for (int i = 0; i < 4; ++i) {
    v.position = float4(center + corners[i] * radius_ndc, 0, 1);
    v.uv = corners[i];
    stream.Append(v);
  }
}
```

```hlsl
float4 PSMain(VSOutput input) : SV_Target {
  float distance_from_center = length(input.uv);
  float mask = saturate((1.0 - distance_from_center) * 8.0);
  return float4(input.color * mask, 0);
}
```

| 点 | 説明 |
| --- | --- |
| **`area`（円の面積）で割る** | **エネルギー保存**。**大きく広がっても全体の明るさは同じ** |
| <strong>加算ブレンド（ONE, ONE）</strong> | **円盤を重ねて足す** |
| **円盤のマスク** | **`length(uv) < 1` の内側だけ**。**縁を少し滑らかに** |

### 方式 2：コンピュートでタイル分け

**ボケの大きい画素だけを、コンピュートで分類してから描画**する方法もあります。**画素の数が多いので**ボケが大きい画素（CoC が閾値以上）だけ**を**スキャッター**します。

## ハイブリッド（実用の標準）

**全画素をスキャッター**すると**重すぎる**ので、**使い分けます**。

| ボケの大きさ | 方式 |
| --- | --- |
| <strong>小さい（CoC < 数画素）</strong> | **ギャザー**（**またはそのまま**） |
| **大きい（CoC ≥ 閾値）かつ、明るい** | **スキャッター**（**玉ボケ**） |

<strong>「明るい点」だけをスキャッター</strong>するのが**効果的**です（**暗い・平らな領域はギャザーで十分きれい**）。

<!-- fig:dof-scatter-gather:begin -->
<!-- fig:dof-scatter-gather:end -->

## 明るさの扱い

**玉ボケの見た目は、元の点の「明るさ」で決まります**。**HDR の高い値（1 を超える）が、そのまま円盤に広がる**ことで、**明るい玉ボケ**が**できます**。

| 点 | 説明 |
| --- | --- |
| **HDR で処理** | **トーンマップの前**。**明るい点が明るい円盤になる** |
| <strong>面積で割る（エネルギー保存）</strong> | **広げても合計の明るさは同じ**。**円盤は薄く、でも十分明るい** |
| **ファイアフライ** | **極端に明るい 1 点が、巨大な円盤になって目立つ**ので、**輝度のクランプ**を併用 |

## コスト

| 項目 | 内容 |
| --- | --- |
| **ジオメトリ数** | **スキャッターする画素の数**（**数万〜数十万**） |
| **フィルレート** | **円盤の面積の合計**（**大きいボケの画素が多いと、爆発的に増える**） |
| **対策** | **スキャッターを明るい画素だけに限定**・**半解像度・タイルごとの上限** |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **ハイブリッド** | **小さいボケはギャザー、大きく明るいボケだけスキャッター** |
| **半解像度で描く** | **フィルレートを 1/4** |
| **輝度クランプ** | **極端な点で巨大な円盤が出るのを防ぐ** |
| <strong>円盤の中を均一でなく、「縁を明るく」</strong> | **実際のレンズの玉ボケ（縁が明るい）に近づく**（[ボケの形](bokeh-shape.md)） |
| **奥から手前の順** | **前景・背景を別パス**（[前景と背景](near-far.md)） |

## よくあるミス

??? failure "スキャッターで、画面全体が明るくなりすぎる"
    **面積で割っていない**。**エネルギー保存**にする。

??? failure "小さな明るい点が、巨大な円盤になって目立ちすぎる"
    **輝度のクランプ**、**CoC の最大値**を下げる。

??? failure "全画素をスキャッターして、フレームが落ちる"
    **大きく明るい画素だけ**にする（**ハイブリッド**）。

??? failure "前景と背景の円盤が、正しい順序で重ならない"
    **前景・背景を別々の画像に描き、合成**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] スキャッター ＝ <strong>各画素が、色を円盤として周りに広げる</strong>
    - [x] <strong>玉ボケ</strong>（<strong>明るい大きなボケ</strong>）が<strong>得意</strong>。<strong>重い</strong>
    - [x] <strong>面積で割って</strong>エネルギー保存。<strong>加算ブレンド</strong>
    - [x] <strong>ハイブリッド</strong>（<strong>小さいボケはギャザー</strong>）が<strong>実用的</strong>
    - [x] <strong>輝度クランプ</strong>と<strong>半解像度</strong>で<strong>コスト管理</strong>

## 参考

- Sousa, "Graphics Gems from CryENGINE 3"（SIGGRAPH 2013）
- McIntosh et al., "Efficiently Simulating the Bokeh of Polygonal Apertures in a Post-Process Depth of Field Shader"（2012）
- Abadie, "A Life of a Bokeh"（SIGGRAPH 2018, DOOM）

## 関連ページ

- [被写界深度（DOF）](index.md)
- [ギャザー方式](gather.md)
- [前景と背景](near-far.md)
- [ボケの形](bokeh-shape.md)
