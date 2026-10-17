---
title: ボケの形
tags:
  - 描画
---

# ボケの形

<strong>ボケの「形」</strong>は、<strong>写真・映画の「味」</strong>を**決める**大切な要素です。**実際のレンズでは、絞りの羽根の枚数でボケの円が多角形になり**、**レンズの設計で縁が明るかったり、中心が明るかったり**します。**ゲームの DOF でも、サンプルの配置・重み付けでこの形を作り分けられます**。このページでは、**円・多角形・ボケの明るさの分布・猫の目（口径食）・サンプル配置・ブルーム的な玉ボケ**を説明します。

!!! tip "ポイント"
    - ボケの形 ＝ <strong>レンズの絞りの形</strong>。<strong>円・五角形・六角形（羽根の枚数）</strong>。
    - <strong>サンプルの配置と重み</strong>で<strong>形を作る</strong>。<strong>円盤は螺旋、多角形は辺に沿って配置</strong>。
    - <strong>ボケの中の明るさ</strong>：<strong>均一・縁が明るい（リング状）・中心が明るい</strong>。<strong>レンズの個性</strong>。
    - <strong>口径食（猫の目）</strong>：<strong>画面の端でボケが楕円に欠ける</strong>。<strong>映画的な味</strong>。
    - <strong>明るい点</strong>ほど<strong>形がはっきり見える</strong>。<strong>HDR で処理</strong>する。
    - <strong>形を凝るほど、サンプル数が増える</strong>。<strong>コストと相談</strong>。

## 形の種類

<svg class="fig illust" viewBox="0 0 780 220" role="img" aria-label="ボケの形">
<text x="20" y="26" class="fig-title">ボケの形：絞り羽根の枚数で決まる</text>
<g fill="#fff7d1" stroke="#f59e0b" stroke-width="3">
<circle cx="110" cy="120" r="56"/>
<polygon points="300,64 354,103 333,166 267,166 246,103"/>
<polygon points="520,64 568,92 568,148 520,176 472,148 472,92"/>
<polygon points="690,64 730,80 750,120 730,160 690,176 650,160 630,120 650,80"/>
</g>
<g font-size="12" text-anchor="middle"><text x="110" y="204">円（羽根が丸い）</text><text x="300" y="204">五角形</text><text x="520" y="204">六角形</text><text x="690" y="204">八角形</text></g>
</svg>

| 形 | 由来 | 見た目 |
| --- | --- | --- |
| **円** | **丸い絞り・多枚羽根** | **滑らか・柔らかい** |
| **多角形** | **5〜9 枚の絞り羽根を絞った状態** | **角張った玉ボケ。写真っぽい** |
| <strong>ドーナツ（リング）</strong> | **反射望遠レンズ** | **中央が欠けた、輪っかのボケ** |

## サンプルの配置で形を作る

### 円盤

**ヴォーゲル螺旋**（[ギャザー方式](gather.md)）が**そのまま円盤**を**作ります**。

### 多角形

**円盤を多角形の領域に押し込む**関数で**サンプルを写します**。

```hlsl
float2 MapDiskToPolygon(float2 p, int sides, float rotation) {
  float r = length(p);
  float angle = atan2(p.y, p.x);
  float sector = 6.28318530718 / sides;
  float local = fmod(angle - rotation + sector * 100.0, sector) - sector * 0.5;
  float polygon_radius = cos(sector * 0.5) / cos(local);
  return p * polygon_radius;
}
```

| 点 | 説明 |
| --- | --- |
| **`sides`** | **羽根の枚数**（**5〜9**） |
| **`rotation`** | **多角形の向き** |
| **`cos(半角) / cos(局所角)`** | **円の半径を多角形の辺までの距離に置き換える** |
| **サンプルをこの関数で円盤から多角形に写す** | **ギャザーのサンプル位置**として使う |

## ボケの中の明るさ

**実際のレンズ**では、**ボケの円盤の内側が均一ではありません**。

| 明るさの分布 | レンズの性質 | 見た目 |
| --- | --- | --- |
| **均一** | **理想的な絞り** | **平らな円盤** |
| **縁が明るい** | <strong>球面収差の補正不足（古い・安いレンズ）</strong> | **縁取りのある玉ボケ。ソープ バブル風** |
| **中心が明るい** | **球面収差の過剰補正** | **柔らかい、なだらかなボケ** |

**サンプルの重みに円の中心からの距離を反映**すると、**この分布を作れます**。

