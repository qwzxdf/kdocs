---
title: Alpha-Tested Shadows
tags:
  - 描画
---

# Alpha-Tested Shadows

<strong>葉や柵・金網のように、テクスチャのアルファで形を切り抜く物</strong>は、<strong>シャドウ マップを描くときも、同じアルファ テストが必要</strong>です。さもないと、四角い板の影が落ちます。ピクセル シェーダーが必要になり、深度専用パスが少し重くなるので、工夫が要ります。このページでは、アルファ テストの影の描き方・コスト・ミップの罠・ハッシュド アルファを説明します。

!!! tip "ポイント"
    - シャドウ マップでも、葉のテクスチャのアルファで `clip` する。
    - 深度専用パスに、ピクセル シェーダーとテクスチャ読み込みが入る。
    - 影専用の、粗いミップのアルファを使うと軽い。
    - ハッシュド アルファで滑らかなフェードにできる。

## アルファ テストの影（葉・柵）
<strong>葉・柵・金網</strong>などは<strong>テクスチャの透明部分を `clip` で捨てて</strong>、形を作っています。シャドウ マップを描くときも、同じアルファ テストをしないと、<strong>影がポリゴンの形（四角）</strong>になってしまいます。

```hlsl
void ShadowPS(float2 uv : TEXCOORD0) {
  float alpha = albedo_tex.Sample(linear_sampler, uv).a;
  clip(alpha - kAlphaCutoff);
}
```

| 点 | 説明 |
| --- | --- |
| シャドウ パスでも `clip` | アルファ付きのマテリアルは、ピクセル シェーダー付きのシャドウ パスで描く |
| Early-Z の無効化 | `clip` があると深度の書き込みがシェーダーの後になる。重くなる |
| 不透明の物は、PS なし | 深度のみのパス（PS を設定しない）で、最速。マテリアルごとにパスを分ける |
| ミップの影響 | アルファ テストの葉は、ミップでアルファが薄まる。ミップ レベルのバイアスや、アルファのカバレッジ保存が必要（遠くで影が薄くなる） |

<strong>描画順</strong>を<strong>「不透明（PS なし）→ アルファ テスト（PS あり）」</strong>にすると<strong>効率</strong>が良いです。

## 問題：葉や柵の、影が、板になる

木の、葉は、<strong>四角い板に、葉の絵</strong>を貼って、<strong>アルファ テスト</strong>で、葉の、形に、切り抜いて、描きます（[Alpha Testing](../../translucency/alpha-test/index.md)）。シャドウ パスで、この板を、そのまま、深度として、描くと、透明部分も、深度に書かれ、葉の影が、四角い板の形に、なります。

```text
 本来の影:                     アルファ テストなしで、描いた影:
   ░ ▓ ░ ▓                       ▓▓▓▓▓▓▓▓
   ▓ ░ ▓ ░     葉の形に          ▓▓▓▓▓▓▓▓    四角い板の影
   ░ ▓ ░ ▓     切り抜かれた       ▓▓▓▓▓▓▓▓
```

## 対策：シャドウ パスでも、アルファ テストをする

シャドウ パスの、<strong>ピクセル シェーダー</strong>で、<strong>メインの描画と、同じ、アルファ テスト</strong>を、行います。透明な画素は、`clip` で、捨て、深度に書きません。

```hlsl
// シャドウ パス用の、ピクセル シェーダー（アルファ テストする物だけ）。
Texture2D<float4> g_albedo : register(t0);
SamplerState g_linear_wrap : register(s0);

void main(float4 pos : SV_Position, float2 uv : TEXCOORD0) {
  float alpha = g_albedo.Sample(g_linear_wrap, uv).a;
  clip(alpha - 0.5);                          // メインの描画と、同じしきい値
  // 色は出力しない。深度だけが、書かれる。
}
```

