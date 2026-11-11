---
title: Performance and Shadow Passes
tags:
  - 描画
---

# Performance and Shadow Passes

葉や草を `clip` で切り抜くシーンは見た目が良い一方で、フレーム時間が思ったより伸びます。奥の葉のピクセル シェーダーまで、何重にも実行されるからです。不透明なメッシュなら手前に隠れた画素のシェーダーは、実行されずに捨てられます。

<strong>`clip` を含むシェーダーは画素が残るかどうかがシェーダーを実行するまで分からないので、Early-Z の恩恵を十分に受けられません</strong>。このページではなぜ遅くなるのか深度プリパスで直す方法、ジオメトリで切り抜く方法、影と深度のパスでのアルファ テスト、オーバードローの測り方を説明します。

!!! tip "ポイント"
    - `clip` があると深度の書き込みはシェーダーの後でしかできません。隠れた葉のシェーダーも実行されます。
    - 対策の本命は深度プリパスです。軽いシェーダーで深度だけを先に描き本描画の深度テストを `EQUAL` にします。
    - 葉の板を輪郭に合わせて切ると、透明な画素のシェーダー実行が減ります。
    - 影のパスでもアルファ テストが必要です。軽いシェーダーと粗いミップ、短い距離で足ります。
    - 草原や森ではオーバードローが 10 倍を超えます。測ってから最適化します。

!!! info "このページを読む前に"
    - [Alpha Testing](index.md)（このセクション全体の地図と読む順番）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## なぜ `clip` は重いのか {#why}

GPU はふつうピクセル シェーダーを実行する前に深度テストを行います（Early-Z）。手前に別の物があって見えない画素はシェーダーを実行せずに捨てます。重いライティングを実行する画素が、見える画素だけになるのが利点です。

<svg class="fig flow" viewBox="0 0 720 250" role="img" aria-label="通常の描画は深度テストをシェーダーの前に行う。clip があると、深度の書き込みはシェーダーの後になる"><defs><marker id="apA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">深度テストの位置</text>
<text x="20" y="62" style="font-size:12px;font-weight:600">通常</text>
<g stroke="#4c8bf5" stroke-width="2" fill="rgba(76,139,245,0.22)"><rect x="80" y="40" width="130" height="40" rx="8"/><rect x="250" y="40" width="130" height="40" rx="8" fill="rgba(229,170,40,0.3)" stroke="#e5aa28"/><rect x="420" y="40" width="130" height="40" rx="8"/></g>
<g style="font-size:12px;font-weight:600" text-anchor="middle"><text x="145" y="65">深度テスト（Early-Z）</text><text x="315" y="65">ピクセル シェーダー</text><text x="485" y="65">深度・色の書き込み</text></g>
<g stroke="currentColor" stroke-width="2" marker-end="url(#apA)"><line x1="210" y1="60" x2="250" y2="60"/><line x1="380" y1="60" x2="420" y2="60"/></g>
<text x="145" y="102" text-anchor="middle" style="font-size:11px">隠れた画素はここで捨てる</text>
<text x="20" y="162" style="font-size:12px;font-weight:600">clip あり</text>
<g stroke="#4c8bf5" stroke-width="2" fill="rgba(76,139,245,0.22)"><rect x="80" y="140" width="130" height="40" rx="8" opacity="0.5"/><rect x="250" y="140" width="130" height="40" rx="8" fill="rgba(229,170,40,0.3)" stroke="#e5aa28"/><rect x="420" y="140" width="130" height="40" rx="8" fill="rgba(229,72,77,0.2)" stroke="#e5484d"/></g>
<g style="font-size:12px;font-weight:600" text-anchor="middle"><text x="145" y="165">制限つき</text><text x="315" y="165">シェーダー＋ clip</text><text x="485" y="165">深度の書き込みは後</text></g>
<g stroke="currentColor" stroke-width="2" marker-end="url(#apA)"><line x1="210" y1="160" x2="250" y2="160"/><line x1="380" y1="160" x2="420" y2="160"/></g>
<text x="315" y="202" text-anchor="middle" style="font-size:11px">見える画素かどうか、ここまで分からない</text>
<text x="360" y="240" text-anchor="middle" style="font-size:12px">clip を使うと、隠れた葉のシェーダーも走る → オーバードローがそのままコストになる</text></svg>

