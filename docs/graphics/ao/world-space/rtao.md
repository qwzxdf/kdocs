---
title: レイトレース AO（RTAO）
tags:
  - 描画
---

# レイトレース AO（RTAO）

**レイトレース AO は、シェーディングする点から、半球にレイを何本か飛ばし、一定距離以内に当たった割合を数えて、AO を求めます**。**ハードウェア レイトレーシングを使えば、画面外や薄い物も含めて、正確な AO** が**得られます**。**レイ数が少ないとノイズが多い**ので、**デノイズが必須**です。このページでは、**仕組み・実装・レイ数とデノイズ・コスト**を説明します。

!!! tip "ポイント"
    - **RTAO ＝ 半球にレイを飛ばし、半径内で当たったら遮蔽**。
    - **レイは、コサイン重みで分布**させる。
    - **1 ピクセル 1〜2 レイ ＋ デノイズ**が**実用的**。
    - **画面外・薄い物の裏側も正しい**。

## レイトレース AO（RTAO）
**DXR**（DirectX Raytracing）などのレイトレーシングで、**三角形に実際にレイを飛ばして**、AO を求めます。

<!-- fig:rtao-rays:begin -->

<svg class="fig illust motion" data-fig="rtao-rays" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-rtao-rays" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">RTAO:半球に短いレイを飛ばして、当たった割合が遮蔽</text>
<rect x="40" y="320" width="700" height="16" fill="#d6c7a1"/>
<rect x="460" y="200" width="90" height="120" fill="#b8794b" stroke="#7a4b2a" stroke-width="2"/>
<rect x="200" y="260" width="60" height="60" fill="#b8794b" stroke="#7a4b2a" stroke-width="2"/>
<circle cx="390" cy="320" r="8" fill="#2563eb" stroke="#ffffff" stroke-width="2"/>
<line x1="390" y1="316" x2="460.11" y2="296.34" stroke="#e5484d" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="0;0;1;1"/></line>
<circle cx="460.11" cy="296.34" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="0;0;1;1"/></circle>
<line x1="390" y1="316" x2="460.25" y2="281.73" stroke="#e5484d" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1145;0.1148;1.0000" values="0;0;1;1"/></line>
<circle cx="460.25" cy="281.73" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1145;0.1148;1.0000" values="0;0;1;1"/></circle>
<line x1="390" y1="316" x2="460.81" y2="276.69" stroke="#e5484d" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1553;0.1556;1.0000" values="0;0;1;1"/></line>
<circle cx="460.81" cy="276.69" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1553;0.1556;1.0000" values="0;0;1;1"/></circle>
<line x1="390" y1="316" x2="460.95" y2="256.83" stroke="#e5484d" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1960;0.1963;1.0000" values="0;0;1;1"/></line>
<circle cx="460.95" cy="256.83" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1960;0.1963;1.0000" values="0;0;1;1"/></circle>
<line x1="390" y1="316" x2="460.03" y2="209.29" stroke="#e5484d" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2367;0.2370;1.0000" values="0;0;1;1"/></line>
<circle cx="460.03" cy="209.29" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2367;0.2370;1.0000" values="0;0;1;1"/></circle>
<line x1="390" y1="316" x2="464.58" y2="145.25" stroke="#2ea043" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2775;0.2778;1.0000" values="0;0;1;1"/></line>
<circle cx="464.58" cy="145.25" r="4" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2775;0.2778;1.0000" values="0;0;1;1"/></circle>
<line x1="390" y1="316" x2="434.81" y2="135.36" stroke="#2ea043" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3182;0.3185;1.0000" values="0;0;1;1"/></line>
<circle cx="434.81" cy="135.36" r="4" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3182;0.3185;1.0000" values="0;0;1;1"/></circle>
<line x1="390" y1="316" x2="411.62" y2="131.23" stroke="#2ea043" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3590;0.3593;1.0000" values="0;0;1;1"/></line>
<circle cx="411.62" cy="131.23" r="4" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3590;0.3593;1.0000" values="0;0;1;1"/></circle>
<line x1="390" y1="316" x2="370.64" y2="130.99" stroke="#2ea043" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3997;0.4000;1.0000" values="0;0;1;1"/></line>
<circle cx="370.64" cy="130.99" r="4" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3997;0.4000;1.0000" values="0;0;1;1"/></circle>
<line x1="390" y1="316" x2="338.09" y2="137.23" stroke="#2ea043" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4404;0.4407;1.0000" values="0;0;1;1"/></line>
<circle cx="338.09" cy="137.23" r="4" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4404;0.4407;1.0000" values="0;0;1;1"/></circle>
<line x1="390" y1="316" x2="307.76" y2="148.72" stroke="#2ea043" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4812;0.4815;1.0000" values="0;0;1;1"/></line>
<circle cx="307.76" cy="148.72" r="4" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4812;0.4815;1.0000" values="0;0;1;1"/></circle>
<line x1="390" y1="316" x2="288.57" y2="159.34" stroke="#2ea043" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5219;0.5222;1.0000" values="0;0;1;1"/></line>
<circle cx="288.57" cy="159.34" r="4" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5219;0.5222;1.0000" values="0;0;1;1"/></circle>
<line x1="390" y1="316" x2="256.96" y2="184.36" stroke="#2ea043" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5627;0.5630;1.0000" values="0;0;1;1"/></line>
<circle cx="256.96" cy="184.36" r="4" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5627;0.5630;1.0000" values="0;0;1;1"/></circle>
<line x1="390" y1="316" x2="236.0" y2="208.72" stroke="#2ea043" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6034;0.6037;1.0000" values="0;0;1;1"/></line>
<circle cx="236.0" cy="208.72" r="4" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6034;0.6037;1.0000" values="0;0;1;1"/></circle>
<line x1="390" y1="316" x2="258.58" y2="263.63" stroke="#e5484d" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6441;0.6444;1.0000" values="0;0;1;1"/></line>
<circle cx="258.58" cy="263.63" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6441;0.6444;1.0000" values="0;0;1;1"/></circle>
<line x1="390" y1="316" x2="258.48" y2="294.34" stroke="#e5484d" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6849;0.6852;1.0000" values="0;0;1;1"/></line>
<circle cx="258.48" cy="294.34" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6849;0.6852;1.0000" values="0;0;1;1"/></circle>
<text x="40" y="66" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">レイ 1 / 16:遮蔽物に当たった（赤）   当たり 1 本<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.1145;0.1148;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="66" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">レイ 2 / 16:遮蔽物に当たった（赤）   当たり 2 本<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1145;0.1148;0.1553;0.1556;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="66" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">レイ 3 / 16:遮蔽物に当たった（赤）   当たり 3 本<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1553;0.1556;0.1960;0.1963;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="66" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">レイ 4 / 16:遮蔽物に当たった（赤）   当たり 4 本<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1960;0.1963;0.2367;0.2370;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="66" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">レイ 5 / 16:遮蔽物に当たった（赤）   当たり 5 本<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2367;0.2370;0.2775;0.2778;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="66" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">レイ 6 / 16:届いた（緑）   当たり 5 本<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2775;0.2778;0.3182;0.3185;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="66" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">レイ 7 / 16:届いた（緑）   当たり 5 本<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3182;0.3185;0.3590;0.3593;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="66" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">レイ 8 / 16:届いた（緑）   当たり 5 本<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3590;0.3593;0.3997;0.4000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="66" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">レイ 9 / 16:届いた（緑）   当たり 5 本<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3997;0.4000;0.4404;0.4407;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="66" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">レイ 10 / 16:届いた（緑）   当たり 5 本<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4404;0.4407;0.4812;0.4815;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="66" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">レイ 11 / 16:届いた（緑）   当たり 5 本<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4812;0.4815;0.5219;0.5222;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="66" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">レイ 12 / 16:届いた（緑）   当たり 5 本<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5219;0.5222;0.5627;0.5630;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="66" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">レイ 13 / 16:届いた（緑）   当たり 5 本<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5627;0.5630;0.6034;0.6037;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="66" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">レイ 14 / 16:届いた（緑）   当たり 5 本<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6034;0.6037;0.6441;0.6444;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="66" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">レイ 15 / 16:遮蔽物に当たった（赤）   当たり 6 本<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6441;0.6444;0.6849;0.6852;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="66" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">レイ 16 / 16:遮蔽物に当たった（赤）   当たり 7 本<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6849;0.6852;0.7256;0.7259;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="66" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">遮蔽 = 7 / 16 → AO = 1 − 0.44 = 0.56<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7256;0.7259;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="396" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">レイの長さは短く（AO の半径）。1 画素 1〜2 本 ＋ デノイズで使う。画面外の物体の遮蔽も、正確に得られる。</text>
</svg>