| 要素 | 内容 |
| --- | --- |
| 頂点シェーダー | UV を、ピクセル シェーダーへ、渡す（深度のみの、パスでは、UV を、省いていた） |
| ピクセル シェーダー | アルファを、読んで、`clip`。テクスチャの、読み込みが、必要になる |
| アルファ テストしない物 | ピクセル シェーダーなし（深度のみ。速い）。物ごとに、シェーダーを、切り替える |

```cpp
// 物ごとに、シェーダーを切り替える（アルファ テストする物だけ、ピクセル シェーダーを使う）。
for (const Mesh& m : shadow_casters) {
  if (m.alpha_tested) {
    context->PSSetShader(shadow_alpha_ps.Get(), nullptr, 0);
    context->PSSetShaderResources(0, 1, m.albedo_srv.GetAddressOf());
  } else {
    context->PSSetShader(nullptr, nullptr, 0);         // 深度のみ（最速）
  }
  Draw(m);
}
```

## 影用の、アルファの、工夫

### ① しきい値を、メインと、そろえる

メインの描画（アルファ 0.5）と、影の（0.5）で、<strong>しきい値が、違う</strong>と、<strong>葉の形と、影の形が、ずれます</strong>。同じ値を、使います。ミップでも、そろえる（[Foliage Translucency](../../terrain/vegetation/translucency.md)）。

### ② 低解像度の、アルファを、読む

影は、<strong>細部が、見えにくい</strong>ので、<strong>アルファのミップ</strong>を、1〜2 段、粗く読むと、テクスチャ読み込みの、コストが、減り、影の縁が、なめらかになります。

```hlsl
float alpha = g_albedo.SampleBias(g_linear_wrap, uv, 1.0).a;       // ミップを 1 段、粗く読む
clip(alpha - 0.5);
```

### ③ ハッシュ アルファ

<strong>影を、確率的に</strong>、薄くする方法です（[Hashed Alpha](../../translucency/alpha-test/hashed-alpha.md)）。<strong>PCF の、サンプルごとに、違う、しきい値</strong>を使うと、葉の影が、柔らかく、半透明に、見えます。

```hlsl
float threshold = BlueNoiseThreshold(pos.xy);
clip(alpha - threshold);                       // 影のアルファも、確率的
```

### ④ 薄くなる、遠くの葉

遠くの、<strong>ミップで、アルファが、薄くなる</strong>問題は、<strong>影にも、起きます</strong>（葉の影が、スカスカ）。アルファ ミップの、カバレッジ補正（Castaño、2010）を、メインと、影の、両方に、適用します。

## 効率

| 項目 | 内容 |
| --- | --- |
| ピクセル シェーダーが、必要になる | 深度のみ（シェーダーなし）が、使えず、シャドウ パスが、重くなる |
| オーバードロー | 葉は、重なって描かれる。影のパスでも、同じ（Early-Z が、効かない。[Performance and Shadow Passes](../../translucency/alpha-test/performance.md)） |
| 対策 1 | 遠くの葉は、影を、落とさない（影を落とす距離を、限る） |
| 対策 2 | 影用の、簡略メッシュ（葉の枚数を、減らした、LOD）を、使う |
| 対策 3 | 木の、影は、幹と、大きな、枝だけを、落とし、葉は、1 枚の、大きな、アルファ カードに、まとめる |

## よくあるミス

??? failure "葉が板の影になる"
    <strong>深度パスにも、アルファ テストを入れる</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 影の深度パスにもアルファ テストが必要
    - [x] ピクセル シェーダーが増えるのでコストに注意

## 参考

- Wyman, McGuire, "Hashed Alpha Testing", Symposium on Interactive 3D Graphics and Games 2017
- Castaño, "Computing Alpha Mipmaps", 2010
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018
- Microsoft Learn, "clip (HLSL)"

## 関連ページ

- [Special Cases](index.md)
- [Rendering Depth](../shadow-map-basics/render-depth.md)
- [Alpha Testing](../../translucency/alpha-test/index.md)
