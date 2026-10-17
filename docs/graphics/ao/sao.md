---
title: SAO（Scalable AO）
tags:
  - 描画
---

# SAO（Scalable AO）

**SAO**（Scalable Ambient Obscurance）は、2012 年に McGuire らが発表した方式です。[Alchemy AO](alchemy-ao.md)の**式はそのまま**に**メモリ アクセスと実装を徹底的に最適化**しました。最大の改良は**深度バッファのミップ マップ**を作って、**遠いサンプルは、粗いミップから読む**ことです。これで**半径をいくら大きくしても、実行時間がほぼ一定**になります（スケーラブル）。論文では、**2560×1600 で、Alchemy の約 7 倍速**と報告されています。

!!! tip "ポイント"
    - 式は <strong>Alchemy AO と同じ</strong>。<strong>変わったのは深度の読み方</strong>。
    - <strong>線形深度のミップ チェーン</strong>を作る。<strong>サンプルが遠いほど、粗いミップ</strong>を読む → <strong>キャッシュに乗り、半径に依存しない速さ</strong>。
    - ミップの作り方は<strong>平均ではなく、代表の 1 点を選ぶ</strong>（境界で嘘の深度ができるのを防ぐ）。
    - 深度だけから、位置と法線を<strong>高精度に復元</strong>する。<strong>G-Buffer 不要</strong>。
    - <strong>後の多くの SSAO 実装に影響</strong>した方式（深度のミップ・キャッシュを意識した設計）。

## 問題：半径が大きいとなぜ遅いか

Alchemy AO は、**画面上の螺旋**でサンプルを置きます。**半径 R が大きい**とサンプルは**画面上で遠く**に散ります。深度テクスチャの**離れた位置を、バラバラに読む**ので**テクスチャ キャッシュが効かず**、メモリ アクセスが**遅く**なります。

| 半径 | サンプルの散らばり | キャッシュ |
| --- | --- | --- |
| 小さい | 近くにまとまる | 効く |
| **大きい** | **画面全体に散る** | <strong>効かない（遅い）</strong> |

## 解決：深度のミップ マップ

**深度テクスチャのミップ チェーン**を作ります。**遠くのサンプルは、粗いミップ**から読みます。**粗いミップは小さい**ので、**キャッシュに収まり**、**散らばっても速い**のです。

<svg class="fig illust" viewBox="0 0 760 270" role="img" aria-label="深度のミップとサンプル">
<text x="20" y="24" class="fig-title">近いサンプルは細かい深度（ミップ 0）、遠いサンプルは粗い深度（ミップが大きい）から読む</text>
<rect x="40" y="60" width="200" height="160" fill="rgba(76,139,245,0.2)" stroke="currentColor" stroke-width="2"/><text x="60" y="52" style="font-size:12px">ミップ 0（フル解像度）</text>
<rect x="270" y="90" width="100" height="100" fill="rgba(46,160,67,0.25)" stroke="currentColor" stroke-width="2"/><text x="272" y="82" style="font-size:12px">ミップ 1</text>
<rect x="400" y="110" width="50" height="60" fill="rgba(229,170,40,0.3)" stroke="currentColor" stroke-width="2"/><text x="400" y="102" style="font-size:12px">ミップ 2</text>
<rect x="480" y="125" width="25" height="30" fill="rgba(229,72,77,0.3)" stroke="currentColor" stroke-width="2"/><text x="470" y="117" style="font-size:12px">ミップ 3</text>
<circle cx="140" cy="140" r="6" fill="currentColor"/><text x="120" y="168" style="font-size:12px">p</text>
<g fill="#4c8bf5"><circle cx="150" cy="130" r="4"/><circle cx="125" cy="150" r="4"/><circle cx="160" cy="155" r="4"/></g>
<g fill="#2ea043"><circle cx="190" cy="120" r="4"/><circle cx="100" cy="95" r="4"/></g>
<g fill="#e5a828"><circle cx="215" cy="185" r="4"/></g>
<text x="560" y="90" style="font-size:13px">近いサンプル → ミップ 0</text>
<text x="560" y="115" style="font-size:13px">中くらい → ミップ 1</text>
<text x="560" y="140" style="font-size:13px">遠い → ミップ 2・3</text>
<text x="20" y="250" style="font-size:12px">遠くのサンプルは、細かい位置の精度が不要なので、粗いミップで十分。小さいテクスチャを読むので、キャッシュに収まり速い</text>
</svg>