```hlsl
float BokehWeight(float2 sample_offset, float edge_boost) {
  float r = length(sample_offset);
  return lerp(1.0, 1.0 + edge_boost, smoothstep(0.6, 1.0, r));
}
```

| `edge_boost` | 見た目 |
| --- | --- |
| **0** | **均一な円盤** |
| **> 0** | <strong>縁が明るい（ソープ バブル）</strong> |
| <strong>< 0</strong> | **中心が明るい** |

<!-- fig:bokeh-shapes-anim:begin -->
<!-- fig:bokeh-shapes-anim:end -->

## 口径食（猫の目ボケ）

**画面の端**では**レンズの筒の影響でボケが丸くなく、楕円形（猫の目）に欠ける**ことがあります。**映画的な味**として**人気**があります。

| 工夫 | 内容 |
| --- | --- |
| **画面中心からの距離で円を欠く** | **端のサンプルを画面中心に向かって、もう 1 つの円との交差領域に限定** |
| **向き** | **欠けた円の向きは、画面中心の方向に揃う** |

```hlsl
float2 ApplyCatEye(float2 offset_in_disk, float2 screen_uv, float strength) {
  float2 from_center = screen_uv - 0.5;
  float distance_from_center = length(from_center);
  float2 axis = from_center / max(distance_from_center, 1e-4);
  float shift = distance_from_center * strength;
  float2 other_center = axis * shift;
  bool inside_other = length(offset_in_disk - other_center) <= 1.0;
  return inside_other ? offset_in_disk : float2(10000.0, 10000.0);
}
```

<strong>欠けたサンプルは使わず（重み 0 に）</strong>、**残りのサンプル数で割り直す**必要があります。

## 玉ボケをブルームと兼ねる

**明るい点が大きなボケの円盤になる**ので、**ブルームと DOF の見た目は近い**です。**重複して、ぼけすぎないよう**：

| 工夫 | 内容 |
| --- | --- |
| **DOF の後にブルーム** | **DOF でぼけた玉ボケを、ブルームでさらに柔らかく** |
| **ブルームのしきい値を調整** | **DOF で広がって薄くなった光は、しきい値を超えにくい** |
| **玉ボケの明るさを保つ** | **スキャッター方式なら、面積で割りつつ、HDR の明るさを残す** |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **形をパラメータにする** | **羽根の枚数・回転・縁の明るさ・猫の目の強さをスライダー**に |
| **サンプル配置を事前計算** | **多角形・形ごとにサンプルを事前に作り、定数バッファへ** |
| **ブルー ノイズで回転** | **少ないサンプルで滑らかに** |
| **ボケの小さい所は円で十分** | **形が見えるのは、大きな明るいボケだけ**。**そこだけ凝る** |
| **スキャッターで形を正確に** | **玉ボケの形を重視するなら、スプライトに形のテクスチャを貼る**（[スキャッター方式](scatter.md)） |

## よくあるミス

??? failure "多角形のボケにしたら、サンプルが偏って、片側が薄い"
    **サンプルを多角形の中に均等に**配置する。**重みをサンプル数で正規化**。

??? failure "猫の目で欠けたサンプルを使い続け、暗くなる"
    **欠けたサンプルの重みを 0 に、合計の重みで割る**。

??? failure "ボケの形が、小さい画素ではまったく見えない"
    **形が見えるのは、大きなボケだけ**。**小さいボケは円で十分**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ボケの形 ＝ <strong>絞りの形</strong>。<strong>円・多角形（羽根の枚数）</strong>
    - [x] <strong>サンプルの配置・重み</strong>で<strong>形と明るさの分布</strong>を作る
    - [x] <strong>縁が明るい・中心が明るい</strong>など<strong>レンズの個性</strong>
    - [x] <strong>猫の目（口径食）</strong>は<strong>画面の端でボケが楕円に欠ける</strong>
    - [x] <strong>形はパラメータ化</strong>し、<strong>大きなボケだけ凝る</strong>

## 参考

- McIntosh et al., "Efficiently Simulating the Bokeh of Polygonal Apertures in a Post-Process Depth of Field Shader"（Computer Graphics Forum 2012）
- Abadie, "A Life of a Bokeh"（SIGGRAPH 2018）
- Wikipedia, "Bokeh"

## 関連ページ

- [被写界深度（DOF）](index.md)
- [ギャザー方式](gather.md)
- [スキャッター方式](scatter.md)
- [ブルーム](../bloom/index.md)
