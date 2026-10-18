---
title: Distance Field AO (DFAO)
tags:
  - 描画
---

# Distance Field AO (DFAO)

<strong>距離場 AO はシーンを「符号付き距離場（各点から、最も近い面までの距離）」で表し、その距離場の上で円錐を進めて、遮蔽を求めます</strong>。<strong>レイトレーシングのハードウェアが無くても、画面外の遮蔽を含む AO が得られます</strong>。距離場は事前計算（静的）で動く物体は別途扱います。このページでは距離場とは・円錐トレースによる AO・長所と短所を説明します。

!!! tip "ポイント"
    - 距離場 ＝ 各点から、最も近い面までの符号付き距離。
    - 距離場上を円錐で進み距離が小さければ遮蔽。
    - ハードウェア レイトレ不要。
    - 弱点：距離場の解像度・動く物体・メモリ。

## 距離場 AO（DFAO）
<strong>符号付き距離場（SDF）</strong>は <strong>空間の各点から、最も近い表面までの距離</strong>を 3D テクスチャに格納したものです。<strong>距離がわかる</strong>ので円錐に沿って歩くと遮蔽の割合をサンプルを数えずに求められます。

<!-- fig:dfao-cone:begin -->

<svg class="fig illust motion" data-fig="dfao-cone" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-dfao-cone" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">距離場 AO: 法線方向へ、円錐を数歩だけ進み、「距離場の値が、進んだ距離より小さい分」を遮蔽にする</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">断面。壁の近くの床の点。壁までの距離 a を 0.2 → 0.5 → 1.0 → 2.0 にして、5 歩の計算で AO を求める</text>
<rect x="30" y="96" width="560" height="300" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 断面(灰 = 壁、円 = 距離場の値)</text>
<line x1="40" y1="370.0" x2="570" y2="370.0" stroke="#475569" stroke-width="4"/>
<circle cx="90.0" cy="370.0" r="7" fill="#1f2937"/>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2798;0.2800;1.0000" values="1;1;0;0"/><rect x="106.0" y="130" width="14" height="240.0" fill="#94a3b8"/>
<circle cx="96.88" cy="360.17" r="9.12" fill="#e5484d" fill-opacity="0.12" stroke="#e5484d" stroke-width="1.5"/>
<circle cx="96.88" cy="360.17" r="3.5" fill="#e5484d"/>
<circle cx="103.77" cy="350.34" r="2.23" fill="#e5484d" fill-opacity="0.12" stroke="#e5484d" stroke-width="1.5"/>
<circle cx="103.77" cy="350.34" r="3.5" fill="#e5484d"/>
<circle cx="117.53" cy="330.68" r="0.0" fill="#e5484d" fill-opacity="0.12" stroke="#e5484d" stroke-width="1.5"/>
<circle cx="117.53" cy="330.68" r="3.5" fill="#e5484d"/>
<circle cx="145.06" cy="291.36" r="0.0" fill="#e5484d" fill-opacity="0.12" stroke="#e5484d" stroke-width="1.5"/>
<circle cx="145.06" cy="291.36" r="3.5" fill="#e5484d"/>
<circle cx="200.13" cy="212.72" r="0.0" fill="#e5484d" fill-opacity="0.12" stroke="#e5484d" stroke-width="1.5"/>
<circle cx="200.13" cy="212.72" r="3.5" fill="#e5484d"/>
<text x="50" y="128" text-anchor="start" style="font-size:18px;font-weight:700;fill:#7c3aed">壁までの距離 a = 0.2</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2798;0.2800;0.4932;0.4933;1.0000" values="0;0;1;1;0;0"/><rect x="130.0" y="130" width="14" height="240.0" fill="#94a3b8"/>
<circle cx="96.88" cy="360.17" r="33.12" fill="#2ea043" fill-opacity="0.12" stroke="#2ea043" stroke-width="1.5"/>
<circle cx="96.88" cy="360.17" r="3.5" fill="#2ea043"/>
<circle cx="103.77" cy="350.34" r="26.23" fill="#2ea043" fill-opacity="0.12" stroke="#2ea043" stroke-width="1.5"/>
<circle cx="103.77" cy="350.34" r="3.5" fill="#2ea043"/>
<circle cx="117.53" cy="330.68" r="12.47" fill="#e5484d" fill-opacity="0.12" stroke="#e5484d" stroke-width="1.5"/>
<circle cx="117.53" cy="330.68" r="3.5" fill="#e5484d"/>
<circle cx="145.06" cy="291.36" r="0.0" fill="#e5484d" fill-opacity="0.12" stroke="#e5484d" stroke-width="1.5"/>
<circle cx="145.06" cy="291.36" r="3.5" fill="#e5484d"/>
<circle cx="200.13" cy="212.72" r="0.0" fill="#e5484d" fill-opacity="0.12" stroke="#e5484d" stroke-width="1.5"/>
<circle cx="200.13" cy="212.72" r="3.5" fill="#e5484d"/>
<text x="50" y="128" text-anchor="start" style="font-size:18px;font-weight:700;fill:#7c3aed">壁までの距離 a = 0.5</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4932;0.4933;0.7065;0.7067;1.0000" values="0;0;1;1;0;0"/><rect x="170.0" y="130" width="14" height="240.0" fill="#94a3b8"/>
<circle cx="96.88" cy="360.17" r="73.12" fill="#2ea043" fill-opacity="0.12" stroke="#2ea043" stroke-width="1.5"/>
<circle cx="96.88" cy="360.17" r="3.5" fill="#2ea043"/>
<circle cx="103.77" cy="350.34" r="66.23" fill="#2ea043" fill-opacity="0.12" stroke="#2ea043" stroke-width="1.5"/>
<circle cx="103.77" cy="350.34" r="3.5" fill="#2ea043"/>
<circle cx="117.53" cy="330.68" r="52.47" fill="#2ea043" fill-opacity="0.12" stroke="#2ea043" stroke-width="1.5"/>
<circle cx="117.53" cy="330.68" r="3.5" fill="#2ea043"/>
<circle cx="145.06" cy="291.36" r="24.94" fill="#e5484d" fill-opacity="0.12" stroke="#e5484d" stroke-width="1.5"/>
<circle cx="145.06" cy="291.36" r="3.5" fill="#e5484d"/>
<circle cx="200.13" cy="212.72" r="0.0" fill="#e5484d" fill-opacity="0.12" stroke="#e5484d" stroke-width="1.5"/>
<circle cx="200.13" cy="212.72" r="3.5" fill="#e5484d"/>
<text x="50" y="128" text-anchor="start" style="font-size:18px;font-weight:700;fill:#7c3aed">壁までの距離 a = 1</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.7065;0.7067;1.0000" values="0;0;1;1"/><rect x="250.0" y="130" width="14" height="240.0" fill="#94a3b8"/>
<circle cx="96.88" cy="360.17" r="89.83" fill="#2ea043" fill-opacity="0.12" stroke="#2ea043" stroke-width="1.5"/>
<circle cx="96.88" cy="360.17" r="3.5" fill="#2ea043"/>
<circle cx="103.77" cy="350.34" r="99.66" fill="#2ea043" fill-opacity="0.12" stroke="#2ea043" stroke-width="1.5"/>
<circle cx="103.77" cy="350.34" r="3.5" fill="#2ea043"/>
<circle cx="117.53" cy="330.68" r="119.32" fill="#2ea043" fill-opacity="0.12" stroke="#2ea043" stroke-width="1.5"/>
<circle cx="117.53" cy="330.68" r="3.5" fill="#2ea043"/>
<circle cx="145.06" cy="291.36" r="104.94" fill="#2ea043" fill-opacity="0.12" stroke="#2ea043" stroke-width="1.5"/>
<circle cx="145.06" cy="291.36" r="3.5" fill="#2ea043"/>
<circle cx="200.13" cy="212.72" r="49.87" fill="#e5484d" fill-opacity="0.12" stroke="#e5484d" stroke-width="1.5"/>
<circle cx="200.13" cy="212.72" r="3.5" fill="#e5484d"/>
<text x="50" y="128" text-anchor="start" style="font-size:18px;font-weight:700;fill:#7c3aed">壁までの距離 a = 2</text>
</g>
<rect x="620" y="96" width="310" height="300" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="620" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">② 5 歩の計算</text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2798;0.2800;1.0000" values="1;1;0;0"/><text x="636" y="136" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">歩 1: 距離 0.15 / 距離場 0.11 → 遮蔽 0.24</text>
<text x="636" y="166" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">歩 2: 距離 0.30 / 距離場 0.03 → 遮蔽 0.91</text>
<text x="636" y="196" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">歩 3: 距離 0.60 / 距離場 0.00 → 遮蔽 1.00</text>
<text x="636" y="226" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">歩 4: 距離 1.20 / 距離場 0.00 → 遮蔽 1.00</text>
<text x="636" y="256" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">歩 5: 距離 2.40 / 距離場 0.00 → 遮蔽 1.00</text>
<text x="636" y="330" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed">AO = 0.35</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2798;0.2800;0.4932;0.4933;1.0000" values="0;0;1;1;0;0"/><text x="636" y="136" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">歩 1: 距離 0.15 / 距離場 0.41 → 遮蔽 0.00</text>
<text x="636" y="166" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">歩 2: 距離 0.30 / 距離場 0.33 → 遮蔽 0.00</text>
<text x="636" y="196" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">歩 3: 距離 0.60 / 距離場 0.16 → 遮蔽 0.74</text>
<text x="636" y="226" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">歩 4: 距離 1.20 / 距離場 0.00 → 遮蔽 1.00</text>
<text x="636" y="256" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">歩 5: 距離 2.40 / 距離場 0.00 → 遮蔽 1.00</text>
<text x="636" y="330" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed">AO = 0.69</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4932;0.4933;0.7065;0.7067;1.0000" values="0;0;1;1;0;0"/><text x="636" y="136" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">歩 1: 距離 0.15 / 距離場 0.91 → 遮蔽 0.00</text>
<text x="636" y="166" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">歩 2: 距離 0.30 / 距離場 0.83 → 遮蔽 0.00</text>
<text x="636" y="196" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">歩 3: 距離 0.60 / 距離場 0.66 → 遮蔽 0.00</text>
<text x="636" y="226" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">歩 4: 距離 1.20 / 距離場 0.31 → 遮蔽 0.74</text>
<text x="636" y="256" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">歩 5: 距離 2.40 / 距離場 0.00 → 遮蔽 1.00</text>
<text x="636" y="330" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed">AO = 0.83</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.7065;0.7067;1.0000" values="0;0;1;1"/><text x="636" y="136" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">歩 1: 距離 0.15 / 距離場 1.12 → 遮蔽 0.00</text>
<text x="636" y="166" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">歩 2: 距離 0.30 / 距離場 1.25 → 遮蔽 0.00</text>
<text x="636" y="196" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">歩 3: 距離 0.60 / 距離場 1.49 → 遮蔽 0.00</text>
<text x="636" y="226" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">歩 4: 距離 1.20 / 距離場 1.31 → 遮蔽 0.00</text>
<text x="636" y="256" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">歩 5: 距離 2.40 / 距離場 0.62 → 遮蔽 0.74</text>
<text x="636" y="330" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed">AO = 0.94</text>
</g>
<text x="40" y="428" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">AO(×100):</text>
<text x="150" y="432" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="1">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0798;0.0800;1.0000" values="1;1;0;0"/></text>
<text x="150" y="432" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">35<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0798;0.0800;0.2932;0.2933;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="432" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">69<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2932;0.2933;0.5065;0.5067;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="432" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">83<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5065;0.5067;0.7198;0.7200;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="432" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">94<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.7198;0.7200;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.9065;0.9067;1.0000" values="0;0;1;1"/><rect x="360" y="410" width="570" height="80" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="376" y="434" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">壁に近いほど、距離場の値が小さく(赤)、AO が暗くなる(0.35 → 0.94)</text>
<text x="376" y="457" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">読み込みは 5 回(距離場の 3D テクスチャ)。画素ごとの深度のサンプルより、少ない</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">距離場は、各点から、いちばん近い物までの距離<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">円錐の中心を数歩進み、距離場が、進んだ距離より小さければ、その分が遮蔽<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.9198;0.9200;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">画面に映らない物も、遮蔽に数えられる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.9198;0.9200;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:dfao-cone:end -->