### どのミップから読むか

**画面上のサンプルまでの距離**（ピクセル）に応じて、ミップを選びます。

<div class="formula">m = clamp( ⌊log₂(距離)⌋ − 定数, 0, 最大ミップ )</div>

参照実装（G3D）ではこの**定数**（`LOG_MAX_OFFSET`）が 3 です。**距離が 8 ピクセル以内ならミップ 0**、16 ピクセルまでミップ 1、…と**距離が 2 倍になるごとに、ミップが 1 つ上がります**。

```hlsl
int MipLevel(float screen_distance) {
  return clamp(int(floor(log2(screen_distance))) - kLogMaxOffset, 0, kMaxMip);
}

float3 SamplePosition(float2 uv, int mip) {
  float z = z_mip_tex.SampleLevel(point_sampler, uv, mip).r;
  return ViewPositionFromLinearZ(uv, z);
}
```

## ミップの作り方：平均してはいけない

深度のミップは、**普通のミップ（4 画素の平均）で作ってはいけません**。**物体の境界**で**手前の画素と奥の画素を平均**すると、**どちらにも存在しない、中間の深度**ができます。この**嘘の深度**が、AO で**幽霊のような遮蔽**を作ります。

| 作り方 | 結果 |
| --- | --- |
| **平均** | 境界で**存在しない深度**ができる（NG） |
| **代表の 1 画素を選ぶ**（例：4 画素のうち、決まった位置の 1 つ） | **実在する深度**だけが残る（SAO の方式） |
| <strong>最小値（最も手前）</strong> | 保守的（遮蔽を多めに見る）。手前の細い物が太く見える |
| <strong>最大値（最も奥）</strong> | 逆に遮蔽を少なめに見る |

SAO は**代表の 1 点を選ぶ**方式（ポイント サンプリングで縮小）を使います。**1 パスで各ミップを計算**します。

```hlsl
float MipDown(float2 uv_in_src) {
  return src_tex.Load(int3(2 * pixel, src_mip)).r;
}
```

## 位置と法線を深度から復元する

SAO は、**G-Buffer の法線を使いません**。**深度だけ**から、位置と法線を復元します。

| 項目 | 方法 |
| --- | --- |
| **位置** | 線形深度 z から、`x = ndc_x · z · tanX`、`y = ndc_y · z · tanY`（[Crytek SSAO](ssao-crytek.md)） |
| **法線** | **隣の画素の位置**との差の外積。**深度の差が小さい側**（左右・上下）を選んで**エッジをまたがない** |
| **精度** | 深度は、**32 ビットの浮動小数点**または、**2 チャンネルに分けて**（上位・下位）、高精度で保存。位置の**誤差が、AO の縞になる**ため |

```hlsl
float3 ReconstructNormal(int2 pixel, float3 c) {
  float3 px = Position(pixel + int2(1, 0));
  float3 nx = Position(pixel + int2(-1, 0));
  float3 py = Position(pixel + int2(0, 1));
  float3 ny = Position(pixel + int2(0, -1));

  float3 dx = abs(px.z - c.z) < abs(nx.z - c.z) ? px - c : c - nx;
  float3 dy = abs(py.z - c.z) < abs(ny.z - c.z) ? py - c : c - ny;
  return normalize(cross(dx, dy));
}
```

## 処理の流れ

