---
title: 視差補正
tags:
  - 描画
---

# 視差補正

**キューブマップは、「プローブの位置から見た景色」なので、別の場所から見ると、反射が実際とずれます**。**部屋の形の箱（ボックス）を想定して、レイと箱の交点を求めて、補正する**のが**標準的な方法**です。このページでは、**視差の問題・ボックス投影・補正の限界**を説明します。

!!! tip "ポイント"
    - **キューブマップは、無限遠の景色を前提**にしているため、**近くの壁がずれる**。
    - **部屋の形の箱を設定し、レイと箱の交点から、読み出す方向を作り直す**（ボックス投影）。
    - **箱の形が実際と違うと、ずれが残る**。
    - **床の反射は、補正しても、不自然になりやすい**（平面反射を併用）。

## 視差の問題と補正
### 視差の問題

プローブは、**1 点（プローブの位置）から見た景色**です。**面とプローブの位置が離れている**と、**面から見た景色とプローブから見た景色が、ずれます**。

<svg class="fig illust" viewBox="0 0 780 300" role="img" aria-label="視差の問題">
<text x="20" y="24" class="fig-title">プローブの位置と、反射する面の位置が違うと、映り込みがずれる</text>
<rect x="50" y="50" width="680" height="220" fill="rgba(150,150,150,0.1)" stroke="currentColor" stroke-width="2"/><text x="60" y="68" style="font-size:12px">部屋（壁）</text>
<circle cx="390" cy="160" r="7" fill="#2ea043"/><text x="364" y="184" style="font-size:12px;fill:#2ea043;font-weight:700">プローブ</text>
<line x1="150" y1="250" x2="330" y2="250" stroke="currentColor" stroke-width="5"/><text x="180" y="270" style="font-size:12px">床の面（反射する）</text>
<circle cx="250" cy="250" r="6" fill="currentColor"/><text x="240" y="238" style="font-size:12px">p</text>
<line x1="250" y1="250" x2="500" y2="110" stroke="#e5484d" stroke-width="2.5"/><text x="500" y="104" style="font-size:12px;fill:#e5484d;font-weight:700">本当の反射が当たる壁</text>
<line x1="390" y1="160" x2="640" y2="20" stroke="#4c8bf5" stroke-width="2" stroke-dasharray="5 3"/><text x="520" y="62" style="font-size:12px;fill:#4c8bf5;font-weight:700">プローブから R 方向に引くと…</text>
<text x="420" y="290" style="font-size:12px">→ 実際より、遠く（別の場所）の景色が映ってしまう</text>
</svg>

特に**平らな床**で**壁との境が実際より遠くに映る**・**物が宙に浮いて見える**といった症状が出ます。

<!-- fig:parallax-box:begin -->

<svg class="fig illust motion" data-fig="parallax-box" viewBox="0 0 780 440" role="img"><rect x="0" y="0" width="780" height="440" rx="14" fill="#ffffff"/>
<defs><marker id="arr-parallax-box" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">視差補正:プローブの位置ではなく、反射点から、箱の壁までの交点で引く</text>
<rect x="120" y="90" width="580" height="260" fill="#f8fafc" stroke="#1f2937" stroke-width="4"/>
<text x="128" y="110" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">部屋（プローブの影響範囲の箱）</text>
<circle cx="330" cy="220" r="9" fill="#e5aa28" stroke="#ffffff" stroke-width="2"/>
<text x="342" y="242" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5aa28">プローブ</text>
<circle cx="200" cy="340" r="8" fill="#2563eb" stroke="#ffffff" stroke-width="2"><animate attributeName="cx" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0593;0.2593;0.4815;0.7037;1.0000" values="200;200;330;520;200;200"/></circle>
<text x="200" y="378" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#2563eb">反射する点</text>
<line x1="200" y1="340" x2="0" y2="0" stroke="#2563eb" stroke-width="2.5"><animate attributeName="x1" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0593;0.2593;0.4815;0.7037;1.0000" values="200;200;330;520;200;200"/><animate attributeName="x2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.2593;0.4815;0.7037;1.0000" values="0;0;398.72;528.72;700;398.72;398.72"/><animate attributeName="y2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.2593;0.4815;0.7037;1.0000" values="0;0;90;90;113.55;90;90"/></line>
<line x1="330" y1="220" x2="0" y2="0" stroke="#e5484d" stroke-width="2" stroke-dasharray="6 4"><animate attributeName="x2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.2593;0.4815;0.7037;1.0000" values="0;0;433.33;433.33;433.33;433.33;433.33"/><animate attributeName="y2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.2593;0.4815;0.7037;1.0000" values="0;0;90;90;90;90;90"/></line>
<line x1="330" y1="220" x2="0" y2="0" stroke="#2ea043" stroke-width="3"><animate attributeName="x2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.2593;0.4815;0.7037;1.0000" values="0;0;398.72;528.72;700;398.72;398.72"/><animate attributeName="y2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.2593;0.4815;0.7037;1.0000" values="0;0;90;90;113.55;90;90"/></line>
<circle cx="0" cy="0" r="6" fill="#e5484d"><animate attributeName="cx" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.2593;0.4815;0.7037;1.0000" values="0;0;433.33;433.33;433.33;433.33;433.33"/><animate attributeName="cy" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.2593;0.4815;0.7037;1.0000" values="0;0;90;90;90;90;90"/></circle>
<circle cx="0" cy="0" r="6" fill="#2ea043"><animate attributeName="cx" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.2593;0.4815;0.7037;1.0000" values="0;0;398.72;528.72;700;398.72;398.72"/><animate attributeName="cy" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.2593;0.4815;0.7037;1.0000" values="0;0;90;90;113.55;90;90"/></circle>
<text x="40" y="60" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">青い線 = 反射レイ。壁に当たる点が、本当に映る場所<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;1.0000;1.0000" values="1;1;0"/></text>
<text x="40" y="404" text-anchor="start" style="font-size:13px;font-weight:500;fill:#e5484d">赤（補正なし）:プローブから、反射方向をそのまま引く → 本当の点とずれる。</text>
<text x="40" y="426" text-anchor="start" style="font-size:13px;font-weight:500;fill:#2ea043">緑（補正あり）:壁の交点を求め、プローブから、その交点への向きで引く → ぴったり合う。</text>
</svg>

