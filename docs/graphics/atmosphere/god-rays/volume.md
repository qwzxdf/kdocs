---
title: Volume-Based God Rays
tags:
  - 描画
---

# Volume-Based God Rays

光の筋を出す方法はふつう画素ごとに視線をたどる必要があります。画素が 200 万あればレイマーチも 200 万本です。ボリューメトリック フォグ（froxel）は、この仕事を「画素ごと」から「セルごと」に変えます。カメラの前の空間を 3D のセルに分けて、セルごとに 1 回だけ影を引きます。そうすると、光の筋はほとんどおまけで出ます。このページでは Wronski（Assassin's Creed IV）の方式を、シャドウ マップの準備から画面への適用まで、コメント付きの完成形で説明します。

!!! tip "ポイント"
    - セルごとに影を 1 回引けば、視線方向の積分が光の筋になる。画素ごとのレイマーチは要らない。
    - セル数は 160 × 90 × 64 ＝ 92 万で、画面の解像度に依存しない。影を引く回数は約 144 分の 1 になる。
    - 影はそのまま引かず ESM に縮小してぼかす。フォグは低周波なので細かい影は不要で、ちらつきの元になる。
    - 解像度が低いので、細い筋は欠ける。ジッターと時間方向の蓄積で見かけの解像度を上げる。
    - 複数のライト、半透明の物体にも同じボリュームで対応できる。

!!! info "このページを読む前に"
    - [God Rays](index.md)（このセクション全体の地図と読む順番）
    - [Volumetric Fog](../volumetric-fog/index.md)（froxel の考え方）

## 読んだ資料 {#sources}

- Bart Wronski, "Volumetric Fog: Unified, Compute Shader Based Solution to Atmospheric Scattering", SIGGRAPH 2014 Advances in Real-Time Rendering in Games。スライドとノート 67 枚の本文を全部読みました。図とビデオと付録のコード（画像）は読めていません。
- Hillaire の Frostbite の発表（SIGGRAPH 2015）と、Real-Time Rendering 第 4 版は、今回は取得できず読んでいません。区間内の解析的な積分は自分で導いた式で、Hillaire の式を読んで写したものではありません。

数字は Wronski の発表の値と自分で C++ で数えた値を区別して書きます。

## なぜ画素ごとのレイマーチではだめか {#why-not}

Wronski の発表は従来のレイマーチの限界を 5 つ挙げています。

1. 多くは近距離の「ボリューメトリック シャドウ」向けで、物理ベースではなく長距離のフォグに向かない。ブレンドは美術が指定する。
2. ループで動くので現代の GPU に向かない。シャドウ マップの読み込みは遅延が大きく、待つあいだ別の仕事をできると効率がよい。
3. エピポーラ サンプリングのような最適化は、密度が場所で変わる媒質や複数のライトに制約がある。ライトごとに別のサンプリングが要る。
4. 後処理として作られているので、フォワードで描く半透明の物体やパーティクルを正しく扱えない。
5. 解像度を落とすと輪郭で、アンダーサンプリングやエイリアスが出て、避けにくい。

放射ぼかし（[Radial Blur](radial-blur.md)）は、同じ発表で「光源が画面外に出ると消える」と書かれています。

発想の元は Kaplanyan の Light Propagation Volumes でした。光を 3D テクスチャに注入して、それを使って参加媒質の輸送を計算する、という将来の課題が書かれていて、Wronski らはこれを採りました。ライトの数に依らず積分が 1 回で済み影の項を足すだけで、ゴッド レイがコストの追加なしに出るという見込みです。

<svg class="fig flow" viewBox="0 0 700 122" role="img" aria-label="4 段階のパイプライン"><defs><marker id="fg-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">ボリューメトリック フォグの 4 段階(各段階は別のコンピュート)</text><rect x="10" y="34" width="150" height="52" rx="6" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="85.0" y="57.0" text-anchor="middle" font-size="11" fill="currentColor">シャドウ マップ</text><text x="85.0" y="71.0" text-anchor="middle" font-size="11" fill="currentColor">4 分の 1 + ESM</text><line x1="160" y1="60" x2="182" y2="60" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#fg-a)"/><rect x="182" y="34" width="150" height="52" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="257.0" y="57.0" text-anchor="middle" font-size="11" fill="currentColor">光の注入</text><text x="257.0" y="71.0" text-anchor="middle" font-size="11" fill="currentColor">密度・影・位相</text><line x1="332" y1="60" x2="354" y2="60" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#fg-a)"/><rect x="354" y="34" width="150" height="52" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="429.0" y="57.0" text-anchor="middle" font-size="11" fill="currentColor">積分</text><text x="429.0" y="71.0" text-anchor="middle" font-size="11" fill="currentColor">奥行きに累積</text><line x1="504" y1="60" x2="526" y2="60" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#fg-a)"/><rect x="526" y="34" width="150" height="52" rx="6" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="601.0" y="57.0" text-anchor="middle" font-size="11" fill="currentColor">適用</text><text x="601.0" y="71.0" text-anchor="middle" font-size="11" fill="currentColor">1 回読んで FMA</text><text x="10" y="110" text-anchor="start" font-size="10" fill="currentColor">前のフレームの注入結果(履歴)を、再投影して混ぜる → 注入へ戻る</text></svg>

## froxel の配置 {#layout}

最初はワールド軸にそろえた直方体で試したそうです。時間方向のフィルターは簡単でしたが、積分に多くのサンプルが要り遅く、エイリアスも出ました。そこで、カメラの視錐台にそろえた配置にしました。

- 横と縦は NDC を等分します。
- 奥行きは指数の分布にします。近くに集め近くが最も精度が要りエイリアスが目立つためです。
- 大きさは 160 × 90 × 64 か 160 × 90 × 128（プラットフォームによる）です。
- 距離は 50〜128 m で、美術の設定です。