### 円錐トレース

<strong>法線の周りの円錐（半角 θ）</strong>に沿って、<strong>距離 t</strong>だけ進んだ点での<strong>距離場の値 d(t)</strong> を読みます。<strong>d(t) が円錐の半径（t·tanθ）より小さければ、円錐が遮られている</strong>ことになります。

<div class="formula">visibility(円錐) ≈ min over t of  clamp( d(t) / (t · tanθ), 0, 1 )</div>

ここで d(t) と円錐の半径 t·tanθ を比べます。d(t) ≥ t·tanθ なら近くに表面がなく、円錐の断面全体が空いているので、可視性は 1 です。d(t) < t·tanθ なら表面が円錐の断面の内側に入っているので、遮蔽が起きておりその比（d / 半径）で割合を出します。

<strong>最小値</strong>を取る（最も遮られた所で決まる）ので<strong>ソフト シャドウの円錐トレース</strong>と同じ考え方です。

```hlsl
float ConeVisibility(float3 origin, float3 dir, float tan_half_angle) {
  float visibility = 1.0;
  float t = kStartOffset;
  for (int i = 0; i < kSteps && t < max_distance; ++i) {
    float d = SampleDistanceField(origin + dir * t);
    visibility = min(visibility, saturate(d / (t * tan_half_angle)));
    t += max(d, kMinStep);
  }
  return visibility;
}
```

