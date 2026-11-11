---
title: Usage and Misconceptions of AO
tags:
  - 描画
---

# Usage and Misconceptions of AO

<strong>AO は間接光の「拡散」を暗くするもの</strong>で、直接光には掛けません。これを間違えると画面が不自然に暗くなります。このページでは AO の正しい適用先・スペキュラ遮蔽・よくある誤解を説明します。

!!! tip "ポイント"
    - AO は環境光（間接拡散）に掛ける。直接光には掛けない。
    - スペキュラの環境光にはスペキュラ遮蔽（別の式）。
    - AO を全体に掛けて、画面を暗くするのは誤用。
    - よくある誤解：AO ＝ 影・AO ＝ 常に暗くなるもの。

!!! info "このページを読む前に"
    - [AO Theory](index.md)（このセクション全体の地図と読む順番）

## AO の使い方

### 掛ける相手：間接光の拡散項だけ

AO は「環境光（空や周囲から来る間接光）が周囲の物にどれだけ遮られるか」を表します。ライト 1 つ 1 つの向きや位置は考えていない量です。そのため、太陽やスポットライトのような<strong>直接光に掛けてはいけません</strong>。直接光の遮蔽はシャドウ マップなどでライトごとに求めるべきものです。直接光に AO を掛けてしまうとライトが当たっている日向の隅まで暗くなり、絵が不自然に汚れます。

```text
float3 ambient = irradiance * albedo * ao;
float3 color = direct_light + ambient;
```

### スペキュラの環境光

IBL（環境マップ）を使うと環境光は拡散項と鏡面項に分かれます。拡散項には AO をそのまま掛けます。鏡面項（映り込み）に同じ AO を掛けるのは正しくありません。鏡面反射は視線の方向と粗さで決まる狭い方向の光だけを拾うので、拡散用の AO では暗さの程度が合いません。鏡面項には視線方向と粗さを考えたスペキュラ遮蔽という別の式を使います（[GTAO](../gtao.md)）。

### 焼いた AO との併用

メッシュに焼き込んだ AO テクスチャは、マイクロ AO（細かいくぼみ・ひび）の役を担います。スクリーン空間 AO は物体どうしの接触（壁と箱の間など）という マクロ AO の役を担います。両者は役割が違うので掛け合わせて併用します。同じ領域を二重に暗くしすぎないようスクリーン空間の半径は、焼き込みで扱う細かさより大きくしておきます。

### リニア空間で掛ける

AO はリニアな光の量に対する係数です。ガンマ空間（sRGB の色のまま）で掛けると、暗部が潰れて見た目が変わります。ライティングの計算が終わるまで、リニア空間のまま処理します（[色の数学](../../../gamemath/color.md)）。

### 強さの調整

`pow(AO, 指数)` で調整します。指数を大きくすると暗い所がより濃くなって、コントラストが上がります。強くしすぎると画面全体が汚れて見えるので、見た目をアーティストが調整できるようパラメータを公開しておくとよいでしょう。

## 適用のコード

AO は <strong>間接光（環境光）にだけ</strong>掛けます。ライティングのパスで環境光の項に AO を掛けます。

```hlsl
SamplerState g_linear_clamp : register(s0);
Texture2D<float> g_ao : register(t5);                          // AO（ぼかし・アップサンプル済み）

// GTAO のマルチ バウンス近似: 明るい色の面ほど、隅で、光が回り込むので、AO を弱める（Jimenez 2016）。
float3 MultiBounceAO(float ao, float3 albedo) {
  float3 a = 2.0404 * albedo - 0.3324;
  float3 b = -4.7951 * albedo + 0.6417;
  float3 c = 2.7552 * albedo + 0.6903;
  return max(ao, ((ao * a + b) * ao + c) * ao);               // ao 自身より、暗くならない
}

// スペキュラ遮蔽: 拡散の AO を鏡面反射の、遮蔽に変換する（Lagarde と de Rousiers、2014）。
float SpecularOcclusion(float n_dot_v, float ao, float roughness) {
  return saturate(pow(n_dot_v + ao, exp2(-16.0 * roughness - 1.0)) - 1.0 + ao);
}

float3 AmbientLighting(float3 albedo, float3 f0, float roughness, float n_dot_v, float2 uv,
                       float3 diffuse_irradiance, float3 specular_ibl) {
  float ao = g_ao.SampleLevel(g_linear_clamp, uv, 0);
  float3 diffuse = diffuse_irradiance * albedo * MultiBounceAO(ao, albedo);   // 拡散の環境光に掛ける
  float3 specular = specular_ibl * SpecularOcclusion(n_dot_v, ao, roughness); // 鏡面の環境光には、変換して掛ける
  return diffuse + specular;
}
// 直接光（太陽、ライト）には、AO を掛けない。直接光の影は、シャドウ マップが受け持つ。

float4 AmbientPS(float4 pos : SV_Position, float2 uv : TEXCOORD0) : SV_Target {
  return float4(AmbientLighting(float3(0.8, 0.8, 0.8), float3(0.04, 0.04, 0.04), 0.3, 0.7, uv, float3(1, 1, 1), float3(1, 1, 1)), 1.0);
}
```

