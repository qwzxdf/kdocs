---
title: PBR（物理ベースレンダリング）
tags:
  - 3Dゲーム
---

# PBR（物理ベースレンダリング）

**PBR**（ピー・ビー・アール、Physically Based Rendering）は、**光の物理的な振る舞いに沿って、陰影を計算する**描画の考え方です。[法線とライティング](lighting-normals.md)の**ブリン・フォン**は、「それっぽく見える」式を、**見た目を見ながら調整**する方法でした。PBR では、**材質を、物理的な意味を持つ数字**（色・金属度・粗さ）で表し、**どんな光の中でも、破綻しない**見た目を目指します。現在の、ほとんどのゲームエンジン（Unreal、Unity、Godot）と、glTF の標準の材質が、PBR です。このページは、**なぜその式になるのか**という原理から、DX11 / HLSL での実装までをまとめます。

!!! tip "ポイント"
    - PBR の<strong>原則は 3 つ</strong>：<strong>① エネルギー保存</strong>（出る光は、入る光より多くならない）、<strong>② マイクロファセット</strong>（表面は、微小な鏡の集まり）、<strong>③ フレネル</strong>（浅い角度ほど、よく反射する）。
    - 材質は<strong>「ベースカラー・金属度（metallic）・粗さ（roughness）」</strong>で表す（<strong>メタリック・ラフネス</strong>方式）。
    - 反射の式は <strong>Cook-Torrance</strong>：<strong>鏡面 ＝ D × G × F ÷ (4 × (N·L) × (N·V))</strong>、拡散は<strong>ランバート</strong>。
    - <strong>D（法線分布）</strong>＝ハイライトの形、<strong>G（幾何減衰）</strong>＝微小な凹凸による影、<strong>F（フレネル）</strong>＝角度による反射率。
    - <strong>金属は、拡散光がなく</strong>、反射が<strong>色付き</strong>。<strong>非金属の F0 は、約 0.04</strong>（ほぼ一定）。
    - <strong>間接光（空・周囲の景色）</strong>は、<strong>IBL</strong>（環境マップ）で。これがないと、PBR は、真っ黒になる。
    - 計算は<strong>リニア空間</strong>、最後に<strong>トーンマッピング + ガンマ補正</strong>。<strong>色のテクスチャは sRGB、それ以外は、リニア</strong>。

## なぜ PBR か

ブリン・フォンには、次の問題があります。

| 問題 | 説明 |
| --- | --- |
| **エネルギー保存がない** | 光沢を上げると、ハイライトが小さくなるだけで、**明るさの総量**が、物理と合わない |
| **パラメータが、見た目任せ** | `shininess = 32` が、何を意味するのか、**物理的な根拠がない**。ライトや環境が変わると、**調整し直し** |
| **材質が、ライトに依存** | 「この金属は、この光なら良く見える」の、**職人技** |
| **金属の表現が苦手** | 金属は、拡散光がなく、反射が色付きという性質を、式に持たない |
| **斜めから見たときの反射が違う** | 現実は、浅い角度で反射が強くなる（**フレネル**） |

PBR は、**物理の式を、そのまま近似**するので、**材質の数字を決めれば、どんな光の下でも、それらしく**なります。**アーティストと、プログラマが、同じ言葉**（粗さ・金属度）で、話せます。

## 光の物理（ここから理解する）

### 光が表面に当たると

光が物体の表面に当たると、**2 つのこと**が起きます。

<div class="anim" data-type="graph" data-label="光が表面に当たったとき：表面で反射する光と、内部に入る光">
n light 入射する光 0 1 hit
n surf 表面 1 1
l light surf hit
---
n light 入射する光 0 1
n surf 表面 1 1
n spec 鏡面反射（specular）_表面ですぐ跳ね返る 2 0 new
l light surf
l surf spec hit 一部が反射
---
n light 入射する光 0 1
n surf 表面 1 1
n spec 鏡面反射（specular）_表面ですぐ跳ね返る 2 0
n inner 内部へ入る（屈折） 2 2 new
l light surf
l surf spec - 一部が反射
l surf inner hit 残りが入る
---
n light 入射する光 0 1
n surf 表面 1 1
n spec 鏡面反射（specular）_表面ですぐ跳ね返る 2 0
n inner 内部へ入る（屈折） 2 2
n diff 拡散反射（diffuse）_内部で散乱して、出てくる 3 2 new
n abs 熱になる_（吸収） 3 3 dim
l light surf
l surf spec - 一部が反射
l surf inner - 残りが入る
l inner diff hit 散乱
l inner abs - 吸収
</div>

| 光 | 起きること | 見え方 |
| --- | --- | --- |
| <strong>鏡面反射（specular）</strong> | 表面で、**すぐ**跳ね返る。**入射角と同じ角度**で出る | **ハイライト**、映り込み。**光の色のまま**（金属以外） |
| <strong>拡散反射（diffuse）</strong> | 内部へ入り、**散乱**して、**あらゆる方向**へ出る。**物体の色**に染まる | 面の色・陰影 |
| **吸収** | 内部で、熱になる | 色の暗さ（吸収されなかった波長が、物体の色になる） |