<strong>数本（たとえば 9〜16 本）の円錐</strong>を<strong>法線の周りに配置</strong>して、コサインで重み付けして平均したものが、AO です。

### 距離場はどこから来るのか

距離場の中身は空間に並べた格子点ごとの「最も近い表面までの距離」です。表面の外側は正、内側は負です。作り方は 2 通りあります。

1 つは <strong>メッシュごとの SDF</strong> です。ビルド時に各メッシュを囲むボックスの中で、格子点から三角形群までの最短距離を計算して、小さな 3D テクスチャに保存します。メッシュを動かしたり回したりしても、SDF は再計算せずワールドの位置を SDF の局所座標へ変換して読めばよいので、動く剛体にも使えます。もう 1 つは <strong>グローバル SDF</strong> です。シーン全体を粗い格子（カメラ中心の入れ子）で覆いメッシュごとの SDF を合成します。遠くの物体はグローバル SDF で一度に調べられるので、トレースが速くなります。Unreal Engine の距離場 AO と距離場シャドウ、そして Lumen のソフトウェア レイトレーシングは、この 2 層の SDF を使っています。

### 円錐の配置とステップ

AO は法線を中心とした数本の円錐（たとえば 9〜16 本）に分けて評価し、各円錐の可視性を法線とのコサインで重み付けして平均します。円錐の本数が多いほど滑らかですが、コストが増えます。