数行ずつ見ると 拡散の環境光にはアルベドで、補正した `MultiBounceAO` を 鏡面の環境光には粗さと視線の角度で変換した `SpecularOcclusion` を掛けています。同じ `ao` をそのまま全部に掛けないのがコツです。

| 掛ける相手 | 掛けるもの | 理由 |
| --- | --- | --- |
| 拡散の環境光 | `MultiBounceAO(ao, albedo)` | 明るい面は隅で、光が回り込む。素の AO は暗すぎる |
| 鏡面の環境光 | `SpecularOcclusion(...)` | 鏡面は、反射方向の狭い範囲だけが効く。粗いほど AO に近くつるつるなら効きにくい |
| 直接光 | 掛けない | 直接光の影は、シャドウ マップが担当。二重に暗くなる |
| エミッシブ | 掛けない | 自分で光る物は、遮られない |

## 数字で確かめる {#measure}

### マルチ バウンスで明るい面の隅を持ち上げる

素の AO は光が 1 回も跳ね返らないと仮定した値です。アルベドが高い面（白い壁）の隅では光が壁の間で何度も跳ね返って、隅が思ったほど暗くなりません。`MultiBounceAO` はその分を持ち上げます。式から計算した結果は次のとおりです。

- アルベド 0.1（黒に近い）では、AO 0.3 が 0.301 で、ほぼ変わりません。
- アルベド 0.5 では AO 0.3 が 0.481 になります。
- アルベド 0.9（白に近い）では、AO 0.3 が 0.661 になります。AO 0.1 でも 0.282 で、AO 0.5 は 0.855 まで上がります。

