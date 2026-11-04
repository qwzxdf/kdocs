---
title: Refraction Boundary Problems
tags:
  - 描画
---

# Refraction Boundary Problems

窓ガラスの前に立つキャラクターを描くとガラスの内側にキャラクターの服の色がにじむことがあります。画面のコピーをずらして読む屈折（[Screen-Space Refraction](screen-space.md)）では、ずらした先に何があるかを読むまで知らないからです。このページではそのにじみの原因と画面の端やガラスの重なりで起きる別の破綻を、1 つずつ見ていきます。どれも完全には直りません。ただし原因が分かればどこまで直して、どこから割り切るかを数字で決められます。

!!! tip "ポイント"
    - 破綻の大半は「ずらした先が、ガラスの手前の物や画面の外に当たる」ことで起きる。
    - 手前の物は深度で見分けて、ずらしを戻す。硬く切り替えると輪郭が飛ぶので、短い幅でなだらかに戻す。
    - 画面の端はずらし量を端で弱める。弱める幅はずらし量以上にすると、読み先が画面の外に出ない。
    - ガラスの重なりはコピーが 1 枚の方式では解けない。重ねないか奥から順にコピーを取り直す。
    - いちばん効くのは、ずらし量を小さくすること。

!!! info "このページを読む前に"
    - [Refraction](index.md)（このセクション全体の地図と読む順番）
    - [Screen-Space Refraction](screen-space.md)（画面のコピーをずらして読む仕組み。このページはその「破綻」の側）

## なぜ破綻するのか {#why}

画面空間の屈折がしていることは次の 3 手です。不透明な物を描いて画面の色をコピーします。ガラスを描くときに画素ごとに法線から「ずらし量」を求めます。コピーをずらした位置で読みます。

ここで読み先の画素はガラスの画素と同じ画面の上にあるだけで、ガラスの向こうにある物とは限りません。ガラスの向こうの物はガラスの画素の位置（ずらす前）にあります。ずらした先には別の物が写っているかもしれません。それがガラスより手前の物だったときに手前の物の色がガラスの中に現れます。

<svg class="fig flow" viewBox="0 0 620 262" role="img" aria-label="画面をずらすと、視線がガラスの手前の人に当たる"><defs><marker id="b1-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#94a3b8"/></marker><marker id="b1-y" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#e5aa28"/></marker></defs><circle cx="40" cy="130" r="8" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="40" y="156" text-anchor="middle" font-size="12" fill="currentColor">カメラ</text><line x1="100" y1="60" x2="100" y2="210" stroke="#94a3b8" stroke-width="2"/><text x="100" y="52" text-anchor="middle" font-size="12" fill="currentColor">画面（コピー）</text><line x1="300" y1="70" x2="300" y2="160" stroke="#4c8bf5" stroke-width="5"/><text x="300" y="62" text-anchor="middle" font-size="12" fill="currentColor">ガラス（10 m）</text><rect x="180" y="165" width="40" height="65" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="200" y="248" text-anchor="middle" font-size="12" fill="currentColor">人（5 m）</text><line x1="560" y1="50" x2="560" y2="240" stroke="#94a3b8" stroke-width="3"/><text x="560" y="42" text-anchor="middle" font-size="12" fill="currentColor">壁（30 m）</text><line x1="40" y1="130" x2="545" y2="148" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#b1-a)" stroke-dasharray="5 4"/><text x="420" y="124" text-anchor="middle" font-size="12" fill="currentColor">ずらさずに読む視線 → 壁</text><line x1="40" y1="130" x2="200" y2="210" stroke="#e5aa28" stroke-width="2" marker-end="url(#b1-y)"/><circle cx="100" cy="160" r="3.5" fill="#e5aa28"/><text x="108" y="182" text-anchor="start" font-size="12" fill="currentColor">ずらした読み先</text><text x="330" y="232" text-anchor="start" font-size="12" fill="currentColor">ずらした視線は、手前の人に当たる</text><text x="320" y="20" text-anchor="middle" font-size="12" fill="currentColor">真上から見た図（左が手前、縦が画面の横方向）</text></svg>

図は真上から見た配置です。左がカメラで縦の線が画面（コピーのテクスチャ）です。ガラスの画素を画面の上でずらすとカメラから見た視線の向きが変わります。ずらした先の視線はガラスの手前に立つ人に当たっています。本物の屈折なら光はガラスの内側を通ってから壁へ向かうので、手前の人に当たることはありません。画面のコピーはその区別を持っていません。