| パス | 内容 |
| --- | --- |
| **① 線形深度 ＋ ミップ** | 深度バッファを**線形深度**に変換して、**ミップ チェーン**を作る |
| **② AO の計算** | 各画素で**螺旋のサンプル**を**距離に応じたミップから読み**、Alchemy の式で足す |
| <strong>③ バイラテラル ブラー（横）</strong> | **深度を使って、境界をまたがないぼかし** |
| <strong>④ バイラテラル ブラー（縦）</strong> | 同様 |
| **⑤ 合成** | **間接光に掛ける** |

論文では、AO の結果と**深度を、1 枚のテクスチャに詰めて**（AO・深度を、2 チャンネル ずつなど）、**ブラー パスの読み込み回数を減らす**工夫もしています。

## 性能の特徴

| 特徴 | 説明 |
| --- | --- |
| **半径に依存しない** | 遠くのサンプルを粗いミップで読むので、**半径を大きくしてもコストはほぼ一定** |
| **サンプル数に比例** | サンプル数 s が増えれば、遅くなる（9〜13 個が目安） |
| **解像度に比例** | 画素数に比例する。**半分の解像度**でさらに軽く（[低解像度のエフェクト](../../rendering/low-res-effects.md)） |
| **ブラーのコスト** | 分離可能なので小さい |

## Alchemy AO との比較

| 項目 | Alchemy AO | SAO |
| --- | --- | --- |
| **AO の式** | 同じ | **同じ** |
| **深度の読み方** | **常にミップ 0** | **距離に応じて、粗いミップ** |
| **半径とコスト** | 大きいと遅い | **ほぼ一定** |
| **法線** | 必要（G-Buffer か復元） | **深度から高精度に復元**（G-Buffer 不要） |
| **実装の工夫** | 基本的な形 | **キャッシュ・パッキング・ブラーの最適化** |

## 弱点

| 弱点 | 説明 |
| --- | --- |
| **式は Alchemy のまま** | ハロー・薄い物・画面外の問題は、そのまま |
| **粗いミップで細部が失われる** | 遠くの細かい遮蔽は、取りこぼす（半径が大きい場合） |
| **ミップのアーティファクト** | **代表の 1 点を選ぶ**ことで、**縮小した深度にちらつき**が出ることがある |
| **コサイン重みは近似** | [GTAO](gtao.md) のような、正確な積分ではない |

## よくあるミス

??? failure "深度のミップを、通常の平均で作って、境界にゴーストが出る"
    **代表の 1 点を選ぶ**（または最小・最大）方式で作ります。

??? failure "非線形の深度のまま、ミップを作る"
    <strong>線形深度（ビュー空間の z）</strong>に変換してから、ミップを作ります。

??? failure "ミップの選び方を、サンプルの 3D 距離でなく、サンプルの番号で決める"
    <strong>画面上の距離（ピクセル）</strong>で選びます。

??? failure "16 ビットの深度で、平らな面に縞が出る"
    32 ビットの浮動小数点か、**2 チャンネルに分けて**精度を確保します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] SAO ＝ <strong>Alchemy AO の式 ＋ 深度のミップ チェーン</strong>
    - [x] <strong>遠いサンプルは、粗いミップから</strong>読み、<strong>キャッシュを効かせる</strong>。<strong>半径に依存しない速さ</strong>
    - [x] ミップは<strong>平均せず、代表の 1 点</strong>で作る（境界のゴースト防止）
    - [x] <strong>深度だけから</strong>、位置と法線を復元（G-Buffer 不要）
    - [x] <strong>後の多くの SSAO 実装に影響</strong>した方式

## 参考

- McGuire, Mara, Luebke, "Scalable Ambient Obscurance"（HPG 2012）
- McGuire et al., "The Alchemy Screen-Space Ambient Obscurance Algorithm"（HPG 2011）

## 関連ページ

- [環境光遮蔽（AO）](index.md)
- [Alchemy AO](alchemy-ao.md)
- [HBAO](hbao.md)
- [フィルタ](filtering.md)
- [低解像度のエフェクト](../../rendering/low-res-effects.md)
- [Hi-Z とスクリーン空間トレース](../../rendering/hiz.md)