**金属**は、特別です。内部に入った光が、**すぐに吸収**されてしまうので、**拡散反射がありません**。すべての光が**鏡面反射**で、反射の**色が、金属の色**（金は黄色、銅は赤みがかった色）になります。

### エネルギー保存

**反射する光の合計は、入ってきた光より、多くならない**——これが、**エネルギー保存**です。鏡面反射が増えれば、拡散反射は、減ります。

```text
入ってきた光 ＝ 鏡面反射 ＋ 拡散反射 ＋ 吸収
    1.0     ＝   F      ＋ (1 − F) × 色 ＋ 残り
```

PBR の式は、**鏡面と拡散の比率**を、フレネル `F` で決めます（`kS = F`、`kD = 1 − F`）。

## 光の量の言葉（放射量）

式に出てくる言葉を、**直感的に**整理します。

| 名前 | 意味 | 例えると |
| --- | --- | --- |
| **放射束（Flux）Φ** | 光源が出す、**光の総量**（W） | 電球の明るさ（ワット数） |
| **放射照度（Irradiance）E** | **面が、受け取る**光の量。**単位面積あたり**（W/m²） | 机の上の、明るさ |
| **放射輝度（Radiance）L** | **ある方向に、進む**光の量。**単位面積・単位立体角あたり** | **目やカメラに、入る光**。**ピクセルの色**は、これ |

**ピクセルの色 ＝ そのピクセルから、カメラに向かう光の放射輝度 `Lo`** です。

### 半球と入射光

面に当たる光は、**面の上の半球**のあらゆる方向から、来ます。

<svg class="fig" viewBox="0 0 560 250" role="img" aria-label="半球と入射・出射方向">
<defs><marker id="pa" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
<path d="M 60 200 A 180 160 0 0 1 420 200" fill="none" stroke="currentColor" stroke-width="1.5" stroke-dasharray="5 4"/>
<line x1="30" y1="200" x2="450" y2="200" stroke="currentColor" stroke-width="3"/>
<circle cx="240" cy="200" r="5" fill="currentColor"/><text x="248" y="222">点 p</text>
<line x1="240" y1="200" x2="240" y2="55" stroke="currentColor" stroke-width="2" marker-end="url(#pa)"/><text x="246" y="62">N（法線）</text>
<line x1="95" y1="105" x2="232" y2="193" stroke="currentColor" stroke-width="2" marker-end="url(#pa)"/><text x="50" y="98">入射光 Li（方向 ωi）</text>
<line x1="248" y1="193" x2="380" y2="110" stroke="currentColor" stroke-width="2" marker-end="url(#pa)"/><text x="330" y="100">出射 Lo（方向 ωo：カメラへ）</text>
<line x1="130" y1="140" x2="140" y2="165" stroke="currentColor" stroke-width="1" /><line x1="300" y1="160" x2="320" y2="120" stroke="currentColor" stroke-width="1" />
<text x="470" y="90">半球のあらゆる方向</text><text x="470" y="112">から、光が来る</text>
</svg>

### レンダリング方程式

ここまでを、**1 つの式**にまとめたものが、**レンダリング方程式**です。

<div class="formula">Lo(p, ωo) ＝ Le(p, ωo) ＋ ∫ fr(p, ωi, ωo) · Li(p, ωi) · (N · ωi) dωi</div>

| 記号 | 意味 |
| --- | --- |
| <strong>Lo(p, ωo)</strong> | **点 p から、方向 ωo（カメラ）へ出る光**＝ピクセルの色 |
| **Le** | 物体自身が発する光（**発光**。エミッシブ） |
| **∫ … dωi** | 面の上の、**半球のすべての入射方向**について、足し合わせる（積分） |
| <strong>fr(p, ωi, ωo)</strong> | **BRDF**。方向 ωi から入った光のうち、方向 ωo へ**反射する割合** |
| <strong>Li(p, ωi)</strong> | 方向 ωi から、**やってくる光** |
| <strong>(N · ωi)</strong> | **入射角による、面の明るさ**（ランバートの `cosθ`。斜めの光は、同じ面積に薄く当たる） |

**ゲームでは、この積分を、そのまま計算できません**。そこで、**光源が数個**なら、積分を**ライトごとの足し算**にし（直接光）、**空や周囲の景色**からの光は、**事前計算**（IBL）で扱います。

## BRDF（反射の割合）

**BRDF**（Bidirectional Reflectance Distribution Function：双方向反射率分布関数）は、「**ある方向から入った光が、ある方向へ、どれだけ反射するか**」を表す関数です。PBR は、**BRDF を、物理的に正しい形で、作る**ことです。

| 性質 | 説明 |
| --- | --- |
| **エネルギー保存** | **すべての方向に反射する光の合計**が、入ってきた光を、超えない |
| **相反性** | **入る方向と出る方向を入れ替えても、値が同じ**（光の経路は逆にたどれる） |
| **非負** | 反射が、負になることはない |