## 手前の物がにじむ {#foreground}

### 数で見る {#numbers}

具体的に数えてみます。画面の幅を 1920 画素として、1 本の走査線だけを考えます。ガラスは 600〜1200 画素で、距離は 10 m とします。背後の壁は 30 m です。人はガラスの手前の 5 m にいて、1100〜1400 画素に立っています。人とガラスは 1100〜1200 画素で重なりますが、人のほうが手前なのでこの範囲のガラスは描かれません。ガラスが見えるのは 600〜1100 画素です。

ガラスは球のように曲がっているとして、法線の x をガラスの中心で 0、端で ±1 にします。ずらし量は「法線 x × 強さ × 画面幅」です。強さが 0.05 なら最大のずらしは 1920 × 0.05 ＝ 96 画素です。

人に近いガラスの画素では法線 x が 0.67 まであります。ここでのずらしは 0.67 × 96 ≒ 64 画素です。ガラスの 1050 画素目を読むと 1050 + 63 ≒ 1113 画素目に当たり、そこは人です。ずらした先が人に当たる画素は 1052〜1100 画素の 48 個になります。ガラスの見える部分は 500 画素なので、1 割弱の画素で人の色が混じることになります。

<svg class="fig flow" viewBox="0 0 660 190" role="img" aria-label="走査線の上で、ずらした先が人に当たる画素の範囲"><defs><marker id="b2-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#94a3b8"/></marker><marker id="b2-y" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#e5aa28"/></marker></defs><text x="20" y="18" text-anchor="start" font-size="12" fill="currentColor">1 本の走査線（画面の幅 1920 画素、強さ 0.05）</text><text x="20.0" y="34" text-anchor="start" font-size="12" fill="currentColor">壁（30 m）</text><text x="20.0" y="74" text-anchor="start" font-size="12" fill="currentColor">人（5 m）</text><text x="20.0" y="114" text-anchor="start" font-size="12" fill="currentColor">ガラスが見える範囲</text><text x="20.0" y="154" text-anchor="start" font-size="12" fill="currentColor">混入する画素</text><rect x="20.0" y="40" width="600.0" height="14" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><rect x="363.75" y="80" width="93.75" height="14" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="367.75" y="91" text-anchor="start" font-size="10" fill="currentColor">1100–1400</text><rect x="207.5" y="120" width="156.25" height="14" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="211.5" y="131" text-anchor="start" font-size="10" fill="currentColor">600–1100</text><rect x="348.75" y="160" width="15.0" height="14" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="342.75" y="172" text-anchor="end" font-size="10" fill="currentColor">1052–1100（48 画素）</text><line x1="360.625" y1="136" x2="379.6875" y2="94" stroke="#e5aa28" stroke-width="1.5" marker-end="url(#b2-y)"/><text x="387.6875" y="112" text-anchor="start" font-size="10" fill="currentColor">1090 → 1151（人）</text><line x1="332.5" y1="136" x2="342.5" y2="56" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#b2-a)"/><text x="324.5" y="108" text-anchor="end" font-size="10" fill="currentColor">1000 → 1032（壁）</text></svg>

### 深度で見分ける {#depth-check}

この混入は読み先の深度を見れば避けられます。ガラスは深度を書かない（深度テストだけして、書き込みはしない）ものとします。すると、不透明パスの深度バッファにはガラスの向こうにある物と手前にある物だけが入っています。読み先の深度がガラスの深度より小さい（近い）ならそこにはガラスの手前の物があります。その場合はずらさずに元の位置を読みます。元の位置はガラスの深度テストを通った画素なので、必ずガラスの向こうの物です。

```hlsl
// 読み先がガラスより手前なら、ずらしを戻す（最小の形）。
float glass_depth = LinearDepth(input.position.z);
float scene_depth = LinearDepth(g_scene_depth.SampleLevel(g_point_clamp, refract_uv, 0));
if (scene_depth < glass_depth) {
  refract_uv = screen_uv;
}
```

比べるのはリニアな距離です。`SV_Position.z` と深度バッファの値はどちらも 0〜1 に押しつぶされた非線形の値で、同じ側の値なら大小の比較はできます。ただし後で幅を [m] で決めたいので、リニアに直しておくほうが調整しやすくなります。