<!-- fig:parallax-box:end -->

### 視差補正：プローブの範囲を箱で近似する

**プローブが写している範囲（部屋）を、箱（または球）で近似**します。**反射レイ**を**表面の位置 p から R 方向に飛ばして、箱と交差する点 H** を求めます。**プローブの位置から H への方向**で、キューブマップを引きます。

<div class="formula">H = p + R · t　（レイと箱の交点）、　引く方向 R′ = H − probe_pos</div>

**表面の位置 p から**、<strong>本当に当たる壁（H）</strong>を求めて、そこを**プローブから見た方向**で引き直すので、**視差のずれが補正されます**。

### 箱（AABB）との交差

```hlsl
float3 BoxProjection(float3 world_pos, float3 R, float3 probe_pos,
                     float3 box_min, float3 box_max) {
  float3 first_plane = (box_max - world_pos) / R;
  float3 second_plane = (box_min - world_pos) / R;
  float3 furthest = max(first_plane, second_plane);
  float distance = min(min(furthest.x, furthest.y), furthest.z);
  float3 hit = world_pos + R * distance;
  return hit - probe_pos;
}
```

| 点 | 説明 |
| --- | --- |
| **`(box_max − pos) / R`・`(box_min − pos) / R`** | 3 軸の箱の面までの距離（レイが各面に当たる t） |
| **`max(first, second)`** | **前向き（レイが進む側）の面**を選ぶ |
| **`min(…x, y, z)`** | **最初に当たる**面（箱の内側からの出口） |
| **戻り値** | プローブから見た方向（正規化はサンプラーが不要） |

!!! note "箱の範囲の決め方"
    **プローブが写す範囲**（影響範囲）を、**部屋の大きさに合わせた箱**にします。**箱が実際の壁と合っているほど**、補正が正確です。**合っていないと補正が逆効果**になることもあります。

### 視差補正の限界

| 限界 | 説明 |
| --- | --- |
| **箱の近似** | **部屋の中の家具・物体は箱の壁として扱われる** → **家具の反射は、壁の位置に映る** |
| **プローブ位置の物陰** | プローブから見えなかった所（家具の裏）は、撮れていない |
| **不規則な形の部屋** | 箱で表せない部屋では、**補正が合わない** |
| **動く物** | プローブには映らない（動的な更新が必要） |

## よくあるミス

??? failure "床や壁に映る景色が、動くと滑って見える"
    **ボックス投影（視差補正）**を入れる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **箱を想定して、読み出す方向を補正**
    - [x] **箱の形が、実際に近いほど良い**

## 参考

- McGuire & Mara, "Efficient GPU Screen-Space Ray Tracing"（JCGT 2014）
- Karis, "Real Shading in Unreal Engine 4"（SIGGRAPH 2013）
- Stachowiak, "Stochastic Screen-Space Reflections"（SIGGRAPH 2015）

## 関連ページ

- [反射プローブ](index.md)
- [プローブの運用](blending.md)
- [平面反射](../planar.md)
