---
title: Implementation Overview and Cost
tags:
  - 描画
---

# Implementation Overview and Cost

<strong>屈折を実装する手順を全体として見ます</strong>。不透明の描画 → 画面のコピー → 屈折物体の描画の順で、フレネル・厚み・色を組み合わせます。このページでは実装の流れとコスト・限界を説明します。

!!! tip "ポイント"
    - 手順：不透明パス → 画面のコピー → 屈折物体 → 半透明。
    - 画面のコピー ＝ 1 回の帯域コスト。
    - 屈折物体同士の重なりは、扱えない（片方の層のみ）。
    - 限界：画面外・重なり・手前の物。

!!! info "このページを読む前に"
    - [Refraction](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 実装の全体像
```hlsl
float4 PSGlass(VsOutput input) : SV_Target {
  float3 n = normalize(input.normal);
  float3 v = normalize(camera_position - input.world_position);
  float2 screen_uv = input.position.xy / screen_size;

  float3 refracted = refract(-v, n, 1.0 / ior);
  float2 uv = ScreenUvFromWorld(input.world_position + refracted * thickness);
  uv = ValidateUv(uv, screen_uv, input.position.z);

  float3 background = scene_color_copy.SampleLevel(linear_clamp, uv, roughness * kMaxMip).rgb;
  background *= exp(-absorption * thickness);

  float3 reflection = SampleEnvironment(reflect(-v, n), roughness);
  float fresnel = Fresnel(saturate(dot(n, v)), 0.04);
  float3 color = lerp(background, reflection, fresnel);
  return float4(color, 1.0);
}
```

<strong>出力アルファは 1</strong>（背景を、自分で混ぜているため）。ブレンドは不要（上書き）です。

## 屈折のコストと限界
| 項目 | 内容 |
| --- | --- |
| 背景のコピー | フル解像度の HDR カラー 1 枚（帯域） |
| 半透明の重なり | コピーは不透明のみ。重なるガラスは別途 |
| 画面空間の限界 | 画面外・裏側の物は、屈折で写らない |
| レイトレの屈折 | 正確（画面外・多重屈折も OK）。HW RT が必要（[Ray-Traced Reflections](../../reflections/rt-reflections/index.md)） |

## 屈折の描画パイプライン

屈折する物（ガラス、水）を描くには <strong>不透明な物を、先に描き</strong>、その結果（色と深度）を読みながら、屈折する物を描きます。

```text
① シャドウ マップなどの、準備パス
② 不透明な物を描く                     → シーンの色（レンダー ターゲット）と、深度
③ シーンの色を、コピーする             → 屈折用の、テクスチャ
④ （必要なら）シーンの色の、ミップマップを作る  → すりガラスの、ぼかし用
⑤ 屈折する物を描く（奥から手前）        → コピーを、読み、ずらして、シーンの色に、書き込む
⑥ 半透明（パーティクルなど）を、描く
⑦ ポストプロセス
```

## DirectX 11 での実装

### ① リソースを作る

```cpp
// シーンの色: レンダー ターゲットとして、描き、シェーダー リソースとしても、読む。
D3D11_TEXTURE2D_DESC desc = {};
desc.Width = width; desc.Height = height;
desc.MipLevels = 0;                                     // 全ミップ（すりガラスの、ぼかし用）
desc.ArraySize = 1;
desc.Format = DXGI_FORMAT_R16G16B16A16_FLOAT;
desc.SampleDesc.Count = 1;                               // MSAA を使うなら、別途リゾルブが必要
desc.Usage = D3D11_USAGE_DEFAULT;
desc.BindFlags = D3D11_BIND_RENDER_TARGET | D3D11_BIND_SHADER_RESOURCE;
desc.MiscFlags = D3D11_RESOURCE_MISC_GENERATE_MIPS;      // GenerateMips を使う
device->CreateTexture2D(&desc, nullptr, &scene_color);
device->CreateTexture2D(&desc, nullptr, &scene_copy);    // コピー先（屈折用）
```

### ② 毎フレームの処理

```cpp
// ② 不透明の描画
context->OMSetRenderTargets(1, scene_color_rtv.GetAddressOf(), depth_dsv.Get());
DrawOpaque();

// ③ シーンの色を、コピー（MSAA なら、ResolveSubresource を使う）
context->CopySubresourceRegion(scene_copy.Get(), 0, 0, 0, 0, scene_color.Get(), 0, nullptr);

// ④ ミップを作る（すりガラス、粗い屈折のため）
context->GenerateMips(scene_copy_srv.Get());

// ⑤ 屈折する物を描く（深度は、読み取り専用の DSV にして、深度 SRV と、共存させる）
context->OMSetRenderTargets(1, scene_color_rtv.GetAddressOf(), depth_dsv_readonly.Get());
ID3D11ShaderResourceView* srvs[2] = {scene_copy_srv.Get(), depth_srv.Get()};
context->PSSetShaderResources(0, 2, srvs);
DrawRefractive();
```

| 手順 | 理由 |
| --- | --- |
| コピーを作る | 読み書きを同じ、テクスチャで同時にできない |
| `GenerateMips` | すりガラスや粗い面の、ぼかしをミップで安く作る |
| 読み取り専用の DSV | 深度を、読み取って深度テストはする書き込みは、しない。同じ深度テクスチャを SRV としても、読める（[Color by Water Depth](../../water/shading/depth-color.md)） |

## コスト

| 処理 | コスト（1080p の目安） |
| --- | --- |
| シーンの色のコピー | 0.05〜0.1 ms（帯域） |
| `GenerateMips` | 0.1〜0.3 ms |
| 屈折する物の描画 | 画面を、占める面積に比例。テクスチャ読み込み 1〜3 回/画素 |
| 画面全体を覆うガラス（水面） | 全画素が屈折の、テクスチャ読み込みを行う。水の描画は数 ms |

<strong>コピーは 1 フレームに 1 回</strong>で、済ませます。屈折する物が複数あっても、同じコピーを読みます（物同士の屈折が、反映されない制約と引き換え）。

### 節約の工夫

| 工夫 | 内容 |
| --- | --- |
| 低解像度のコピー | コピーを、画面の半分の解像度に。ぼかす屈折（すりガラス）には、十分 |
| 屈折する物が無いときはコピーを、省く | 画面にガラスが映っていないフレームでは、コピーも `GenerateMips` も不要 |
| 範囲を限る | ガラスの周りの、矩形だけコピーする（`CopySubresourceRegion` の範囲指定） |
| 遠くのガラスは屈折なし | 遠くではずれが、小さい。反射と色だけで描く |

## シェーダーの構成

屈折する物のシェーダーは <strong>複数の、要素の合成</strong>です。

```hlsl
float4 main(PSInput input) : SV_Target {
  float3 N = normalize(input.world_normal);
  float3 V = normalize(g_camera_position - input.world_position);

  // ① 屈折（画面のコピーを、ずらして、読む）
  float3 refracted = SampleRefraction(input, N, V);             // Screen-Space Refraction
  // ② 色（厚みによる、吸収）
  float thickness = ComputeThickness(input);
  refracted *= exp(-g_absorption * thickness);                  // Thickness and Color
  // ③ 反射（環境マップ、SSR）
  float3 reflected = SampleReflection(reflect(-V, N), g_roughness);
  // ④ フレネル
  float F = FresnelSchlick(saturate(dot(N, V)), g_f0);
  // ⑤ 合成
  float3 color = lerp(refracted, reflected, F);
  // ⑥ スペキュラー（光源のハイライト）
  color += SpecularHighlight(N, V, g_light_dir, g_light_color, g_roughness);
  return float4(color, 1.0);
}
```

最終的に ブレンドせずに 不透明として、書き込みます（背景の色はすでに屈折の、読み込みの中に含まれている）。アルファ ブレンドは不要です。

## 深度の扱い

屈折する物は <strong>深度を書き込む</strong>か、どうかを決めます。

| 設定 | 内容 |
| --- | --- |
| 書き込む | 屈折する物の後ろに、描く半透明（パーティクル）が、隠される。ガラスの向こうの煙は見えない。正しい場合が多い |
| 書き込まない | 屈折する物の向こうに、あとから描く物がガラスを貫いて見える。ガラスの向こうのパーティクルが、ガラスの上に重なって見える（間違い） |

通常は深度を書き込みます（不透明の物として、扱うので）。ガラスの向こうの半透明は、ガラスの前に先に描いてコピーに、含めておきます。

## 描画の順番

| 順 | 描くもの |
| --- | --- |
| 1 | 不透明 |
| 2 | ガラスの向こうに見える、半透明（パーティクル、植物の葉） |
| 3 | コピー |
| 4 | 屈折するもの（ガラス、水） |
| 5 | ガラスの手前に見える、半透明 |

<strong>屈折する物の後ろにある半透明</strong>を、コピーの前に、描くのがポイントです。

## よくあるミス

??? failure "屈折物体の重なりが、正しく表示されない"
    <strong>重なりは 1 層だけ屈折</strong>とし、OIT などで補う。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 不透明 → コピー → 屈折の順
    - [x] 重なりと画面外が限界

## 参考

- Sousa, "Generic Refraction Simulation", GPU Gems 2, Chapter 19, 2005
- Mittring, "Finding Next Gen: CryEngine 2", SIGGRAPH 2007, Advances in Real-Time Rendering in 3D Graphics and Games
- Microsoft Learn, "ID3D11DeviceContext::CopyResource"
- Microsoft Learn, "ID3D11DeviceContext::GenerateMips"

## 関連ページ

- [Refraction](index.md)
- [Screen-Space Refraction](screen-space.md)
- [OIT](../oit/index.md)
