---
title: Dithered Transparency
tags:
  - 描画
---

# Dithered Transparency

<strong>ディザ透明は規則的な点の模様（ディザ パターン）で、画素を間引いて半透明に見せる手法</strong>です。カメラに近づいた物体やキャラクターを隠す壁を、なめらかに消すのに使われます。このページではディザ透明の仕組みと使い所を説明します。

!!! tip "ポイント"
    - 規則的なパターンで、アルファに応じて画素を捨てる。
    - ソート不要・深度も書ける。
    - カメラ近くの物の、フェード アウトに便利。
    - ハッシュド アルファより、パターンが見える。

!!! info "このページを読む前に"
    - [Alpha Testing](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## ディザ透明
<strong>カメラに近づいた物を半透明にして向こうを見えるようにする</strong>（例：キャラの前の壁・木）ときに、ブレンドではなくディザ パターンで捨てる方法があります。

```hlsl
static const float kBayer4x4[16] = {
    0.0 / 16, 8.0 / 16, 2.0 / 16, 10.0 / 16,
    12.0 / 16, 4.0 / 16, 14.0 / 16, 6.0 / 16,
    3.0 / 16, 11.0 / 16, 1.0 / 16, 9.0 / 16,
    15.0 / 16, 7.0 / 16, 13.0 / 16, 5.0 / 16};

uint2 p = uint2(input.position.xy) % 4;
float threshold = kBayer4x4[p.y * 4 + p.x];
clip(fade_alpha - threshold);
```

不透明のまま深度も書きソートも不要で、半透明のような見た目になります（ゲームのカメラが、壁を透かす用途で定番）。

### ディザ透明の仕組み

ディザ透明は透明度を画素の点々の密度で表します。たとえば透明度 50 % なら、画素の半分を捨て残り半分を不透明に描きます。捨てる画素は画面上で規則的な模様（ベイヤー行列など）で決めます。ベイヤー行列は 4×4 の画素に 0〜1 のしきい値を割り当てた表で、アルファが各画素のしきい値より大きいときだけ残します。

```hlsl
static const float kBayer4x4[16] = {
   0.0 / 16,  8.0 / 16,  2.0 / 16, 10.0 / 16,
  12.0 / 16,  4.0 / 16, 14.0 / 16,  6.0 / 16,
   3.0 / 16, 11.0 / 16,  1.0 / 16,  9.0 / 16,
  15.0 / 16,  7.0 / 16, 13.0 / 16,  5.0 / 16 };

float threshold = kBayer4x4[(pixel.y % 4) * 4 + (pixel.x % 4)];
clip(alpha - threshold);
```

### 使いどころ：カメラ前の遮蔽物を透かす

最もよく使われるのはカメラとプレイヤーの間に入った壁や木を、近づくほど透かして消す表現です。距離に応じてアルファを下げディザで抜けば、ソートも深度の問題もなく不透明のまま（深度を書けるので、影やポストプロセスも正しく動きます）、自然にフェードアウトします。

### TAA と組み合わせる

規則的な模様はそのままだと網目が見えます。TAA を使うならフレームごとにしきい値の表をずらし（ベイヤー行列の代わりにブルー ノイズや、フレーム番号で回転した行列を使い）、TAA に平均させると網目が溶けて、滑らかな半透明に見えます（[Hashed Alpha](hashed-alpha.md) と同じ原理です）。

<!-- fig:dither-alpha:begin -->

<svg class="fig illust motion" data-fig="dither-alpha" viewBox="0 0 780 440" role="img"><rect x="0" y="0" width="780" height="440" rx="14" fill="#ffffff"/>
<defs><marker id="arr-dither-alpha" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">ディザ透明: アルファを上げると、閾値の小さい画素から順に不透明になる</text>
<rect x="150" y="90" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="150" y="90" width="58" height="58" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0864;0.0867;1.0000" values="0;0;1;1"/></rect>
<text x="179.0" y="125.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">0.03</text>
<rect x="212" y="90" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="212" y="90" width="58" height="58" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4413;0.4415;1.0000" values="0;0;1;1"/></rect>
<text x="241.0" y="125.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">0.53</text>
<rect x="274" y="90" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="274" y="90" width="58" height="58" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1751;0.1754;1.0000" values="0;0;1;1"/></rect>
<text x="303.0" y="125.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">0.16</text>
<rect x="336" y="90" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="336" y="90" width="58" height="58" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5300;0.5302;1.0000" values="0;0;1;1"/></rect>
<text x="365.0" y="125.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">0.66</text>
<rect x="150" y="152" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="150" y="152" width="58" height="58" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.6187;0.6190;1.0000" values="0;0;1;1"/></rect>
<text x="179.0" y="187.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">0.78</text>
<rect x="212" y="152" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="212" y="152" width="58" height="58" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2639;0.2641;1.0000" values="0;0;1;1"/></rect>
<text x="241.0" y="187.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">0.28</text>
<rect x="274" y="152" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="274" y="152" width="58" height="58" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.7074;0.7077;1.0000" values="0;0;1;1"/></rect>
<text x="303.0" y="187.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">0.91</text>
<rect x="336" y="152" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="336" y="152" width="58" height="58" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3526;0.3528;1.0000" values="0;0;1;1"/></rect>
<text x="365.0" y="187.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">0.41</text>
<rect x="150" y="214" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="150" y="214" width="58" height="58" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2195;0.2198;1.0000" values="0;0;1;1"/></rect>
<text x="179.0" y="249.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">0.22</text>
<rect x="212" y="214" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="212" y="214" width="58" height="58" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5743;0.5746;1.0000" values="0;0;1;1"/></rect>
<text x="241.0" y="249.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">0.72</text>
<rect x="274" y="214" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="274" y="214" width="58" height="58" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1308;0.1310;1.0000" values="0;0;1;1"/></rect>
<text x="303.0" y="249.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">0.09</text>
<rect x="336" y="214" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="336" y="214" width="58" height="58" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4856;0.4859;1.0000" values="0;0;1;1"/></rect>
<text x="365.0" y="249.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">0.59</text>
<rect x="150" y="276" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="150" y="276" width="58" height="58" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.7518;0.7520;1.0000" values="0;0;1;1"/></rect>
<text x="179.0" y="311.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">0.97</text>
<rect x="212" y="276" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="212" y="276" width="58" height="58" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3969;0.3972;1.0000" values="0;0;1;1"/></rect>
<text x="241.0" y="311.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">0.47</text>
<rect x="274" y="276" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="274" y="276" width="58" height="58" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.6630;0.6633;1.0000" values="0;0;1;1"/></rect>
<text x="303.0" y="311.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">0.84</text>
<rect x="336" y="276" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="336" y="276" width="58" height="58" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3082;0.3085;1.0000" values="0;0;1;1"/></rect>
<text x="365.0" y="311.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">0.34</text>
<text x="150" y="78" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">各画素の数字 = 閾値。アルファ &gt; 閾値 なら描く(黒)</text>
<text x="390" y="395" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">アルファ = 0.08 → 1 / 16 画素が不透明<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.1825;0.1828;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="395" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">アルファ = 0.25 → 4 / 16 画素が不透明<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1825;0.1828;0.3008;0.3011;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="395" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">アルファ = 0.42 → 7 / 16 画素が不透明<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3008;0.3011;0.4191;0.4194;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="395" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">アルファ = 0.58 → 9 / 16 画素が不透明<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4191;0.4194;0.5374;0.5376;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="395" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">アルファ = 0.75 → 12 / 16 画素が不透明<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5374;0.5376;0.6557;0.6559;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="395" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">アルファ = 0.92 → 15 / 16 画素が不透明<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.6557;0.6559;0.7739;0.7742;1.0000" values="0;0;1;1;0;0"/></text>
</svg>

<!-- fig:dither-alpha:end -->

## ディザリングとは

<strong>ディザリング</strong>は 限られた段階しか、表現できないときに小さな点の配置で、中間の濃さを表現する方法です。新聞の写真が黒い点の大きさと密度で、グレーを表すのと同じです。

透明の表現に使うと アルファ 0.5 を、画素の半分を描き半分を捨てることで、表します。半透明のブレンドを使わず深度を書き込み、ソートも不要で半透明に見せられます。

## ディザ パターン

画素ごとに <strong>しきい値</strong>を決めておき、アルファがそのしきい値を超えた画素だけ、描きます。

```text
アルファ 0.25      0.50          0.75
□□□□              ■□■□          ■■■■
□■□□              □■□■          ■□■■
□□□□              ■□■□          ■■■■
□□□■              □■□■          ■■□■
```

### ベイヤー行列（Bayer）

古典的なディザ パターンです（Bayer、1973）。規則的な行列でしきい値を決めます。

```hlsl
// 4×4 のベイヤー行列。値は 0〜15。16 で割って、0〜1 のしきい値にする。
static const float kBayer4x4[16] = {
     0.0,  8.0,  2.0, 10.0,
    12.0,  4.0, 14.0,  6.0,
     3.0, 11.0,  1.0,  9.0,
    15.0,  7.0, 13.0,  5.0};

float BayerThreshold(float2 screen_pos) {
  uint2 p = uint2(screen_pos) & 3;                        // 画素の座標の、下位 2 ビット
  return (kBayer4x4[p.y * 4 + p.x] + 0.5) / 16.0;
}

// ディザ透明: アルファが、しきい値より小さい画素を、捨てる。
void DitherClip(float2 screen_pos, float alpha) {
  clip(alpha - BayerThreshold(screen_pos));
}
```

| 特徴 | 内容 |
| --- | --- |
| 規則的 | 格子状のパターンが、見える。近くで見ると目立つ |
| 17 段階 | 4×4 では、17 段階（0〜16 個の画素）しか、表現できない |
| 安い | テーブル引きと、比較だけ |

### Interleaved Gradient Noise

Jimenez（2014）の、画面座標から安い式で疑似ランダムな、しきい値を作る方法です。ベイヤーより 規則性が目立ちません。

```hlsl
float IGN(float2 screen_pos) {
  return frac(52.9829189 * frac(dot(screen_pos, float2(0.06711056, 0.00583715))));
}
void DitherClipIGN(float2 screen_pos, float alpha) { clip(alpha - IGN(screen_pos)); }
```

### ブルー ノイズ

ブルー ノイズ（Ulichney、1988）は 低周波の成分が少なく点が均等に、散らばるノイズです。規則性もなくダマにもならずディザに、最適です。事前に作ったブルー ノイズの、テクスチャを画面にタイルして、しきい値として読みます（Georgiev と Fajardo、2016）。

```hlsl
Texture2D<float> g_blue_noise : register(t8);             // 64×64 など（R8_UNORM、タイルできる）

float BlueNoiseThreshold(float2 screen_pos) {
  return g_blue_noise.Load(int3(int2(screen_pos) & 63, 0));
}
```

| パターン | 見た目 | コスト | 段階 |
| --- | --- | --- | --- |
| ベイヤー 4×4 | 格子状。規則性が見える | 最小 | 17 |
| IGN | 規則性が目立たない | 小 | 実質、連続 |
| ブルー ノイズ | 最もなめらか。粒が均一 | 小（テクスチャ 1 回） | 実質、連続（64×64 なら 4,096 段階） |

## 用途 1：距離でフェードして消える

<strong>近づきすぎた物</strong>（カメラの前の木、柵）を ディザで消すと視界を塞がず、ポップもしません。

```hlsl
// カメラに近いほど、消える（ディザ フェード）。
float fade = saturate((distance_to_camera - near_fade_start) / (near_fade_end - near_fade_start));
clip(fade - BlueNoiseThreshold(input.position.xy));
```

## 用途 2：LOD の切り替え

<strong>2 つの LOD をディザで、混ぜて</strong>、切り替える。一方の描く画素ともう一方の、描く画素が補い合うようにしきい値を、反転させます。

```hlsl
// LOD A: fade が 1 → 0 に向かうとき、少しずつ、消える。
clip(fade_a - BlueNoiseThreshold(input.position.xy));
// LOD B: 同じしきい値で、反転（A が捨てた画素を、B が描く）。
clip((1.0 - fade_a) - (1.0 - BlueNoiseThreshold(input.position.xy)));   // = clip(BlueNoise - fade_a)
```

同じしきい値パターンを 2 つの LOD で、使うことが肝心です。A が描かない画素を B が描くので、重なりも穴もありません。

## 用途 3：半透明を安く

<strong>ソートできない大量の物</strong>（草、髪）のアルファをディザで近似します。深度に書き込めソートが不要です。

| 場面 | 内容 |
| --- | --- |
| 一時的なフェード | キャラクターの、出現・消滅 |
| 遠くの草 | 密度を距離で、間引く（ディザで画素単位に） |
| 透けるキャラ（ステルス） | 半透明風に |

## ディザの最大の問題：ざらつき

ディザは <strong>点の粗さ</strong>が見えます。1 画素の粒がちらちらして、ザラザラした見た目です。

| 対策 | 内容 |
| --- | --- |
| TAA（時間的アンチエイリアス） | ディザのパターンを、フレームごとにずらして TAA で、平均すると滑らかな半透明に見える（[TAA](../../postprocess/antialiasing/taa.md)） |
| ブルー ノイズ | 粒が均一で、ダマにならずザラつきが目立たない |
| 高解像度 | 画素が小さい（4K）ほど点が、目立たない |

TAA と組み合わせるときは、パターンをフレームごとにずらす（ノイズの座標に、フレーム番号に応じたオフセットを足す）。

```hlsl
// フレームごとに、ノイズの参照位置を、ずらす（TAA で、平均されて、なめらかに見える）。
float2 jitter = float2(frame_index * 17, frame_index * 31);
float threshold = g_blue_noise.Load(int3(int2(screen_pos + jitter) & 63, 0));
```

## よくあるミス

??? failure "ディザの点々が目立つ"
    <strong>TAA を併用</strong>する・ブルー ノイズを使う。

## これだけ覚える

!!! abstract "まとめ"
    - [x] パターンで間引いて、半透明に見せる
    - [x] カメラ近くのフェードに便利

## 参考

- Bayer, "An Optimum Method for Two-Level Rendition of Continuous-Tone Pictures", IEEE International Conference on Communications, 1973（ベイヤー行列によるディザ）
- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare", SIGGRAPH 2014, Advances in Real-Time Rendering in Games（Interleaved Gradient Noise）
- Ulichney, "Dithering with Blue Noise", Proceedings of the IEEE, Vol. 76, No. 1, 1988
- Georgiev, Fajardo, "Blue-Noise Dithered Sampling", SIGGRAPH 2016 Talks
- Wyman, McGuire, "Hashed Alpha Testing", Symposium on Interactive 3D Graphics and Games 2017

## 関連ページ

- [Alpha Testing](index.md)
- [Hashed Alpha](hashed-alpha.md)
