---
title: Hair Transparency
tags:
  - 描画
---

# Hair Transparency

髪の毛 1 本は、<strong>画素より細く、半透明</strong>です。しかも、頭には何万本もあり、<strong>何十層も重なります</strong>。これを正しい順序で合成するのは、半透明描画の中でも最も難しい問題の 1 つです。このページでは、髪の透明を扱う代表的な方法（アルファ テスト、A2C、ハッシュド アルファ、OIT、2 パス描画）と、使い分けを説明します。

!!! tip "ポイント"
    - 髪は<strong>画素より細く、何層も重なる</strong>。ふつうのアルファ ブレンド（ソート必要）は破綻する。
    - カードには<strong>アルファ テスト ＋ A2C（または TAA）</strong>が基本。深度を書けるので影も付く。
    - 2 パス描画：不透明部分（アルファ ≥ 0.9）を先に深度付きで描き、半透明の縁を後でブレンド。
    - ストランドには<strong>OIT（PPLL など）</strong>が使われる。メモリと時間が重い。
    - 髪専用のソート：カード単位で、根元から毛先など、描画順を工夫する。

## なぜ難しいのか

[Alpha Blending and Sorting](../../translucency/blending-sorting/index.md) で見たとおり、アルファ ブレンドは、<strong>奥から手前の順</strong>に描く必要があります。髪では、これが 2 つの理由で破綻します。

第 1 に、<strong>ポリゴンの数が多く、交差します</strong>。髪のカードは、頭の周りに何十枚も重なり、互いに食い込んでいます。1 枚の板の一部が別の板の手前、別の一部が奥、という状況が普通に起きるので、ポリゴン単位のソートでは、順序が決められません。

第 2 に、<strong>髪の毛は半透明の縁を持ちます</strong>。髪の束の端は、アルファがなだらかに 0 へ落ちており、縁が柔らかく見える設計になっています。この縁を、不透明のように扱うと、輪郭がギザギザになります。半透明として扱うと、順序の問題が出ます。

## アルファ テスト

最も単純な方法は、<strong>アルファ テスト</strong>です。アルファが 0.5 などのしきい値より小さい画素を捨て（`clip`）、それ以外を不透明として描きます。深度を書けるので、ソートが不要で、Z バッファで正しく重なります。影も付けられます。

問題は、<strong>輪郭がギザギザ</strong>になることと、遠くで髪が<strong>やせる</strong>ことです。アルファの値が連続的に変わる縁が、0 と 1 の 2 値に切られるため、階段状になります。また、ミップマップでアルファが平均されて薄まり、閾値を超える画素が減るので、遠くで髪が薄くなります（[Alpha Testing](../../translucency/alpha-test/index.md) のミップの罠）。

## A2C（Alpha to Coverage）と TAA

ギザギザを滑らかにする方法の 1 つが、<strong>Alpha to Coverage</strong>（A2C）です。MSAA を使って、アルファの値を、サブサンプルの<strong>カバレッジ</strong>（覆う数）に変換します。たとえば、アルファが 0.5 で 4x MSAA なら、4 つのサブサンプルのうち 2 つを覆います。アルファ ブレンドのようなソートが不要で、縁が滑らかになります（[Alpha to Coverage](../../translucency/alpha-test/alpha-to-coverage.md)）。MSAA が使えない（ディファード）場合は、ハッシュド アルファと TAA の組み合わせで、同様の効果が得られます（[Hashed Alpha](../../translucency/alpha-test/hashed-alpha.md)）。ノイズ的に画素を捨て、TAA が時間方向に平均して滑らかにします。

これらは、髪のカードに対して、実用的で標準的な方法です。ただし、A2C のサンプル数（4〜8）の段階しか表せないため、髪の淡い縁を、完全には再現できません。

## 2 パス描画

髪のカードの品質を上げる、実用的な方法が <strong>2 パス描画</strong>です。髪を、不透明に近い部分と、半透明の縁に分けて、別々に描きます。

