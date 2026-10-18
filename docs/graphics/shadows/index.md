---
title: Shadows
tags:
  - 描画
---

# Shadows

影は<strong>「光源から見えない場所」</strong>です。物体の位置関係を伝え、画面に**奥行きと現実感**を与えます。ライトの計算（明るさ）は、**面の向きと光の向き**から**局所的**に決まりますが、**影は他の物体に遮られるか**という**大域的な情報**が要ります。「その点から光源へ遮るものがあるか」を、**どう安く調べるか**が影の手法の中心です。このセクションでは、**シャドウ マップを中心に**、**バイアス・フィルタ・カスケード・ソフト シャドウ・レイトレ**まで方式ごとに**原理から**説明します。

## Page List {#ページ一覧}

| ページ | 内容 |
| --- | --- |
| [Shadow Map Basics](shadow-map-basics/index.md) | 光から見た深度を撮り、比べる。行列・サンプラー・手順 |
| [Shadow Bias](bias/index.md) | シャドウ アクネ・ピーター パンニング。定数・スロープ・法線オフセット・受け手平面 |
| [PCF](pcf.md) | 周りの複数点を比べて平均する、縁のぼかし |
| [PCSS](pcss.md) | 遮蔽物との距離で縁のぼけを変える（接触は鋭く、離れるとソフト） |
| [VSM, ESM and MSM](vsm/index.md) | 深度のモーメントを保存して、フィルタできる影 |
| [Cascaded Shadow Maps (CSM)](cascaded.md) | 距離ごとに分割して、近くを細かく。屋外の標準 |
| [Point and Spot Light Shadows](local-lights/index.md) | キューブマップ・アトラス・解像度の割り当て |
| [Contact Shadows](contact-shadows.md) | 画面空間で細かい接触の影を補う |
| [Distance Field Shadows](sdf-shadows.md) | 符号付き距離場の円錐トレースで、ソフトな影 |
| [Ray-Traced Shadows](ray-traced.md) | レイで正確な影・面光源のソフトな影 |
| [Virtual Shadow Maps](virtual-shadow-maps.md) | 巨大な仮想テクスチャ。画面の 1 ピクセルに 1 テクセル |
| [Shadow Volumes](shadow-volumes.md) | ステンシルで影の領域を直接数える古典的な方式 |
| [Special Cases](special-cases/index.md) | アルファ テスト・半透明・植物・キャラクター・フェード |
| [方式の比較](comparison.md) | 原理・品質・コストの一覧と選び方 |

## Kinds of Shadows {#影の種類}

| 種類 | 説明 |
| --- | --- |
| **ハード シャドウ** | 影と日向の境が**くっきり**。点光源・太陽（の近似）で、境界が鋭い |
| **ソフト シャドウ** | 境界が**ぼけている**（**半影・ペナンブラ**）。**光源に大きさがある**ため |
| **接触硬化** | **遮蔽物に近いほど鋭く**、**離れるほどぼける**（現実の影の性質） |
| **自己影** | 物体が**自分自身**に落とす影 |
| **間接光の影** | 間接光を遮る→ AO や GI の領域（[AO](../ao/index.md)） |

### Why Penumbrae Exist {#半影ができる理由}

**光源に大きさ**があると**物体の後ろのある点**から光源を見たとき、**光源の一部だけが隠れる**ことがあります。**全部が隠れる所**が<strong>本影（アンブラ）</strong>、**一部が隠れる所**が<strong>半影（ペナンブラ）</strong>です。**遮蔽物から離れるほど、半影が広く**なります。

