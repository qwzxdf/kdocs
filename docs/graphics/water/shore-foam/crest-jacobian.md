---
title: Crest Foam: The Jacobian
tags:
  - 描画
---

# Crest Foam: The Jacobian

<strong>波頭が尖って、メッシュが縮む所に、泡が出る</strong>のが<strong>自然な波</strong>です。この縮み具合を、ヤコビアンという値で測れます。このページでは、ヤコビアンによる波頂の泡を説明します。

!!! tip "ポイント"
    - ヤコビアン ＝ 水面の面積の変化率。
    - 値が小さい（縮む）所に、泡が出る。
    - Gerstner 波・FFT で、計算できる。
    - しきい値を決めて、泡のマスクにする。

## 波頂の泡：ヤコビアン
<strong>波が尖りすぎると頂が折れて砕けます</strong>。<strong>折れる所は水平変位の面積が潰れる所</strong>で、<strong>ヤコビアン（変位の面積比）</strong>で検出できます。

<strong>水面の位置を `P = P₀ + D(P₀)`（`D` は水平変位）</strong>とすると<strong>面積の変化率</strong>は<strong>次の行列式</strong>です。

<div class="formula">J = (1 + ∂Dx/∂x)(1 + ∂Dz/∂z) − (∂Dx/∂z)(∂Dz/∂x)</div>

| 値 | 意味 |
| --- | --- |
| J = 1 | 面積が変わらない（平らな水面） |
| J > 1 | 広がっている（谷） |
| J < 1 | 縮んでいる（波頂に向かって粒子が集まる） |
| J ≤ 0 | 折れている（粒子が追い越した）。泡が出る |

<strong>Gerstner 波なら、解析的に求まります</strong>。

```hlsl
float3 GerstnerJacobian(float2 position, GerstnerWave wave, float time) {
  float k = 2.0 * 3.14159265 / wave.wavelength;
  float phase = k * dot(wave.direction, position) + time * wave.speed * k;
  float s = sin(phase) * wave.steepness;
  return float3(wave.direction.x * wave.direction.x * s,
                wave.direction.y * wave.direction.y * s,
                wave.direction.x * wave.direction.y * s);
}

float jacobian = 1.0;
float3 sum = float3(0, 0, 0);
for (int i = 0; i < kWaveCount; ++i) {
  sum += GerstnerJacobian(position, waves[i], time);
}
jacobian = (1.0 - sum.x) * (1.0 - sum.y) - sum.z * sum.z;

float crest_mask = saturate((foam_threshold - jacobian) / foam_softness);
```

コードの要点です。`foam_threshold` は、この値より J が小さいと泡になるしきい値で（例：0.7）、1 より小さい値にします。`foam_softness` は泡が立ち上がる幅（例：0.3）です。FFT 海面では、ヤコビアンを変位マップから計算して、テクスチャに出します（[Water Waves](../waves/index.md)）。

この方法は、Tessendorf の "Simulating Ocean Water"（SIGGRAPH Course Notes、2001）で提案されたもので、波の水平方向の変位（Gerstner 波の尖り）から、波が折れる場所を判定します。

<strong>FFT では水平変位マップの差分</strong>から<strong>ヤコビアンを求め</strong>、別のテクスチャに書き出すのが定番です。

<!-- fig:jacobian-fold:begin -->