1. 不透明パス：アルファが高い画素（たとえば 0.9 以上）だけを、アルファ テストで描き、深度を書きます。髪の中心部分が、正しい深度順で、不透明に描かれます。
2. 半透明パス：深度書き込みなしで、アルファ ブレンドで、髪の縁（アルファが 0〜0.9 の部分）を描きます。ここで、不透明パスの深度を使って、髪の中心の背後の縁が隠れるようにします。

この方法で、中心部分は順序が正しく、縁は柔らかく見えます。半透明パスのカードは、<strong>髪の層の順（内側から外側）</strong>でソートします。カードの重なる順序が、髪の構造から決まっているので、ポリゴン単位のソートでなく、<strong>カード単位の固定順</strong>で描けます。

さらに、半透明パスのシェーディングを、不透明パスと分けて、簡略化できます（縁は細く暗いので、鏡面を省略する、など）。

## ストランド用の OIT

1 本ずつ描くストランドは、さらに難しい問題です。ストランドは<strong>画素より細く</strong>、1 画素に数十本が重なります。ポリゴン単位のソートは不可能で、アルファ テストでは細すぎて消えます。ここでは、<strong>OIT</strong>（Order-Independent Transparency、順序非依存の透明）が使われます。

AMD の TressFX は、<strong>PPLL</strong>（Per-Pixel Linked List）を使います。各画素に、その画素を覆う髪のフラグメントを、連結リストとして保存し、最後に深度順に並べて合成します（[PPLL](../../translucency/oit/ppll.md)）。正確ですが、メモリ（画素 × 層数）と、画素ごとのソートの時間が大きいです。TressFX では、保存するフラグメントを<strong>手前の数枚</strong>（たとえば 8 枚）に絞り、それより奥のフラグメントは、Weighted Blended のような近似でまとめて処理する、ハイブリッドも使われます（[Hybrid Approaches](../../translucency/oit/hybrid.md)）。

近年の Unreal Engine の Groom は、別のアプローチで、<strong>ビジビリティ バッファ</strong>にストランドを描き（ソフトウェア ラスタライズでサブピクセル精度）、画素ごとに最も手前の数本だけを保存して、MSAA 的に合成します。

## 髪の根元から毛先への、アルファの設計

髪のカードのアルファ テクスチャは、<strong>根元から毛先へ</strong>向かって、<strong>徐々に薄くなる</strong>ように作ります。根元は不透明で、毛先に向かって細く、アルファが下がります。毛先を完全に不透明にしてしまうと、髪の束の端が硬く、板のように見えます。根元側が不透明なので、頭皮が透けて見えるのを防ぎます。

髪の色の濃さも、根元は暗く、毛先は明るくなるのが一般的です（頭皮に近い部分は陰になるため）。

## 描画の順序まとめ

髪を含むシーンの描画順は、次のようになります。

1. 不透明な物体（地形・建物・キャラクターの体）を描く。
2. 髪の不透明パス（アルファ テスト、深度を書く）。
3. 肌の SSS などの処理（髪の領域を除いて）。
4. 髪の半透明パス（縁のブレンド、深度は書かない）。
5. ほかの半透明（パーティクルなど）。
6. TAA・ポストプロセス。

## 実装：ハッシュド アルファ テストと、2 パス描画

### ハッシュド アルファ テスト（Wyman と McGuire、2017）

アルファ テストの閾値を、固定の 0.5 にすると、細い毛が、ぷつぷつ途切れます。閾値を、画素ごとに、ばらつかせ、時間で変えると、TAA が平均して、半透明に見えます。

