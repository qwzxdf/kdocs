---
title: Ray-Traced Shadows
tags:
  - 描画
---

# Ray-Traced Shadows

**シャドウ マップ**は、**光から見たシーンをいったん画像（深度）に写し**、そこから**近似**します。そのため、**解像度・バイアス・エイリアシング**の問題が付きまといます。**レイトレース影**は、**画素から光へ直接レイを飛ばし**、**途中で何かに当たるか**を、**ジオメトリそのもの**に対して調べる方式です。**シャドウ マップの問題が、根本から消え**、**面光源の半影**も**レイを光源の面上にばらまく**ことで、**物理的に正しく**作れます。**DXR**（DirectX Raytracing）に対応した GPU が必要です。

!!! tip "ポイント"
    - <strong>画素（ワールド位置）から、光へシャドウ レイ</strong>を 1 本。<strong>当たれば影、当たらなければ日向</strong>。
    - <strong>シャドウ マップなし</strong>：<strong>解像度・バイアス・ピーター パンニング・アクネが存在しない</strong>。
    - <strong>面光源の半影</strong>：<strong>光源の面上のランダムな点</strong>へ飛ばし、<strong>平均</strong>。<strong>接触硬化が正確</strong>。
    - 必要なもの：<strong>加速構造（BLAS・TLAS）</strong>・<strong>DXR 対応 GPU</strong>。
    - <strong>少ないレイ</strong>（画素あたり 1 本）＋<strong>デノイズ</strong>で<strong>リアルタイム</strong>に。
    - 最適化：<strong>Any-Hit 不要</strong>（<strong>当たった時点で終了</strong>）・<strong>RayQuery（インライン）</strong>。

## 原理

画素の**ワールド位置 `P`** から、**光源への方向**へ**レイ**を飛ばします。**途中で何かに当たったら影**です。

光源の種類ごとに、レイの方向は次のように決めます。平行光（太陽）では、光の逆方向（`-L`）に飛ばします。光源の大きさ（視直径）を考慮して、方向を円錐内でランダムにずらします。点光源やスポットライトでは、ライトの位置へ向かう方向に飛ばし、光源の大きさ（半径）を考慮して、光源の球面上のランダムな点を狙います。矩形の面光源では、面上のランダムな点へ飛ばします。このランダムなずらしが、物理的に正しい半影を生みます。

**ランダムに方向をずらす**ことで、<strong>1 本ずつのレイは「影か日向か」の 0/1 だが平均すると半影（0〜1）</strong>になります。

### 影の判定

```hlsl
float TraceShadowRay(float3 origin, float3 direction, float t_max) {
  RayQuery<RAY_FLAG_ACCEPT_FIRST_HIT_AND_END_SEARCH |
           RAY_FLAG_SKIP_CLOSEST_HIT_SHADER> query;
  RayDesc ray;
  ray.Origin = origin;
  ray.Direction = direction;
  ray.TMin = 0.001;
  ray.TMax = t_max;
  query.TraceRayInline(scene_tlas, 0, 0xFF, ray);
  query.Proceed();
  return query.CommittedStatus() == COMMITTED_TRIANGLE_HIT ? 0.0 : 1.0;
}
```

コードの要点です。`RAY_FLAG_ACCEPT_FIRST_HIT_AND_END_SEARCH` は、最初に当たった時点で探索を終了させるフラグで、最も近いヒットを探す必要がないので、大幅に速くなります。`RAY_FLAG_SKIP_CLOSEST_HIT_SHADER` は、当たったかどうかだけが分かればよいので、シェーダーを呼びません。`TMin` は、自己交差（自分の面に当たる）を避ける小さなオフセットで、`TMax` は光源までの距離（点光源）です。それより先は見ません。RayQuery（インライン）を使うと、ピクセル シェーダーやコンピュート シェーダーの中から、直接レイを飛ばせます（DXR 1.1）。

<!-- fig:rt-shadow-samples:begin -->