C++ で数えると 160 × 90 × 64 は 921,600 セルで、720p の画素数（1280 × 720 ＝ 921,600）に一致します。論文もこの一致に触れています。RGBA16F なら 1 枚 7.03 MiB で散乱、積分、履歴の 3 枚で 21.1 MiB です（RGBA16F は私の仮定です）。影を引く回数は 92 万回で、1080p・64 歩の画素ごとレイマーチ（1.33 億回）の約 144 分の 1 です。

<svg class="fig flow" viewBox="0 0 700 152" role="img" aria-label="指数刻みのスライス"><defs><marker id="fg-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">奥行きの 64 スライス(near 0.5 m, far 128 m)。奥ほど厚い</text><line x1="30.0" y1="40" x2="30.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="40.0" y1="40" x2="40.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="50.0" y1="40" x2="50.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="60.0" y1="40" x2="60.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="70.0" y1="40" x2="70.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="80.0" y1="40" x2="80.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="90.0" y1="40" x2="90.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="100.0" y1="40" x2="100.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="110.0" y1="40" x2="110.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="120.0" y1="40" x2="120.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="130.0" y1="40" x2="130.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="140.0" y1="40" x2="140.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="150.0" y1="40" x2="150.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="160.0" y1="40" x2="160.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="170.0" y1="40" x2="170.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="180.0" y1="40" x2="180.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="190.0" y1="40" x2="190.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="200.0" y1="40" x2="200.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="210.0" y1="40" x2="210.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="220.0" y1="40" x2="220.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="230.0" y1="40" x2="230.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="240.0" y1="40" x2="240.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="250.0" y1="40" x2="250.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="260.0" y1="40" x2="260.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="270.0" y1="40" x2="270.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="280.0" y1="40" x2="280.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="290.0" y1="40" x2="290.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="300.0" y1="40" x2="300.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="310.0" y1="40" x2="310.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="320.0" y1="40" x2="320.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="330.0" y1="40" x2="330.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="340.0" y1="40" x2="340.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="350.0" y1="40" x2="350.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="360.0" y1="40" x2="360.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="370.0" y1="40" x2="370.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="380.0" y1="40" x2="380.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="390.0" y1="40" x2="390.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="400.0" y1="40" x2="400.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="410.0" y1="40" x2="410.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="420.0" y1="40" x2="420.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="430.0" y1="40" x2="430.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="440.0" y1="40" x2="440.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="450.0" y1="40" x2="450.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="460.0" y1="40" x2="460.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="470.0" y1="40" x2="470.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="480.0" y1="40" x2="480.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="490.0" y1="40" x2="490.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="500.0" y1="40" x2="500.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="510.0" y1="40" x2="510.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="520.0" y1="40" x2="520.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="530.0" y1="40" x2="530.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="540.0" y1="40" x2="540.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="550.0" y1="40" x2="550.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="560.0" y1="40" x2="560.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="570.0" y1="40" x2="570.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="580.0" y1="40" x2="580.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="590.0" y1="40" x2="590.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="600.0" y1="40" x2="600.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="610.0" y1="40" x2="610.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="620.0" y1="40" x2="620.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="630.0" y1="40" x2="630.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="640.0" y1="40" x2="640.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="650.0" y1="40" x2="650.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="660.0" y1="40" x2="660.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><line x1="670.0" y1="40" x2="670.0" y2="80" stroke="#94a3b8" stroke-width="0.8"/><text x="30.0" y="98" text-anchor="middle" font-size="10" fill="currentColor">0.5 m</text><text x="190.0" y="98" text-anchor="middle" font-size="10" fill="currentColor">2 m</text><text x="350.0" y="98" text-anchor="middle" font-size="10" fill="currentColor">8 m</text><text x="510.0" y="98" text-anchor="middle" font-size="10" fill="currentColor">32 m</text><text x="670.0" y="98" text-anchor="middle" font-size="10" fill="currentColor">128 m</text><rect x="477.5" y="40" width="8" height="40" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="481.50849518197793" y="118" text-anchor="middle" font-size="10" fill="currentColor">25 m 付近: 厚み 2.23 m</text><text x="30" y="140" text-anchor="start" font-size="10" fill="currentColor">スライスの厚み: 0.5 m で 0.045 m、8 m で 0.72 m、32 m で 2.9 m、117 m で 10.6 m</text></svg>

指数の刻みは near 0.5 m、far 128 m、64 層とするとスライスの厚みは手前の 0.045 m から奥の 10.6 m まで変わります。32 層目（8 m）で 0.72 m、48 層目（32 m）で 2.9 m です。奥ほど厚いのは遠くの 1 画素が広い範囲を映すからですが、遠くの細い筋は粗くしか表せません。

この解像度で足りる理由を発表は 5 つ挙げています。

1. 各深度で低周波の情報を持つ。
2. 適用のときに 4 次元（quadrilinear）の補間をするので、1 つのセルが見えない。
3. 画素は元の解像度の正確な深度を持つ。
4. 透視の補正とボリュームの形が、情報を正しく配る。
5. 深度の不連続で輪郭のアーティファクトが出ない。

最後の点が重要です。2D の低解像度の後処理では輪郭で、どの深度を採るかを選ぶ必要があり（バイラテラルのアップサンプルなど）、必ず不正確な画素が出ます。3D テクスチャなら画素ごとにその深度で区分線形に補間されるので、この問題が起きません。結果は柔らかく細かい幾何の詳細は出ませんが、実際の大気では多重散乱で筋が柔らかくなるので、見た目に合うと発表は述べています。

## 影の準備：ESM に縮小する {#shadow}

カスケード シャドウ マップはフォグには情報が多すぎます。AC4 のカスケードは 4 枚で 1536² か 1k²、最初の 2 枚は数 m に密集しています。幅の広い PCF では遅くちらつきも残りました。

そこで、ESM（指数シャドウ マップ）を使います。カスケードを 4 分の 1 に縮小して、R32F の 1024 × 256 のテクスチャにします。縮小の際に指数の影の関数を計算し、さらに分離可能な箱フィルターを重ねます。ESM は影の確率をフィルターできそれで影の関数を縮小できます。通常のレンダリングでは光漏れが欠点ですが、参加媒質の中では目立たなかった、と書かれています。

