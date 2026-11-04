---
title: Reflection Comparison
tags:
  - 描画
---

# Reflection Comparison

水面に空が映り濡れた床にライトが伸び金属の車体に周りの景色が流れる。反射は見た目のリアルさを大きく左右します。ところが反射を作る方法は 1 つではありません。平面反射、リフレクション プローブ、SSR、レイトレーシング反射の 4 つがありどれも得意な場面と弱点が違います。実際のゲームはこれらを重ねて使います。

このページは 4 方式を並べて、どの場面で何を使うかと重ねる設計を決めるためのページです。個別の仕組みは各ページに任せます。ここでは、違いを表と数字で見て 4 方式を 1 つの反射色にまとめる HLSL まで書きます。

!!! tip "ポイント"
    平面反射は正確で平面専用、プローブは安くて位置がずれる、SSR は細かいが画面内だけレイトレは正確で重い。粗い反射はプローブ、近くの細かい反射は SSR、平面は平面反射、高品質はレイトレです。組み合わせは平面反射、SSR、ローカル プローブ、グローバル プローブの順に重ねます。信頼度でなめらかに混ぜて BRDF の積分は混ぜ終わった後に 1 回だけ掛けます。

!!! info "このページを読む前に"
    - [Reflections](index.md)（このセクション全体の地図と読む順番）

## 総合比較表

次の表は 4 方式を観点ごとに並べた引く用の一覧です。各セルの理由はこの後の節で書きます。

| 項目 | 平面反射 | プローブ | SSR | レイトレ |
| --- | --- | --- | --- | --- |
| 景色の出どころ | 鏡映カメラ | 事前のキューブマップ | 画面の深度と色 | シーンの BVH |
| 画面外・裏側 | 映る | 映る（静的） | 映らない | 映る |
| 対象の面 | 平面のみ | あらゆる面 | あらゆる面 | あらゆる面 |
| 動く物体 | 映る | 映らない | 映る（画面内） | 映る |
| 粗さ（ぼけ） | ぼかしで近似 | ミップ | 確率的・ミップ | 確率的 |
| 位置の正確さ | 正確 | 視差のずれ | 正確（画面内） | 正確 |
| ノイズ | なし | なし | あり | あり（デノイズ必須） |
| コスト | 大 | 小 | 中 | 大 |
| 必要なハード | なし | なし | なし | レイトレ対応 GPU |
| 実装の手間 | 小〜中 | 中 | 中〜大 | 大 |

## 4 方式の性格

### 平面反射

鏡映の位置にカメラを置いてシーンをもう一度描きます。景色は本物なので位置も動く物体も画面外も正確に映ります。ただし平面でしか成り立たずシーンの再描画なので、ジオメトリ処理のコストは解像度を半分にしても下がりません。水面と鏡だけに使います。

### リフレクション プローブ

事前にキューブマップを撮っておき反射方向で引くだけです。コストは小さく画面外も映ります。代わりに撮った位置からの景色なので、そのままでは床や壁に映る物の位置がずれます。ずれを減らすのが視差補正（箱で補正する方法）で、プローブごとに箱を設定する手間が要ります。動く物体は撮った時点にいなければ映りません。

### SSR

画面の深度バッファに向かってレイを進めて、当たった画素の色を借ります。細かい映り込みが画面内なら正確に出る反面、画面の外・物の裏側・半透明は映せません。ここを補うのがフォールバックです（[SSR Fallback and Compositing](ssr-fallback.md)）。

### レイトレース反射

シーンの BVH にレイを飛ばします。画面外も裏側も映り品質が最も高い方式です。レイとヒット点のシェーディングとデノイズで重くなり DXR 対応の GPU が要ります。SSR の失敗分だけを補うハイブリッドもあります（[Ray-Traced Reflections](rt-reflections/index.md)）。

## 場面別の使い分け

### 水面と鏡

平面反射にします。水面は平面で反射が主役の場面だからです。広い海や湖で重い場合は SSR とプローブで代用します。鏡は完全な反射が必要なので平面反射です。

