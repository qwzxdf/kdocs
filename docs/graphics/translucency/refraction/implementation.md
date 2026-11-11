---
title: Implementation Overview and Cost
tags:
  - 描画
---

# Implementation Overview and Cost

ガラスや水の向こうの景色はゆがんで見えます。この「ゆがみ」を作るにはガラスのピクセルを描くときにガラスの後ろの景色の色を読み出す必要があります。ところが GPU は描いている最中のレンダー ターゲットを同時に読めません。そこで、不透明な物を先に描いてその結果をコピーしておいて、屈折する物がそのコピーを読むという手順を踏みます。

<strong>屈折の実装は不透明パス → 画面のコピー → 屈折する物の描画、という並びが骨格</strong>です。このページではその流れ DirectX 11 での実装、シェーダーの構成、描く順番、コストと節約の方法、限界を説明します。

!!! tip "ポイント"
    - 手順は不透明パス → 画面のコピー → 屈折物体 → 半透明の順です。
    - 画面のコピーは 1 フレームに 1 回の帯域コストです。屈折する物が複数あっても同じコピーを読みます。
    - 屈折する物同士の重なりは、片方の層しか写りません。
    - 画面外、ガラスより手前の物、重なりが画面空間の屈折の限界です。
    - 出力のアルファは 1 です。背景は自分で混ぜているのでブレンドは不要です。

!!! info "このページを読む前に"
    - [Refraction](index.md)（このセクション全体の地図と読む順番）

## 描画パイプライン {#pipeline}

<svg class="fig flow" viewBox="0 0 720 230" role="img" aria-label="不透明、屈折の向こうの半透明、コピー、屈折物体、手前の半透明の順に描く"><defs><marker id="rfA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">屈折する物を描くパスの順番</text>
<g stroke="#4c8bf5" stroke-width="2" fill="rgba(76,139,245,0.22)"><rect x="12" y="50" width="120" height="56" rx="9"/><rect x="152" y="50" width="120" height="56" rx="9"/><rect x="292" y="50" width="120" height="56" rx="9" fill="rgba(229,170,40,0.3)" stroke="#e5aa28"/><rect x="432" y="50" width="120" height="56" rx="9"/><rect x="572" y="50" width="120" height="56" rx="9"/></g>
<g style="font-size:12px;font-weight:600" text-anchor="middle"><text x="72" y="74">① 不透明</text><text x="212" y="74">② ガラスの向こうの</text><text x="352" y="74">③ コピー</text><text x="492" y="74">④ 屈折する物</text><text x="632" y="74">⑤ 手前の半透明</text></g>
<g style="font-size:11px" text-anchor="middle"><text x="72" y="92">色と深度</text><text x="212" y="92">半透明（葉・煙）</text><text x="352" y="92">ミップも作る</text><text x="492" y="92">コピーを読む</text><text x="632" y="92">ガラスの前の煙など</text></g>
<g stroke="currentColor" stroke-width="2" marker-end="url(#rfA)"><line x1="132" y1="78" x2="152" y2="78"/><line x1="272" y1="78" x2="292" y2="78"/><line x1="412" y1="78" x2="432" y2="78"/><line x1="552" y1="78" x2="572" y2="78"/></g>
<rect x="292" y="124" width="260" height="38" rx="8" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="422" y="147" text-anchor="middle" style="font-size:12px">③ と ④ の間に、屈折する物の後ろにある物を全部入れておく</text>
<text x="360" y="200" text-anchor="middle" style="font-size:12px">コピーに入っていない物は、屈折した景色には写らない。順番がそのまま見え方を決める</text></svg>

流れを番号で並べると次のとおりです。

1. シャドウ マップなどの準備パスを実行します。
2. 不透明な物を描きます。結果はシーンの色（レンダー ターゲット）と深度です。
3. ガラスの向こうに見える半透明（葉、煙など）を描きます。
4. シーンの色をコピーします。屈折用のテクスチャです。
5. 必要ならコピーのミップマップを作ります。すりガラスのぼかしに使います。
6. 屈折する物を奥から手前へ描きます。コピーを読んでずらしてシーンの色に書き込みます。
7. ガラスの手前に見える半透明（パーティクルなど）を描きます。
8. ポストプロセスを実行します。

