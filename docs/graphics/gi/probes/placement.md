---
title: プローブの置き方
tags:
  - 描画
---

# プローブの置き方

**プローブは、多いほど精密ですが、メモリとベイクの時間が増えます**。**格子状に置く方法と、重要な所に手動で置く方法**があります。このページでは、**置き方の方針と、密度の決め方**を説明します。

!!! tip "ポイント"
    - **格子状に自動配置 ＋ 重要な所を手動で補う**。
    - **光が変化する所（窓・影の境目）は密に**。
    - **壁の中に置かない**（無効なプローブは、補間から外す）。
    - **密度が低いと、光がぼやけ、漏れる**。

## 置き方
**プローブの配置**は、**品質**に直結します。

| 指針 | 内容 |
| --- | --- |
| **光が変化する場所に密に** | **明暗の境目・窓の近く・照明の近く** |
| **動く物体が通る場所に置く** | **通路・部屋・キャラが歩く範囲** |
| **壁の両側に置く** | **壁の内側にプローブがあると、反対側の光**が**混ざる**（**ライト リーク**） |
| **家具の中・壁の中は避ける** | **幾何の内部**のプローブは、<strong>黒（または不正な値）</strong>に |
| **高さ方向にも** | **床・腰・頭**の**数段** |
| **自動配置** | **格子を自動生成**し、**幾何の内側のプローブを、除外・補完** |

<!-- fig:probe-light-leak:begin -->

<svg class="fig illust motion" data-fig="probe-light-leak" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-probe-light-leak" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">ライト リーク:壁の向こうのプローブが、混ざってしまう</text>
<text x="40" y="68" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d">可視性なし（そのまま補間）</text>
<rect x="40" y="90" width="330" height="220" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="202" y="90" width="10" height="220" fill="#475569"/>
<text x="130" y="108" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">暗い部屋</text>
<text x="290" y="108" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">明るい部屋</text>
<rect x="40" y="90" width="162" height="220" fill="#0f172a" fill-opacity="0.22"/>
<circle cx="80" cy="150" r="11" fill="#5a5a5a" stroke="#1f2937" stroke-width="2"/>
<circle cx="80" cy="260" r="11" fill="#5a5a5a" stroke="#1f2937" stroke-width="2"/>
<circle cx="330" cy="150" r="11" fill="#f3f3f3" stroke="#1f2937" stroke-width="2"/>
<circle cx="330" cy="260" r="11" fill="#f3f3f3" stroke="#1f2937" stroke-width="2"/>
<circle cx="160" cy="200" r="9" fill="#ffffff" stroke="#1f2937" stroke-width="3"><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.1440;0.2080;0.2720;0.3360;0.4000;0.4640;0.5280;0.5920;0.6560;0.7200;1.0000" values="160;160;100;109;118;127;136;145;154;163;172;181;190;190"/></circle>
<rect x="130" y="330" width="150" height="30" fill="#888888" stroke="#94a3b8" stroke-width="1.5"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.1440;0.2080;0.2720;0.3360;0.4000;0.4640;0.5280;0.5920;0.6560;0.7200;1.0000" values="#888888;#888888;#8a8a8a;#8f8f8f;#949494;#989898;#9d9d9d;#a1a1a1;#a5a5a5;#a9a9a9;#adadad;#b1b1b1;#b4b4b4;#b4b4b4"/></rect>
<text x="205" y="352" text-anchor="start" style="font-size:1px;font-weight:700;fill:#ffffff">→</text>
<text x="60" y="352" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">結果:</text>
<text x="400" y="68" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">可視性あり（壁の向こうは除く）</text>
<rect x="400" y="90" width="330" height="220" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="562" y="90" width="10" height="220" fill="#475569"/>
<text x="490" y="108" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">暗い部屋</text>
<text x="650" y="108" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">明るい部屋</text>
<rect x="400" y="90" width="162" height="220" fill="#0f172a" fill-opacity="0.22"/>
<circle cx="440" cy="150" r="11" fill="#5a5a5a" stroke="#1f2937" stroke-width="2"/>
<circle cx="440" cy="260" r="11" fill="#5a5a5a" stroke="#1f2937" stroke-width="2"/>
<circle cx="690" cy="150" r="11" fill="#f3f3f3" stroke="#1f2937" stroke-width="2"/>
<circle cx="690" cy="260" r="11" fill="#f3f3f3" stroke="#1f2937" stroke-width="2"/>
<circle cx="520" cy="200" r="9" fill="#ffffff" stroke="#1f2937" stroke-width="3"><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.1440;0.2080;0.2720;0.3360;0.4000;0.4640;0.5280;0.5920;0.6560;0.7200;1.0000" values="520;520;460;469;478;487;496;505;514;523;532;541;550;550"/></circle>
<rect x="490" y="330" width="150" height="30" fill="#888888" stroke="#94a3b8" stroke-width="1.5"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.1440;0.2080;0.2720;0.3360;0.4000;0.4640;0.5280;0.5920;0.6560;0.7200;1.0000" values="#888888;#888888;#5a5a5a;#5a5a5a;#5a5a5a;#5a5a5a;#5a5a5a;#5a5a5a;#5a5a5a;#5a5a5a;#5a5a5a;#5a5a5a;#5a5a5a;#5a5a5a"/></rect>
<text x="565" y="352" text-anchor="start" style="font-size:1px;font-weight:700;fill:#ffffff">→</text>
<text x="420" y="352" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">結果:</text>
<text x="40" y="386" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">暗い部屋の中の点を、壁へ近づける<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;1.0000" values="1;1;0;0"/></text>
<text x="40" y="386" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">左:壁の向こうの明るいプローブが混ざり、暗い部屋が明るくなる（漏れ）。右:壁越しは重み 0 → 暗いまま<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:probe-light-leak:end -->

### ライト リーク（壁越しの漏れ）

**プローブ間の補間**は、**壁の存在を知らない**ので、**壁の向こう側のプローブの光**が、**こちら側に漏れる**ことがあります。

| 対策 | 内容 |
| --- | --- |
| **プローブの配置の工夫** | **壁の近くを密に**・**壁の両側にそれぞれ**置く |
| **可視性の重み付け** | **物体から、プローブが見えるか**を**判定**し、**見えないプローブの重みを下げる**（[DDGI](../ddgi.md)の方式） |
| <strong>ボリュームの分割（ゾーン）</strong> | **部屋ごと**に**プローブ グループを分ける** |
| **法線バイアス** | **物体の位置を法線方向に少しずらして**、**補間** |

## よくあるミス

??? failure "プローブが壁の中にあって、暗い・おかしな色になる"
    **壁の中のプローブは無効にして、補間から外す**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **格子 ＋ 手動で補う**
    - [x] **変化の大きい所を密に**

## 参考

- Kajiya, "The Rendering Equation"（SIGGRAPH 1986）
- Ramamoorthi & Hanrahan, "An Efficient Representation for Irradiance Environment Maps"（SIGGRAPH 2001）
- Majercik et al., "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields"（JCGT 2019）

## 関連ページ

- [プローブ GI](index.md)
- [補間の方式](interpolation.md)
- [動的な更新](dynamic-update.md)