```hlsl
// ボリューメトリック フォグ用の影の準備（Wronski 2014 の第 1 段階）。
// 高解像度のカスケード シャドウ マップを 4 分の 1 に縮小し、指数シャドウ マップ（ESM）に変換して、
// 箱フィルターでぼかす。フォグは低周波なので、細かい影の情報は要らない。ちらつきの元にもなる。

Texture2D<float> g_cascade_depth : register(t0);     // カスケード シャドウ マップ（光から見た深度、0〜1）
RWTexture2D<float> g_esm_out : register(u0);         // ESM（R32_FLOAT）。解像度は入力の 1/4

cbuffer EsmCB : register(b0) {
  uint2 g_out_size;      // 出力の大きさ（例: 1024 x 256）
  float g_esm_c;         // ESM の指数 c（大きいほど影が鋭いが、数値が溢れやすい。一例: 80）
  float g_pad;
};

// 4 x 4 の領域を 1 画素に縮め、exp(c * depth) を平均する。
// ESM は「遮蔽物の深度の指数」をフィルターできるのが特徴。深度そのものを平均してはいけない。
[numthreads(8, 8, 1)]
void DownsampleEsmCS(uint3 id : SV_DispatchThreadID) {
  if (any(id.xy >= g_out_size)) return;                         // 端数のスレッドは何もしない

  float sum = 0.0;
  [unroll] for (int y = 0; y < 4; ++y) {
    [unroll] for (int x = 0; x < 4; ++x) {
      float depth = g_cascade_depth.Load(int3(id.xy * 4 + int2(x, y), 0));   // 4 倍の位置の 16 画素
      sum += exp(g_esm_c * depth);                              // 遮蔽物の深度を ESM の値に変える
    }
  }
  g_esm_out[id.xy] = sum / 16.0;                                // 16 画素の平均
}

// 箱フィルター（分離可能）。横と縦の 2 回に分けて呼ぶ。半径 r の箱で平均する。
Texture2D<float> g_esm_in : register(t1);
cbuffer BlurCB : register(b1) {
  int2 g_direction;      // (1, 0) なら横、(0, 1) なら縦
  int g_radius;          // 箱の半径 [texel]。一例: 2
  int g_pad2;
};

[numthreads(8, 8, 1)]
void BoxBlurCS(uint3 id : SV_DispatchThreadID) {
  if (any(id.xy >= g_out_size)) return;

  float sum = 0.0;
  for (int i = -g_radius; i <= g_radius; ++i) {
    int2 p = int2(id.xy) + g_direction * i;
    p = clamp(p, int2(0, 0), int2(g_out_size) - 1);             // 端は繰り返す（外側を読まない）
    sum += g_esm_in.Load(int3(p, 0));
  }
  g_esm_out[id.xy] = sum / (2 * g_radius + 1);
}

// ESM の可視性。フィルター後の値 esm_value は exp(c * 遮蔽物の深度) の平均。
// 受け手（フォグのセル）の深度 receiver が遮蔽物より手前なら、exp(c * (遮蔽物 - 受け手)) は 1 より大きくなり、
// saturate で 1（日向）になる。奥なら 0 に近づく（影）。
float EsmVisibility(float esm_value, float receiver_depth) {
  return saturate(esm_value * exp(-g_esm_c * receiver_depth));
}
```

`DownsampleEsmCS` は 4 × 4 の領域の `exp(c × 深度)` を平均します。深度そのものを平均して `exp` を取ってはいけません。ESM は遮蔽物の深度の指数をフィルターすることで成り立つからです。可視性は `saturate(フィルター後の値 × exp(-c × 受け手の深度))` です。ESM の式そのものは発表では「付録のコード」にあり私は読めていません。上のコードは ESM の一般的な定義から書いたものです。`c` が大きいほど影は鋭いが `exp` が溢れやすくなります。

## ボリュームを作る：光の注入 {#inject}

密度は風で動く 1 オクターブのノイズと高さによる指数の減衰です。複数のオクターブも試したが差はわずかでコストに見合わなかった、と書かれています。蒸気のような重い粒子は地面に溜まるので、高さで指数に減らします。

ライティングは主光源（太陽か月）、定数の環境光、視錐台に入って美術がフォグに影響すると印を付けた動的な点光源をすべて足します。主光源の影は ESM で引きます。結果は密度を掛けて RGB に散乱係数を A に入れます。

位相関数は AC4 では物理ベースのものがなく、太陽の方向と逆の方向の 2 色の美術的な勾配で、それ以外は等方でした。発表の後半で Henyey-Greenstein 位相関数を使う拡張が説明されています。HG は実行時に効率よく評価でき球面調和に簡単に展開でき異方性の係数を変えられる、と書かれています。