<!-- fig:rtao-rays:end -->

### 手順

RTAO のアルゴリズムは、とても単純です。

まず、G-Buffer から、画素のワールド位置と法線を得ます。次に、法線の側の半球に、<strong>コサイン分布</strong>でレイの方向を作ります。コサイン分布とは、法線に近い方向ほど多く選ばれる分布です。この分布で方向を選ぶと、AO の積分にある `n·ω` の重みと確率密度が打ち消し合って、<strong>AO は単に「遮られなかったレイの割合」</strong>になります（[Approximating the Integral](../theory/approximation.md)）。重みを別に掛ける必要がないので、実装が簡単です。

レイは、最大距離 R（AO の影響半径）まで飛ばします。ここで知りたいのは「当たったかどうか」だけで、どこで当たったか、何に当たったかは要りません。そのため、<strong>any-hit の最初の当たりで探索を打ち切って</strong>構いません。当たれば V = 0、当たらなければ V = 1 で、全レイの平均が AO です。

```hlsl
[shader("raygeneration")]
void RtaoRayGen() {
  uint2 pixel = DispatchRaysIndex().xy;
  float3 p = WorldPosition(pixel);
  float3 n = WorldNormal(pixel);

  float3 dir = CosineSampleHemisphere(n, Random2(pixel, frame_index));

  RayDesc ray;
  ray.Origin = p + n * kRayBias;
  ray.Direction = dir;
  ray.TMin = 0.0;
  ray.TMax = ao_radius;

  AoPayload payload;
  payload.hit = 1.0;
  TraceRay(scene, RAY_FLAG_ACCEPT_FIRST_HIT_AND_END_SEARCH | RAY_FLAG_SKIP_CLOSEST_HIT_SHADER,
           0xFF, 0, 0, 0, ray, payload);

  ao_output[pixel] = payload.hit;
}
```

