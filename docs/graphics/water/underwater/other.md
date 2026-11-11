---
title: Other Underwater Elements
tags:
  - 描画
---

# Other Underwater Elements

水中を霧と光の筋だけで作ると、画面は青くなりますが水の中にいる感じは出ません。地上との違いは空気中なら気にならない小さなものが、目に入るかどうかで決まります。漂う粒、上がっていく泡、画面のわずかなゆらぎこもった音です。

<strong>水中の雰囲気は霧や光に加えて粒子、色補正、音で作ります</strong>。このページでは浮遊粒子（マリン スノー）、泡、水の動き画面のゆがみ色補正、音、水に入る瞬間と出る瞬間の切り替えを説明します。

!!! tip "ポイント"
    - 浮遊粒子はカメラの周りの箱の中だけに置いて、箱の外へ出たら反対側へ戻します。数百個で無限に続く粒の海に見えます。
    - 泡はゆっくり上がって、深さに応じてふくらみます。水面で消します。
    - 画面のゆがみはごくわずかにします。強すぎると酔います。
    - 色補正は彩度とコントラストを下げて、青緑へ寄せます。
    - 音は高音を削ります。見た目の切り替えと同時に行います。
    - 水面をまたぐ切り替えは瞬時に行わず 0.2〜0.5 秒で補間します。

!!! info "このページを読む前に"
    - [Underwater Rendering](index.md)（このセクション全体の地図と、読む順番）

## 浮遊粒子（マリン スノー） {#marine-snow}

水中にはプランクトンの死骸、泥、微生物などの細かい粒がゆっくり漂っています。カメラの周りに小さな白い点を動かすだけで、水の中にいる感じが出ます。目安は次のとおりです。

- 数: 数百〜数千個です。
- 大きさ: 数ピクセルです。奥にあるほど小さくなります。
- 動き: ゆっくり漂ってゆっくり沈みます。流れのテクスチャがあればそれに乗せます。
- ライティング: 光の筋の中で明るく光ります（散乱）。影の中は暗くなります。
- 描画: 加算ブレンドかアルファ ブレンドの小さな板（ビルボード）です。

粒子を世界中に置くと数が足りません。カメラの周りの箱の中だけに置いて、箱の外へ出たものは反対側から再登場させます。

<svg class="fig flow" viewBox="0 0 720 260" role="img" aria-label="カメラの周りの箱の中で粒子を循環させる。箱の外へ出ると反対側に出る"><defs><marker id="uoA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">カメラの周りの箱で、粒子をループさせる（上から見た図）</text>
<rect x="210" y="46" width="300" height="190" fill="rgba(76,139,245,0.10)" stroke="#4c8bf5" stroke-width="2" stroke-dasharray="6 4"/>
<g fill="#e5aa28"><circle cx="260" cy="90" r="4"/><circle cx="330" cy="70" r="4"/><circle cx="440" cy="100" r="4"/><circle cx="290" cy="180" r="4"/><circle cx="470" cy="190" r="4"/><circle cx="400" cy="210" r="4"/></g>
<path d="M360,160 L340,128 L380,128 Z" fill="#e5484d"/><text x="360" y="182" text-anchor="middle" style="font-size:12px;font-weight:600">カメラ</text>
<line x1="450" y1="100" x2="500" y2="100" stroke="currentColor" stroke-width="2" marker-end="url(#uoA)"/>
<circle cx="518" cy="100" r="4" fill="none" stroke="#e5aa28" stroke-dasharray="2 2"/>
<line x1="550" y1="100" x2="520" y2="100" stroke="none"/>
<circle cx="222" cy="100" r="4" fill="#e5aa28" opacity="0.6"/>
<text x="560" y="96" style="font-size:12px">箱の右端を出ると</text><text x="560" y="114" style="font-size:12px">左端から再登場</text>
<text x="20" y="130" style="font-size:12px">反対側から</text><text x="20" y="148" style="font-size:12px">入ってくる</text>
<text x="360" y="254" text-anchor="middle" style="font-size:12px">箱は、カメラと一緒に動く。粒子の座標は、カメラとの相対位置で折り返す</text></svg>