深度の読み方にも注意があります。深度の SRV はポイント サンプラーで読みます。リニア補間で読むと人の輪郭で、人の深度と壁の深度が混ざった値になりどちらでもない距離で比べてしまいます。

### 戻すと何が起きるか {#hard-switch}

さきの走査線で戻したあとの混入を数えると 0 になります。ところが、戻した画素と戻さない画素が隣り合う所で、読み先が急に飛びます。強さ 0.05 では隣の画素との間で最大 47 画素離れます。背後の壁がなめらかなら目立ちませんが、模様があるとそこで模様が切れて、ガラスの中に細い縦線のような境目が出ます。

強さを上げると飛びは大きくなります。0.02 で 22 画素、0.10 で 76 画素です。次の表がこの走査線の結果です。

| 強さ | 最大のずらし | 混入（そのまま） | 混入（戻す） | 最大の飛び |
| --- | --- | --- | --- | --- |
| 0.02 | 38 画素 | 23 | 0 | 22 画素 |
| 0.05 | 96 画素 | 48 | 0 | 47 画素 |
| 0.10 | 192 画素 | 78 | 0 | 76 画素 |

飛びを小さくするには戻すか戻さないかを 0 と 1 で決めず深度の差に応じて、少しずつ戻します。

```hlsl
// 差が 0 以上なら 1（ずらす）、-g_depth_fade 以下なら 0（戻す）。間は直線でつなぐ。
float keep = saturate((scene_depth - glass_depth) / g_depth_fade + 1.0);
refract_uv = lerp(screen_uv, refract_uv, keep);
```

`g_depth_fade` は戻す幅です。一例として 0.5 m とすると、ガラスの 0.5 m 手前から、ずらしが少しずつ弱まりガラスの深度に着いたとき完全にずらします。この幅の中にある物はガラスのすぐ手前の物（ガラスに触れている物、張りついた汚れなど）です。

<svg class="fig flow" viewBox="0 0 330 200" role="img" aria-label="手前の物を戻す重みの形"><text x="40" y="18" text-anchor="start" font-size="12" fill="currentColor">手前の物を戻す重み（幅 0.5 m）</text><line x1="40" y1="150" x2="280" y2="150" stroke="#94a3b8"/><line x1="160" y1="30" x2="160" y2="150" stroke="#94a3b8" stroke-dasharray="3 3"/><polyline points="40,150 100.0,150 160,30 280,30" fill="none" stroke="#4c8bf5" stroke-width="2.5"/><polyline points="40,150 160,150 160,30 280,30" fill="none" stroke="#e5aa28" stroke-width="1.5" stroke-dasharray="5 3"/><text x="40" y="166" text-anchor="middle" font-size="10" fill="currentColor">-1 m</text><text x="160" y="166" text-anchor="middle" font-size="10" fill="currentColor">0（ガラス）</text><text x="280" y="166" text-anchor="middle" font-size="10" fill="currentColor">+1 m</text><text x="34" y="38" text-anchor="end" font-size="10" fill="currentColor">1</text><text x="34" y="150" text-anchor="end" font-size="10" fill="currentColor">0</text><text x="44" y="80" text-anchor="start" font-size="10" fill="currentColor">手前</text><text x="276" y="80" text-anchor="end" font-size="10" fill="currentColor">奥</text><text x="40" y="184" text-anchor="start" font-size="10" fill="currentColor">青: なだらかに戻す　黄の破線: 0 か 1 で切り替え</text></svg>

ここで注意したいことがあります。さきの 1 本の走査線の実験では人の深度が 5 m と壁の深度が 30 m の 2 値しかないので、なだらかに戻しても結果は同じです。なだらかな切り替えが効くのは、深度が連続して変わる場所（ガラスに触れている地面や傾いた物）です。この部分は私の推測で実験では確かめていません。

### 別の方法：屈折面のマスク {#mask}

深度を使わない方法もあります。Sousa（GPU Gems 2、第 19 章）は不透明なシーンのコピーのアルファ チャンネルを使います。アルファを白でクリアして屈折する物を描いた所だけ黒で書きます。屈折する物のシェーダーはずらした先のアルファを見て、黒（＝屈折面の上）のときだけずらした先の色を使います。白（＝屈折面の外）のときはずらさない位置の色を使います。