3 と 4 の順番が要点です。屈折する物の後ろにある半透明をコピーの前に描いておくと屈折した景色に写ります。

## DirectX 11 での実装 {#d3d11}

### リソースを作る

シーンの色はレンダー ターゲットとして描いて、シェーダー リソースとしても読みます。コピー先は屈折物体が読むテクスチャです。

```cpp
// （コンパイルしていない）
D3D11_TEXTURE2D_DESC desc = {};
desc.Width = width;
desc.Height = height;
desc.MipLevels = 0;                                     // 全ミップ（すりガラスのぼかし用）
desc.ArraySize = 1;
desc.Format = DXGI_FORMAT_R16G16B16A16_FLOAT;           // HDR のまま持つ
desc.SampleDesc.Count = 1;                               // MSAA を使うなら別にリゾルブが必要
desc.Usage = D3D11_USAGE_DEFAULT;
desc.BindFlags = D3D11_BIND_RENDER_TARGET | D3D11_BIND_SHADER_RESOURCE;
desc.MiscFlags = D3D11_RESOURCE_MISC_GENERATE_MIPS;      // GenerateMips を使う
device->CreateTexture2D(&desc, nullptr, &scene_color);
device->CreateTexture2D(&desc, nullptr, &scene_copy);    // コピー先（屈折用）
```

### 毎フレームの処理

```cpp
// （コンパイルしていない）
// 不透明を描く
context->OMSetRenderTargets(1, scene_color_rtv.GetAddressOf(), depth_dsv.Get());
DrawOpaque();
DrawTranslucentBehindGlass();                           // ガラスの向こうの半透明

// シーンの色をコピー（MSAA なら ResolveSubresource を使う）
context->CopySubresourceRegion(scene_copy.Get(), 0, 0, 0, 0, scene_color.Get(), 0, nullptr);

// ミップを作る（すりガラス、粗い屈折のため）
context->GenerateMips(scene_copy_srv.Get());

// 屈折する物を描く。深度は読み取り専用の DSV にして、深度 SRV と共存させる
context->OMSetRenderTargets(1, scene_color_rtv.GetAddressOf(), depth_dsv_readonly.Get());
ID3D11ShaderResourceView* srvs[2] = {scene_copy_srv.Get(), depth_srv.Get()};
context->PSSetShaderResources(0, 2, srvs);
DrawRefractive();
```

コピーを作るのは読み書きを同じテクスチャで同時にできないからです。`GenerateMips` はすりガラスのぼかしをミップで安く作るために使います。読み取り専用の DSV は深度を読んで深度テストはするけれど書き込みはしない設定で、同じ深度テクスチャを SRV としても読めます（[Color by Water Depth](../../water/shading/depth-color.md) 参照）。

## シェーダーの構成 {#shader}

屈折する物のシェーダーはいくつかの要素の合成です。屈折、色（吸収）、反射、フレネル、スペキュラーを順に求めて最後に混ぜます。まず、定数とテクスチャです。