<svg class="fig illust motion" data-fig="jacobian-fold" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-jacobian-fold" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">ヤコビアン: 水面が詰まって、折り返す所(J が小さい所)に泡を出す</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">3 つの波を足した、横にも動く水面。尖り具合 λ を上げると、折り返す所が増える</text>
<rect x="30" y="96" width="900" height="220" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 水面の形(赤い点 = J が 0.25 より小さい = 泡)</text>
<line x1="40" y1="236.0" x2="920" y2="236.0" stroke="#e2e8f0" stroke-width="1.5" stroke-dasharray="5 5"/>
<path d="M60.0,198.68 L65.0,201.9 L70.0,204.98 L75.0,207.92 L80.0,210.69 L85.0,213.28 L90.0,215.65 L95.0,217.82 L100.0,219.76 L105.0,221.48 L110.0,222.97 L115.0,224.23 L120.0,225.28 L125.0,226.12 L130.0,226.76 L135.0,227.22 L140.0,227.51 L145.0,227.65 L150.0,227.67 L155.0,227.58 L160.0,227.41 L165.0,227.18 L170.0,226.9 L175.0,226.62 L180.0,226.34 L185.0,226.08 L190.0,225.88 L195.0,225.74 L200.0,225.69 L205.0,225.73 L210.0,225.88 L215.0,226.16 L220.0,226.56 L225.0,227.09 L230.0,227.76 L235.0,228.56 L240.0,229.49 L245.0,230.54 L250.0,231.72 L255.0,233.0 L260.0,234.38 L265.0,235.84 L270.0,237.36 L275.0,238.94 L280.0,240.54 L285.0,242.16 L290.0,243.78 L295.0,245.38 L300.0,246.93 L305.0,248.43 L310.0,249.86 L315.0,251.19 L320.0,252.43 L325.0,253.55 L330.0,254.55 L335.0,255.42 L340.0,256.16 L345.0,256.76 L350.0,257.22 L355.0,257.54 L360.0,257.74 L365.0,257.82 L370.0,257.79 L375.0,257.65 L380.0,257.44 L385.0,257.15 L390.0,256.81 L395.0,256.44 L400.0,256.07 L405.0,255.7 L410.0,255.36 L415.0,255.08 L420.0,254.86 L425.0,254.75 L430.0,254.74 L435.0,254.87 L440.0,255.15 L445.0,255.58 L450.0,256.19 L455.0,256.98 L460.0,257.96 L465.0,259.14 L470.0,260.5 L475.0,262.06 L480.0,263.79 L485.0,265.7 L490.0,267.77 L495.0,269.99 L500.0,272.33 L505.0,274.77 L510.0,277.29 L515.0,279.85 L520.0,282.44 L525.0,285.02 L530.0,287.55 L535.0,290.01 L540.0,292.35 L545.0,294.54 L550.0,296.55 L555.0,298.35 L560.0,299.9 L565.0,301.17 L570.0,302.13 L575.0,302.75 L580.0,303.01 L585.0,302.89 L590.0,302.37 L595.0,301.44 L600.0,300.08 L605.0,298.3 L610.0,296.08 L615.0,293.44 L620.0,290.37 L625.0,286.9 L630.0,283.03 L635.0,278.79 L640.0,274.21 L645.0,269.3 L650.0,264.1 L655.0,258.65 L660.0,252.98 L665.0,247.13 L670.0,241.15 L675.0,235.08 L680.0,228.97 L685.0,222.86 L690.0,216.79 L695.0,210.82 L700.0,204.98 L705.0,199.32 L710.0,193.89 L715.0,188.72 L720.0,183.85 L725.0,179.31 L730.0,175.14 L735.0,171.36 L740.0,167.99 L745.0,165.05 L750.0,162.56 L755.0,160.52 L760.0,158.95 L765.0,157.84 L770.0,157.18 L775.0,156.98 L780.0,157.22 L785.0,157.88 L790.0,158.94 L795.0,160.37 L800.0,162.16 L805.0,164.27 L810.0,166.67 L815.0,169.33 L820.0,172.2 L825.0,175.26 L830.0,178.47 L835.0,181.78 L840.0,185.16 L845.0,188.58 L850.0,191.99 L855.0,195.37 L860.0,198.68" fill="none" stroke="#2563eb" stroke-width="3.5"><animate attributeName="d" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0444;0.2489;0.4533;0.6578" values="M60.0,198.68 L65.0,201.9 L70.0,204.98 L75.0,207.92 L80.0,210.69 L85.0,213.28 L90.0,215.65 L95.0,217.82 L100.0,219.76 L105.0,221.48 L110.0,222.97 L115.0,224.23 L120.0,225.28 L125.0,226.12 L130.0,226.76 L135.0,227.22 L140.0,227.51 L145.0,227.65 L150.0,227.67 L155.0,227.58 L160.0,227.41 L165.0,227.18 L170.0,226.9 L175.0,226.62 L180.0,226.34 L185.0,226.08 L190.0,225.88 L195.0,225.74 L200.0,225.69 L205.0,225.73 L210.0,225.88 L215.0,226.16 L220.0,226.56 L225.0,227.09 L230.0,227.76 L235.0,228.56 L240.0,229.49 L245.0,230.54 L250.0,231.72 L255.0,233.0 L260.0,234.38 L265.0,235.84 L270.0,237.36 L275.0,238.94 L280.0,240.54 L285.0,242.16 L290.0,243.78 L295.0,245.38 L300.0,246.93 L305.0,248.43 L310.0,249.86 L315.0,251.19 L320.0,252.43 L325.0,253.55 L330.0,254.55 L335.0,255.42 L340.0,256.16 L345.0,256.76 L350.0,257.22 L355.0,257.54 L360.0,257.74 L365.0,257.82 L370.0,257.79 L375.0,257.65 L380.0,257.44 L385.0,257.15 L390.0,256.81 L395.0,256.44 L400.0,256.07 L405.0,255.7 L410.0,255.36 L415.0,255.08 L420.0,254.86 L425.0,254.75 L430.0,254.74 L435.0,254.87 L440.0,255.15 L445.0,255.58 L450.0,256.19 L455.0,256.98 L460.0,257.96 L465.0,259.14 L470.0,260.5 L475.0,262.06 L480.0,263.79 L485.0,265.7 L490.0,267.77 L495.0,269.99 L500.0,272.33 L505.0,274.77 L510.0,277.29 L515.0,279.85 L520.0,282.44 L525.0,285.02 L530.0,287.55 L535.0,290.01 L540.0,292.35 L545.0,294.54 L550.0,296.55 L555.0,298.35 L560.0,299.9 L565.0,301.17 L570.0,302.13 L575.0,302.75 L580.0,303.01 L585.0,302.89 L590.0,302.37 L595.0,301.44 L600.0,300.08 L605.0,298.3 L610.0,296.08 L615.0,293.44 L620.0,290.37 L625.0,286.9 L630.0,283.03 L635.0,278.79 L640.0,274.21 L645.0,269.3 L650.0,264.1 L655.0,258.65 L660.0,252.98 L665.0,247.13 L670.0,241.15 L675.0,235.08 L680.0,228.97 L685.0,222.86 L690.0,216.79 L695.0,210.82 L700.0,204.98 L705.0,199.32 L710.0,193.89 L715.0,188.72 L720.0,183.85 L725.0,179.31 L730.0,175.14 L735.0,171.36 L740.0,167.99 L745.0,165.05 L750.0,162.56 L755.0,160.52 L760.0,158.95 L765.0,157.84 L770.0,157.18 L775.0,156.98 L780.0,157.22 L785.0,157.88 L790.0,158.94 L795.0,160.37 L800.0,162.16 L805.0,164.27 L810.0,166.67 L815.0,169.33 L820.0,172.2 L825.0,175.26 L830.0,178.47 L835.0,181.78 L840.0,185.16 L845.0,188.58 L850.0,191.99 L855.0,195.37 L860.0,198.68;M60.0,198.68 L65.0,201.9 L70.0,204.98 L75.0,207.92 L80.0,210.69 L85.0,213.28 L90.0,215.65 L95.0,217.82 L100.0,219.76 L105.0,221.48 L110.0,222.97 L115.0,224.23 L120.0,225.28 L125.0,226.12 L130.0,226.76 L135.0,227.22 L140.0,227.51 L145.0,227.65 L150.0,227.67 L155.0,227.58 L160.0,227.41 L165.0,227.18 L170.0,226.9 L175.0,226.62 L180.0,226.34 L185.0,226.08 L190.0,225.88 L195.0,225.74 L200.0,225.69 L205.0,225.73 L210.0,225.88 L215.0,226.16 L220.0,226.56 L225.0,227.09 L230.0,227.76 L235.0,228.56 L240.0,229.49 L245.0,230.54 L250.0,231.72 L255.0,233.0 L260.0,234.38 L265.0,235.84 L270.0,237.36 L275.0,238.94 L280.0,240.54 L285.0,242.16 L290.0,243.78 L295.0,245.38 L300.0,246.93 L305.0,248.43 L310.0,249.86 L315.0,251.19 L320.0,252.43 L325.0,253.55 L330.0,254.55 L335.0,255.42 L340.0,256.16 L345.0,256.76 L350.0,257.22 L355.0,257.54 L360.0,257.74 L365.0,257.82 L370.0,257.79 L375.0,257.65 L380.0,257.44 L385.0,257.15 L390.0,256.81 L395.0,256.44 L400.0,256.07 L405.0,255.7 L410.0,255.36 L415.0,255.08 L420.0,254.86 L425.0,254.75 L430.0,254.74 L435.0,254.87 L440.0,255.15 L445.0,255.58 L450.0,256.19 L455.0,256.98 L460.0,257.96 L465.0,259.14 L470.0,260.5 L475.0,262.06 L480.0,263.79 L485.0,265.7 L490.0,267.77 L495.0,269.99 L500.0,272.33 L505.0,274.77 L510.0,277.29 L515.0,279.85 L520.0,282.44 L525.0,285.02 L530.0,287.55 L535.0,290.01 L540.0,292.35 L545.0,294.54 L550.0,296.55 L555.0,298.35 L560.0,299.9 L565.0,301.17 L570.0,302.13 L575.0,302.75 L580.0,303.01 L585.0,302.89 L590.0,302.37 L595.0,301.44 L600.0,300.08 L605.0,298.3 L610.0,296.08 L615.0,293.44 L620.0,290.37 L625.0,286.9 L630.0,283.03 L635.0,278.79 L640.0,274.21 L645.0,269.3 L650.0,264.1 L655.0,258.65 L660.0,252.98 L665.0,247.13 L670.0,241.15 L675.0,235.08 L680.0,228.97 L685.0,222.86 L690.0,216.79 L695.0,210.82 L700.0,204.98 L705.0,199.32 L710.0,193.89 L715.0,188.72 L720.0,183.85 L725.0,179.31 L730.0,175.14 L735.0,171.36 L740.0,167.99 L745.0,165.05 L750.0,162.56 L755.0,160.52 L760.0,158.95 L765.0,157.84 L770.0,157.18 L775.0,156.98 L780.0,157.22 L785.0,157.88 L790.0,158.94 L795.0,160.37 L800.0,162.16 L805.0,164.27 L810.0,166.67 L815.0,169.33 L820.0,172.2 L825.0,175.26 L830.0,178.47 L835.0,181.78 L840.0,185.16 L845.0,188.58 L850.0,191.99 L855.0,195.37 L860.0,198.68;M46.48,198.68 L51.33,201.9 L56.29,204.98 L61.33,207.92 L66.46,210.69 L71.67,213.28 L76.94,215.65 L82.27,217.82 L87.64,219.76 L93.04,221.48 L98.47,222.97 L103.91,224.23 L109.34,225.28 L114.77,226.12 L120.19,226.76 L125.58,227.22 L130.93,227.51 L136.25,227.65 L141.53,227.67 L146.75,227.58 L151.93,227.41 L157.05,227.18 L162.12,226.9 L167.13,226.62 L172.09,226.34 L177.0,226.08 L181.86,225.88 L186.67,225.74 L191.45,225.69 L196.19,225.73 L200.9,225.88 L205.59,226.16 L210.27,226.56 L214.94,227.09 L219.6,227.76 L224.28,228.56 L228.96,229.49 L233.67,230.54 L238.4,231.72 L243.16,233.0 L247.96,234.38 L252.8,235.84 L257.69,237.36 L262.62,238.94 L267.61,240.54 L272.65,242.16 L277.74,243.78 L282.88,245.38 L288.07,246.93 L293.31,248.43 L298.59,249.86 L303.91,251.19 L309.27,252.43 L314.66,253.55 L320.08,254.55 L325.51,255.42 L330.96,256.16 L336.41,256.76 L341.86,257.22 L347.31,257.54 L352.73,257.74 L358.14,257.82 L363.52,257.79 L368.87,257.65 L374.17,257.44 L379.44,257.15 L384.66,256.81 L389.83,256.44 L394.95,256.07 L400.02,255.7 L405.04,255.36 L410.02,255.08 L414.94,254.86 L419.82,254.75 L424.67,254.74 L429.48,254.87 L434.26,255.15 L439.03,255.58 L443.78,256.19 L448.53,256.98 L453.28,257.96 L458.06,259.14 L462.85,260.5 L467.68,262.06 L472.55,263.79 L477.48,265.7 L482.48,267.77 L487.54,269.99 L492.69,272.33 L497.92,274.77 L503.25,277.29 L508.68,279.85 L514.22,282.44 L519.86,285.02 L525.62,287.55 L531.49,290.01 L537.47,292.35 L543.56,294.54 L549.76,296.55 L556.06,298.35 L562.45,299.9 L568.94,301.17 L575.5,302.13 L582.13,302.75 L588.82,303.01 L595.56,302.89 L602.32,302.37 L609.11,301.44 L615.9,300.08 L622.68,298.3 L629.43,296.08 L636.14,293.44 L642.8,290.37 L649.38,286.9 L655.87,283.03 L662.27,278.79 L668.55,274.21 L674.7,269.3 L680.71,264.1 L686.57,258.65 L692.27,252.98 L697.81,247.13 L703.17,241.15 L708.36,235.08 L713.37,228.97 L718.2,222.86 L722.84,216.79 L727.31,210.82 L731.61,204.98 L735.73,199.32 L739.69,193.89 L743.5,188.72 L747.17,183.85 L750.7,179.31 L754.11,175.14 L757.42,171.36 L760.63,167.99 L763.77,165.05 L766.85,162.56 L769.88,160.52 L772.88,158.95 L775.87,157.84 L778.86,157.18 L781.87,156.98 L784.92,157.22 L788.01,157.88 L791.16,158.94 L794.39,160.37 L797.7,162.16 L801.11,164.27 L804.62,166.67 L808.24,169.33 L811.99,172.2 L815.86,175.26 L819.85,178.47 L823.98,181.78 L828.23,185.16 L832.61,188.58 L837.11,191.99 L841.74,195.37 L846.48,198.68;M32.96,198.68 L37.66,201.9 L42.57,204.98 L47.67,207.92 L52.93,210.69 L58.34,213.28 L63.89,215.65 L69.54,217.82 L75.28,219.76 L81.09,221.48 L86.94,222.97 L92.81,224.23 L98.69,225.28 L104.55,226.12 L110.38,226.76 L116.15,227.22 L121.87,227.51 L127.5,227.65 L133.05,227.67 L138.51,227.58 L143.86,227.41 L149.1,227.18 L154.24,226.9 L159.26,226.62 L164.18,226.34 L169.0,226.08 L173.72,225.88 L178.35,225.74 L182.9,225.69 L187.38,225.73 L191.81,225.88 L196.19,226.16 L200.54,226.56 L204.88,227.09 L209.21,227.76 L213.55,228.56 L217.93,229.49 L222.34,230.54 L226.8,231.72 L231.32,233.0 L235.92,234.38 L240.61,235.84 L245.38,237.36 L250.25,238.94 L255.22,240.54 L260.29,242.16 L265.47,243.78 L270.75,245.38 L276.13,246.93 L281.61,248.43 L287.18,249.86 L292.82,251.19 L298.54,252.43 L304.33,253.55 L310.16,254.55 L316.03,255.42 L321.92,256.16 L327.83,256.76 L333.73,257.22 L339.61,257.54 L345.47,257.74 L351.28,257.82 L357.04,257.79 L362.73,257.65 L368.35,257.44 L373.88,257.15 L379.32,256.81 L384.66,256.44 L389.91,256.07 L395.05,255.7 L400.09,255.36 L405.03,255.08 L409.88,254.86 L414.65,254.75 L419.34,254.74 L423.96,254.87 L428.53,255.15 L433.06,255.58 L437.56,256.19 L442.06,256.98 L446.57,257.96 L451.11,259.14 L455.7,260.5 L460.36,262.06 L465.11,263.79 L469.97,265.7 L474.95,267.77 L480.08,269.99 L485.37,272.33 L490.84,274.77 L496.5,277.29 L502.36,279.85 L508.44,282.44 L514.73,285.02 L521.24,287.55 L527.98,290.01 L534.94,292.35 L542.12,294.54 L549.52,296.55 L557.12,298.35 L564.91,299.9 L572.87,301.17 L581.0,302.13 L589.26,302.75 L597.64,303.01 L606.11,302.89 L614.65,302.37 L623.22,301.44 L631.8,300.08 L640.36,298.3 L648.87,296.08 L657.29,293.44 L665.6,290.37 L673.76,286.9 L681.75,283.03 L689.53,278.79 L697.09,274.21 L704.39,269.3 L711.42,264.1 L718.14,258.65 L724.55,252.98 L730.62,247.13 L736.35,241.15 L741.73,235.08 L746.74,228.97 L751.4,222.86 L755.69,216.79 L759.62,210.82 L763.21,204.98 L766.46,199.32 L769.38,193.89 L772.0,188.72 L774.33,183.85 L776.4,179.31 L778.22,175.14 L779.84,171.36 L781.27,167.99 L782.55,165.05 L783.7,162.56 L784.76,160.52 L785.77,158.95 L786.74,157.84 L787.73,157.18 L788.75,156.98 L789.83,157.22 L791.01,157.88 L792.32,158.94 L793.77,160.37 L795.4,162.16 L797.21,164.27 L799.24,166.67 L801.49,169.33 L803.98,172.2 L806.71,175.26 L809.7,178.47 L812.95,181.78 L816.46,185.16 L820.22,188.58 L824.23,191.99 L828.48,195.37 L832.96,198.68;M19.44,198.68 L24.0,201.9 L28.86,204.98 L34.0,207.92 L39.39,210.69 L45.02,213.28 L50.83,215.65 L56.81,217.82 L62.92,219.76 L69.13,221.48 L75.41,222.97 L81.72,224.23 L88.03,225.28 L94.32,226.12 L100.56,226.76 L106.73,227.22 L112.8,227.51 L118.76,227.65 L124.58,227.67 L130.26,227.58 L135.79,227.41 L141.15,227.18 L146.35,226.9 L151.39,226.62 L156.27,226.34 L160.99,226.08 L165.57,225.88 L170.02,225.74 L174.35,225.69 L178.57,225.73 L182.71,225.88 L186.78,226.16 L190.81,226.56 L194.81,227.09 L198.81,227.76 L202.83,228.56 L206.89,229.49 L211.0,230.54 L215.2,231.72 L219.49,233.0 L223.89,234.38 L228.41,235.84 L233.07,237.36 L237.87,238.94 L242.83,240.54 L247.94,242.16 L253.21,243.78 L258.63,245.38 L264.2,246.93 L269.92,248.43 L275.77,249.86 L281.74,251.19 L287.82,252.43 L293.99,253.55 L300.24,254.55 L306.54,255.42 L312.88,256.16 L319.24,256.76 L325.59,257.22 L331.92,257.54 L338.2,257.74 L344.42,257.82 L350.56,257.79 L356.6,257.65 L362.52,257.44 L368.32,257.15 L373.98,256.81 L379.49,256.44 L384.86,256.07 L390.07,255.7 L395.13,255.36 L400.05,255.08 L404.83,254.86 L409.47,254.75 L414.01,254.74 L418.44,254.87 L422.79,255.15 L427.08,255.58 L431.34,256.19 L435.59,256.98 L439.85,257.96 L444.17,259.14 L448.55,260.5 L453.04,262.06 L457.66,263.79 L462.45,265.7 L467.43,267.77 L472.62,269.99 L478.06,272.33 L483.76,274.77 L489.75,277.29 L496.05,279.85 L502.65,282.44 L509.59,285.02 L516.86,287.55 L524.47,290.01 L532.41,292.35 L540.69,294.54 L549.28,296.55 L558.18,298.35 L567.36,299.9 L576.81,301.17 L586.5,302.13 L596.39,302.75 L606.46,303.01 L616.67,302.89 L626.97,302.37 L637.33,301.44 L647.7,300.08 L658.04,298.3 L668.3,296.08 L678.43,293.44 L688.39,290.37 L698.14,286.9 L707.62,283.03 L716.8,278.79 L725.64,274.21 L734.09,269.3 L742.12,264.1 L749.71,258.65 L756.82,252.98 L763.43,247.13 L769.52,241.15 L775.09,235.08 L780.11,228.97 L784.59,222.86 L788.53,216.79 L791.94,210.82 L794.82,204.98 L797.19,199.32 L799.08,193.89 L800.5,188.72 L801.5,183.85 L802.1,179.31 L802.34,175.14 L802.26,171.36 L801.9,167.99 L801.32,165.05 L800.55,162.56 L799.64,160.52 L798.65,158.95 L797.61,157.84 L796.59,157.18 L795.62,156.98 L794.75,157.22 L794.02,157.88 L793.48,158.94 L793.16,160.37 L793.09,162.16 L793.32,164.27 L793.86,166.67 L794.73,169.33 L795.97,172.2 L797.57,175.26 L799.56,178.47 L801.93,181.78 L804.68,185.16 L807.82,188.58 L811.34,191.99 L815.22,195.37 L819.44,198.68"/></path>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2487;0.2489;1.0000" values="1;1;0;0"/><text x="60" y="352" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed">λ = 0.0</text>
<text x="60" y="382" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043">J が 0.25 より小さい点: 0 / 161 個</text>
<rect x="60.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="70.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="80.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="90.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="100.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="110.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="120.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="130.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="140.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="150.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="160.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="170.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="180.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="190.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="200.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="210.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="220.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="230.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="240.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="250.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="260.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="270.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="280.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="290.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="300.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="310.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="320.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="330.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="340.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="350.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="360.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="370.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="380.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="390.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="400.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="410.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="420.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="430.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="440.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="450.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="460.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="470.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="480.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="490.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="500.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="510.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="520.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="530.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="540.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="550.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="560.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="570.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="580.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="590.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="600.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="610.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="620.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="630.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="640.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="650.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="660.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="670.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="680.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="690.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="700.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="710.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="720.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="730.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="740.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="750.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="760.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="770.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="780.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="790.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="800.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="810.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="820.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="830.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="840.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="850.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0533" values="#e5e7eb;#94d9f8"/></rect>
<rect x="60" y="410" width="800.0" height="10.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60" y="404" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">J の帯(赤 = 泡)</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2487;0.2489;0.4532;0.4533;1.0000" values="0;0;1;1;0;0"/><text x="60" y="352" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed">λ = 0.6</text>
<text x="60" y="382" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043">J が 0.25 より小さい点: 0 / 161 個</text>
<rect x="60.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#98daf9"/></rect>
<rect x="70.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#94d9f8"/></rect>
<rect x="80.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#91d8f8"/></rect>
<rect x="90.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#8fd7f8"/></rect>
<rect x="100.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#8dd7f8"/></rect>
<rect x="110.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#8cd7f8"/></rect>
<rect x="120.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#8cd7f8"/></rect>
<rect x="130.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#8dd7f8"/></rect>
<rect x="140.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#8ed7f8"/></rect>
<rect x="150.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#90d8f8"/></rect>
<rect x="160.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#92d8f8"/></rect>
<rect x="170.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#94d9f8"/></rect>
<rect x="180.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#96d9f9"/></rect>
<rect x="190.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#98daf9"/></rect>
<rect x="200.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#99daf9"/></rect>
<rect x="210.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#9adbf9"/></rect>
<rect x="220.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#9bdbf9"/></rect>
<rect x="230.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#9bdbf9"/></rect>
<rect x="240.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#9adbf9"/></rect>
<rect x="250.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#99daf9"/></rect>
<rect x="260.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#98daf9"/></rect>
<rect x="270.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#96daf9"/></rect>
<rect x="280.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#94d9f8"/></rect>
<rect x="290.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#92d8f8"/></rect>
<rect x="300.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#91d8f8"/></rect>
<rect x="310.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#8fd7f8"/></rect>
<rect x="320.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#8ed7f8"/></rect>
<rect x="330.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#8dd7f8"/></rect>
<rect x="340.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#8cd6f8"/></rect>
<rect x="350.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#8cd6f8"/></rect>
<rect x="360.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#8dd7f8"/></rect>
<rect x="370.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#8ed7f8"/></rect>
<rect x="380.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#8fd7f8"/></rect>
<rect x="390.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#91d8f8"/></rect>
<rect x="400.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#93d8f8"/></rect>
<rect x="410.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#95d9f9"/></rect>
<rect x="420.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#96daf9"/></rect>
<rect x="430.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#98daf9"/></rect>
<rect x="440.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#99daf9"/></rect>
<rect x="450.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#99daf9"/></rect>
<rect x="460.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#99daf9"/></rect>
<rect x="470.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#98daf9"/></rect>
<rect x="480.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#96daf9"/></rect>
<rect x="490.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#94d9f8"/></rect>
<rect x="500.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#91d8f8"/></rect>
<rect x="510.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#8dd7f8"/></rect>
<rect x="520.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#8ad6f8"/></rect>
<rect x="530.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#85d4f8"/></rect>
<rect x="540.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#81d3f8"/></rect>
<rect x="550.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#7dd2f8"/></rect>
<rect x="560.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#7ad1f8"/></rect>
<rect x="570.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#77d0f8"/></rect>
<rect x="580.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#75cff8"/></rect>
<rect x="590.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#74cff8"/></rect>
<rect x="600.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#73cff8"/></rect>
<rect x="610.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#74cff8"/></rect>
<rect x="620.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#77d0f8"/></rect>
<rect x="630.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#7ad1f8"/></rect>
<rect x="640.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#7ed2f8"/></rect>
<rect x="650.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#83d4f8"/></rect>
<rect x="660.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#89d6f8"/></rect>
<rect x="670.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#8fd7f8"/></rect>
<rect x="680.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#96d9f9"/></rect>
<rect x="690.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#9ddbf9"/></rect>
<rect x="700.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#a3ddf9"/></rect>
<rect x="710.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#a9dff9"/></rect>
<rect x="720.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#aee1f9"/></rect>
<rect x="730.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#b3e2f9"/></rect>
<rect x="740.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#b6e3f9"/></rect>
<rect x="750.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#b9e4f9"/></rect>
<rect x="760.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#bae4f9"/></rect>
<rect x="770.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#bae4f9"/></rect>
<rect x="780.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#b8e4f9"/></rect>
<rect x="790.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#b6e3f9"/></rect>
<rect x="800.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#b3e2f9"/></rect>
<rect x="810.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#afe1f9"/></rect>
<rect x="820.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#abe0f9"/></rect>
<rect x="830.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#a6def9"/></rect>
<rect x="840.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#a1ddf9"/></rect>
<rect x="850.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#9ddbf9"/></rect>
<rect x="60" y="410" width="800.0" height="10.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60" y="404" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">J の帯(赤 = 泡)</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4532;0.4533;0.6576;0.6578;1.0000" values="0;0;1;1;0;0"/><circle cx="782.55" cy="165.05" r="4" fill="#e5484d"/>
<circle cx="783.7" cy="162.56" r="4" fill="#e5484d"/>
<circle cx="784.76" cy="160.52" r="4" fill="#e5484d"/>
<circle cx="785.77" cy="158.95" r="4" fill="#e5484d"/>
<circle cx="786.74" cy="157.84" r="4" fill="#e5484d"/>
<circle cx="787.73" cy="157.18" r="4" fill="#e5484d"/>
<circle cx="788.75" cy="156.98" r="4" fill="#e5484d"/>
<circle cx="789.83" cy="157.22" r="4" fill="#e5484d"/>
<circle cx="791.01" cy="157.88" r="4" fill="#e5484d"/>
<text x="60" y="352" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed">λ = 1.2</text>
<text x="60" y="382" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d">J が 0.25 より小さい点: 9 / 161 個</text>
<rect x="60.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#9cdbf9"/></rect>
<rect x="70.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#94d9f8"/></rect>
<rect x="80.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#8ed7f8"/></rect>
<rect x="90.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#89d6f8"/></rect>
<rect x="100.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#86d5f8"/></rect>
<rect x="110.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#84d4f8"/></rect>
<rect x="120.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#84d4f8"/></rect>
<rect x="130.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#86d4f8"/></rect>
<rect x="140.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#88d5f8"/></rect>
<rect x="150.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#8bd6f8"/></rect>
<rect x="160.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#8fd7f8"/></rect>
<rect x="170.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#93d9f8"/></rect>
<rect x="180.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#97daf9"/></rect>
<rect x="190.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#9bdbf9"/></rect>
<rect x="200.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#9ddcf9"/></rect>
<rect x="210.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#a0dcf9"/></rect>
<rect x="220.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#a1ddf9"/></rect>
<rect x="230.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#a1ddf9"/></rect>
<rect x="240.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#a0dcf9"/></rect>
<rect x="250.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#9edcf9"/></rect>
<rect x="260.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#9bdbf9"/></rect>
<rect x="270.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#98daf9"/></rect>
<rect x="280.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#94d9f8"/></rect>
<rect x="290.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#90d8f8"/></rect>
<rect x="300.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#8dd7f8"/></rect>
<rect x="310.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#89d6f8"/></rect>
<rect x="320.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#87d5f8"/></rect>
<rect x="330.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#85d4f8"/></rect>
<rect x="340.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#84d4f8"/></rect>
<rect x="350.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#84d4f8"/></rect>
<rect x="360.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#85d4f8"/></rect>
<rect x="370.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#87d5f8"/></rect>
<rect x="380.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#8ad6f8"/></rect>
<rect x="390.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#8dd7f8"/></rect>
<rect x="400.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#91d8f8"/></rect>
<rect x="410.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#95d9f9"/></rect>
<rect x="420.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#98daf9"/></rect>
<rect x="430.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#9bdbf9"/></rect>
<rect x="440.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#9ddcf9"/></rect>
<rect x="450.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#9edcf9"/></rect>
<rect x="460.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#9ddcf9"/></rect>
<rect x="470.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#9bdbf9"/></rect>
<rect x="480.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#98daf9"/></rect>
<rect x="490.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#93d9f8"/></rect>
<rect x="500.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#8ed7f8"/></rect>
<rect x="510.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#86d5f8"/></rect>
<rect x="520.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#7fd2f8"/></rect>
<rect x="530.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#76d0f8"/></rect>
<rect x="540.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#6ecdf8"/></rect>
<rect x="550.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#66cbf8"/></rect>
<rect x="560.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#5fc9f8"/></rect>
<rect x="570.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#59c7f8"/></rect>
<rect x="580.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#55c6f8"/></rect>
<rect x="590.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#53c5f8"/></rect>
<rect x="600.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#52c5f8"/></rect>
<rect x="610.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#54c6f8"/></rect>
<rect x="620.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#59c7f8"/></rect>
<rect x="630.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#5fc9f8"/></rect>
<rect x="640.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#67cbf8"/></rect>
<rect x="650.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#72cef8"/></rect>
<rect x="660.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#7ed2f8"/></rect>
<rect x="670.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#8ad6f8"/></rect>
<rect x="680.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#98daf9"/></rect>
<rect x="690.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#a5def9"/></rect>
<rect x="700.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#b2e2f9"/></rect>
<rect x="710.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#bee5f9"/></rect>
<rect x="720.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#c8e9f9"/></rect>
<rect x="730.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#d1ebf9"/></rect>
<rect x="740.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#d8edf9"/></rect>
<rect x="750.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#fca5a5"/></rect>
<rect x="760.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#fca5a5"/></rect>
<rect x="770.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#fca5a5"/></rect>
<rect x="780.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#fca5a5"/></rect>
<rect x="790.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#d8edf9"/></rect>
<rect x="800.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#d1ebf9"/></rect>
<rect x="810.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#c9e9f9"/></rect>
<rect x="820.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#c1e6f9"/></rect>
<rect x="830.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#b7e4f9"/></rect>
<rect x="840.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#aee1f9"/></rect>
<rect x="850.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#a5def9"/></rect>
<rect x="60" y="410" width="800.0" height="10.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60" y="404" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">J の帯(赤 = 泡)</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6576;0.6578;1.0000" values="0;0;1;1"/><circle cx="800.5" cy="188.72" r="4" fill="#e5484d"/>
<circle cx="801.5" cy="183.85" r="4" fill="#e5484d"/>
<circle cx="802.1" cy="179.31" r="4" fill="#e5484d"/>
<circle cx="802.34" cy="175.14" r="4" fill="#e5484d"/>
<circle cx="802.26" cy="171.36" r="4" fill="#e5484d"/>
<circle cx="801.9" cy="167.99" r="4" fill="#e5484d"/>
<circle cx="801.32" cy="165.05" r="4" fill="#e5484d"/>
<circle cx="800.55" cy="162.56" r="4" fill="#e5484d"/>
<circle cx="799.64" cy="160.52" r="4" fill="#e5484d"/>
<circle cx="798.65" cy="158.95" r="4" fill="#e5484d"/>
<circle cx="797.61" cy="157.84" r="4" fill="#e5484d"/>
<circle cx="796.59" cy="157.18" r="4" fill="#e5484d"/>
<circle cx="795.62" cy="156.98" r="4" fill="#e5484d"/>
<circle cx="794.75" cy="157.22" r="4" fill="#e5484d"/>
<circle cx="794.02" cy="157.88" r="4" fill="#e5484d"/>
<circle cx="793.48" cy="158.94" r="4" fill="#e5484d"/>
<circle cx="793.16" cy="160.37" r="4" fill="#e5484d"/>
<circle cx="793.09" cy="162.16" r="4" fill="#e5484d"/>
<circle cx="793.32" cy="164.27" r="4" fill="#e5484d"/>
<circle cx="793.86" cy="166.67" r="4" fill="#e5484d"/>
<circle cx="794.73" cy="169.33" r="4" fill="#e5484d"/>
<text x="60" y="352" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed">λ = 1.8</text>
<text x="60" y="382" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d">J が 0.25 より小さい点: 21 / 161 個</text>
<rect x="60.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#a0dcf9"/></rect>
<rect x="70.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#94d9f8"/></rect>
<rect x="80.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#8bd6f8"/></rect>
<rect x="90.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#84d4f8"/></rect>
<rect x="100.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#7fd2f8"/></rect>
<rect x="110.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#7cd2f8"/></rect>
<rect x="120.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#7cd2f8"/></rect>
<rect x="130.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#7ed2f8"/></rect>
<rect x="140.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#82d3f8"/></rect>
<rect x="150.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#87d5f8"/></rect>
<rect x="160.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#8cd7f8"/></rect>
<rect x="170.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#92d8f8"/></rect>
<rect x="180.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#98daf9"/></rect>
<rect x="190.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#9edcf9"/></rect>
<rect x="200.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#a2ddf9"/></rect>
<rect x="210.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#a5def9"/></rect>
<rect x="220.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#a7dff9"/></rect>
<rect x="230.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#a7dff9"/></rect>
<rect x="240.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#a5def9"/></rect>
<rect x="250.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#a3ddf9"/></rect>
<rect x="260.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#9fdcf9"/></rect>
<rect x="270.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#99dbf9"/></rect>
<rect x="280.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#94d9f8"/></rect>
<rect x="290.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#8ed7f8"/></rect>
<rect x="300.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#89d5f8"/></rect>
<rect x="310.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#84d4f8"/></rect>
<rect x="320.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#80d3f8"/></rect>
<rect x="330.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#7dd2f8"/></rect>
<rect x="340.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#7bd1f8"/></rect>
<rect x="350.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#7cd1f8"/></rect>
<rect x="360.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#7dd2f8"/></rect>
<rect x="370.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#80d3f8"/></rect>
<rect x="380.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#85d4f8"/></rect>
<rect x="390.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#8ad6f8"/></rect>
<rect x="400.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#8fd7f8"/></rect>
<rect x="410.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#95d9f9"/></rect>
<rect x="420.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#9adbf9"/></rect>
<rect x="430.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#9edcf9"/></rect>
<rect x="440.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#a1ddf9"/></rect>
<rect x="450.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#a2ddf9"/></rect>
<rect x="460.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#a2ddf9"/></rect>
<rect x="470.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#9fdcf9"/></rect>
<rect x="480.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#9adbf9"/></rect>
<rect x="490.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#93d9f8"/></rect>
<rect x="500.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#8ad6f8"/></rect>
<rect x="510.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#7fd3f8"/></rect>
<rect x="520.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#74cff8"/></rect>
<rect x="530.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#67cbf8"/></rect>
<rect x="540.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#5bc8f8"/></rect>
<rect x="550.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#4fc4f8"/></rect>
<rect x="560.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#45c1f8"/></rect>
<rect x="570.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#3cbef8"/></rect>
<rect x="580.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#38bdf8"/></rect>
<rect x="590.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#38bdf8"/></rect>
<rect x="600.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#38bdf8"/></rect>
<rect x="610.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#38bdf8"/></rect>
<rect x="620.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#3bbef8"/></rect>
<rect x="630.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#44c1f8"/></rect>
<rect x="640.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#51c5f8"/></rect>
<rect x="650.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#60c9f8"/></rect>
<rect x="660.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#72cff8"/></rect>
<rect x="670.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#85d4f8"/></rect>
<rect x="680.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#99daf9"/></rect>
<rect x="690.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#ade0f9"/></rect>
<rect x="700.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#c0e6f9"/></rect>
<rect x="710.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#d2ecf9"/></rect>
<rect x="720.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#fca5a5"/></rect>
<rect x="730.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#fca5a5"/></rect>
<rect x="740.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#fca5a5"/></rect>
<rect x="750.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#fca5a5"/></rect>
<rect x="760.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#fca5a5"/></rect>
<rect x="770.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#fca5a5"/></rect>
<rect x="780.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#fca5a5"/></rect>
<rect x="790.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#fca5a5"/></rect>
<rect x="800.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#fca5a5"/></rect>
<rect x="810.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#fca5a5"/></rect>
<rect x="820.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#d7edf9"/></rect>
<rect x="830.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#c9e9f9"/></rect>
<rect x="840.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#bae4f9"/></rect>
<rect x="850.0" y="410.0" width="10.3" height="10.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#ade0f9"/></rect>
<rect x="60" y="410" width="800.0" height="10.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60" y="404" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">J の帯(赤 = 泡)</text>
</g>
<text x="560" y="362" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937">泡の点の数:</text>
<text x="670" y="366" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0532;0.0533;1.0000" values="1;1;0;0"/></text>
<text x="670" y="366" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0532;0.0533;0.2576;0.2578;1.0000" values="0;0;1;1;0;0"/></text>
<text x="670" y="366" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2576;0.2578;0.4620;0.4622;1.0000" values="0;0;1;1;0;0"/></text>
<text x="670" y="366" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">9<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4620;0.4622;0.6665;0.6667;1.0000" values="0;0;1;1;0;0"/></text>
<text x="670" y="366" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">21<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6665;0.6667;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8354;0.8356;1.0000" values="0;0;1;1"/><rect x="560" y="384" width="370" height="120" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="576" y="408" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">J = (横の伸び縮み)× 1 を、数値で調べる</text>
<text x="576" y="431" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">J &lt; 0.25 の所 = 水面が詰まって、折り返す所</text>
<text x="576" y="454" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">→ 泡の濃さを、その場所だけ上げる</text>
<text x="576" y="477" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">λ を上げるほど、泡の出る範囲が広がる</text>
</g>
<text x="30" y="530" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">水面の各点が、横にどれだけ動いたかから、詰まり具合 J を計算する<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0443;0.0444;1.0000" values="1;1;0;0"/></text>
<text x="30" y="530" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">λ を上げて、波頭を尖らせる。J が小さい所に、赤い点(泡)が出る<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0443;0.0444;0.8620;0.8622;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="530" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">泡は、波頭に沿って、自然に出る<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8620;0.8622;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:jacobian-fold:end -->