仕組みが単純で深度を読まずに済みます。ただし、この仕組みから考えるとずらした先が屈折面の輪郭の外に出た画素は、手前の物でなくても戻されます。背後の壁が輪郭の外へ続いていても、屈折面の外は白なのでずらしが効きません。輪郭の近くで屈折が弱く見えるはずです。これは私が仕組みから考えたことで、実際に動かして確かめてはいません。Sousa の章も手前の物の色が背景の色に置き換わるので、アーティファクトが見えることがあると書いています。

深度の方法はずらした先が輪郭の外でも背後の物ならずらしを残せます。そのかわり深度バッファを SRV として読める形にしておく必要があります。

アルファのマスクはコピーにアルファ チャンネルがあれば足ります。深度の比較は読める深度バッファが要ります。手前の物を見分けられる点はどちらも同じです。

## 画面の端 {#screen-edge}

コピーは画面の大きさしかありません。ガラスの画素が画面の端に近いとずらした先が画面の外に出ます。クランプ サンプラー（`linear_clamp`）では端の画素が引き伸ばされた色になります。ラップ サンプラーだと反対側の端の色が出て、もっと目立ちます。

どのくらい端に近いと危ないかはずらし量で決まります。1920 画素の幅で強さが 0.05 なら端から 96 画素以内にあるガラスの画素は、画面の外を読む可能性があります。0.10 なら 192 画素です。

### 端で弱める {#fade-edge}

端に近づくほどずらし量を弱めれば、読み先は画面の外に出ません。端からの距離を `e`（UV）として、重みを `e / w` で 1 に頭打ちします。ずらしは「強さ × 重み」以下になるので、読み先が画面の内側にとどまる条件は `強さ × e / w ≤ e` です。これは `w ≥ 強さ` と同じです。

つまり、弱める幅 `w` を強さ以上にすれば、読み先は画面の外に出ません。強さが 0.05 なら幅は 0.05 以上です。サンプルの 0.1 はその倍の余裕があります。

<svg class="fig flow" viewBox="0 0 330 200" role="img" aria-label="画面の端でずらしを弱める重み"><text x="40" y="18" text-anchor="start" font-size="12" fill="currentColor">画面の端でずらしを弱める重み（幅 0.1）</text><line x1="40" y1="150" x2="300" y2="150" stroke="#94a3b8"/><polyline points="40,150 160.0,30 280.0,30" fill="none" stroke="#4c8bf5" stroke-width="2.5"/><line x1="100.0" y1="150" x2="100.0" y2="30" stroke="#e5aa28" stroke-dasharray="3 3"/><text x="40" y="166" text-anchor="middle" font-size="10" fill="currentColor">画面の端</text><text x="100.0" y="166" text-anchor="middle" font-size="10" fill="currentColor">0.05</text><text x="160.0" y="166" text-anchor="middle" font-size="10" fill="currentColor">0.1</text><text x="280.0" y="166" text-anchor="middle" font-size="10" fill="currentColor">0.2（UV）</text><text x="40" y="184" text-anchor="start" font-size="10" fill="currentColor">黄の線: 強さ 0.05。幅がこれ以上なら画面の外を読まない</text></svg>

弱める幅は広いほど安全ですが、画面の端でガラスの屈折がなくなる範囲も広がります。0.1 の幅は 1920 画素の画面で 192 画素にあたりそこでは屈折が少しずつ弱くなります。

### 画面より広く描く {#guard-band}

もうひとつの方法はシーンのコピーを画面より少し広く描いておくことです。上下左右に 5 % ずつ足すと面積は (1.1 × 1.1) ＝ 1.21 倍になります。1920 × 1080 なら 2112 × 1188 画素で、不透明パスを描くコストが 2 割ほど増えます。屈折の強い水面を画面いっぱいに出すゲームなら選ぶ価値がありますが、薄いガラスでは割に合いません。

薄いガラスではずらし量が小さいので、そもそも端の問題が目立ちません。強さが 0.02 なら影響があるのは端の 38 画素だけです。

## ガラスの向こうのガラス {#overlap}

コピーはガラスを描く前に 1 枚だけ取ります。向こうのガラスはそのコピーに入っていません。手前のガラスを描いても向こうのガラスの屈折は、映りません。

