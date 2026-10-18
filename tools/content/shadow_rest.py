import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import pg  # noqa: E402

LOKOVIC = '''Lokovic, Veach, "Deep Shadow Maps", SIGGRAPH 2000（半透明の、影）'''
KIM = '''Kim, Neumann, "Opacity Shadow Maps", Eurographics Workshop on Rendering 2001'''
BLINN = '''Blinn, "Me and My (Fake) Shadow", IEEE Computer Graphics and Applications, Vol. 8, No. 1, 1988（平面への、投影影）'''
WYMAN = '''Wyman, McGuire, "Hashed Alpha Testing", Symposium on Interactive 3D Graphics and Games 2017'''
CASTANO = '''Castaño, "Computing Alpha Mipmaps", 2010'''
ENGEL = '''Engel, "Cascaded Shadow Maps", ShaderX5, 2006'''
ZHANG = '''Zhang, Sun, Zhu, "Parallel-Split Shadow Maps for Large-Scale Virtual Environments", VRCIA 2006'''
DIMITROV = '''Dimitrov, "Cascaded Shadow Maps", NVIDIA White Paper, 2007'''
VALIENT = '''Valient, "Stable Rendering of Cascaded Shadow Maps", ShaderX6, 2008'''
RTR = '''Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018'''
FERNANDO = '''Fernando, "Percentage-Closer Soft Shadows", SIGGRAPH 2005 Sketches'''
REEVES = '''Reeves, Salesin, Cook, "Rendering Antialiased Shadows with Depth Maps", SIGGRAPH 1987'''
MCGUIRE = '''McGuire, Mara, "Efficient GPU Screen-Space Ray Tracing", Journal of Computer Graphics Techniques, Vol. 3, No. 4, 2014'''
WRIGHT = '''Wright, "Dynamic Occlusion with Signed Distance Fields", SIGGRAPH 2015, Advances in Real-Time Rendering in Games'''
QUILEZ = '''Quilez, "Soft Shadows in Raymarched SDFs", iquilezles.org'''
HART = '''Hart, "Sphere Tracing: A Geometric Method for the Antialiased Ray Tracing of Implicit Surfaces", The Visual Computer, Vol. 12, 1996'''
CROW = '''Crow, "Shadow Algorithms for Computer Graphics", SIGGRAPH 1977'''
EVERITT = '''Everitt, Kilgard, "Practical and Robust Stenciled Shadow Volumes for Hardware-Accelerated Rendering", NVIDIA White Paper, 2002'''
DXR = '''Microsoft, "DirectX Raytracing (DXR) Functional Spec"'''
HEITZ = '''Heitz, Hill, McGuire, "Combining Analytic Direct Illumination and Stochastic Shadows", Symposium on Interactive 3D Graphics and Games 2018'''
SCHIED = '''Schied et al., "Spatiotemporal Variance-Guided Filtering: Real-Time Reconstruction for Path-Traced Global Illumination", High-Performance Graphics 2017'''
FERNANDO01 = '''Fernando, Fernandez, Bala, Greenberg, "Adaptive Shadow Maps", SIGGRAPH 2001'''
LEFOHN = '''Lefohn, Sengupta, Owens, "Resolution-Matched Shadow Maps", ACM Transactions on Graphics, Vol. 26, No. 4, 2007'''
GIEGL = '''Giegl, Wimmer, "Queried Virtual Shadow Maps", Symposium on Interactive 3D Graphics and Games 2007'''

# ================================================================ special cases
pg.Dedup("shadows/special-cases/index.md")
pg.Add("shadows/special-cases/index.md", '''
## 特殊なケース：通常の、シャドウ マップでは、うまくいかない物

通常の、シャドウ マップは、**不透明で、閉じた、メッシュ**を、前提にしています。実際の、ゲームには、次のような、**例外**が、あります。

| ケース | 問題 | ページ |
| --- | --- | --- |
| **アルファ テストの物**（葉、柵、金網） | 透明部分も、影になる | [Alpha-Tested Shadows](alpha-test-shadows.md) |
| **半透明の物**（ガラス、煙、色付きの窓） | 光を、一部、通す | [Translucent Shadows](translucent-shadows.md) |
| **キャラクター** | 小さな、動く物。**接地**と、**自己影**が、重要。**色**の、問題も | [Character Shadows and Color](character-shadows.md) |
| **遠景** | シャドウ マップの、範囲外。**遠くの影**を、どう、扱うか | [Distant Shadows](distant-shadows.md) |
| **簡易な影**（接地、軽量） | シャドウ マップが、**重すぎる**、**要らない** | [Blob and Planar Projected Shadows](blob-planar.md) |

## 共通の、考え方

| 考え方 | 内容 |
| --- | --- |
| **影の目的を、考える** | その影は、**何のため**か。**物が、地面に、接している**ことを、示す（**接地感**）のか、**光の方向**を、見せるのか、**雰囲気**か |
| **物ごとに、方法を、変える** | **主役**（キャラクター）には、**高品質**。**背景**には、**簡易** |
| **見えない、差は、省く** | **遠く、小さい、暗い**影は、**簡易な方法**で、十分。**本物のシャドウ マップ**を、使わない |

''', before="## よくあるミス")
pg.Refs("shadows/special-cases/index.md", [RTR, BLINN, LOKOVIC, WYMAN])

