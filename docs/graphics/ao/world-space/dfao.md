---
title: 距離場 AO（DFAO）
tags:
  - 描画
---

# 距離場 AO（DFAO）

**距離場 AO は、シーンを「符号付き距離場（各点から、最も近い面までの距離）」で表し、その距離場の上で円錐を進めて、遮蔽を求めます**。**レイトレーシングのハードウェアが無くても、画面外の遮蔽を含む AO が得られます**。**距離場は事前計算（静的）**で、**動く物体は別途扱います**。このページでは、**距離場とは・円錐トレースによる AO・長所と短所**を説明します。

!!! tip "ポイント"
    - **距離場 ＝ 各点から、最も近い面までの符号付き距離**。
    - **距離場上を、円錐で進み、距離が小さければ遮蔽**。
    - **ハードウェア レイトレ不要**。
    - **弱点**：**距離場の解像度・動く物体・メモリ**。

## 距離場 AO（DFAO）
<strong>符号付き距離場（SDF）</strong>は、**空間の各点から、最も近い表面までの距離**を、3D テクスチャに格納したものです。**距離がわかる**ので**円錐に沿って歩く**と**遮蔽の割合**を**サンプルを数えずに**求められます。

<!-- fig:dfao-cone:begin -->

<svg class="fig illust motion" data-fig="dfao-cone" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-dfao-cone" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">距離場 AO:円錐を進めて、距離と円錐の幅を比べる</text>
<rect x="40" y="330" width="700" height="16" fill="#d6c7a1"/>
<circle cx="430" cy="205" r="42" fill="#b8794b" stroke="#7a4b2a" stroke-width="2"/>
<circle cx="120" cy="330" r="8" fill="#2563eb" stroke="#ffffff" stroke-width="2"/>
<line x1="120" y1="330" x2="678.6358681455016" y2="369.06362529671014" stroke="#cbd5e1" stroke-width="1.5" stroke-dasharray="5 4"/>
<line x1="120" y1="330" x2="614.4506520009991" y2="67.09592483990116" stroke="#cbd5e1" stroke-width="1.5" stroke-dasharray="5 4"/>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="0;0;1;1"/><circle cx="143.48" cy="325.01" r="6.88" fill="none" stroke="#e5aa28" stroke-width="2"/>
<circle cx="143.48" cy="325.01" r="160" fill="none" stroke="#2ea043" stroke-width="2" stroke-dasharray="4 3"/>
<circle cx="143.48" cy="325.01" r="4" fill="#1f2937"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1553;0.1556;1.0000" values="0;0;1;1"/><circle cx="379.97" cy="274.74" r="76.21" fill="none" stroke="#e5aa28" stroke-width="2"/>
<circle cx="379.97" cy="274.74" r="43.83" fill="none" stroke="#2ea043" stroke-width="2" stroke-dasharray="4 3"/>
<circle cx="379.97" cy="274.74" r="4" fill="#1f2937"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2367;0.2370;1.0000" values="0;0;1;1"/><circle cx="420.97" cy="266.03" r="88.23" fill="none" stroke="#e5aa28" stroke-width="2"/>
<circle cx="420.97" cy="266.03" r="19.69" fill="none" stroke="#2ea043" stroke-width="2" stroke-dasharray="4 3"/>
<circle cx="420.97" cy="266.03" r="4" fill="#1f2937"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3182;0.3185;1.0000" values="0;0;1;1"/><circle cx="468.44" cy="255.94" r="102.14" fill="none" stroke="#e5aa28" stroke-width="2"/>
<circle cx="468.44" cy="255.94" r="21.81" fill="none" stroke="#2ea043" stroke-width="2" stroke-dasharray="4 3"/>
<circle cx="468.44" cy="255.94" r="4" fill="#1f2937"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3997;0.4000;1.0000" values="0;0;1;1"/><circle cx="523.39" cy="244.26" r="118.25" fill="none" stroke="#e5aa28" stroke-width="2"/>
<circle cx="523.39" cy="244.26" r="59.3" fill="none" stroke="#2ea043" stroke-width="2" stroke-dasharray="4 3"/>
<circle cx="523.39" cy="244.26" r="4" fill="#1f2937"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4812;0.4815;1.0000" values="0;0;1;1"/><circle cx="587.01" cy="230.73" r="136.9" fill="none" stroke="#e5aa28" stroke-width="2"/>
<circle cx="587.01" cy="230.73" r="117.1" fill="none" stroke="#2ea043" stroke-width="2" stroke-dasharray="4 3"/>
<circle cx="587.01" cy="230.73" r="4" fill="#1f2937"/>
</g>
<text x="40" y="60" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">ステップ 1:最も近い物までの距離 d = 269、円錐の半径 = 7 → 遮蔽を 0.00 足す（合計 0.00）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.1553;0.1556;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="60" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">ステップ 2:最も近い物までの距離 d = 44、円錐の半径 = 76 → 遮蔽を 0.42 足す（合計 0.42）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1553;0.1556;0.2367;0.2370;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="60" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">ステップ 3:最も近い物までの距離 d = 20、円錐の半径 = 88 → 遮蔽を 0.45 足す（合計 0.87）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2367;0.2370;0.3182;0.3185;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="60" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">ステップ 4:最も近い物までの距離 d = 22、円錐の半径 = 102 → 遮蔽を 0.10 足す（合計 0.97）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3182;0.3185;0.3997;0.4000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="60" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">ステップ 5:最も近い物までの距離 d = 59、円錐の半径 = 118 → 遮蔽を 0.01 足す（合計 0.99）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3997;0.4000;0.4812;0.4815;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="60" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">ステップ 6:最も近い物までの距離 d = 117、円錐の半径 = 137 → 遮蔽を 0.00 足す（合計 0.99）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4812;0.4815;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="394" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d" opacity="0">→ この円錐の遮蔽 ≒ 0.99。円錐を数方向に飛ばして、平均が AO になる<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5627;0.5630;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="412" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">緑の点線の円 = 距離場の距離 d、橙の円 = 円錐の断面。d が円錐より小さいほど、遮蔽される。</text>
</svg>

