---
title: Point Lights: Cube Maps
tags:
  - 描画
---

# Point Lights: Cube Maps

**点光源は、全方向を照らす**ので、**影を作るには、全方向の深度が必要**です。**キューブ マップ（6 面）に、各方向の深度を描く**のが**標準**で、**サンプルは、ライトから画面の点への方向ベクトルで引く**ので**簡単**です。**ただし、6 回描くので、コストが 6 倍**です。このページでは、**キューブ マップの作り方・方向ベクトルでのサンプル・線形距離の保存・面の境界と PCF**を説明します。

!!! tip "ポイント"
    - **点光源の影 ＝ 6 面のキューブ マップ**（**各面 90° の透視投影**）。
    - **サンプルは、方向ベクトルで引く**（**面を意識しなくてよい**）。
    - **保存は、非線形深度より、ライトからの距離（線形）**が**扱いやすい**。
    - **面の境界で、PCF のサンプルが隣の面に跨ぐ**ので**注意**。

<!-- fig:point-cubemap-faces:begin -->

<svg class="fig illust motion" data-fig="point-cubemap-faces" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-point-cubemap-faces" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">点光源の影:6 方向にシャドウ マップを描く（キューブ マップ）</text>
<polygon points="390,238 473.44,154.56 473.44,321.44" fill="#fecaca" fill-opacity="0.18" stroke="#94a3b8" stroke-width="1.5"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0741;0.0963;0.2000;0.2222;1.0000" values="0.18;0.18;0.55;0.55;0.18;0.18"/></polygon>
<polygon points="390,238 306.56,154.56 473.44,154.56" fill="#bbf7d0" fill-opacity="0.18" stroke="#94a3b8" stroke-width="1.5"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2222;0.2444;0.3481;0.3704;1.0000" values="0.18;0.18;0.55;0.55;0.18;0.18"/></polygon>
<polygon points="390,238 306.56,321.44 306.56,154.56" fill="#bfdbfe" fill-opacity="0.18" stroke="#94a3b8" stroke-width="1.5"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3704;0.3926;0.4963;0.5185;1.0000" values="0.18;0.18;0.55;0.55;0.18;0.18"/></polygon>
<polygon points="390,238 473.44,321.44 306.56,321.44" fill="#fde68a" fill-opacity="0.18" stroke="#94a3b8" stroke-width="1.5"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5185;0.5407;0.6444;0.6667;1.0000" values="0.18;0.18;0.55;0.55;0.18;0.18"/></polygon>
<circle cx="490" cy="218" r="15" fill="#e5484d" stroke="#ffffff" stroke-width="2"/>
<circle cx="370" cy="133" r="15" fill="#2ea043" stroke="#ffffff" stroke-width="2"/>
<circle cx="295" cy="273" r="15" fill="#2563eb" stroke="#ffffff" stroke-width="2"/>
<circle cx="430" cy="333" r="15" fill="#e5aa28" stroke="#ffffff" stroke-width="2"/>
<circle cx="390" cy="238" r="13" fill="#e5aa28" stroke="#ffffff" stroke-width="2"/>
<text x="390" y="274" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#e5aa28">点光源</text>
<text x="532.0" y="243.0" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">+X（右）</text>
<text x="60" y="70" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">面 1:+X 向きに、90° の視野でシャドウ マップを描く<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.2219;0.2222;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390.0" y="101.0" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">+Z（奥）</text>
<text x="60" y="70" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">面 2:+Z 向きに、90° の視野でシャドウ マップを描く<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2219;0.2222;0.3701;0.3704;1.0000" values="0;0;1;1;0;0"/></text>
<text x="248.0" y="243.00000000000003" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">−X（左）</text>
<text x="60" y="70" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">面 3:−X 向きに、90° の視野でシャドウ マップを描く<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3701;0.3704;0.5182;0.5185;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390.0" y="385.0" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">−Z（手前）</text>
<text x="60" y="70" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">面 4:−Z 向きに、90° の視野でシャドウ マップを描く<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5182;0.5185;0.6664;0.6667;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">上（+Y）と下（−Y）も加えて 6 面。描画は 6 回（視錐台カリングで、物が無い面は省ける）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6664;0.6667;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="60" y="70" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2ea043" opacity="0">まとめ:光を中心に、6 つの方向へ<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6664;0.6667;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="60" y="410" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">上から見た図。影を引く時は、光から見た方向ベクトルで、6 面のうちの 1 枚を選ぶ。</text>
</svg>

<!-- fig:point-cubemap-faces:end -->