## マイクロファセット理論

**表面は、肉眼では平らでも、顕微鏡で見れば、微小な凸凹**の集まりです。**ひとつひとつは、完全な鏡**（マイクロファセット）と考えます。

<svg class="fig" viewBox="0 0 600 230" role="img" aria-label="滑らかな面と粗い面のマイクロファセット">
<defs><marker id="pb" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
<text x="20" y="22" class="fig-title">滑らか（roughness 小）</text>
<polyline points="20,150 70,148 120,151 170,149 220,150 270,148" fill="none" stroke="currentColor" stroke-width="3"/>
<line x1="70" y1="40" x2="120" y2="146" stroke="currentColor" stroke-width="2" marker-end="url(#pb)"/>
<line x1="125" y1="146" x2="175" y2="40" stroke="currentColor" stroke-width="2" marker-end="url(#pb)"/>
<line x1="155" y1="40" x2="190" y2="144" stroke="currentColor" stroke-width="2" marker-end="url(#pb)"/>
<line x1="195" y1="144" x2="245" y2="40" stroke="currentColor" stroke-width="2" marker-end="url(#pb)"/>
<text x="20" y="190">反射が、同じ方向にそろう</text><text x="20" y="212">→ 小さく鋭いハイライト（鏡に近い）</text>
<text x="320" y="22" class="fig-title">粗い（roughness 大）</text>
<polyline points="320,150 345,125 370,160 395,120 420,158 445,128 470,162 495,122 520,156 560,130" fill="none" stroke="currentColor" stroke-width="3"/>
<line x1="350" y1="40" x2="372" y2="156" stroke="currentColor" stroke-width="2" marker-end="url(#pb)"/>
<line x1="382" y1="156" x2="340" y2="45" stroke="currentColor" stroke-width="2" marker-end="url(#pb)"/>
<line x1="420" y1="40" x2="440" y2="150" stroke="currentColor" stroke-width="2" marker-end="url(#pb)"/>
<line x1="450" y1="150" x2="520" y2="50" stroke="currentColor" stroke-width="2" marker-end="url(#pb)"/>
<line x1="490" y1="40" x2="515" y2="150" stroke="currentColor" stroke-width="2" marker-end="url(#pb)"/>
<text x="320" y="190">反射が、ばらばらの方向へ散る</text><text x="320" y="212">→ 広くぼんやりしたハイライト</text>
</svg>

**ある方向へ光を反射できるのは、「法線が、ちょうど、光と視線の真ん中（ハーフベクトル H）を向いている」微小な面だけ**です。そこで、BRDF は、次の 3 つを組み合わせて作ります。

| 項 | 名前 | 何を表すか |
| --- | --- | --- |
| **D** | **法線分布関数** | 微小な面のうち、**法線が H を向いているものの割合**。粗さで、形が変わる |
| **G** | <strong>幾何減衰（シャドウイング・マスキング）</strong> | 微小な凸凹に、**光が遮られる**（入る光）、**反射が遮られる**（出る光）割合 |
| **F** | **フレネル** | 角度によって変わる、**反射する割合** |

## Cook-Torrance BRDF

PBR の標準の BRDF は、**拡散**と**鏡面**の和です。

<div class="formula">fr ＝ kD · (albedo / π) ＋ kS · ( D · G · F ) / ( 4 · (N·L) · (N·V) )</div>

| 部分 | 意味 |
| --- | --- |
| **kD · albedo / π** | **拡散**（ランバート）。**`/π`** は、半球で積分したとき、エネルギーを**超えない**ための係数 |
| <strong>kS · D·G·F / (4 (N·L)(N·V))</strong> | **鏡面**（Cook-Torrance）。分母の <strong>4 (N·L)(N·V)</strong> は、微小面の向きから、実際の光の経路に直す係数 |
| **kS ＝ F** | 鏡面反射の割合（フレネルが決める） |
| <strong>kD ＝ (1 − kS) × (1 − metallic)</strong> | 拡散の割合。**鏡面に使われた分は、引く**。**金属は、0**（拡散なし） |

### D：法線分布関数（GGX）

**GGX**（Trowbridge-Reitz）は、現在の標準です。**ハイライトの、すそが長い**（中心が鋭く、周りになだらかに広がる）のが、実際の材質と合います。

<div class="formula">D(h) ＝ α² / ( π · ( (N·H)² · (α² − 1) + 1 )² )　　　α ＝ roughness²</div>

| 値 | 説明 |
| --- | --- |
| **`N·H`** | 法線と、ハーフベクトルの、一致の度合い（1 で一致） |
| **`α = roughness²`** | **粗さを二乗**する（見た目の変化が、**均等**になる。Disney の方式） |
| **roughness が小さい** | `N·H = 1` の周りだけが、**とても大きい**値 → 小さく鋭いハイライト |
| **roughness が大きい** | 広い範囲で、**なだらか** → 広くぼやけたハイライト |

### G：幾何減衰（Smith + Schlick-GGX）

