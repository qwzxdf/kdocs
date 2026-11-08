---
title: Alpha-Tested Shadows
tags:
  - 描画
---

# Alpha-Tested Shadows

木の葉を四角い板にテクスチャを貼って、アルファで葉の形に切り抜くという作り方は、本編の描画では問題なく動きます。ところがシャドウ マップにそのまま描くと地面に落ちるのは葉の影ではなく、四角い板の影です。切り抜きの情報はピクセル シェーダーのアルファ テストにしかないからです。

そこでシャドウ パスでも同じアルファ テストをします。代わりに深度専用の高速なパスが使えなくなりピクセル シェーダーとテクスチャ読み込みが入ります。このページではアルファ テストの影の描き方、コスト、ミップで影が痩せる問題、ハッシュド アルファによる柔らかい影を説明します。

!!! tip "ポイント"
    - シャドウ マップでも葉のテクスチャのアルファで `clip` します。
    - 深度専用パスにピクセル シェーダーとテクスチャ読み込みが入ります。アルファ テストの物だけに限ります。
    - 影用に粗いミップのアルファを読むと軽くなります。ただし、遠くで葉が痩せる問題に注意します。
    - ハッシュド アルファを使うと PCF の平均で柔らかい影になります。

!!! info "このページを読む前に"
    - [Special Cases](index.md)（このセクション全体の地図と読む順番）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 問題：葉や柵の影が板になる

木の葉は四角い板に葉の絵を貼りアルファ テストで葉の形に切り抜いて描きます（[Alpha Testing](../../translucency/alpha-test/index.md)）。シャドウ パスでこの板をそのまま深度として描くと透明な部分まで深度に書かれ、葉の影が四角い板の形になります。柵や金網も同じで網目ではなく面の影になります。

```text
 本来の影:                     アルファ テストなしで描いた影:
   ░ ▓ ░ ▓                       ▓▓▓▓▓▓▓▓
   ▓ ░ ▓ ░     葉の形に          ▓▓▓▓▓▓▓▓    四角い板の影
   ░ ▓ ░ ▓     切り抜かれた       ▓▓▓▓▓▓▓▓
```

<svg class="fig flow" viewBox="0 0 640 230" role="img" aria-label="アルファ テストなしとありの深度パスの違い">
<defs><marker id="atA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs>
<text x="14" y="22" class="fig-title">深度専用パスと、アルファ テスト付きパス</text>
<rect x="20" y="44" width="170" height="44" rx="8" fill="rgba(76,139,245,0.22)" stroke="currentColor" stroke-width="2"/><text x="105" y="66" text-anchor="middle" dominant-baseline="central">頂点シェーダー</text>
<rect x="250" y="44" width="170" height="44" rx="8" fill="rgba(76,139,245,0.22)" stroke="currentColor" stroke-width="2"/><text x="335" y="66" text-anchor="middle" dominant-baseline="central">深度に書く(PS なし)</text>
<rect x="20" y="128" width="170" height="44" rx="8" fill="rgba(76,139,245,0.22)" stroke="currentColor" stroke-width="2"/><text x="105" y="150" text-anchor="middle" dominant-baseline="central">頂点シェーダー(+UV)</text>
<rect x="250" y="128" width="170" height="44" rx="8" fill="rgba(229,170,40,0.28)" stroke="currentColor" stroke-width="2"/><text x="335" y="150" text-anchor="middle" dominant-baseline="central">PS: アルファ → clip</text>
<rect x="470" y="128" width="150" height="44" rx="8" fill="rgba(76,139,245,0.22)" stroke="currentColor" stroke-width="2"/><text x="545" y="150" text-anchor="middle" dominant-baseline="central">深度に書く</text>
<g stroke="currentColor" stroke-width="2" fill="none" marker-end="url(#atA)">
<line x1="190" y1="66" x2="246" y2="66"/><line x1="190" y1="150" x2="246" y2="150"/><line x1="420" y1="150" x2="466" y2="150"/>
</g>
<text x="440" y="70" style="font-size:12px">最速。四角い板の影になる</text>
<text x="20" y="208" style="font-size:12px">アルファ テストの物だけ下の経路を通す。不透明な物は上の経路のまま</text>
</svg>

## 対策：シャドウ パスでもアルファ テストをする

シャドウ パスのピクセル シェーダーで、メインの描画と同じアルファ テストを行います。透明な画素は `clip` で捨て深度に書きません。

```hlsl
// シャドウ パス用のピクセル シェーダー(アルファ テストする物だけ)。
Texture2D<float4> g_albedo : register(t0);            // 葉などのアルベド(アルファ入り)
SamplerState g_linear_wrap : register(s0);            // 線形補間 + 繰り返し

void main(float4 pos : SV_Position, float2 uv : TEXCOORD0) {
  float alpha = g_albedo.Sample(g_linear_wrap, uv).a;   // テクスチャのアルファ(0 = 透明、1 = 不透明)
  clip(alpha - 0.5);                                    // 0.5 未満の画素を捨てる。メインの描画と同じしきい値
  // 色は出力しない。clip を通った画素の深度だけが書かれる。
}
```