pg.Dedup("shadows/special-cases/alpha-test-shadows.md")
pg.Add("shadows/special-cases/alpha-test-shadows.md", '''
## 問題：葉や柵の、影が、板になる

木の、葉は、**四角い板に、葉の絵**を貼って、**アルファ テスト**で、**葉の、形に、切り抜いて**、描きます（[Alpha Testing](../../translucency/alpha-test/index.md)）。**シャドウ パス**で、この板を、**そのまま**、**深度として、描く**と、**透明部分も、深度に書かれ**、**葉の影が、四角い板**の形に、なります。

```text
 本来の影:                     アルファ テストなしで、描いた影:
   ░ ▓ ░ ▓                       ▓▓▓▓▓▓▓▓
   ▓ ░ ▓ ░     葉の形に          ▓▓▓▓▓▓▓▓    四角い板の影
   ░ ▓ ░ ▓     切り抜かれた       ▓▓▓▓▓▓▓▓
```

## 対策：シャドウ パスでも、アルファ テストをする

シャドウ パスの、**ピクセル シェーダー**で、**メインの描画と、同じ、アルファ テスト**を、行います。**透明な画素**は、**`clip`** で、**捨て**、**深度に書きません**。

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
| 頂点シェーダー | **UV を、ピクセル シェーダーへ**、渡す（深度のみの、パスでは、UV を、省いていた） |
| ピクセル シェーダー | **アルファを、読んで、`clip`**。**テクスチャの、読み込みが、必要**になる |
| アルファ テストしない物 | **ピクセル シェーダーなし**（深度のみ。**速い**）。**物ごとに、シェーダーを、切り替える** |

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

メインの描画（アルファ 0.5）と、影の（0.5）で、**しきい値が、違う**と、**葉の形と、影の形が、ずれます**。**同じ値**を、使います。**ミップ**でも、そろえる（[Foliage Translucency](../../terrain/vegetation/translucency.md)）。

### ② 低解像度の、アルファを、読む

影は、**細部が、見えにくい**ので、**アルファのミップ**を、**1〜2 段、粗く**読むと、**テクスチャ読み込みの、コスト**が、減り、**影の縁が、なめらか**になります。

```hlsl
float alpha = g_albedo.SampleBias(g_linear_wrap, uv, 1.0).a;       // ミップを 1 段、粗く読む
clip(alpha - 0.5);
```

### ③ ハッシュ アルファ

**影を、確率的に**、薄くする方法です（[Hashed Alpha](../../translucency/alpha-test/hashed-alpha.md)）。**PCF の、サンプルごとに、違う、しきい値**を使うと、**葉の影が、柔らかく、半透明**に、見えます。

```hlsl
float threshold = BlueNoiseThreshold(pos.xy);
clip(alpha - threshold);                       // 影のアルファも、確率的
```

### ④ 薄くなる、遠くの葉

遠くの、**ミップで、アルファが、薄くなる**問題は、**影にも、起きます**（**葉の影が、スカスカ**）。**アルファ ミップの、カバレッジ補正**（Castaño、2010）を、メインと、影の、**両方に**、適用します。

## 効率

| 項目 | 内容 |
| --- | --- |
| **ピクセル シェーダーが、必要になる** | 深度のみ（シェーダーなし）が、**使えず**、シャドウ パスが、**重くなる** |
| **オーバードロー** | 葉は、**重なって**描かれる。影のパスでも、**同じ**（Early-Z が、効かない。[Performance and Shadow Passes](../../translucency/alpha-test/performance.md)） |
| 対策 1 | **遠くの葉は、影を、落とさない**（影を落とす距離を、限る） |
| 対策 2 | **影用の、簡略メッシュ**（葉の枚数を、減らした、LOD）を、使う |
| 対策 3 | **木の、影は、幹と、大きな、枝だけ**を、落とし、**葉は、1 枚の、大きな、アルファ カード**に、**まとめる** |

''', before="## よくあるミス")
pg.Refs("shadows/special-cases/alpha-test-shadows.md", [WYMAN, CASTANO, RTR, "Microsoft Learn, \"clip (HLSL)\""])