<svg class="fig flow" viewBox="0 0 720 250" role="img" aria-label="視線がガラスで曲がり、厚みの分だけ進んだ点を画面の UV に直して背景を読む"><defs><marker id="rfB" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">屈折の読み出し: 曲げて、進めて、画面に戻す</text>
<rect x="250" y="70" width="160" height="110" fill="rgba(76,139,245,0.15)" stroke="#4c8bf5" stroke-width="2"/><text x="330" y="200" text-anchor="middle" style="font-size:12px">ガラス（厚み）</text>
<line x1="60" y1="40" x2="250" y2="100" stroke="currentColor" stroke-width="2.5" marker-end="url(#rfB)"/><text x="60" y="34" style="font-size:12px">視線</text>
<line x1="250" y1="100" x2="410" y2="136" stroke="#e5aa28" stroke-width="3" marker-end="url(#rfB)"/><text x="330" y="106" text-anchor="middle" style="font-size:12px;fill:#b7791f">refract</text>
<line x1="250" y1="100" x2="410" y2="150" stroke="#94a3b8" stroke-dasharray="4 4"/><text x="425" y="160" style="font-size:12px;fill:#64748b">曲げなかった場合</text>
<circle cx="410" cy="136" r="6" fill="#e5484d"/><text x="425" y="130" style="font-size:12px;font-weight:600">world + 屈折方向 × 厚み</text>
<line x1="410" y1="136" x2="410" y2="222" stroke="#e5484d" stroke-dasharray="4 3"/><line x1="40" y1="222" x2="700" y2="222" stroke="currentColor" stroke-width="1.5"/><text x="410" y="240" text-anchor="middle" style="font-size:12px">この点の画面 UV で、コピーを読む</text></svg>


```hlsl
Texture2D<float4> g_scene_copy : register(t0);        // 不透明パスのコピー（ミップつき）
Texture2D<float> g_depth : register(t1);              // 不透明の深度
TextureCube<float4> g_environment : register(t2);     // 環境マップ（粗さでミップを引く）
SamplerState g_linear_clamp : register(s0);

cbuffer GlassConstants : register(b0) {
  float4x4 g_view_proj;
  float3 g_camera_position;
  float g_ior;                 // 屈折率。ガラス 1.5、水 1.33
  float3 g_absorption;         // 色ごとの吸収の強さ（1/メートル）。例: (0.3, 0.1, 0.05)
  float g_thickness;           // 厚み（メートル）。ここでは定数
  float2 g_screen_size;
  float g_roughness;           // 0 = 透明、大きいほどすりガラス
  float g_max_mip;             // コピーの最大ミップ番号
  float3 g_light_dir;          // 光の来る向き（正規化済み）
  float g_f0;                  // 垂直入射の反射率。ガラスで 0.04
  float3 g_light_color;
  float _pad;
};

struct PsInput {
  float4 position : SV_Position;
  float3 world_position : TEXCOORD0;
  float3 world_normal : TEXCOORD1;
};
```

次に、ワールド座標を画面の UV に直す関数と読み出し位置の妥当性の確認です。

```hlsl
float2 ScreenUvFromWorld(float3 world_pos) {
  float4 clip = mul(float4(world_pos, 1.0), g_view_proj);
  float2 ndc = clip.xy / clip.w;
  return float2(ndc.x * 0.5 + 0.5, 0.5 - ndc.y * 0.5);     // D3D は v が下向き
}

// 屈折でずらした先が使えないときは、ずらさない UV に戻す
float2 ValidateUv(float2 uv, float2 original_uv, float glass_depth) {
  // 画面の外は、コピーに景色がない
  if (any(uv < 0.0) || any(uv > 1.0)) return original_uv;
  // ずらした先に、ガラスより手前の物がある（人物がガラスの前に立っているなど）。
  // その物の色を、ガラスの向こうの景色として読むと、手前の物がガラスに写り込む
  float scene_depth = g_depth.SampleLevel(g_linear_clamp, uv, 0);
  if (scene_depth < glass_depth) return original_uv;
  return uv;
}
```

`ValidateUv` の 2 つ目の判定は屈折の限界を隠す工夫です。ガラスの手前にある物の色がガラスのゆがみに引きずられて見えるのをずらさずに読むことで防ぎます。深度は標準（小さいほど近い）を前提に比べています。

最後に、本体のピクセル シェーダーです。