`clip(x)` は `x` が 0 未満のときその画素を捨てます。ここでは `alpha - 0.5` なのでアルファが 0.5 未満の画素が捨てられます。出力が `void` で `SV_Target` を持たないのは、シャドウ パスでは色を書かないからです。

`fxc` で `ps_5_0` にコンパイルして、エラーが出ないことを確かめました。GPU では動かしていません。

頂点シェーダーは UV をピクセル シェーダーへ渡す必要があります。深度のみのパスでは UV を省いていたはずなので、アルファ テストの物用の頂点シェーダーを別に用意します。

```cpp
// 物ごとにシェーダーを切り替える(アルファ テストする物だけ、ピクセル シェーダーを使う)。
for (const Mesh& m : shadow_casters) {
  if (m.alpha_tested) {                                              // 葉・柵・金網など
    context->VSSetShader(shadow_alpha_vs.Get(), nullptr, 0);         // UV を渡す頂点シェーダー
    context->PSSetShader(shadow_alpha_ps.Get(), nullptr, 0);         // アルファを読んで clip
    context->PSSetShaderResources(0, 1, m.albedo_srv.GetAddressOf());   // アルベドを t0 に
  } else {
    context->VSSetShader(shadow_depth_vs.Get(), nullptr, 0);         // 位置だけの頂点シェーダー
    context->PSSetShader(nullptr, nullptr, 0);                       // PS なし = 深度のみ(最速)
  }
  Draw(m);                                                           // 描画(Draw は説明用の関数)
}
```

このコードはコンパイルして確かめていません。描画順を不透明（PS なし）→ アルファ テスト（PS あり）の順にそろえると、シェーダーの切り替えが減って効率が良くなります。

## 影用のアルファの工夫

### しきい値をメインとそろえる

メインの描画のしきい値が 0.5 で、影が 0.3 なら影のほうが葉が太く出ます。しきい値が違うと葉の形と影の形がずれて、葉が光って見えたり影が浮いて見えたりします。同じ値を使います。ミップの扱いもそろえます（[Foliage Translucency](../../terrain/vegetation/translucency.md)）。

### 粗いミップのアルファを読む

影は細部が見えにくいのでアルファのミップを 1〜2 段粗く読むとテクスチャ読み込みが軽くなり、影の縁がなめらかになります。

```hlsl
float alpha = g_albedo.SampleBias(g_linear_wrap, uv, 1.0).a;   // ミップを 1 段粗く読む(バイアス +1)
clip(alpha - 0.5);                                              // 以降は同じ
```

ただし、粗く読むほど細い葉や柵のアルファが薄まります。幅 1 ピクセルの不透明な棒が、背景の透明に囲まれているとします。ミップ 0 のアルファは 1.0、ミップ 1 は 0.5、ミップ 2 は 0.25、ミップ 3 は 0.125 です（棒の太さを 1・2・4・8 ピクセルの平均として計算した値）。しきい値 0.5 ではミップ 2 以上で棒が消えます。

### 遠くで薄くなる葉にカバレッジを補正する

遠くの葉は画面で小さくなるにつれて高いミップが選ばれアルファが薄まって、影がスカスカになります。ミップごとにしきい値を超える画素の割合（カバレッジ）が元と同じになるように、アルファに倍率を掛けて補正する方法が知られています（Castaño の "Computing Alpha Mipmaps"、2010。このページでは原文を読んでいません）。メインの描画と影の両方に同じ補正を適用します。

```hlsl
cbuffer ShadowAlphaCB : register(b0) {
  float g_cutoff;             // アルファのしきい値(メインと同じ値、例: 0.5)
  float g_mip_bias;           // ミップのバイアス(例: 1.0)
  float g_coverage_scale;     // カバレッジ補正の倍率(ミップごとにビルド時に求めた値の一例)
  float pad;                  // 16 バイト境界にそろえる詰め物
};

void ShadowPS(float4 pos : SV_Position, float2 uv : TEXCOORD0) {
  float alpha = g_albedo.SampleBias(g_linear_wrap, uv, g_mip_bias).a;   // 粗いミップのアルファ
  alpha = saturate(alpha * g_coverage_scale);                           // 薄まった分を倍率で戻す(足した)
  clip(alpha - g_cutoff);                                               // しきい値で切る
}
```

倍率をどう求めるかはここでは扱いません。ミップごとに違う値が必要で 1 つの定数では足りないことがあります。

### ハッシュド アルファ

