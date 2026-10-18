---
title: The Underside of the Surface and Crossing It
tags:
  - 描画
---

# The Underside of the Surface and Crossing It

**水中から水面を見上げると、水面は、鏡のように反射する部分と、空が見える部分（スネルの窓）に分かれます**。**カメラが水面をまたぐ時の、見た目の切り替え**にも**注意**が必要です。このページでは、**水面の裏側の見え方と、またぐ処理**を説明します。

!!! tip "ポイント"
    - **水面の裏側は、全反射とスネルの窓**。
    - **水面を描く時、裏面も描く**（カリングを切る）。
    - **カメラが水面をまたぐ瞬間は、画面の半分が水中**になる。
    - **またぐ時は、水面の位置で、画面を上下に分ける**。

<!-- fig:snell-window:begin -->

<svg class="fig illust motion" data-fig="snell-window" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-snell-window" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">水中から見上げる:一定の角度の内側は空、外側は水面が鏡になる</text>
<rect x="40" y="80" width="700" height="110" fill="#e0f2fe" fill-opacity="0.5"/>
<rect x="40" y="190" width="700" height="130" fill="#7dd3fc" fill-opacity="0.35"/>
<line x1="40" y1="190" x2="740" y2="190" stroke="#0284c7" stroke-width="3"/>
<text x="50" y="104" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">空</text>
<circle cx="390" cy="300" r="11" fill="#2563eb" stroke="#ffffff" stroke-width="2"/>
<text x="406" y="305" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2563eb">水中の目</text>
<polygon points="390,300 264.55,190 515.45,190" fill="#e5aa28" fill-opacity="0.12" stroke="#e5aa28" stroke-width="1.5" stroke-dasharray="5 4"/>
<text x="390" y="182" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#e5aa28">スネルの窓（約 49°）</text>
<line x1="390" y1="300" x2="390" y2="190" stroke="#2ea043" stroke-width="3"><animate attributeName="x2" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0667;0.0932;0.1198;0.1464;0.1729;0.1995;0.2260;0.2526;0.2792;0.3057;0.3323;0.3589;0.3854;0.4120;0.4385;0.4651;0.4917;0.5182;0.5448;0.5714;0.5979;0.6245;0.6510;0.6776;0.7042;0.7307;0.7573;0.7839;0.8104;0.8370;0.8635;0.8901;0.9167;1.0000" values="390;390;394.2;398.42;402.65;406.93;411.26;415.65;420.12;424.68;429.36;434.16;439.12;444.25;449.57;455.12;460.92;467.02;473.46;480.27;487.53;495.3;503.66;512.7;522.55;533.35;545.29;558.58;573.52;590.5;610.02;632.78;659.71;692.22;692.22"/></line>
<line x1="390" y1="190" x2="390" y2="100" stroke="#2ea043" stroke-width="3"><animate attributeName="x1" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0667;0.0932;0.1198;0.1464;0.1729;0.1995;0.2260;0.2526;0.2792;0.3057;0.3323;0.3589;0.3854;0.4120;0.4385;0.4651;0.4917;0.5182;0.5448;0.5714;0.5979;0.6245;0.6510;0.6776;0.7042;0.7307;0.7573;0.7839;0.8104;0.8370;0.8635;0.8901;0.9167;1.0000" values="390;390;394.2;398.42;402.65;406.93;411.26;415.65;420.12;424.68;429.36;434.16;439.12;444.25;449.57;455.12;460.92;467.02;473.46;480.27;487.53;495.3;503.66;512.7;522.55;533.35;545.29;558.58;573.52;590.5;610.02;632.78;659.71;692.22;692.22"/><animate attributeName="x2" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0667;0.0932;0.1198;0.1464;0.1729;0.1995;0.2260;0.2526;0.2792;0.3057;0.3323;0.3589;0.3854;0.4120;0.4385;0.4651;0.4917;0.5182;0.5448;0.5714;0.5979;0.6245;0.6510;0.6776;0.7042;0.7307;0.7573;0.7839;0.8104;0.8370;0.8635;0.8901;0.9167;1.0000" values="390;390;398.78;407.59;416.5;425.52;434.73;444.16;453.88;463.95;474.47;485.51;497.21;509.71;523.23;538.02;554.49;573.21;595.1;621.75;656.3;706.14;795.93;1154.89;645.68;660.29;675.85;692.58;710.76;730.78;753.14;778.51;807.87;842.57;842.57"/><animate attributeName="y2" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0667;0.0932;0.1198;0.1464;0.1729;0.1995;0.2260;0.2526;0.2792;0.3057;0.3323;0.3589;0.3854;0.4120;0.4385;0.4651;0.4917;0.5182;0.5448;0.5714;0.5979;0.6245;0.6510;0.6776;0.7042;0.7307;0.7573;0.7839;0.8104;0.8370;0.8635;0.8901;0.9167;1.0000" values="100;100;100;100;100;100;100;100;100;100;100;100;100;100;100;100;100;100;100;100;100;100;100;100;292.18;287.4;282.49;277.43;272.26;266.96;261.55;256.03;250.42;244.72;244.72"/><animate attributeName="stroke" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0000;0.6587" values="#2ea043;#2ea043;#e5484d"/></line>
<text x="40" y="52" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">窓の内側を見る:屈折して、空が見える<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.6583;0.6587;1.0000" values="1;1;0;0"/></text>
<text x="40" y="52" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">窓の外側を見る:全反射して、水中（海底）の景色が映る<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.6583;0.6587;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="406" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">見上げる角度が大きくなる（横を向く）と、ある角度から先は、水面が鏡になる。これが水中の「天井」の見え方。</text>
</svg>

