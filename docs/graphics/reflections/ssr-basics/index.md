---
title: SSR Basics
tags:
  - 描画
---

# SSR Basics

<strong>SSR（スクリーン スペース リフレクション）は、すでに描いた画面の画像（色と深度）だけを使って、反射を作る手法</strong>です。<strong>反射レイを画面の上でたどり、当たった画素の色を持ってくる</strong>という、とても単純な発想ですが、細かい所で、つまずきやすいです。このセクションでは、発想・レイの進め方・厚み・色の取得とフェード・コストと粗さ・アーティファクトを、1 つずつ別のページで説明します。

## 発想
[Reflections](../index.md)で見たとおり、鏡面反射は「<strong>反射方向 R に何が見えるか</strong>」です。SSR は、<strong>R の方向にレイを飛ばして</strong>、画面の深度バッファを「簡易なシーン」とみなして、レイが当たる所を探します。

<svg class="fig illust" viewBox="0 0 780 300" role="img" aria-label="SSR のレイ進行">
<text x="20" y="24" class="fig-title">反射方向のレイを、画面の深度バッファの上で進める。面の奥に入った所が「当たり」</text>
<polygon points="60,230 300,230 300,150 420,150 420,230 720,230 720,270 60,270" fill="rgba(150,150,150,0.3)" stroke="currentColor" stroke-width="2"/>
<text x="330" y="140" style="font-size:12px">壁（深度バッファに映る面）</text>
<circle cx="150" cy="230" r="7" fill="currentColor"/><text x="130" y="254" style="font-size:12px">p（反射する点）</text>
<line x1="150" y1="230" x2="395" y2="120" stroke="#e5484d" stroke-width="3"/>
<g fill="#e5484d"><circle cx="190" cy="212" r="4"/><circle cx="230" cy="194" r="4"/><circle cx="270" cy="176" r="4"/><circle cx="310" cy="158" r="4"/><circle cx="350" cy="140" r="4"/></g>
<circle cx="372" cy="152" r="7" fill="none" stroke="#2ea043" stroke-width="3"/><text x="380" y="190" style="font-size:12px;fill:#2ea043;font-weight:700">当たり（レイ ＞ 面の深度）</text>
<text x="20" y="288" style="font-size:12px">各ステップで、レイの奥行きと、その画素の深度を比べる。レイが面の奥へ潜ったところが交点</text>
</svg>

## 手順
| 手順 | 内容 |
| --- | --- |
| ① 反射方向を求める | 法線と視線から `R = reflect(視線, 法線)`（ビュー空間） |
| ② レイを作る | 始点 P（その画素の位置）、方向 R |
| ③ レイを進める | 画面空間で、1 ステップずつ進む |
| ④ 各ステップで当たり判定 | レイの奥行きとその画素の深度を比べる |
| ⑤ 当たった画素の色を取る | 反射として使う |
| ⑥ 端・粗さ・向きでフェード | 信頼できない反射を弱める |

### なぜレイを画面空間で進めるのか

レイを 3D 空間で進めて、各点を画面に投影して深度を比べる方法もありますが、それだと画面上で同じ画素に何度も当たり、無駄が多くなります。そこで、レイの始点と終点を先に画面に投影し、<strong>画面上の線分</strong>として、1 画素ずつ（あるいは数画素ずつ）たどります（McGuire と Mara、2014）。画面上の 1 画素ずつ進めば、見落としがなく、サンプル数も画面の大きさで上限が決まります。ただし、透視投影では、画面上で等間隔に進んでも、3D 空間では等間隔になりません。奥行きは `1/z` が画面上で線形に変化する性質を使って補間するのが、正しいやり方です（[Linear Marching](linear-march.md)）。

### なぜレイを画面空間で進めるのか

レイを 3D 空間で進めて、各点を画面に投影して深度を比べる方法もありますが、それだと画面上で同じ画素に何度も当たり、無駄が多くなります。そこで、レイの始点と終点を先に画面に投影し、<strong>画面上の線分</strong>として、1 画素ずつ（あるいは数画素ずつ）たどります（McGuire と Mara、2014）。画面上の 1 画素ずつ進めば、見落としがなく、サンプル数も画面の大きさで上限が決まります。ただし、透視投影では、画面上で等間隔に進んでも、3D 空間では等間隔になりません。奥行きは `1/z` が画面上で線形に変化する性質を使って補間するのが、正しいやり方です（[Linear Marching](linear-march.md)）。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Linear Marching](linear-march.md) | レイを進める・歩幅・当たりの精密化 |
| [Thickness](thickness.md) | 「裏側へ抜けた」を当たりにしない工夫 |
| [Color Lookup and Fading](color-fade.md) | 当たりの色・信頼度で反射を弱める |
| [Cost and Roughness](cost-roughness.md) | 解像度・簡易のぼかし |
| [Artifacts and Evaluation](artifacts.md) | SSR の問題点・長所と短所 |

## SSR とは

<strong>SSR</strong>（Screen-Space Reflections、<strong>画面空間の、反射</strong>）は、画面に、映っている、情報（深度、色）だけを、使って、反射を、近似する方法です。反射する面の、各画素から、反射方向に、レイを、飛ばし、画面の中の、何かに、当たったら、その画素の、色を、反射として、使います。