pg.Dedup("shadows/special-cases/translucent-shadows.md")
pg.Add("shadows/special-cases/translucent-shadows.md", '''
## 問題：半透明の物は、光を、一部、通す

ガラス窓、色付きの、ステンド グラス、煙、薄い、布は、**光を、一部だけ、通します**。通常の、シャドウ マップは、**光が通るか、完全に遮られるか**の、**二択**です。そのまま、**半透明の物を、描く**と、**完全な影**に、なるか、**影が、まったく、できない**かの、**どちらか**に、なってしまいます。

| 物 | 現実の影 | 通常のシャドウ マップ（不透明として、描く） | 描かない場合 |
| --- | --- | --- | --- |
| 無色の、ガラス | ほぼ、透明（わずかに、暗い） | **真っ黒**（間違い） | 影なし（近い） |
| 色付きガラス | **色付きの影** | 真っ黒 | 影なし |
| 煙・霧 | **薄い**影（密度に、比例） | 真っ黒 | 影なし |

## 方法 1：影を、落とさない（最も簡単）

**半透明の物は、シャドウ パスで、描かない**。**無色の、ガラス**や、**薄い**物は、これで、**十分**な場合が、多いです。

## 方法 2：アルファに応じた、確率的な影

**アルファが、0.3 の、物**を、**30% の画素だけ、不透明として、シャドウ マップに、描きます**。**PCF**で、読むと、**平均されて、30% の、濃さの影**に、なります（[Hashed Alpha](../../translucency/alpha-test/hashed-alpha.md)）。

```hlsl
// 半透明の影: アルファを、ランダムなしきい値と、比べて、確率的に、深度を書く。
void main(float4 pos : SV_Position, float2 uv : TEXCOORD0) {
  float alpha = g_albedo.Sample(g_linear_wrap, uv).a * g_opacity;
  clip(alpha - BlueNoiseThreshold(pos.xy));        // アルファが小さいほど、深度が書かれにくい
}
```

| 長所 | 短所 |
| --- | --- |
| 簡単。**PCF が、そのまま、使える** | **ノイズ**（TAA や、広い PCF で、減らす） |
| 半透明の度合いが、**反映**される | **色**は、反映されない（影は、グレー） |

## 方法 3：色付きの、影

**色付きガラス**の、影は、**ガラスの色**に、染まります。**光が、ガラスを、通る間に、吸収**されて、**ガラスの色**だけが、残るためです。**色付きの、影**を、作るには、**シャドウ マップを、2 枚**、使います。

| シャドウ マップ | 内容 |
| --- | --- |
| ① **不透明な物だけ**の、深度 | 通常のシャドウ マップ |
| ② **半透明な物の、色（透過色）** | **半透明な物**を、描き、**各画素の、光の、透過色**を、**乗算ブレンド**で、書き込む（カラー テクスチャ） |

```hlsl
// 半透明の、シャドウ パス（②）: 光の透過色を、乗算で積む（RGB のレンダー ターゲット）。
// ブレンド: SrcBlend = ZERO、DestBlend = SRC_COLOR（現在の値 × 出力色）。初期値は (1,1,1)。
float4 main(PSInput input) : SV_Target {
  float4 tint = g_albedo.Sample(g_linear_wrap, input.uv);
  // 透過色: α が小さい（透明）ほど、白（影響なし）。α が大きいほど、ガラスの色。
  float3 transmit = lerp(float3(1, 1, 1), tint.rgb, tint.a);
  return float4(transmit, 1.0);
}
```

```hlsl
// メイン パス: 不透明な影（深度）で光を遮り、半透明な影（色）で光を染める。
float opaque_lit = SampleOpaqueShadow(world_pos);             // 0 or 1（PCF 込み）
float3 tint = g_translucent_shadow.Sample(g_linear_clamp, uv).rgb;   // 光が、ガラスを通ったあとの、色
// ただし、ガラスより、手前にある画素だけ、色を受ける（ガラスの、奥にある物だけが、染まる）。
float glass_depth = g_translucent_depth.Sample(g_linear_clamp, uv);
float3 light_color = (depth > glass_depth) ? g_light_color * tint : g_light_color;
float3 lit = light_color * opaque_lit;
```

**「画素が、ガラスの、奥にあるか」**を、判定するために、**ガラスの、深度**（半透明な物の、最も、手前の深度）も、**別に、保存**します。

## 方法 4：深度の、分布を、保存する（Deep / Opacity シャドウ マップ）

**半透明の物が、複数、重なる**（煙、髪、葉）と、**光は、重なった層を、順に、通る**ので、**通過した、光の割合**は、**奥に進むほど、減っていきます**。この、**深度ごとの、光の通過率**を、**シャドウ マップに、保存**する方法です。

| 手法 | 内容 |
| --- | --- |
| **Deep Shadow Maps**（Lokovic と Veach、2000） | 画素ごとに、**深度に対する、透過率の、関数**（区分的な、線形）を、保存。**映画の、レンダリング**で、使われた |
| **Opacity Shadow Maps**（Kim と Neumann、2001） | 深度を、**複数の層**（スライス）に、分け、**各層での、不透明度**を、**テクスチャ**に、保存 |

```text
Opacity Shadow Maps:
   層 1（手前） 層 2    層 3    層 4（奥）
   ┌────┐     ┌────┐  ┌────┐  ┌────┐        各層で、そこまでの、累積した、不透明度を、保存
   │ 0.2│     │ 0.5│  │ 0.8│  │ 0.9│
   └────┘     └────┘  └────┘  └────┘
画素の深度が、層 3 と 4 の間 → 層 3 と 4 の、不透明度を、補間 → 約 0.85 の、影
```

実装は、**複雑**で、**メモリも、重い**（層の数だけ、テクスチャ）。**髪の毛**（[Hair Shadows](../../skin-hair/hair/shadows.md)）、**煙・雲**（[Cloud Shadows](../../atmosphere/clouds/shadows.md)）など、**半透明の層が、密に重なる**物で、使われます。

## 使い分け

| 物 | 方法 |
| --- | --- |
| 無色の、窓ガラス | **影を、落とさない**（方法 1） |
| 薄い、布、半透明の、植物 | **確率的な影**（方法 2） |
| **色付きガラス**、ステンド グラス | **色付きの影**（方法 3）。重要な、演出なら |
| 煙、霧、パーティクル | **確率的な影**、または、**ボリューム ライティング**（[Volumetric Fog](../../atmosphere/volumetric-fog/index.md)） |
| 髪、雲（密に重なる、層） | **Deep / Opacity シャドウ マップ**、または、専用の手法 |

''', before="## よくあるミス")
pg.Refs("shadows/special-cases/translucent-shadows.md", [LOKOVIC, KIM, WYMAN, RTR])

