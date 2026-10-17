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

| 手順 | 内容 |
| --- | --- |
| **① 画素の位置と法線を得る** | G-Buffer から |
| **② レイの方向を作る** | **法線の側の半球**に**コサイン分布**で |
| **③ レイを飛ばす** | **最大距離 R**（影響半径）まで。**any-hit は不要**（当たったかだけ分かればよい） |
| **④ 当たったか** | 当たれば V = 0、当たらなければ V = 1 |
| **⑤ 平均する** | `AO = 平均(V)` |

[理論](../theory/index.md)のとおり、**コサイン分布でサンプルすれば、`AO = V の平均`**です。

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

| 点 | 説明 |
| --- | --- |
| **`ACCEPT_FIRST_HIT_AND_END_SEARCH`** | **最初に当たった時点で終了**。最も近い交点は不要なので、**速い** |
| **`SKIP_CLOSEST_HIT_SHADER`** | 当たった後のシェーダーを省略 |
| **ミス シェーダーで `hit = 0`** | 当たらなければ、可視（payload の初期値を 1 にして、ミスで 0 にする、などの規約） |
| **`ray.TMax = R`** | **半径 R**。これが、AO の影響範囲 |
| **レイのバイアス** | 自己交差を避けるため、**法線方向に少し浮かせる** |

### 特徴

| 利点 | 欠点 |
| --- | --- |
| **正確**（画面外・隠れた物・薄い物も正しく遮蔽） | **1 画素 1〜2 本**のレイでは、**ノイズが大きい** |
| **ハローなどのアーティファクトが無い** | **ノイズ除去（デノイザー）が必須**（[フィルタ](../filtering/index.md)） |
| **コサイン重みが自然に入る** | **レイトレーシング対応の GPU** が必要。**BVH の構築・更新**のコスト |
| **半径の大きさに強い** | 動く物体が多いと、**BVH の更新**が重い |

### デノイズ

レイは**画素あたり 1 本**程度なので、**ノイズだらけ**です。<strong>空間（バイラテラル）と時間（再投影）</strong>で平均します。<strong>AO は 1 チャンネル（スカラー）</strong>で、他のレイトレ効果（反射・GI）より、**デノイズが軽い**です。

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