頂点シェーダーが粒子の位置を時間から計算します。バッファは各粒子の初期位置と速度だけです。

```hlsl
cbuffer MarineSnowConstants : register(b0) {
  float4x4 g_view_proj;
  float3 g_camera_pos;
  float g_time;              // 秒
  float3 g_camera_right;     // ビルボード用。カメラの右方向
  float g_box_size;          // 箱の 1 辺（メートル）。例: 20
  float3 g_camera_up;        // ビルボード用。カメラの上方向
  float g_particle_size;     // 粒子の大きさ（メートル）。例: 0.02
};

struct Particle {
  float3 seed_pos;           // 0..1 の乱数（箱の中の初期位置）
  float _pad0;
  float3 velocity;           // 漂う速度（m/s）。例: (0.05, -0.08, 0.03)
  float brightness;          // 0..1。粒ごとの明るさ
};
StructuredBuffer<Particle> g_particles : register(t0);

struct MsOut {
  float4 pos : SV_Position;
  float2 uv : TEXCOORD0;
  float alpha : TEXCOORD1;
};

MsOut MarineSnowVS(uint vertex_id : SV_VertexID, uint instance_id : SV_InstanceID) {
  Particle p = g_particles[instance_id];

  // 箱の中の位置 + 速度 × 時間。カメラとの相対位置を、箱の幅で折り返す
  float3 world = p.seed_pos * g_box_size + p.velocity * g_time;
  float3 rel = world - g_camera_pos;
  rel -= g_box_size * floor(rel / g_box_size + 0.5);       // -box/2 .. +box/2 に収める

  // 箱の端では消える。端で急に出入りしてもポップしない
  float3 edge = abs(rel) / (g_box_size * 0.5);             // 0 = 中心、1 = 端
  float fade = 1.0 - smoothstep(0.7, 1.0, max(edge.x, max(edge.y, edge.z)));

  // ビルボードの板（ストリップ 4 頂点）。カメラ方向を向けて広げる
  float2 corner = float2(vertex_id & 1, vertex_id >> 1) * 2.0 - 1.0;
  float3 center = g_camera_pos + rel;
  float3 pos = center + (g_camera_right * corner.x + g_camera_up * corner.y) * g_particle_size;

  MsOut o;
  o.pos = mul(float4(pos, 1.0), g_view_proj);
  o.uv = corner * 0.5 + 0.5;
  o.alpha = fade * p.brightness;
  return o;
}

float4 MarineSnowPS(MsOut i) : SV_Target {
  float d = length(i.uv - 0.5) * 2.0;                      // 中心 0、縁 1
  float soft = saturate(1.0 - d * d);                      // 丸くぼかす
  return float4(float3(1, 1, 1) * soft * i.alpha, soft * i.alpha);   // 加算ブレンド用
}
```

`floor(rel / g_box_size + 0.5)` が折り返しの要です。`rel` が箱の外へ出ていれば箱の幅の整数倍だけ引いて、`−box/2〜+box/2` に戻します。`fmod` を使うと負の数で符号が反転する結果になるので、ここでは使いません。箱の中心はカメラの位置なので、カメラが動けば箱も動いて粒子は後ろへ流れていくように見えます。

箱の端は `fade` で消えます。箱の端で粒子が反対側へ飛ぶ瞬間を見えなくするためです。

数字で確かめます。箱の 1 辺が 20 m で、粒子が 1000 個なら密度は `1000 / 8000 m³ ＝ 0.125 個/m³` です。カメラの正面 5 m までの視野の中に数十個が見えます。数を増やすより箱を小さくした方が、近くの密度が上がります。

## 泡 {#bubbles}

泡はダイバーの吐く息、水に落ちた物の泡、船のスクリューの後ろの帯、火山の熱水など場面ごとに出ます。パーティクルで表現して上へ昇って、ゆらゆら揺れて水面で消えるようにします。

- 上昇速度は 0.2〜0.5 m/s が目安です。
- 揺れは左右の小さなサイン波にします。
- 水圧が下がると泡はふくらみます。