## 波頭の、泡は、いつ出るか

海の波は、<strong>波頭が、尖り</strong>、さらに強くなると、<strong>波頭が、砕けて、泡</strong>になります。波が、砕けるのは、波の、斜面が、急になりすぎたときです。水の粒が、波頭で、集まりすぎて、ぶつかるとも、言えます。

波の頂点を、水平にも動かす方式（Gerstner 波、FFT 海面）では、<strong>頂点が、集まって、面積が、小さくなった場所</strong>が、砕けそうな場所です。この「<strong>面積の縮み具合</strong>」を、数値にしたものが、ヤコビアンです。

## ヤコビアン

各頂点を、動く前の位置 `P₀ = (x₀, z₀)` から、動いた後の位置 `P = P₀ + D(P₀)` へ、移すとします（`D` は、水平の変位）。この写像が、<strong>面積を、どれだけ変えるか</strong>を表すのが、ヤコビアン `J` です。

```text
J = ( 1 + ∂Dx/∂x )( 1 + ∂Dz/∂z ) − ( ∂Dx/∂z )( ∂Dz/∂x )
```

| J の値 | 意味 |
| --- | --- |
| 1 | 面積が、変わらない（頂点の、間隔が、そのまま） |
| 1 より大きい | 面積が、広がる（谷。頂点が、散る） |
| 0 に近づく | 面積が、つぶれる（波頭。頂点が、集まる） |
| 負 | 写像が、裏返る（頂点が、追い越して、波頭が、折れている） |

