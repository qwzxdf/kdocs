---
title: Applying a Height Map to the Surface
tags:
  - 描画
---

# Applying a Height Map to the Surface

<strong>シミュレーションした高さマップを、水面のメッシュの高さと法線に足す</strong>と、波紋が見えます。シミュレーションする範囲はカメラの周りに限るのが普通です。このページでは反映の方法とシミュレーション領域を説明します。

!!! tip "ポイント"
    - 高さマップを読んで、頂点の高さに足す。
    - 傾きから法線にも足す。
    - シミュレーション領域は、カメラの周りの四角。
    - 領域が動く時はマップをずらす。

## 高さマップを水面に反映する
<strong>シミュレーションの高さを水面に反映</strong>します。

反映先は 2 つです。頂点の高さは頂点シェーダーで高さマップを読み、波の高さに足します。法線は高さマップの勾配から法線を作り、波の法線に足します（細かい凹凸が見えます）。

```hlsl
float2 texel = 1.0 / sim_size;
float hl = ripple_map.Sample(linear_clamp, uv - float2(texel.x, 0)).r;
float hr = ripple_map.Sample(linear_clamp, uv + float2(texel.x, 0)).r;
float hd = ripple_map.Sample(linear_clamp, uv - float2(0, texel.y)).r;
float hu = ripple_map.Sample(linear_clamp, uv + float2(0, texel.y)).r;

float3 ripple_normal = normalize(float3((hl - hr) * normal_strength, 2.0 * texel_world, (hd - hu) * normal_strength));
```

コードの要点です。中心差分で左右・上下の差が勾配になります。`normal_strength` が大きいほど凹凸がはっきりします。合成は波の法線の XZ に波紋の XZ を足して正規化します。

## シミュレーション領域
<strong>水面全体を高解像度でシミュレーションするのは、重すぎます</strong>。カメラ周りの狭い領域だけを対象にします。

| 工夫 | 内容 |
| --- | --- |
| カメラ追従 | 領域の中心をカメラの近くに置く |
| ずれの処理 | 領域が動くとき、テクセル単位で動かして高さを読み替える（波がずれないようにワールド座標をテクセルに揃える） |
| 解像度 | 512×512 を、20〜30 m 四方など。1 テクセル 5 cm 程度 |
| 端でフェード | 領域の端で高さを 0 に近づける（切れ目が見えない） |

## 波紋をシミュレーションする（波動方程式）

水面に物が触れたとき <strong>波紋が、広がる</strong>様子は 波動方程式を、高さ場（格子の各点が高さを持つ）で解くと、再現できます（Tessendorf、2004、Müller、2008）。

```text
∂²h/∂t² = c² × ∇²h            h: 水面の高さ、c: 波の速さ、∇²h: 周りとの、高さの差（ラプラシアン）
```

「周りより高い所は下がる方向へ加速し、周りより低い所は上がる方向へ、加速する」という意味です。バネがつながったような動きで 波が、伝わります。

## 離散化

格子の各点 `h[x, z]` を時間ステップ `dt` ごとに、更新します。<strong>今のフレーム</strong>の高さ `h` と、1 つ前のフレームの高さ `h_prev` を持ちます。

```text
laplacian = h[x+1,z] + h[x−1,z] + h[x,z+1] + h[x,z−1] − 4 h[x,z]
h_new = 2 h − h_prev + (c dt / dx)² × laplacian
h_new *= damping            （1 より少し小さい値。波が、だんだん消える）
```

| 値 | 意味 |
| --- | --- |
| `2 h − h_prev` | 速度（前回からの変化）を、そのまま続ける（慣性） |
| `(c dt / dx)² × laplacian` | 周りに引っ張られる力 |
| `damping` | 0.99〜0.999。小さいほど波が早く消える |

!!! warning "時間ステップには、上限がある（CFL 条件）"
    `c dt / dx` が大きすぎると 計算が、発散します（波が爆発的に大きくなる）。2 次元の格子では `c dt / dx ≤ 1/√2 ≈ 0.707` を守ります。`dx` が小さいほど `dt` も小さくする必要があります。固定の時間ステップで計算するのが、安全です。

## 計算シェーダー

3 つの高さマップ（今、前、次）を <strong>ローテーション</strong>して使います。

