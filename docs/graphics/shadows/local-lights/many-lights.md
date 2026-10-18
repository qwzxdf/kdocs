---
title: Shadows for Many Lights
tags:
  - 描画
---

# Shadows for Many Lights

**影を持つライトが数十個になる**と、**すべてにシャドウ マップを作ると、フレームが破綻**します。**そこで、シャドウ マップを 1 枚の大きなアトラスにまとめ、画面上の大きさに応じて解像度を配分し、静止したライトの影はキャッシュ**します。このページでは、**アトラス・解像度の割り当て・キャッシュ・影付きライトの描画・バイアスと精度**を説明します。

!!! tip "ポイント"
    - **シャドウ マップを、大きなアトラスにまとめて管理**する。
    - **画面上で大きい・近いライトに、大きな解像度**を割り当てる。
    - **静止したライトと静止した物の影は、キャッシュして、毎フレーム描かない**。
    - **影を持つライトの数に、上限**を設ける。

<!-- fig:many-lights-cache:begin -->

<svg class="fig illust motion" data-fig="many-lights-cache" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-many-lights-cache" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">多数のライトの影:毎フレーム、少しずつ更新して、予算に収める</text>
<rect x="50" y="100" width="100" height="90" rx="8" fill="#e0f2fe" stroke="#38bdf8" stroke-width="2"/>
<text x="100.0" y="128" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ライト 1</text>
<text x="100.0" y="152" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">静止</text>
<rect x="164" y="100" width="100" height="90" rx="8" fill="#e0f2fe" stroke="#38bdf8" stroke-width="2"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0667;0.1292;0.1917;0.2542;0.3167;0.3792;0.4417;0.5042;0.5667;0.6292;0.6917;0.7542;0.8167;0.8792" values="#e0f2fe;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a"/></rect>
<text x="214.0" y="128" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ライト 2</text>
<text x="214.0" y="152" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#e5484d">動く</text>
<rect x="278" y="100" width="100" height="90" rx="8" fill="#e0f2fe" stroke="#38bdf8" stroke-width="2"/>
<text x="328.0" y="128" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ライト 3</text>
<text x="328.0" y="152" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">静止</text>
<rect x="392" y="100" width="100" height="90" rx="8" fill="#e0f2fe" stroke="#38bdf8" stroke-width="2"/>
<text x="442.0" y="128" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ライト 4</text>
<text x="442.0" y="152" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">静止</text>
<rect x="506" y="100" width="100" height="90" rx="8" fill="#e0f2fe" stroke="#38bdf8" stroke-width="2"/>
<text x="556.0" y="128" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ライト 5</text>
<text x="556.0" y="152" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">静止</text>
<rect x="620" y="100" width="100" height="90" rx="8" fill="#e0f2fe" stroke="#38bdf8" stroke-width="2"/>
<text x="670.0" y="128" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ライト 6</text>
<text x="670.0" y="152" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">静止</text>
<rect x="50" y="204" width="100" height="90" rx="8" fill="#e0f2fe" stroke="#38bdf8" stroke-width="2"/>
<text x="100.0" y="232" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ライト 7</text>
<text x="100.0" y="256" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">静止</text>
<rect x="164" y="204" width="100" height="90" rx="8" fill="#e0f2fe" stroke="#38bdf8" stroke-width="2"/>
<text x="214.0" y="232" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ライト 8</text>
<text x="214.0" y="256" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">静止</text>
<rect x="278" y="204" width="100" height="90" rx="8" fill="#e0f2fe" stroke="#38bdf8" stroke-width="2"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0667;0.1292;0.1917;0.2542;0.3167;0.3792;0.4417;0.5042;0.5667;0.6292;0.6917;0.7542;0.8167;0.8792" values="#e0f2fe;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a"/></rect>
<text x="328.0" y="232" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ライト 9</text>
<text x="328.0" y="256" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#e5484d">動く</text>
<rect x="392" y="204" width="100" height="90" rx="8" fill="#e0f2fe" stroke="#38bdf8" stroke-width="2"/>
<text x="442.0" y="232" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ライト 10</text>
<text x="442.0" y="256" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">静止</text>
<rect x="506" y="204" width="100" height="90" rx="8" fill="#e0f2fe" stroke="#38bdf8" stroke-width="2"/>
<text x="556.0" y="232" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ライト 11</text>
<text x="556.0" y="256" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">静止</text>
<rect x="620" y="204" width="100" height="90" rx="8" fill="#e0f2fe" stroke="#38bdf8" stroke-width="2"/>
<text x="670.0" y="232" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ライト 12</text>
<text x="670.0" y="256" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">静止</text>
<rect x="50" y="308" width="100" height="90" rx="8" fill="#e0f2fe" stroke="#38bdf8" stroke-width="2"/>
<text x="100.0" y="336" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ライト 13</text>
<text x="100.0" y="360" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">静止</text>
<rect x="164" y="308" width="100" height="90" rx="8" fill="#e0f2fe" stroke="#38bdf8" stroke-width="2"/>
<text x="214.0" y="336" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ライト 14</text>
<text x="214.0" y="360" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">静止</text>
<rect x="278" y="308" width="100" height="90" rx="8" fill="#e0f2fe" stroke="#38bdf8" stroke-width="2"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0667;0.1292;0.1917;0.2542;0.3167;0.3792;0.4417;0.5042;0.5667;0.6292;0.6917;0.7542;0.8167;0.8792" values="#e0f2fe;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a"/></rect>
<text x="328.0" y="336" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ライト 15</text>
<text x="328.0" y="360" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#e5484d">動く</text>
<rect x="392" y="308" width="100" height="90" rx="8" fill="#e0f2fe" stroke="#38bdf8" stroke-width="2"/>
<text x="442.0" y="336" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ライト 16</text>
<text x="442.0" y="360" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">静止</text>
<rect x="506" y="308" width="100" height="90" rx="8" fill="#e0f2fe" stroke="#38bdf8" stroke-width="2"/>
<text x="556.0" y="336" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ライト 17</text>
<text x="556.0" y="360" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">静止</text>
<rect x="620" y="308" width="100" height="90" rx="8" fill="#e0f2fe" stroke="#38bdf8" stroke-width="2"/>
<text x="670.0" y="336" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ライト 18</text>
<text x="670.0" y="360" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">静止</text>
<text x="50" y="66" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">黄色 = このフレームで、シャドウ マップを描き直したライト。他は、前のフレームの結果を使い回す<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;1.0000;1.0000" values="1;1;0"/></text>
<text x="50" y="366" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">動くライト（赤い文字）は、毎フレーム更新。静止したライトは、順番に（ラウンド ロビン）、数個ずつ更新する。</text>
<text x="50" y="390" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">1 フレームに描くシャドウ マップの数に、上限を決める → コストが一定になる。</text>
</svg>