### 磨かれた床と濡れた路面

SSR とプローブにします。面積が広く平面反射は再描画が重くなります。足元の細かい映り込みは SSR、画面外はプローブが受け持ちます。

### 金属と粗い面

金属の機械や車体は曲面なので、プローブで基本の映り込みを出し、近い物を SSR で重ねます。岩や木のような粗い面はぼけた反射で足りるので、プローブだけで済みます。

### ガラスと窓

半透明は深度が書かれないので、SSR は使えません。プローブと専用の工夫（ガラスのシェーダーが自分で反射を引く）で作ります。

### 高品質を優先する PC

レイトレ反射をハイブリッドで入れます。画面外と裏側の反射が必要な場面に効きます。

### モバイル

プローブに簡易な平面反射を足します。軽さが最優先です。

## 粗さごとの得意不得意

粗さによっても得意な方式は変わります。次の図は粗さの帯ごとの得意不得意を濃さで表したものです。

<svg class="fig flow" viewBox="0 0 580 270" role="img" aria-label="粗さごとの得意不得意。濃いほど得意"><text x="14" y="22" class="fig-title">粗さごとの得意不得意（濃いほど得意）</text><text x="200" y="54" text-anchor="middle" style="font-size:12px;font-weight:600">平面反射</text><text x="300" y="54" text-anchor="middle" style="font-size:12px;font-weight:600">プローブ</text><text x="400" y="54" text-anchor="middle" style="font-size:12px;font-weight:600">SSR</text><text x="500" y="54" text-anchor="middle" style="font-size:12px;font-weight:600">レイトレ</text><text x="14" y="86" style="font-size:12px;font-weight:600">粗さ 0（鏡）</text><rect x="150" y="64" width="100" height="36" fill="rgba(76,139,245,0.58)" stroke="#94a3b8" stroke-width="1"/><text x="200" y="87" text-anchor="middle" style="font-size:14px;font-weight:600">◎</text><rect x="250" y="64" width="100" height="36" fill="rgba(76,139,245,0.24)" stroke="#94a3b8" stroke-width="1"/><text x="300" y="87" text-anchor="middle" style="font-size:14px;font-weight:600">△</text><rect x="350" y="64" width="100" height="36" fill="rgba(76,139,245,0.41)" stroke="#94a3b8" stroke-width="1"/><text x="400" y="87" text-anchor="middle" style="font-size:14px;font-weight:600">○</text><rect x="450" y="64" width="100" height="36" fill="rgba(76,139,245,0.58)" stroke="#94a3b8" stroke-width="1"/><text x="500" y="87" text-anchor="middle" style="font-size:14px;font-weight:600">◎</text><text x="14" y="122" style="font-size:12px;font-weight:600">低（0.1〜0.3）</text><rect x="150" y="100" width="100" height="36" fill="rgba(76,139,245,0.41)" stroke="#94a3b8" stroke-width="1"/><text x="200" y="123" text-anchor="middle" style="font-size:14px;font-weight:600">○</text><rect x="250" y="100" width="100" height="36" fill="rgba(76,139,245,0.41)" stroke="#94a3b8" stroke-width="1"/><text x="300" y="123" text-anchor="middle" style="font-size:14px;font-weight:600">○</text><rect x="350" y="100" width="100" height="36" fill="rgba(76,139,245,0.58)" stroke="#94a3b8" stroke-width="1"/><text x="400" y="123" text-anchor="middle" style="font-size:14px;font-weight:600">◎</text><rect x="450" y="100" width="100" height="36" fill="rgba(76,139,245,0.58)" stroke="#94a3b8" stroke-width="1"/><text x="500" y="123" text-anchor="middle" style="font-size:14px;font-weight:600">◎</text><text x="14" y="158" style="font-size:12px;font-weight:600">中（0.4〜0.6）</text><rect x="150" y="136" width="100" height="36" fill="rgba(76,139,245,0.24)" stroke="#94a3b8" stroke-width="1"/><text x="200" y="159" text-anchor="middle" style="font-size:14px;font-weight:600">△</text><rect x="250" y="136" width="100" height="36" fill="rgba(76,139,245,0.58)" stroke="#94a3b8" stroke-width="1"/><text x="300" y="159" text-anchor="middle" style="font-size:14px;font-weight:600">◎</text><rect x="350" y="136" width="100" height="36" fill="rgba(76,139,245,0.41)" stroke="#94a3b8" stroke-width="1"/><text x="400" y="159" text-anchor="middle" style="font-size:14px;font-weight:600">○</text><rect x="450" y="136" width="100" height="36" fill="rgba(76,139,245,0.41)" stroke="#94a3b8" stroke-width="1"/><text x="500" y="159" text-anchor="middle" style="font-size:14px;font-weight:600">○</text><text x="14" y="194" style="font-size:12px;font-weight:600">高（0.7〜）</text><rect x="150" y="172" width="100" height="36" fill="rgba(76,139,245,0.08)" stroke="#94a3b8" stroke-width="1"/><text x="200" y="195" text-anchor="middle" style="font-size:14px;font-weight:600">×</text><rect x="250" y="172" width="100" height="36" fill="rgba(76,139,245,0.58)" stroke="#94a3b8" stroke-width="1"/><text x="300" y="195" text-anchor="middle" style="font-size:14px;font-weight:600">◎</text><rect x="350" y="172" width="100" height="36" fill="rgba(76,139,245,0.24)" stroke="#94a3b8" stroke-width="1"/><text x="400" y="195" text-anchor="middle" style="font-size:14px;font-weight:600">△</text><rect x="450" y="172" width="100" height="36" fill="rgba(76,139,245,0.24)" stroke="#94a3b8" stroke-width="1"/><text x="500" y="195" text-anchor="middle" style="font-size:14px;font-weight:600">△</text><text x="14" y="236" style="font-size:12px;font-weight:400">鏡に近い面は SSR・レイトレ・平面反射、粗い面はプローブで足りる。</text><text x="14" y="256" style="font-size:12px;font-weight:400">◎○△× の判断を濃さに置き換えた。</text></svg>

