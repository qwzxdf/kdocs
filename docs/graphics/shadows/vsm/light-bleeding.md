---
title: Light Bleeding
tags:
  - 描画
---

# Light Bleeding

**VSM は、複数の物体が重なる影で、本来は影の所に、光が漏れて見えます**。**これが光漏れ（ライト ブリーディング）**で、**VSM の最大の欠点**です。**チェビシェフの不等式は、確率の上限しか与えないので、複雑な分布では、影を薄く評価しすぎる**ためです。このページでは、**光漏れが起きる理由・見え方・簡単な対策（影の割合の再マッピング）**を説明します。

!!! tip "ポイント"
    - **光漏れ ＝ 影の中なのに、光が漏れて明るく見える**。
    - **原因 ＝ 深度の分布が、2 つの山（手前と奥の物体）になる場合、平均と分散だけでは表せない**。
    - **簡単な対策**：**影の割合を、しきい値で再マッピング**（**低い値を 0 に潰す**）。
    - **本格的な対策**：**EVSM・MSM**。

<!-- fig:vsm-light-bleeding:begin -->

<svg class="fig illust motion" data-fig="vsm-light-bleeding" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-vsm-light-bleeding" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">VSM の光漏れ: 手前の物が 2 段あると、平均と分散だけでは、影が薄くなる</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">手前の物 A(0.15)と B(0.45)が重なる所の、奥(深度 0.6)の点。正解は 4 分の 3 が影。式で出した光の割合を比べる</text>
<rect x="30" y="96" width="440" height="200" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 16 個のサンプルの深度</text>
<rect x="48" y="257.5" width="21" height="22.5" fill="#fca5a5" stroke="#64748b" stroke-width="1"/>
<rect x="74" y="257.5" width="21" height="22.5" fill="#fca5a5" stroke="#64748b" stroke-width="1"/>
<rect x="100" y="257.5" width="21" height="22.5" fill="#fca5a5" stroke="#64748b" stroke-width="1"/>
<rect x="126" y="257.5" width="21" height="22.5" fill="#fca5a5" stroke="#64748b" stroke-width="1"/>
<rect x="152" y="257.5" width="21" height="22.5" fill="#fca5a5" stroke="#64748b" stroke-width="1"/>
<rect x="178" y="257.5" width="21" height="22.5" fill="#fca5a5" stroke="#64748b" stroke-width="1"/>
<rect x="204" y="212.5" width="21" height="67.5" fill="#fcd34d" stroke="#64748b" stroke-width="1"/>
<rect x="230" y="212.5" width="21" height="67.5" fill="#fcd34d" stroke="#64748b" stroke-width="1"/>
<rect x="256" y="212.5" width="21" height="67.5" fill="#fcd34d" stroke="#64748b" stroke-width="1"/>
<rect x="282" y="212.5" width="21" height="67.5" fill="#fcd34d" stroke="#64748b" stroke-width="1"/>
<rect x="308" y="212.5" width="21" height="67.5" fill="#fcd34d" stroke="#64748b" stroke-width="1"/>
<rect x="334" y="212.5" width="21" height="67.5" fill="#fcd34d" stroke="#64748b" stroke-width="1"/>
<rect x="360" y="137.5" width="21" height="142.5" fill="#93c5fd" stroke="#64748b" stroke-width="1"/>
<rect x="386" y="137.5" width="21" height="142.5" fill="#93c5fd" stroke="#64748b" stroke-width="1"/>
<rect x="412" y="137.5" width="21" height="142.5" fill="#93c5fd" stroke="#64748b" stroke-width="1"/>
<rect x="438" y="137.5" width="21" height="142.5" fill="#93c5fd" stroke="#64748b" stroke-width="1"/>
<line x1="40" y1="190.0" x2="460" y2="190.0" stroke="#1f2937" stroke-width="2.5" stroke-dasharray="5 4"/>
<text x="458" y="184.0" text-anchor="end" style="font-size:12px;font-weight:700;fill:#1f2937">受ける点 t = 0.6</text>
<text x="48" y="118" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">A = 0.15(6 個)、B = 0.45(6 個)、地面 0.95(4 個)</text>
<rect x="500" y="96" width="430" height="200" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="500" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">② 数える と 式で出す</text>
<text x="520" y="134" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043">正解: t より奥のサンプル = 4 / 16 → 光 0.25</text>
<text x="520" y="164" text-anchor="start" style="font-size:14px;font-weight:500;fill:#1f2937">平均 μ = 0.462、分散 σ² = 0.096</text>
<text x="520" y="194" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d">σ² ÷ (σ² + (t − μ)²) = 0.836</text>
<text x="520" y="226" text-anchor="start" style="font-size:15px;font-weight:700;fill:#991b1b">→ 本当は 0.25 なのに、0.84 も光が漏れる</text>
<rect x="30" y="320" width="900" height="170" fill="#ffffff" stroke="#2ea043" stroke-width="1.8" rx="6"/>
<text x="30" y="310" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043">③ 漏れを減らす補正(低い値を 0 にして、残りを 0〜1 に伸ばす)</text>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1393;0.1395;1.0000" values="0;0;1;1"/><text x="50" y="366" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">何もしない</text>
<rect x="300" y="352" width="350.95" height="20" fill="#e5484d" opacity="0.85"/>
<text x="658.9510869565217" y="367" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">光 0.84</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2975;0.2977;1.0000" values="0;0;1;1"/><text x="50" y="398" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">0.2 以下を 0 にして伸ばす</text>
<rect x="300" y="384" width="333.69" height="20" fill="#e5484d" opacity="0.85"/>
<text x="641.6888586956522" y="399" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">光 0.79</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4556;0.4558;1.0000" values="0;0;1;1"/><text x="50" y="430" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">0.4 以下を 0 にして伸ばす</text>
<rect x="300" y="416" width="304.92" height="20" fill="#e5484d" opacity="0.85"/>
<text x="612.9184782608695" y="431" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">光 0.73</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6138;0.6140;1.0000" values="0;0;1;1"/><text x="50" y="462" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">0.6 以下を 0 にして伸ばす</text>
<rect x="300" y="448" width="247.38" height="20" fill="#e5484d" opacity="0.85"/>
<text x="555.3777173913044" y="463" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">光 0.59</text>
</g>
<line x1="405.0" y1="340" x2="405.0" y2="482" stroke="#2ea043" stroke-width="2.5" stroke-dasharray="6 5"/>
<text x="411.0" y="336" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">正解 0.25</text>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.7719;0.7721;1.0000" values="0;0;1;1"/><rect x="500" y="96" width="430" height="200" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="516" y="120" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1e3a8a">補正を強くすると漏れは減るが、</text>
<text x="516" y="144" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1e3a8a">薄い影も消えやすい(補正 0.6 で光 0.59)</text>
<text x="516" y="168" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">→ 補正値は、見た目で調整する</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">平均と分散だけでは、「手前の物が 2 段ある」ことが分からない<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1393;0.1395;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">漏れを、低い値を切り捨てる補正で、減らしていく<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1393;0.1395;0.7719;0.7721;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">補正のしすぎは、薄い影を消す<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.7719;0.7721;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:vsm-light-bleeding:end -->

