---
title: Where to Apply Fog
tags:
  - 描画
---

# Where to Apply Fog

<strong>フォグは屋外では重要ですが、夜や屋内では使い方を変える必要があります</strong>。このページでは フォグを適用する場所と、夜・閉所の扱いを説明します。

!!! tip "ポイント"
    - 不透明・半透明の両方にフォグを適用する。
    - 加算ブレンドはフォグで黒に近づける。
    - 夜はフォグを暗い色に。
    - 屋内はフォグを弱める・別設定にする。

!!! info "このページを読む前に"
    - [Aerial Perspective and Fog](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 適用する場所
| 場所 | 内容 |
| --- | --- |
| フル スクリーン パス | 不透明描画後に深度から位置を再構築して一括適用。簡単 |
| マテリアルのシェーダー内 | 各物体のピクセル シェーダーでフォグを適用。半透明にも自然に適用 |
| 半透明 | 半透明は深度バッファに無いので、物ごとにシェーダー内で適用（パーティクル、ガラス） |
| ポストプロセスの前 | HDR の線形空間 |

<strong>加算ブレンドの物</strong>は フォグの色を足さず、透過率だけ掛けます（霞の中で光が薄まるだけ）。足すと遠くの加算パーティクルが白く浮きます。

## 夜と閉所
| 状況 | 扱い |
| --- | --- |
| 夜 | フォグの色を暗く。月明かりで少しだけ明るく |
| 室内 | フォグを薄くする／区画ごとに変える（ボリューム フォグ） |
| 洞窟・屋内の区画 | 区画（ボリューム）ごとにフォグの設定を持ち、境で補間 |
| ライトの周り | 点光源の周りだけ霧が光る（[Volumetric Fog](../volumetric-fog/index.md)） |

### 設計上の注意

フォグはどこにどのように適用するかで、見た目の一貫性が大きく変わります。まず、<strong>すべての描画物に適用すること</strong>が基本です。不透明物だけにフォグをかけて、パーティクルや半透明の物にかけないと、遠くの煙や窓ガラスが霞の中で不自然に浮き出ます。

次に、描画の順番と合成方法です。通常のアルファ ブレンドの物は、シェーダーの出力色にフォグを適用してからブレンドします。加算ブレンドの物（炎、光）はフォグの色を足すのでなく、透過率だけを掛けて薄めます。霞の中で光が減衰するだけだからです。フォグの色を足すと遠くの加算パーティクルが白く浮いてしまいます。

また、空にもフォグを適用するかを決めます。空は無限遠にありフォグの色の源でもあるので、通常は空にフォグを重ねません。ただし、雲や星のような空の中の物は地平線付近でフォグがかかるように調整することがあります。

## 霧をどこでかけるか

霧は <strong>最終的に画面に出る色</strong>に、かけます。どの段階でどの物にかけるかを整理します。

| 方法 | タイミング | 内容 |
| --- | --- | --- |
| 各物体のピクセル シェーダーの最後 | 物体を描くとき | 物体ごとに霧を計算して色にかける。フォワード レンダリングの標準 |
| ポスト プロセス（全画面） | 全部の物を描いた後 | 深度バッファから、各画素の距離を求めて全画素に霧をかける。ディファードの標準 |

## 方法 1：物体ごとにかける

<strong>ピクセル シェーダー</strong>の最後で、物体の色に霧を適用します。

```hlsl
float4 main(PSInput input) : SV_Target {
  float3 color = ComputeLighting(input);                              // ライティング済みの色
  float distance = length(input.world_position - g_camera_position);
  color = ApplyFog(color, distance);                                  // 最後に、霧
  return float4(color, 1.0);
}
```

長所は 半透明の物にもそのまま、かけられることです（半透明の物も自分の、ピクセル シェーダーで霧をかける）。短所はすべてのマテリアルのシェーダーに霧の、コードを入れる必要があることです。

## 方法 2：ポスト プロセス

<strong>全画面のピクセル シェーダー</strong>で、深度バッファから画素ごとの距離を復元して霧をかけます。

```hlsl
float4 FogPostPS(float2 uv : TEXCOORD0) : SV_Target {
  float3 scene = g_scene_color.Sample(g_point_clamp, uv).rgb;
  float depth = g_scene_depth.Sample(g_point_clamp, uv).r;

  // 深度から、ワールド位置を復元して、カメラまでの距離を求める。
  float3 world_pos = ReconstructWorldPosition(uv, depth);
  float distance = length(world_pos - g_camera_position);

  return float4(ApplyFog(scene, distance), 1.0);
}
```

長所は マテリアルのシェーダーを変えなくてよいこと 1 か所で霧を管理できることです。短所は半透明の物（深度に書かれない）に霧がかからないことです。

## 半透明の物をどうするか

ポスト プロセスの霧は <strong>不透明な物の、深度</strong>だけを見ます。半透明の物（煙、ガラス、パーティクル）は深度に書かれないので霧がかからず霧の中で浮いて見えます。

| 対策 | 内容 |
| --- | --- |
| 半透明の物は自分のシェーダーで、霧をかける | ポスト プロセスの霧と、同じ関数を半透明のマテリアルの、ピクセル シェーダーでも呼ぶ。ポスト プロセスは不透明にだけ、かかる（半透明はかけた後に描く） |
| 描画順を変える | 1) 不透明を描く、2) 霧をかける 3) 半透明を描く（半透明の、シェーダーに霧が組み込まれている） |

```text
① 不透明を描く（深度を書く）
② ポスト プロセスで、霧を、かける（不透明にだけ）
③ 半透明を描く（各自の、ピクセル シェーダーで、霧を、かける）
```

## 空にかけるか

<strong>空</strong>は 無限遠で深度が最大です。霧をかけると空がすべて霧の色になって空が消えます。

| 方法 | 内容 |
| --- | --- |
| 空には霧をかけない | 深度が最大（空）の画素はスキップ。空はそのまま |
| 空に少しだけ霧をかける | 地平線の近くだけ、霧の色に近づける（空と霧の境目が自然に） |
| 濃霧のとき | 空も霧の色に（霧の中にいる感じ） |

```hlsl
// 深度が最大（空）の画素は、霧をかけない。または、方向に応じた、弱い霧にする。
if (depth >= 1.0) {
  // 地平線に近いほど、霧の色に近づける（空と、遠景の、霧がつながる）。
  float horizon_blend = saturate(1.0 - abs(view_dir.y) * 3.0);
  return float4(lerp(scene, g_fog_color, horizon_blend * g_fog_sky_strength), 1.0);
}
```

## ディファード レンダリングでの注意

<strong>ディファード</strong>では ライティングの後にポスト プロセスで霧をかけます。ライティングの結果（HDR の色）に霧をかけるので物理的に正しい順序です（霧は、光の通り道の現象）。

## 色の順序

霧は <strong>ライティングの後</strong>、トーン マッピングの前にかけます。

```text
ライティング → 霧 → ポスト エフェクト（ブルーム） → トーン マッピング → ガンマ
```

トーン マッピングの後に霧をかけると 霧の色が LDR（0〜1）に押し込まれ明るい霧の表現（HDR）ができません。ブルーム（霧の中の光のにじみ）も、霧の後にかけるほうが自然です。

## よくあるミス

??? failure "半透明の物だけ、フォグがかかっていない"
    <strong>半透明にもフォグを適用</strong>する。

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