<svg class="fig illust motion" data-fig="rt-shadow-samples" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-rt-shadow-samples" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">レイトレの影:面光源に向けた複数のレイで、半影を作る</text>
<rect x="250" y="72" width="280" height="16" rx="8" fill="#e5aa28"/>
<text x="542" y="84" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5aa28">面光源</text>
<rect x="350" y="180" width="150" height="16" fill="#b8794b" stroke="#7a4b2a" stroke-width="2"/>
<rect x="40" y="340" width="700" height="14" fill="#d6c7a1"/>
<circle cx="560" cy="340" r="8" fill="#2563eb" stroke="#ffffff" stroke-width="2"/>
<text x="572" y="328" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2563eb">調べる点（半影の中）</text>
<g opacity="0"><animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0830;0.0833;0.3830;0.3833;1.0000" values="0;0;1;1;0;0"/><line x1="560" y1="340" x2="390.0" y2="80" stroke="#e5484d" stroke-width="3"/>
<circle cx="390.0" cy="80" r="4" fill="#e5484d"/>
<text x="60" y="76" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">レイ 1 本:見えた 0 本 → 光 0 %</text>
<rect x="600" y="380" width="100" height="26" fill="#000000" stroke="#94a3b8" stroke-width="1.5"/>
<text x="580" y="398" text-anchor="end" style="font-size:12px;font-weight:700;fill:#64748b">結果</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.3830;0.3833;0.6830;0.6833;1.0000" values="0;0;1;1;0;0"/><line x1="560" y1="340" x2="283.6" y2="80" stroke="#e5484d" stroke-width="2"/>
<circle cx="283.6" cy="80" r="4" fill="#e5484d"/>
<line x1="560" y1="340" x2="353.6" y2="80" stroke="#e5484d" stroke-width="2"/>
<circle cx="353.6" cy="80" r="4" fill="#e5484d"/>
<line x1="560" y1="340" x2="426.4" y2="80" stroke="#e5484d" stroke-width="2"/>
<circle cx="426.4" cy="80" r="4" fill="#e5484d"/>
<line x1="560" y1="340" x2="496.4" y2="80" stroke="#2ea043" stroke-width="2"/>
<circle cx="496.4" cy="80" r="4" fill="#2ea043"/>
<text x="60" y="76" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">レイ 4 本:見えた 1 本 → 光 25 %</text>
<rect x="600" y="380" width="100" height="26" fill="#888888" stroke="#94a3b8" stroke-width="1.5"/>
<text x="580" y="398" text-anchor="end" style="font-size:12px;font-weight:700;fill:#64748b">結果</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.6830;0.6833;0.9830;0.9833;1.0000" values="0;0;1;1;0;0"/><line x1="560" y1="340" x2="258.75" y2="80" stroke="#e5484d" stroke-width="2"/>
<circle cx="258.75" cy="80" r="4" fill="#e5484d"/>
<line x1="560" y1="340" x2="276.25" y2="80" stroke="#e5484d" stroke-width="2"/>
<circle cx="276.25" cy="80" r="4" fill="#e5484d"/>
<line x1="560" y1="340" x2="293.75" y2="80" stroke="#e5484d" stroke-width="2"/>
<circle cx="293.75" cy="80" r="4" fill="#e5484d"/>
<line x1="560" y1="340" x2="311.25" y2="80" stroke="#e5484d" stroke-width="2"/>
<circle cx="311.25" cy="80" r="4" fill="#e5484d"/>
<line x1="560" y1="340" x2="328.75" y2="80" stroke="#e5484d" stroke-width="2"/>
<circle cx="328.75" cy="80" r="4" fill="#e5484d"/>
<line x1="560" y1="340" x2="346.25" y2="80" stroke="#e5484d" stroke-width="2"/>
<circle cx="346.25" cy="80" r="4" fill="#e5484d"/>
<line x1="560" y1="340" x2="363.75" y2="80" stroke="#e5484d" stroke-width="2"/>
<circle cx="363.75" cy="80" r="4" fill="#e5484d"/>
<line x1="560" y1="340" x2="381.25" y2="80" stroke="#e5484d" stroke-width="2"/>
<circle cx="381.25" cy="80" r="4" fill="#e5484d"/>
<line x1="560" y1="340" x2="398.75" y2="80" stroke="#e5484d" stroke-width="2"/>
<circle cx="398.75" cy="80" r="4" fill="#e5484d"/>
<line x1="560" y1="340" x2="416.25" y2="80" stroke="#e5484d" stroke-width="2"/>
<circle cx="416.25" cy="80" r="4" fill="#e5484d"/>
<line x1="560" y1="340" x2="433.75" y2="80" stroke="#e5484d" stroke-width="2"/>
<circle cx="433.75" cy="80" r="4" fill="#e5484d"/>
<line x1="560" y1="340" x2="451.25" y2="80" stroke="#e5484d" stroke-width="2"/>
<circle cx="451.25" cy="80" r="4" fill="#e5484d"/>
<line x1="560" y1="340" x2="468.75" y2="80" stroke="#2ea043" stroke-width="2"/>
<circle cx="468.75" cy="80" r="4" fill="#2ea043"/>
<line x1="560" y1="340" x2="486.25" y2="80" stroke="#2ea043" stroke-width="2"/>
<circle cx="486.25" cy="80" r="4" fill="#2ea043"/>
<line x1="560" y1="340" x2="503.75" y2="80" stroke="#2ea043" stroke-width="2"/>
<circle cx="503.75" cy="80" r="4" fill="#2ea043"/>
<line x1="560" y1="340" x2="521.25" y2="80" stroke="#2ea043" stroke-width="2"/>
<circle cx="521.25" cy="80" r="4" fill="#2ea043"/>
<text x="60" y="76" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">レイ 16 本:見えた 4 本 → 光 25 %</text>
<rect x="600" y="380" width="100" height="26" fill="#888888" stroke="#94a3b8" stroke-width="1.5"/>
<text x="580" y="398" text-anchor="end" style="font-size:12px;font-weight:700;fill:#64748b">結果</text>
</g>
<text x="40" y="400" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">レイが少ないと、0 か 1 のノイズ。増やすほど、なめらかな半影に近づく（デノイズで補う）。</text>
</svg>