<!-- fig:dfao-cone:end -->

### 円錐トレース

<strong>法線の周りの円錐（半角 θ）</strong>に沿って、**距離 t**だけ進んだ点での<strong>距離場の値 d(t)</strong> を読みます。**d(t) が、円錐の半径（t·tanθ）より小さければ、円錐が遮られている**ことになります。

<div class="formula">visibility(円錐) ≈ min over t of  clamp( d(t) / (t · tanθ), 0, 1 )</div>

| d(t) と円錐の半径 | 意味 |
| --- | --- |
| **d(t) ≥ t·tanθ** | 近くに表面がない。円錐の断面全体が空いている → 1 |
| **d(t) < t·tanθ** | 表面が円錐の断面の内側に入っている → 遮蔽。**比で割合を出す** |

**最小値**を取る（最も遮られた所で決まる）ので**ソフト シャドウの円錐トレース**と同じ考え方です。

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

**数本（たとえば 9〜16 本）の円錐**を**法線の周りに配置**して、**コサインで重み付けして平均**したものが、AO です。

### 特徴

| 利点 | 欠点 |
| --- | --- |
| **ノイズが少ない**（円錐 = 領域の平均。点ではない） | **SDF の生成・格納**が必要（メッシュごとの SDF、グローバル SDF） |
| **ソフトで滑らか** | **細い物・薄い物は、SDF の解像度**で潰れる |
| **画面外・隠れた物も効く** | **動く物体・変形**に弱い（SDF の更新が高コスト） |
| **レイトレ ハードウェア不要** | **メモリを食う**（SDF ボリューム） |

**静的な背景**には向き、**キャラクターなどの動く物**は、別途（**カプセルの近似**など）扱うのが一般的です。

## よくあるミス

??? failure "距離場の解像度が粗く、細い物の AO が出ない"
    **解像度を上げる・細い物は別の方法**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **距離場の上で、円錐を進めて遮蔽を求める**
    - [x] **ハードウェア不要だが、距離場の管理が必要**

## 参考

- Mittring, "Finding Next Gen: CryEngine 2"（SIGGRAPH 2007）
- Jimenez et al., "Practical Real-Time Strategies for Accurate Indirect Occlusion"（SIGGRAPH 2016）

## 関連ページ

- [世界空間 AO](index.md)
- [レイトレース AO](rtao.md)
- [Distance Field Shadows](../../shadows/sdf-shadows.md)