ステップの進め方は <strong>球トレーシング</strong>と同じです。いま居る点での距離 d は「この距離までは表面がない」ことを保証するので、安全に d だけ進めます。遠くの表面を飛び越える心配がなく、空いた空間は少ないステップで通り抜けられます。ただし、表面に近づくと d が小さくなって、進みが遅くなります。`kMinStep` は止まってしまうのを防ぐ下限です。

### 特徴



| 利点 | 欠点 |
| --- | --- |
| ノイズが少ない（円錐 = 領域の平均。点ではない） | SDF の生成・格納が必要（メッシュごとの SDF、グローバル SDF） |
| ソフトで滑らか | 細い物・薄い物は、SDF の解像度で潰れる |
| 画面外・隠れた物も効く | 動く物体・変形に弱い（SDF の更新が高コスト） |
| レイトレ ハードウェア不要 | メモリを食う（SDF ボリューム） |


欠点は SDF の生成と格納が必要なこと（メッシュごとの SDF とグローバル SDF）、細い物や薄い物は SDF の解像度で潰れること動く物体や変形するメッシュ（スキニングされたキャラクターなど）に弱いこと、そしてメモリを食うことです。

欠点は SDF の生成と格納が必要なこと（メッシュごとの SDF とグローバル SDF）、細い物や薄い物は SDF の解像度で潰れること動く物体や変形するメッシュ（スキニングされたキャラクターなど）に弱いこと、そしてメモリを食うことです。