<!-- fig:rt-shadow-samples:end -->

## 半影：面光源のサンプリング

**面光源**（有限の大きさ）の影を**物理的に正確**に作るには、**光源の面上にランダムな点**を選び、**そこへレイ**を飛ばします。

```hlsl
float3 SampleSunDirection(float3 sun_dir, float angular_radius, float2 xi) {
  float cos_theta = lerp(cos(angular_radius), 1.0, xi.x);
  float sin_theta = sqrt(1.0 - cos_theta * cos_theta);
  float phi = 2.0 * 3.14159265 * xi.y;
  float3 local_dir = float3(sin_theta * cos(phi), sin_theta * sin(phi), cos_theta);
  return TransformToBasis(local_dir, sun_dir);
}
```

太陽の方向のサンプルのコードの要点です。太陽の視直径（約 0.27 度の半角）の円錐内で、ランダムな方向を一様に選びます。`xi` は 2 つの乱数で、ブルー ノイズ・IGN・低食い違い列などを使います。`TransformToBasis` は、太陽方向を軸とした局所座標を、ワールドへ変換する関数です。

**1 画素あたり 1 本**のレイでは、**半影は、0 か 1 のノイズ**になります。**複数本を平均**するか、**デノイズ**して滑らかにします。

### 接触硬化は、正確

**遮蔽物が近い**と**光源の面上のどの点へのレイも、同じ遮蔽物に当たる**ので、**影は鋭く**なります。**遮蔽物が離れる**と**光源の面上の点によって、当たる・当たらないが分かれ**、**ぼけます**。[PCSS](pcss.md)が近似した性質が**ここでは自然に再現**されます。

## デノイズ

**1 画素 1 本**の**ノイズの多い影**を、**滑らかにする**には、**デノイズ**します。

1 画素 1 本のノイズの多い影を滑らかにするデノイズの方法です。時間蓄積（TAA 的）は、前のフレームの結果を再投影して混ぜます（カメラや物の動きに注意）。空間フィルタは、バイラテラルや À-trous ウェーブレットで、法線と深度を手がかりに、エッジを保ってぼかします。分散ガイドは、画素の分散を見て、ノイズの多い所ほど強くフィルタします。専用デノイザとしては、NVIDIA NRD（ReBLUR・SIGMA）、AMD FidelityFX Denoiser などがあり、影専用の SIGMA は半影に最適化されています。

**影専用のデノイザ**は、<strong>可視性（0〜1）</strong>を、<strong>距離（遮蔽物までの距離）</strong>とともに受け取り、**半影の幅**に応じて、**フィルタの強さ**を変えます。

## 加速構造

**レイトレース影**には、<strong>シーンの加速構造（BVH）</strong>が必要です。

加速構造は 2 層です。BLAS（Bottom-Level）は、メッシュごとの BVH で、三角形を含みます。TLAS（Top-Level）は、BLAS のインスタンスを、変換行列付きで並べた BVH です。更新については、動く物体は TLAS のインスタンス行列を更新し、変形する（スキニングされた）物は BLAS を再構築またはリフィットします。

