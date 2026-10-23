---
title: パーティクルと半透明
tags:
  - 最適化
  - 3Dゲーム
---

# パーティクルと半透明

煙・炎・魔法・ガラスなどの**半透明**は、見た目を豊かにしますが、描画の中で最も重くなりやすい要素です。理由は奥の物体を見せる必要があるため、Early-Z で捨てられず、重なった数だけピクセルシェーダーとブレンドが実行されるからです。このページでは、半透明がなぜ重いのか、どう減らすかを説明します。

!!! tip "ポイント"
    - 半透明は<strong>オーバードローが避けられない</strong>。重なる分だけ計算・ブレンドする。
    - ブレンドは<strong>レンダーターゲットの読み込み＋書き込み</strong>なので、帯域幅も使う。
    - 画面を大きく覆う 1 枚が、小さな 100 枚より重いことがある。
    - 対策は縮小バッファ・枚数削減・形に合わせた板・軽いシェーダー。
    - ソートが必要（奥から手前）。順序が崩れると見た目が壊れる。
    - 数が多いときはGPU パーティクル（コンピュートで更新）。

## なぜ重いのか

| 理由 | 説明 |
| --- | --- |
| **Early-Z が効かない** | 奥も見せるので深度テストで捨てられない |
| ブレンドの読み書き | 既存の色を読んで混ぜて、書く（帯域幅を使う） |
| 重なりの数 | 煙の板が 10 枚重なれば、そのピクセルは 10 回計算される |
| 大きな板 | 画面の大半を覆う 1 枚が、数百万ピクセルを塗る |
| 透明部分の無駄 | 四角い板の中の透明な部分もシェーダーが実行される |

オーバードローを色で可視化する（重なるほど明るくする）と、どこが重いのかが一目で分かります（[調査ツール](tools.md)）。

## 減らす方法

### 縮小バッファに描く

煙・霧・炎はもともとぼんやりしているので、**半分や 4 分の 1 の解像度で描いて、最後に合成**しても見た目はあまり変わりません。ピクセル数が 1/4〜1/16 になります（[低解像度のエフェクト](low-res-effects.md)）。

| 点 | 説明 |
| --- | --- |
| 深度テスト | 縮小した深度バッファを使う（最大値・最小値で縮小） |
| 境界のにじみ | 深度を考慮したアップサンプルで、物体の縁を保つ |
| ソフト パーティクル | 深度を読んで地面との交差を柔らかくする（読み込みが増える） |

### 板を形に合わせる

四角い板に丸い煙のテクスチャを貼ると、角の透明部分が無駄になります。

| 工夫 | 説明 |
| --- | --- |
| トリミング | 板を 8 角形などにして、透明部分を減らす（頂点が増えるがピクセルが大きく減る） |
| テクスチャ アトラス | 複数の模様を 1 枚にまとめて、切り替えを減らす |
| サイズを小さく | 画面を覆う巨大な板は避ける |

### 枚数を減らす

| 工夫 | 説明 |
| --- | --- |
| LOD | 遠くでは枚数を減らす |
| 距離で消す | 小さすぎる・遠すぎるものは出さない |
| 画面を覆うほど重なる煙 | 枚数を減らして、1 枚あたりを濃くする |
| カリング | 視錐台の外のエミッターは更新・描画しない |

### シェーダーを軽くする

パーティクルのピクセルシェーダーは、数が多いので、1 回あたりを非常に軽くします。

| 工夫 | 説明 |
| --- | --- |
| ライティングを簡略化 | 煙にフルの PBR は不要。環境光と単純な方向光で十分 |
| テクスチャ読み込みを少なく | 1〜2 回に抑える |
| フォーマット | 低精度のフォーマット（FP16）を使う |

## ソートとブレンド

半透明は**奥から手前**の順に描かないと、見た目が壊れます。

| 方式 | 説明 |
| --- | --- |
| 加算ブレンド | 火花・光の粒など。順序に依存しないのでソート不要 |
| アルファ ブレンド | 煙・ガラスなど。ソートが必要 |
| オブジェクト単位のソート | カメラからの距離で並べる。粒子内の順序は無視（安いが粗い） |
| 粒子単位のソート | GPU で粒子ごとにソート（高品質だが重い） |
| OIT（順序非依存透明） | ソートなしで正しく混ぜる手法。重く、設計が必要 |

## GPU パーティクル

パーティクルが数万〜数百万になると、CPU での更新が追いつきません。**コンピュート シェーダーで位置・速度を更新**し、そのまま描画します。

| 点 | 説明 |
| --- | --- |
| CPU の負担がほぼゼロ | 生成の指示を送るだけ |
| データの置き場 | 構造化バッファに位置・速度・寿命を置く |
| 描画 | インスタンシング（インダイレクト）で、生きている粒子だけ描く |
| 衝突 | 深度バッファを読んで画面空間で簡易な衝突をする |

## 半透明が、どれだけ重いか：数字で見る

1920×1080 は、約 207 万ピクセルです。画面全体を、覆う半透明を、10 枚重ねると、どれだけのピクセルを、ブレンドするでしょうか。

```text
ブレンドするピクセル数 ＝ 207 万 × 10 枚 ＝ 約 2,070 万ピクセル / フレーム

1 ピクセルのブレンド（RGBA16F のレンダー ターゲット）:
  読む 8 バイト + 書く 8 バイト ＝ 16 バイト
帯域 ＝ 2,070 万 × 16 バイト ≒ 330 MB / フレーム
60 FPS なら ≒ 20 GB/s
```