<svg class="fig flow" viewBox="0 0 720 250" role="img" aria-label="マルチ バウンス AO。アルベドが高いほど、同じ AO でも明るく持ち上がる"><text x="14" y="22" class="fig-title">AO と、マルチ バウンス後の値（アルベド 0.1、0.5、0.9）</text>
<line x1="70" y1="190" x2="370" y2="190" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="190" x2="70" y2="50" stroke="currentColor" stroke-width="1.5"/>
<text x="62" y="56" text-anchor="end" style="font-size:12px">1</text><text x="62" y="194" text-anchor="end" style="font-size:12px">0</text><text x="370" y="210" text-anchor="end" style="font-size:12px">入力の AO（0 〜 1）</text>
<path d="M70.0,190.0 L77.5,186.5 L85.0,183.0 L92.5,179.5 L100.0,176.0 L107.5,172.5 L115.0,169.0 L122.5,165.5 L130.0,162.0 L137.5,158.5 L145.0,155.0 L152.5,151.5 L160.0,148.0 L167.5,144.5 L175.0,141.0 L182.5,137.5 L190.0,134.0 L197.5,130.5 L205.0,127.0 L212.5,123.5 L220.0,120.0 L227.5,116.5 L235.0,113.0 L242.5,109.5 L250.0,106.0 L257.5,102.5 L265.0,99.0 L272.5,95.5 L280.0,92.0 L287.5,88.5 L295.0,85.0 L302.5,81.5 L310.0,78.0 L317.5,74.5 L325.0,71.0 L332.5,67.5 L340.0,64.0 L347.5,60.5 L355.0,57.0 L362.5,53.5 L370.0,50.0" fill="none" stroke="#94a3b8" stroke-dasharray="5 4" stroke-width="2"/>
<path d="M70.0,190.0 L77.5,186.5 L85.0,183.0 L92.5,179.5 L100.0,176.0 L107.5,172.5 L115.0,169.0 L122.5,165.5 L130.0,162.0 L137.5,158.5 L145.0,155.0 L152.5,151.5 L160.0,147.9 L167.5,144.3 L175.0,140.7 L182.5,137.0 L190.0,133.4 L197.5,129.8 L205.0,126.2 L212.5,122.6 L220.0,119.0 L227.5,115.4 L235.0,111.8 L242.5,108.2 L250.0,104.6 L257.5,101.0 L265.0,97.5 L272.5,93.9 L280.0,90.4 L287.5,86.9 L295.0,83.4 L302.5,79.9 L310.0,76.5 L317.5,73.1 L325.0,69.7 L332.5,66.3 L340.0,63.0 L347.5,59.7 L355.0,56.5 L362.5,53.2 L370.0,50.0" fill="none" stroke="#4c8bf5" stroke-width="3"/><path d="M70.0,190.0 L77.5,182.9 L85.0,176.1 L92.5,169.6 L100.0,163.4 L107.5,157.5 L115.0,151.8 L122.5,146.3 L130.0,141.2 L137.5,136.2 L145.0,131.5 L152.5,127.0 L160.0,122.7 L167.5,118.6 L175.0,114.7 L182.5,110.9 L190.0,107.4 L197.5,104.0 L205.0,100.7 L212.5,97.6 L220.0,94.7 L227.5,91.8 L235.0,89.1 L242.5,86.5 L250.0,84.0 L257.5,81.6 L265.0,79.2 L272.5,77.0 L280.0,74.8 L287.5,72.6 L295.0,70.5 L302.5,68.5 L310.0,66.4 L317.5,64.4 L325.0,62.4 L332.5,60.4 L340.0,58.4 L347.5,56.3 L355.0,54.3 L362.5,52.2 L370.0,50.0" fill="none" stroke="#e5aa28" stroke-width="3"/><path d="M70.0,190.0 L77.5,179.2 L85.0,169.1 L92.5,159.5 L100.0,150.6 L107.5,142.2 L115.0,134.3 L122.5,127.0 L130.0,120.1 L137.5,113.8 L145.0,107.9 L152.5,102.5 L160.0,97.5 L167.5,92.9 L175.0,88.7 L182.5,84.8 L190.0,81.3 L197.5,78.1 L205.0,75.3 L212.5,72.7 L220.0,70.4 L227.5,68.3 L235.0,66.5 L242.5,64.8 L250.0,63.4 L257.5,62.1 L265.0,61.0 L272.5,60.0 L280.0,59.2 L287.5,58.4 L295.0,57.6 L302.5,57.0 L310.0,56.3 L317.5,55.7 L325.0,55.1 L332.5,54.4 L340.0,53.7 L347.5,52.9 L355.0,52.1 L362.5,51.1 L370.0,50.0" fill="none" stroke="#e5484d" stroke-width="3"/>
<g style="font-size:12px;font-weight:600"><text x="400" y="80" style="fill:#e5484d">アルベド 0.9（白）: AO 0.3 → 0.661</text><text x="400" y="104" style="fill:#b7791f">アルベド 0.5: 0.3 → 0.481</text><text x="400" y="128" style="fill:#4c8bf5">アルベド 0.1（黒）: 0.3 → 0.301</text><text x="400" y="152" style="fill:#64748b">破線: そのまま（変換なし）</text></g>
<text x="360" y="238" text-anchor="middle" style="font-size:12px">明るい面ほど光が回り込んで、隅が暗くなりきらない。素の AO を掛けると暗すぎる</text></svg>

### スペキュラ遮蔽は粗さで効き方が変わる

`SpecularOcclusion` の指数は `exp2(−16 × roughness − 1)` で粗さ 0.1 なら約 0.165、0.5 なら約 0.002、1.0 なら約 0.00001 です。粗さが 0.5 以上では `pow` がほぼ 1 になって、結果は AO そのものになります（拡散と同じ暗さです）。粗さ 0.1（つるつる）では `NdotV` と AO で、結果が大きく変わります。AO 0.3 のとき `NdotV = 0.5` で 0.264、`NdotV = 0.9` で 0.331、`NdotV = 0.1`（ほぼ真横から）で 0.16 です。つるつるの面は視線が面に平行なほど鏡面反射が強く遮られます。粗い面は拡散と同じ AO で済みます。