## 点光源：キューブ マップ
**点光源**は**あらゆる方向**に光を出します。**6 方向（±X, ±Y, ±Z）に、視野角 90 度の透視投影**で描けば、**全方向を覆えます**（**キューブ シャドウ マップ**）。

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="キューブ シャドウ マップ">
<text x="20" y="24" class="fig-title">点光源から 6 方向へ、視野角 90 度で描く（真上から見た図）</text>
<circle cx="200" cy="140" r="9" fill="rgba(229,170,40,0.9)" stroke="currentColor" stroke-width="2"/><text x="214" y="132" style="font-size:12px">光源</text>
<line x1="200" y1="140" x2="320" y2="40" stroke="currentColor" stroke-dasharray="4 3"/><line x1="200" y1="140" x2="320" y2="240" stroke="currentColor" stroke-dasharray="4 3"/>
<line x1="200" y1="140" x2="80" y2="40" stroke="currentColor" stroke-dasharray="4 3"/><line x1="200" y1="140" x2="80" y2="240" stroke="currentColor" stroke-dasharray="4 3"/>
<text x="326" y="146" style="font-size:12px">+X 面</text><text x="30" y="146" style="font-size:12px">−X 面</text><text x="170" y="40" style="font-size:12px">+Z 面</text><text x="170" y="254" style="font-size:12px">−Z 面</text>
<text x="420" y="90" style="font-size:13px">各面：視野角 90°、アスペクト 1</text>
<text x="420" y="116" style="font-size:13px">±Y 面（上下）も同様に描く（図は省略）</text>
<text x="420" y="152" style="font-size:13px">画素 → ライトからのベクトル v の</text>
<text x="420" y="172" style="font-size:13px">絶対値が最大の成分で、使う面が決まる</text>
</svg>

| 方式 | 内容 |
| --- | --- |
| **6 枚のレンダー ターゲット** | `Texture2DArray` の 6 スライス（または `TextureCube`）に、**6 回**描く |
| **ジオメトリ シェーダーで 1 回** | **`SV_RenderTargetArrayIndex`** で、**1 回の描画で 6 面**へ（環境による。効率は微妙） |
| **ビュー インスタンシング** | 対応環境で、**1 回のドロー**で複数面 |

### サンプル：方向ベクトルで引く

**キューブ マップ**は、**ライトから画素へのベクトル**で、**サンプル**できます。**比較には保存された深度**と<strong>そのベクトルの長さ（または面ごとの深度）</strong>を使います。

```hlsl
float PointShadow(float3 world_pos) {
  float3 v = world_pos - light_position;
  float3 a = abs(v);
  float major = max(a.x, max(a.y, a.z));
  float depth = (light_far * (major - light_near)) / (major * (light_far - light_near));
  return shadow_cube.SampleCmpLevelZero(shadow_sampler, v, depth - bias);
}
```

| 点 | 説明 |
| --- | --- |
| **`major`** | **絶対値が最大の成分**＝**その面の、ビュー空間の z** |
| **`depth`** | **透視投影の深度の式**で**射影後の深度**（0〜1）に変換（左手系の `XMMatrixPerspectiveFovLH` と同じ） |
| **`shadow_cube`** | `TextureCube`（比較サンプラー）。**面の境界もハードウェアが補間** |

### 線形な距離を保存する方法

**射影後の深度**でなく、**ライトからの線形距離**（`length(v) / light_far`）を、**ピクセル シェーダーで書く**方式もあります。**比較は単純**ですが**ハードウェアの深度テスト・Early-Z を使えない**（深度を自分で書く）ので**描画が遅く**なります。**射影後の深度**が一般的です。

### 面の境界と PCF

**面の境界をまたぐ PCF**は、**隣の面のテクセル**を参照する必要があります。**キューブ マップのハードウェア サンプラー**は、**面をまたぐ補間**を**正しく**処理します。**自前で面ごとの 2D テクスチャ配列**を使うと、**境界で PCF が途切れる**ので、**注意**が必要です。

## よくあるミス

??? failure "キューブ マップの面の継ぎ目に線が出る"
    **PCF のサンプルが面を跨ぐ**ので、**方向ベクトルでサンプル**し、**境界の処理**をする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **点光源の影 ＝ 6 面のキューブ マップ**
    - [x] **方向ベクトルで引く**。**コストは 6 倍**

## 参考

- Eisemann et al., "Real-Time Shadows"（CRC Press 2011）
- Microsoft, "Common Techniques to Improve Shadow Depth Maps"（Microsoft Learn）

## 関連ページ

- [Point and Spot Light Shadows](index.md)
- [Spot Lights](spot-light.md)
- [Dual Paraboloid](dual-paraboloid.md)
