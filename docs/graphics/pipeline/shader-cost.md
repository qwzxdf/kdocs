---
title: Shader Cost
tags:
  - 最適化
  - 3Dゲーム
---

# Shader Cost

ピクセル数や頂点数といった量を減らしても、1 回あたりのシェーダーが重ければ、GPU は遅いままです。ところが「どう書けば軽くなるか」は思い込みで語られがちです。`pow(x, 2.0)` は重いから `x * x` に書き換えるループの中の計算は外へ出すといった定番の助言は、今のコンパイラが自動でやってくれることも多く、書き換えても何も変わりません。逆に、効く書き換えもあります。このページでは HLSL を `fxc` でコンパイルして命令数を数えどの書き方が本当に効くかを確かめます。そのうえで、分岐のダイバージェンス、占有率、待ち時間の隠し方をモデルの計算で整理します。

!!! tip "ポイント"
    - 定数の指数の `pow` は `fxc` が乗算に直す。`pow(x, 2.0)` と `x * x` の命令数は同じ（1 命令）で、`pow(x, 5.0)` と `x*x*x*x*x` も同じ（3 命令）だった。指数が変数の `pow` だけが `log` と `exp` を使う重い形になる。
    - 粗さ・金属・AO を 1 枚のテクスチャに詰めると、読み込みが 3 回から 1 回に減る。命令数も 7 から 1 になった。メモリ読み込みを減らす工夫は演算の書き換えより効きやすい。
    - ウェーブ内でランダムな条件の分岐は、確率 1 % でも 32 スレッドのウェーブの約 27 % が両方の道を通る。画面上の円の内側だけが真、のような空間的にそろった条件では両方を通るウェーブは 1 % 前後になる。
    - ループ内の定数の計算を外へ出す書き換えは、ループを展開すると `fxc` が自動で行う。展開前後で命令数がほとんど変わらなかった（94 と 92）。測らずに書き換えない。
    - 占有率はレジスタ数で決まる。待ちを隠すのに必要なウェーブ数は `待ち時間 ÷ 1 回の演算量 + 1`。