<svg class="fig flow" viewBox="0 0 720 240" role="img" aria-label="粗さごとのスペキュラ遮蔽の指数。粗いほど AO そのものに近づく"><text x="14" y="22" class="fig-title">スペキュラ遮蔽の指数 exp2(−16 r − 1)</text>
<line x1="60" y1="190" x2="690" y2="190" stroke="currentColor" stroke-width="1.5"/>
<g stroke-width="2" fill="rgba(76,139,245,0.28)" stroke="#4c8bf5"><rect x="130" y="60" width="100" height="130"/><rect x="300" y="187" width="100" height="3"/><rect x="470" y="189" width="100" height="1"/></g>
<g style="font-size:12px" text-anchor="middle"><text x="180" y="54">0.165</text><text x="350" y="181">0.002</text><text x="520" y="183">0.00001</text>
<text x="180" y="210">粗さ 0.1（つるつる）</text><text x="350" y="210">粗さ 0.5</text><text x="520" y="210">粗さ 1.0</text></g>
<text x="360" y="232" text-anchor="middle" style="font-size:12px">指数が 0 に近いと pow が 1 に近づき、結果は AO そのもの。つるつるのときだけ視線の角度が効く</text></svg>

!!! note "確かめた範囲"
    マルチ バウンスとスペキュラ遮蔽の数字は、Jimenez ら（2016）と Lagarde ら（2014）の式を Python で計算した値です。式の係数は記憶から書いたもので、原典（未読）では確かめていません。HLSL は `fxc`（`ps_5_0`）でコンパイルして確かめました。GPU での描画は確認していません。

## 画面に出して確認する

AO が正しく掛かっているかは <strong>AO だけ</strong>、ライティング済みの画面、AO を掛けない画面をキーで、切り替えて見ます。

```text
// デバッグ表示: 切り替えで、AO だけを白黒で出す。
if (g_debug_mode == kDebugAoOnly) return float4(ao.xxx, 1.0);
if (g_debug_mode == kDebugNoAo) return float4(AmbientLightingWithoutAo(...) + direct, 1.0);
```

隅と接地面が 自然に暗く日向や大きな面が 暗くなっていないことそして、AO の効きが動いてもちらつかないことを確認します。

## よくある誤解
??? failure "AO はライトの影の代わりになる"
    AO は<strong>ライトを考慮しない</strong>ので、影の向きを表せません。接地感を出すだけで光源の方向による影は、シャドウ マップなどで別に作ります。

??? failure "AO をシーン全体に掛けて、明るい場所まで暗くなる"
    間接光だけに掛けます。直接光に掛けると日向まで暗くなります。

??? failure "半径を大きくして、広い範囲の陰影を出そうとする"
    半径に比例してサンプルの取りこぼしとコストが増えます。大きな陰影は間接光の方式（[GI](../../index.md)）やライトマップの役目です。

## よくあるミス

??? failure "直接光（太陽）に AO を掛けて、日向が暗い"
    <strong>AO は環境光だけ</strong>に掛ける。

## これだけ覚える

!!! abstract "まとめ"
    - [x] AO は間接拡散にだけ掛ける
    - [x] スペキュラにはスペキュラ遮蔽

## 参考

このページは次の資料を読まずに書きました。

- Landis, "Production-Ready Global Illumination", SIGGRAPH 2002 Course 16（ambient occlusion の、映画制作での使われ方）
- Jimenez, Wu, Pesce, Jarabo, "Practical Real-Time Strategies for Accurate Indirect Occlusion", SIGGRAPH 2016, Physically Based Shading in Theory and Practice
- Lagarde, de Rousiers, "Moving Frostbite to Physically Based Rendering 3.0", SIGGRAPH 2014（スペキュラ オクルージョン）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（Ambient Occlusion の章）

## 関連ページ

- [AO Theory](index.md)
- [AO Artifacts](../artifacts/index.md)
- [PBR](../../../3d/pbr.md)
