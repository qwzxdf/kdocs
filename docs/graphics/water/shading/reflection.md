---
title: Water Reflection
tags:
  - 描画
---

# Water Reflection

水面には空、雲、遠くの山、岸の建物が映ります。映り込みがないと水面はただの青い板に見えます。ところが、反射の取り方にはそれぞれ弱点があります。環境マップは近くの物が映らず SSR は画面の外が映らず平面反射は波で乱れた反射が作れません。

<strong>水の反射は 1 つの方法では足りないので、SSR（または平面反射）で近くを環境マップで空と遠景を映して、フォールバックで重ねます</strong>。反射の強さはフレネルで決めます。このページでは反射の取り方の比較、重ね方、反射方向の作り方（地平線の下を向く問題の実測つき）、平面反射の鏡像カメラ（実行して確認）、空の反射、合成を説明します。

!!! tip "ポイント"
    - 空は環境マップ（キューブマップ）で、周囲の物は SSR か平面反射で映します。
    - フォールバックの順は SSR（または平面反射）、環境マップです。
    - 波の法線で反射方向をずらすと歪みが出ます。遠くの水面では法線を弱めて安定させます。
    - 浅い角度では波の法線の少しの傾きで、反射が地平線の下を向きます。仰角 3°、傾きの標準偏差 0.05 で、約 30 % でした。
    - 反射の強さはフレネルで決めます。真上から見ると約 0.02 で、遠くほど強くなります。

!!! info "このページを読む前に"
    - [Water Shading](index.md)（このセクション全体の地図と読む順番）

## 反射の取り方 {#methods}

- 環境マップ（キューブマップ）は空と遠景を映します。コストは小さいですが近くの物（船、岸の建物）が映りません。
- 平面反射は水面の上にあるすべてを映します。シーンをもう一度描くのでコストは大きく、波で乱れた反射は作れません（ごまかします）。
- SSR は画面に映っているものを映します。コストは中くらいで画面の外が映らず水平に近い視線では、画面の端から反射が消えます。
- レイトレーシングはすべてを映します。対応する GPU が必要です。

## 重ね方: フォールバック {#fallback}

実際のゲームでは 1 つだけでは足りないので、重ねます。基本は環境マップで空と遠景を安定して映します。その上に SSR を足して近くの岸辺や船、橋の映り込みを出します。

<svg class="fig flow" viewBox="0 0 720 220" role="img" aria-label="反射のフォールバック。SSR で当たれば使い、外れたら環境マップ。フレネルで強さを決める"><defs><marker id="wrA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">反射の重ね方</text>
<g stroke-width="2"><rect x="20" y="50" width="180" height="64" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><rect x="250" y="50" width="180" height="64" rx="9" fill="rgba(229,170,40,0.3)" stroke="#e5aa28"/><rect x="480" y="50" width="220" height="64" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/></g>
<g style="font-size:12px;font-weight:600" text-anchor="middle"><text x="110" y="76">① SSR / 平面反射</text><text x="340" y="76">② 環境マップ（空）</text><text x="590" y="76">③ フレネルで水の色と混ぜる</text></g>
<g style="font-size:11px" text-anchor="middle"><text x="110" y="96">近くの物。当たれば使う</text><text x="340" y="96">当たらない画素の穴を埋める</text><text x="590" y="96">F = 0.02 + (1−0.02)(1−cosθ)^5</text></g>
<g stroke="currentColor" stroke-width="2" marker-end="url(#wrA)"><line x1="200" y1="82" x2="250" y2="82"/><line x1="430" y1="82" x2="480" y2="82"/></g>
<text x="360" y="160" text-anchor="middle" style="font-size:12px">画面外や画面端で SSR が外れた画素は、環境マップへフェードで戻す</text>
<text x="360" y="182" text-anchor="middle" style="font-size:12px">穏やかな湖や池なら、平面反射が品質で勝つ。波のある海は、平面反射の鏡像を法線の XZ で歪ませる</text></svg>

SSR が当たらなかった画素（画面外や画面端）は、環境マップへフェードで戻します（[SSR Fallback and Compositing](../../reflections/ssr-fallback.md)）。湖や池のように水面が完全に平らな場合は、平面反射が品質で勝ります。波のある海は法線が場所ごとに違い反射方向がバラバラになるので、平面反射の鏡像を波の法線の XZ 成分で歪ませて使います。

## 反射方向の作り方 {#direction}

