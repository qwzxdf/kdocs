---
title: 距離場の影
tags:
  - 描画
---

# 距離場の影

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
| <strong>間接的な、空の遮蔽（距離場 AO）</strong> | **同じ SDF を、AO にも使う**（[AO の手法](../ao/world-space.md)） |

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

- [影](index.md)
- [PCSS](pcss.md)
- [カスケード シャドウ マップ](cascaded.md)
- [AO のその他の手法（距離場 AO）](../ao/world-space.md)