**微小な凸凹**で、**入る光**が隣の山に隠れ（シャドウイング）、**出る光**が隠れる（マスキング）ことを、表します。**入る側と出る側を、別々に計算して、掛け合わせます**（Smith）。

<div class="formula">G ＝ G1(N·L) · G1(N·V)　　　G1(x) ＝ x / ( x · (1 − k) + k )　　　k ＝ (roughness + 1)² / 8（直接光）</div>

| 値 | 説明 |
| --- | --- |
| **`N·V` / `N·L` が小さい**（浅い角度） | `G1` が小さくなる（光が、遮られやすい） |
| **roughness が大きい** | 全体に、遮られやすい |
| **`k`** | 直接光では `(r+1)²/8`、IBL では `r²/2` を使う（Epic Games の近似） |

### F：フレネル（Schlick の近似）

**フレネル**は、「**浅い角度**で見るほど、**反射が強くなる**」現象です。水面を真上から見ると透けますが、**遠くの水面は、空を、鏡のように映します**。

<div class="formula">F ＝ F0 ＋ ( 1 − F0 ) · ( 1 − (H·V) )⁵</div>

<svg class="fig" viewBox="0 0 560 250" role="img" aria-label="フレネル反射率の曲線">
<defs><marker id="pc" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
<line x1="60" y1="200" x2="520" y2="200" stroke="currentColor" stroke-width="2" marker-end="url(#pc)"/>
<line x1="60" y1="200" x2="60" y2="30" stroke="currentColor" stroke-width="2" marker-end="url(#pc)"/>
<text x="470" y="222">視線の角度（正面 → 浅い角度）</text><text x="64" y="26">反射率 F</text>
<line x1="60" y1="180" x2="500" y2="180" stroke="currentColor" stroke-dasharray="4 4" stroke-width="1"/><text x="505" y="184">F0</text>
<path d="M 60 180 C 280 178 400 170 440 120 S 490 50 500 45" fill="none" stroke="currentColor" stroke-width="3"/>
<text x="70" y="168">正面：F0（非金属は約 0.04＝4%）</text>
<text x="300" y="75">真横に近づくと、</text><text x="300" y="95">1（100%）に近づく</text>
<text x="60" y="244">非金属：真正面はほとんど反射せず、浅い角度で、鏡のようになる</text>
</svg>

| 値 | 説明 |
| --- | --- |
| **F0** | **正面から見たときの反射率**。物質で決まる |
| **`H·V`** | 視線とハーフベクトルの内積。**浅い角度**ほど、0 に近づく |
| **`(1 − H·V)⁵`** | 浅い角度で、急に効いてくる項 |

## 材質：メタリック・ラフネス

材質を、**3 つの数字**で表します。

| パラメータ | 範囲 | 意味 |
| --- | --- | --- |
| <strong>ベースカラー（albedo）</strong> | RGB | 非金属は**拡散色**、金属は<strong>反射色（F0）</strong> |
| <strong>金属度（metallic）</strong> | 0〜1 | **0 ＝ 非金属**（プラスチック・木・肌）、**1 ＝ 金属**。**中間は、錆びなど、境目**に使う |
| <strong>粗さ（roughness）</strong> | 0〜1 | **0 ＝ 鏡**、**1 ＝ ざらざら**（マット） |

### 金属と非金属

<svg class="fig" viewBox="0 0 600 220" role="img" aria-label="金属と非金属の光の振る舞い">
<defs><marker id="pd" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
<text x="20" y="22" class="fig-title">非金属（絶縁体）</text>
<rect x="20" y="110" width="250" height="70" fill="none" stroke="currentColor" stroke-width="2"/>
<line x1="60" y1="40" x2="120" y2="108" stroke="currentColor" stroke-width="2" marker-end="url(#pd)"/>
<line x1="120" y1="108" x2="180" y2="40" stroke="currentColor" stroke-width="2" marker-end="url(#pd)"/>
<text x="185" y="50">鏡面（白〜光の色。約 4%）</text>
<path d="M 120 108 L 150 150 L 190 128 L 235 108" fill="none" stroke="currentColor" stroke-width="2" stroke-dasharray="4 3" marker-end="url(#pd)"/>
<text x="30" y="205">内部で散乱して出る＝拡散（物体の色）</text>
<text x="320" y="22" class="fig-title">金属（導体）</text>
<rect x="320" y="110" width="250" height="70" fill="none" stroke="currentColor" stroke-width="2"/>
<line x1="360" y1="40" x2="420" y2="108" stroke="currentColor" stroke-width="2" marker-end="url(#pd)"/>
<line x1="420" y1="108" x2="480" y2="40" stroke="currentColor" stroke-width="2" marker-end="url(#pd)"/>
<text x="485" y="50">鏡面（金属の色）</text>
<text x="330" y="150">内部に入った光は、すぐ吸収される</text>
<text x="330" y="205">拡散なし。反射が、ほぼすべて</text>
</svg>