`clip` があるとその画素が残るかどうかは、シェーダーを実行しないと分かりません。深度の書き込みはシェーダーの後でなければできません。深度テストを前に行うこと自体は可能な GPU もありますが、「テストして通っても書き込みは後」になって、同じ位置に重なる葉の効果的な除去ができません。階層化された深度（HiZ）の更新も画素が残るかどうか分からないので制限されます。どこまで制限されるかは GPU の実装ごとに違います。

結果として、葉や草のように画面を何重にも覆う物を `clip` で描くと奥の葉まで、すべてのピクセル シェーダーが実行されます。オーバードローがそのままコストになります。

## 深度プリパス {#prepass}

対策の本命は深度プリパスです。画面全体の深度を軽いシェーダーで先に描いておいて、本描画では深度が一致する画素だけを実行します。

1. 深度プリパス: 軽いピクセル シェーダー（テクスチャを 1 回読んで `clip` するだけ）で、深度を書きます。色は計算しません。
2. 本描画: 重いライティングを行います。深度テストは `EQUAL` にします。深度が一致した画素、つまり最終的に見える画素だけで、重いシェーダーが実行されます。

数字で確かめます。重いシェーダーのコストを 40、軽いシェーダーを 4 とします。画素ごとの重なりが平均 8 枚（オーバードロー 8 倍）で、見える画素はそのうちの 1 枚です。

<svg class="fig flow" viewBox="0 0 720 240" role="img" aria-label="プリパスなしでは重いシェーダーが 8 回、プリパスありでは軽いシェーダー 8 回と重いシェーダー 1 回"><text x="14" y="22" class="fig-title">1 画素あたりのコスト（相対値）</text>
<line x1="60" y1="190" x2="680" y2="190" stroke="currentColor" stroke-width="1.5"/>
<rect x="120" y="40" width="130" height="150" fill="rgba(229,72,77,0.25)" stroke="#e5484d" stroke-width="2"/><text x="185" y="34" text-anchor="middle" style="font-size:12px;font-weight:600">320</text><text x="185" y="212" text-anchor="middle" style="font-size:12px">プリパスなし</text><text x="185" y="228" text-anchor="middle" style="font-size:11px">重い × 8 重なり</text>
<rect x="400" y="145" width="60" height="45" fill="rgba(229,170,40,0.35)" stroke="#e5aa28" stroke-width="2"/><rect x="460" y="145" width="130" height="0" fill="none"/><rect x="400" y="168" width="60" height="22" fill="rgba(76,139,245,0.28)" stroke="#4c8bf5" stroke-width="2"/>
<text x="460" y="212" text-anchor="middle" style="font-size:12px">プリパスあり</text><text x="460" y="228" text-anchor="middle" style="font-size:11px">軽い × 8 ＋ 重い × 1</text><text x="430" y="138" text-anchor="middle" style="font-size:12px;font-weight:600">72</text>
<text x="560" y="110" style="font-size:12px">約 4.4 倍 軽い</text><text x="560" y="130" style="font-size:12px">（320 ÷ 72）</text></svg>

プリパスなしでは `8 × 40 = 320` です。プリパスありでは `8 × 4 + 1 × 40 = 72` で約 4.4 倍軽くなります。軽いシェーダーが重いシェーダーの 1/10 なら見える画素の割合が `1/8` のとき、損益分岐は十分に下です。式にすると `C_軽 / C_重 < 1 − N_見える / N_全体` のときプリパスが得になります。

まず、プリパスのシェーダーです。

```hlsl
Texture2D<float4> g_albedo : register(t0);
SamplerState g_linear_wrap : register(s0);

cbuffer FrameConstants : register(b0) {
  float4x4 g_view_proj;
  float g_alpha_cutoff;      // アルファ テストのしきい値。例: 0.5
  float3 _pad;
};

struct VsOut {
  float4 pos : SV_Position;
  float2 uv : TEXCOORD0;
};

// プリパスと本描画で、同じ頂点シェーダーを使う（深度を一致させるため）
VsOut FoliageVS(float3 world_pos : POSITION, float2 uv : TEXCOORD0) {
  VsOut o;
  o.pos = mul(float4(world_pos, 1.0), g_view_proj);
  o.uv = uv;
  return o;
}

// 深度プリパス: テクスチャを 1 回読んで clip するだけ。色は出力しない
void DepthPrepassPS(VsOut i) {
  float alpha = g_albedo.Sample(g_linear_wrap, i.uv).a;
  clip(alpha - g_alpha_cutoff);
}
```

