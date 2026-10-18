---
title: Depth Peeling
tags:
  - 描画
---

# Depth Peeling

**Depth Peeling は、最も手前の層を描いて、その次の層、さらに次…と、1 枚ずつ剥ぎながら描く手法**です。**正確ですが、層の数だけ描画が必要**で、**重い**です。このページでは、**Depth Peeling の仕組みと限界**を説明します。

!!! tip "ポイント"
    - **1 パスごとに、1 層ずつ（手前から）取り出す**。
    - **層の数だけ、パスが必要**（4 層なら 4 パス）。
    - **正確だが、重い**。
    - **現在は、PPLL や WBOIT に置き換わっている**。

<!-- fig:depth-peeling-passes:begin -->

<svg class="fig illust motion" data-fig="depth-peeling-passes" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-depth-peeling-passes" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">Depth Peeling:手前の層から、1 パスに 1 枚ずつ剥いでいく</text>
<line x1="60" y1="60" x2="60" y2="340" stroke="#1f2937" stroke-width="2"/>
<text x="60" y="52" text-anchor="start" style="font-size:11px;font-weight:700;fill:#64748b">視点（上から見下ろす）</text>
<rect x="140" y="80" width="300" height="22" fill="#e5484d" fill-opacity="0.35" stroke="#e5484d" stroke-width="2"/>
<text x="150" y="96" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">層 1</text>
<rect x="140" y="150" width="300" height="22" fill="#2ea043" fill-opacity="0.35" stroke="#2ea043" stroke-width="2"/>
<text x="150" y="166" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">層 2</text>
<rect x="140" y="220" width="300" height="22" fill="#2563eb" fill-opacity="0.35" stroke="#2563eb" stroke-width="2"/>
<text x="150" y="236" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">層 3</text>
<rect x="140" y="290" width="300" height="22" fill="#e5aa28" fill-opacity="0.35" stroke="#e5aa28" stroke-width="2"/>
<text x="150" y="306" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">層 4</text>
<line x1="90" y1="60" x2="90" y2="340" stroke="#64748b" stroke-width="2" stroke-dasharray="4 4"/>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0825;0.0828;0.2756;0.2759;1.0000" values="0;0;1;1;0;0"/><circle cx="90" cy="91" r="8" fill="#e5484d" stroke="#ffffff" stroke-width="2"/>
<line x1="60" y1="91" x2="140" y2="91" stroke="#e5484d" stroke-width="2.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2756;0.2759;0.4687;0.4690;1.0000" values="0;0;1;1;0;0"/><circle cx="90" cy="161" r="8" fill="#2ea043" stroke="#ffffff" stroke-width="2"/>
<line x1="60" y1="161" x2="140" y2="161" stroke="#2ea043" stroke-width="2.5"/>
<line x1="60" y1="104" x2="460" y2="104" stroke="#e5484d" stroke-width="2" stroke-dasharray="6 3"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4687;0.4690;0.6618;0.6621;1.0000" values="0;0;1;1;0;0"/><circle cx="90" cy="231" r="8" fill="#2563eb" stroke="#ffffff" stroke-width="2"/>
<line x1="60" y1="231" x2="140" y2="231" stroke="#2563eb" stroke-width="2.5"/>
<line x1="60" y1="174" x2="460" y2="174" stroke="#e5484d" stroke-width="2" stroke-dasharray="6 3"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6618;0.6621;0.8549;0.8552;1.0000" values="0;0;1;1;0;0"/><circle cx="90" cy="301" r="8" fill="#e5aa28" stroke="#ffffff" stroke-width="2"/>
<line x1="60" y1="301" x2="140" y2="301" stroke="#e5aa28" stroke-width="2.5"/>
<line x1="60" y1="244" x2="460" y2="244" stroke="#e5484d" stroke-width="2" stroke-dasharray="6 3"/>
</g>
<text x="40" y="380" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">パス 1:しきい値より奥で、最も手前の層（層 1）を取り出す<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0825;0.0828;0.2756;0.2759;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="380" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">パス 2:しきい値より奥で、最も手前の層（層 2）を取り出す<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2756;0.2759;0.4687;0.4690;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="380" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">パス 3:しきい値より奥で、最も手前の層（層 3）を取り出す<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4687;0.4690;0.6618;0.6621;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="380" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">パス 4:しきい値より奥で、最も手前の層（層 4）を取り出す<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6618;0.6621;0.8549;0.8552;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="80" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">各パスの結果（層ごとの画像）</text>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2370;0.2372;1.0000" values="0;0;1;1"/><rect x="520" y="96" width="120" height="44" fill="#e5484d" fill-opacity="0.5" stroke="#e5484d" stroke-width="2"/>
<text x="580" y="123" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">層 1 の画像</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4301;0.4303;1.0000" values="0;0;1;1"/><rect x="520" y="152" width="120" height="44" fill="#2ea043" fill-opacity="0.5" stroke="#2ea043" stroke-width="2"/>
<text x="580" y="179" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">層 2 の画像</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6232;0.6234;1.0000" values="0;0;1;1"/><rect x="520" y="208" width="120" height="44" fill="#2563eb" fill-opacity="0.5" stroke="#2563eb" stroke-width="2"/>
<text x="580" y="235" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">層 3 の画像</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.8163;0.8166;1.0000" values="0;0;1;1"/><rect x="520" y="264" width="120" height="44" fill="#e5aa28" fill-opacity="0.5" stroke="#e5aa28" stroke-width="2"/>
<text x="580" y="291" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">層 4 の画像</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.8549;0.8552;1.0000" values="0;0;1;1"/><line x1="650" y1="190" x2="700" y2="190" stroke="#1f2937" stroke-width="2.5" marker-end="url(#arr-depth-peeling-passes)"/>
<rect x="700" y="150" width="60" height="80" fill="#9ca3af" stroke="#1f2937" stroke-width="2"/>
<text x="730" y="246" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#1f2937">奥から合成</text>
</g>
<text x="40" y="404" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">層の数だけパスが必要（4 層なら 4 パス）。正確だが、重い。<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.8549;0.8552;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:depth-peeling-passes:end -->