```hlsl
// ボリューメトリック フォグの本体（Wronski 2014 の第 2〜4 段階）。
//   ① InjectCS: 各セルの密度と、光の届き具合（影）を書く。ゴッド レイはここで影を引くだけで出る。
//   ② IntegrateCS: 奥行き方向に散乱光と透過率を累積して、各スライスに保存する。
//   ③ ApplyFog: 画面の画素が、自分の距離のスライスを 1 回読んで合成する。
// froxel は 160 x 90 x 64（画面の NDC を等分、奥行きは指数）。

RWTexture3D<float4> g_scatter : register(u0);        // rgb = 散乱光（密度込み）、a = 消散係数 [1/m]
RWTexture3D<float4> g_integrated : register(u1);     // rgb = カメラからそのスライスまでの散乱光、a = 透過率
Texture3D<float4> g_history : register(t0);          // 前フレームの g_scatter（時間方向の蓄積）
Texture2D<float> g_esm : register(t1);               // ② ではなく ① で使う ESM（fog_shadow.hlsl で作ったもの）
Texture3D<float4> g_integrated_srv : register(t2);   // ApplyFog 用（③）
SamplerState g_linear_clamp : register(s0);

cbuffer FogCB : register(b0) {
  float4x4 g_inv_view_proj;      // クリップ → ワールド（ジッター込みの現在のフレーム用）
  float4x4 g_prev_view_proj;     // 前のフレームのワールド → クリップ（履歴の読み出し用）
  float4x4 g_sun_view_proj;      // ワールド → 太陽のシャドウ マップのクリップ空間
  float3 g_camera_pos;           // カメラ位置 [m]
  float g_near;                  // froxel の手前端 [m]
  float3 g_sun_dir;              // 太陽へ向かう単位ベクトル
  float g_far;                   // froxel の奥端 [m]（Wronski は 50〜128 m）
  float3 g_sun_color;            // 太陽の色 × 強さ（線形）
  float g_esm_c;                 // ESM の指数（fog_shadow.hlsl と同じ値）
  float3 g_ambient;              // 空の環境光（定数。AC4 と同じ簡単な扱い）
  float g_phase_g;               // Henyey-Greenstein の g（-1〜1。0.3〜0.8 が普通。一例）
  float3 g_jitter;               // froxel 内のジッター量（0〜1 のセル内オフセット）。フレームごとに変える
  float g_history_weight;        // 履歴の重み（一例: 0.9）。0 なら時間蓄積しない
  float g_base_density;          // 基本の密度 [1/m]（一例: 0.02）
  float g_height_falloff;        // 高さによる減衰 [1/m]（一例: 0.1）
  float g_time;                  // 時間 [s]（風で動かす）
  float g_pad;
};

static const uint3 kGrid = uint3(160, 90, 64);   // froxel の分割数

// ---------- 座標の変換 ----------

// 奥行きのスライス番号（0〜63 の連続値）→ カメラからの距離 [m]。指数の刻み。
float SliceToDistance(float slice) {
  return g_near * pow(max(g_far / g_near, 1.0), slice / kGrid.z);   // far > near。max は保険
}

// 距離 [m] → スライス番号（連続値）。
float DistanceToSlice(float distance_m) {
  return log(distance_m / g_near) / log(g_far / g_near) * kGrid.z;
}

// セル（整数座標 + 0〜1 のセル内位置）→ ワールド位置。ジッターは t に入れる。
float3 CellToWorld(uint3 cell, float3 offset) {
  float3 uvw = (float3(cell) + offset) / float3(kGrid);          // 0〜1 の froxel 座標
  float2 ndc = uvw.xy * float2(2, -2) + float2(-1, 1);           // xy は NDC（y を反転）
  float view_dist = SliceToDistance(uvw.z * kGrid.z);            // このスライスの距離 [m]
  // 画素の方向を求める。ファー面（NDC の z = 1）上の点をワールドに戻し、カメラから向かう方向にする。
  float4 clip_far = float4(ndc, 1.0, 1.0);
  float4 w_far = mul(clip_far, g_inv_view_proj);
  float3 far_world = w_far.xyz / w_far.w;                        // 画素の方向の、ファー面上の点
  float3 dir = normalize(far_world - g_camera_pos);              // カメラからその画素へ向かう単位ベクトル
  // 距離は「視線に沿った距離」として扱う。Wronski の froxel は奥行き（ビュー z）で切るので、
  // 画面の端では本来より少し近い。簡略化のため、この差は無視する。足した処理。
  return g_camera_pos + dir * view_dist;
}
```

セルの位置は froxel の座標から作ります。スライスの距離は指数の刻みなので、`near × (far/near)^(k/N)` です。ジッターでセル内の別の点を見るのは、後述の時間方向の蓄積で細い筋を出すためです。