このコードの要点は次のとおりです。`RAY_FLAG_ACCEPT_FIRST_HIT_AND_END_SEARCH` は、最初に当たった時点で探索を終えるフラグで、最も近い交点を求める必要がない AO では、これで大きく速くなります。`RAY_FLAG_SKIP_CLOSEST_HIT_SHADER` は、当たった後のシェーダーを省略します。当たらなければ可視とするために、payload の初期値を 1 にし、ミス シェーダーで 0 ではなく可視の値を返す規約にします（ここでは当たったら 0 を書く運用です）。`ray.TMax = R` が AO の影響範囲を決めます。レイの出発点は、自己交差を避けるために、法線方向へ少し浮かせます。

### レイの方向の作り方

コサイン分布の方向は、2 つの乱数 (u1, u2) から作ります。円盤の上に一様に点を取り、それを半球に持ち上げる（Malley の方法）のが標準です。

<div class="formula">r = √u1、φ = 2π·u2　→　局所座標 (r cos φ, r sin φ, √(1 − u1))</div>

局所座標の z 軸を法線に合わせるために、法線から作った接線ベクトル 2 本で基底を組んで変換します。乱数は、画素の位置とフレーム番号から作ったブルー ノイズや低ディスクレパンシー列を使うと、同じレイ数でもノイズが小さくなり、時間蓄積の収束も速くなります（[Noise Patterns](../filtering/noise-pattern.md)）。

