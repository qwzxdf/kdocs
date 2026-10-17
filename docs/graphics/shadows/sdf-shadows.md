---
title: Distance Field Shadows
tags:
  - 描画
---

# Distance Field Shadows

**シャドウ マップ**は、**光から見た深度**を描きます。**距離場の影**（Distance Field Shadows）は、**シーンを符号付き距離場（SDF）として持ち**、**画素から光へ向かう**レイを、**距離場の上で進め**て、**遮蔽を調べる**方式です。**距離場**には<strong>「最も近い物までの距離」</strong>が入っているので**レイを安全な距離だけ一気に進められ**（**スフィア トレーシング**）、<strong>「どれだけ、ぎりぎりをかすめたか」</strong>から、**柔らかい半影**を**ほぼ無料で**作れます。**静的なシーン**・**遠景**の影に向きます。

!!! tip "ポイント"
    - <strong>SDF</strong>：空間の各点に<strong>最も近い表面までの距離</strong>を保存（<strong>3D テクスチャ</strong>）。
    - <strong>スフィア トレーシング</strong>：<strong>その距離だけ、安全に進む</strong>。<strong>数ステップ</strong>で遠くまで届く。
    - <strong>半影</strong>：レイが<strong>物の近くを通るほど暗く</strong>なる。<strong>min(k · d / t)</strong> で、<strong>ソフトな影</strong>が<strong>追加コストなし</strong>。
    - <strong>光源の大きさ</strong>を<strong>k</strong> で調整できる。<strong>接触硬化</strong>が自然に出る。
    - <strong>メッシュの SDF を、事前に作る</strong>（<strong>静的</strong>）。<strong>動く物・変形</strong>に弱い。
    - <strong>メモリ・SDF の解像度</strong>が品質を決める。<strong>細い物</strong>が<strong>消える</strong>ことがある。

## 符号付き距離場（SDF）とは

**SDF**（Signed Distance Field）は、<strong>空間の各点に、「最も近い表面までの距離」</strong>を入れたものです。**表面の外側は正、内側は負**です。

| 点の位置 | SDF の値 |
| --- | --- |
| **表面の外側** | **正**（表面までの最短距離） |
| **表面上** | **0** |
| **表面の内側** | **負** |

**メッシュ**からは、<strong>格子（3D テクスチャ）</strong>に、**各点の距離**を**事前計算**して作ります（**ボクセルごとに最も近い三角形までの距離**）。

## スフィア トレーシング

**距離場の最大の利点**は、<strong>「距離」が、「安全に進める量」</strong>だということです。**ある点の距離が d** なら、**半径 d の球の中には、表面がない**ので**どの方向にも、d だけ進んでも表面にぶつかりません**。

<svg class="fig illust" viewBox="0 0 780 270" role="img" aria-label="スフィア トレーシング">
<text x="20" y="24" class="fig-title">各点の「最も近い物までの距離」だけ、安全に進む（スフィア トレーシング）</text>
<path d="M 450 250 Q 480 150 560 130 Q 650 120 720 240 L 720 250 Z" fill="rgba(150,150,150,0.5)" stroke="currentColor" stroke-width="2"/><text x="520" y="200" style="font-size:12px">形</text>
<circle cx="70" cy="220" r="6" fill="currentColor"/><text x="50" y="244" style="font-size:12px">画素</text>
<circle cx="70" cy="220" r="60" fill="none" stroke="currentColor" stroke-dasharray="4 3" opacity="0.5"/>
<circle cx="140" cy="190" r="6" fill="currentColor"/><circle cx="140" cy="190" r="86" fill="none" stroke="currentColor" stroke-dasharray="4 3" opacity="0.5"/>
<circle cx="240" cy="155" r="6" fill="currentColor"/><circle cx="240" cy="155" r="112" fill="none" stroke="currentColor" stroke-dasharray="4 3" opacity="0.5"/>
<circle cx="362" cy="115" r="6" fill="currentColor"/><circle cx="362" cy="115" r="60" fill="none" stroke="currentColor" stroke-dasharray="4 3" opacity="0.5"/>
<line x1="70" y1="220" x2="700" y2="40" stroke="currentColor" stroke-width="2"/><text x="640" y="32" style="font-size:12px">光へ</text>
<text x="40" y="270" style="font-size:12px">ステップごとに、距離（点線の円の半径）だけ進む。表面に近づくほど、ステップが小さくなる</text>
</svg>

| 項目 | 内容 |
| --- | --- |
| **ステップの大きさ** | **その点の SDF の値** |
| **終了条件** | **SDF がほぼ 0**（表面に当たった）→ 影。**光に十分近づいた・最大距離**に達した → 日向 |
| **ステップ数** | **開けた空間では少なく**（大きく進める）。**物の近くでは増える** |