```hlsl
float4 PSGlass(PsInput input) : SV_Target {
  float3 n = normalize(input.world_normal);
  float3 v = normalize(g_camera_position - input.world_position);
  float2 screen_uv = input.position.xy / g_screen_size;

  // ① 屈折: 視線を曲げて、厚みの分だけ進んだ点を、画面の UV に直す
  float3 refracted_dir = refract(-v, n, 1.0 / g_ior);
  float2 uv = ScreenUvFromWorld(input.world_position + refracted_dir * g_thickness);
  uv = ValidateUv(uv, screen_uv, input.position.z);

  // 粗さが大きいほど、高いミップ（ぼけた絵）を読む。すりガラスの表現
  float3 background = g_scene_copy.SampleLevel(g_linear_clamp, uv, g_roughness * g_max_mip).rgb;

  // ② 色: 厚みで吸収する（ベールの法則）。厚いほど、吸収の強い色が減る
  background *= exp(-g_absorption * g_thickness);

  // ③ 反射: 環境マップ。粗いほど、ぼけたミップを読む
  float3 reflection = g_environment.SampleLevel(g_linear_clamp, reflect(-v, n), g_roughness * 6.0).rgb;

  // ④ フレネル: 浅い角度ほど、反射が強くなる（Schlick の近似）
  float cos_theta = saturate(dot(n, v));
  float fresnel = g_f0 + (1.0 - g_f0) * pow(1.0 - cos_theta, 5.0);

  // ⑤ 合成: 屈折（背景）と反射を、フレネルで混ぜる
  float3 color = lerp(background, reflection, fresnel);

  // ⑥ スペキュラー: 光源のハイライト（Blinn-Phong の簡易版。粗さで広がる）
  float3 h = normalize(g_light_dir + v);
  float power = lerp(256.0, 8.0, g_roughness);
  color += g_light_color * pow(saturate(dot(n, h)), power) * fresnel;

  return float4(color, 1.0);   // 背景は自分で混ぜたので、アルファは 1（ブレンドなし）
}
```

出力のアルファは 1 でブレンドはオフにして上書きします。背景の色はもう `background` に含まれているからです。ここで通常のアルファ ブレンドをかけると、背景が二重に足されて明るくなります。

`refract` の第 3 引数は屈折率の比 `n1 / n2` です。空気（1.0）からガラス（1.5）へ入るので `1 / 1.5` です。`refract` は全反射のとき 0 ベクトルを返します。ガラスの外から見る場合は起きません。

数字で確かめます。`g_absorption = (0.3, 0.1, 0.05)`、`g_thickness = 0.1` m なら `exp(−0.3 × 0.1) = 0.97`、`exp(−0.1 × 0.1) = 0.99`、`exp(−0.05 × 0.1) = 0.995` で赤が約 3 % 弱くなって、ほぼ透明です。厚みが 1 m なら赤が `exp(−0.3) = 0.74`、青が `exp(−0.05) = 0.95` で青緑がかった色になります。

!!! note "確かめた範囲"
    HLSL は `fxc`（`ps_5_0`）でコンパイルして、エラーが出ないことを確かめました。C++ はコンパイルしていません。GPU での描画は確認していません。

## 深度と描く順番 {#depth}

屈折する物が深度を書き込むかどうかで、見え方が変わります。

書き込むとガラスの向こうにあとから描く半透明（パーティクル）が、ガラスに隠されます。ガラスの向こうの煙は見えなくなります。正しい場合が多い選択です。

書き込まないとあとから描いた物がガラスを貫いて見えます。ガラスの向こうのパーティクルが、ガラスの上に重なるおかしな見え方になります。

通常は、不透明な物として扱うので深度を書き込みます。ガラスの向こうの半透明はガラスより前に（コピーの前に）描いて、コピーに含めます。ガラスの手前の半透明は屈折する物のあとで描きます。「屈折する物の後ろにある半透明はコピーの前に描く」のがポイントです。

## コスト {#cost}

屈折のコストはコピー、ミップ、屈折する物の描画に分かれます。1920 × 1080 の `R16G16B16A16_FLOAT`（1 画素 8 バイト）で見積もります。

コピーは 1 枚が `1920 × 1080 × 8 B ≒ 15.8 MiB` です。読んで書くので帯域は約 32 MiB 動きます。300 GB/s の GPU なら約 0.1 ms です。4K（3840 × 2160）なら 4 倍の約 0.4 ms です。