影を確率的に薄くする方法です（[Hashed Alpha](../../translucency/alpha-test/hashed-alpha.md)）。画素ごとにしきい値を変えると、アルファが 0.3 の所は約 3 割の画素だけが残ります。PCF が複数のテクセルを平均すると、葉の影が柔らかく半透明に見えます。

```hlsl
// 画素の位置から 0〜1 の疑似乱数を作る(足した: 簡単なハッシュの一例)。
float Hash12(float2 p) {
  float3 p3 = frac(float3(p.xyx) * 0.1031);          // 小数部を取って散らす
  p3 += dot(p3, p3.yzx + 33.33);                     // 成分を混ぜる
  return frac((p3.x + p3.y) * p3.z);                 // 0〜1 に落とす
}

void ShadowHashedPS(float4 pos : SV_Position, float2 uv : TEXCOORD0) {
  float alpha = g_albedo.Sample(g_linear_wrap, uv).a;                  // アルファ
  float threshold = max(Hash12(pos.xy), 1.0 / 255.0);                  // 0 だと全部通ってしまうので下限を置く
  clip(alpha - threshold);                                             // alpha が threshold より大きければ残る
}
```

一様乱数のしきい値ならアルファ p の画素が残る確率はちょうど p です。シミュレーションで確かめた結果は p = 0.1・0.3・0.5・0.8 で、残る割合が約 0.100・0.300・0.500・0.799 でした。

PCF の 16 サンプルで平均した場合の影の濃さは、p = 0.3 で平均 0.30、標準偏差 0.114、p = 0.5 で平均 0.50、標準偏差 0.125 でした。標準偏差は画面でのちらつきの大きさに相当します。サンプル数を増やすか時間方向に積算（TAA）して抑えます。

`fxc` で `ps_5_0` にコンパイルして、エラーが出ないことを確かめました。

## 効率

アルファ テストの影が重いのは、次の 3 つです。

- ピクセル シェーダーが必要になります。深度のみ（シェーダーなし）が使えなくなりシャドウ パスが重くなります。
- オーバードロー。葉は重なって描かれ影のパスでも同じです。2048² のシャドウ マップは約 420 万画素ですが、オーバードロー 4 なら最大で約 1,680 万回のアルファ読み込みです（仮定の数字）。Early-Z が効かないことも響きます（[Performance and Shadow Passes](../../translucency/alpha-test/performance.md)）。
- 全ライトの全葉で起きる。ライトごとにシャドウ パスがあるので、ライトが増えるほどアルファ テストの物の負担が増えます。

対策は 3 つあります。

1. 遠くの葉は影を落とさないようにします（影を落とす距離を限ります）。
2. 影用に簡略メッシュ（葉の枚数を減らした LOD）を使います。
3. 木の影は幹と大きな枝だけで落とし、葉は 1 枚の大きなアルファ カードにまとめます。

## よくあるミス

??? failure "葉が板の影になる"
    深度パスにアルファ テストが入っていません。アルファ テストの物だけピクセル シェーダー付きのパスで描きます。

??? failure "影の葉がメインの葉より太いまたは細い"
    メインのしきい値と影のしきい値が違います。ミップのバイアスやカバレッジ補正も同じ設定にそろえます。

??? failure "遠くの木の影が、スカスカになる"
    高いミップでアルファが薄まりしきい値で多くの画素が捨てられています。カバレッジ補正を入れるか影用のミップを固定します。

??? failure "ハッシュド アルファの影が、ちらつく"
    しきい値が画素の位置だけで決まり PCF のサンプル数が少ないと濃さの標準偏差が大きく残ります。サンプル数を増やすか TAA で時間方向に平均します。

## 確かめたこと

- HLSL を `fxc`（`ps_5_0`）でコンパイルして、エラーが出ないことを確かめました。
- ミップごとのアルファ、ハッシュド アルファの通過率と PCF のばらつきは、Python で計算またはシミュレーションした値です。
- GPU では動かしておらず描画結果は見ていません。C++ のコードはコンパイルしていません。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 影の深度パスにもアルファ テストが必要です。
    - [x] ピクセル シェーダーが増えるので、アルファ テストの物だけに限ります。
    - [x] しきい値とミップの扱いは、メインとそろえます。
    - [x] 遠くで痩せる葉には、カバレッジ補正かハッシュド アルファを使います。

## 参考

このページは次の資料を読まずに書きました。内容は一般に知られている説明と手元で計算した数字に基づいています。

- Chris Wyman, Morgan McGuire, "Hashed Alpha Testing", Symposium on Interactive 3D Graphics and Games 2017。未読。
- Ignacio Castaño, "Computing Alpha Mipmaps", 2010。未読。
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018。未読。
- Microsoft Learn, "clip (HLSL)"。未読。

## 関連ページ

- [Special Cases](index.md)
- [Rendering Depth](../shadow-map-basics/render-depth.md)
- [Alpha Testing](../../translucency/alpha-test/index.md)