```hlsl
float SphereTraceShadow(float3 origin, float3 light_dir) {
  float t = kStartOffset;
  [loop] for (int i = 0; i < kMaxSteps; ++i) {
    float3 p = origin + light_dir * t;
    float d = SampleSDF(p);
    if (d < kHitEpsilon) return 0.0;
    t += d;
    if (t > kMaxDistance) break;
  }
  return 1.0;
}
```

<!-- fig:sdf-soft-shadow:begin -->

<svg class="fig illust motion" data-fig="sdf-soft-shadow" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-sdf-soft-shadow" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">SDF のソフト シャドウ:球で安全な距離を測りながら、最小の隙間を覚える</text>
<circle cx="330" cy="276" r="38" fill="#b8794b" stroke="#7a4b2a" stroke-width="2"/>
<circle cx="90" cy="300" r="7" fill="#2563eb"/>
<text x="80" y="324" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">影を調べたい点</text>
<circle cx="680" cy="130" r="13" fill="#e5aa28"/>
<text x="674" y="110" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5aa28">光</text>
<line x1="90" y1="300" x2="680" y2="130" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="4 4"/>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="0;0;1;1"/><circle cx="97.69" cy="297.79" r="120" fill="none" stroke="#2ea043" stroke-width="2" stroke-dasharray="4 3"/>
<circle cx="97.69" cy="297.79" r="4" fill="#2ea043"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1330;0.1333;1.0000" values="0;0;1;1"/><circle cx="285.38" cy="243.7" r="17.08" fill="none" stroke="#2ea043" stroke-width="2" stroke-dasharray="4 3"/>
<circle cx="285.38" cy="243.7" r="4" fill="#2ea043"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1923;0.1926;1.0000" values="0;0;1;1"/><circle cx="301.79" cy="238.97" r="8.54" fill="none" stroke="#2ea043" stroke-width="2" stroke-dasharray="4 3"/>
<circle cx="301.79" cy="238.97" r="4" fill="#2ea043"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2516;0.2519;1.0000" values="0;0;1;1"/><circle cx="310.01" cy="236.61" r="6.18" fill="none" stroke="#2ea043" stroke-width="2" stroke-dasharray="4 3"/>
<circle cx="310.01" cy="236.61" r="4" fill="#2ea043"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3108;0.3111;1.0000" values="0;0;1;1"/><circle cx="315.94" cy="234.9" r="5.44" fill="none" stroke="#2ea043" stroke-width="2" stroke-dasharray="4 3"/>
<circle cx="315.94" cy="234.9" r="4" fill="#2ea043"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3701;0.3704;1.0000" values="0;0;1;1"/><circle cx="321.71" cy="233.24" r="5.56" fill="none" stroke="#2ea043" stroke-width="2" stroke-dasharray="4 3"/>
<circle cx="321.71" cy="233.24" r="4" fill="#2ea043"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4293;0.4296;1.0000" values="0;0;1;1"/><circle cx="327.47" cy="231.58" r="6.5" fill="none" stroke="#2ea043" stroke-width="2" stroke-dasharray="4 3"/>
<circle cx="327.47" cy="231.58" r="4" fill="#2ea043"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4886;0.4889;1.0000" values="0;0;1;1"/><circle cx="333.71" cy="229.78" r="8.37" fill="none" stroke="#2ea043" stroke-width="2" stroke-dasharray="4 3"/>
<circle cx="333.71" cy="229.78" r="4" fill="#2ea043"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5479;0.5481;1.0000" values="0;0;1;1"/><circle cx="341.76" cy="227.46" r="11.94" fill="none" stroke="#2ea043" stroke-width="2" stroke-dasharray="4 3"/>
<circle cx="341.76" cy="227.46" r="4" fill="#2ea043"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6071;0.6074;1.0000" values="0;0;1;1"/><circle cx="353.23" cy="224.15" r="18.81" fill="none" stroke="#2ea043" stroke-width="2" stroke-dasharray="4 3"/>
<circle cx="353.23" cy="224.15" r="4" fill="#2ea043"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6664;0.6667;1.0000" values="0;0;1;1"/><circle cx="371.31" cy="218.94" r="32.44" fill="none" stroke="#2ea043" stroke-width="2" stroke-dasharray="4 3"/>
<circle cx="371.31" cy="218.94" r="4" fill="#2ea043"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7256;0.7259;1.0000" values="0;0;1;1"/><circle cx="402.48" cy="209.96" r="60.06" fill="none" stroke="#2ea043" stroke-width="2" stroke-dasharray="4 3"/>
<circle cx="402.48" cy="209.96" r="4" fill="#2ea043"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7849;0.7852;1.0000" values="0;0;1;1"/><circle cx="460.19" cy="193.33" r="116.22" fill="none" stroke="#2ea043" stroke-width="2" stroke-dasharray="4 3"/>
<circle cx="460.19" cy="193.33" r="4" fill="#2ea043"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.8441;0.8444;1.0000" values="0;0;1;1"/><circle cx="571.87" cy="161.16" r="120" fill="none" stroke="#2ea043" stroke-width="2" stroke-dasharray="4 3"/>
<circle cx="571.87" cy="161.16" r="4" fill="#2ea043"/>
</g>
<text x="40" y="52" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">ステップ 1:最も近い物までの距離 d = 195 → それだけ進む。隙間の比 k·d/t = 195.33（最小 1.00）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.1330;0.1333;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="52" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">ステップ 2:最も近い物までの距離 d = 17 → それだけ進む。隙間の比 k·d/t = 0.67（最小 0.67）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1330;0.1333;0.1923;0.1926;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="52" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">ステップ 3:最も近い物までの距離 d = 9 → それだけ進む。隙間の比 k·d/t = 0.31（最小 0.31）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1923;0.1926;0.2516;0.2519;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="52" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">ステップ 4:最も近い物までの距離 d = 6 → それだけ進む。隙間の比 k·d/t = 0.22（最小 0.22）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2516;0.2519;0.3108;0.3111;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="52" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">ステップ 5:最も近い物までの距離 d = 5 → それだけ進む。隙間の比 k·d/t = 0.19（最小 0.19）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3108;0.3111;0.3701;0.3704;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="52" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">ステップ 6:最も近い物までの距離 d = 6 → それだけ進む。隙間の比 k·d/t = 0.18（最小 0.18）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3701;0.3704;0.4293;0.4296;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="52" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">ステップ 7:最も近い物までの距離 d = 6 → それだけ進む。隙間の比 k·d/t = 0.21（最小 0.18）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4293;0.4296;0.4886;0.4889;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="52" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">ステップ 8:最も近い物までの距離 d = 8 → それだけ進む。隙間の比 k·d/t = 0.26（最小 0.18）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4886;0.4889;0.5479;0.5481;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="52" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">ステップ 9:最も近い物までの距離 d = 12 → それだけ進む。隙間の比 k·d/t = 0.36（最小 0.18）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5479;0.5481;0.6071;0.6074;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="52" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">ステップ 10:最も近い物までの距離 d = 19 → それだけ進む。隙間の比 k·d/t = 0.55（最小 0.18）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6071;0.6074;0.6664;0.6667;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="52" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">ステップ 11:最も近い物までの距離 d = 32 → それだけ進む。隙間の比 k·d/t = 0.89（最小 0.18）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6664;0.6667;0.7256;0.7259;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="52" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">ステップ 12:最も近い物までの距離 d = 60 → それだけ進む。隙間の比 k·d/t = 1.48（最小 0.18）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7256;0.7259;0.7849;0.7852;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="52" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">ステップ 13:最も近い物までの距離 d = 116 → それだけ進む。隙間の比 k·d/t = 2.41（最小 0.18）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7849;0.7852;0.8441;0.8444;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="52" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">ステップ 14:最も近い物までの距離 d = 230 → それだけ進む。隙間の比 k·d/t = 3.67（最小 0.18）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.8441;0.8444;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="390" text-anchor="start" style="font-size:16px;font-weight:700;fill:#e5484d" opacity="0">→ 影の明るさ = 0.18（最も物体に近づいた所の比で決まる）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.9034;0.9037;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="410" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">物体のそばを通るほど、比が小さくなって濃い影。遠ければ 1（影なし）。</text>
</svg>