解くにはガラスを奥から手前の順に描いて、1 枚描くたびにコピーを取り直します。RGBA16F の 1920 × 1080 のコピーは、1 画素 8 バイトで 約 16.6 MB（15.8 MiB）です。コピーは読んで書くので 1 回で約 33 MB を動かします。ガラスが 3 枚重なればコピーは 3 回になります。

重なる枚数が決まっているならその分だけコピーを取り直すのも手です。決まっていないなら重ならないようにレベルを作るか 2 枚目以降は屈折をやめて、ふつうのアルファ ブレンドにします。Sousa も章のまとめで奥から手前の順に描いてメッシュごとにコピーを更新する案と、アルファ ブレンドで近似する案をあげています。

## 縁の黒い線とにじみ {#rim}

ガラスの縁は法線が視線に垂直に近くなります。法線の xy は大きいのでずらしも最大になります。縁の外側はガラスの外の物なので、ずらした先が輪郭の外の物に当たると、縁の周りに明るい輪や暗い輪ができます。MSAA や TAA で縁の画素が、ガラスと背景の混ざった色になると、さらに目立ちます。

対処は縁でずらしを弱めることです。法線と視線の内積（`saturate(dot(N, V))`）をずらし量に掛けます。縁では内積が 0 に近づくので、ずらしも 0 に近づきます。フレネルの反射は縁で強まる（[Fresnel](fresnel.md)）ので、縁の屈折が弱くなっても反射のほうが見えて、違和感が出にくくなります。

MSAA のレンダー ターゲットをコピーするときは、リゾルブしたあとのテクスチャを使います。リゾルブ前のコピーはそのままでは SRV として読めません。

## 地形と交わる線 {#intersection}

水面やガラスが地形や床と交わる線の近くでは、ガラスの深度と背後の物の深度の差が、ほとんど 0 になります。この付近ではずらした先の深度が、わずかにガラスより手前になるかどうかで、ずらす・戻すが細かく切り替わります。線がギザギザになります。

先ほどの深度の差に応じてなだらかに戻す方法は、この場所でいちばん効きます。ずらしの幅をそのまま交差の線の近くで弱める効果になるためです。そのうえで、岸辺に泡を重ねると交差の線自体が見えにくくなります（[Shore Foam: Depth Difference](../../water/shore-foam/shore-depth.md)）。深度の差で透明度を変える考え方は[Soft Particles](../blending-sorting/soft-particles.md) と同じです。

## 通して書くと {#complete}

ここまでを 1 本にしたピクセル シェーダーです。ずらし量の計算、縁の弱め画面の端の弱め手前の物の戻し、の順に書いています。「足した処理」と書いた所は資料の式ではなく、このページで考えた処理で定数は一例です。`fxc`（ps_5_0）でコンパイルして確かめました。実行して画面を確かめてはいません。

```hlsl
Texture2D<float4> g_scene_copy : register(t0);   // 不透明パスの色のコピー
Texture2D<float> g_scene_depth : register(t1);   // 不透明パスの深度（ガラスは書かない）
SamplerState g_linear_clamp : register(s0);
SamplerState g_point_clamp : register(s1);

cbuffer RefractionCB : register(b0) {
  float4x4 g_view;
  float2 g_inv_screen_size;     // 1 / (幅, 高さ)
  float g_refraction_strength;  // UV の最大ずらし量（一例: 0.05）
  float g_depth_fade;           // 深度差 [m] でずらしを戻す幅（一例: 0.5）
  float g_edge_width;           // 画面端で弱める幅（UV, 一例: 0.1）
  float g_near;
  float g_far;
  float g_pad;
  float3 g_tint;
};

// 通常の深度（0 が near, 1 が far）を、視点からの距離 [m] に直す。
float LinearDepth(float z) {
  return g_near * g_far / (g_far - z * (g_far - g_near));
}

struct PSInput {
  float4 position : SV_Position;
  float3 world_normal : NORMAL;
  float3 view_dir : TEXCOORD0;   // 視点 → 表面（ワールド）
};

float4 main(PSInput input) : SV_Target {
  float2 screen_uv = input.position.xy * g_inv_screen_size;

  // 1. 法線から、ずらし量を求める。
  float3 n = normalize(input.world_normal);
  float3 view_normal = mul((float3x3)g_view, n);
  float2 offset = view_normal.xy * g_refraction_strength * float2(1, -1);

  // 2. 縁（法線が視線に垂直）では弱める。足した処理。
  float facing = saturate(dot(n, -normalize(input.view_dir)));
  offset *= facing;

  // 3. 画面の端では弱める。足した処理。
  float2 edge_dist = min(screen_uv, 1.0 - screen_uv);
  offset *= saturate(min(edge_dist.x, edge_dist.y) / g_edge_width);

  float2 refract_uv = screen_uv + offset;

  // 4. 読み先がガラスより手前なら、ずらしを戻す。
  float glass_depth = LinearDepth(input.position.z);
  float scene_depth = LinearDepth(g_scene_depth.SampleLevel(g_point_clamp, refract_uv, 0));
  // 差が 0 以上なら 1（ずらす）、-g_depth_fade 以下なら 0（戻す）。間は直線でつなぐ。
  float keep = saturate((scene_depth - glass_depth) / g_depth_fade + 1.0);
  refract_uv = lerp(screen_uv, refract_uv, keep);

  float3 background = g_scene_copy.SampleLevel(g_linear_clamp, refract_uv, 0).rgb;
  return float4(background * g_tint, 1.0);
}
```