| | 非金属（metallic = 0） | 金属（metallic = 1） |
| --- | --- | --- |
| <strong>拡散（diffuse）</strong> | **あり**（ベースカラー） | **なし**（0） |
| <strong>鏡面の色（F0）</strong> | **約 0.04**（無色・白）。ほぼ全物質で同じ | **ベースカラー**（色付き） |
| **例** | プラスチック、木、石、肌、布、ゴム | 金、銅、鉄、アルミ |

### F0 と拡散色の計算

```hlsl
float3 f0 = lerp(float3(0.04f, 0.04f, 0.04f), base_color, metallic);
float3 diffuse_color = base_color * (1.0f - metallic);
```

| 材質 | F0（リニア） | 備考 |
| --- | --- | --- |
| 非金属（標準） | **0.04** | 水・プラスチック・ガラスは、約 0.02〜0.05 |
| 宝石（ダイヤモンド） | 0.17 | |
| 鉄 | (0.56, 0.57, 0.58) | |
| アルミ | (0.91, 0.92, 0.92) | |
| 金 | (1.00, 0.77, 0.34) | |
| 銅 | (0.95, 0.64, 0.54) | |

**金属度は、0 か 1 に近い値**にします（**中間の値は、錆びや汚れの境目**だけに、使います）。

### 材質のサンプル

<svg class="fig" viewBox="0 0 640 330" role="img" aria-label="metallic と roughness の見え方">
<defs>
<radialGradient id="d1" cx="35%" cy="30%" r="80%"><stop offset="0" stop-color="#5f8ff0"/><stop offset="0.7" stop-color="#2a4fa8"/><stop offset="1" stop-color="#101a3a"/></radialGradient>
<radialGradient id="h1" cx="35%" cy="30%" r="14%"><stop offset="0" stop-color="#ffffff" stop-opacity="1"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/></radialGradient>
<radialGradient id="h2" cx="35%" cy="30%" r="28%"><stop offset="0" stop-color="#ffffff" stop-opacity="0.8"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/></radialGradient>
<radialGradient id="h3" cx="35%" cy="30%" r="45%"><stop offset="0" stop-color="#ffffff" stop-opacity="0.5"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/></radialGradient>
<radialGradient id="h4" cx="35%" cy="30%" r="65%"><stop offset="0" stop-color="#ffffff" stop-opacity="0.28"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/></radialGradient>
<radialGradient id="m1" cx="35%" cy="30%" r="80%"><stop offset="0" stop-color="#6b5320"/><stop offset="1" stop-color="#0c0a05"/></radialGradient>
<radialGradient id="mh1" cx="35%" cy="30%" r="14%"><stop offset="0" stop-color="#ffe9a8" stop-opacity="1"/><stop offset="1" stop-color="#e6b84a" stop-opacity="0"/></radialGradient>
<radialGradient id="mh2" cx="35%" cy="30%" r="30%"><stop offset="0" stop-color="#f6d27a" stop-opacity="0.95"/><stop offset="1" stop-color="#e6b84a" stop-opacity="0"/></radialGradient>
<radialGradient id="mh3" cx="35%" cy="30%" r="55%"><stop offset="0" stop-color="#e8bd55" stop-opacity="0.85"/><stop offset="1" stop-color="#c8962c" stop-opacity="0"/></radialGradient>
<radialGradient id="mh4" cx="35%" cy="30%" r="85%"><stop offset="0" stop-color="#d9a63a" stop-opacity="0.8"/><stop offset="1" stop-color="#8a6a1c" stop-opacity="0.1"/></radialGradient>
</defs>
<text x="20" y="22" class="fig-title">上：非金属（metallic = 0）　下：金属（metallic = 1）　左 → 右：roughness 0.1 / 0.35 / 0.65 / 1.0</text>
<g>
<circle cx="90" cy="100" r="55" fill="url(#d1)"/><circle cx="90" cy="100" r="55" fill="url(#h1)"/>
<circle cx="245" cy="100" r="55" fill="url(#d1)"/><circle cx="245" cy="100" r="55" fill="url(#h2)"/>
<circle cx="400" cy="100" r="55" fill="url(#d1)"/><circle cx="400" cy="100" r="55" fill="url(#h3)"/>
<circle cx="555" cy="100" r="55" fill="url(#d1)"/><circle cx="555" cy="100" r="55" fill="url(#h4)"/>
<circle cx="90" cy="250" r="55" fill="url(#m1)"/><circle cx="90" cy="250" r="55" fill="url(#mh1)"/>
<circle cx="245" cy="250" r="55" fill="url(#m1)"/><circle cx="245" cy="250" r="55" fill="url(#mh2)"/>
<circle cx="400" cy="250" r="55" fill="url(#m1)"/><circle cx="400" cy="250" r="55" fill="url(#mh3)"/>
<circle cx="555" cy="250" r="55" fill="url(#m1)"/><circle cx="555" cy="250" r="55" fill="url(#mh4)"/>
</g>
<text x="40" y="322">小さく鋭い</text><text x="195" y="322">やや広い</text><text x="355" y="322">広くぼんやり</text><text x="500" y="322">ほぼ一面</text>
</svg>