```hlsl
// ---------- 密度 ----------

// 簡単なハッシュ ノイズ（0〜1）。本番では Perlin ノイズの 3D テクスチャを読む。足した処理。
float Hash31(float3 p) {
  p = frac(p * 0.3183099 + 0.1);
  p *= 17.0;
  return frac(p.x * p.y * p.z * (p.x + p.y + p.z));
}

// 3 次元の値ノイズ（8 近傍を補間）。
float ValueNoise(float3 p) {
  float3 i = floor(p);
  float3 f = frac(p);
  f = f * f * (3.0 - 2.0 * f);                                  // なめらかな補間
  float n000 = Hash31(i + float3(0, 0, 0)), n100 = Hash31(i + float3(1, 0, 0));
  float n010 = Hash31(i + float3(0, 1, 0)), n110 = Hash31(i + float3(1, 1, 0));
  float n001 = Hash31(i + float3(0, 0, 1)), n101 = Hash31(i + float3(1, 0, 1));
  float n011 = Hash31(i + float3(0, 1, 1)), n111 = Hash31(i + float3(1, 1, 1));
  return lerp(lerp(lerp(n000, n100, f.x), lerp(n010, n110, f.x), f.y),
              lerp(lerp(n001, n101, f.x), lerp(n011, n111, f.x), f.y), f.z);
}

// 霧の密度 [1/m]。Wronski: 風で動く 1 オクターブのノイズ + 高さによる指数の減衰。
// 複数のオクターブは、コストに見合う差が出なかったと書かれている。
float FogDensity(float3 world) {
  float3 wind = float3(1.0, 0.0, 0.5) * g_time * 0.5;            // 風で流れる向きと速さ（一例）
  float noise = ValueNoise(world * 0.08 + wind);                 // 波長 約 12 m の模様
  float height = exp(-max(world.y, 0.0) * g_height_falloff);     // 重い粒子は低い所に溜まる（指数の分布）
  return g_base_density * height * lerp(0.5, 1.5, noise);        // ノイズで 0.5〜1.5 倍に揺らす
}

// ---------- 位相関数 ----------

// Henyey-Greenstein。cos_theta は視線と光の向きのなす角の cos。
// g > 0 で前方散乱（太陽に向かって見ると明るい）、g = 0 で等方。
float HenyeyGreenstein(float cos_theta, float g) {
  float g2 = g * g;
  float denom = 1.0 + g2 - 2.0 * g * cos_theta;
  return (1.0 - g2) / (4.0 * 3.14159265 * pow(max(denom, 1e-4), 1.5));
}

// ---------- ① 光の注入 ----------

[numthreads(8, 8, 4)]
void InjectCS(uint3 id : SV_DispatchThreadID) {
  if (any(id >= kGrid)) return;

  // 1. セルの位置。ジッターで、フレームごとにセル内の別の点を見る（時間方向の蓄積で、細かい筋が出る）。
  float3 world = CellToWorld(id, 0.5 + g_jitter);

  // 2. 霧の密度。これが消散係数（散乱 + 吸収）。ここでは吸収を 0 として、散乱係数と同じにする。
  float density = FogDensity(world);

  // 3. 太陽の影。シャドウ マップの座標へ変換して、ESM を読む。
  float4 sun_clip = mul(float4(world, 1.0), g_sun_view_proj);
  float3 sun_ndc = sun_clip.xyz / sun_clip.w;
  float2 sun_uv = sun_ndc.xy * float2(0.5, -0.5) + 0.5;
  float visibility = 1.0;                                         // シャドウ マップの外は日向とみなす。足した処理
  if (all(sun_uv >= 0.0) && all(sun_uv <= 1.0)) {
    float esm = g_esm.SampleLevel(g_linear_clamp, sun_uv, 0);
    visibility = saturate(esm * exp(-g_esm_c * sun_ndc.z));       // ESM の可視性（fog_shadow.hlsl と同じ式）
  }

  // 4. 位相関数。カメラからセルへ向かう視線と、太陽の向きの間の角。
  float3 view_dir = normalize(world - g_camera_pos);
  // 太陽へ向かうベクトルと、視線の向きの内積。太陽に向かって見るほど +1 に近い。符号は -view_dir を使う。
  float cos_theta = dot(-view_dir, g_sun_dir);
  float phase = HenyeyGreenstein(cos_theta, g_phase_g);

  // 5. 散乱光 = 太陽 × 影 × 位相 + 環境光。どちらも密度（散乱係数）を掛けて、単位長さあたりにする。
  float3 in_scatter = (g_sun_color * visibility * phase + g_ambient) * density;

  // 6. 時間方向の蓄積。前のフレームの同じ点を読んで、履歴と混ぜる。
  float4 current = float4(in_scatter, density);
  float4 prev_clip = mul(float4(world, 1.0), g_prev_view_proj);
  float3 prev_ndc = prev_clip.xyz / prev_clip.w;
  float3 prev_uvw = float3(prev_ndc.xy * float2(0.5, -0.5) + 0.5,
                           DistanceToSlice(length(world - g_camera_pos)) / kGrid.z);
  float weight = g_history_weight;
  if (any(prev_uvw < 0.0) || any(prev_uvw > 1.0)) weight = 0.0;   // 前のフレームの froxel の外 = 履歴なし
  float4 history = g_history.SampleLevel(g_linear_clamp, prev_uvw, 0);
  g_scatter[id] = lerp(current, history, weight);
}
```

`InjectCS` の手順は 6 つです。セルの位置、密度、影、位相関数、散乱光、時間方向の蓄積です。シャドウ マップの外は日向とみなしています。位相関数の cos は視線の逆向きと太陽へ向かう向きの内積で、太陽に向かって見るほど +1 に近づきます。

## 積分する：奥行き方向に累積する {#integrate}

3 番目の段階が散乱方程式の数値解法です。外向きの散乱はベール・ランベルト則の指数関数で、密度の積分に依存します。内向きの散乱はそれまでの内向き散乱光の総和（距離による外向きの減衰込み）です。内向きの値はすでにボリュームに入っているので、各画素の列でカメラから奥へ進み密度の和、内向き散乱光、外向きの減衰係数を累積すれば済みます。

結果のボリュームは各テクセルに「カメラからその 3D 点までにどれだけの光が内向きに散乱されたか」と「どれだけの密度が累積されたか（外向きの減衰）」を持ちます。このデータはフォワードでもディファードでも使えます。

```hlsl
// ---------- ② 積分 ----------

// 各 (x, y) の列で、手前から奥へ累積する。スライスごとに結果を保存しておくと、
// 画面の画素は自分の深度のスライスを 1 回読むだけで、カメラからそこまでの散乱光が分かる。
[numthreads(8, 8, 1)]
void IntegrateCS(uint3 id : SV_DispatchThreadID) {
  if (any(id.xy >= kGrid.xy)) return;

  float3 accumulated = 0.0;                                      // ここまでの散乱光
  float transmittance = 1.0;                                     // ここまでの透過率
  float prev_dist = g_near;                                      // 前のスライスの手前端の距離

  for (uint z = 0; z < kGrid.z; ++z) {
    float4 cell = g_scatter[uint3(id.xy, z)];                    // rgb = 散乱光、a = 消散係数
    float next_dist = SliceToDistance(z + 1);                    // このスライスの奥端
    float step_len = next_dist - prev_dist;                      // このスライスの厚み [m]（指数なので奥ほど厚い）

    // 区間の透過率（ベール・ランベルト則）。
    float cell_transmittance = exp(-cell.a * step_len);

    // 区間内の散乱光の積分。セル内で散乱光と消散係数が一定だと仮定すると、
    //   ∫0^L S exp(-σ t) dt = S (1 - exp(-σ L)) / σ
    // 自分で導いた閉じた式。単純な S × L より、厚いスライスでも明るさが過大にならない。
    float3 integral = cell.rgb * (1.0 - cell_transmittance) / max(cell.a, 1e-5);

    accumulated += transmittance * integral;                     // 手前までの透過率を掛けて足す
    transmittance *= cell_transmittance;                         // 透過率を更新

    g_integrated[uint3(id.xy, z)] = float4(accumulated, transmittance);   // 「カメラからスライス z の奥端まで」
    prev_dist = next_dist;
  }
}
```

区間内の積分はセル内で散乱光 S と消散係数 σ が一定だと仮定すると、`∫0^L S e^(-σt) dt = S (1 − e^(−σL)) / σ` です。`S × L` と単純に掛けると厚いスライス（遠方では 10 m 超）で、光を過大に足します。Wronski の発表は数値的に累積すると書くだけで、この式は載っていません。この式は私が導いたものです。