```hlsl
Texture2D<float> g_h : register(t0);              // 現在の高さ
Texture2D<float> g_h_prev : register(t1);         // 1 つ前
RWTexture2D<float> g_h_next : register(u0);       // 次（出力）

cbuffer WaveSimCB : register(b0) {
  float g_wave_coeff;      // (c dt / dx)²（0.5 以下）
  float g_damping;         // 0.995 など
  int g_size;
  float pad;
};

[numthreads(8, 8, 1)]
void Step(uint3 id : SV_DispatchThreadID) {
  int2 p = int2(id.xy);
  float h = g_h[p];
  float lap = g_h[min(p + int2(1, 0), g_size - 1)] + g_h[max(p - int2(1, 0), 0)]
            + g_h[min(p + int2(0, 1), g_size - 1)] + g_h[max(p - int2(0, 1), 0)]
            - 4.0 * h;
  float next = 2.0 * h - g_h_prev[p] + g_wave_coeff * lap;
  g_h_next[p] = next * g_damping;
}
```

```cpp
// 3 枚を、ローテーションして、毎フレーム（または、固定ステップごとに）実行する。
std::swap(h_prev, h);          // h_prev ← 今の h
std::swap(h, h_next);          // h ← 計算した次の h
// （h_next は、次のステップで、上書きされる）
context->CSSetShader(step_cs.Get(), nullptr, 0);
ID3D11ShaderResourceView* srvs[2] = {h_srv.Get(), h_prev_srv.Get()};
context->CSSetShaderResources(0, 2, srvs);
context->CSSetUnorderedAccessViews(0, 1, h_next_uav.GetAddressOf(), nullptr);
context->Dispatch(size / 8, size / 8, 1);
```

読み書きに 同じテクスチャを、同時に使えないので 3 枚を、役割を替えながら使います（今を読み、前を読み次に書く）。

## 波を起こす（外力）

物が水面に触れたとき <strong>その位置の高さを、押し下げる（または持ち上げる）</strong>ことで波紋を、起こします（[Writing Object Contacts](contact.md)）。

```hlsl
// 物が、水面を押した位置に、高さを足す（ブラシ）。
float d = distance(float2(id.xy), impact_pos);
float push = impact_strength * saturate(1.0 - d / impact_radius);
g_h_next[id.xy] += push;
```

## 水面メッシュに適用する

シミュレーションの結果（高さマップ）を、<strong>水面の頂点の高さに足し込み</strong>ます。

```hlsl
// 頂点シェーダー: 通常の波（FFT、Gerstner）に、波紋の高さを、足す。
float2 interaction_uv = (world_xz - g_interaction_origin) / g_interaction_size;
float ripple = g_ripple_height.SampleLevel(g_linear_clamp, interaction_uv, 0);
// 範囲の端では、波紋の影響を、0 にする（窓の外へ、波紋が、はみ出さないよう）
float edge_fade = 1.0 - saturate(max(abs(interaction_uv.x - 0.5), abs(interaction_uv.y - 0.5)) * 2.0 - 0.9) * 10.0;
world_pos.y += ripple * edge_fade;
```

法線も波紋の高さから 差分で、求めて水面の法線に足します（[Computing Normals](../waves/normals.md)、傾きを足し合わせる）。

## 窓をカメラに合わせる

高さマップは <strong>プレイヤーの周りの、数十メートル</strong>だけを覆います（256×256 を、50 m に割り当てて 1 画素 約 20 cm）。カメラが動くと窓も動き 中身を、ずらす必要があります。円環バッファ（`WRAP`）を使うとコピーなしで、窓を動かせます（[Trampled Grass](../../terrain/vegetation/trample.md) と、同じ考え方）。窓が動いたとき新しく範囲に入った帯は、0 にクリアします。

## 性能と品質

| 項目 | 内容 |
| --- | --- |
| 解像度 | 256×256〜512×512。1 画素 10〜20 cm が、波紋の細かさの限界 |
| 計算量 | 1 ステップ、数万〜数十万画素。GPU では 0.05 ms 程度 |
| 波の速さ | `c` を小さくすると波紋が、ゆっくり広がる。見た目で調整 |
| 減衰 | 小さい波紋はすぐ消えるように、`damping` を小さめにする |
| 反射 | 窓の端で波が跳ね返る。端で減衰を強くして吸収する（スポンジ層） |

## よくあるミス

??? failure "領域の端で、波紋が途切れる"
    <strong>端でフェード</strong>する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 高さと法線に、足し込む
    - [x] 領域はカメラに追従

## 参考

- Müller, "Fast Water Simulation for Games Using Height Fields", Game Developers Conference 2008（高さ場の波動方程式による水面）
- Tessendorf, "Interactive Water Surfaces", Game Programming Gems 4, 2004（高さ場の波紋の、シミュレーション）
- Courant, Friedrichs, Lewy, "Über die partiellen Differenzengleichungen der mathematischen Physik", Mathematische Annalen, Vol. 100, 1928（CFL 条件の原典）

## 関連ページ

- [Water Interaction](index.md)
- [Writing Object Contacts](contact.md)