## 直接光の計算（HLSL、DX11）

ここまでの式を、そのまま、HLSL にします。**ライトごとに、足し算**します。

```hlsl
static const float kPi = 3.14159265359f;

float DistributionGGX(float n_dot_h, float roughness) {
  float a = roughness * roughness;
  float a2 = a * a;
  float d = n_dot_h * n_dot_h * (a2 - 1.0f) + 1.0f;
  return a2 / (kPi * d * d);
}

float GeometrySchlickGGX(float n_dot_x, float roughness) {
  float r = roughness + 1.0f;
  float k = (r * r) / 8.0f;
  return n_dot_x / (n_dot_x * (1.0f - k) + k);
}

float GeometrySmith(float n_dot_v, float n_dot_l, float roughness) {
  return GeometrySchlickGGX(n_dot_v, roughness) * GeometrySchlickGGX(n_dot_l, roughness);
}

float3 FresnelSchlick(float h_dot_v, float3 f0) {
  return f0 + (1.0f - f0) * pow(1.0f - h_dot_v, 5.0f);
}

float3 DirectLight(float3 n, float3 v, float3 l, float3 radiance,
                   float3 albedo, float metallic, float roughness) {
  float3 h = normalize(v + l);
  float n_dot_l = max(dot(n, l), 0.0f);
  float n_dot_v = max(dot(n, v), 0.0001f);
  float n_dot_h = max(dot(n, h), 0.0f);
  float h_dot_v = max(dot(h, v), 0.0f);

  float3 f0 = lerp(float3(0.04f, 0.04f, 0.04f), albedo, metallic);

  float d = DistributionGGX(n_dot_h, roughness);
  float g = GeometrySmith(n_dot_v, n_dot_l, roughness);
  float3 f = FresnelSchlick(h_dot_v, f0);

  float3 specular = (d * g * f) / max(4.0f * n_dot_v * n_dot_l, 0.0001f);

  float3 k_d = (1.0f - f) * (1.0f - metallic);
  float3 diffuse = k_d * albedo / kPi;

  return (diffuse + specular) * radiance * n_dot_l;
}
```

| 注意 | 説明 |
| --- | --- |
| **`n_dot_v` に、最小値** | `0` になると、分母がゼロ割りになる |
| **roughness の下限** | **0.04 程度**にする（0 だと、ハイライトが、点になって消える） |
| **`radiance`** | ライトの色 × 強さ（ポイントライトは、距離の 2 乗で減衰させる） |
| **最後の `* n_dot_l`** | レンダリング方程式の `(N·ωi)` |

### ピクセルシェーダー

```hlsl
Texture2D albedo_map : register(t0);
Texture2D normal_map : register(t1);
Texture2D metal_rough_map : register(t2);
Texture2D ao_map : register(t3);
SamplerState linear_sampler : register(s0);

float4 PSMain(VsOutput input) : SV_TARGET {
  float3 albedo = albedo_map.Sample(linear_sampler, input.uv).rgb;
  float2 mr = metal_rough_map.Sample(linear_sampler, input.uv).bg;
  float metallic = mr.x;
  float roughness = max(mr.y, 0.04f);
  float ao = ao_map.Sample(linear_sampler, input.uv).r;

  float3 n = normalize(input.normal);
  float3 v = normalize(camera_position - input.world_position);

  float3 color = float3(0, 0, 0);
  for (int i = 0; i < light_count; ++i) {
    float3 l = normalize(-lights[i].direction);
    color += DirectLight(n, v, l, lights[i].color, albedo, metallic, roughness);
  }

  float3 ambient = AmbientIBL(n, v, albedo, metallic, roughness) * ao;
  color += ambient;

  return float4(color, 1.0f);
}
```

## 間接光（IBL）

**ライトの直接光だけ**では、**金属は、ほぼ真っ黒**になります（拡散がなく、反射する相手が、光源だけ）。実際の金属は、**空や周囲の景色**を映すので、**周囲全体からの光**を、考えます。これが**IBL**（Image Based Lighting、画像ベースのライティング）です。

**環境マップ**（キューブマップ。**周囲 360° の景色の画像**）を、**光源**として扱います。レンダリング方程式の積分は、重いので、**事前に計算**しておきます。

<div class="anim" data-type="graph" data-label="IBL：重い積分を、事前計算して、テクスチャにしておく">
n env 環境マップ_（周囲の景色） 0 1 hit
---
n env 環境マップ_（周囲の景色） 0 1
n irr 拡散用_irradiance マップ 1 0 new
n pre 鏡面用_プリフィルタ マップ 1 1 new
n lut BRDF_LUT 1 2 new
l env irr hit 半球で積分
l env pre hit 粗さごとにぼかす
---
n env 環境マップ_（周囲の景色） 0 1 dim
n irr 拡散用_irradiance マップ 1 0
n pre 鏡面用_プリフィルタ マップ 1 1
n lut BRDF_LUT 1 2
n px ピクセル 2 1 new
l irr px hit 法線で引く
l pre px hit 反射方向で引く
l lut px hit 粗さ・角度で引く
</div>