<svg class="fig illust" viewBox="0 0 780 280" role="img" aria-label="本影と半影">
<text x="20" y="24" class="fig-title">面光源が作る影：本影（完全に暗い）と半影（部分的に暗い）</text>
<rect x="60" y="50" width="160" height="22" fill="rgba(229,170,40,0.6)" stroke="currentColor" stroke-width="2"/><text x="82" y="46" style="font-size:12px">面光源（大きさがある）</text>
<rect x="110" y="130" width="60" height="22" fill="rgba(150,150,150,0.7)" stroke="currentColor" stroke-width="2"/><text x="176" y="146" style="font-size:12px">遮蔽物</text>
<line x1="60" y1="72" x2="410" y2="240" stroke="currentColor" stroke-dasharray="4 3"/><line x1="220" y1="72" x2="30" y2="240" stroke="currentColor" stroke-dasharray="4 3"/>
<line x1="60" y1="72" x2="30" y2="240" stroke="currentColor" stroke-dasharray="4 3" opacity="0.4"/><line x1="220" y1="72" x2="410" y2="240" stroke="currentColor" stroke-dasharray="4 3" opacity="0.4"/>
<line x1="20" y1="240" x2="500" y2="240" stroke="currentColor" stroke-width="4"/>
<rect x="190" y="236" width="40" height="8" fill="#111" opacity="0.9"/><text x="168" y="266" style="font-size:12px;font-weight:700">本影</text>
<rect x="120" y="236" width="70" height="8" fill="#555" opacity="0.6"/><rect x="230" y="236" width="70" height="8" fill="#555" opacity="0.6"/><text x="70" y="266" style="font-size:12px">半影</text><text x="262" y="266" style="font-size:12px">半影</text>
<text x="540" y="100" style="font-weight:700">光源が大きい・遮蔽物から遠いほど</text>
<text x="540" y="124" style="font-weight:700">半影が広い</text>
<text x="520" y="160" style="font-size:12px">→ 接地部はくっきり（接触硬化）</text>
<text x="540" y="180" style="font-size:12px">→ 離れた所の影は、ぼんやり</text>
</svg>

ゲームの**太陽**も**空の上で大きさ**（視直径は約 0.5 度）を持つので**遠くの影**ほど、**わずかにぼけます**。この**物理的な振る舞い**を、**どの程度まじめに再現するか**が、方式ごとの差になります。

## How to Get Shadows: Three Main Families {#影の求め方大きく-3-系統}

| 系統 | 方式 | 考え方 |
| --- | --- | --- |
| **深度を比べる**（画像ベース） | **シャドウ マップ**・VSM・CSM・仮想シャドウ マップ | 光から見た**深度の画像**と、比べる |
| **幾何を直接使う** | **シャドウ ボリューム** | 影の**領域そのもの**をジオメトリで作り、ステンシルで数える |
| **レイで調べる** | **レイトレース影**・**距離場の影** | 光源へ**レイを飛ばして**、遮蔽を直接調べる |

**ほとんどのゲームは、シャドウ マップ系**です。**レイトレ**は**対応 GPU で高品質な影**として加わります。

## Applying Shadows {#影の適用}

**影は直接光だけ**に掛けます。**間接光（環境光）には掛けません**（AO・GI の領域）。

```hlsl
float shadow = SampleShadow(world_pos, normal);
float3 direct = albedo * light_color * saturate(dot(N, L)) * shadow;
float3 ambient = albedo * irradiance * ao;
float3 color = direct + ambient;
```

コードの要点です。`shadow` は、0（影）から 1（日向）の可視性です。影は、影を落とすライトごとに計算が必要です。そして、影は直接光にだけ掛けます。間接光には掛けません。影の中でも空の光（環境光）は届くからです。

## Conditions for Good Shadows {#良い影の条件}

| 条件 | 内容 |
| --- | --- |
| **位置が合っている** | 影が物体に**接している**（浮かない・ずれない） |
| **縁が自然** | ギザギザ（エイリアシング）がない。適度にソフト |
| **自己影が破綻しない** | 平らな面に縞（アクネ）がない |
| **全距離で適切な解像度** | 近くも遠くも**画面で同じ細かさ**に見える |
| **コストが見合う** | 影の描画は**シーンの再描画**。**ドロー コール・頂点・メモリ**を使う |

## Cost of Shadows (Overview) {#影のコスト概観}

| 項目 | コスト |
| --- | --- |
| **シャドウ マップの描画** | **シーンを光から見て再描画**。ジオメトリ処理が主（[影のコスト](../../rendering/shadows.md)） |
| **メモリ** | シャドウ マップの解像度 × 枚数（2048² を、4 枚で数十 MB） |
| **サンプリング** | **画素ごと**にシャドウ マップを複数回読む（PCF） |
| **カスケード・ライト数** | 枚数に比例 |

**描画コストの減らし方**は、[描画最適化の「影のコスト」](../../rendering/shadows.md)にまとめています。**このセクションは、手法の原理と品質**を扱います。

## Related Pages {#関連ページ}

- [描画](../index.md)
- [Shadow Map Basics](shadow-map-basics/index.md)
- [影のコスト（最適化）](../../rendering/shadows.md)
- [法線とライティング](../../3d/lighting-normals.md)
- [Ambient Occlusion (AO)](../ao/index.md)