<strong>`J` が、小さい（しきい値より、小さい）場所に、泡を出します</strong>。

```hlsl
// ヤコビアンが、しきい値（たとえば 0.5）より小さい場所を、泡にする。
float foam = saturate((foam_threshold - jacobian) / foam_softness);
```

| パラメーター | 目安 | 効果 |
| --- | --- | --- |
| `foam_threshold` | 0.3〜0.8 | 大きいほど、多くの場所に、泡が出る |
| `foam_softness` | 0.1〜0.5 | 大きいほど、泡の縁が、なだらか |

## Gerstner 波の、ヤコビアン

Gerstner 波では、水平変位の偏微分が、<strong>解析的</strong>に、求まります（[Gerstner Waves](../waves/gerstner.md)）。

```text
∂Dx/∂x = −Σ Q A ω Dx² sinθ         ∂Dz/∂z = −Σ Q A ω Dz² sinθ
∂Dx/∂z = −Σ Q A ω Dx Dz sinθ      ∂Dz/∂x = ∂Dx/∂z（対称）
```

```hlsl
// 各波について、足し込む。
float s = sin(theta);
dxdx -= w.steepness * w.amplitude * k * s * w.direction.x * w.direction.x;
dzdz -= w.steepness * w.amplitude * k * s * w.direction.y * w.direction.y;
dxdz -= w.steepness * w.amplitude * k * s * w.direction.x * w.direction.y;
// 最後に:
float jacobian = (1.0 + dxdx) * (1.0 + dzdz) - dxdz * dxdz;
```