!!! info "このページを読む前に"
    - [Pipeline and Optimization](index.md)（このセクション全体の地図と読む順番）
    - [GPU Pipeline Overview](../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）
    - [Bottlenecks](bottlenecks.md)（CPU と GPU のどちらが遅いかの切り分け）

## 読んだ資料とこのページの範囲 {#sources}

このページは特定の論文や GPU ベンダーの資料を読んで書いたものではありません。数字は 2 種類で次の通りです。

- **`fxc` の命令数。** Windows SDK の `fxc`（`/O3`）が出す DXBC のアセンブリの命令を数えました。DXBC はドライバーが GPU の機械語にする前の中間表現です。実機の命令数や時間とは一致しません。同じ処理の書き方を比べる目安です。数え方は `dcl_` 以外の命令の行（`ret` を除く）です。
- **C++ のモデル計算。** 分岐、占有率、待ちの隠し方を簡単なモデルで計算しました。レジスタ ファイルの大きさや待ち時間は、実機の値ではなく仮定です。数字の大きさではなく式の形を見てください。

実機の GPU（ウェーブの大きさレジスタ ファイル、待ち時間）の具体的な数字はベンダーの資料を読んでいないので、書きません。実際のシェーダーの時間は PIX や各ベンダーのプロファイラーで測ってください。旧版にあった「NVIDIA は 32、AMD は 32 または 64」のようなウェーブの大きさは、出典を確かめていないのでこのページでは「GPU によって 32 や 64 など」と曖昧にしておきます。

## シェーダーの時間は何で決まるか {#what}

シェーダーの時間はおおまかに 4 つで決まります。

1. **演算（ALU）。** 加減乗除、内積、`mad` は軽く `sqrt`、`rsqrt`、`sin`、`log`、`exp`、`rcp`（除算の元）は特殊な演算で、重くなります。このページの「特殊」はこれらです。
2. **メモリ読み込み。** テクスチャとバッファの読み込みです。待ち時間が長くキャッシュに乗るかどうかが効きます。
3. **分岐。** 同じウェーブのスレッドが違う道に進むと両方の道を順に実行します。
4. **レジスタ。** 1 スレッドが使うレジスタが多いと同時に動かせるウェーブが減り待ちを隠せなくなります。

演算、メモリ、分岐、レジスタのどれが支配しているかで、効く対策が変わります。演算を減らしてもメモリ待ちが支配していれば、速くなりません。

## 演算 {#alu}

演算の書き方を命令数で比べました。小さな関数に分けて `fxc` の `/O3` でコンパイルし、命令数と特殊な演算の数を数えます。入力は定数バッファから読んで、定数畳み込みを防いでいます。

```hlsl
```hlsl
// ---------- A. 演算 ----------
float4 MulSq(float2 uv : TEXCOORD0) : SV_Target { return g_a.x * g_a.x; }                          // x * x
float4 PowSq(float2 uv : TEXCOORD0) : SV_Target { return pow(g_a.x, 2.0); }                         // pow(x, 2)
float4 Mul5(float2 uv : TEXCOORD0) : SV_Target { float x2 = g_a.x * g_a.x; return x2 * x2 * g_a.x; }   // x^5 を乗算 3 回で
float4 PowConst5(float2 uv : TEXCOORD0) : SV_Target { return pow(g_a.x, 5.0); }                     // pow(x, 5)
float4 PowVar(float2 uv : TEXCOORD0) : SV_Target { return pow(g_a.x, g_b.x); }                      // pow(x, y)
float4 Sqrt(float2 uv : TEXCOORD0) : SV_Target { return sqrt(g_a.x); }
float4 Rsqrt(float2 uv : TEXCOORD0) : SV_Target { return rsqrt(g_a.x); }
float4 Sin(float2 uv : TEXCOORD0) : SV_Target { return sin(g_a.x); }
float4 DivVar(float2 uv : TEXCOORD0) : SV_Target { return g_a.x / g_b.x; }                          // 変数の除算
float4 DivConst(float2 uv : TEXCOORD0) : SV_Target { return g_a.x / 3.0; }                          // 定数の除算（乗算に直る）
float4 Normalize(float2 uv : TEXCOORD0) : SV_Target { return float4(normalize(g_a.xyz), 0); }
float4 NormalizeManual(float2 uv : TEXCOORD0) : SV_Target { return float4(g_a.xyz * rsqrt(dot(g_a.xyz, g_a.xyz)), 0); }
float4 Mad(float2 uv : TEXCOORD0) : SV_Target { return g_a * g_b + g_c; }                           // 乗算 + 加算
float4 MatVec(float2 uv : TEXCOORD0) : SV_Target { return mul(g_a, g_m); }                          // 4x4 行列 × ベクトル
```
```

```text title="fxc /O3 の命令数（ps_5_0）"
MulSq              instructions=1   texture=0  special=0  flow=0
PowSq              instructions=1   texture=0  special=0  flow=0
Mul5               instructions=3   texture=0  special=0  flow=0
PowConst5          instructions=3   texture=0  special=0  flow=0
PowVar             instructions=3   texture=0  special=2  flow=0
Sqrt               instructions=1   texture=0  special=1  flow=0
Rsqrt              instructions=1   texture=0  special=1  flow=0
Sin                instructions=1   texture=0  special=1  flow=0
DivVar             instructions=1   texture=0  special=1  flow=0
DivConst           instructions=1   texture=0  special=0  flow=0
Normalize          instructions=4   texture=0  special=1  flow=0
NormalizeManual    instructions=4   texture=0  special=1  flow=0
Mad                instructions=1   texture=0  special=0  flow=0
MatVec             instructions=4   texture=0  special=0  flow=0
```

読みどころは 3 つあります。

**定数の指数の `pow` は書き換えが要りません。** `pow(g_a.x, 2.0)` は 1 命令で `g_a.x * g_a.x` と同じです。`pow(g_a.x, 5.0)` は 3 命令で手で `x2 = x*x; x2*x2*x` と書いたものと同じです。`fxc` が指数が定数の `pow` を乗算の列に直しているからです。旧版の「`pow(x, 2.0)` をそのまま書く → `x * x` にします」は、`fxc` では不要でした。ただし、これは `fxc`（DXBC）の話です。ドライバーのコンパイラの動きはここでは見えません。

**指数が変数の `pow` は重い形です。** `pow(g_a.x, g_b.x)` は 3 命令でうち 2 つが特殊（`log` と `exp`）です。`pow(x, y) = exp2(y × log2(x))` という式に展開されます。べき乗の指数が実行時に決まる鏡面ハイライトなどでは、この 2 つの特殊命令が毎回かかります。

**除算は定数なら乗算になります。** `g_a.x / 3.0` は特殊 0 で 1 命令です。`g_a.x / g_b.x` は特殊 1（`rcp` を使う除算）です。また、`normalize` は 4 命令（内積、`rsqrt`、乗算）で手で `v * rsqrt(dot(v, v))` と書いても同じ 4 命令でした。

## メモリ読み込み {#memory}

読み込みを数える前にメモリを待つ間の動きを整理します。GPU はあるウェーブがメモリを待つ間に別のウェーブを実行して、待ちを隠します。ところが、読み込みの結果で次の座標が決まる「依存した読み込み」が連なると、1 つのウェーブの中で待ちが直列になります。

```hlsl
```hlsl
// ---------- C. テクスチャ読み込み ----------
float4 Tex4Independent(float2 uv : TEXCOORD0) : SV_Target {                                         // 座標が決まっていて、4 回が互いに独立
  return g_tex0.Sample(g_samp, uv) + g_tex1.Sample(g_samp, uv) + g_tex2.Sample(g_samp, uv) + g_tex3.Sample(g_samp, uv);
}
float4 Tex4Dependent(float2 uv : TEXCOORD0) : SV_Target {                                           // 前の結果で次の座標を決める（直列）
  float2 p = uv;
  p += g_tex0.Sample(g_samp, p).xy * 0.01;
  p += g_tex1.Sample(g_samp, p).xy * 0.01;
  p += g_tex2.Sample(g_samp, p).xy * 0.01;
  return g_tex3.Sample(g_samp, p);
}
float4 TexSeparate(float2 uv : TEXCOORD0) : SV_Target {                                             // 粗さ・金属・AO を 3 枚から
  return float4(g_tex0.Sample(g_samp, uv).r, g_tex1.Sample(g_samp, uv).r, g_tex2.Sample(g_samp, uv).r, 0);
}
float4 TexPacked(float2 uv : TEXCOORD0) : SV_Target {                                               // 1 枚に詰めたもの
  return g_packed.Sample(g_samp, uv);
}
```
```

```text title="fxc /O3 の命令数（テクスチャ読み込み）"
Tex4Independent    instructions=7   texture=4  special=0  flow=0
Tex4Dependent      instructions=7   texture=4  special=0  flow=0
TexSeparate        instructions=7   texture=3  special=0  flow=0
TexPacked          instructions=1   texture=1  special=0  flow=0
```

`Tex4Independent` と `Tex4Dependent` はどちらも 7 命令で、テクスチャ読み込みが 4 回です。静的な命令数では依存の有無が見えません。依存した読み込みの待ちは命令数ではなく、遅延として効きます。だから「命令数が同じだから同じ速さ」とは言えません。

一方、`TexSeparate`（粗さ・金属・AO を 3 枚から読む）は、読み込み 3 回で 7 命令、`TexPacked`（1 枚に詰めたもの）は読み込み 1 回で 1 命令です。**詰めるだけで読み込みが 3 分の 1 になります。** 同じ UV で読むならチャンネルに詰めたほうが、キャッシュの面でも有利です。

## ループ {#loop}

```hlsl
```hlsl
// ---------- D. ループ ----------
float4 LoopRuntime(float2 uv : TEXCOORD0) : SV_Target {
  float4 sum = 0;
  [loop] for (int i = 0; i < 8; ++i) sum += g_tex0.Sample(g_samp, uv + float2(i, 0) * 0.01);       // ループのまま
  return sum;
}
float4 LoopUnrolled(float2 uv : TEXCOORD0) : SV_Target {
  float4 sum = 0;
  [unroll] for (int i = 0; i < 8; ++i) sum += g_tex0.Sample(g_samp, uv + float2(i, 0) * 0.01);     // 展開
  return sum;
}
```
```

`[loop]` のままだとループ本体は 1 回分の読み込み（テクスチャ 1、命令 13）で分岐の命令が 2 つ付きます。`[unroll]` すると 8 回分が展開されて、テクスチャ 8、命令 19 になり分岐はなくなります。展開すると命令は増えますがループの管理（カウンターの更新と比較）が消え読み込みを並べて発行できます。回数が小さくて固定なら展開が有利なことが多く、回数が大きいまたは実行時に決まるならループのままにします。

## 分岐 {#branch}

### `[branch]` と `[flatten]` {#branch-flatten}

```hlsl
```hlsl
// ---------- B. 分岐 ----------
float Heavy(float x) { return pow(sin(x) * 0.5 + 0.5, 3.0) + sqrt(abs(cos(x))); }                   // 重い処理の例
float4 BranchHeavy(float2 uv : TEXCOORD0) : SV_Target { [branch] if (g_flag != 0) return Heavy(g_a.x); else return g_a.x; }
float4 FlattenHeavy(float2 uv : TEXCOORD0) : SV_Target { [flatten] if (g_flag != 0) return Heavy(g_a.x); else return g_a.x; }
```
```

重い処理（`Heavy`）を `if` で囲んだ形を `[branch]` と `[flatten]` で比べると、`[branch]` は 9 命令（分岐 3）、`[flatten]` は 8 命令（分岐 0）でした。`[flatten]` は両方の道を計算して結果を選びます。重い道が重くないなら `[flatten]` で足ります。重い道を飛ばしたいなら `[branch]` にします。ただし、飛ばせるのはそのウェーブの全スレッドが同じ側に進むときだけです。

### ウェーブの中で条件がばらつくとき {#divergence}

GPU は複数のスレッドをウェーブにまとめ同じ命令を一緒に実行します。ウェーブ内のスレッドが違う道に進むと両方の道を順に実行し、使わない側をマスクします。

条件がスレッドごとに独立なランダムだとして、ウェーブが 2 つの道を両方通る確率を計算します。真の確率を `p`、ウェーブのスレッド数を `W` とすると、真の道を通る確率は `1 − (1−p)^W`、偽の道を通る確率は `1 − p^W` です。両方を通る確率は `1 − p^W − (1−p)^W` になります。

<svg class="fig flow" viewBox="0 0 640 260" role="img" aria-label="ウェーブが両方の道を通る確率(ランダムな条件)"><defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">ウェーブが両方の道を通る確率(ランダムな条件)</text><line x1="60" y1="210" x2="600" y2="210" stroke="#94a3b8"/><line x1="60" y1="40" x2="60" y2="210" stroke="#94a3b8"/><text x="54" y="214.0" text-anchor="end" font-size="10" fill="currentColor">0</text><text x="54" y="129.0" text-anchor="end" font-size="10" fill="currentColor">0.5</text><text x="54" y="44.0" text-anchor="end" font-size="10" fill="currentColor">1</text><text x="54.54545454545455" y="226" text-anchor="middle" font-size="10" fill="currentColor">0</text><text x="163.63636363636363" y="226" text-anchor="middle" font-size="10" fill="currentColor">10</text><text x="272.72727272727275" y="226" text-anchor="middle" font-size="10" fill="currentColor">20</text><text x="381.8181818181818" y="226" text-anchor="middle" font-size="10" fill="currentColor">30</text><text x="490.90909090909093" y="226" text-anchor="middle" font-size="10" fill="currentColor">40</text><text x="600.0" y="226" text-anchor="middle" font-size="10" fill="currentColor">50</text><text x="330.0" y="244" text-anchor="middle" font-size="11" fill="currentColor">真になるスレッドの割合 p (%)</text><polyline points="60.0,184.8 65.5,163.2 70.9,144.8 76.4,129.1 81.8,115.6 87.3,104.1 92.7,94.4 98.2,86.0 103.6,79.0 109.1,72.9 114.5,67.8 120.0,63.5 125.5,59.8 130.9,56.7 136.4,54.0 141.8,51.8 147.3,49.9 152.7,48.3 158.2,47.0 163.6,45.8 169.1,44.9 174.5,44.1 180.0,43.4 185.5,42.8 190.9,42.4 196.4,42.0 201.8,41.6 207.3,41.4 212.7,41.1 218.2,40.9 223.6,40.8 229.1,40.6 234.5,40.5 240.0,40.4 245.5,40.4 250.9,40.3 256.4,40.2 261.8,40.2 267.3,40.2 272.7,40.1 278.2,40.1 283.6,40.1 289.1,40.1 294.5,40.1 300.0,40.0 305.5,40.0 310.9,40.0 316.4,40.0 321.8,40.0 327.3,40.0 332.7,40.0 338.2,40.0 343.6,40.0 349.1,40.0 354.5,40.0 360.0,40.0 365.5,40.0 370.9,40.0 376.4,40.0 381.8,40.0 387.3,40.0 392.7,40.0 398.2,40.0 403.6,40.0 409.1,40.0 414.5,40.0 420.0,40.0 425.5,40.0 430.9,40.0 436.4,40.0 441.8,40.0 447.3,40.0 452.7,40.0 458.2,40.0 463.6,40.0 469.1,40.0 474.5,40.0 480.0,40.0 485.5,40.0 490.9,40.0 496.4,40.0 501.8,40.0 507.3,40.0 512.7,40.0 518.2,40.0 523.6,40.0 529.1,40.0 534.5,40.0 540.0,40.0 545.5,40.0 550.9,40.0 556.4,40.0 561.8,40.0 567.3,40.0 572.7,40.0 578.2,40.0 583.6,40.0 589.1,40.0 594.5,40.0 600.0,40.0" fill="none" stroke="#334155" stroke-width="2.4"/><line x1="470" y1="48" x2="496" y2="48" stroke="#334155" stroke-width="2.4"/><text x="502" y="52" text-anchor="start" font-size="11" fill="currentColor">W = 32</text><polyline points="60.0,163.3 65.5,129.4 70.9,104.6 76.4,86.7 81.8,73.6 87.3,64.2 92.7,57.4 98.2,52.5 103.6,48.9 109.1,46.4 114.5,44.6 120.0,43.2 125.5,42.3 130.9,41.6 136.4,41.2 141.8,40.8 147.3,40.6 152.7,40.4 158.2,40.3 163.6,40.2 169.1,40.1 174.5,40.1 180.0,40.1 185.5,40.0 190.9,40.0 196.4,40.0 201.8,40.0 207.3,40.0 212.7,40.0 218.2,40.0 223.6,40.0 229.1,40.0 234.5,40.0 240.0,40.0 245.5,40.0 250.9,40.0 256.4,40.0 261.8,40.0 267.3,40.0 272.7,40.0 278.2,40.0 283.6,40.0 289.1,40.0 294.5,40.0 300.0,40.0 305.5,40.0 310.9,40.0 316.4,40.0 321.8,40.0 327.3,40.0 332.7,40.0 338.2,40.0 343.6,40.0 349.1,40.0 354.5,40.0 360.0,40.0 365.5,40.0 370.9,40.0 376.4,40.0 381.8,40.0 387.3,40.0 392.7,40.0 398.2,40.0 403.6,40.0 409.1,40.0 414.5,40.0 420.0,40.0 425.5,40.0 430.9,40.0 436.4,40.0 441.8,40.0 447.3,40.0 452.7,40.0 458.2,40.0 463.6,40.0 469.1,40.0 474.5,40.0 480.0,40.0 485.5,40.0 490.9,40.0 496.4,40.0 501.8,40.0 507.3,40.0 512.7,40.0 518.2,40.0 523.6,40.0 529.1,40.0 534.5,40.0 540.0,40.0 545.5,40.0 550.9,40.0 556.4,40.0 561.8,40.0 567.3,40.0 572.7,40.0 578.2,40.0 583.6,40.0 589.1,40.0 594.5,40.0 600.0,40.0" fill="none" stroke="#4c8bf5" stroke-width="2.4"/><line x1="470" y1="64" x2="496" y2="64" stroke="#4c8bf5" stroke-width="2.4"/><text x="502" y="68" text-anchor="start" font-size="11" fill="currentColor">W = 64</text></svg>

C++ の結果を読みます。`W = 32` で `p = 0.1 %` のとき両方を通る確率は 3.2 % です。1 % で 27.5 %、5 % で 80.6 % です。真の道のコストを 100、偽の道を 10 として期待コストを出すと `p = 1 %` で、理想（スレッドごとに別々に実行できた場合）の約 3.4 倍、`p = 5 %` で約 6.3 倍になります。`W = 64` ではさらに悪くなります（`p = 1 %` で 5.3 倍）。**まれにしか真にならない重い処理でもランダムに散らばると、ほぼ毎回、全員が重い道を待つことになります。**

### 空間的にそろっているとき {#coherent}

条件が画面上でまとまっていれば、話は変わります。1920×1080 の画面の中央に半径 R の円を置き円の内側だけを真とします。8×4（32 スレッド）と 8×8（64 スレッド）のタイルをウェーブとして、真と偽が混ざるタイルの割合を数えました。R = 50 で 0.09 %（8×4）、R = 300 で 0.57 %、R = 500 で 1.01 % です。**混ざるのは円の縁のタイルだけです。** 縁の長さは円周に比例するので、全タイル数に対する割合は小さくなります。

ここから分岐を安くする方法が見えます。条件が近くの画素で似た値になるようにします。たとえば、ライトの影響範囲、マテリアルの種類、画面上の領域（タイル）などで分けた条件は、空間的にそろいやすいです。画素ごとの乱数や細かいノイズで決まる条件は、そろいません。

## 占有率 {#occupancy}

GPU はあるウェーブがメモリを待つ間に別のウェーブを実行して、待ち時間を隠します。同時に動かせるウェーブの数が、占有率です。レジスタ ファイルは有限なので、1 スレッドが使うレジスタが多いほど載るウェーブが減ります。

C++ でレジスタ ファイルを「1 レーンあたり合計 256 レジスタ、最大 10 ウェーブ」と**仮定**して、数えました。1 スレッド 24 レジスタなら 10 ウェーブ（100 %）、32 で 8 ウェーブ、48 で 5 ウェーブ、64 で 4 ウェーブ、96 で 2 ウェーブです。この数字は仮定で実機の値ではありませんが、**レジスタを増やすとウェーブ数が階段状に落ちる**という形は共通です。

待ちを隠すのに必要なウェーブ数は待ち時間を `L`、メモリ読み込みの間にウェーブが計算する量を `A`（サイクル）として、`ceil(L / A) + 1` です。`L = 400`（仮定）で `A = 20` なら 21 ウェーブ、`A = 100` なら 5 ウェーブです。**1 回の読み込みの間に演算が多いシェーダーは、少ないウェーブでも待ちを隠せます。** 演算が少ないシェーダーは多くのウェーブが要るので、レジスタを減らす効果が大きくなります。

<svg class="fig flow" viewBox="0 0 640 230" role="img" aria-label="1 スレッドのレジスタ数とウェーブ数(仮定: 合計 256、最大 10)"><defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">1 スレッドのレジスタ数とウェーブ数(仮定: 合計 256、最大 10)</text><line x1="60" y1="190" x2="600" y2="190" stroke="#94a3b8"/><line x1="60" y1="40" x2="60" y2="190" stroke="#94a3b8"/><text x="54" y="194.0" text-anchor="end" font-size="10" fill="currentColor">0</text><text x="54" y="119.0" text-anchor="end" font-size="10" fill="currentColor">5</text><text x="54" y="44.0" text-anchor="end" font-size="10" fill="currentColor">10</text><rect x="75.6" y="40.0" width="43.0" height="150.0" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="97.07142857142857" y="36.0" text-anchor="middle" font-size="10" fill="currentColor">10</text><text x="98.57142857142857" y="206" text-anchor="middle" font-size="11" fill="currentColor">24</text><rect x="152.7" y="70.0" width="43.0" height="120.0" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="174.21428571428572" y="66.0" text-anchor="middle" font-size="10" fill="currentColor">8</text><text x="175.71428571428572" y="206" text-anchor="middle" font-size="11" fill="currentColor">32</text><rect x="229.9" y="115.0" width="43.0" height="75.0" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="251.35714285714283" y="111.0" text-anchor="middle" font-size="10" fill="currentColor">5</text><text x="252.85714285714283" y="206" text-anchor="middle" font-size="11" fill="currentColor">48</text><rect x="307.0" y="130.0" width="43.0" height="60.0" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="328.5" y="126.0" text-anchor="middle" font-size="10" fill="currentColor">4</text><text x="330.0" y="206" text-anchor="middle" font-size="11" fill="currentColor">64</text><rect x="384.1" y="160.0" width="43.0" height="30.0" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="405.6428571428571" y="156.0" text-anchor="middle" font-size="10" fill="currentColor">2</text><text x="407.1428571428571" y="206" text-anchor="middle" font-size="11" fill="currentColor">96</text><rect x="461.3" y="160.0" width="43.0" height="30.0" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="482.7857142857142" y="156.0" text-anchor="middle" font-size="10" fill="currentColor">2</text><text x="484.2857142857142" y="206" text-anchor="middle" font-size="11" fill="currentColor">128</text><rect x="538.4" y="175.0" width="43.0" height="15.0" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="559.9285714285714" y="171.0" text-anchor="middle" font-size="10" fill="currentColor">1</text><text x="561.4285714285714" y="206" text-anchor="middle" font-size="11" fill="currentColor">200</text></svg>

## 組み合わせの実例 {#example}

ライトを 4 つ回す簡単な鏡面つきのシェーダーを 2 通りに書いて比べました。

```hlsl
```hlsl
// ---------- E. 組み合わせ: 同じ見た目の 2 通りの書き方 ----------
cbuffer LightCB : register(b1) {
  float4 g_light_pos[4];     // xyz = 位置、w = 半径の逆数
  float4 g_light_color[4];
  float3 g_camera_pos;
  float g_pad;
};

struct ShadeIn { float4 pos : SV_Position; float3 world : TEXCOORD0; float2 uv : TEXCOORD1; };

// 書き換え前: 3 枚のテクスチャ、ライトごとに normalize、ループの中で毎回 pow(2, 定数 × 粗さ)
float4 ShadeBefore(ShadeIn i) : SV_Target {
  float rough = g_tex0.Sample(g_samp, i.uv).r;
  float metal = g_tex1.Sample(g_samp, i.uv).r;
  float ao = g_tex2.Sample(g_samp, i.uv).r;
  float3 n = normalize(g_tex3.Sample(g_samp, i.uv).xyz * 2.0 - 1.0);
  float3 sum = 0;
  for (int k = 0; k < 4; ++k) {
    float3 v = normalize(g_camera_pos - i.world);                  // ライトに依存しないのにループの中
    float3 l = normalize(g_light_pos[k].xyz - i.world);
    float3 h = normalize(l + v);
    float shininess = pow(2.0, (1.0 - rough) * 10.0);              // ライトに依存しないのにループの中
    float spec = pow(saturate(dot(n, h)), shininess) * (1.0 + metal);
    float atten = saturate(1.0 - length(g_light_pos[k].xyz - i.world) * g_light_pos[k].w);
    sum += g_light_color[k].rgb * (saturate(dot(n, l)) + spec) * atten * atten;
  }
  return float4(sum * ao, 1.0);
}

// 書き換え前（ループ展開つき。命令数を後と同じ条件で比べるため）: 3 枚のテクスチャ、ライトごとに normalize、ループの中で毎回 pow(2, 定数 × 粗さ)
float4 ShadeBeforeUnrolled(ShadeIn i) : SV_Target {
  float rough = g_tex0.Sample(g_samp, i.uv).r;
  float metal = g_tex1.Sample(g_samp, i.uv).r;
  float ao = g_tex2.Sample(g_samp, i.uv).r;
  float3 n = normalize(g_tex3.Sample(g_samp, i.uv).xyz * 2.0 - 1.0);
  float3 sum = 0;
  [unroll] for (int k = 0; k < 4; ++k) {
    float3 v = normalize(g_camera_pos - i.world);                  // ライトに依存しないのにループの中
    float3 l = normalize(g_light_pos[k].xyz - i.world);
    float3 h = normalize(l + v);
    float shininess = pow(2.0, (1.0 - rough) * 10.0);              // ライトに依存しないのにループの中
    float spec = pow(saturate(dot(n, h)), shininess) * (1.0 + metal);
    float atten = saturate(1.0 - length(g_light_pos[k].xyz - i.world) * g_light_pos[k].w);
    sum += g_light_color[k].rgb * (saturate(dot(n, l)) + spec) * atten * atten;
  }
  return float4(sum * ao, 1.0);
}

// 書き換え後: 粗さ・金属・AO を 1 枚に詰めライトに依存しない値をループの外へ、normalize を rsqrt に
float4 ShadeAfter(ShadeIn i) : SV_Target {
  float3 pack = g_packed.Sample(g_samp, i.uv).rgb;                 // R = 粗さ、G = 金属、B = AO
  float3 n = normalize(g_tex3.Sample(g_samp, i.uv).xyz * 2.0 - 1.0);
  float3 to_cam = g_camera_pos - i.world;
  float3 v = to_cam * rsqrt(dot(to_cam, to_cam));                  // ループの外へ
  float shininess = exp2((1.0 - pack.r) * 10.0);                   // pow(2, x) = exp2(x)。ループの外へ
  float spec_scale = 1.0 + pack.g;
  float3 sum = 0;
  [unroll] for (int k = 0; k < 4; ++k) {
    float3 to_l = g_light_pos[k].xyz - i.world;
    float d2 = dot(to_l, to_l);
    float inv_d = rsqrt(d2);
    float3 l = to_l * inv_d;                                       // 長さを求めた rsqrt を再利用
    float3 h = normalize(l + v);
    float spec = pow(saturate(dot(n, h)), shininess) * spec_scale;
    float atten = saturate(1.0 - d2 * inv_d * g_light_pos[k].w);   // length(to_l) = d2 * rsqrt(d2)
    sum += g_light_color[k].rgb * (saturate(dot(n, l)) + spec) * atten * atten;
  }
  return float4(sum * pack.b, 1.0);
}
```
```

書き換え前は粗さ・金属・AO を 3 枚のテクスチャから読みライトごとに視線方向を `normalize` し、`pow(2.0, …)` を毎回計算しています。書き換え後は 3 つを 1 枚に詰め視線方向と `exp2` を外へ出し、`normalize` を `rsqrt` に直しています。

命令数は次の通りです。ループのままの書き換え前は 43 命令（テクスチャ 4、特殊 8、分岐 2）、展開した書き換え前は 94 命令（特殊 23）、書き換え後は 92 命令（特殊 19、テクスチャ 2）です。

**展開した書き換え前と書き換え後を比べると、命令数は 94 から 92 で、ほとんど変わりません。** 視線方向の `normalize` や `pow(2, …)` はループを展開すれば、`fxc` が共通部分式として外に出していたからです。手で外へ出した効果はほぼありません。

効いたのは**テクスチャ読み込みが 4 回から 2 回に減った**ことと、特殊な演算が 23 から 19 に減ったことです。命令数に見えにくいメモリ待ちの減り方が大きいのが、この書き換えの効果です。ループを展開しない場合はループの外へ出す書き換えが意味を持つ可能性があります。ただし、本当にそうかは実機で測らないと分かりません。

## 頂点へ移す・事前計算 {#move}

ピクセルは頂点よりずっと多いので、画素ごとに同じ値になる計算は頂点か CPU に移せます。ライト方向のようにゆっくり変わる値は、頂点で計算して補間しても足ります。ただし、補間では精度が足りないもの（鏡面ハイライトなど）は、画素で計算します。LUT やベイクで事前計算できるものは、テーブルを引くほうが速いことがあります。ただし、そのテーブルの読み込みもメモリ待ちになるので、演算が十分に重いときだけ効きます。

## シェーダーのバリアント {#variants}

マクロで機能のオン・オフを切り替えると、組み合わせの数だけシェーダーが増えます。3 つの機能なら 2³ = 8 通り 10 個なら 1,024 通りです。本当に使う組み合わせだけをビルドします。全画素で同じ値の分岐（定数バッファのフラグ）は、ウェーブの中で割れないのでバリアントを減らす手段にもなります。

## 測り方 {#measure}

このページの命令数は DXBC の静的な数字です。実機の時間は PIX や各ベンダーのプロファイラーで測ります。シェーダーを一時的に空にして、速くなるかを見る切り分けも有効です（[Bottlenecks](bottlenecks.md)）。

## 数字を出した C++ {#experiment}

```cpp
```cpp
// シェーダーのコストの考え方を数える。GPU の実機の数字ではなく、モデルの計算。
//   [1] 分岐: スレッドごとにランダムな条件のときウェーブ（W スレッド）が両方の道を通る確率と、期待コスト
//   [2] 分岐: 画面上の円の内側だけが真のとき両方の道を通るウェーブの割合（空間的にそろっている場合）
//   [3] 占有率: レジスタ数とウェーブ数（レジスタ ファイルの大きさは仮定）
//   [4] 待ちを隠すのに必要なウェーブ数（待ち時間は仮定）
#include <algorithm>
#include <cmath>
#include <cstdio>

int main() {
  // ---- [1] 条件が互いに独立（ランダム）なとき ----
  // ウェーブが「真の道」を実行するのは、1 スレッドでも真があるとき（確率 1 - (1-p)^W）。
  // 「偽の道」は 1 スレッドでも偽があるとき（確率 1 - p^W）。
  std::printf("[1] random per-thread condition, true path cost A=100, false path cost B=10 (arbitrary units)\n");
  std::printf("  W   p        P(both paths)  wave cost   ideal cost   ratio\n");
  for (int W : {32, 64}) {
    for (double p : {0.001, 0.01, 0.05, 0.5}) {
      double p_true_path = 1 - std::pow(1 - p, W);           // 真の道を実行する確率
      double p_false_path = 1 - std::pow(p, W);              // 偽の道を実行する確率
      double both = p_true_path + p_false_path - 1;          // 両方を通る確率（= 1 - p^W - (1-p)^W）
      double wave_cost = 100 * p_true_path + 10 * p_false_path;
      double ideal = 100 * p + 10 * (1 - p);                 // スレッドごとに別々に実行できた場合の平均
      std::printf("%3d  %-7.3f  %-13.3f  %-10.1f  %-10.1f   %.2f\n", W, p, both, wave_cost, ideal, wave_cost / ideal);
    }
  }

  // ---- [2] 空間的にそろっている場合: 1920x1080 の画面で、半径 R の円の内側だけが真 ----
  std::printf("\n[2] spatially coherent condition: disc of radius R at the screen center, waves are 8x4 (32) or 8x8 (64) pixel tiles\n");
  const int Wd = 1920, Hd = 1080;
  const double cx = Wd / 2.0, cy = Hd / 2.0;
  for (double R : {50.0, 150.0, 300.0, 500.0}) {
    for (int tw : {8}) {
      for (int th : {4, 8}) {
        long tiles = 0, mixed = 0;
        for (int ty = 0; ty < Hd; ty += th)
          for (int tx = 0; tx < Wd; tx += tw) {
            bool any_true = false, any_false = false;
            for (int y = ty; y < ty + th && y < Hd; ++y)
              for (int x = tx; x < tx + tw && x < Wd; ++x) {
                double dx = x + 0.5 - cx, dy = y + 0.5 - cy;
                (dx * dx + dy * dy <= R * R ? any_true : any_false) = true;
              }
            ++tiles;
            mixed += any_true && any_false;
          }
        std::printf("R=%4.0f  tile %dx%d (%2d threads): %6ld tiles, %4ld mixed = %.2f %%\n", R, tw, th, tw * th, tiles, mixed, 100.0 * mixed / tiles);
      }
    }
  }

  // ---- [3] 占有率（レジスタ ファイルの大きさは仮定）----
  std::printf("\n[3] occupancy model (assumed: 256 registers per lane in total, at most 10 waves)\n");
  const int total_regs = 256, max_waves = 10;
  for (int regs : {24, 32, 48, 64, 96, 128, 200}) {
    int waves = std::min(max_waves, total_regs / regs);
    std::printf("regs per thread = %3d -> %2d waves (%3.0f %% of max)\n", regs, waves, 100.0 * waves / max_waves);
  }

  // ---- [4] 待ちを隠すのに必要なウェーブ数（仮定の待ち時間）----
  std::printf("\n[4] waves needed to hide latency L when each wave computes A cycles between fetches: ceil(L/A) + 1\n");
  for (double L : {200.0, 400.0}) {
    for (double A : {10.0, 20.0, 50.0, 100.0}) {
      std::printf("L=%3.0f A=%3.0f -> %2d waves\n", L, A, (int)std::ceil(L / A) + 1);
    }
  }
  return 0;
}
```
```

```text title="実行結果"
[1] random per-thread condition, true path cost A=100, false path cost B=10 (arbitrary units)
  W   p        P(both paths)  wave cost   ideal cost   ratio
 32  0.001    0.032          13.2        10.1         1.30
 32  0.010    0.275          37.5        10.9         3.44
 32  0.050    0.806          90.6        14.5         6.25
 32  0.500    1.000          110.0       55.0         2.00
 64  0.001    0.062          16.2        10.1         1.61
 64  0.010    0.474          57.4        10.9         5.27
 64  0.050    0.962          106.2       14.5         7.33
 64  0.500    1.000          110.0       55.0         2.00
```

```text title="実行結果（続き）"
[2] spatially coherent condition: disc of radius R at the screen center, waves are 8x4 (32) or 8x8 (64) pixel tiles
R=  50  tile 8x4 (32 threads):  64800 tiles,   60 mixed = 0.09 %
R=  50  tile 8x8 (64 threads):  32400 tiles,   42 mixed = 0.13 %
R= 150  tile 8x4 (32 threads):  64800 tiles,  184 mixed = 0.28 %
R= 150  tile 8x8 (64 threads):  32400 tiles,  126 mixed = 0.39 %
R= 300  tile 8x4 (32 threads):  64800 tiles,  372 mixed = 0.57 %
R= 300  tile 8x8 (64 threads):  32400 tiles,  262 mixed = 0.81 %
R= 500  tile 8x4 (32 threads):  64800 tiles,  652 mixed = 1.01 %
R= 500  tile 8x8 (64 threads):  32400 tiles,  434 mixed = 1.34 %
```

```text title="実行結果（続き）"
[3] occupancy model (assumed: 256 registers per lane in total, at most 10 waves)
regs per thread =  24 -> 10 waves (100 % of max)
regs per thread =  32 ->  8 waves ( 80 % of max)
regs per thread =  48 ->  5 waves ( 50 % of max)
regs per thread =  64 ->  4 waves ( 40 % of max)
regs per thread =  96 ->  2 waves ( 20 % of max)
regs per thread = 128 ->  2 waves ( 20 % of max)
regs per thread = 200 ->  1 waves ( 10 % of max)
```

```text title="実行結果（続き）"
[4] waves needed to hide latency L when each wave computes A cycles between fetches: ceil(L/A) + 1
L=200 A= 10 -> 21 waves
L=200 A= 20 -> 11 waves
L=200 A= 50 ->  5 waves
L=200 A=100 ->  3 waves
L=400 A= 10 -> 41 waves
L=400 A= 20 -> 21 waves
L=400 A= 50 ->  9 waves
L=400 A=100 ->  5 waves
```

## よくあるミス {#mistakes}

??? failure "定数の指数の `pow` を手で乗算に書き換えて時間を使う"
    `fxc` は指数が定数の `pow` を乗算に直す。命令数は同じだった。直すべきなのは指数が変数の `pow` や特殊な演算の連なりのほう。

??? failure "演算ばかり減らして、メモリ読み込みが支配のまま"
    テクスチャを 3 枚から 1 枚に詰めると、読み込みが 3 分の 1 になる。演算の書き換えより効きやすい。

??? failure "ランダムな条件を分岐で囲んで、重い処理を飛ばしたつもりになる"
    ウェーブの中で割れると、両方の道を通る。条件を空間的にそろえるか `[flatten]` で足りる軽い処理にする。

??? failure "巨大な 1 つのシェーダーに全機能を詰め込む"
    レジスタが増えて占有率が下がる。パスを分ける。

??? failure "命令数が同じだから、同じ速さだと思う"
    静的な命令数は依存した読み込みの待ちを表さない。`Tex4Independent` と `Tex4Dependent` はどちらも 7 命令だった。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] コストは演算・メモリ読み込み・分岐・レジスタ。どれが支配かを測ってから直す。
    - [x] 定数の指数の `pow` は、コンパイラが乗算にする。指数が変数の `pow` は `log` と `exp` を使う。
    - [x] テクスチャを 1 枚に詰めると、読み込みが減る。
    - [x] ランダムな分岐は、まれでもウェーブの中で割れる。空間的にそろえる。
    - [x] レジスタを増やすとウェーブ数が階段状に落ちる。待ちを隠せなくなる。

## 参考 {#references}

- Microsoft, "fxc" (HLSL Shader Compiler), Windows SDK. このページの命令数は `fxc` 10.1 の出力。
- このページの HLSL 断片と C++ のモデルは、説明のために書いたもの。実機の GPU の資料（ウェーブの大きさレジスタ ファイル、待ち時間）は読んでいない。

## 関連ページ {#related}

- [Pipeline and Optimization](index.md)
- [Bottlenecks](bottlenecks.md)
- [Memory Bandwidth](bandwidth.md)
- [分岐と仮想関数](../../optimize/branching-virtual.md)
- [PBR](../../3d/pbr.md)
