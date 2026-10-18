---
title: Scatter Method
tags:
  - 描画
---

# Scatter Method

<strong>スキャッター（Scatter）</strong>は、**ギャザーの逆**で、<strong>「各画素が自分の色を、CoC の円盤として周りに広げる（散らす）」</strong>方式の DOF です。<strong>特に明るい小さな点が大きな円盤（ボケ）</strong>として**広がる様子**を**ギャザーより正確に**表現できます。**映画のような、光の玉ボケ**が**得られる**反面、**重い**ため、**使い所を絞り**ます。このページでは、<strong>ギャザーとの違い・スプライトで散らす方法・明るさの扱い・コスト・使い分け（ハイブリッド）</strong>を説明します。

!!! tip "ポイント"
    - スキャッター ＝ <strong>各画素が、自分の色を CoC の大きさの円盤として周りに足し込む</strong>。
    - <strong>ギャザー</strong>は<strong>小さなボケは得意</strong>、<strong>大きな明るいボケの形（玉ボケ）</strong>は<strong>苦手</strong>。<strong>スキャッターは玉ボケが得意</strong>。
    - 実装は<strong>画素ごとにスプライト（板ポリ）を描き、加算ブレンド</strong>。<strong>ジオメトリ数が画素数</strong>になり<strong>重い</strong>。
    - <strong>ボケが大きい（CoC が閾値以上）画素だけ</strong>を<strong>スキャッター</strong>し、<strong>残りはギャザー</strong>にする（<strong>ハイブリッド</strong>）。
    - <strong>明るさ</strong>：<strong>円盤は面積で割って、エネルギーを保存</strong>する。
    - <strong>描画順（奥から手前）</strong>が<strong>重要</strong>。

## ギャザーとの違い

ギャザーとの違いを整理します。発想は、ギャザーが自分が周りから集めるのに対し、スキャッターは自分が周りへ広げます。処理の単位は、ギャザーが出力画素、スキャッターが入力画素（スプライト）です。大きな明るいボケは、ギャザーではサンプルが足りずざらつき、形が出にくいのに対し、スキャッターでは円盤として正確に出ます。重なりの順序は、ギャザーでは扱いにくく、スキャッターなら奥から描けば自然です。コストは、ギャザーがサンプル数に画素数を掛けた量、スキャッターが画素数に円盤の面積を掛けた量（描画）です。

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

コードの要点です。円の面積で割るのは、エネルギー保存のためで、大きく広がっても全体の明るさは同じになります。加算ブレンド（ONE, ONE）で、円盤を重ねて足します。円盤のマスクは `length(uv) < 1` の内側だけで、縁は少し滑らかにします。

### 方式 2：コンピュートでタイル分け

**ボケの大きい画素だけを、コンピュートで分類してから描画**する方法もあります。**画素の数が多いので**ボケが大きい画素（CoC が閾値以上）だけ**を**スキャッター**します。

## ハイブリッド（実用の標準）

**全画素をスキャッター**すると**重すぎる**ので、**使い分けます**。

全画素をスキャッターすると重すぎるので、使い分けます。ボケが小さい（CoC が数画素未満）ならギャザー、またはそのままにします。ボケが大きく（CoC がしきい値以上）、かつ明るいなら、スキャッターで玉ボケを作ります。

<strong>「明るい点」だけをスキャッター</strong>するのが**効果的**です（**暗い・平らな領域はギャザーで十分きれい**）。

<!-- fig:dof-scatter-gather:begin -->