## 画面に適用する {#apply}

```hlsl
// ---------- ③ 画面に適用 ----------

// 物体の色に透過率を掛け、散乱光を足す。霧の式と同じ形だが、散乱光に影（光の筋）が入っている。
float3 ApplyFog(float3 scene_color, float2 screen_uv, float view_dist) {
  float slice = DistanceToSlice(clamp(view_dist, g_near, g_far)); // froxel の範囲にそろえる
  float3 uvw = float3(screen_uv, slice / kGrid.z);
  float4 fog = g_integrated_srv.SampleLevel(g_linear_clamp, uvw, 0);   // 3 次元のバイリニア（縁の不連続が出ない）
  return scene_color * fog.a + fog.rgb;                           // 物の色 × 透過率 + 散乱光
}
```

適用は 3D テクスチャの双線形読み込みと積和演算だけです。奥行きは画素の深度から決まるので、フォワードで描く半透明の物体やパーティクルにも同じ式でそのまま使えます。何枚重なっても正しく透過率と散乱光が付きます。Wronski の発表はこれを他の後処理との大きな違いとして挙げています。

## 細い筋は出るのか：時間方向の蓄積 {#temporal}

低解像度の弱点は筋が細いときです。アンチエイリアスの考え方で言えば、セルの中心で 1 点だけ影を引くのは、1 サンプル/画素の描画と同じで、細い光の筋を取りこぼします。

発表は拡張としてジッターと時間方向の再投影を挙げています。毎フレーム、サンプル位置を少しずらし前のフレームと再投影で混ぜます。2D の TAA は動く物体の遮蔽と解除で苦労しますが、3D のボリュームでは簡単です。動く物体が占めた空間は無効になるが、その後ろのデータは正しく（早期の打ち切りを使わなければ）、無効なのは視錐台の外だけだからです。位置のジッターは規則的な格子のエイリアスを高周波のノイズに替えノイズは低解像度のカーネルで簡単にぼかせます。もっとも単純な 1 サンプルのジッターと再投影だけで、輪郭のアーティファクトはほぼ消えたと書かれています。

これを C++ で確かめました。視線に沿って 25 m 付近にある、明るい区間（光の筋）をスライスの中心 1 点で見た推定と 8 フレームのジッター（層化）で見た推定を、真値と比べます。筋の位置はスライスとの位相をランダムにして、各 2 万回試します。

結果は下の「数字を出す C++」の実行結果にあります。

筋が 0.25 m でスライスの厚みが 2.23 m なら中心 1 点は、筋を完全に取りこぼす（推定 0）か 9 倍に膨らませるかのどちらかで、標準偏差が真値の 2.96 倍です。8 フレームのジッターで 0.63 まで下がります。平均はどちらもほぼ 1 で偏りは小さいが、分散が大きいことが分かります。筋の長さがスライスの厚みを超える 4 m では、中心 1 点でも 0.22 です。

<svg class="fig flow" viewBox="0 0 580 224" role="img" aria-label="細い筋の推定の誤差"><defs><marker id="fg-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">推定 / 真値の標準偏差(小さいほどよい)。スライス厚 2.23 m に対する筋の長さ w</text><line x1="60" y1="184" x2="520" y2="184" stroke="#94a3b8"/><rect x="80" y="45.2" width="34" height="138.8" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="97" y="41.25" text-anchor="middle" font-size="10" fill="currentColor">2.96</text><rect x="118" y="154.5" width="34" height="29.5" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="135" y="150.46875" text-anchor="middle" font-size="10" fill="currentColor">0.63</text><text x="116" y="200" text-anchor="middle" font-size="10" fill="currentColor">w = 0.25 m</text><rect x="168" y="93.1" width="34" height="90.9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="185" y="89.0625" text-anchor="middle" font-size="10" fill="currentColor">1.94</text><rect x="206" y="169.0" width="34" height="15.0" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="223" y="165.0" text-anchor="middle" font-size="10" fill="currentColor">0.32</text><text x="204" y="200" text-anchor="middle" font-size="10" fill="currentColor">w = 0.5 m</text><rect x="256" y="131.5" width="34" height="52.5" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="273" y="127.5" text-anchor="middle" font-size="10" fill="currentColor">1.12</text><rect x="294" y="176.5" width="34" height="7.5" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="311" y="172.5" text-anchor="middle" font-size="10" fill="currentColor">0.16</text><text x="292" y="200" text-anchor="middle" font-size="10" fill="currentColor">w = 1.0 m</text><rect x="344" y="167.6" width="34" height="16.4" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="361" y="163.59375" text-anchor="middle" font-size="10" fill="currentColor">0.35</text><rect x="382" y="180.2" width="34" height="3.7" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="399" y="176.25" text-anchor="middle" font-size="10" fill="currentColor">0.08</text><text x="380" y="200" text-anchor="middle" font-size="10" fill="currentColor">w = 2.0 m</text><rect x="432" y="173.7" width="34" height="10.3" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="449" y="169.6875" text-anchor="middle" font-size="10" fill="currentColor">0.22</text><rect x="470" y="182.1" width="34" height="1.9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="487" y="178.125" text-anchor="middle" font-size="10" fill="currentColor">0.04</text><text x="468" y="200" text-anchor="middle" font-size="10" fill="currentColor">w = 4.0 m</text><text x="516" y="42" text-anchor="end" font-size="10" fill="currentColor">青: 中心 1 点 / 黄: 8 フレームのジッター</text></svg>

## コストと最適化 {#cost}

Wronski の発表では全体が約 1.1 ms でした。解像度を倍にすると 1.6 ms です。いちばん重いのは密度の構築とライティングで約 0.43 ms、残りの段階はどれも 0.2 ms 未満です。適用の段階は他のパスと統合すれば「無料」になります。プラットフォーム固有の GPU は発表に書かれていません。