反射の方向は波の法線から計算します（`reflect(−V, N)`）。波で法線が傾くので反射が揺れて、歪みます。

### 地平線の下を向く反射

波の法線が傾いて反射の向きが水面の下を向くことがあります。空が映る環境マップの下半分（地面）を読むことになって、黒や不自然な色が出ます。遠くの水面ほど起きやすいです。視線が水平に近いので法線の少しの傾きで、反射が下を向きます。

測りました。視線が水面に対して仰角 `α` で入るとして、法線の傾き（x と z の勾配）を標準偏差 `σ` の正規乱数にして、反射ベクトルの `y` が負になる割合を 20 万回の試行で求めました。

<svg class="fig flow" viewBox="0 0 720 260" role="img" aria-label="視線の仰角と法線の傾きごとの、反射が地平線の下を向く割合"><text x="14" y="22" class="fig-title">反射が地平線の下を向く割合（実測）</text>
<line x1="60" y1="200" x2="690" y2="200" stroke="currentColor" stroke-width="1.5"/>
<g stroke-width="2"><rect x="90" y="199" width="26" height="1" fill="rgba(76,139,245,0.28)" stroke="#4c8bf5"/><rect x="120" y="199" width="26" height="1" fill="rgba(229,170,40,0.3)" stroke="#e5aa28"/><rect x="150" y="199" width="26" height="1" fill="rgba(229,72,77,0.28)" stroke="#e5484d"/><rect x="180" y="190" width="26" height="10" fill="rgba(60,160,90,0.3)" stroke="#3ca05a"/>
<rect x="260" y="199" width="26" height="1" fill="rgba(76,139,245,0.28)" stroke="#4c8bf5"/><rect x="290" y="190" width="26" height="10" fill="rgba(229,170,40,0.3)" stroke="#e5aa28"/><rect x="320" y="153" width="26" height="47" fill="rgba(229,72,77,0.28)" stroke="#e5484d"/><rect x="350" y="115" width="26" height="85" fill="rgba(60,160,90,0.3)" stroke="#3ca05a"/>
<rect x="430" y="125" width="26" height="75" fill="rgba(76,139,245,0.28)" stroke="#4c8bf5"/><rect x="460" y="70" width="26" height="130" fill="rgba(229,170,40,0.3)" stroke="#e5aa28"/><rect x="490" y="55" width="26" height="145" fill="rgba(229,72,77,0.28)" stroke="#e5484d"/><rect x="520" y="48" width="26" height="152" fill="rgba(60,160,90,0.3)" stroke="#3ca05a"/></g>
<g style="font-size:12px" text-anchor="middle"><text x="145" y="222" style="font-weight:600">仰角 30°</text><text x="315" y="222" style="font-weight:600">10°</text><text x="485" y="222" style="font-weight:600">3°</text></g>
<g style="font-size:11px"><text x="570" y="70">凡例（左から）傾きの標準偏差</text><text x="570" y="88" style="fill:#4c8bf5">0.02</text><text x="610" y="88" style="fill:#b7791f">0.05</text><text x="650" y="88" style="fill:#e5484d">0.1</text><text x="570" y="106" style="fill:#3ca05a">0.2（緑）</text></g>
<text x="360" y="246" text-anchor="middle" style="font-size:12px">仰角 3°、傾き 0.05 で 30 %、0.1 で 40 %。浅い角度ほど、傾きが小さくても下を向く</text></svg>

仰角 30° では傾きが 0.1 でも 0.4 % しかなく、0.2 で 9.9 % です。仰角 10° では傾き 0.05 で 4.2 %、0.1 で 19.4 % です。仰角 3° では傾き 0.02 で 9.4 %、0.05 で 30.1 %、0.1 で 39.7 % になります。仰角 1° では傾き 0.02 でも 33.1 % です。遠くの水面ではほとんどの反射が下を向く可能性があります。

対策は 2 つです。反射の向きの `y` を小さな正の値で下限にして、水平近くへ押し戻します。遠くでは波の法線を平らに弱めます（[Computing Normals](../waves/normals.md)）。

## シェーダー {#shader}

SSR の結果、環境マップ、フレネルを 1 つのシェーダーにまとめます。