<!-- fig:sdf-soft-shadow:end -->

## ソフト シャドウの仕組み

**スフィア トレーシングの途中**で、**レイがどれだけ物に近づいたか**を、記録します。**ぎりぎりをかすめたレイ**は、**半影の領域**にあります。

<div class="formula">shadow = min over t of ( k · d(t) / t )　（0〜1 にクランプ）</div>

| 項 | 意味 |
| --- | --- |
| <strong>d(t)</strong> | レイ上の位置 t での、SDF の値（**物までの距離**） |
| **d / t** | **距離 ÷ 進んだ距離**＝**円錐の開き角（のタンジェント）に相当** |
| **k** | **影の鋭さ**（光源の大きさの逆数）。**大きいほど鋭い** |
| **min** | **最も物に近づいた所**が**影の濃さを決める** |

```hlsl
float SoftSphereTraceShadow(float3 origin, float3 light_dir, float k) {
  float shadow = 1.0;
  float t = kStartOffset;
  [loop] for (int i = 0; i < kMaxSteps; ++i) {
    float d = SampleSDF(origin + light_dir * t);
    if (d < kHitEpsilon) return 0.0;
    shadow = min(shadow, k * d / t);
    t += d;
    if (t > kMaxDistance) break;
  }
  return saturate(shadow);
}
```

