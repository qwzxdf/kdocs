---
title: Thin Translucency
tags:
  - 描画
---

# Thin Translucency

太陽や強い光を背にして、耳や指を見ると、**赤く透けて見えます**。肌が薄い所では、光が肌の**反対側の面から入り**、内部を通り抜けて、こちら側へ出てくるためです。これが**薄い部位の透過**（thin translucency）です。SSS の画面空間のぼかしやLUTは、「光が当たった面の近くの広がり」しか扱えず、この**裏から来る光**は表せません。このページでは、Jimenez らの "Real-Time Realistic Skin Translucency"（2010）に沿って、「裏から入った光の量」を、シャドウ マップから求める方法を説明します。

!!! tip "ポイント"
    - 耳・鼻・指・唇のように**薄い所**は、**反対側から入った光が、透けて見える**。
    - 透けた光の量は、**肌を通る距離（厚み）**で決まる。**厚いほど、光は弱く、赤い**。
    - **厚みは、シャドウ マップで測る**。**光から見た手前の面までの深さ**と、**今の点の深さ**の差。
    - 厚みから透過率への変換は、**拡散プロファイルを、厚みの関数にした形**（**ガウスの和**）。
    - **裏側の法線**を使って、**透過光の向き**を決める。**表面の光は別**に計算する。

## 何が起きているか

肌の内部で光は散乱しながら進み、少しずつ吸収されます。薄い部位では、反対側から入った光が、**吸収されきる前に**こちら側の表面にたどり着けます。吸収されやすさは、色で違います。赤は吸収されにくく、緑や青は吸収されやすいので、通り抜けた光は、**赤みを帯びます**。耳を光に透かすと赤橙色に見えるのは、そのためです。

必要な計算は、「点 P に、裏側から入った光が、肌の中を通って P まで届く量」です。この量は、**光が肌の中を通った距離 s**（厚み）で決まります。

* 厚みが小さい（薄い）→ 光が強く届く。
* 厚みが大きい（厚い）→ 光は弱く、赤だけが残る。

したがって、各点 P で、光の方向に沿った**肌の厚み s**を知る必要があります。

## シャドウ マップで厚みを測る

厚みを知る方法として、**シャドウ マップ**が利用できます。シャドウ マップは、光から見た、最も手前の面までの距離を保存しています。

点 P が、光に照らされていない側（影の側）にあるとします。光から見て、P の前に、光に近い側の肌の面があります。シャドウ マップに保存された距離 d₁（光から、手前の面まで）と、P の光からの距離 d₂ の差が、**光が肌の中を通った距離**、つまり厚みになります。

<div class="formula">s = d₂ − d₁　（光から見た P の距離 − シャドウ マップの距離）</div>

d₁ と d₂ は、シャドウ マップをサンプルするときの、光空間の座標から得られます。この方法は、ほぼ追加コスト無しで、シャドウ マップの 1 回の読み込みで済みます。

```hlsl
float Thickness(float3 world_pos, float3 normal) {
  float3 offset_pos = world_pos - normal * kNormalOffset;
  float4 light_pos = mul(float4(offset_pos, 1.0), light_view_projection);
  float2 uv = light_pos.xy / light_pos.w * float2(0.5, -0.5) + 0.5;
  float d1 = shadow_depth_tex.SampleLevel(point_clamp, uv, 0).r;
  float d2 = light_pos.z / light_pos.w;
  return abs(LinearizeLightDepth(d2) - LinearizeLightDepth(d1));
}
```

`kNormalOffset` は、P を法線の逆向き（肌の内側）に少しずらすための値です。P が表面ちょうどにあると、シャドウ マップの値と区別できず、自己影のノイズが出るからです。

## 厚みから透過光へ

厚み s から、透過する光の量を計算します。これは、**拡散プロファイルを、厚みの関数にしたもの**です。肌の内部を、距離 s だけ光が通り抜けたとき、どれだけ光が残るかを表します。Jimenez らは、これを、拡散プロファイル R(r) の近似に使うガウスの和で、そのまま表せることを示しました。

<div class="formula">T(s) = Σᵢ wᵢ · exp(−s² / vᵢ)</div>

w_i と v_i は、[Diffusion Profiles](diffusion-profile.md) のガウスの和と同じ重みと分散です。RGB ごとに別の重みを持つので、厚みが増えるにつれて、青、緑の順に消え、赤が残ります。ガウスの 6 項をそのまま使うと重いので、肌の透過に効く、広い分散のガウス 3〜4 項に絞るのが一般的です。