## FFT 海面の、ヤコビアン

FFT 海面（[FFT Ocean](../waves/fft-ocean.md)）では、<strong>水平変位の画像 `Dx`、`Dz`</strong> が、テクスチャとして、得られます。その<strong>隣の画素との差</strong>（中央差分）から、偏微分を求めます。

```hlsl
// 変位テクスチャ（xy = Dx, Dz）から、ヤコビアンを求める。
float2 d_right = g_displacement.SampleLevel(g_point_wrap, uv + float2(texel, 0), 0).xz;
float2 d_left  = g_displacement.SampleLevel(g_point_wrap, uv - float2(texel, 0), 0).xz;
float2 d_up    = g_displacement.SampleLevel(g_point_wrap, uv + float2(0, texel), 0).xz;
float2 d_down  = g_displacement.SampleLevel(g_point_wrap, uv - float2(0, texel), 0).xz;

float2 ddx_ = (d_right - d_left) / (2.0 * texel_world);       // (∂Dx/∂x, ∂Dz/∂x)
float2 ddz_ = (d_up - d_down) / (2.0 * texel_world);          // (∂Dx/∂z, ∂Dz/∂z)

float jacobian = (1.0 + ddx_.x) * (1.0 + ddz_.y) - ddz_.x * ddx_.y;
```

