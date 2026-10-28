---
title: Hybrid Pipeline
tags:
  - 描画
---

# Hybrid Pipeline

<strong>全画素にレイトレを使うと重いので、「SSR で当たった所は SSR、外れた所だけレイトレ」</strong>という、ハイブリッド構成が現実的です。さらに、粗さが高い所はプローブにフォールバックします。このページではハイブリッドの組み立て方と、性能の工夫を説明します。

!!! tip "ポイント"
    - まず SSR。当たらなかった画素だけレイトレ。
    - 粗さが高い画素は、プローブ（ノイズが多くレイトレの価値が低い）。
    - 半解像度でトレースして、アップサンプル。
    - レイの数・距離に上限を設ける。

!!! info "このページを読む前に"
    - [Ray-Traced Reflections](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

<!-- fig:rt-hybrid-flow:begin -->

<svg class="fig illust motion" data-fig="rt-hybrid-flow" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-rt-hybrid-flow" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">ハイブリッド:画素ごとに、使う方式を選ぶ</text>
<rect x="40" y="170" width="120" height="50" rx="8" fill="#1f2937" fill-opacity="0.18" stroke="#1f2937" stroke-width="2.5"/>
<text x="100.0" y="200.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">反射が必要な画素</text>
<rect x="210" y="170" width="150" height="50" rx="8" fill="#2563eb" fill-opacity="0.18" stroke="#2563eb" stroke-width="2.5"/>
<text x="285.0" y="200.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">SSR が当たった?</text>
<rect x="420" y="60" width="150" height="50" rx="8" fill="#2563eb" fill-opacity="0.18" stroke="#2563eb" stroke-width="2.5"/>
<text x="495.0" y="90.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">SSR の色を使う</text>
<rect x="420" y="170" width="150" height="50" rx="8" fill="#7c3aed" fill-opacity="0.18" stroke="#7c3aed" stroke-width="2.5"/>
<text x="495.0" y="200.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">粗さが高い?</text>
<rect x="620" y="120" width="130" height="50" rx="8" fill="#e5aa28" fill-opacity="0.18" stroke="#e5aa28" stroke-width="2.5"/>
<text x="685.0" y="150.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">プローブを使う</text>
<rect x="620" y="250" width="130" height="50" rx="8" fill="#2ea043" fill-opacity="0.18" stroke="#2ea043" stroke-width="2.5"/>
<text x="685.0" y="280.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">レイトレを使う</text>
<line x1="160" y1="195" x2="210" y2="195" stroke="#64748b" stroke-width="2" marker-end="url(#arr-rt-hybrid-flow)"/>
<line x1="360" y1="195" x2="420" y2="195" stroke="#64748b" stroke-width="2" marker-end="url(#arr-rt-hybrid-flow)"/>
<line x1="390" y1="185" x2="420" y2="90" stroke="#64748b" stroke-width="2" marker-end="url(#arr-rt-hybrid-flow)"/>
<line x1="570" y1="195" x2="620" y2="145" stroke="#64748b" stroke-width="2" marker-end="url(#arr-rt-hybrid-flow)"/>
<line x1="570" y1="200" x2="620" y2="270" stroke="#64748b" stroke-width="2" marker-end="url(#arr-rt-hybrid-flow)"/>
<text x="400" y="138" text-anchor="start" style="font-size:11px;font-weight:700;fill:#2563eb">はい</text>
<text x="372" y="215" text-anchor="start" style="font-size:11px;font-weight:700;fill:#64748b">いいえ</text>
<text x="586" y="148" text-anchor="start" style="font-size:11px;font-weight:700;fill:#e5aa28">はい</text>
<text x="590" y="252" text-anchor="start" style="font-size:11px;font-weight:700;fill:#2ea043">いいえ</text>
<circle cx="100" cy="195" r="10" fill="#e5484d" stroke="#ffffff" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;0.3308;0.3310;1.0000" values="0;0;1;1;0;0"/><animate attributeName="cx" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0690;0.1310;0.1931;1.0000" values="100;100;285;495;495"/><animate attributeName="cy" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0690;0.1310;0.1931;1.0000" values="195;195;195;85;85"/></circle>
<text x="40" y="350" text-anchor="start" style="font-size:16px;font-weight:700;fill:#e5484d" opacity="0">画素 A(鏡面・当たった)<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;0.3446;0.3448;1.0000" values="0;0;1;1;0;0"/></text>
<circle cx="100" cy="195" r="10" fill="#2563eb" stroke="#ffffff" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3446;0.3448;0.6066;0.6069;1.0000" values="0;0;1;1;0;0"/><animate attributeName="cx" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3448;0.4069;0.4690;0.5310;1.0000" values="100;100;285;495;685;685"/><animate attributeName="cy" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3448;0.4069;0.4690;0.5310;1.0000" values="195;195;195;195;275;275"/></circle>
<text x="40" y="350" text-anchor="start" style="font-size:16px;font-weight:700;fill:#2563eb" opacity="0">画素 B(画面外へ出た・滑らか)<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3446;0.3448;0.6204;0.6207;1.0000" values="0;0;1;1;0;0"/></text>
<circle cx="100" cy="195" r="10" fill="#e5aa28" stroke="#ffffff" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6204;0.6207;0.8825;0.8828;1.0000" values="0;0;1;1;0;0"/><animate attributeName="cx" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6207;0.6828;0.7448;0.8069;1.0000" values="100;100;285;495;685;685"/><animate attributeName="cy" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6207;0.6828;0.7448;0.8069;1.0000" values="195;195;195;195;145;145"/></circle>
<text x="40" y="350" text-anchor="start" style="font-size:16px;font-weight:700;fill:#e5aa28" opacity="0">画素 C(ざらざら・外れ)<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6204;0.6207;0.8963;0.8966;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="390" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">SSR で当たれば最も安い。外れた画素だけ、レイトレかプローブへ。粗い面は、プローブで十分（ノイズが多く、レイトレの価値が低い）。</text>
</svg>

<!-- fig:rt-hybrid-flow:end -->

## ハイブリッド構成：SSR とレイトレの組み合わせ
<strong>画面内に当たりがある</strong>場合は、SSR（Hi-Z）で足りることが多いです。画面に当たりがない（画面外・裏側・失敗）レイだけをレイトレにします。

ハイブリッド構成は 3 段階です。最初に SSR（Hi-Z）を先に実行し、画面内で当たればその色を使います（安いため）。次に、当たらなかったレイだけをレイトレに回します。画面外へ出たレイや厚みで弾かれたレイが対象です。最後に、両方の結果を画素ごとに選んで合成します。

利点はレイトレのレイが大きく減ってコストが下がることと、SSR が画面内の細かさ（足元の映り込み）に強いことです。注意点は SSR とレイトレで見た目（色・ぼけ）が違うと境目が見えることです。同じ BRDF・同じ色空間で揃えます。

利点：レイトレのレイが大きく減る（コスト削減）。SSR は画面内の細かさ（足元の映り込み）に強い。

注意：SSR とレイトレで見た目（色・ぼけ）が違うと境目が見える。同じ BRDF・同じ色空間でそろえます。

## 性能の工夫
| 工夫 | 内容 |
| --- | --- |
| 粗さによるレイの省略 | 粗い面はレイを飛ばさない |
| 半分の解像度 | レイを半分の解像度で飛ばし、アップサンプル |
| レイのソート・まとめ | 似た方向・似たメッシュのレイをまとめて処理（コヒーレンス向上）。シェーダー実行の並べ替え（SER） |
| レイの最大距離 | 短くする（遠くは空・プローブ） |
| インライン レイトレ（`RayQuery`） | コンピュート シェーダーから直接（ヒット シェーダーなし）。軽い処理に向く |
| LOD・簡易メッシュ | BVH 用に軽いメッシュを使う |
| アルファ テスト | any-hit は重い。葉・フェンスは必要最小限に |
| 動く物体の BVH 更新 | リフィット（再構築より安い）・更新頻度の削減 |

## ハイブリッド：SSR と、RT のいいとこ取り

<strong>フルスクリーンの RT 反射</strong>は、重いです。SSRは安いが画面の外・隠れた面は、映せません。組み合わせます。SSR で取れる画素は SSR（安い）、取れなかった画素だけ RT（高い）で、補います（Stachowiak、2018、Barré-Brisebois ら、2019）。

```text
各画素:
   ① まず、SSR を、試す（画面空間の、レイマーチ）
        ↓ 当たった（信頼できる）→ SSR の結果を使う（RT は、不要）
        ↓ 当たらなかった / 信頼できない → ② RT を、飛ばす
```

## 利点

| 利点 | 内容 |
| --- | --- |
| コストが下がる | SSR で、取れる画素（多くの画面内の反射）は、RT を飛ばさない。RT のレイ数が大幅に減る |
| 画質が高い | SSR が、取れない（画面の外、隠れた面）部分は RT で正確 |
| 近距離の精度 | SSR は画面の実際の、ジオメトリを使うので近距離で細かく、正確（RT の BVH は簡略化した、メッシュかもしれない） |

## 流れ（概略）

```hlsl
// ① SSR パス: 各画素で、SSR を試す。結果と、成否を書き出す。
float4 ssr = TraceSSR(pixel);                                          // rgb = 色、a = 信頼度（0 = 失敗）
g_ssr_result[pixel] = ssr;

// ② RT パス: SSR が、失敗（信頼度が低い）した画素だけ、RT を飛ばす。
[shader("raygeneration")]
void HybridRayGen() {
  uint2 pixel = DispatchRaysIndex().xy;
  float4 ssr = g_ssr_result[pixel];
  if (ssr.a > 0.99) { g_final_reflection[pixel] = ssr.rgb; return; }   // SSR が、十分 → RT は、不要
  // ... 反射レイを飛ばす（[Ray Generation]）...
  float3 rt = payload.radiance;
  g_final_reflection[pixel] = lerp(rt, ssr.rgb, ssr.a);                // 信頼度で、混ぜる（SSR が、一部、成功した画素）
}
```

<strong>SSR の信頼度が十分に高い</strong>画素は、RT を飛ばしません。信頼度が低い（画面の端、物の裏、SSR が外れた）画素だけ RT を飛ばします。RT の画素数が画面の数 %〜数十 % に、減ります。

## DXR のインライン レイトレーシング

<strong>RT を飛ばす画素が少ない</strong>（疎）なら、計算シェーダーの中からインラインでレイを飛ばす（`RayQuery`）方法が効率的です。DXR 1.1 の機能でレイ生成シェーダーの、ディスパッチ（シェーダー テーブル）が不要です。

```hlsl
// 計算シェーダーの中から、インラインで、レイを飛ばす（DXR 1.1 の RayQuery）。
[numthreads(8, 8, 1)]
void InlineRTCS(uint3 id : SV_DispatchThreadID) {
  if (g_ssr_result[id.xy].a > 0.99) return;                              // SSR が、十分な画素は、スキップ
  RayDesc ray = MakeReflectionRay(id.xy);
  RayQuery<RAY_FLAG_CULL_NON_OPAQUE | RAY_FLAG_ACCEPT_FIRST_HIT_AND_END_SEARCH> q;
  q.TraceRayInline(g_scene, RAY_FLAG_NONE, 0xFF, ray);
  q.Proceed();                                                           // BVH を辿る
  if (q.CommittedStatus() == COMMITTED_TRIANGLE_HIT) {
    // 当たった: 三角形の情報から、手で、シェーディング
  }
}
```

`RayQuery` は 計算シェーダー・ピクセル シェーダーから、呼べます。画素を絞ってシェーダー テーブルを使わず手軽に RT を組み込めます。ただし、当たった面のマテリアルを動的に切り替える（シェーダー テーブルの、利点）ことは自分で書く必要があります。

## SSR と RT の継ぎ目

<strong>SSR の画素</strong>と RT の画素が隣り合うと色がずれて境目が見えることが、あります。

| 問題 | 対策 |
| --- | --- |
| 明るさ・色のずれ | SSR と RT の、ライティングをそろえる（同じ露出、環境光） |
| 境目のギザギザ | 信頼度をなめらかに変化させる（SSR の、フェード。[Color Lookup and Fading](../ssr-basics/color-fade.md)）、RT の重みを少しずつ増やす |
| SSR の細部と RT の、粗さ | RT の BVH が、簡略（LOD、細部が無い）だと SSR の詳細な反射と差が出る。BVH の LOD を高めに |

## 選択の目安

| 状況 | 方式 |
| --- | --- |
| コストを最小に | SSR + 反射プローブ（RT なし） |
| 品質とコストのバランス | ハイブリッド（SSR + RT、SSR が外れた画素だけ） |
| 最高品質（ハイエンド） | フル RT（全反射面で、RT） |

## よくあるミス

??? failure "レイトレの負荷が画面いっぱいで重い"
    <strong>SSR で当たった画素は、レイトレを飛ばさない</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] SSR → レイトレ → プローブ の順にフォールバック
    - [x] 半解像度とレイ数の上限で、コストを抑える

## 参考

- Stachowiak, "Stochastic All The Things: Raytracing in Hybrid Real-Time Rendering", Digital Dragons 2018
- Barré-Brisebois, Halén, Wihlidal, Lauritzen, Bekkers, Stachowiak, Andersson, "Hybrid Rendering for Real-Time Ray Tracing", Ray Tracing Gems, Chapter 25, 2019
- Microsoft, "DirectX Raytracing (DXR) Functional Spec"
- Stachowiak, Uludag, "Stochastic Screen-Space Reflections", SIGGRAPH 2015, Advances in Real-Time Rendering in Games（Frostbite の SSR）
- McGuire, Mara, "Efficient GPU Screen-Space Ray Tracing", Journal of Computer Graphics Techniques, Vol. 3, No. 4, 2014

## 関連ページ

- [Ray-Traced Reflections](index.md)
- [SSR Basics](../ssr-basics/index.md)
- [Denoising](denoise.md)