**物に近づくほど `d` が小さく**、**遠くの物（`t` が大きい）ほど、`d / t` がさらに小さく**なります。**接触部（`t` が小さい）は鋭く**、**遠くの遮蔽物は、ぼける**ので**接触硬化**が自然に出ます（[PCSS](pcss.md)と同じ性質）。

### 改良：滑らかな半影

単純な `min(k · d / t)` は、**半影に縞**（段差）が出ることがあります。**1 つ前のステップの `d` との差**から、**より正確な距離**（「最も近づいた点」）を**補間して求める**改良（**Inigo Quilez の improved soft shadows**）があります。

## メッシュからの距離場

| 方式 | 内容 |
| --- | --- |
| <strong>メッシュ SDF（オブジェクトごと）</strong> | **各メッシュの SDF を、事前計算**し、**3D テクスチャ**として保存。**配置された物体**ごとに**ワールド空間から、物体のローカル空間へ変換**して引く（**Unreal Engine の Distance Field Shadows**） |
| **グローバル SDF** | **オブジェクトの SDF を、視点の周りの大きな 1 つの SDF** に**合成**。**1 回のサンプルでシーン全体の距離**が得られる（**カスケード**で遠くを粗く） |
| **解析 SDF** | **球・箱・カプセル**など、**式で距離が出る形**。<strong>キャラクターの影（カプセル シャドウ）</strong>など |

### カプセル シャドウ

**キャラクターの骨**に<strong>カプセル（線分 ＋ 半径）</strong>を割り当て、**カプセルの SDF の式**で、**ソフトな影**を作ります。**変形するキャラクター**にも、**安い近似の影**が作れます（**シャドウ マップと併用**）。

## 長所と短所

| 長所 | 短所 |
| --- | --- |
| **ソフトな影**が**追加コストなし**（接触硬化も自然） | **静的なシーン**向き（SDF の事前計算が要る） |
| **レイのステップが少ない**（距離だけ進む） | **メモリ**（3D テクスチャ）。**SDF の解像度**で品質が決まる |
| **シャドウ マップのアクネ・解像度の問題がない** | **細い物・薄い物が、SDF で消える** |
| **遠景の影に低コスト** | **動く物・変形する物**は**別の手段**が必要 |
| **光源サイズの調整が直感的** | **半影の近似**が**物理的に正確ではない** |

## 使いどころ

| 状況 | 使い方 |
| --- | --- |
| **遠景の大きな影** | **カスケードの遠い範囲を距離場の影で**（シャドウ マップは、近くだけ） |
| **静的なシーン** | **柔らかい太陽の影**を全域で |
| **キャラクター** | **カプセル シャドウ**で柔らかい接地影 |
| <strong>間接的な、空の遮蔽（距離場 AO）</strong> | **同じ SDF を、AO にも使う**（[AO の手法](../ao/world-space/index.md)） |

## よくあるミス

??? failure "SDF の解像度が粗く、細い物（柵・葉）の影が消える"
    **解像度を上げる**・**細い物は別扱い**（シャドウ マップ）にします。

??? failure "レイの開始位置が表面にあり、自己遮蔽で真っ暗"
    **開始位置を法線方向に少しずらす**（`kStartOffset`）。

??? failure "動く物体を、静的な SDF に入れて、影が遅れる・出ない"
    **動く物はシャドウ マップ・カプセル**で補います。

??? failure "`min(k · d / t)` で、半影に縞が出る"
    **改良版**（補間による距離の補正）を使います。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>SDF</strong> ＝ <strong>各点に、最も近い表面までの距離</strong>を保存した 3D テクスチャ
    - [x] <strong>スフィア トレーシング</strong>：<strong>距離だけ安全に進む</strong>。<strong>少ないステップで遠くまで</strong>
    - [x] <strong>半影</strong> ＝ <strong>min(k · d / t)</strong>。<strong>接触硬化が自然に出る</strong>（追加コストなし）
    - [x] <strong>静的なシーン・遠景・カプセル影</strong>に向く。<strong>動く物・細い物</strong>は苦手
    - [x] <strong>シャドウ マップと併用</strong>が、実用的

## 参考

- Quilez, "soft shadows in raymarched SDFs"（iquilezles.org）
- Epic Games, "Distance Field Shadows"（Unreal Engine ドキュメント）
- Hart, "Sphere Tracing: A Geometric Method for the Antialiased Ray Tracing of Implicit Surfaces"（1996）

## 関連ページ

- [Shadows](index.md)
- [PCSS](pcss.md)
- [Cascaded Shadow Maps (CSM)](cascaded.md)
- [AO のその他の手法（距離場 AO）](../ao/world-space/index.md)