ふくらむ量はボイルの法則から見積もれます。水深が 10 m 増えるごとに圧力が約 1 気圧ずつ増えます。深さ `d` メートルの圧力は `1 + d / 10` 気圧です。泡の体積は圧力に反比例するので、半径は `(圧力)^(−1/3)` に比例します。深さ 10 m（2 気圧）から水面（1 気圧）まで上がると、体積が 2 倍で半径が `2^(1/3) ≒ 1.26` 倍になります。

```hlsl
struct Bubble {
  float3 pos;
  float age;                 // 秒
  float3 vel;                // 上向きの速度（m/s）
  float radius0;             // 発生時の半径（メートル）。例: 0.01
  float depth0;              // 発生時の水深（メートル）
  float3 _pad;
};

RWStructuredBuffer<Bubble> g_bubbles : register(u0);

cbuffer BubbleConstants : register(b1) {
  float g_dt;
  float g_water_surface_y;   // 水面の高さ（ワールド y）
  float g_sway_amount;       // 揺れの大きさ（メートル）。例: 0.03
  uint g_count;
};

// 泡の半径。深さ d（メートル）での値。圧力は 1 + d / 10（気圧）
float BubbleRadius(float radius0, float depth0, float depth) {
  float p0 = 1.0 + depth0 / 10.0;
  float p = 1.0 + max(depth, 0.0) / 10.0;
  return radius0 * pow(p0 / p, 1.0 / 3.0);
}

[numthreads(64, 1, 1)]
void BubbleCS(uint3 id : SV_DispatchThreadID) {
  if (id.x >= g_count) return;
  Bubble b = g_bubbles[id.x];

  b.age += g_dt;
  b.pos += b.vel * g_dt;                                     // 上昇
  // 左右に揺れる。泡ごとに位相をずらす（age と pos.y で決まる）
  b.pos.x += sin(b.age * 5.0 + b.pos.y * 3.0) * g_sway_amount * g_dt * 5.0;
  b.pos.z += cos(b.age * 4.0 + b.pos.y * 2.0) * g_sway_amount * g_dt * 5.0;

  // 水面に着いたら、発生時の位置へ戻して再利用する（足した処理。実際は別バッファで発生管理）
  if (b.pos.y >= g_water_surface_y) {
    b.pos.y = g_water_surface_y - b.depth0;
    b.age = 0.0;
  }
  g_bubbles[id.x] = b;
}
```

水面で泡を消す処理は簡単にするために発生時の深さへ戻して再利用しています。実際のゲームでは発生を別のパス（イベントで追加するリスト）で管理します。描画側は `BubbleRadius` を使って深さに応じた大きさで板を描きます。見た目は半透明の丸で縁が明るく、中心が透けて小さなハイライトを置くと泡らしく見えます。

## 水の動き {#motion}

水中では水の流れで海藻がゆらゆら揺れて、物がわずかに漂います。

- 海藻やサンゴは頂点シェーダーでゆっくり揺らします（[Wind](../../terrain/vegetation/wind.md) と同じ方法を、ゆっくり大きな波長で）。
- 魚の群れはボイド（群れのアルゴリズム）で動かします。GPU なら数千匹を動かせます。
- 浮かぶごみは水の流れに沿って、ゆっくり動かします。

水中の動きは空気中よりはるかにゆっくりで、周期も長くなります。同じ式を使って速さの係数を小さくします。

## 画面のゆがみ・色補正 {#post}

カメラが水の中に入ると画面全体がゆらゆらとゆがんで見えます（光が波打つ水の中を通るため）。ポストプロセスで画面の座標をわずかにずらします。色補正も同じパスで行います。