次に、本描画です。深度テストが `EQUAL` なのでプリパスで `clip` した結果が深度に入っており本描画では `clip` が要りません。

```hlsl
// 本描画: 重いライティングを行う。深度が一致した画素にだけ、実行される
float4 FoliageMainPS(VsOut i) : SV_Target {
  float4 albedo = g_albedo.Sample(g_linear_wrap, i.uv);
  // …重いライティングの計算（省略）…
  return float4(albedo.rgb, 1.0);
}
```

C++ 側は深度ステートを切り替えます。

```cpp
// （コンパイルしていない）本描画: 深度の書き込みを無効にして、テストを「等しい」にする
D3D11_DEPTH_STENCIL_DESC ds = {};
ds.DepthEnable = TRUE;
ds.DepthWriteMask = D3D11_DEPTH_WRITE_MASK_ZERO;     // 書き込まない（プリパスで書いた）
ds.DepthFunc = D3D11_COMPARISON_EQUAL;               // プリパスの深度と一致する画素だけ
device->CreateDepthStencilState(&ds, &depth_equal_state);
```

`EQUAL` には落とし穴があります。プリパスと本描画で頂点シェーダーの計算が 1 ビットでも違うと深度が一致せず、画素が欠けます。同じ頂点シェーダー（同じ行列、同じ計算）を共有します。別のシェーダーを使うと最適化の違いでずれる可能性があります。ずれが心配なら `LESS_EQUAL` にしてわずかなずれを許します。

## ジオメトリで切り抜く {#geometry}

葉を四角い板に絵を貼るのではなく、葉の輪郭に近い多角形で作ると、透明な画素のシェーダー実行が減ります。

- 葉の内側の完全に不透明な部分は `clip` なしのメッシュにします。Early-Z が効きます。
- 葉の縁のアルファのある部分だけを `clip` ありのメッシュにします。

メッシュを 2 つに分けて不透明な部分を先に描くと縁の描画も Early-Z が効いた状態で行えます。

板の形でも無駄が変わります。画面上で 100 × 100 画素になる葉のカードなら正方形の板は 1 万画素のうち約 60 % が透明です。6000 画素のシェーダーが、捨てられるのに実行されます。葉の輪郭に合わせて 8〜12 頂点で切ると、透明は約 15 % の 1500 画素になります。頂点数を少し増やして画素を大きく減らすのは、よい取引です。

## 影・深度パスでのアルファ テスト {#shadow}

シャドウ マップを描くときも葉をアルファで切り抜く必要があります。影のパスは深度だけを書くので、軽いピクセル シェーダーを使います。

```hlsl
// 影のパス: アルファのテクスチャだけを読む。ライティングはしない
cbuffer ShadowPassConstants : register(b1) {
  float g_shadow_mip_bias;   // 影では粗いミップを読む。例: 1.5
  float3 _pad1;
};

void ShadowAlphaPS(VsOut i) {
  // 影は細かい形が不要なので、ミップを上げて読む（読み出しが軽く、縁のちらつきも減る）
  float alpha = g_albedo.SampleBias(g_linear_wrap, i.uv, g_shadow_mip_bias).a;
  clip(alpha - g_alpha_cutoff);
}
```

影のパスの工夫は次のとおりです。

- 軽いシェーダーにします。アルファのテクスチャだけを読みます。
- 低解像度のミップを読みます。影は細かい形が不要です。
- 遠くの葉は影を落としません。影に描く距離を限ります。
- 影用の LOD は描画より粗くします。

詳しくは [Alpha-Tested Shadows](../../shadows/special-cases/alpha-test-shadows.md) にあります。

## そのほかの方法 {#others}