```hlsl
// 画素ごとに、疑似乱数の閾値を決め、アルファがそれより小さければ捨てる（ワールド位置から決めるので、動いても貼りつく）。
float Hash(float2 p) { return frac(sin(dot(p, float2(127.1, 311.7))) * 43758.5453); }

float HashedThreshold(float3 object_pos, float3 object_dx, float3 object_dy) {
  float max_deriv = max(length(object_dx), length(object_dy));            // 画面上の 1 画素が、オブジェクト空間で覆う大きさ
  float pix_scale = 1.0 / max_deriv;
  float2 pix_scale_pair = float2(exp2(floor(log2(pix_scale))), exp2(ceil(log2(pix_scale))));
  float2 alpha = float2(Hash(floor(pix_scale_pair.x * object_pos.xy)), Hash(floor(pix_scale_pair.y * object_pos.xy)));
  float lerp_factor = frac(log2(pix_scale));
  return lerp(alpha.x, alpha.y, lerp_factor);                              // 2 つのスケールの閾値を補間
}
```

閾値の模様を、物体に貼りつけておくと、カメラが動いても、ちらつきません。スケールを、距離に応じて 2 の冪で切り替えるのは、遠くでも、近くでも、同じ粗さに見せるためです。

```hlsl
// ピクセル シェーダーの最後で、アルファと閾値を比べる。
float threshold = clamp(HashedThreshold(input.object_pos, ddx(input.object_pos), ddy(input.object_pos)), 1e-3, 1.0);
if (alpha < threshold) discard;
```

### 2 パス描画：まず、毛先を、深度に書き、次に、色を描く

```cpp
// パス 1: アルファ テスト（閾値 0.5 ほど）で、深度だけ書く。毛の芯の部分が、確実に、深度を作る。
context->OMSetDepthStencilState(depth_write_state.Get(), 0);
DrawHairDepthOnly();

// パス 2: 深度は、書かずに、比較だけ（EQUAL ではなく LESS_EQUAL）。色を、アルファ ブレンドで描く（奥から手前の順に並べ替えた、ストランド）。
context->OMSetDepthStencilState(depth_test_only_state.Get(), 0);
context->OMSetBlendState(alpha_blend_state.Get(), nullptr, 0xFFFFFFFF);
DrawHairColor();
```

パス 1 で、髪の「芯」を確定させると、パス 2 では、毛の周りの、柔らかい縁だけが、アルファ ブレンドされ、重なりの順序の乱れが、目立ちません。

## よくあるミス

??? failure "髪の輪郭がギザギザで、ちらつく"
    <strong>A2C（MSAA）</strong>か<strong>ハッシュド アルファ ＋ TAA</strong>に切り替える。

??? failure "遠くで髪が薄くなって、透けて見える"
    <strong>ミップでアルファが薄まっている</strong>。<strong>ミップごとにアルファを補正</strong>する（カバレッジ保存）。

??? failure "髪の縁が、頭皮や服の手前に出てしまう"
    <strong>半透明パスの描画順が、深度と合っていない</strong>。<strong>不透明パスの深度</strong>を読んで、背後を隠す。

??? failure "OIT のメモリが足りず、髪の一部が欠ける"
    <strong>保存するフラグメントの数を絞り</strong>、<strong>残りは近似でまとめる</strong>（ハイブリッド OIT）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 髪は<strong>細く、何層も重なる</strong>ので、ふつうのブレンドは破綻する
    - [x] カードは<strong>アルファ テスト ＋ A2C（または TAA）</strong>。2 パスで中心と縁を分ける
    - [x] ストランドは OIT（PPLL）、またはビジビリティ バッファ
    - [x] アルファは根元から毛先へ薄くする

## 参考

- AMD GPUOpen, "TressFX" ドキュメント
- Yang, Hensley, Grün, Thibieroz, "Real-Time Concurrent Linked List Construction on the GPU"（EGSR 2010）
- Wyman, McGuire, "Hashed Alpha Testing"（I3D 2017）

## 関連ページ

- [Hair Overview](index.md)
- [Hair Geometry](geometry.md)
- [Alpha Testing](../../translucency/alpha-test/index.md)
- [Order-Independent Transparency (OIT)](../../translucency/oit/index.md)