### 拡散の間接光（irradiance マップ）

**法線方向の半球**から来る光を、**あらかじめ平均**（積分）して、**小さなキューブマップ**（32×32 程度）に保存します。**法線で引く**だけで、その向きの、**拡散の環境光**が分かります。<strong>球面調和関数（SH）</strong>で、9 個の係数に、圧縮する方法もあります。

### 鏡面の間接光（split-sum 近似）

鏡面は、**積分が、視線に依存**するので、さらに**2 つに分けて**、事前計算します（**split-sum 近似**、Epic Games）。

<div class="formula">鏡面の間接光 ≈ prefiltered(R, roughness) × ( F0 · A + B )</div>

| 部分 | 事前計算 | 引き方 |
| --- | --- | --- |
| <strong>prefiltered(R, roughness)</strong> | 環境マップを、**粗さごとに、ぼかして**、**ミップマップの各段**に保存 | **反射方向 R** と、**粗さ**（ミップのレベル）で引く |
| **A, B**（BRDF LUT） | <strong>視線角度 (N·V)</strong> と **粗さ**から、**F0 の係数**を求めた、**2D テクスチャ** | `(N·V, roughness)` で引く（**材質に依らず、1 枚でよい**） |

```hlsl
TextureCube irradiance_map : register(t4);
TextureCube prefilter_map : register(t5);
Texture2D brdf_lut : register(t6);

float3 AmbientIBL(float3 n, float3 v, float3 albedo, float metallic, float roughness) {
  float n_dot_v = max(dot(n, v), 0.0001f);
  float3 f0 = lerp(float3(0.04f, 0.04f, 0.04f), albedo, metallic);

  float3 k_s = f0 + (max(1.0f - roughness, f0) - f0) * pow(1.0f - n_dot_v, 5.0f);
  float3 k_d = (1.0f - k_s) * (1.0f - metallic);

  float3 diffuse = irradiance_map.Sample(linear_sampler, n).rgb * albedo * k_d;

  float3 r = reflect(-v, n);
  const float kMaxMip = 4.0f;
  float3 prefiltered = prefilter_map.SampleLevel(linear_sampler, r, roughness * kMaxMip).rgb;
  float2 brdf = brdf_lut.Sample(linear_sampler, float2(n_dot_v, roughness)).rg;
  float3 specular = prefiltered * (f0 * brdf.x + brdf.y);

  return diffuse + specular;
}
```

| 注意 | 説明 |
| --- | --- |
| **環境マップは HDR** | `DXGI_FORMAT_R16G16B16A16_FLOAT`。太陽の明るさは、1 を大きく超える |
| **BRDF LUT** | 起動時に生成（またはファイルから）。<strong>2 チャンネル（R16G16）</strong> |
| <strong>作るのは、ビルド時（ツール）</strong> | 実行時にやると重い。**cmgen・IBLBaker・自作のツール**で、事前に |
| <strong>AO（アンビエント オクルージョン）</strong> | 間接光を、**凹みで暗くする**。`ao_map` を、間接光だけに掛ける |

## 色空間とトーンマッピング

PBR は、**物理的な光の量**を、足し算するので、**リニア空間**で計算します。

| 項目 | 説明 |
| --- | --- |
| <strong>色のテクスチャ（albedo、emissive）</strong> | **sRGB**（ガンマ付き）で保存されている。**`_SRGB` フォーマット**で読めば、読み込み時に**リニアへ自動変換** |
| <strong>データのテクスチャ（法線、metallic、roughness、AO）</strong> | **リニア**。**sRGB にしない** |
| **計算** | **すべて、リニア空間** |
| **HDR の値** | 光の量は、**1 を超えて**よい（太陽は 100 以上など） |
| **トーンマッピング** | **HDR の値を、0〜1 の画面の範囲に**収める。**Reinhard**、**ACES** など |
| **ガンマ補正** | 最後に、**sRGB へ**（レンダーターゲットが `_SRGB` なら自動） |

```hlsl
float3 ToneMapReinhard(float3 c, float exposure) {
  c *= exposure;
  return c / (1.0f + c);
}
```

**トーンマッピングを忘れる**と、**明るい所が真っ白に飛び**、見た目が、きつくなります。

## テクスチャセット

PBR の材質は、**複数のテクスチャ**で与えます。

| テクスチャ | 内容 | 色空間 |
| --- | --- | --- |
| <strong>ベースカラー（albedo）</strong> | 拡散色 / 金属の色。**影・光の情報を含めない** | **sRGB** |
| **法線マップ** | 細かな凹凸（[法線マップ](lighting-normals.md)） | リニア |
| **メタリック・ラフネス** | glTF では、**G ＝ roughness、B ＝ metallic** | リニア |
| <strong>AO（オクルージョン）</strong> | 凹みの暗さ。glTF では、**R** | リニア |
| **エミッシブ** | 自己発光 | sRGB |