`GenerateMips` はミップがもとの約 1/3 を足すので、帯域は 1.3 倍ほどですが、ダウンサンプルのパスが何回も走るので、0.1〜0.3 ms が目安です（見積もりです。実測は GPU によって違います）。

屈折する物の描画は画面を占める面積に比例します。1 画素あたりテクスチャ読み出しが 1〜3 回（コピー、深度、環境マップ）あります。水面のように画面全体を覆うガラスは全画素でその読み出しを行うので、数 ms かかることがあります。

コピーは 1 フレームに 1 回で済ませます。屈折する物が複数あっても同じコピーを読みます。物同士の屈折が反映されない制約と引き換えです。

### 節約の工夫

- 低解像度のコピーにします。画面の半分の解像度にすると帯域が 1/4 になります。ぼかす屈折（すりガラス）にはそれで十分です。
- 屈折する物が画面にないフレームでは、コピーも `GenerateMips` も省きます。
- 範囲を限ります。ガラスの周りの矩形だけをコピーします（`CopySubresourceRegion` の範囲指定）。
- 遠くのガラスは屈折をやめます。遠くではずれが小さいので反射と色だけで描きます。

## 限界 {#limits}

画面空間の屈折はコピーに写っている景色しか使えません。そのため、次の限界があります。

- 画面の外の物は屈折で写りません。端に近いほど `ValidateUv` で元の UV に戻されて、ゆがみが消えます。
- ガラスの後ろの裏側（隠れた面）は、写りません。
- 屈折する物同士の重なりは片方の層しか屈折しません。コピーは不透明な物だけだからです。重なるガラスは別の処理（OIT など）で補います。

レイトレーシングの屈折は画面外も多重の屈折も正確に扱えます。ただし、ハードウェア RT が必要です（[Ray-Traced Reflections](../../reflections/rt-reflections/index.md)）。

## よくあるミス {#mistakes}

??? failure "屈折物体の重なりが正しく表示されない"
    原因はコピーに屈折する物を含めていないことです。コピーは不透明な物だけなので、重なる側のガラスは手前の 1 層だけが屈折します。許容するか OIT で重なりを別に処理します。

??? failure "ガラスの前に立つ人物が、ガラスに引きずられて歪む"
    原因は屈折でずらした先にガラスより手前の物があって、その色を読んでしまうことです。ずらした先の深度を読んでガラスより手前ならずらさない UV に戻します（`ValidateUv`）。

??? failure "ガラスが背景より明るく、白っぽく光る"
    原因は背景を自分で混ぜているのに、通常のアルファ ブレンドもかけていることです。背景が二重に足されます。ブレンドをオフにしてアルファを 1 で上書きします。

??? failure "不透明なオブジェクトが、ガラスの前でも屈折の中に写る"
    原因は深度 SRV と DSV を同時にバインドして、描画がエラーになるか深度が読めていないことです。深度の読み取り専用 DSV（`D3D11_DSV_READ_ONLY_DEPTH`）を作って、SRV と共存させます。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 不透明 → コピー → 屈折の順に描きます。コピーに入れた物だけが屈折した景色に写ります。
    - [x] コピーは 1 フレームに 1 回です。帯域は 1080p の HDR で約 32 MiB です。
    - [x] 屈折する物のアルファは 1 で、ブレンドせずに上書きします。
    - [x] 画面外とガラスの手前の物は、ずらさずに元の UV へ戻します。
    - [x] 重なる屈折は 1 層しか写りません。

## 参考 {#references}

このページは次の資料を読まずに書きました。コストは画素数とバイト数からの見積もりで、実測ではありません。

- Sousa, "Generic Refraction Simulation", GPU Gems 2, Chapter 19, 2005
- Mittring, "Finding Next Gen: CryEngine 2", SIGGRAPH 2007, Advances in Real-Time Rendering in 3D Graphics and Games
- Microsoft Learn, "ID3D11DeviceContext::CopyResource"
- Microsoft Learn, "ID3D11DeviceContext::GenerateMips"

## 関連ページ

- [Refraction](index.md)
- [Screen-Space Refraction](screen-space.md)
- [OIT](../oit/index.md)