- 不透明な物を先に描いて深度を埋めます。アルファ テストの物の前に不透明を描くとアルファ テストの物の一部が Early-Z で隠れます。構成は不透明、アルファ テスト、半透明の順です。
- アルファのミップが薄くなる問題を補正したミップで直します（[Foliage Translucency](../../terrain/vegetation/translucency.md)）。遠くで葉がスカスカにならないので、カードを増やす必要がなくオーバードローが減ります。
- 遠景はアルファを使いません。遠くの木はインポスター（板 1 枚）かアルファを使わないメッシュ（LOD で葉を塊の不透明な形にする）に置き換えます（[Trees](../../terrain/vegetation/trees.md)）。
- `[earlydepthstencil]` は深度テストと書き込みをシェーダーの前に行う属性です。`clip` した画素も深度を書いてしまうので、アルファ テストの物には使えません。`clip` を使わない物でだけ使えます。

## 計測する {#measure}

最適化の前にオーバードローを測ります。

- オーバードローを色で可視化します。描かれた回数を加算ブレンドで数えます。
- ピクセル シェーダーの実行回数を PIX、RenderDoc、GPU プロファイラーのカウンターで見ます。
- `clip` を一時的に無効にして、フレーム時間を比べます。

```hlsl
// オーバードロー可視化: 描かれるたびに少しずつ加算する（加算ブレンド ONE, ONE）
float4 OverdrawPS(VsOut i) : SV_Target {
  return float4(0.1, 0.05, 0.02, 1.0);
}
// 結果の明るい所ほど、重なって描かれた画素が多い。0.1 ずつ足せば、10 回で白に近づく
```

!!! note "確かめた範囲"
    HLSL は `fxc` で、`FoliageVS`（`vs_5_0`）、`DepthPrepassPS`・`FoliageMainPS`・`ShadowAlphaPS`・`OverdrawPS`（`ps_5_0`）をコンパイルして、エラーが出ないことを確かめました。コストの比は例示の数字で実測ではありません。GPU での計測は行っていません。

草原や森の場面ではオーバードローが 10 倍を超えることもあります。測らずに最適化しないことが大切です（[パフォーマンス プロファイラー](../../../vs/profiler.md)）。

## よくあるミス {#mistakes}

??? failure "葉が多いシーンで、フレーム時間が伸びる"
    原因は `clip` の画素でオーバードローが重なって、重いシェーダーが何重にも実行されることです。深度プリパスに切り替えるか葉の板を輪郭に合わせて切ります。まずオーバードローを可視化して、どこが重なっているかを確かめます。

??? failure "深度プリパスにしたら、葉の縁が欠けるまたは点滅する"
    原因はプリパスと本描画で頂点シェーダーが違い深度が `EQUAL` で一致しないことです。同じ頂点シェーダーを使います。ずれが残る場合は `LESS_EQUAL` にします。

??? failure "葉の影が、四角い板になる"
    原因は影のパスで `clip` していないことです。影のパスにもアルファ テストのシェーダーを使います。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] `clip` があると、深度の書き込みが後になって隠れた葉のシェーダーも走ります。
    - [x] 深度プリパスで、軽いシェーダーで先に深度を書いて、本描画は `EQUAL` にします。重なりが 8 倍で軽い対重いが 1 対 10 なら約 4.4 倍軽くなります。
    - [x] 葉の板を輪郭に合わせて切ります。
    - [x] 影のパスでもアルファ テストをして、粗いミップと短い距離で軽くします。

## 参考 {#references}

このページは次の資料を読まずに書きました。コストの数字は例示のための仮定で、実測ではありません。Early-Z や HiZ の挙動は GPU ごとに違うので、一般的な説明にとどめました。

- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（透明と、アルファ合成の章）
- Wyman, McGuire, "Hashed Alpha Testing", Symposium on Interactive 3D Graphics and Games 2017
- Akeley, Hanrahan, et al., "Real-Time Graphics Architecture", Stanford CS448 講義資料（Early-Z、HiZ の基本）
- Microsoft Learn, "D3D11_BLEND_DESC"（`AlphaToCoverageEnable`、`D3D11_RENDER_TARGET_BLEND_DESC`）

## 関連ページ

- [Alpha Testing](index.md)
- [Alpha-Tested Shadows](../../shadows/special-cases/alpha-test-shadows.md)