C++ の走査線の実験は次のとおりです。ガラスの画素ごとに読み先がガラスの手前になる数、戻したあとの混入、読み先の最大の飛びを数えます。MSVC（`/std:c++latest /W4`）でコンパイルして、実行しました。

```cpp
// 1 本の走査線で、屈折の読み先がガラスの手前の物に当たる画素を数える。
#include <algorithm>
#include <cmath>
#include <cstdio>

namespace {
constexpr int kWidth = 1920;          // 画面の幅 [px]
constexpr float kGlassDepth = 10.0f;  // ガラスの距離 [m]
constexpr float kWallDepth = 30.0f;   // 背後の壁 [m]
constexpr float kPersonDepth = 5.0f;  // ガラスの手前の人 [m]
constexpr int kGlassL = 600, kGlassR = 1200;    // ガラスの範囲
constexpr int kPersonL = 1100, kPersonR = 1400; // 人の範囲

// 不透明パスの深度（ガラスは深度を書かない）。
float OpaqueDepth(int x) {
  if (x >= kPersonL && x < kPersonR) return kPersonDepth;
  return kWallDepth;
}
bool InGlass(int x) { return x >= kGlassL && x < kGlassR; }
// ガラスを描く画素か（深度テストでガラスが人の奥なら描かれない）。
bool GlassVisible(int x) { return InGlass(x) && OpaqueDepth(x) > kGlassDepth; }

// 球のように曲がったガラス: 中心 0、端 ±1 の法線 x。
float NormalX(int x) {
  return (x - 0.5f * (kGlassL + kGlassR)) / (0.5f * (kGlassR - kGlassL));
}
int Clamp(int x) { return std::clamp(x, 0, kWidth - 1); }
}  // namespace

int main() {
  const float strengths[] = {0.02f, 0.05f, 0.10f};
  std::printf("strength  max_offset  bad(plain)  bad(hard)  jump(hard)\n");
  for (float s : strengths) {
    int bad_plain = 0, bad_hard = 0, jump = 0, prev_uv = -1;
    for (int x = 0; x < kWidth; ++x) {
      if (!GlassVisible(x)) { prev_uv = -1; continue; }
      int off = static_cast<int>(std::lround(NormalX(x) * s * kWidth));
      int uv = Clamp(x + off);
      float d = OpaqueDepth(uv);
      bool front = d < kGlassDepth;  // 読み先がガラスより手前
      if (front) ++bad_plain;
      // 硬い切り替え: 手前なら元の位置を読む。
      int uv_hard = front ? x : uv;
      if (OpaqueDepth(uv_hard) < kGlassDepth) ++bad_hard;
      if (prev_uv >= 0) jump = std::max(jump, std::abs(uv_hard - prev_uv));
      prev_uv = uv_hard;
    }
    std::printf("%.2f      %4d        %4d        %4d       %4d\n", s,
                static_cast<int>(std::lround(s * kWidth)), bad_plain, bad_hard, jump);
  }
  // 画面端: 端からの距離と最大ずらし量。
  for (float s : strengths) {
    int px = static_cast<int>(std::lround(s * kWidth));
    std::printf("strength %.2f: 端から %d px 以内の画素は、外を読む可能性がある\n", s, px);
  }
}
```

