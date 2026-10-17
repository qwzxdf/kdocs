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

GPU のテクスチャ読み込みは、隣り合う画素をまとめてキャッシュに載せて速くしています。半径が小さければ、サンプルは p の近くにまとまり、同じキャッシュ ラインから何度も読めます。半径が大きいと、サンプルは画面の遠くに散り、1 回読むたびに別のメモリ領域へアクセスする形になります。メモリの帯域が足りなくなり、AO の計算は「計算量」でなく「メモリ待ち」で遅くなります。

HBAO や Alchemy AO でも、半径を大きくすると急に重くなることがありました。これは式の問題でなく、<strong>深度の読み方の問題</strong>です。SAO は式を変えず、読み方だけを変えて、この問題を解きます。

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

手前の物体の画素（深度 2 m）と、その背後の壁の画素（深度 10 m）を平均すると、6 m という値ができます。ところが、画面のその場所には、6 m の所に面は存在しません。この<strong>存在しない面</strong>が、AO の計算のとき、サンプルを遮る幽霊のような遮蔽物として働きます。

そこで、SAO は 4 画素の中から<strong>実在する 1 画素を選ぶ</strong>方法を採ります（ポイント サンプリングで縮小）。選ばれた値は必ずどこかに実在する深度なので、境界で嘘の深度が生まれません。最小値（最も手前）を取る方法もあり、遮蔽を多めに見る安全側の選択ですが、手前の細い物が太く見えるという副作用があります。最大値（最も奥）を取る方法はその逆で、遮蔽を少なめに見ます。

SAO の方式は、**代表の 1 点を選ぶ**だけで、各ミップは前のミップから 1 パスで作れます。

```hlsl
float MipDown(float2 uv_in_src) {
  return src_tex.Load(int3(2 * pixel, src_mip)).r;
}
```

## 位置と法線を深度から復元する

SAO は、**G-Buffer の法線を使いません**。**深度だけ**から、位置と法線を復元します。

<strong>位置</strong>は、線形深度 z と画面上の位置から計算します。画面の座標 (ndc_x, ndc_y) を −1〜1 で表すと、`x = ndc_x · z · tanX`、`y = ndc_y · z · tanY` です（tanX・tanY は視野角の半分の tan。[Crytek SSAO](ssao-crytek.md)）。

<strong>法線</strong>は、隣の画素の位置との差を 2 本とって外積を取れば求まります。ここでの工夫は、左右・上下のうち<strong>深度の差が小さい側</strong>を選ぶことです。物体の輪郭では、片側が別の面になっていて、そちらを使うと法線が大きくずれます。差が小さいほうは、同じ面の側である可能性が高いからです。

<strong>精度</strong>も大切です。復元した位置の誤差は、そのまま AO の縞になります。深度は 32 ビット浮動小数点で持つか、上位・下位の 2 チャンネルに分けて高精度に保存します。

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

SAO は 5 つのパスで構成されます。

最初に、深度バッファを<strong>線形深度</strong>に変換し、同時にミップ チェーンを作ります。次に、AO を計算します。各画素で螺旋状にサンプルを置き、サンプルまでの画面上の距離に応じたミップから深度を読み、Alchemy の式で足し合わせます。その後、バイラテラル ブラーを横方向、縦方向の順に 2 回かけて、ノイズを消します。バイラテラル ブラーは 2 次元のぼかしを縦横の 1 次元に分けた（分離可能）形で、コストを大幅に減らします。最後に、結果を間接光に掛けて合成します。

論文には、実装の細かい最適化もあります。AO の結果と深度を、1 枚のテクスチャのチャンネルに<strong>詰めて</strong>保存し、ブラーのパスでテクスチャを読む回数を減らします。1 回のテクスチャ読み込みで、AO と深度の両方が手に入るためです。メモリ帯域が律速になる処理では、こういう工夫の積み重ねが効きます。

## 性能の特徴

SAO のコストは、主に 3 つで決まります。サンプル数に比例して増えます（9〜13 個が目安）。画素数に比例して増えます（半分の解像度で計算すれば、さらに軽くなります。[低解像度のエフェクト](../../rendering/low-res-effects.md)）。そして、<strong>半径にはほぼ依存しません</strong>。これが「スケーラブル」の意味です。ブラーは分離可能なので、コストは小さいです。

## Alchemy AO との比較

AO の式そのものは Alchemy AO と同じで、変わったのは「読み方」だけです。Alchemy AO は常にミップ 0（フル解像度）の深度を読みます。SAO は距離に応じて粗いミップを読むので、半径を大きくしてもコストがほぼ一定です。法線も、G-Buffer に頼らず、深度だけから高精度に復元できます。ほかにも、キャッシュ、パッキング、ブラーの最適化など、実装面の工夫を多く入れています。

## 弱点

式が Alchemy のままなので、ハロー、薄い物、画面外といった[スクリーン空間 AO の共通の弱点](artifacts/index.md)は、そのまま残ります。

粗いミップを使うことによる弱点もあります。遠くの細かい遮蔽は、粗い深度では取りこぼします。半径が大きい場合に目立ちます。また、代表の 1 点を選ぶ方式は、カメラが動くと選ばれる画素が切り替わり、縮小した深度が<strong>ちらつく</strong>ことがあります（[Noise, Banding and Flicker](artifacts/noise-flicker.md)）。コサイン重みも近似なので、[GTAO](gtao.md) のような正確な積分ではありません。

## より良いやり方

SAO の「深度のミップ」の発想は、その後の多くの実装に受け継がれています。最近の実装は、深度のミップを Hi-Z（階層化深度バッファ）として使い回します。シーンの他の処理（SSR のレイ マーチ、カリング）と共有できるためです（[Hi-Z とスクリーン空間トレース](../../rendering/hiz.md)）。また、精度を重視するなら、SAO の速さの工夫に GTAO の積分を組み合わせた構成を取ります（実際、XeGTAO は深度のミップ チェーンに、GTAO の積分を載せています）。

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

- [Ambient Occlusion (AO)](index.md)
- [Alchemy AO](alchemy-ao.md)
- [HBAO](hbao.md)
- [フィルタ](filtering/index.md)
- [低解像度のエフェクト](../../rendering/low-res-effects.md)
- [Hi-Z とスクリーン空間トレース](../../rendering/hiz.md)