粗さ 0 の鏡は平面反射とレイトレが完全に正確です。SSR も細かく出ますがプローブは映り込みがぼけてしまいます。ぼけないだけの解像度を持つキューブマップが必要になります。

粗さが 0.1 から 0.3 の低い帯では、SSR とレイトレが最も良く出ます。平面反射とプローブも使えます。

0.4 から 0.6 の中くらいの帯では、プローブが得意です。SSR はぼかしの分のノイズが増えレイトレは重くなります。平面反射はぼかしを正確に作るのが難しくなります。

0.7 以上の高い帯では粗い反射はプローブで十分です。SSR は不安定でレイトレはコストに見合わず平面反射は向きません。

## 数字で見積もる

方式の差を数字の見積もりで確かめます。フル HD（1920 × 1080）を例にします。

### プローブのメモリ

512 × 512 のキューブマップは、6 面で 512 × 512 × 6 = 1,572,864 テクセルです。ミップを含めると全体で 4/3 倍の約 2,097,152 テクセルになります。RGBA16F は 1 テクセル 8 バイトなので、約 16 MiB です。BC6H に圧縮すると 1 テクセル 1 バイトなので約 2 MiB になり、8 分の 1 です。プローブを 100 個置くと無圧縮で約 1.6 GiB、BC6H で約 200 MiB です。圧縮の有無で置ける数が大きく変わります。

### SSR とレイトレのレイ数

画素ごとに 1 本のレイはフル HD で 2,073,600 本です。半分の解像度（960 × 540）なら 518,400 本で、4 分の 1 です。SSR はこのレイを深度バッファの上で進めレイトレは BVH に飛ばします。1 本あたりのコストは SSR は Hi-Z の段数、レイトレはシーンの複雑さで変わります。

### 平面反射の再描画

平面反射は半分の解像度（960 × 540）の RGBA16F が約 4 MB です。メモリは小さくても描くオブジェクトの数は本編と同じ（鏡映側で見える物）なので、頂点処理とドローコールが増えます。そのため、コストの桁は解像度よりオブジェクト数で決まります。

