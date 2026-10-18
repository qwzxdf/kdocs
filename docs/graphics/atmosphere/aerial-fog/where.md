---
title: Where to Apply Fog
tags:
  - 描画
---

# Where to Apply Fog

<strong>フォグは、屋外では重要ですが、夜や屋内では、使い方を変える必要があります</strong>。このページでは、<strong>フォグを適用する場所と、夜・閉所の扱い</strong>を説明します。

!!! tip "ポイント"
    - 不透明・半透明の両方に、フォグを適用する。
    - 加算ブレンドは、フォグで黒に近づける。
    - 夜は、フォグを暗い色に。
    - 屋内は、フォグを弱める・別設定にする。

## 適用する場所
| 場所 | 内容 |
| --- | --- |
| フル スクリーン パス | 不透明描画後に深度から位置を再構築して一括適用。簡単 |
| マテリアルのシェーダー内 | 各物体のピクセル シェーダーでフォグを適用。半透明にも自然に適用 |
| 半透明 | 半透明は深度バッファに無いので、物ごとにシェーダー内で適用（パーティクル、ガラス） |
| ポストプロセスの前 | HDR の線形空間 |

<strong>加算ブレンドの物</strong>は、<strong>フォグの色を足さず、透過率だけ掛けます</strong>（霞の中で光が薄まるだけ）。足すと遠くの加算パーティクルが白く浮きます。

## 夜と閉所
| 状況 | 扱い |
| --- | --- |
| 夜 | フォグの色を暗く。月明かりで少しだけ明るく |
| 室内 | フォグを薄くする／区画ごとに変える（ボリューム フォグ） |
| 洞窟・屋内の区画 | 区画（ボリューム）ごとにフォグの設定を持ち、境で補間 |
| ライトの周り | 点光源の周りだけ霧が光る（[Volumetric Fog](../volumetric-fog/index.md)） |

### 設計上の注意

フォグは、どこにどのように適用するかで、見た目の一貫性が大きく変わります。まず、<strong>すべての描画物に適用すること</strong>が基本です。不透明物だけにフォグをかけて、パーティクルや半透明の物にかけないと、遠くの煙や窓ガラスが、霞の中で不自然に浮き出ます。

次に、<strong>描画の順番と合成方法</strong>です。通常のアルファ ブレンドの物は、シェーダーの出力色にフォグを適用してからブレンドします。加算ブレンドの物（炎、光）は、フォグの色を足すのでなく、<strong>透過率だけを掛けて</strong>薄めます。霞の中で光が減衰するだけだからです。フォグの色を足すと、遠くの加算パーティクルが白く浮いてしまいます。

また、<strong>空</strong>にもフォグを適用するかを決めます。空は無限遠にあり、フォグの色の源でもあるので、通常は空にフォグを重ねません。ただし、雲や星のような空の中の物は、地平線付近でフォグがかかるように調整することがあります。

## 霧を、どこで、かけるか

霧は、<strong>最終的に、画面に出る、色</strong>に、かけます。<strong>どの段階で、どの物に、かけるか</strong>を、整理します。

| 方法 | タイミング | 内容 |
| --- | --- | --- |
| 各物体の、ピクセル シェーダーの最後 | 物体を、描くとき | 物体ごとに、霧を計算して、色に、かける。フォワード レンダリングの、標準 |
| ポスト プロセス（全画面） | 全部の物を、描いた後 | 深度バッファから、各画素の、距離を、求めて、全画素に、霧を、かける。ディファードの、標準 |

## 方法 1：物体ごとに、かける

<strong>ピクセル シェーダー</strong>の、最後で、<strong>物体の色に、霧を、適用</strong>します。

```hlsl
float4 main(PSInput input) : SV_Target {
  float3 color = ComputeLighting(input);                              // ライティング済みの色
  float distance = length(input.world_position - g_camera_position);
  color = ApplyFog(color, distance);                                  // 最後に、霧
  return float4(color, 1.0);
}
```

<strong>長所</strong>は、<strong>半透明の物にも、そのまま、かけられる</strong>ことです（半透明の物も、自分の、ピクセル シェーダーで、霧を、かける）。短所は、すべての、マテリアルの、シェーダーに、霧の、コードを、入れる必要があることです。

## 方法 2：ポスト プロセス

<strong>全画面の、ピクセル シェーダー</strong>で、<strong>深度バッファ</strong>から、画素ごとの、距離を、復元して、霧を、かけます。