### コストの考え方

RTAO のコストは、レイの数と、レイの長さ R で決まります。R が短いと、レイが BVH のごく一部しか走査しないで済むので、とても軽くなります。AO の半径は 0.5〜2 m 程度が普通なので、長いレイを使う反射や GI と比べて、**1 レイあたりの処理が桁違いに軽い**のが RTAO の強みです。

軽さを活かして、実用的には 1 画素 1 本のレイを毎フレーム飛ばし、デノイザーで集めます。半分の解像度でレイを飛ばして、フル解像度の深度を見ながらアップサンプルする構成もあります。

### 特徴

利点は、画面外・隠れた物・薄い物も含めて、正しく遮蔽できることです。ハローなどのアーティファクトがなく、コサイン重みが自然に入り、半径の大きさにも強いです。

欠点は、1 画素 1〜2 本のレイではノイズが大きく、デノイザーが必須なことです。レイトレーシング対応の GPU が必要で、BVH の構築と更新のコストがかかります。動く物体が多いと、BVH の更新が重くなります。

### デノイズ

レイは画素あたり 1 本程度なので、そのままでは、ノイズだらけです。空間（バイラテラル ブラー）と時間（再投影した履歴との混合）で平均します（[AO Filtering](../filtering/index.md)）。AO は 1 チャンネル（スカラー）で、色を持つ反射や GI に比べて、デノイズがずっと軽く済みます。

ノイズの大きさは、実は画素ごとに違います。完全に遮られた隅や、完全に開けた場所では、全レイの結果が同じなので、ばらつきがありません。ばらつきが大きいのは、遮蔽と非遮蔽が混ざる縁です。そこで、履歴の分散を見て、ばらつきの大きい画素だけブラーを強める、分散ガイド付きのフィルタ（SVGF など）を使うと、きれいに仕上がります。

### より良いやり方：スクリーン空間との併用

RTAO の 1 本のレイは、<strong>正確ですがノイズが大きい</strong>。GTAO は、<strong>ノイズが小さいが画面外を知らない</strong>。この 2 つは相補的です。画面内の細かい接触は GTAO で安く出し、RTAO は GTAO が苦手な画面外や薄い物の影響だけを補う（画素あたり 0.25 本の低いレート）構成にすれば、品質とコストの両方を良くできます。ハードウェアの許す範囲で、「RTAO を最高画質設定、GTAO を標準設定」と切り替えるのも、現実的な選択です。

また、レイの出発点の自己交差は、ノイズやちらつきの原因になります。法線方向へ浮かせる距離を、画素の距離に応じて変える、またはレイに法線方向の TMin を設定するなどして、調整してください。アルファ テストのある葉や柵は、any-hit シェーダーでアルファを評価しないと、板が遮蔽物になってしまいます。



## よくあるミス

??? failure "レイ数が少なくて、ノイズだらけ"
    **時間蓄積と空間フィルタ（デノイズ）**を使う（[フィルタ](../filtering/index.md)）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **RTAO ＝ 半球レイで遮蔽を数える**
    - [x] **正確だが、レイ数とデノイズが課題**

## 参考

- Mittring, "Finding Next Gen: CryEngine 2"（SIGGRAPH 2007）
- Jimenez et al., "Practical Real-Time Strategies for Accurate Indirect Occlusion"（SIGGRAPH 2016）

## 関連ページ

- [世界空間 AO](index.md)
- [距離場 AO](dfao.md)
- [フィルタ](../filtering/index.md)