```hlsl
Texture2D<float4> g_scene : register(t0);
SamplerState g_linear_clamp : register(s0);

cbuffer UnderwaterPostConstants : register(b2) {
  float g_post_time;
  float g_wobble;            // ゆがみの強さ（UV 単位）。例: 0.002
  float g_saturation;        // 彩度の倍率。例: 0.7
  float g_contrast;          // コントラストの倍率。例: 0.85
  float3 g_tint;             // 色を寄せる先。例: (0.55, 0.85, 0.9)
  float g_tint_amount;       // 寄せる強さ 0..1。例: 0.35
  float g_vignette;          // 周辺減光の強さ。例: 0.5
  float3 _pad;
};

float4 UnderwaterPostPS(float4 pos : SV_Position, float2 uv : TEXCOORD0) : SV_Target {
  // ① ゆがみ: ゆっくりした 2 つのサイン波で、UV をわずかにずらす
  float2 wobble = float2(sin(uv.y * 20.0 + g_post_time * 1.5),
                         cos(uv.x * 20.0 + g_post_time * 1.2)) * g_wobble;
  float3 color = g_scene.SampleLevel(g_linear_clamp, uv + wobble, 0).rgb;

  // ② 彩度を下げる: 輝度との間を補間する（1 未満で灰色へ近づく）
  float luma = dot(color, float3(0.2126, 0.7152, 0.0722));
  color = lerp(luma.xxx, color, g_saturation);

  // ③ コントラストを下げる: 中間の灰色（0.5）を軸にして、縮める
  color = (color - 0.5) * g_contrast + 0.5;

  // ④ 青緑へ寄せる: 色合いを掛けて混ぜる
  color = lerp(color, color * g_tint, g_tint_amount);

  // ⑤ 周辺減光: 画面の端を暗くして、閉じた視界の印象を作る
  float2 d = uv - 0.5;
  float vig = 1.0 - g_vignette * dot(d, d) * 2.0;
  return float4(color * saturate(vig), 1.0);
}
```

ゆがみの強さ `g_wobble` は 0.002（画面の幅の 0.2 %）程度に抑えます。1920 ピクセルの幅なら約 4 ピクセルのずれです。強すぎると酔う人が出ます。

色補正は彩度とコントラストを下げて、青緑へ寄せます。これは赤が水に吸収されて霧でコントラストが落ちるという水中の見え方に合わせた調整です。さらに、周辺減光を強めると暗く閉じた視界の印象になります。遠くを被写界深度でぼかすと水の濁りの表現が加わります。カラー グレーディングの LUT を水に入った瞬間に切り替える（または補間する）方法でも、同じ効果が出ます（[Color Grading](../../postprocess/color-grading/index.md)）。

!!! note "確かめた範囲"
    HLSL は `fxc` で、`MarineSnowVS`・`MarineSnowPS`（`vs_5_0`、`ps_5_0`）、`BubbleCS`（`cs_5_0`）、`UnderwaterPostPS`（`ps_5_0`）をコンパイルしてエラーが出ないことを確かめました。GPU での描画は確認していません。

## 音 {#audio}

見た目だけでなく音も水中の雰囲気を大きく変えます。水中では高音が削られてこもった音になります。ローパス フィルタ（低い周波数だけを通すフィルタ）をかけて作ります。

最も簡単なフィルタは 1 次のローパス（1 極）です。サンプリング周波数を `fs`、カットオフ周波数を `fc` として、係数を次のように決めます。

```text
a = 1 − exp(−2π · fc / fs)
y[n] = y[n−1] + a · (x[n] − y[n−1])
```

`fs = 48000` Hz、`fc = 800` Hz なら `a = 1 − exp(−0.1047) ≒ 0.099` です。800 Hz より高い音が徐々に弱まります。カットオフ周波数は水中の見た目に合わせて、数百 Hz から 1〜2 kHz の間で決めます。値は一例です。

そのほかの音の要素は次のとおりです。

- 水の低いごぼごぼという環境音と泡の音を重ねます。
- 水面の上の音は小さくこもって聞こえます。逆に、水面の上から見ると水中の音はほぼ聞こえません。

水に入る境目でフィルタをなめらかに切り替えると、水中に入った感じが出ます。多くのオーディオ ミドルウェアはフィルタの係数をパラメーターとして持っているので、水深や水中かどうかで補間します。

## 水に入る瞬間と出る瞬間 {#transition}

水に入る瞬間は水しぶきと泡、画面の水滴、音のフィルタ、霧と色補正の切り替えが一度に起きます。水から出る瞬間は画面を水が流れ落ちて（レンズの水滴）、音、霧、色補正が元に戻ります。