```hlsl
TextureCube<float4> g_sky_cube : register(t0);          // 空の環境マップ（ミップつき）
Texture2D<float4> g_ssr : register(t1);                 // SSR の結果（rgb = 色、a = 信頼度 0..1）
Texture2D<float4> g_planar : register(t2);              // 平面反射（鏡像カメラで描いたもの）
Texture2D<float4> g_refraction : register(t3);          // 屈折（水の下の色）
SamplerState g_linear_clamp : register(s0);

cbuffer WaterReflectionConstants : register(b0) {
  float3 g_camera_position;
  float g_distortion;         // 平面反射の歪みの強さ。例: 0.03
  float2 g_screen_size;
  float g_roughness;          // 0..1。大きいほど、環境マップのぼけたミップを読む
  float g_max_sky_mip;        // 環境マップの最大ミップ番号。例: 8
  float g_use_planar;         // 1 = 平面反射、0 = SSR
  float g_f0;                 // 水の垂直入射の反射率。0.02
  float2 _pad;
};

float4 WaterReflectionPS(float4 pos : SV_Position, float3 world_pos : TEXCOORD0,
                         float3 wave_normal : TEXCOORD1) : SV_Target {
  float3 n = normalize(wave_normal);
  float3 v = normalize(world_pos - g_camera_position);            // カメラから水面へ
  float2 screen_uv = pos.xy / g_screen_size;

  // ① 反射方向。地平線の下を向いたら、水平近くへ押し戻す
  float3 reflect_dir = reflect(v, n);
  reflect_dir.y = max(reflect_dir.y, 0.02);
  reflect_dir = normalize(reflect_dir);

  // ② 空: 環境マップ。粗さに応じたミップを読む
  float3 sky = g_sky_cube.SampleLevel(g_linear_clamp, reflect_dir, g_roughness * g_max_sky_mip).rgb;

  // ③ 近くの物: SSR（信頼度つき）か、平面反射（波の法線で歪ませる）
  float3 near_color;
  float near_confidence;
  if (g_use_planar > 0.5) {
    float2 reflect_uv = screen_uv + n.xz * g_distortion;
    reflect_uv.x = 1.0 - reflect_uv.x;                              // 鏡像なので左右を反転する（実装による）
    near_color = g_planar.SampleLevel(g_linear_clamp, reflect_uv, 0).rgb;
    near_confidence = 1.0;
  } else {
    float4 ssr = g_ssr.SampleLevel(g_linear_clamp, screen_uv, 0);
    near_color = ssr.rgb;
    near_confidence = ssr.a;                                        // 当たらなければ 0
  }
  float3 reflection = lerp(sky, near_color, near_confidence);       // 当たらない画素は環境マップ

  // ④ フレネルで、屈折（水の下）と混ぜる
  float cos_theta = saturate(dot(n, -v));
  float fresnel = g_f0 + (1.0 - g_f0) * pow(1.0 - cos_theta, 5.0);
  float3 refraction = g_refraction.SampleLevel(g_linear_clamp, screen_uv, 0).rgb;
  return float4(lerp(refraction, reflection, fresnel), 1.0);
}
```

①の `max(reflect_dir.y, 0.02)` が地平線の下を向く問題への対策です。`v` がカメラから水面へ向かう向きなので `reflect(v, n)` で、反射が得られます。

## 平面反射 {#planar}

水面はほぼ平らです。水面を鏡としてカメラを水面の反対側に置いた仮想のカメラで、シーンをもう一度描くと正確な反射が得られます。

```text
 実際のカメラ ●
                 ╲
 ━━━━━━━━━━━━━━━━ 水面（y = h）
                 ╱
 鏡像のカメラ  ●   ← 水面について反対側
```

鏡像のカメラは `XMMatrixReflect` で作れます。MSVC（DirectXMath）で実行して確かめました。水面 `y = 2`、カメラ位置 `(1, 5, 2)`、視線 `(0, −0.6, 0.8)` なら鏡像の位置は `(1, −1, 2)`（`y` が `2h − y`）、視線は `(0, 0.6, 0.8)`（`y` だけ反転）で、上向きは `(0, −1, 0)` に反転します。鏡映の行列式は `−1` で向きが反転します。そのため、三角形の巻き順（カリング）を反転するか画像を上下反転して使います。