<svg class="fig illust motion" data-fig="dof-scatter-gather" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-dof-scatter-gather" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">ギャザー（集める）とスキャッター（まき散らす）</text>
<text x="30" y="68" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">ギャザー:画素が、周りから集める</text>
<rect x="30" y="90" width="29" height="29" fill="#f1f5f9"/>
<rect x="60" y="90" width="29" height="29" fill="#f1f5f9"/>
<rect x="90" y="90" width="29" height="29" fill="#f1f5f9"/>
<rect x="120" y="90" width="29" height="29" fill="#f1f5f9"/>
<rect x="150" y="90" width="29" height="29" fill="#f1f5f9"/>
<rect x="180" y="90" width="29" height="29" fill="#f1f5f9"/>
<rect x="210" y="90" width="29" height="29" fill="#f1f5f9"/>
<rect x="240" y="90" width="29" height="29" fill="#f1f5f9"/>
<rect x="270" y="90" width="29" height="29" fill="#f1f5f9"/>
<rect x="30" y="120" width="29" height="29" fill="#f1f5f9"/>
<rect x="60" y="120" width="29" height="29" fill="#f1f5f9"/>
<rect x="90" y="120" width="29" height="29" fill="#f1f5f9"/>
<rect x="120" y="120" width="29" height="29" fill="#f1f5f9"/>
<rect x="150" y="120" width="29" height="29" fill="#f1f5f9"/>
<rect x="180" y="120" width="29" height="29" fill="#f1f5f9"/>
<rect x="210" y="120" width="29" height="29" fill="#f1f5f9"/>
<rect x="240" y="120" width="29" height="29" fill="#f1f5f9"/>
<rect x="270" y="120" width="29" height="29" fill="#f1f5f9"/>
<rect x="30" y="150" width="29" height="29" fill="#f1f5f9"/>
<rect x="60" y="150" width="29" height="29" fill="#f1f5f9"/>
<rect x="90" y="150" width="29" height="29" fill="#f1f5f9"/>
<rect x="120" y="150" width="29" height="29" fill="#f1f5f9"/>
<rect x="150" y="150" width="29" height="29" fill="#f1f5f9"/>
<rect x="180" y="150" width="29" height="29" fill="#f1f5f9"/>
<rect x="210" y="150" width="29" height="29" fill="#f1f5f9"/>
<rect x="240" y="150" width="29" height="29" fill="#f1f5f9"/>
<rect x="270" y="150" width="29" height="29" fill="#f1f5f9"/>
<rect x="30" y="180" width="29" height="29" fill="#f1f5f9"/>
<rect x="60" y="180" width="29" height="29" fill="#f1f5f9"/>
<rect x="90" y="180" width="29" height="29" fill="#f1f5f9"/>
<rect x="120" y="180" width="29" height="29" fill="#f1f5f9"/>
<rect x="150" y="180" width="29" height="29" fill="#f1f5f9"/>
<rect x="180" y="180" width="29" height="29" fill="#f1f5f9"/>
<rect x="210" y="180" width="29" height="29" fill="#f1f5f9"/>
<rect x="240" y="180" width="29" height="29" fill="#f1f5f9"/>
<rect x="270" y="180" width="29" height="29" fill="#f1f5f9"/>
<rect x="30" y="210" width="29" height="29" fill="#f1f5f9"/>
<rect x="60" y="210" width="29" height="29" fill="#f1f5f9"/>
<rect x="90" y="210" width="29" height="29" fill="#f1f5f9"/>
<rect x="120" y="210" width="29" height="29" fill="#f1f5f9"/>
<rect x="150" y="210" width="29" height="29" fill="#f1f5f9"/>
<rect x="180" y="210" width="29" height="29" fill="#f1f5f9"/>
<rect x="210" y="210" width="29" height="29" fill="#f1f5f9"/>
<rect x="240" y="210" width="29" height="29" fill="#f1f5f9"/>
<rect x="270" y="210" width="29" height="29" fill="#f1f5f9"/>
<rect x="30" y="240" width="29" height="29" fill="#f1f5f9"/>
<rect x="60" y="240" width="29" height="29" fill="#f1f5f9"/>
<rect x="90" y="240" width="29" height="29" fill="#f1f5f9"/>
<rect x="120" y="240" width="29" height="29" fill="#f1f5f9"/>
<rect x="150" y="240" width="29" height="29" fill="#f1f5f9"/>
<rect x="180" y="240" width="29" height="29" fill="#f1f5f9"/>
<rect x="210" y="240" width="29" height="29" fill="#f1f5f9"/>
<rect x="240" y="240" width="29" height="29" fill="#f1f5f9"/>
<rect x="270" y="240" width="29" height="29" fill="#f1f5f9"/>
<rect x="30" y="270" width="29" height="29" fill="#f1f5f9"/>
<rect x="60" y="270" width="29" height="29" fill="#f1f5f9"/>
<rect x="90" y="270" width="29" height="29" fill="#f1f5f9"/>
<rect x="120" y="270" width="29" height="29" fill="#f1f5f9"/>
<rect x="150" y="270" width="29" height="29" fill="#f1f5f9"/>
<rect x="180" y="270" width="29" height="29" fill="#f1f5f9"/>
<rect x="210" y="270" width="29" height="29" fill="#f1f5f9"/>
<rect x="240" y="270" width="29" height="29" fill="#f1f5f9"/>
<rect x="270" y="270" width="29" height="29" fill="#f1f5f9"/>
<rect x="30" y="300" width="29" height="29" fill="#f1f5f9"/>
<rect x="60" y="300" width="29" height="29" fill="#f1f5f9"/>
<rect x="90" y="300" width="29" height="29" fill="#f1f5f9"/>
<rect x="120" y="300" width="29" height="29" fill="#f1f5f9"/>
<rect x="150" y="300" width="29" height="29" fill="#f1f5f9"/>
<rect x="180" y="300" width="29" height="29" fill="#f1f5f9"/>
<rect x="210" y="300" width="29" height="29" fill="#f1f5f9"/>
<rect x="240" y="300" width="29" height="29" fill="#f1f5f9"/>
<rect x="270" y="300" width="29" height="29" fill="#f1f5f9"/>
<rect x="30" y="330" width="29" height="29" fill="#f1f5f9"/>
<rect x="60" y="330" width="29" height="29" fill="#f1f5f9"/>
<rect x="90" y="330" width="29" height="29" fill="#f1f5f9"/>
<rect x="120" y="330" width="29" height="29" fill="#f1f5f9"/>
<rect x="150" y="330" width="29" height="29" fill="#f1f5f9"/>
<rect x="180" y="330" width="29" height="29" fill="#f1f5f9"/>
<rect x="210" y="330" width="29" height="29" fill="#f1f5f9"/>
<rect x="240" y="330" width="29" height="29" fill="#f1f5f9"/>
<rect x="270" y="330" width="29" height="29" fill="#f1f5f9"/>
<text x="410" y="68" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">スキャッター:明るい画素が、周りへまく</text>
<rect x="410" y="90" width="29" height="29" fill="#f1f5f9"/>
<rect x="440" y="90" width="29" height="29" fill="#f1f5f9"/>
<rect x="470" y="90" width="29" height="29" fill="#f1f5f9"/>
<rect x="500" y="90" width="29" height="29" fill="#f1f5f9"/>
<rect x="530" y="90" width="29" height="29" fill="#f1f5f9"/>
<rect x="560" y="90" width="29" height="29" fill="#f1f5f9"/>
<rect x="590" y="90" width="29" height="29" fill="#f1f5f9"/>
<rect x="620" y="90" width="29" height="29" fill="#f1f5f9"/>
<rect x="650" y="90" width="29" height="29" fill="#f1f5f9"/>
<rect x="410" y="120" width="29" height="29" fill="#f1f5f9"/>
<rect x="440" y="120" width="29" height="29" fill="#f1f5f9"/>
<rect x="470" y="120" width="29" height="29" fill="#f1f5f9"/>
<rect x="500" y="120" width="29" height="29" fill="#f1f5f9"/>
<rect x="530" y="120" width="29" height="29" fill="#f1f5f9"/>
<rect x="560" y="120" width="29" height="29" fill="#f1f5f9"/>
<rect x="590" y="120" width="29" height="29" fill="#f1f5f9"/>
<rect x="620" y="120" width="29" height="29" fill="#f1f5f9"/>
<rect x="650" y="120" width="29" height="29" fill="#f1f5f9"/>
<rect x="410" y="150" width="29" height="29" fill="#f1f5f9"/>
<rect x="440" y="150" width="29" height="29" fill="#f1f5f9"/>
<rect x="470" y="150" width="29" height="29" fill="#f1f5f9"/>
<rect x="500" y="150" width="29" height="29" fill="#f1f5f9"/>
<rect x="530" y="150" width="29" height="29" fill="#f1f5f9"/>
<rect x="560" y="150" width="29" height="29" fill="#f1f5f9"/>
<rect x="590" y="150" width="29" height="29" fill="#f1f5f9"/>
<rect x="620" y="150" width="29" height="29" fill="#f1f5f9"/>
<rect x="650" y="150" width="29" height="29" fill="#f1f5f9"/>
<rect x="410" y="180" width="29" height="29" fill="#f1f5f9"/>
<rect x="440" y="180" width="29" height="29" fill="#f1f5f9"/>
<rect x="470" y="180" width="29" height="29" fill="#f1f5f9"/>
<rect x="500" y="180" width="29" height="29" fill="#f1f5f9"/>
<rect x="530" y="180" width="29" height="29" fill="#f1f5f9"/>
<rect x="560" y="180" width="29" height="29" fill="#f1f5f9"/>
<rect x="590" y="180" width="29" height="29" fill="#f1f5f9"/>
<rect x="620" y="180" width="29" height="29" fill="#f1f5f9"/>
<rect x="650" y="180" width="29" height="29" fill="#f1f5f9"/>
<rect x="410" y="210" width="29" height="29" fill="#f1f5f9"/>
<rect x="440" y="210" width="29" height="29" fill="#f1f5f9"/>
<rect x="470" y="210" width="29" height="29" fill="#f1f5f9"/>
<rect x="500" y="210" width="29" height="29" fill="#f1f5f9"/>
<rect x="530" y="210" width="29" height="29" fill="#f1f5f9"/>
<rect x="560" y="210" width="29" height="29" fill="#f1f5f9"/>
<rect x="590" y="210" width="29" height="29" fill="#f1f5f9"/>
<rect x="620" y="210" width="29" height="29" fill="#f1f5f9"/>
<rect x="650" y="210" width="29" height="29" fill="#f1f5f9"/>
<rect x="410" y="240" width="29" height="29" fill="#f1f5f9"/>
<rect x="440" y="240" width="29" height="29" fill="#f1f5f9"/>
<rect x="470" y="240" width="29" height="29" fill="#f1f5f9"/>
<rect x="500" y="240" width="29" height="29" fill="#f1f5f9"/>
<rect x="530" y="240" width="29" height="29" fill="#f1f5f9"/>
<rect x="560" y="240" width="29" height="29" fill="#f1f5f9"/>
<rect x="590" y="240" width="29" height="29" fill="#f1f5f9"/>
<rect x="620" y="240" width="29" height="29" fill="#f1f5f9"/>
<rect x="650" y="240" width="29" height="29" fill="#f1f5f9"/>
<rect x="410" y="270" width="29" height="29" fill="#f1f5f9"/>
<rect x="440" y="270" width="29" height="29" fill="#f1f5f9"/>
<rect x="470" y="270" width="29" height="29" fill="#f1f5f9"/>
<rect x="500" y="270" width="29" height="29" fill="#f1f5f9"/>
<rect x="530" y="270" width="29" height="29" fill="#f1f5f9"/>
<rect x="560" y="270" width="29" height="29" fill="#f1f5f9"/>
<rect x="590" y="270" width="29" height="29" fill="#f1f5f9"/>
<rect x="620" y="270" width="29" height="29" fill="#f1f5f9"/>
<rect x="650" y="270" width="29" height="29" fill="#f1f5f9"/>
<rect x="410" y="300" width="29" height="29" fill="#f1f5f9"/>
<rect x="440" y="300" width="29" height="29" fill="#f1f5f9"/>
<rect x="470" y="300" width="29" height="29" fill="#f1f5f9"/>
<rect x="500" y="300" width="29" height="29" fill="#f1f5f9"/>
<rect x="530" y="300" width="29" height="29" fill="#f1f5f9"/>
<rect x="560" y="300" width="29" height="29" fill="#f1f5f9"/>
<rect x="590" y="300" width="29" height="29" fill="#f1f5f9"/>
<rect x="620" y="300" width="29" height="29" fill="#f1f5f9"/>
<rect x="650" y="300" width="29" height="29" fill="#f1f5f9"/>
<rect x="410" y="330" width="29" height="29" fill="#f1f5f9"/>
<rect x="440" y="330" width="29" height="29" fill="#f1f5f9"/>
<rect x="470" y="330" width="29" height="29" fill="#f1f5f9"/>
<rect x="500" y="330" width="29" height="29" fill="#f1f5f9"/>
<rect x="530" y="330" width="29" height="29" fill="#f1f5f9"/>
<rect x="560" y="330" width="29" height="29" fill="#f1f5f9"/>
<rect x="590" y="330" width="29" height="29" fill="#f1f5f9"/>
<rect x="620" y="330" width="29" height="29" fill="#f1f5f9"/>
<rect x="650" y="330" width="29" height="29" fill="#f1f5f9"/>
<rect x="148" y="208" width="33" height="33" fill="none" stroke="#e5aa28" stroke-width="4"/>
<circle cx="135.0" cy="135.0" r="5" fill="#2563eb" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="0;0;1;1"/></circle>
<line x1="135.0" y1="135.0" x2="165.0" y2="225.0" stroke="#2563eb" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="0;0;1;1"/></line>
<circle cx="195.0" cy="135.0" r="5" fill="#2563eb" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0864;0.0867;1.0000" values="0;0;1;1"/></circle>
<line x1="195.0" y1="135.0" x2="165.0" y2="225.0" stroke="#2563eb" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0864;0.0867;1.0000" values="0;0;1;1"/></line>
<circle cx="105.0" cy="165.0" r="5" fill="#2563eb" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0990;0.0993;1.0000" values="0;0;1;1"/></circle>
<line x1="105.0" y1="165.0" x2="165.0" y2="225.0" stroke="#2563eb" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0990;0.0993;1.0000" values="0;0;1;1"/></line>
<circle cx="165.0" cy="165.0" r="5" fill="#2563eb" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1116;0.1119;1.0000" values="0;0;1;1"/></circle>
<line x1="165.0" y1="165.0" x2="165.0" y2="225.0" stroke="#2563eb" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1116;0.1119;1.0000" values="0;0;1;1"/></line>
<circle cx="225.0" cy="165.0" r="5" fill="#2563eb" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1241;0.1244;1.0000" values="0;0;1;1"/></circle>
<line x1="225.0" y1="165.0" x2="165.0" y2="225.0" stroke="#2563eb" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1241;0.1244;1.0000" values="0;0;1;1"/></line>
<circle cx="75.0" cy="195.0" r="5" fill="#2563eb" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1367;0.1370;1.0000" values="0;0;1;1"/></circle>
<line x1="75.0" y1="195.0" x2="165.0" y2="225.0" stroke="#2563eb" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1367;0.1370;1.0000" values="0;0;1;1"/></line>
<circle cx="135.0" cy="195.0" r="5" fill="#2563eb" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1493;0.1496;1.0000" values="0;0;1;1"/></circle>
<line x1="135.0" y1="195.0" x2="165.0" y2="225.0" stroke="#2563eb" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1493;0.1496;1.0000" values="0;0;1;1"/></line>
<circle cx="195.0" cy="195.0" r="5" fill="#2563eb" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1619;0.1622;1.0000" values="0;0;1;1"/></circle>
<line x1="195.0" y1="195.0" x2="165.0" y2="225.0" stroke="#2563eb" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1619;0.1622;1.0000" values="0;0;1;1"/></line>
<circle cx="255.0" cy="195.0" r="5" fill="#2563eb" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1745;0.1748;1.0000" values="0;0;1;1"/></circle>
<line x1="255.0" y1="195.0" x2="165.0" y2="225.0" stroke="#2563eb" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1745;0.1748;1.0000" values="0;0;1;1"/></line>
<circle cx="105.0" cy="225.0" r="5" fill="#2563eb" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1871;0.1874;1.0000" values="0;0;1;1"/></circle>
<line x1="105.0" y1="225.0" x2="165.0" y2="225.0" stroke="#2563eb" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1871;0.1874;1.0000" values="0;0;1;1"/></line>
<circle cx="225.0" cy="225.0" r="5" fill="#2563eb" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1997;0.2000;1.0000" values="0;0;1;1"/></circle>
<line x1="225.0" y1="225.0" x2="165.0" y2="225.0" stroke="#2563eb" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1997;0.2000;1.0000" values="0;0;1;1"/></line>
<circle cx="75.0" cy="255.0" r="5" fill="#2563eb" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2123;0.2126;1.0000" values="0;0;1;1"/></circle>
<line x1="75.0" y1="255.0" x2="165.0" y2="225.0" stroke="#2563eb" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2123;0.2126;1.0000" values="0;0;1;1"/></line>
<circle cx="135.0" cy="255.0" r="5" fill="#2563eb" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2249;0.2252;1.0000" values="0;0;1;1"/></circle>
<line x1="135.0" y1="255.0" x2="165.0" y2="225.0" stroke="#2563eb" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2249;0.2252;1.0000" values="0;0;1;1"/></line>
<circle cx="195.0" cy="255.0" r="5" fill="#2563eb" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2375;0.2378;1.0000" values="0;0;1;1"/></circle>
<line x1="195.0" y1="255.0" x2="165.0" y2="225.0" stroke="#2563eb" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2375;0.2378;1.0000" values="0;0;1;1"/></line>
<circle cx="255.0" cy="255.0" r="5" fill="#2563eb" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2501;0.2504;1.0000" values="0;0;1;1"/></circle>
<line x1="255.0" y1="255.0" x2="165.0" y2="225.0" stroke="#2563eb" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2501;0.2504;1.0000" values="0;0;1;1"/></line>
<circle cx="105.0" cy="285.0" r="5" fill="#2563eb" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2627;0.2630;1.0000" values="0;0;1;1"/></circle>
<line x1="105.0" y1="285.0" x2="165.0" y2="225.0" stroke="#2563eb" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2627;0.2630;1.0000" values="0;0;1;1"/></line>
<circle cx="165.0" cy="285.0" r="5" fill="#2563eb" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2753;0.2756;1.0000" values="0;0;1;1"/></circle>
<line x1="165.0" y1="285.0" x2="165.0" y2="225.0" stroke="#2563eb" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2753;0.2756;1.0000" values="0;0;1;1"/></line>
<circle cx="225.0" cy="285.0" r="5" fill="#2563eb" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2879;0.2881;1.0000" values="0;0;1;1"/></circle>
<line x1="225.0" y1="285.0" x2="165.0" y2="225.0" stroke="#2563eb" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2879;0.2881;1.0000" values="0;0;1;1"/></line>
<circle cx="135.0" cy="315.0" r="5" fill="#2563eb" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3004;0.3007;1.0000" values="0;0;1;1"/></circle>
<line x1="135.0" y1="315.0" x2="165.0" y2="225.0" stroke="#2563eb" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3004;0.3007;1.0000" values="0;0;1;1"/></line>
<circle cx="195.0" cy="315.0" r="5" fill="#2563eb" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3130;0.3133;1.0000" values="0;0;1;1"/></circle>
<line x1="195.0" y1="315.0" x2="165.0" y2="225.0" stroke="#2563eb" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3130;0.3133;1.0000" values="0;0;1;1"/></line>
<rect x="530" y="210" width="29" height="29" fill="#e5aa28"/>
<rect x="500" y="120" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5635" values="#f1f5f9;#fed7aa"/></rect>
<rect x="530" y="120" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5593" values="#f1f5f9;#fed7aa"/></rect>
<rect x="560" y="120" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5635" values="#f1f5f9;#fed7aa"/></rect>
<rect x="470" y="150" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5548" values="#f1f5f9;#fed7aa"/></rect>
<rect x="500" y="150" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5395" values="#f1f5f9;#fed7aa"/></rect>
<rect x="530" y="150" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5333" values="#f1f5f9;#fed7aa"/></rect>
<rect x="560" y="150" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5395" values="#f1f5f9;#fed7aa"/></rect>
<rect x="590" y="150" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5548" values="#f1f5f9;#fed7aa"/></rect>
<rect x="440" y="180" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5635" values="#f1f5f9;#fed7aa"/></rect>
<rect x="470" y="180" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5395" values="#f1f5f9;#fed7aa"/></rect>
<rect x="500" y="180" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5181" values="#f1f5f9;#fed7aa"/></rect>
<rect x="530" y="180" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5074" values="#f1f5f9;#fed7aa"/></rect>
<rect x="560" y="180" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5181" values="#f1f5f9;#fed7aa"/></rect>
<rect x="590" y="180" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5395" values="#f1f5f9;#fed7aa"/></rect>
<rect x="620" y="180" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5635" values="#f1f5f9;#fed7aa"/></rect>
<rect x="440" y="210" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5593" values="#f1f5f9;#fed7aa"/></rect>
<rect x="470" y="210" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5333" values="#f1f5f9;#fed7aa"/></rect>
<rect x="500" y="210" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5074" values="#f1f5f9;#fed7aa"/></rect>
<rect x="560" y="210" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5074" values="#f1f5f9;#fed7aa"/></rect>
<rect x="590" y="210" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5333" values="#f1f5f9;#fed7aa"/></rect>
<rect x="620" y="210" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5593" values="#f1f5f9;#fed7aa"/></rect>
<rect x="440" y="240" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5635" values="#f1f5f9;#fed7aa"/></rect>
<rect x="470" y="240" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5395" values="#f1f5f9;#fed7aa"/></rect>
<rect x="500" y="240" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5181" values="#f1f5f9;#fed7aa"/></rect>
<rect x="530" y="240" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5074" values="#f1f5f9;#fed7aa"/></rect>
<rect x="560" y="240" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5181" values="#f1f5f9;#fed7aa"/></rect>
<rect x="590" y="240" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5395" values="#f1f5f9;#fed7aa"/></rect>
<rect x="620" y="240" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5635" values="#f1f5f9;#fed7aa"/></rect>
<rect x="470" y="270" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5548" values="#f1f5f9;#fed7aa"/></rect>
<rect x="500" y="270" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5395" values="#f1f5f9;#fed7aa"/></rect>
<rect x="530" y="270" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5333" values="#f1f5f9;#fed7aa"/></rect>
<rect x="560" y="270" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5395" values="#f1f5f9;#fed7aa"/></rect>
<rect x="590" y="270" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5548" values="#f1f5f9;#fed7aa"/></rect>
<rect x="500" y="300" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5635" values="#f1f5f9;#fed7aa"/></rect>
<rect x="530" y="300" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5593" values="#f1f5f9;#fed7aa"/></rect>
<rect x="560" y="300" width="29" height="29" fill="#f1f5f9"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5635" values="#f1f5f9;#fed7aa"/></rect>
<text x="30" y="390" text-anchor="start" style="font-size:13px;font-weight:500;fill:#1f2937" opacity="0">ギャザー:1 画素ごとに、決まった数を集める（コストが一定。重なりの扱いが難しい）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4441;0.4444;1.0000" values="1;1;0;0"/></text>
<text x="30" y="390" text-anchor="start" style="font-size:13px;font-weight:500;fill:#1f2937" opacity="0">スキャッター:明るい点の分だけ、円盤を描く（コスト = 点の数 × 面積。ボケの形がきれい）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4441;0.4444;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="30" y="412" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043" opacity="0">実用:明るい点だけスキャッター ＋ 残りはギャザー（ハイブリッド）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6293;0.6296;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:dof-scatter-gather:end -->