<strong>静的な背景</strong>には向き <strong>キャラクターなどの動く物</strong>は、別途（カプセルの近似など）扱うのが一般的です。キャラクターの骨に沿って数個のカプセルを置き「カプセルの遮蔽」を解析的な式で求めて足し合わせます。カプセルは単純な形なので円錐との交差を式で計算でき SDF の更新が不要になります。

### より良いやり方

DFAO は現在は単独の AO としてよりも Lumen のような<strong>GI の基盤</strong>として使われることが多くなりました。距離場を使ったレイ トレースを「ソフトウェアで動くレイトレース」として使い、AO や間接光を同じデータ構造で出す設計です。AO だけが欲しい場合はスクリーン空間の [GTAO](../gtao.md) を基本として、画面外の大きな遮蔽だけを距離場で補う構成が現実的です（[World-Space AO Comparison](comparison.md)）。

!!! info "ここで使われる「積分」をやさしく言うと"
    DFAO の積分は <strong>半球を数本の円錐に分けて、円錐ごとの遮られ具合を足す</strong>ことです。

    - 法線の向きの半球を 5〜9 本の円錐に粗く分ける（方向を細かく刻む代わりに、<strong>太い束で刻む</strong>）。
    - 各円錐に沿って距離場（物までの距離）を読みながら進み「円錐の、どれくらいが物に遮られたか」を見積もる。
    - 円錐ごとの結果を重みつきで足して、AO にする。

    円錐の本数が少ないので、細かい形は表せませんがレイを何百本も飛ばすよりはるかに軽く済みます。

    <strong>数式を使わないくわしい説明</strong>は [Integrals and Elevation Angles in Plain Words](../theory/integral-intuition.md) です。

## よくあるミス

??? failure "距離場の解像度が粗く、細い物の AO が出ない"
    <strong>解像度を上げる・細い物は別の方法</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 距離場の上で、円錐を進めて遮蔽を求める
    - [x] ハードウェア不要だが、距離場の管理が必要

## 参考

- Wright, "Dynamic Occlusion with Signed Distance Fields", SIGGRAPH 2015, Advances in Real-Time Rendering in Games（Unreal Engine 4 の DFAO）
- Quilez, "Sphere soft shadows / Distance functions"（距離関数の基礎。iquilezles.org）
- Crassin, Neyret, Sainz, Green, Eisemann, "Interactive Indirect Illumination Using Voxel Cone Tracing", Computer Graphics Forum (Pacific Graphics 2011)

## 関連ページ

- [Ray-Traced, Distance-Field and Voxel AO](index.md)
- [Ray-Traced AO (RTAO)](rtao.md)
- [Distance Field Shadows](../../shadows/sdf-shadows.md)