!!! warning "テクスチャに、光の情報を焼き込まない"
    ベースカラーに、**影や、ハイライトを描き込む**と、PBR のライトと**二重**になり、不自然になります。**光は、ライトに任せる**のが、PBR の約束です。

## DX11 での実装の流れ

| 手順 | 内容 |
| --- | --- |
| **1. 定数バッファ** | カメラ位置、ライト（方向・色・強さ）、材質のスカラー（metallic・roughness の倍率） |
| <strong>2. テクスチャ（SRV）</strong> | albedo（`_SRGB`）・法線・metallic-roughness・AO を `PSSetShaderResources` |
| **3. IBL 用リソース** | irradiance・prefilter（キューブマップ）・BRDF LUT を、スロットに設定 |
| **4. サンプラー** | `MIN_MAG_MIP_LINEAR` + 異方性（[メッシュとテクスチャ](mesh-textures.md)） |
| **5. 描画先は HDR** | `R16G16B16A16_FLOAT` に描いて、最後に、**トーンマップ**してバックバッファへ |
| **6. 頂点にタンジェント** | 法線マップに必要（[メッシュとテクスチャ](mesh-textures.md)） |

```cpp
struct LightCB {
  Vector3 direction;
  float intensity;
  Vector3 color;
  float pad;
};

struct MaterialCB {
  Vector4 base_color_factor;
  float metallic_factor;
  float roughness_factor;
  Vector2 pad;
};
```

## ブリン・フォンとの違い

| | ブリン・フォン | PBR |
| --- | --- | --- |
| **材質の数字** | 拡散色・鏡面色・光沢（見た目任せ） | **ベースカラー・金属度・粗さ**（物理的な意味） |
| **ハイライトの形** | `pow(N·H, 光沢)` | **GGX**（すそが長い） |
| **角度による反射** | なし | **フレネル**（浅い角度で強い） |
| **エネルギー保存** | **なし** | **あり** |
| **金属** | 工夫が必要 | **metallic = 1** で |
| **環境光** | 一定の色 | **IBL**（周囲の景色） |
| **計算量** | 軽い | **重め**（ピクセルごとに、多くの計算） |
| **向いている** | 古い・軽い描画、スタイライズ | **写実的な描画、多くの照明条件** |

## よくあるミス

??? failure "金属が、真っ黒になる"
    **間接光（IBL）がありません**。金属は、周囲を映すので、環境マップが必要です。

??? failure "色が、白っぽく・暗く見える"
    **ガンマ（sRGB）の扱い**が、間違っています。albedo は `_SRGB`、**法線・metallic・roughness は、リニア**。最後に、**トーンマッピング**します。

??? failure "非金属なのに、ハイライトが、色付きになる"
    `F0` を、ベースカラーにしています。**非金属は、0.04 の無色**です（`lerp(0.04, albedo, metallic)`）。

??? failure "roughness を 0 にして、ハイライトが消える・NaN になる"
    <strong>下限（0.04 程度）</strong>を設けます。分母のゼロ割りも、`max(..., 0.0001)` で避けます。

??? failure "metallic が、0.5 などの中間値ばかり"
    現実の材質には、ほぼ**中間がありません**。**0 か 1** にします（境目だけ、中間）。

??? failure "albedo テクスチャに、影が描き込んである"
    ライトと**二重**になります。**光の情報を、除いた**テクスチャにします。

??? failure "法線マップの Y が逆で、凹凸が反転する"
    **DirectX 系と OpenGL 系**で、**Y（緑）の向きが逆**です。モデルのツールの設定を、確認します。

??? failure "パラメータを、見た目で、ライトごとに調整している"
    PBR の目的に反します。**材質は、物理の値**にして、**ライトの強さ・色**で、調整します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] PBR の核は、<strong>エネルギー保存・マイクロファセット・フレネル</strong>
    - [x] 材質は<strong>ベースカラー・金属度・粗さ</strong>。<strong>非金属の F0 ＝ 0.04</strong>、<strong>金属は、拡散なし・F0 ＝ベースカラー</strong>
    - [x] 反射は <strong>Cook-Torrance：D（GGX）× G（Smith）× F（Schlick）÷ 4(N·L)(N·V)</strong> ＋ <strong>ランバート（albedo / π）</strong>
    - [x] <strong>直接光はライトごとの足し算</strong>、<strong>間接光は IBL</strong>（irradiance・prefilter・BRDF LUT）
    - [x] <strong>リニア空間で計算</strong>し、<strong>トーンマッピング + ガンマ補正</strong>。<strong>色は sRGB、それ以外はリニア</strong>
    - [x] <strong>roughness の下限、ゼロ割りの回避、法線の Y の向き</strong>に注意

## 関連ページ

- [3D ゲーム（目次）](index.md)
- [法線とライティング](lighting-normals.md)
- [メッシュとテクスチャ](mesh-textures.md)
- [変換と MVP](transforms-mvp.md)
- [深度とカリング](depth-culling.md)