pg.Dedup("shadows/special-cases/character-shadows.md")
pg.Add("shadows/special-cases/character-shadows.md", '''
## キャラクターの、影が、特別な、理由

キャラクターは、ゲームで、**最も、注目される物**です。**足元の、接地**、**顔・体の、自己影**、**動くことによる、影の、ちらつき**が、**すぐに、目に付きます**。

| 課題 | 内容 |
| --- | --- |
| **接地感** | 足元の影が、**地面に、しっかり、接している**ことで、**キャラクターが、地面の上に、立っている**ように、見える。接地が、弱いと、**浮いて**見える |
| **自己影** | 顔、首、服の、折り目の、**細かい自己影**。**解像度が、足りない**と、ぼやけて、**汚く**見える |
| **ちらつき** | キャラクターが、動き、**影の縁が、ちらちら**する（テクセル スナップ、PCF で、軽減） |
| **薄い物** | 髪、マント、細いアクセサリーの、影が、**欠ける**（ピーター パンニング） |

## キャラクターの、専用の、シャドウ マップ

**シーン全体を、覆う、カスケード**の、**1 画素**は、**数センチ〜数十センチ**です。**キャラクターの、顔**（数十センチ）は、**数画素**にしか、**映りません**。**キャラクター専用の、シャドウ マップ**を、作ると、**解像度が、大幅に上がります**。

```cpp
// キャラクターを囲む、小さな範囲（半径 2 m）に、シャドウ マップを割り当てる。
// 解像度 2048 で、1 画素 = 約 2 mm。顔や、服の、細かい影が、出る。
float radius = 2.0f;
Matrix character_view = Matrix::CreateLookAt(character_center - light_dir * radius, character_center, up);
Matrix character_proj = Matrix::CreateOrthographicOffCenter(-radius, radius, -radius, radius, 0.0f, 2.0f * radius);
```

| 方式 | 内容 |
| --- | --- |
| **キャラクター専用の、シャドウ マップ** | キャラクターごとに、**小さな範囲**を、**高解像度**で。**主役**の、数体だけ |
| **カスケードの、最初のカスケード**を、キャラクターに | カメラの、すぐ近く（最も細かい）カスケードが、**キャラクターを、覆う** |
| **接触の影**（コンタクト シャドウ） | 画面空間で、**足元の、短い影**を、補う（[Contact Shadows](../contact-shadows.md)） |

## 接地感を、出す

### ① 足元の、ブロブ影

キャラクターの、**足元に、丸い、暗いテクスチャ**を、貼る（[Blob and Planar Projected Shadows](blob-planar.md)）。**簡単で、安定**。シャドウ マップが、**ぼやけても**、足元は、**しっかり接地**して見えます。

### ② コンタクト シャドウ

**画面空間**で、**キャラクターの、近くだけ**、**短い距離**の、影を、レイマーチで、求めます（[Contact Shadows](../contact-shadows.md)）。**シャドウ マップの、解像度では、出せない、細かい接触の影**が、出ます。

### ③ アンビエント オクルージョン

足元は、**地面と体の、隙間**で、**環境光が、遮られて、暗く**なります。**AO**（[AO](../../ao/index.md)）で、**自然な暗さ**が、出ます。

| 方法 | 効果 |
| --- | --- |
| ブロブ影 | **足元の、丸い暗がり**。**どんな環境でも、安定**して接地して見える |
| コンタクト シャドウ | **細かい、接触の影**（足と地面の、境目） |
| AO | **全体の、暗がり**（体と地面の、隙間、脇の下） |

**3 つを、組み合わせる**と、シャドウ マップが、**荒くても**、**接地感**が、保たれます。

## 影の、色

影は、**真っ黒では、ありません**。**影の中も、環境光**（空の光、周りの、反射光）が、**当たります**。

```hlsl
// 影の中でも、環境光が、残る。直接光だけが、影で、遮られる。
float3 direct = albedo * g_light_color * n_dot_l * shadow;       // 影で、遮られる
float3 ambient = albedo * g_ambient_color;                        // 影に、関係なく、残る
float3 color = direct + ambient;
```

| 問題 | 内容 |
| --- | --- |
| 影の中が、**真っ黒** | 環境光が、無い、または、**弱すぎる**。**空の色（青みがかった）**を、足す |
| 影の色が、**グレー** | 屋外では、**影は、青みがかる**（空の青い光が、当たるため）。**環境光を、青っぽく** |
| **影の中の、キャラクター**が、**浮く** | 周りの、影の色と、**キャラクターの影の中の色**が、**合っていない**。**同じ、環境光**で、照らす |

## キャラクターの、影の、ちらつき

| 原因 | 対策 |
| --- | --- |
| キャラクターの、**位置が、動く**ことで、**シャドウ マップの、画素**が、ずれる | **テクセル スナップ**（[Aliasing and Stabilization](../shadow-map-basics/aliasing-stabilize.md)）。キャラクターの、中心を、画素の、整数倍に、丸める |
| **アニメーション**で、細い、パーツが、動く | **PCF を、広く**（5×5）。**TAA** |
| **薄い**パーツ（髪、マント）の、影が、**欠ける** | **影用の、厚みのある、メッシュ**。**両面を、描く** |

## 影を、**落とす**側と、**受ける**側の、制御

| 設定 | 内容 |
| --- | --- |
| **影を、落とさない** | 小さな、アクセサリー、銃の、細部、**目の、周り**（眼球の、影が、顔に、落ちると、**不自然**） |
| **影を、受けない** | 目、歯（**光り方が、不自然**になるため）、**顔の、特定の部分**（アーティストの、意図） |
| **自己影の、調整** | **顔**では、自己影を、**弱める**（鼻の下、顎の影が、**強すぎる**と、不自然）。**バイアスの、調整** |

アーティストが、**物ごとに、フラグを、設定**できる仕組み（影を落とす / 受ける）を、用意しておくと、**調整が、楽**です。

''', before="## よくあるミス")
pg.Refs("shadows/special-cases/character-shadows.md", [VALIENT, RTR, MCGUIRE, DIMITROV])