```text
反射する面の画素 P:
   視線 V と法線 N から、反射方向 R を求める
   P から R の向きに、画面空間で、レイを進める（深度バッファを、辿る）
   何かに、当たったら、当たった画素の「ライティング済みの色」を、P の反射色にする
```

## 最小の、考え方

<strong>1 つの、画素</strong>について、<strong>5 つの手順</strong>です。

| 手順 | 内容 | ページ |
| --- | --- | --- |
| ① 反射ベクトルを、求める | 視線と、法線から | このページ |
| ② レイを、進める | 画面空間で、1 歩ずつ、深度を、確かめる | [Linear Marching](linear-march.md) |
| ③ 当たりを、判定する | レイが、面の、裏に、入った（厚み以内） | [Thickness](thickness.md) |
| ④ 色を、読む・フェードする | 当たった画素の、色。画面の端、遠いほど、薄く | [Color Lookup and Fading](color-fade.md) |
| ⑤ 粗さに、応じて、ぼかす | 粗い面は、ぼかす（[Cost and Roughness](cost-roughness.md)） | [Cost and Roughness](cost-roughness.md) |

## ① 反射ベクトルと、画面空間への、投影

```hlsl
// G バッファから、ビュー空間の位置と、法線を読み、反射ベクトルを求める。
float3 position_vs = ReconstructViewPosition(uv, depth);                    // ビュー空間の位置（カメラが原点）
float3 normal_vs = DecodeNormal(g_gbuffer_normal.Load(int3(pixel, 0)));
float3 view_dir_vs = normalize(position_vs);                                // カメラから、画素へ向かう向き
float3 reflect_dir_vs = reflect(view_dir_vs, normal_vs);                    // 反射ベクトル
```

<strong>カメラから、画素への、向き</strong>（視線）を、<strong>法線で、反射</strong>させた向きが、反射ベクトルです。ビュー空間で、扱うと、カメラが、原点で、簡単です。

```hlsl
// レイの、始点と終点を、画面（uv）に、投影して、画面上の、線分にする。
float3 end_vs = position_vs + reflect_dir_vs * g_max_distance;
float4 start_clip = mul(float4(position_vs, 1.0), g_proj);
float4 end_clip = mul(float4(end_vs, 1.0), g_proj);
float2 start_uv = start_clip.xy / start_clip.w * float2(0.5, -0.5) + 0.5;
float2 end_uv = end_clip.xy / end_clip.w * float2(0.5, -0.5) + 0.5;
```

<strong>レイの始点と終点</strong>を、<strong>画面空間</strong>（uv）に、投影します。画面上の、線分を、1 画素ずつ（または、数画素ずつ）辿ると、画面の、深度と、比べられます（[Linear Marching](linear-march.md)）。

## SSR の、限界

SSR は、<strong>画面の、情報だけ</strong>を、使うので、<strong>根本的な、限界</strong>が、あります。

| 限界 | 内容 | 対策 |
| --- | --- | --- |
| 画面の外が、映らない | 画面に、映っていない物は、反射に、出ない | 反射プローブで、補う（[Combining with SSR](../probes/combine-ssr.md)） |
| 隠れた面が、映らない | 手前の物の、裏は、深度バッファに、無い。物の、裏側の、反射が、欠ける | 厚みを、仮定（[Thickness](thickness.md)）、プローブで補う |
| 画面の端で、反射が、消える | レイが、画面の外に、出る | 端で、フェード（[Color Lookup and Fading](color-fade.md)） |
| カメラに、向かう反射が、弱い | 反射方向が、カメラの方向に、近い（鏡に、真正面から、向き合う）と、カメラの、背後の、景色が、必要（画面に、無い） | 信頼度を、下げて、プローブへ |
| 細い物を、すり抜ける | ステップが、粗いと、細い物を、飛び越える | ステップを、細かく、Hi-Z（[Hi-Z SSR](../ssr-hiz.md)） |

## これだけ覚える

!!! abstract "まとめ"
    - [x] SSR は、画面の中だけの反射
    - [x] レイを深度と比べて、当たりを探す
    - [x] 外れた所は、フォールバックで補う

## 参考

- McGuire, Mara, "Efficient GPU Screen-Space Ray Tracing", Journal of Computer Graphics Techniques, Vol. 3, No. 4, 2014
- Stachowiak, Uludag, "Stochastic Screen-Space Reflections", SIGGRAPH 2015, Advances in Real-Time Rendering in Games（Frostbite の SSR）
- Uludag, "Hi-Z Screen-Space Cone-Traced Reflections", GPU Pro 5, 2014
- Valient, "Reflections and Volumetrics of Killzone Shadow Fall", SIGGRAPH 2014, Advances in Real-Time Rendering in Games
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（反射、IBL の章）

## 関連ページ

- [Reflections](../index.md)
- [Hi-Z SSR](../ssr-hiz.md)
- [Stochastic SSR](../ssr-stochastic.md)
- [SSR Fallback and Compositing](../ssr-fallback.md)