**影に使う BLAS は、見た目より単純でよい**（**低ポリのプロキシ**）ことが多く、**メモリ・構築コスト**を減らせます。

## ハイブリッド構成

**全画素をレイトレース**すると重いので、**シャドウ マップと併用**します。

全画素をレイトレースすると重いので、シャドウ マップと併用するのが一般的です。太陽の影だけをレイトレースする構成では、主ライトの柔らかい影と正確な接触を得ます。シャドウ マップで完全な影・完全な日向を判断し、半影の領域だけ RT で精密に追う構成もあります。近くだけ RT にして、遠景はシャドウ マップにする構成もあります。品質設定で切り替えて、RT 非対応の GPU はシャドウ マップにします。

**画面空間のマスク**（半影のありそうな画素）を作り、**その画素だけレイを飛ばす**と、**大幅に安く**なります。

## コスト

レイトレース影のコストです。レイ数は、画素数にライト数を掛け、さらに 1〜数本を掛けた量です。加速構造の構築・更新・メモリのコストがかかります。デノイズは追加のパスです。ライトが多いと、ライトごとにレイが必要なので、重要なライトに限ります。

**ライトが多数**ある場合は、**ライトの重要度でサンプルするライトを 1 つ選ぶ**（**ReSTIR**・**重要度サンプリング**）手法があります。

## シャドウ マップとの比較

シャドウ マップとの比較です。精度は、シャドウ マップが解像度とバイアスの影響を受けるのに対し、レイトレースはジオメトリそのものを使うので正確です。アーティファクトは、シャドウ マップがアクネ・ピーター パンニング・エイリアシングを持つのに対し、レイトレースはほぼなく、ノイズだけです。半影は、シャドウ マップが近似（PCSS）、レイトレースが物理的に正確です。透過やアルファ テストは、シャドウ マップでは扱いにくいですが、レイトレースなら Any-Hit シェーダーで可能です。必要なハードウェアは、シャドウ マップは不要、レイトレースは DXR 対応 GPU です。コストは、中程度と大（デノイズ込み）です。多数のライトに対し、シャドウ マップは負荷が増え、レイトレースはライト数に比例します。

## 長所と短所

レイトレース影の長所は、シャドウ マップの問題がすべて消えること、正確な半影と接触硬化が得られること、シャドウ マップのレンダリング パスが不要なこと、アルファ テストの物（葉）も正確なことです。短所は、DXR 対応 GPU が必須なこと、加速構造の維持（メモリと更新）、ノイズとデノイズ、ライト数に比例して重くなることです。

## よくあるミス

??? failure "自己交差で、面が黒いノイズだらけ"
    **`TMin` を小さく設定**し、**レイの原点を法線方向にわずかにずらす**。

??? failure "Any-Hit 不要なのに、最も近いヒットを探していて、遅い"
    **`ACCEPT_FIRST_HIT_AND_END_SEARCH`** を指定します。

??? failure "デノイズなしで、1 本のレイでノイズだらけ"
    **時間蓄積・空間フィルタ・専用デノイザ**を使います。

??? failure "全ライトに、全画素でレイを飛ばして、重い"
    **主ライトだけ RT**・**マスクした画素のみ**にします。

## これだけ覚える

!!! abstract "まとめ"
    - [x] レイトレース影 ＝ <strong>画素から光へ、シャドウ レイを飛ばし、当たれば影</strong>
    - [x] <strong>シャドウ マップの問題（解像度・バイアス・アクネ）が、存在しない</strong>
    - [x] <strong>光源の面上にランダムにレイを飛ばして平均</strong> ＝ <strong>正確な半影・接触硬化</strong>
    - [x] <strong>最初のヒットで終了</strong>（<strong>ACCEPT_FIRST_HIT</strong>）で速くする。<strong>デノイズ</strong>が必須
    - [x] <strong>ハイブリッド</strong>（シャドウ マップ ＋ RT）が実用的。<strong>DXR 対応 GPU</strong>が必要

## 参考

- Microsoft, "DirectX Raytracing (DXR) Functional Spec"
- NVIDIA, "Ray Tracing Gems"（シャドウ・デノイズの章）
- NVIDIA, "NRD (NVIDIA Real-Time Denoisers)"（SIGMA：影用デノイザ）

## 関連ページ

- [Shadows](index.md)
- [PCSS](pcss.md)
- [RT 反射](../reflections/rt-reflections/index.md)
- [Distance Field Shadows](sdf-shadows.md)