```hlsl
float3 Transmittance(float s) {
  float s2 = s * s;
  return float3(0.233, 0.455, 0.649) * exp(-s2 / 0.0064) +
         float3(0.100, 0.336, 0.344) * exp(-s2 / 0.0484) +
         float3(0.118, 0.198, 0.000) * exp(-s2 / 0.187) +
         float3(0.113, 0.007, 0.007) * exp(-s2 / 0.567) +
         float3(0.358, 0.004, 0.000) * exp(-s2 / 1.99) +
         float3(0.078, 0.000, 0.000) * exp(-s2 / 7.41);
}
```

厚みの単位は mm です。シャドウ マップから得た距離が m 単位なら、変換が必要です。

## 最終的な組み立て

透過した光を、肌の色に反映して、拡散反射に足します。

```hlsl
float3 TransmittedLight(float3 world_pos, float3 normal, float3 light_dir, float3 light_color, float3 albedo) {
  float s = Thickness(world_pos, normal) * kMetersToMillimeters;
  float3 t = Transmittance(s);
  float back_lit = saturate(dot(-normal, light_dir));
  return t * back_lit * albedo * light_color;
}
```

`back_lit` は、光が裏側から当たっているか（法線の裏が光を向くか）の係数です。表側が光を向いている場合は、通常の拡散反射に任せて、`back_lit` で透過の寄与を 0 にします。反対に、表側が影の側のときだけ、透過が効きます。

## より良いやり方

厚みを求める方法には、いくつかの改良があります。

**法線の向きに応じた補正**。光が斜めに当たると、実際に肌の中を通る距離は、垂直に通る距離より長くなります。厚み s を、光と法線のなす角（`N·L`）で補正すると、斜めの場合の過剰な透過を抑えられます。

**厚みマップ**。シャドウ マップが使えない場合や、シャドウを描かないライトに対しては、事前に計算した**厚みマップ**（キャラクターの UV に焼いたテクスチャ）を使います。耳や鼻、指で厚みが小さく、頭の中心部で大きくなるように、キャラクターを作るときにベイクします。実行時の計算は、マップを 1 回引くだけで済み、シャドウ マップに依らない分、安定します。

**画面空間のぼかしと併用**。透過光は、表面の光と同じ散乱を受けるので、透過光の結果も SSS のぼかしの対象に含めると、自然になじみます。

## よくあるミス

??? failure "耳が光の側でも赤く透けて、不自然"
    透過は、**表側が影の側（光が裏から当たる）**のときだけ。`dot(-N, L)` で重みを掛けて、**光が表から当たるときは 0** にする。

??? failure "透過がノイズだらけでちらつく"
    P が表面ちょうどにあると、シャドウ マップと比べたときに自己影が出る。**法線の逆向きに少しずらして**サンプルする。**シャドウ マップを PCF やぼかしで滑らかに**サンプルする。

??? failure "厚みの単位が合わず、透過が強すぎる・弱すぎる"
    ガウスの分散は **mm²**。距離を **mm に変換**してから入れる。

??? failure "厚い頭の中央まで、光が透けて見える"
    ガウスの広い項を入れすぎている。**s が大きいときに T が十分小さくなる**ように、項を絞る。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 薄い部位は<strong>裏から入った光が透ける</strong>。**赤みを帯びる**
    - [x] 厚みは<strong>シャドウ マップの距離の差</strong>で測る
    - [x] 透過率は<strong>ガウスの和 T(s) = Σ w exp(−s²/v)</strong>。**厚いほど赤だけが残る**
    - [x] **表が影の側のときだけ**効かせる。**厚みマップで代用**もできる

## 参考

- Jimenez, Whelan, Sundstedt, Gutierrez, "Real-Time Realistic Skin Translucency"（IEEE Computer Graphics and Applications, 2010）
- d'Eon, Luebke, "Advanced Techniques for Realistic Real-Time Skin Rendering"（GPU Gems 3, 2007）

## 関連ページ

- [Skin Overview](index.md)
- [Diffusion Profiles](diffusion-profile.md)
- [Separable SSS](screen-space-sss.md)
- [Shadow Map Basics](../../shadows/shadow-map-basics/index.md)