```hlsl
float4 FogPostPS(float2 uv : TEXCOORD0) : SV_Target {
  float3 scene = g_scene_color.Sample(g_point_clamp, uv).rgb;
  float depth = g_scene_depth.Sample(g_point_clamp, uv).r;

  // 深度から、ワールド位置を、復元して、カメラまでの距離を、求める。
  float3 world_pos = ReconstructWorldPosition(uv, depth);
  float distance = length(world_pos - g_camera_position);

  return float4(ApplyFog(scene, distance), 1.0);
}
```

<strong>長所</strong>は、<strong>マテリアルの、シェーダーを、変えなくて、よい</strong>こと、1 か所で、霧を、管理できることです。短所は、半透明の物（深度に、書かれない）に、霧が、かからないことです。

## 半透明の物を、どうするか

ポスト プロセスの、霧は、<strong>不透明な物の、深度</strong>だけを、見ます。<strong>半透明の物</strong>（煙、ガラス、パーティクル）は、深度に、書かれないので、霧が、かからず、霧の中で、浮いて見えます。

| 対策 | 内容 |
| --- | --- |
| 半透明の物は、自分のシェーダーで、霧をかける | ポスト プロセスの霧と、同じ関数を、半透明の、マテリアルの、ピクセル シェーダーでも、呼ぶ。ポスト プロセスは、不透明にだけ、かかる（半透明は、かけた後に、描く） |
| 描画順を、変える | 1) 不透明を描く、2) 霧を、かける、3) 半透明を描く（半透明の、シェーダーに、霧が、組み込まれている） |

```text
① 不透明を描く（深度を書く）
② ポスト プロセスで、霧を、かける（不透明にだけ）
③ 半透明を描く（各自の、ピクセル シェーダーで、霧を、かける）
```

## 空に、かけるか

<strong>空</strong>は、<strong>無限遠</strong>で、深度が、最大です。霧を、かけると、空が、すべて、霧の色になって、空が、消えます。

| 方法 | 内容 |
| --- | --- |
| 空には、霧を、かけない | 深度が、最大（空）の画素は、スキップ。空は、そのまま |
| 空に、少しだけ、霧をかける | 地平線の近くだけ、霧の色に、近づける（空と、霧の、境目が、自然に） |
| 濃霧のとき | 空も、霧の色に（霧の中に、いる感じ） |

```hlsl
// 深度が、最大（空）の画素は、霧をかけない。または、方向に応じた、弱い霧にする。
if (depth >= 1.0) {
  // 地平線に近いほど、霧の色に近づける（空と、遠景の、霧が、つながる）。
  float horizon_blend = saturate(1.0 - abs(view_dir.y) * 3.0);
  return float4(lerp(scene, g_fog_color, horizon_blend * g_fog_sky_strength), 1.0);
}
```

## ディファード レンダリングでの、注意

<strong>ディファード</strong>では、<strong>ライティングの後</strong>に、ポスト プロセスで、霧を、かけます。ライティングの、結果（HDR の色）に、霧を、かけるので、物理的に、正しい順序です（霧は、光の通り道の現象）。

## 色の、順序

霧は、<strong>ライティングの、後</strong>、<strong>トーン マッピングの、前</strong>に、かけます。

```text
ライティング → 霧 → ポスト エフェクト（ブルーム） → トーン マッピング → ガンマ
```

<strong>トーン マッピングの、後</strong>に、霧を、かけると、<strong>霧の、色が、LDR</strong>（0〜1）に、押し込まれ、明るい霧の、表現（HDR）が、できません。ブルーム（霧の中の、光の、にじみ）も、霧の後に、かけるほうが、自然です。

## よくあるミス

??? failure "半透明の物だけ、フォグがかかっていない"
    <strong>半透明にも、フォグを適用</strong>する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] すべての物にかけ、場所で設定を変える

## 参考

- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（参加媒質、雲、霧の章）
- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique", Computer Graphics Forum (Eurographics Symposium on Rendering 2020)
- Wronski, "Volumetric Fog: Unified Compute Shader Based Solution to Atmospheric Scattering", SIGGRAPH 2014, Advances in Real-Time Rendering in Games

## 関連ページ

- [Aerial Perspective and Fog](index.md)
- [Matching Fog Color to the Sky](color-match.md)