20 GB/s は、GPU の帯域の、数%〜十数%に、当たります（GPU による）。<strong>1 つの煙の演出だけで</strong>、これだけ使います。半分の解像度で描けば、ピクセル数が 1/4 になり、帯域も、約 5 GB/s に、減ります。

## 縮小バッファに描いて、合成する

煙のような、ぼんやりした物は、半分の解像度で描いて、最後に、フル解像度へ重ねます。

```cpp
// ① 半分の解像度の、レンダー ターゲットと、縮小した深度（深度テスト用）を用意する。
SetViewport(width / 2, height / 2);
context->OMSetRenderTargets(1, half_rtv.GetAddressOf(), half_depth_dsv.Get());
Clear(half_rtv, {0, 0, 0, 0});                                    // 透明な黒で、クリア

// ② 半透明のパーティクルを、ここに描く（プリマルチプライド アルファ）。
DrawParticles();

// ③ フル解像度のシーンに、重ねて合成する。
SetViewport(width, height);
context->OMSetRenderTargets(1, scene_rtv.GetAddressOf(), nullptr);
context->PSSetShaderResources(0, 1, half_srv.GetAddressOf());
DrawFullscreenTriangle();                                         // 合成シェーダー（下）
```

```hlsl
// ③ の合成シェーダー: 縮小バッファ（rgb は色、a は、後ろを、どれだけ隠すか）を、バイリニアで、拡大して重ねる。
Texture2D g_particles : register(t0);
SamplerState g_linear : register(s0);

float4 PSComposite(float4 pos : SV_Position, float2 uv : TEXCOORD0) : SV_Target {
  float4 p = g_particles.Sample(g_linear, uv);                    // プリマルチプライド（色に、アルファが掛け済み）
  return p;                                                       // ブレンド: ONE, INV_SRC_ALPHA で、シーンに重ねる
}
```

縮小して描くと、物体の縁で、煙が、にじみます（低解像度の深度が、縁を、またぐため）。縁が気になるときは、<strong>深度を考慮した拡大</strong>（フル解像度の深度と、近い縮小の深度を、比べて、似た位置の値だけを、混ぜる）にします（[Upsampling](../graphics/ao/filtering/upsample.md) と同じ考え方）。

## GPU パーティクルを、実装する

粒子が数万を超えるなら、<strong>計算シェーダーで、粒子を更新し、そのまま描く</strong>のが、効率的です。

```hlsl
struct Particle {
  float3 position;
  float life;                // 残りの寿命（秒）。0 以下で、死ぬ
  float3 velocity;
  float size;
};

RWStructuredBuffer<Particle> g_particles : register(u0);
AppendStructuredBuffer<uint> g_alive_list : register(u1);        // 今フレーム、生きている粒子の番号

cbuffer UpdateCB : register(b0) {
  float g_dt;
  float3 g_gravity;
  uint g_particle_count;
};

[numthreads(64, 1, 1)]
void UpdateCS(uint3 id : SV_DispatchThreadID) {
  if (id.x >= g_particle_count) return;
  Particle p = g_particles[id.x];
  if (p.life <= 0.0) return;                                       // 死んでいる粒子は、飛ばす

  p.velocity += g_gravity * g_dt;
  p.position += p.velocity * g_dt;
  p.life -= g_dt;
  g_particles[id.x] = p;
  if (p.life > 0.0) g_alive_list.Append(id.x);                     // 生きている粒子の番号を、追加
}
```

```cpp
// 更新: 生きている粒子のリスト（Append バッファ）を、毎フレーム空にして、作り直す。
UINT zero = 0;
context->CSSetUnorderedAccessViews(1, 1, alive_uav.GetAddressOf(), &zero);   // カウンターを 0 に
context->Dispatch((max_particles + 63) / 64, 1, 1);

// 描画: 生きている粒子の数を、間接描画の引数へコピーして、CPU に戻さず、描く。
context->CopyStructureCount(draw_args_buffer.Get(), sizeof(UINT), alive_uav.Get());   // InstanceCount の位置へ
context->DrawInstancedIndirect(draw_args_buffer.Get(), 0);        // 4 頂点（四角形）× 生きている数
```

頂点シェーダーは、`SV_InstanceID` で、`g_alive_list` から粒子の番号を引き、`SV_VertexID` で、四角形の 4 隅を作って、カメラの方を向けます（ビルボード）。CPU は、粒子の生成の指示を送るだけで、更新も、描画の数の決定も、GPU が行います（[Structured and Raw Buffers](../directx/dx11/structured-buffer.md)、[Instanced Drawing](../directx/dx11/instancing-draw.md)）。

## よくあるミス

??? failure "画面を覆う巨大な煙を、フル解像度で描く"
    縮小バッファにします。

??? failure "透明な余白が大きい板を、そのまま使う"
    形に沿って切り詰めます。

??? failure "全粒子に、重いライティングを使う"
    簡略化します。

??? failure "加算でよい物を、アルファ ブレンドにしてソートしている"
    加算に変えるとソートが不要になります。

??? failure "オーバードローを見ずに、枚数だけ減らす"
    可視化して、重い場所から直します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 半透明は<strong>オーバードロー＋ブレンドの帯域</strong>で重い
    - [x] 縮小バッファで、ピクセル数を 1/4〜1/16 に
    - [x] 板を形に合わせ、枚数とサイズを減らす
    - [x] 加算ブレンドならソート不要
    - [x] 大量ならGPU パーティクル

## 関連ページ

- [描画最適化](index.md)
- [オーバードローと Z プリパス](overdraw.md)
- [低解像度のエフェクト](low-res-effects.md)
- [メモリ帯域幅](bandwidth.md)
- [Translucency](../graphics/translucency/index.md)