実際の時間は、GPU・解像度・設定で大きく変わります。このページでは見積もりません。実機のプロファイラーで測ってください（[Profiling Tools](../pipeline/tools.md)）。

## 組み合わせの設計

現実的な構成は階層です。上ほど正確で下ほど安定しています。

1. 平面反射: 水面と鏡で、平面を最も正確に出す。
2. SSR: 画面内の細かい映り込み（足元と近くの物）。
3. ローカル プローブ: 画面外と粗い反射。部屋やエリアの単位で視差を補正する。
4. グローバル プローブ: 空と遠景を映す最後の砦。
5. レイトレ（任意）: SSR が失敗した画素のレイを補うハイブリッド。

<svg class="fig flow" viewBox="0 0 680 330" role="img" aria-label="反射を下から順に重ねる。グローバル プローブ、ローカル プローブ、SSR、平面反射。重ねるたびに lerp"><defs><marker id="rfA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">下から順に lerp で重ねる</text><rect x="16" y="250" width="300" height="50" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="166.0" y="266.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">グローバル プローブ</text><text x="166.0" y="284.0" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:400">空・遠景。重みなし（最後の砦）</text><rect x="16" y="176" width="300" height="50" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="166.0" y="192.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">ローカル プローブ</text><text x="166.0" y="210.0" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:400">部屋の箱の中。箱の端で重みが 0 へ</text><rect x="16" y="102" width="300" height="50" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="166.0" y="118.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">SSR</text><text x="166.0" y="136.0" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:400">画面内の当たり。信頼度 a</text><rect x="16" y="40" width="300" height="50" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="166.0" y="56.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">平面反射</text><text x="166.0" y="74.0" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:400">水面・鏡の画素だけ。重み 0 か 1</text><line x1="166" y1="250" x2="166" y2="226" stroke="currentColor" stroke-width="2" marker-end="url(#rfA)"/><text x="176" y="242" style="font-size:11px">lerp(下, 上, 重み)</text><line x1="166" y1="176" x2="166" y2="152" stroke="currentColor" stroke-width="2" marker-end="url(#rfA)"/><text x="176" y="168" style="font-size:11px">lerp(下, 上, 重み)</text><line x1="166" y1="102" x2="166" y2="78" stroke="currentColor" stroke-width="2" marker-end="url(#rfA)"/><text x="176" y="94" style="font-size:11px">lerp(下, 上, 重み)</text><rect x="380" y="102" width="284" height="100" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="522.0" y="143.0" text-anchor="middle" dominant-baseline="central" style="font-size:14px;font-weight:600">最終の反射色</text><text x="522.0" y="161.0" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:400">に BRDF（F0·A + B）を 1 回</text><line x1="316" y1="65" x2="380" y2="140" stroke="currentColor" stroke-width="2" marker-end="url(#rfA)"/><text x="380" y="240" style="font-size:12px;font-weight:400">スペキュラ遮蔽は、プローブ由来の部分にだけ掛ける。</text><text x="380" y="260" style="font-size:12px;font-weight:400">BRDF の積分は、混ぜ終わった後に 1 回だけ。</text></svg>

重ねる順番は下から上へ lerp で上書きしていくのと同じです。上に重ねる方式ほど重みの意味が強くなります。

### 混ぜる原則

信頼度でなめらかに混ぜます。急に切り替えると反射の境目がはっきり見えます（[SSR Fallback and Compositing](ssr-fallback.md)）。

BRDF の積分は混ぜ終わった反射に 1 回だけ `F0 · A + B` を掛けます。方式ごとに掛けると二重になり境目で明るさが食い違います。

粗さからミップへの対応は全方式で同じにします。同じ粗さがプローブでは強いぼけ SSR では弱いぼけになると、境目でぼけ方が変わって見えます。

露出と色空間もそろえます。SSR の入力はブルームと露出の前の HDR から取ります。プローブの色が古いライティングのままだと境目で色がずれます。

スペキュラ遮蔽はプローブ由来の部分にだけ掛けます。隅で光が回り込まないことを表すので、画面の実物を映す SSR や平面反射には掛けません。

## 4 方式を 1 つにまとめる HLSL

ここまでの原則をライティング パスの末尾で動く関数にします。`fxc`（`ps_5_0`）でコンパイルして確かめました。実行はしていないので見た目の確認は自分のシーンで行ってください。

### 入力

```hlsl
// reflection_resolve.hlsl : 4 方式の反射を、信頼度で重ねて 1 つの反射色にする（ライティング パスの末尾）。
// 優先順位（下から重ねる）: グローバル プローブ → ローカル プローブ → SSR → 平面反射。

Texture2D<float4> g_ssr          : register(t0);  // rgb = 反射色、a = 信頼度（SSR のパスが書く）
Texture2D<float4> g_planar       : register(t1);  // 平面反射（水面・鏡）の画像。画面と同じ座標系
Texture2D<float2> g_brdf_lut     : register(t2);  // split-sum の LUT。x = スケール、y = バイアス
TextureCube<float4> g_global_env : register(t3);  // グローバル プローブ（空・遠景）。ミップ付き
TextureCube<float4> g_local_env  : register(t4);  // ローカル プローブ（部屋）。ミップ付き
SamplerState g_linear_clamp      : register(s0);

cbuffer ReflectionParams : register(b0) {
  float3 g_local_center;     // ローカル プローブの中心（ワールド）
  float  g_local_blend;      // プローブの境で混ぜる幅（ワールド単位）
  float3 g_local_extent;     // ローカル プローブの箱の半径（ワールド）
  float  g_max_mip;          // キューブマップの最大ミップ番号（例: 512² なら 9）
  float3 g_camera_pos;
  float  g_max_ray_length;   // SSR の最大の長さ（ワールド単位）
};

struct SurfaceData {
  float3 position;     // ワールド位置
  float3 normal;       // ワールド法線（正規化済み）
  float  roughness;    // 知覚的な粗さ 0〜1
  float3 f0;           // 垂直入射の反射率
  float  ao;           // 環境遮蔽 0〜1（スペキュラ遮蔽に使う）
  float2 uv;           // 画面 UV
  float  planar_weight;  // 平面反射が有効な画素か（水面なら 1）
};
```

入力は SSR のパスが書いた画像（反射色と信頼度）、平面反射の画像、split-sum の LUT、2 つのプローブです。定数バッファはローカル プローブの箱とキューブマップの最大ミップ番号を持ちます。`g_max_ray_length` はこの関数では使っていません。SSR のパス側で信頼度を作るときの値と同じものを置いておく場所です。

### 補助関数

```hlsl
// 粗さ → ミップ。全方式で同じ対応を使う（境目で粗さが食い違うのを防ぐ）。
float RoughnessToMip(float roughness) {
  return roughness * g_max_mip;   // 一例の線形。プローブのプリフィルタに合わせて決める
}

// ローカル プローブの箱の中なら 1、箱の外へ向かって blend の幅で 0 になる。
float LocalProbeWeight(float3 position) {
  float3 d = abs(position - g_local_center);
  float3 inside = (g_local_extent - d) / max(g_local_blend, 1e-4);
  return saturate(min(inside.x, min(inside.y, inside.z)));
}

// 箱で視差補正した方向（Lagarde 2012 の考え方）。箱の面までの距離を求め、プローブ中心からの方向に直す。
float3 BoxProjectedDir(float3 position, float3 dir) {
  float3 rd = dir;
  float3 box_min = g_local_center - g_local_extent;
  float3 box_max = g_local_center + g_local_extent;
  float3 t1 = (box_max - position) / rd;
  float3 t2 = (box_min - position) / rd;
  float3 far_t = max(t1, t2);                    // 各軸で、レイが箱を出る距離
  float t = min(far_t.x, min(far_t.y, far_t.z)); // いちばん早く出る面
  return (position + rd * t) - g_local_center;
}

// スペキュラ遮蔽（Lagarde and de Rousiers 2014）。隅でプローブ由来の反射を弱める。
float SpecularOcclusion(float n_dot_v, float ao, float roughness) {
  return saturate(pow(max(n_dot_v + ao, 0.0), exp2(-16.0 * roughness - 1.0)) - 1.0 + ao);
}

// SSR の信頼度を、画面端で減らす（足した処理。SSR のパスが先に掛けている場合は不要）。
float ScreenEdgeFade(float2 uv) {
  float2 e = abs(uv - 0.5) * 2.0;                // 中心 0、端 1
  return 1.0 - smoothstep(0.85, 1.0, max(e.x, e.y));
}
```

`RoughnessToMip` は全方式の粗さの対応を 1 か所に集めるための関数です。プローブのプリフィルタが線形の粗さでミップを作っていなければ、ここを合わせます。`LocalProbeWeight` は箱の内側からの距離を blend の幅で割って 0 から 1 にします。箱の中心付近は 1、端で 0 になります。`BoxProjectedDir` は反射のレイが箱を出る点を求めて、プローブ中心からその点への方向を返します。これでプローブの撮影位置と画素の位置のずれが減ります。レイ方向の成分が 0 だと除算が inf になりますが、`min` が他の軸の有限な値を選ぶので、結果は壊れません。

### 重ねる処理

```hlsl
float3 ResolveReflection(SurfaceData s) {
  float3 v = normalize(g_camera_pos - s.position);
  float n_dot_v = saturate(dot(s.normal, v));
  float3 r = reflect(-v, s.normal);
  float mip = RoughnessToMip(s.roughness);

  // 1. 最後の砦: グローバル プローブ（空・遠景）。方向だけで引く。
  float3 color = g_global_env.SampleLevel(g_linear_clamp, r, mip).rgb;

  // 2. ローカル プローブ: 箱の中なら視差補正して引く。外へ向かって滑らかに弱まる。
  float local_w = LocalProbeWeight(s.position);
  float3 local = g_local_env.SampleLevel(g_linear_clamp, BoxProjectedDir(s.position, r), mip).rgb;
  color = lerp(color, local, local_w);

  // プローブ由来の部分だけにスペキュラ遮蔽を掛ける（SSR は画面の実物を映すので、遮蔽は不要）。
  color *= SpecularOcclusion(n_dot_v, s.ao, s.roughness);

  // 3. SSR: 信頼度 a で重ねる。画面端でも弱める。
  float4 ssr = g_ssr.SampleLevel(g_linear_clamp, s.uv, 0);
  color = lerp(color, ssr.rgb, ssr.a * ScreenEdgeFade(s.uv));

  // 4. 平面反射: 水面・鏡の画素だけ。最も正確なので最後に重ねる。
  float3 planar = g_planar.SampleLevel(g_linear_clamp, s.uv, mip * 0.5).rgb;   // 粗さはミップで近似（一例）
  color = lerp(color, planar, s.planar_weight);

  // 5. BRDF の積分（split-sum）は、混ぜ終わった反射に 1 回だけ掛ける。方式ごとに掛けると二重になる。
  float2 brdf = g_brdf_lut.SampleLevel(g_linear_clamp, float2(n_dot_v, s.roughness), 0);
  return color * (s.f0 * brdf.x + brdf.y);
}

float4 main(float4 pos : SV_Position, float2 uv : TEXCOORD0) : SV_Target {
  SurfaceData s;
  s.position = float3(0, 0, 0);   // 実際は G バッファから再構成する
  s.normal = float3(0, 1, 0);
  s.roughness = 0.3;
  s.f0 = float3(0.04, 0.04, 0.04);
  s.ao = 1.0;
  s.uv = uv;
  s.planar_weight = 0.0;
  return float4(ResolveReflection(s), 1.0);
}
```

1 番目のグローバル プローブから始めて、`lerp` で上へ重ねます。スペキュラ遮蔽をプローブの直後に掛けるのが、順番の肝です。SSR と平面反射を重ねた後に掛けると、実物の映り込みまで隅で暗くなります。平面反射のぼかしはミップを半分にして近似しました。平面反射の画像にミップがあることが前提で、無い場合はぼかしのパスが別に要ります。最後に BRDF を 1 回だけ掛けます。`main` はコンパイル確認用の入口で、実際は G バッファから `SurfaceData` を作ります。

## 設計の流れ

導入は効果の大きい順に進めます。

1. プローブから始める。粗い反射と最後の砦になる。
2. 水面や鏡があれば平面を平面反射にする。
3. SSR を足す。接地した足元と近くの細かい反射が出る。信頼度でプローブと混ぜる。
4. 対応 GPU ならレイトレを足す。SSR の失敗分を補う。
5. チューニングする。粗さのしきい値、解像度、プローブの更新頻度を決める。

## よくあるミス

??? failure "SSR だけで済ませて、画面端で反射が消える"
    SSR は画面外を映せないので、画面の端やカメラを動かした瞬間に反射が消えます。画面端の信頼度を下げプローブで補います。

??? failure "プローブだけで、足元の細かい映り込みを期待する"
    プローブには近くの小さな物が映りません。床に立つキャラの足元が映らず浮いて見えます。SSR を重ねます。

??? failure "全部の面に平面反射を使って重い"
    平面反射はシーンの再描画なので、使う面の数だけ増えます。水面と鏡だけに限り床は SSR とプローブにします。

??? failure "方式の境目で明るさやぼけが違って見える"
    BRDF の積分を方式ごとに掛けていたり粗さからミップへの対応が方式で違ったりすると、境目に段差が出ます。式と対応を 1 か所に集めます。

??? failure "レイトレを入れたが、ざらざらのまま"
    反射のレイは少ないので、デノイズに頼ります。デノイザーを後回しにしてレイ数だけ増やすと重くなるだけです。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 平面反射は平面専用で正確、プローブは安くて視差、SSR は画面内だけレイトレは重い
    - [x] 粗い反射はプローブ、細かい近い反射は SSR、平面は平面反射
    - [x] 重ねる順は平面反射、SSR、ローカル プローブ、グローバル プローブ
    - [x] BRDF の積分は、混ぜ終わった後に 1 回だけ
    - [x] 導入はプローブ、SSR、平面反射とレイトレの順

## 参考

このページは同じセクションの各ページ（Reflections、Planar Reflections、Reflection Probes、SSR Fallback and Compositing、Ray-Traced Reflections）をもとに 4 方式の選び方としてまとめたものです。次の資料はこのページを書くために読み直していません。メモリとレイ数の見積もりはこのページで計算しました。

- Morgan McGuire, Michael Mara, "Efficient GPU Screen-Space Ray Tracing", Journal of Computer Graphics Techniques, Vol. 3, No. 4, 2014.（SSR）
- Tomasz Stachowiak, Yasin Uludag, "Stochastic Screen-Space Reflections", SIGGRAPH 2015, Advances in Real-Time Rendering in Games.（確率的 SSR）
- Sébastien Lagarde, Charles de Rousiers, "Moving Frostbite to Physically Based Rendering 3.0", SIGGRAPH 2014, Physically Based Shading in Theory and Practice.（スペキュラ遮蔽、IBL）
- Colin Barré-Brisebois, Henrik Halén, Graham Wihlidal, Andrew Lauritzen, Jasper Bekkers, Tomasz Stachowiak, Johan Andersson, "Hybrid Rendering for Real-Time Ray Tracing", Ray Tracing Gems, Chapter 25, Apress, 2019.（ハイブリッド）
- Tomas Akenine-Möller, Eric Haines, Naty Hoffman, Angelo Pesce, Michał Iwanicki, Sébastien Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018.（反射と IBL の章）

## 関連ページ

- [Reflections](index.md)
- [Planar Reflections](planar.md)
- [Reflection Probes](probes/index.md)
- [Stochastic SSR](ssr-stochastic.md)
- [SSR Fallback and Compositing](ssr-fallback.md)
- [Ray-Traced Reflections](rt-reflections/index.md)