pg.Dedup("shadows/special-cases/distant-shadows.md")
pg.Add("shadows/special-cases/distant-shadows.md", '''
## 問題：遠くの影は、どうするか

太陽の影は、**カスケード**（[CSM](../cascaded.md)）で、**カメラの近く**を、覆います。**遠く**（数百メートル〜数キロ）まで、**シャドウ マップを、伸ばす**と、**1 画素が、巨大**になり、**影が、ぼやけます**。一方、**遠景に、影が、全く無い**と、**山、建物、木が、平らに見え**、**距離感が、失われます**。

| 距離 | 影の、必要性 |
| --- | --- |
| 近景（〜50 m） | **細かい影**（キャラクター、物） |
| 中景（50〜300 m） | **建物、木の、影**。形が、分かる程度 |
| 遠景（300 m〜） | **山、大きな建物の、大きな影**。**細部は、不要** |
| 超遠景（数 km） | **地形の、起伏**（山の影が、谷に、落ちる） |

## 方法 1：カスケードを、遠くまで、伸ばす

最も、単純な、方法です。**最後のカスケード**を、**遠くまで**、覆います。

| 項目 | 内容 |
| --- | --- |
| 長所 | **仕組みが、統一**される。特別な、処理が、不要 |
| 短所 | **遠くの、カスケード**は、**1 画素が、数メートル**になり、**ぼやけた影**。**描画範囲が、広く**、**コストが、高い**（遠くの物も、シャドウ パスで、描く） |

**遠くのカスケードは、更新を、間引く**（数フレームに 1 回）ことで、コストを、抑えられます（[CSM](../cascaded.md)）。

## 方法 2：遠景用に、**事前計算**した、影

**動かない、遠景**（山、大きな建物）の影は、**事前に、計算して**、**テクスチャに焼いて**おきます。

| 方式 | 内容 |
| --- | --- |
| **ベイクした、シャドウ マップ** | 遠景の、**静的な物**だけを、**高解像度、広範囲**の、シャドウ マップに、**あらかじめ描いて**保存。**太陽の、位置**ごとに、**複数枚**を、用意し、**時間帯**で、**補間** |
| **ライトマップ** | **地形・建物**の、**影**を、**ライトマップ**に、焼き込む（[Lightmaps](../../gi/lightmaps/index.md)）。**太陽が、動かない**場面に、向く |
| **地形の、シャドウ**（高さマップから） | **地形の、高さマップ**から、**太陽の方向に、レイマーチ**して、**影を、事前に、計算**（[Heightmaps and Meshes](../../terrain/heightmap-mesh/index.md)）。**山の影**が、**安く**作れる |

### 地形の、影を、高さマップから

**高さマップ**を、太陽の方向に、**走査**すると、**各点が、影か**を、**事前に、判定**できます。

```hlsl
// 高さマップを、太陽の方向に、レイマーチして、影を求める（計算シェーダー、事前計算、または、毎フレーム）。
float TerrainShadow(float2 xz, float h, float3 sun_dir_to_light) {
  const int kSteps = 128;
  float2 step_xz = normalize(sun_dir_to_light.xz) * g_step_length;
  float rise = sun_dir_to_light.y / max(length(sun_dir_to_light.xz), 1e-4);   // 水平 1 あたりの、上昇
  float2 p = xz;
  float ray_h = h;
  for (int i = 0; i < kSteps; ++i) {
    p += step_xz;
    ray_h += rise * g_step_length;
    float terrain_h = SampleHeight(p);
    if (terrain_h > ray_h) return 0.0;               // 地形が、レイより高い → 影
  }
  return 1.0;
}
```

**高さマップの、レイマーチ**は、**簡単で、広い範囲**を、**安く**、扱えます。**太陽が、動く**（時間帯）ので、**毎フレーム、または、数フレームに 1 回**、**低解像度**で、再計算する場合もあります。

## 方法 3：距離場（SDF）の影

**メッシュの、距離場**（各点から、最も近い面までの、距離）を、**事前に**作り、**レイマーチ**で、**柔らかい影**を、**安く**、**遠くまで**作ります（[Distance Field Shadows](../sdf-shadows.md)）。**シャドウ マップを、描かずに**、**遠景の、静的な影**を、作れます。

## 方法 4：フェード（遠くで、影を、消す）

**影を、遠くで、突然、消す**と、**境目が、見えます**。**カスケードの、最後**で、**影を、フェード アウト**します。

```hlsl
// 影の有効範囲の、端で、影の強さを、フェードさせる。
float fade = saturate((shadow_distance - view_depth) / fade_range);       // 端で 0、手前で 1
float shadow = lerp(1.0, ShadowFactor(world_pos), fade);                   // フェードの外は、影なし（1.0）
```

| 項目 | 内容 |
| --- | --- |
| フェードの幅 | 最後のカスケードの、10〜20% |
| 遠景の、明るさ | 影が、消えた、遠景は、**全体として、少し、明るく**見える。**遠景の、色**（空気遠近法）で、**ごまかす** |

## 組み合わせ（実際のゲーム）

| 距離 | 方式 |
| --- | --- |
| 〜50 m | カスケード 0〜1（高解像度、毎フレーム） |
| 50〜300 m | カスケード 2〜3（更新を、間引く） |
| 300 m〜2 km | **事前計算**（地形の影、ベイクした、建物の影）、または、**SDF の影** |
| それ以上 | 影なし。**空気遠近法**（[Aerial Perspective and Fog](../../atmosphere/aerial-fog/index.md)）で、**遠景の、雰囲気**を作る |

**近くは、動的に、遠くは、事前計算に、切り替える**のが、**大規模な、ゲームの、定番の、構成**です。**切り替えの、境目**は、**フェード**で、**なめらかに、つなぎます**。

''', before="## よくあるミス")
pg.Refs("shadows/special-cases/distant-shadows.md", [DIMITROV, ENGEL, WRIGHT, RTR])