## Depth Peeling
<strong>「最も手前の層」を、深度テストで取り出し、次に「その次の層」を取り出し…と、層を剥がしていく</strong>方法です。

Depth Peeling の手順は 4 段階です。1 枚目は、通常の深度テストで最も手前の半透明の層を画像 1 に描き、深度 1 を保存します。2 枚目は、深度 1 より奥の最も手前を画像 2 に描きます（前の深度より手前のフラグメントは捨てます）。これを層の数だけ繰り返します。最後に、奥の層から手前へ、N 枚の画像を重ねて合成します。

原典は、Everitt の "Interactive Order-Independent Transparency"（NVIDIA、2001）で、後に Bavoil と Myers が、手前と奥を同時に剥がす Dual Depth Peeling（2008）で、パスを半分にしました。

```hlsl
float4 PSMain(VsOutput input) : SV_Target {
  float previous_depth = previous_depth_texture.Load(int3(input.position.xy, 0)).r;
  clip(input.position.z - previous_depth - kEpsilon);
  return Shade(input);
}
```

コードの要点です。`clip(z - previous_depth - ε)` で、前の層と同じか手前のフラグメントを捨てます。層の数は、4 層でも多くのシーンで足りますが、足りない画素は欠けます。コストは N 回の描画で、シーン全体の半透明ジオメトリを N 回流します。派生として Dual Depth Peeling があり、手前と奥を同時に剥がすのでパスが半分になります。

## よくあるミス

??? failure "層が多いシーンで、Depth Peeling が遅すぎる"
    **PPLL や WBOIT**に切り替える。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **1 層ずつ剥いで、正確に描く**
    - [x] **重いので、現在は少数派**

## 参考

- McGuire & Bavoil, "Weighted Blended Order-Independent Transparency"（JCGT 2013）
- Everitt, "Interactive Order-Independent Transparency"（NVIDIA 2001）
- Wyman & McGuire, "Hashed Alpha Testing"（I3D 2017）

## 関連ページ

- [OIT](index.md)
- [PPLL](ppll.md)
- [WBOIT](wboit.md)