```text title="実行結果"
strength  max_offset  bad(plain)  bad(hard)  jump(hard)
0.02        38          23           0         22
0.05        96          48           0         47
0.10       192          78           0         76
strength 0.02: 端から 38 px 以内の画素は、外を読む可能性がある
strength 0.05: 端から 96 px 以内の画素は、外を読む可能性がある
strength 0.10: 端から 192 px 以内の画素は、外を読む可能性がある
```

この実験は 1 本の走査線で深度が 2 値の場面です。実際の画面では人の輪郭の外側でもずらした先が別の物に当たります。数字は「ずらし量が大きいほど混入と飛びが増える」ことを見るためのもので、実際のゲームの値ではありません。

## まとめ：境界の扱い

| 問題 | 原因 | 対策 |
| --- | --- | --- |
| [手前の物がにじむ](#foreground) | ずらした先がガラスの手前 | 深度で戻す |
| [画面の端](#screen-edge) | ずらした先が画面の外 | 端で弱める |
| [ガラスの重なり](#overlap) | コピーが 1 枚 | 奥から手前へコピーを取り直す |
| [縁のにじみ](#rim) | 縁でずらしが最大 | 縁で弱める |
| [地形との交差](#intersection) | 深度の差が 0 付近 | なだらかに戻す |

## よくあるミス

??? failure "ガラスの手前の物の色が、ガラスの中に映り込んで歪む"
    読み先の深度を比べていない。`scene_depth < glass_depth` のときずらしを戻す。深度を比べているのに直らないときはガラスが深度を書いていないかを確かめる。ガラスが深度を書くと深度バッファの値がガラス自身の深度になり比べても差が出ない。

??? failure "人の輪郭で、深度の比較が揺れる"
    深度をリニア補間のサンプラーで読んでいる。人と壁の深度が混ざった値はどちらの距離でもない。ポイント サンプラー（`SampleLevel` か `Load`）で読む。

??? failure "戻した所に縦の細い線が出る"
    0 と 1 で硬く切り替えている。深度の差に応じて `lerp` し戻す幅 `g_depth_fade` を 0.3〜0.5 m くらいにして試す（一例）。

??? failure "画面の端で、色が引き伸ばされる"
    端でずらし量を弱めていない。弱める幅をずらしの強さ以上にする。

??? failure "深度バッファを SRV にできず読めない"
    深度のテクスチャを `TYPELESS` の形式で作っていない。`R32_TYPELESS` で作って DSV は `D32_FLOAT`、SRV は `R32_FLOAT` にする。DSV と SRV を同時に使うなら読み取り専用の DSV（`D3D11_DSV_READ_ONLY_DEPTH`）を使う。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 屈折のにじみはずらした先の深度で見分けて戻す。
    - [x] 戻すときは深度の差に応じて、なだらかに戻す。
    - [x] 画面の端は弱める幅をずらしの強さ以上にする。
    - [x] 重なるガラスは奥から順にコピーを取り直すか割り切る。
    - [x] いちばん効く対策は、ずらし量を小さくすること。

## 参考

- Tiago Sousa, "Generic Refraction Simulation", GPU Gems 2, Chapter 19, Addison-Wesley, 2005. <https://developer.nvidia.com/gpugems/gpugems2/part-ii-shading-lighting-and-shadows/chapter-19-generic-refraction-simulation>（「手前の物」の節に、屈折面のマスクと重なるガラスの限界の話がある。NVIDIA の Web 版を取得して要点を確認した。全文とコードは読んでいない）
- Chris Wyman, "An Approximate Image-Space Approach for Interactive Refraction", ACM Transactions on Graphics 24(3), SIGGRAPH 2005（このページの作成時には読み直していない）
- Martin Mittring, "Finding Next Gen: CryEngine 2", SIGGRAPH 2007（読み直していない）
- 深度の比較、画面の端の弱め数値実験はこのページで考えた方法と計算で、上の資料の内容ではない

## 関連ページ

- [Refraction](index.md)
- [Screen-Space Refraction](screen-space.md)
- [Implementation Overview and Cost](implementation.md)
- [Fresnel](fresnel.md)
- [Dispersion](dispersion.md)