pg.Dedup("shadows/special-cases/blob-planar.md")
pg.Add("shadows/special-cases/blob-planar.md", '''
## シャドウ マップを、使わない、影

**シャドウ マップ**は、**強力**ですが、**コストが、高く**、**画質の、調整**（バイアス、ちらつき）も、**大変**です。**用途によっては**、**もっと、簡単な方法**で、**十分に、見栄えのする影**が、作れます。

## ブロブ影（丸い、影）

**物の、足元に、丸くて、ぼんやりした、暗い絵**（**ブロブ**）を、**地面に、貼る**だけの、**最も、簡単な影**です。

```text
     ●  キャラクター
     │
   ░░▓▓░░     ← 足元の、丸いブロブ影
 ━━━━━━━━━━━  地面
```

| 長所 | 短所 |
| --- | --- |
| **非常に、軽い**（四角形 1 枚） | **形が、丸い**（物の形に、ならない） |
| **ちらつかない、安定** | **光の方向**に、依存しない（真下に、できる） |
| **接地感**が、しっかり出る | 地面が、**凸凹**だと、**浮いて**見える |
| モバイル、**低スペック**で、使える | 他の物に、**影が、落ちない** |

### 実装

```hlsl
// ブロブ影: 地面に貼った、四角形（デカール）の、ピクセル シェーダー。中心から、距離で、暗くする。
float4 main(float2 uv : TEXCOORD0) : SV_Target {
  float d = distance(uv, float2(0.5, 0.5)) * 2.0;            // 中心 0、縁 1
  float alpha = saturate(1.0 - d);
  alpha *= alpha;                                             // 縁を、なだらかに（2 乗）
  return float4(0, 0, 0, alpha * g_shadow_opacity);          // アルファ ブレンドで、地面に、重ねる
}
```

| 工夫 | 内容 |
| --- | --- |
| **高さで、薄くする** | 物が、地面から、**離れる**（ジャンプ）ほど、**薄く、広がる** |
| **地面に、沿わせる** | 四角形を、**地面の、形に**、**投影**（デカール、[Terrain Decals and Roads](../../terrain/texturing/decals.md)）。**斜面でも、浮かない** |
| **複数**（足ごと） | 足ごとに、ブロブを置くと、**歩く、足元の、接地**が、強調される |

## 平面への、投影影（プラナー シャドウ）

**物の頂点を、平面（地面）に、投影**して、**影の形**を、**そのまま、描く**方法です（Blinn、1988）。**物の、形に、なった、影**が、**平らな地面**に、できます。

```text
 光
  ╲
    ╲     ●物
      ╲   │
 ━━━━━━━▓▓▓▓━━━  地面  ← 物の形を、地面に、投影した、影
```

**光の方向**と、**平面の式**から、**投影行列**を、作ります。

```cpp
using namespace DirectX::SimpleMath;

// 平面 n·p + d = 0 に、光の方向 l（光が進む向き）で、投影する行列（右手系、行ベクトル）。
// 投影行列 = d·I − l·nᵀ  の形（頂点を、同次座標で、平面上へ、移す）。
Matrix PlanarShadowMatrix(const Vector3& plane_normal, float plane_d, const Vector3& light_dir) {
  const float dot = plane_normal.Dot(light_dir);
  Matrix m;
  m._11 = dot - light_dir.x * plane_normal.x * -1.0f;   // 実装の詳細は、行列の転置と符号に注意
  // （ここでは、概念を示す。実際には DirectX::XMMatrixShadow を使うと、簡単）
  return DirectX::XMMatrixShadow(DirectX::XMVectorSet(plane_normal.x, plane_normal.y, plane_normal.z, plane_d),
                                 DirectX::XMVectorSet(-light_dir.x, -light_dir.y, -light_dir.z, 0.0f));
}
```

`DirectX::XMMatrixShadow`（DirectXMath）が、**平面と、光の位置（または方向）**から、**投影行列**を、**作ってくれます**。

| 要素 | 内容 |
| --- | --- |
| 描き方 | **物を、投影行列で、変換して、もう一度描く**。色は、**半透明の、黒** |
| **二重ブレンド**の問題 | 物の、**三角形が、重なる**部分が、**2 回描かれ**、**濃くなる**（ムラ）。**ステンシル**で、**1 画素 1 回**に、制限する |
| **Z ファイティング** | 影の平面が、地面と、**同じ高さ**で、**チラつく**。**少し、持ち上げる**（バイアス）、または、**深度バイアス** |

```cpp
// 二重ブレンドの防止: ステンシルが 0 の画素にだけ描き、描いたら、ステンシルを 1 にする。
D3D11_DEPTH_STENCIL_DESC ds = {};
ds.DepthEnable = TRUE;
ds.DepthWriteMask = D3D11_DEPTH_WRITE_MASK_ZERO;
ds.DepthFunc = D3D11_COMPARISON_LESS_EQUAL;
ds.StencilEnable = TRUE;
ds.StencilReadMask = ds.StencilWriteMask = 0xFF;
ds.FrontFace.StencilFunc = D3D11_COMPARISON_EQUAL;              // ステンシルが 0 のとき、だけ
ds.FrontFace.StencilPassOp = D3D11_STENCIL_OP_INCR_SAT;         // 描いたら、1 に増やす
ds.FrontFace.StencilFailOp = D3D11_STENCIL_OP_KEEP;
ds.FrontFace.StencilDepthFailOp = D3D11_STENCIL_OP_KEEP;
ds.BackFace = ds.FrontFace;
device->CreateDepthStencilState(&ds, &planar_shadow_ds);
// 参照値 0 で設定する: context->OMSetDepthStencilState(planar_shadow_ds.Get(), 0);
```

| 長所 | 短所 |
| --- | --- |
| **物の形**の影が、出る | **平らな地面にしか**、落ちない（階段、壁、他の物に、落ちない） |
| **光の方向**に、従う | 影の縁が、**硬い**（ぼかしが、難しい） |
| シャドウ マップが、不要 | **物を、もう一度描く**（コストが、かかる） |
| 古い、ゲーム機、**モバイル**で、使われる | **自己影、他の物への影**が、無い |

## 使い分け

| 状況 | 方法 |
| --- | --- |
| **モバイル、低スペック** | ブロブ影（最も安い） |
| **キャラクターの、接地感の、補強** | ブロブ影（シャドウ マップと、**併用**） |
| 平らな地面の、**物の形**の影 | プラナー シャドウ |
| **遠くの、小さな物**（群衆、車） | ブロブ影（シャドウ マップは、**省く**） |
| 本格的な、ゲーム（PC、コンソール） | **シャドウ マップ + コンタクト シャドウ**。ブロブ影は、**補助** |

''', before="## よくあるミス")
pg.Refs("shadows/special-cases/blob-planar.md", [BLINN, RTR, "Microsoft Learn, \"XMMatrixShadow function (DirectXMath)\""])