<!-- fig:snell-window:end -->

## 水面の裏側
**水中から水面を見上げる**と、**水面は「鏡」と「窓」の両方**になります。

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="水中から見上げる窓">
<text x="20" y="24" class="fig-title">水中から見上げる：臨界角の内側だけ空が見え、外側は全反射</text>
<rect x="40" y="110" width="700" height="130" fill="#4c8bf5" fill-opacity="0.2"/>
<line x1="40" y1="110" x2="740" y2="110" stroke="#4c8bf5" stroke-width="3"/>
<circle cx="390" cy="225" r="7" fill="#e5484d"/>
<text x="402" y="230" style="font-size:12px">カメラ</text>
<line x1="390" y1="225" x2="390" y2="110" stroke="currentColor" stroke-opacity="0.4" stroke-dasharray="4 4"/>
<line x1="390" y1="225" x2="505" y2="110" stroke="#2ea043" stroke-width="3"/>
<line x1="390" y1="225" x2="275" y2="110" stroke="#2ea043" stroke-width="3"/>
<line x1="505" y1="110" x2="610" y2="60" stroke="#2ea043" stroke-width="3"/>
<line x1="275" y1="110" x2="170" y2="60" stroke="#2ea043" stroke-width="3"/>
<text x="612" y="62" style="font-size:12px">空が見える</text>
<line x1="390" y1="225" x2="610" y2="110" stroke="#e5aa28" stroke-width="3"/>
<line x1="610" y1="110" x2="690" y2="215" stroke="#e5aa28" stroke-width="3"/>
<text x="600" y="172" style="font-size:12px">全反射</text>
<text x="400" y="170" style="font-size:12px">臨界角 約 49°</text>
</svg>

**水から空気へ出る光は、臨界角（約 49°）より浅い角度だと屈折せずに全反射**します。

<div class="formula">臨界角 θc = asin( n₂ / n₁ ) = asin( 1.0 / 1.33 ) ≈ 48.8°</div>

水中から水面を見上げると、見え方が範囲で変わります。真上に近い範囲（円の内側）では、空が見えます（窓）。空は円形に縮んで見えます（スネルの窓）。円の外側では、全反射が起きて、水中の景色が水面に鏡のように映ります。

```hlsl
float3 refracted = refract(-view_dir, -normal, 1.33 / 1.0);
bool total_internal_reflection = dot(refracted, refracted) < 0.001;

float3 color = total_internal_reflection
             ? SampleUnderwaterReflection(reflect(-view_dir, -normal))
             : SampleSky(refracted);
```

コードの要点です。`refract` の戻り値が 0 なら全反射（屈折できない）です。水中側から見るので、法線を反転します。水面の下側のシェーディングは、水中側の屈折率でフレネルを計算します。

## 水面をまたぐ処理
**水面ぎりぎりにカメラがあるとき、画面の上半分は水の外、下半分は水の中**になります。

| 工夫 | 内容 |
| --- | --- |
| **近い面を塞ぐ** | **カメラ前方の水面に細い帯**（水中のフォグ色）**を描き、境目の隙間をなくす** |
| **水位線の描画** | **ポストプロセスで水位の画面上の位置を求め、上下で別の処理** |
| **体積の判定** | **水のボリューム（メッシュ）を描き、前面・裏面で内外を決める** |
| **遷移** | **水に入る瞬間は、フェードで急変を隠す** |

## よくあるミス

??? failure "水に入る瞬間、画面がちらつく"
    **水面のメッシュは、裏面も描き**、**水中の判定をなめらかに**切り替える。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **裏面も描く**
    - [x] **またぐ瞬間の処理に注意**

## 参考

- Tessendorf, "Simulating Ocean Water"（SIGGRAPH Course Notes 2001）
- Finch, "Effective Water Simulation from Physical Models"（GPU Gems 2004）
- Vlachos, "Water Flow in Portal 2"（SIGGRAPH 2010）

## 関連ページ

- [Underwater Rendering](index.md)
- [Underwater Fog](fog.md)