<!-- fig:many-lights-cache:end -->

## 多数のライトの影
**ライトが多い**ほど、**影の計算がすぐに破綻**します。

ライトが増えると、3 つのコストが同時に膨らみます。描画回数は、点光源が 6 回、スポットが 1 回で、ライトごとに掛かります。メモリは、キューブ 1 つ（1024²×6 面）が約 24 MB（D32）なので、数十個で数百 MB になります。フィルタのコストは、画素ごとに、影付きのライトの数だけサンプルが必要です。

### 管理の方法

| 方法 | 内容 |
| --- | --- |
| **影付きライトの数を制限** | **重要なライトだけ**影付き（例：画面の近く・大きい・明るい） |
| **優先度付け** | **画面上の大きさ・明るさ・距離**で**スコア**を付け、**上位 N 個**だけに影 |
| **アトラス** | **1 枚の大きなテクスチャ**に、**複数のシャドウ マップ**を**敷き詰める**。**ライトごとに解像度を可変**（近いライトは大きく） |
| **解像度の可変** | **画面上で小さいライト**は、**低い解像度** |
| **更新頻度** | **静的なライト・静的な物**は**キャッシュ**し、**動く物が入ったときだけ更新** |
| **遠方・画面外の除外** | **視錐台の外・遠いライト**は**描かない** |

### シャドウ マップのキャッシュ

**静的なシーンのシャドウ マップ**は、**一度描いた結果を再利用**できます。

キャッシュの戦略です。静的なジオメトリの影はキャッシュし、動的な物の影だけを毎フレーム上書き（または合成）します。動かないライトは、ライトが動いたときだけ再生成し、そうでなければ再描画しません。動く物のいる範囲だけを部分的に更新するダーティ領域の管理もあります。

**2 枚**（静的用・動的用）を**持ち、画素ごとに両方を引いて、小さい方（より暗い方）を取る**方法もあります。

## 影のあるライトの描画での使い方
**ライティング**の段階で**ライトごとの影の係数**を、**そのライトの寄与に掛けます**。

```hlsl
float shadow = SpotShadow(world_pos, light_index);
float3 lit = EvaluateLight(light, surface) * shadow;
```

**クラスター ライティング**・**タイル ベース**と組み合わせると、**影付きライトの情報**を**ライト リストに含めて、引けるようにします**（[ライト カリング](../../../rendering/light-culling.md)）。

## バイアスと精度
バイアスと精度の注意点です。透視投影の深度は非線形で、近くに集中して遠くで精度が不足します。近クリップ面を大きく、遠クリップ面を短くして精度を保ちます。バイアスは距離によって必要な量が変わるので、ワールド単位の法線オフセットが扱いやすいです（[Shadow Bias](../bias/index.md)）。Reversed-Z は、シャドウ マップにも有効です（浮動小数点の深度）。

## よくあるミス

??? failure "影付きライトの数が増えて、フレーム時間が増える一方"
    **影付きライトの数に上限・距離で影を切る・キャッシュ**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **アトラスで管理・解像度を配分・キャッシュ**
    - [x] **影付きライトの数を制限**

## 参考

- Eisemann et al., "Real-Time Shadows"（CRC Press 2011）
- Microsoft, "Common Techniques to Improve Shadow Depth Maps"（Microsoft Learn）

## 関連ページ

- [Point and Spot Light Shadows](index.md)
- [Virtual Shadow Maps](../virtual-shadow-maps.md)
- [Tiled と Clustered](../../../rendering/light-culling.md)