# ================================================================ refs / additions for the larger pages
pg.Refs("shadows/cascaded.md", [ENGEL, DIMITROV, ZHANG, VALIENT, "Lloyd, Govindaraju, Quammen, Molnar, Manocha, \"Logarithmic Perspective Shadow Maps\", ACM Transactions on Graphics, Vol. 27, No. 4, 2008"])
pg.Refs("shadows/pcf.md", [REEVES, FERNANDO, "Microsoft Learn, \"D3D11_SAMPLER_DESC\"（比較フィルター）", RTR])
pg.Refs("shadows/pcss.md", [FERNANDO, REEVES, "Annen, Mertens, Bekaert, Seidel, Sillion, \"Convolution Shadow Maps\", Eurographics Symposium on Rendering 2007", RTR])
pg.Refs("shadows/contact-shadows.md", [MCGUIRE, RTR])
pg.Refs("shadows/sdf-shadows.md", [WRIGHT, QUILEZ, HART])
pg.Refs("shadows/ray-traced.md", [DXR, HEITZ, SCHIED, "Whitted, \"An Improved Illumination Model for Shaded Display\", Communications of the ACM, Vol. 23, No. 6, 1980（レイトレーシングの原典）"])
pg.Refs("shadows/shadow-volumes.md", [CROW, EVERITT, "Heidmann, \"Real Shadows Real Time\", Iris Universe, No. 18, 1991（ステンシルを使った、シャドウ ボリューム）"])
pg.Refs("shadows/virtual-shadow-maps.md", [FERNANDO01, LEFOHN, GIEGL, "Epic Games, \"Virtual Shadow Maps\", Unreal Engine 5 ドキュメント"])
pg.Refs("shadows/comparison.md", [REEVES, DIMITROV, "Donnelly, Lauritzen, \"Variance Shadow Maps\", Symposium on Interactive 3D Graphics and Games 2006", WRIGHT, RTR])
pg.Refs("shadows/index.md", [RTR, REEVES, DIMITROV, "Williams, \"Casting Curved Shadows on Curved Surfaces\", SIGGRAPH 1978"])
print("ok")