```cpp
#include <DirectXMath.h>

using namespace DirectX;

// 水面 y = h を鏡にした、鏡像のカメラ（位置と視線方向）を作る
struct MirrorCamera { XMFLOAT3 position, forward, up; };

MirrorCamera MakeMirrorCamera(XMFLOAT3 pos, XMFLOAT3 forward, XMFLOAT3 up, float water_height) {
  // 平面 (0, 1, 0, -h): y - h = 0。XMMatrixReflect はこの平面に対する鏡映の行列
  const XMMATRIX reflect = XMMatrixReflect(XMVectorSet(0, 1, 0, -water_height));
  MirrorCamera m;
  XMStoreFloat3(&m.position, XMVector3TransformCoord(XMLoadFloat3(&pos), reflect));       // 点は 2h - y
  XMStoreFloat3(&m.forward, XMVector3TransformNormal(XMLoadFloat3(&forward), reflect));   // 方向は y 成分だけ反転
  XMStoreFloat3(&m.up, XMVector3TransformNormal(XMLoadFloat3(&up), reflect));
  return m;
}
```

水面より下にある物を描かないよう水面で斜めにクリップします。範囲は水面より上にある物だけに絞ります。解像度は画面の半分程度に下げます（反射はぼやけてよい）。描くものは遠景（空、山）と重要な近景だけに絞ります。全シーンを描くと描画が 2 倍に近くなります。

平面反射は水面が平ら（波が小さい）ときに最も正確です。波が大きい海では歪みが大きくて、ごまかしになります。小さな池、プール、湖に向きます。

## 空の反射 {#sky}

空は環境マップ（キューブマップ）で映すのが基本です。昼と夜、天候の変化に合わせて環境マップを更新します。事前のキューブマップ（昼、夜、夕方）を時間帯で混ぜるか大気からリアルタイムに生成するか（[Atmosphere Model](../../atmosphere/scattering/atmosphere-model.md)）、大気の LUT を直接引く方法があります。粗さがあるとき（細かい波のばらつき）は、キューブマップのミップを読みます（[Prefiltering (Split-Sum)](../../reflections/probes/prefilter.md)）。

## 合成 {#blend}

反射の強さはフレネルで決まります（[Water Fresnel](fresnel.md)）。真上から見ると `F ≈ 0.02` で反射はほぼ見えません。遠くを見るほど `F` が大きくなって、反射が支配的になります。遠くの水面は法線が細かく揺れてちらつきやすいので、距離に応じて法線を平らにする（粗さを上げる）処理を入れます。

!!! note "確かめた範囲"
    HLSL は `fxc`（`ps_5_0`）で、`WaterReflectionPS` をコンパイルしてエラーが出ないことを確かめました。C++ は MSVC（`/W4`、DirectXMath）でコンパイルして、鏡像カメラの数字を実行して確かめました。地平線の下を向く割合は Python の乱数シミュレーションです。GPU での描画は確認していません。

## よくあるミス {#mistakes}

??? failure "水面の反射が画面の端で途切れる"
    原因は SSR が画面の外を映せないことです。SSR の信頼度で環境マップへフェードして戻します。

??? failure "遠くの水面に黒い筋やちらつきが出る"
    原因は反射の向きが地平線の下を向いて、環境マップの下半分を読むことです。`reflect_dir.y` に下限を設けて遠くでは波の法線を弱めます。

??? failure "平面反射が、上下逆に映るまたは水面の下のものまで映る"
    原因は鏡像カメラの向き（上向きの反転、巻き順）の扱いと斜めクリップがないことです。巻き順（カリング）を反転して、水面で斜めにクリップします。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 空は環境マップ、近くは SSR か平面反射で、フォールバックで重ねます。
    - [x] 浅い角度では反射が地平線の下を向きます。`y` の下限と遠くの法線の減衰で防ぎます。
    - [x] 平面反射は鏡像カメラで描きます。巻き順を反転します。
    - [x] 強さはフレネルで決めます。

## 参考 {#references}

このページは次の資料を読まずに書きました。数字は自分で書いた C++ と Python の実測です。

- Mittring, "Finding Next Gen: CryEngine 2", SIGGRAPH 2007, Advances in Real-Time Rendering in 3D Graphics and Games（水の描画、平面反射と屈折のコピー）
- Lagarde, de Rousiers, "Moving Frostbite to Physically Based Rendering 3.0", SIGGRAPH 2014（反射とフレネルの扱い）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（フレネル、屈折、スネルの法則）
- Tessendorf, "Simulating Ocean Water", SIGGRAPH 2001 Course Notes

## 関連ページ

- [Water Shading](index.md)
- [Reflections](../../reflections/index.md)
- [Planar Reflections](../../reflections/planar.md)