## 明るさの扱い

**玉ボケの見た目は、元の点の「明るさ」で決まります**。**HDR の高い値（1 を超える）が、そのまま円盤に広がる**ことで、**明るい玉ボケ**が**できます**。

玉ボケの見た目は、元の点の明るさで決まります。HDR の高い値（1 を超える）が、そのまま円盤に広がるので、明るい玉ボケができます。そのため、トーンマップの前の HDR で処理します。面積で割る（エネルギー保存）ことで、広げても合計の明るさは同じになり、円盤は薄くても十分明るくなります。極端に明るい 1 点が巨大な円盤になって目立つファイアフライには、輝度のクランプを併用します。

## コスト

コストです。ジオメトリ数は、スキャッターする画素の数で、数万〜数十万になります。フィルレートは、円盤の面積の合計で、大きいボケの画素が多いと爆発的に増えます。対策は、スキャッターを明るい画素だけに限定する、半解像度にする、タイルごとの上限を設ける、といった方法です。

## より良いやり方

より良いやり方を挙げます。小さいボケはギャザー、大きく明るいボケだけスキャッターというハイブリッドにします。半解像度で描いてフィルレートを 1/4 にします。輝度クランプで、極端な点が巨大な円盤になるのを防ぎます。円盤の中を均一でなく縁を明るくして、実際のレンズの玉ボケに近づけます（[Bokeh Shape](bokeh-shape.md)）。奥から手前の順に、前景と背景を別パスで描きます（[Foreground and Background](near-far.md)）。

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

- [Depth of Field (DOF)](index.md)
- [Gather Method](gather.md)
- [Foreground and Background](near-far.md)
- [Bokeh Shape](bokeh-shape.md)