<svg class="fig flow" viewBox="0 0 620 180" role="img" aria-label="ボリューメトリック フォグのコスト"><defs><marker id="fg-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">Wronski の報告(ms)。ほかの各段階は 0.2 ms 未満</text><text x="182" y="50" text-anchor="end" font-size="11" fill="currentColor">全体(160x90x64)</text><rect x="190" y="34" width="220.0" height="22" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="416.0" y="50" text-anchor="start" font-size="10" fill="currentColor">1.1</text><text x="182" y="84" text-anchor="end" font-size="11" fill="currentColor">全体(倍の解像度)</text><rect x="190" y="68" width="320.0" height="22" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="516.0" y="84" text-anchor="start" font-size="10" fill="currentColor">1.6</text><text x="182" y="118" text-anchor="end" font-size="11" fill="currentColor">密度とライティング</text><rect x="190" y="102" width="86.0" height="22" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="282.0" y="118" text-anchor="start" font-size="10" fill="currentColor">0.43</text><text x="182" y="152" text-anchor="end" font-size="11" fill="currentColor">ほかの各段階(上限)</text><rect x="190" y="136" width="40.0" height="22" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="236.0" y="152" text-anchor="start" font-size="10" fill="currentColor">0.2 未満</text></svg>

最適化の案として発表は次を挙げています。

- 高い占有率と VGPR の少なさに最も恩恵を受けたので、段階を分けて動かす。
- コストの一部はシャドウ マップの準備なので、他の低周波のライティング（パーティクル、半透明、海）で再利用する。
- 遠くは影とライティングを LOD で省く。
- ジオメトリの後ろにあるセルは Hi-Z で早期に打ち切る。
- ライトの数が多いなら Forward+ やクラスタードで、フォグのライトを絞る。
- ジオメトリに依存しないので、シャドウ マップができたらすぐ非同期コンピュートで動かせる。G バッファを埋める頂点中心のパスと並べるとよい。
- 面光源のような重いライトはライトの境界の箱と交差するセルだけを間接ディスパッチで計算する。

## 環境光（スカイ）を足す {#ambient}

AC4 の方式ではフォグに環境光や GI がなく、影の中が暗くなりすぎます。外向きの散乱だけがあって内向きがないためです。発表はこれを GI の SH で補う拡張を示しています。HG 位相関数は帯球面調和に簡単に展開でき 2 次なら回転も簡単です。視線に回した位相関数の SH と保存した空の光（GI）の SH の積を積分して、フォグの応答を得ます。この項は上のコードでは単純な定数の環境光に置き換えています。

## 数字を出す C++ {#cpp}

MSVC（`/std:c++latest /W4`）でコンパイルして実行しました。HLSL は `fxc`（cs_5_0）でコンパイルして確かめました。実行して絵は確かめていません。「足した処理」「一例」と書いた所は発表にない処理です。

```cpp
// froxel の数字を出す。
//  1. 160 x 90 x 64 のセル数・メモリ・指数刻みのスライスの厚み
//  2. 細い光の筋（視線に沿った明るい区間）を、スライスの中心 1 点で見たときの誤差と、
//     ジッターを足した時間方向の蓄積でどれだけ戻るか
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <random>
#include <vector>

namespace {
constexpr double kMiB = 1024.0 * 1024.0;
constexpr int kNx = 160, kNy = 90, kNz = 64;     // froxel の分割数
constexpr double kNear = 0.5, kFar = 128.0;      // 手前端・奥端 [m]。奥端は Wronski の 50〜128 m の上限

// スライス k の手前端の距離。z(k) = near * (far / near)^(k / N)。
double SliceStart(double k) { return kNear * std::pow(kFar / kNear, k / kNz); }

// 明るい区間 [lo, hi]（視線に沿った距離 [m]）にいる光の筋。1 を日向、0 を影とする。
double Lit(double z, double lo, double hi) { return (z >= lo && z < hi) ? 1.0 : 0.0; }

// froxel の推定: 各スライスの中心（jitter = 0.5）または [0, 1) のジッター位置で影を 1 回だけ引き、
// そのスライスの厚みを掛けて足す。真値は筋の長さ (hi - lo)。
double Estimate(double lo, double hi, const std::vector<double>& jitters) {
  double total = 0.0;
  for (int k = 0; k < kNz; ++k) {
    const double z0 = SliceStart(k), z1 = SliceStart(k + 1);
    double sum = 0.0;
    for (double j : jitters) sum += Lit(z0 + (z1 - z0) * j, lo, hi);   // ジッター位置で影を引く
    total += (z1 - z0) * sum / jitters.size();                          // 厚み × 平均の可視性
  }
  return total;
}
}  // namespace

int main() {
  std::printf("== froxel ==\n");
  const long long cells = static_cast<long long>(kNx) * kNy * kNz;
  std::printf("%d x %d x %d = %lld セル（720p の画素数 %d と同じ）\n", kNx, kNy, kNz, cells, 1280 * 720);
  std::printf("RGBA16F 1 枚: %.2f MiB、散乱 + 積分 + 履歴の 3 枚: %.2f MiB\n", cells * 8 / kMiB,
              3 * cells * 8 / kMiB);
  std::printf("影を引く回数: %lld 回 / フレーム（1080p の画素ごとレイマーチ 64 歩なら %.0f 回）\n", cells,
              1920.0 * 1080 * 64);

  std::printf("\nスライスの厚み（near %.1f m, far %.0f m, %d 層）\n", kNear, kFar, kNz);
  std::printf("スライス  手前端[m]  厚み[m]\n");
  for (int k : {0, 16, 32, 48, 63}) {
    std::printf("%5d    %8.2f  %7.3f\n", k, SliceStart(k), SliceStart(k + 1) - SliceStart(k));
  }

  std::printf("\n== 細い光の筋を、スライス中心 1 点で見る ==\n");
  std::printf("筋の位置は 25 m 付近。ここでのスライス厚: %.2f m\n", [] {
    int k = static_cast<int>(std::log(25.0 / kNear) / std::log(kFar / kNear) * kNz);
    return SliceStart(k + 1) - SliceStart(k);
  }());
  std::printf("筋の長さ w[m]  推定/真値: 中心1点(平均, 標準偏差)  ジッター 1 点/フレーム x 8 フレーム(平均, 標準偏差)\n");

  std::mt19937_64 rng(7);
  std::uniform_real_distribution<double> u(0.0, 1.0);
  for (double w : {0.25, 0.5, 1.0, 2.0, 4.0}) {
    std::vector<double> single, jittered;
    for (int trial = 0; trial < 20000; ++trial) {
      const double lo = 24.0 + u(rng) * 2.0;           // 筋の始まり。スライスとの位相をランダムにする
      const double hi = lo + w;
      single.push_back(Estimate(lo, hi, {0.5}) / w);     // 毎回、スライスの中心で引く
      // 8 フレーム。各フレームは別のジッター（0, 1/8, ... の層化したずれ + ランダム）で 1 点引き、平均する。
      std::vector<double> js;
      for (int f = 0; f < 8; ++f) js.push_back((f + u(rng)) / 8.0);
      jittered.push_back(Estimate(lo, hi, js) / w);
    }
    auto stats = [](const std::vector<double>& v) {
      double s = 0, s2 = 0;
      for (double x : v) { s += x; s2 += x * x; }
      const double m = s / v.size();
      return std::pair<double, double>(m, std::sqrt(std::max(0.0, s2 / v.size() - m * m)));
    };
    const auto a = stats(single), b = stats(jittered);
    std::printf("%6.2f         %5.2f, %5.2f                    %5.2f, %5.2f\n", w, a.first, a.second, b.first,
                b.second);
  }
  return 0;
}
```