`texel_world` は、変位マップの、<strong>1 画素のワールド上の大きさ</strong>（`patch_size / N`）です。

!!! tip "ヤコビアンを、FFT で、直接求める"
    差分は、<strong>ノイズを増やしやすい</strong>です。<strong>周波数空間で、微分を掛けて、逆 FFT する</strong>と、正確に、偏微分が、得られます（`∂/∂x ↔ i kx`）。逆 FFT の、画像の枚数が、増えますが、きれいな泡になります。

## 泡の、ためる・消す

ヤコビアンが、小さい瞬間だけ、泡を出すと、<strong>一瞬で消えて、ちらつきます</strong>。<strong>泡を、ためて、ゆっくり消す</strong>と、波頭が、通り過ぎた後にも、泡が、尾を引いて残ります（[Persistent Foam](foam-history.md)）。

```hlsl
// 泡の蓄積: 新しい泡と、前の泡（減衰させたもの）の、大きい方を取る。
float new_foam = saturate((foam_threshold - jacobian) / foam_softness);
float foam = max(new_foam, prev_foam * exp(-decay_rate * dt));
```

## 泡の、位置の補正

ヤコビアンは、<strong>動く前の位置 `P₀`</strong> の関数です。泡を、<strong>画面の、どこに、出すか</strong>は、動いた後の位置 `P` です。頂点シェーダーで、ヤコビアンを求めて、補間して、ピクセルへ、渡すなら、自動で、合います。テクスチャに焼く場合は、`P₀` の座標に、書かれるので、波頭の位置と、泡が、わずかに、ずれて見えることがあります。変位を、足して、`P` の位置で、読むように、補正します（水平変位は、頂点シェーダーが、すでに、反映しているので、頂点の `P₀` を、UV として、読めばよい）。

## よくあるミス

??? failure "波頭に、泡がまったく出ない"
    <strong>ヤコビアンのしきい値</strong>を<strong>調整</strong>する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 波が尖る所に、泡
    - [x] ヤコビアンで測る

## 参考

- Tessendorf, "Simulating Ocean Water", SIGGRAPH 2001 Course Notes（水平変位と、波頭の折れ）
- Jensen, Golias, "Deep-Water Animation and Rendering", Gamasutra, 2001（海の描画。泡、波頭）
- Fournier, Reeves, "A Simple Model of Ocean Waves", SIGGRAPH 1986

## 関連ページ

- [Shore Foam](index.md)
- [Gerstner Waves](../waves/gerstner.md)
- [FFT Ocean](../waves/fft-ocean.md)