## 弱点：光漏れ（ライト ブリーディング）
VSM は<strong>「分散」と「平均」だけ</strong>しか見ません。**遮蔽物が複数あり、深度が違う**場合、**統計だけでは区別できず**、**影の中に光が漏れた**ように見える部分が出ます。

<svg class="fig illust" viewBox="0 0 780 270" role="img" aria-label="VSM の光漏れ">
<text x="20" y="24" class="fig-title">深度の異なる遮蔽物が重なると、統計だけでは区別できず、影に光が漏れる</text>
<rect x="100" y="60" width="140" height="14" fill="rgba(150,150,150,0.7)" stroke="currentColor" stroke-width="2"/><text x="108" y="54" style="font-size:12px">遮蔽物 A（手前）</text>
<rect x="160" y="110" width="140" height="14" fill="rgba(150,150,150,0.5)" stroke="currentColor" stroke-width="2"/><text x="308" y="124" style="font-size:12px">遮蔽物 B（奥）</text>
<line x1="60" y1="230" x2="560" y2="230" stroke="currentColor" stroke-width="4"/><text x="60" y="254" style="font-size:12px">受け手</text>
<rect x="160" y="226" width="80" height="8" fill="#111" opacity="0.8"/><rect x="240" y="226" width="60" height="8" fill="#888" opacity="0.5"/>
<text x="330" y="190" style="font-size:12px;fill:#e5484d;font-weight:700">B の影の領域のうち、A に遮られていない所が、</text>
<text x="330" y="208" style="font-size:12px;fill:#e5484d;font-weight:700">本来より、薄く（明るく）見える ＝ 光漏れ</text>
<text x="400" y="100" style="font-size:12px">原因：A と B の深度の平均・分散だけでは、</text>
<text x="400" y="118" style="font-size:12px">「どちらが、何割か」が、分からない</text>
</svg>

### 対策

| 対策 | 内容 |
| --- | --- |
| <strong>光漏れの低減（リマップ）</strong> | 日向の割合 `p` を、**`(p − a) / (1 − a)`**（`a` は 0.2〜0.5）で、**下側を切り捨てて**引き伸ばす。**薄い漏れを消せる**が**半影の滑らかさが減る** |
| **分散の下限を調整** | `kMinVariance` を大きく |
| **ESM・EVSM・MSM** | 方式を変える（下記） |
| **遮蔽物の深度差を小さく** | シーンの設計（**重なりを少なく**） |

```hlsl
float ReduceLightBleeding(float p_max, float amount) {
  return saturate((p_max - amount) / (1.0 - amount));
}
```

## よくあるミス

??? failure "光漏れを消そうとしきい値を上げすぎて、影の縁が硬くなる"
    **しきい値を段階的に調整**。**EVSM・MSM への切り替えも検討**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **光漏れ ＝ VSM の欠点**。**多重の影で、影が薄くなりすぎる**
    - [x] **簡単な対策はしきい値、本格的には EVSM・MSM**

## 参考

- Eisemann et al., "Real-Time Shadows"（CRC Press 2011）
- Microsoft, "Common Techniques to Improve Shadow Depth Maps"（Microsoft Learn）

## 関連ページ

- [VSM, ESM and MSM](index.md)
- [EVSM](evsm.md)
- [MSM](msm.md)