瞬間的に切り替えると不自然です。水面をまたぐ間（0.2〜0.5 秒）で、補間します（[The Underside of the Surface and Crossing It](surface-back.md)）。

<svg class="fig flow" viewBox="0 0 720 230" role="img" aria-label="水に入ると、水中の度合いが 0 から 1 へ補間され、霧・色補正・音のフィルタが同時に変わる"><defs><marker id="uoB" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">水に入る: 水中の度合い（0 → 1）を 0.3 秒で補間する</text>
<line x1="60" y1="190" x2="680" y2="190" stroke="currentColor" stroke-width="1.5" marker-end="url(#uoB)"/><line x1="60" y1="190" x2="60" y2="50" stroke="currentColor" stroke-width="1.5"/>
<text x="680" y="212" text-anchor="end" style="font-size:12px">時間</text><text x="52" y="56" text-anchor="end" style="font-size:12px">1</text><text x="52" y="194" text-anchor="end" style="font-size:12px">0</text>
<path d="M60,190 L260,190 C300,190 330,60 380,60 L680,60" fill="none" stroke="#4c8bf5" stroke-width="3.5"/>
<line x1="260" y1="60" x2="260" y2="190" stroke="#94a3b8" stroke-dasharray="4 4"/><line x1="380" y1="60" x2="380" y2="190" stroke="#94a3b8" stroke-dasharray="4 4"/>
<text x="260" y="208" text-anchor="middle" style="font-size:12px">水面をまたぐ</text><text x="380" y="208" text-anchor="middle" style="font-size:12px">0.3 秒後</text>
<text x="400" y="100" style="font-size:12px">この 1 つの値で、霧の濃さ・</text><text x="400" y="118" style="font-size:12px">彩度・色味・音のカットオフを</text><text x="400" y="136" style="font-size:12px">まとめて補間する</text></svg>

「水中の度合い」を 1 つの値にして霧、色補正、音のフィルタが全部その値で動くようにします。パラメーターごとに別々のタイマーを持つと切り替えのタイミングがずれて、見た目と音がちぐはぐになります。

## よくあるミス {#mistakes}

??? failure "水中なのに、地上と同じ雰囲気に見える"
    原因は霧しか切り替えていないことです。粒子、色補正、音も水中用に切り替えます。それぞれが小さくても全部そろうと水の中という印象が強くなります。

??? failure "浮遊粒子が、カメラを動かしたときに画面に張り付く"
    原因は粒子の位置を世界の座標でなくカメラ基準で動かしていることです。箱はカメラと一緒に動かして粒子の座標は世界の座標のままカメラとの相対位置で折り返します。

??? failure "箱の端で、粒子がポンと出たり消えたりする"
    原因は折り返す瞬間に粒子が不連続に飛ぶのに、フェードしていないことです。箱の端の近くでアルファを 0 に落とします（`fade`）。

??? failure "画面のゆがみで酔う"
    原因は `g_wobble` が大きすぎることです。0.002 程度から始めて周期を遅くします。画面の中心付近だけを小さくするのも有効です。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 浮遊粒子はカメラの周りの箱でループさせます。端でフェードします。
    - [x] 泡は深さが減るほど大きくなります（深さ 10 m から水面で半径 1.26 倍）。
    - [x] 色補正は彩度とコントラストを下げて青緑に寄せます。ゆがみは小さくします。
    - [x] 音はローパス フィルタでこもらせます。
    - [x] 水中の度合いを 1 つの値にして、0.2〜0.5 秒でまとめて補間します。

## 参考 {#references}

このページは次の資料を読まずに書きました。泡の大きさの見積もりはボイルの法則から自分で導きました。HLSL は `fxc` でのコンパイルまで確かめています。

- Guardado, Sánchez-Crespo, "Rendering Water Caustics", GPU Gems, Chapter 2, 2004
- Mitchell, "Light Shafts: Rendering Shadows in Participating Media", Game Developers Conference 2004
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018
- Reynolds, "Flocks, Herds, and Schools: A Distributed Behavioral Model", SIGGRAPH 1987（ボイド（群れ）の原典）

## 関連ページ

- [Underwater Rendering](index.md)
- [Color Grading](../../postprocess/color-grading/index.md)