```text title="実行結果"
== froxel ==
160 x 90 x 64 = 921600 セル（720p の画素数 921600 と同じ）
RGBA16F 1 枚: 7.03 MiB、散乱 + 積分 + 履歴の 3 枚: 21.09 MiB
影を引く回数: 921600 回 / フレーム（1080p の画素ごとレイマーチ 64 歩なら 132710400 回）
```

```text title="実行結果（続き）"
スライスの厚み（near 0.5 m, far 128 m, 64 層）
スライス  手前端[m]  厚み[m]
    0        0.50    0.045
   16        2.00    0.181
   32        8.00    0.724
   48       32.00    2.896
   63      117.38   10.623
```

```text title="実行結果（続き）"
== 細い光の筋を、スライス中心 1 点で見る ==
筋の位置は 25 m 付近。ここでのスライス厚: 2.23 m
筋の長さ w[m]  推定/真値: 中心1点(平均, 標準偏差)  ジッター 1 点/フレーム x 8 フレーム(平均, 標準偏差)
  0.25          1.12,  2.96                     1.00,  0.63
  0.50          1.13,  1.94                     1.00,  0.32
  1.00          1.11,  1.12                     1.00,  0.16
  2.00          1.00,  0.35                     1.00,  0.08
  4.00          1.07,  0.22                     1.00,  0.04
```

## 長所と短所

- 長所: 画素ごとのレイマーチより軽い。セルごとに 1 回影を引く。画面の解像度に依存しない。
- 長所: 密度が場所で変わる媒質、複数のライト、半透明の物体を同じ仕組みで扱える。
- 長所: 3D の補間で輪郭の不連続が出ない。時間方向の蓄積が 3D のほうが簡単。
- 短所: 解像度が低く細い筋は欠ける。指数の刻みで遠くほど粗い。
- 短所: 奥行きの分割による縞（[Quality and Performance](../volumetric-fog/quality.md)）が出る。
- 短所: メモリ（3D テクスチャ数枚）。環境光を足さないと影の中が暗すぎる。

## よくあるミス

??? failure "光の筋がちらつく"
    シャドウ マップを縮小せずに引いている。ESM に縮小し箱フィルターでぼかす。ジッターを入れたら時間方向の蓄積（履歴の重み 0.9 前後）も入れる。

??? failure "細い筋が消えるまたは太く出る"
    スライスの厚みが筋より厚い。ジッターを毎フレーム変えて履歴と混ぜる。それでも足りないならその場所だけシャドウ マップのレイマーチを足す（[Shadow Map Raymarching](shadowmap-march.md)）。

??? failure "遠くの霧が明るすぎる"
    区間の積分を `S × L` で足している。スライスが厚いと過大になる。`S (1 − e^(−σL)) / σ` を使う。

??? failure "影の中が真っ暗で、霧がない"
    環境光を入れていない。外向きの散乱だけが働いて暗くなりすぎる。定数でもよいので環境光を足す。

??? failure "動く物体の後ろに尾を引く"
    履歴の重みが大きすぎるまたは再投影が合っていない。前のフレームの froxel の外を読んだら履歴の重みを 0 にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] セルごとに影を 1 回引いて、奥行き方向に積分する。光の筋はおまけで出る。
    - [x] 影は ESM に縮小してぼかす。フォグは低周波でよい。
    - [x] 160 × 90 × 64 ＝ 720p の画素数。影の回数は約 144 分の 1。
    - [x] 細い筋は欠ける。ジッターと時間方向の蓄積で戻す。
    - [x] 全体で約 1.1 ms（Wronski の報告）。

## 参考

- Bart Wronski, "Volumetric Fog: Unified, Compute Shader Based Solution to Atmospheric Scattering", ACM SIGGRAPH 2014 Courses, Advances in Real-Time Rendering in Games, 2014. <https://advances.realtimerendering.com/s2014/wronski/bwronski_volumetric_fog_siggraph2014.pdf>（スライドとノートの本文を全部読んだ。図とビデオ、付録のコード画像は読めていない）
- Sébastien Hillaire, "Physically Based and Unified Volumetric Rendering in Frostbite", SIGGRAPH 2015（取得できず、読んでいない）
- Akenine-Möller ほか, "Real-Time Rendering", 4th Edition, CRC Press, 2018（読んでいない）

## 関連ページ

- [God Rays](index.md)
- [Volumetric Fog](../volumetric-fog/index.md)
- [Froxels](../volumetric-fog/froxel.md)
- [Shadow Map Raymarching](shadowmap-march.md)
- [Radial Blur](radial-blur.md)
