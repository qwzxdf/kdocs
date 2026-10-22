# -*- coding: utf-8 -*-
"""組み込み関数の表。

1 行 = 名前 | シグネチャ(;; 区切り) | 説明 | 最低シェーダー モデル
T = スカラー/ベクター/行列のどれでもよい同じ型、F = float 系、I = int 系、U = uint 系。
"""

RAW = r"""
# ---- 数学 ----
abs | T abs(T x) | 絶対値。 | 1.0
acos | F acos(F x) | 逆余弦(ラジアン)。x は [-1, 1]。 | 1.0
all | bool all(T x) | すべての成分が 0 でなければ true。 | 1.0
any | bool any(T x) | 0 でない成分が 1 つでもあれば true。 | 1.0
asdouble | double asdouble(uint lowbits, uint highbits);;double2 asdouble(uint2 lowbits, uint2 highbits) | 2 つの uint のビット列を double として読み替える。 | 5.0
asfloat | F asfloat(T x) | ビット列を float として読み替える(int / uint / float)。 | 4.0
asfloat16 | float16_t asfloat16(T x) | ビット列を float16_t として読み替える。 | 6.2
asin | F asin(F x) | 逆正弦(ラジアン)。 | 1.0
asint | I asint(T x) | ビット列を int として読み替える。 | 4.0
asint16 | int16_t asint16(T x) | ビット列を int16_t として読み替える。 | 6.2
asuint | U asuint(T x);;void asuint(double value, out uint lowbits, out uint highbits) | ビット列を uint として読み替える。double は 2 つの uint に分ける。 | 4.0
asuint16 | uint16_t asuint16(T x) | ビット列を uint16_t として読み替える。 | 6.2
atan | F atan(F x) | 逆正接(ラジアン)。 | 1.0
atan2 | F atan2(F y, F x) | y / x の逆正接。象限を区別して [-π, π] を返す。 | 1.0
ceil | F ceil(F x) | 切り上げ。 | 1.0
clamp | T clamp(T x, T min, T max) | x を [min, max] に収める。 | 1.0
clip | void clip(F x) | x のどれかの成分が 0 未満なら、そのピクセルを破棄する。ピクセル シェーダー専用。 | 1.0
cos | F cos(F x) | 余弦(ラジアン)。 | 1.0
cosh | F cosh(F x) | 双曲線余弦。 | 1.0
countbits | uint countbits(U x) | 立っているビットの数。 | 5.0
cross | float3 cross(float3 x, float3 y) | 外積。 | 1.0
D3DCOLORtoUBYTE4 | int4 D3DCOLORtoUBYTE4(float4 x) | float4 の色を 0〜255 の int4 に変換する(成分の並びを入れ替える)。 | 1.0
ddx | F ddx(F x) | 画面 X 方向の偏微分。 | 2.0
ddx_coarse | F ddx_coarse(F x) | 粗い(2x2 クアッドで共通の)X 偏微分。 | 5.0
ddx_fine | F ddx_fine(F x) | 細かい(ピクセルごとの)X 偏微分。 | 5.0
ddy | F ddy(F x) | 画面 Y 方向の偏微分。 | 2.0
ddy_coarse | F ddy_coarse(F x) | 粗い Y 偏微分。 | 5.0
ddy_fine | F ddy_fine(F x) | 細かい Y 偏微分。 | 5.0
degrees | F degrees(F x) | ラジアンを度に変換する。 | 1.0
determinant | float determinant(floatNxN m) | 行列式。 | 1.0
distance | float distance(F x, F y) | 2 点間の距離。 | 1.0
dot | float dot(F x, F y);;int dot(I x, I y) | 内積。 | 1.0
dst | float4 dst(float4 src0, float4 src1) | 距離ベクトルを計算する(ライティング用の古い関数)。 | 5.0
exp | F exp(F x) | e の x 乗。 | 1.0
exp2 | F exp2(F x) | 2 の x 乗。 | 1.0
f16tof32 | float f16tof32(uint x) | 下位 16 ビットの half を float に変換する。 | 5.0
f32tof16 | uint f32tof16(float x) | float を half のビット列(下位 16 ビット)に変換する。 | 5.0
faceforward | F faceforward(F n, F i, F ng) | dot(i, ng) < 0 なら n、そうでなければ -n を返す。 | 1.0
firstbithigh | int firstbithigh(I x) | 最上位の立っているビットの位置(0 から数える)。無ければ -1。 | 5.0
firstbitlow | int firstbitlow(I x) | 最下位の立っているビットの位置。無ければ -1。 | 5.0
floor | F floor(F x) | 切り捨て。 | 1.0
fma | double fma(double a, double b, double c) | a * b + c を 1 回の丸めで計算する(double 用)。 | 5.0
fmod | F fmod(F x, F y) | 浮動小数点の剰余。符号は x に従う。 | 1.0
frac | F frac(F x) | 小数部分。 | 1.0
frexp | F frexp(F x, out F exp) | x を仮数と指数に分ける。 | 1.0
fwidth | F fwidth(F x) | abs(ddx(x)) + abs(ddy(x))。 | 2.0
isfinite | bool isfinite(F x) | 有限(NaN でも ∞ でもない)なら true。 | 1.0
isinf | bool isinf(F x) | ±∞ なら true。 | 1.0
isnan | bool isnan(F x) | NaN なら true。 | 1.0
isnormal | bool isnormal(F x) | 正規化数(0・非正規化数・∞・NaN 以外)なら true。 | 6.0
ldexp | F ldexp(F x, F exp) | x * 2^exp。 | 1.0
length | float length(F x) | ベクターの長さ。 | 1.0
lerp | F lerp(F x, F y, F s) | x + s * (y - x)。線形補間。 | 1.0
lit | float4 lit(float ndotl, float ndoth, float m) | ライティング係数(ambient, diffuse, specular, 1)を計算する。 | 1.0
log | F log(F x) | 自然対数。 | 1.0
log10 | F log10(F x) | 常用対数。 | 1.0
log2 | F log2(F x) | 2 を底とする対数。 | 1.0
mad | T mad(T a, T b, T c) | a * b + c。 | 5.0
max | T max(T x, T y) | 大きいほう。 | 1.0
min | T min(T x, T y) | 小さいほう。 | 1.0
modf | F modf(F x, out F ip) | 整数部と小数部に分ける。戻り値が小数部、ip が整数部。 | 1.0
msad4 | uint4 msad4(uint reference, uint2 source, uint4 accum) | マスク付き絶対差の和(4 回分)。 | 5.0
mul | T mul(T a, T b) | 行列とベクターの積、行列同士の積、スカラーの積。HLSL は行ベクトルで v * M と書く。 | 1.0
noise | float noise(F x) | 疑似ノイズ。現在は使えない。 | 1.0
normalize | F normalize(F x) | 長さ 1 に正規化する。 | 1.0
pow | F pow(F x, F y) | x の y 乗。x が負だと NaN。 | 1.0
printf | void printf(string format, ...) | デバッグ出力(PIX / DXC のデバッグ層)。 | 6.0
radians | F radians(F x) | 度をラジアンに変換する。 | 1.0
rcp | F rcp(F x) | 逆数 1 / x。 | 5.0
reflect | F reflect(F i, F n) | 入射ベクトル i を法線 n で反射する。 | 1.0
refract | F refract(F i, F n, float eta) | 屈折ベクトル。eta は屈折率の比。 | 1.0
reversebits | U reversebits(U x) | ビットの並びを反転する。 | 5.0
round | F round(F x) | 四捨五入(偶数丸め)。 | 1.0
rsqrt | F rsqrt(F x) | 1 / sqrt(x)。 | 1.0
saturate | F saturate(F x) | [0, 1] に収める。 | 1.0
select | T select(bool cond, T a, T b) | 成分ごとの三項演算子。cond が true なら a、false なら b。HLSL 2021 以降。 | 6.0
sign | I sign(F x) | 符号(-1, 0, 1)。 | 1.0
sin | F sin(F x) | 正弦(ラジアン)。 | 1.0
sincos | void sincos(F x, out F s, out F c) | sin と cos を一度に計算する。 | 1.0
sinh | F sinh(F x) | 双曲線正弦。 | 1.0
smoothstep | F smoothstep(F min, F max, F x) | エルミート補間(3x² - 2x³)。範囲外は 0 / 1。 | 1.0
sqrt | F sqrt(F x) | 平方根。 | 1.0
step | F step(F y, F x) | x >= y なら 1、そうでなければ 0。 | 1.0
tan | F tan(F x) | 正接(ラジアン)。 | 1.0
tanh | F tanh(F x) | 双曲線正接。 | 1.0
transpose | T transpose(T m) | 転置行列。 | 1.0
trunc | F trunc(F x) | 0 方向への切り捨て。 | 1.0
abort | void abort() | シェーダーを中断する(デバッグ用)。 | 1.0
errorf | void errorf(string format, ...) | エラー メッセージを出力する(デバッグ用)。 | 1.0
# ---- 16 ビット・パック ----
dot2add | float dot2add(half2 a, half2 b, float c) | half2 の内積に float を足す。 | 6.4
dot4add_u8packed | uint dot4add_u8packed(uint a, uint b, uint c) | 8 ビット × 4 の符号なしパック同士の内積に c を足す。 | 6.4
dot4add_i8packed | int dot4add_i8packed(uint a, uint b, int c) | 8 ビット × 4 の符号付きパック同士の内積に c を足す。 | 6.4
pack_u8 | uint8_t4_packed pack_u8(uint4 unpackedValue);;uint8_t4_packed pack_u8(int16_t4 unpackedValue) | 4 つの値を下位 8 ビットずつ切り出して 1 つの uint にパックする。 | 6.6
pack_s8 | int8_t4_packed pack_s8(int4 unpackedValue);;int8_t4_packed pack_s8(int16_t4 unpackedValue) | 4 つの値を符号付き 8 ビットでパックする。 | 6.6
pack_clamp_u8 | uint8_t4_packed pack_clamp_u8(int4 unpackedValue);;uint8_t4_packed pack_clamp_u8(int16_t4 unpackedValue) | 0〜255 に収めてからパックする。 | 6.6
pack_clamp_s8 | int8_t4_packed pack_clamp_s8(int4 unpackedValue);;int8_t4_packed pack_clamp_s8(int16_t4 unpackedValue) | -128〜127 に収めてからパックする。 | 6.6
unpack_u8u16 | uint16_t4 unpack_u8u16(uint8_t4_packed packedValue) | パックされた 8 ビット × 4 を uint16_t4 に展開する。 | 6.6
unpack_u8u32 | uint4 unpack_u8u32(uint8_t4_packed packedValue) | パックされた 8 ビット × 4 を uint4 に展開する。 | 6.6
unpack_s8s16 | int16_t4 unpack_s8s16(int8_t4_packed packedValue) | 符号付きでパックされた値を int16_t4 に展開する。 | 6.6
unpack_s8s32 | int4 unpack_s8s32(int8_t4_packed packedValue) | 符号付きでパックされた値を int4 に展開する。 | 6.6
# ---- アトミック ----
InterlockedAdd | void InterlockedAdd(R dest, T value);;void InterlockedAdd(R dest, T value, out T original_value) | dest に value を足す(原子的)。 | 5.0
InterlockedAnd | void InterlockedAnd(R dest, T value);;void InterlockedAnd(R dest, T value, out T original_value) | dest と value の論理積を取る(原子的)。 | 5.0
InterlockedCompareExchange | void InterlockedCompareExchange(R dest, T compare_value, T value, out T original_value) | dest が compare_value と等しければ value を書く。元の値を返す。 | 5.0
InterlockedCompareStore | void InterlockedCompareStore(R dest, T compare_value, T value) | dest が compare_value と等しければ value を書く。 | 5.0
InterlockedExchange | void InterlockedExchange(R dest, T value, out T original_value) | dest と value を入れ替える。 | 5.0
InterlockedMax | void InterlockedMax(R dest, T value);;void InterlockedMax(R dest, T value, out T original_value) | dest と value の大きいほうを書く。64 ビットは SM 6.6。 | 5.0
InterlockedMin | void InterlockedMin(R dest, T value);;void InterlockedMin(R dest, T value, out T original_value) | dest と value の小さいほうを書く。64 ビットは SM 6.6。 | 5.0
InterlockedOr | void InterlockedOr(R dest, T value);;void InterlockedOr(R dest, T value, out T original_value) | dest と value の論理和を取る。 | 5.0
InterlockedXor | void InterlockedXor(R dest, T value);;void InterlockedXor(R dest, T value, out T original_value) | dest と value の排他的論理和を取る。 | 5.0
# ---- DXC の定義表(gen_intrin_main.txt)との突き合わせで、足した物 ----
NonUniformResourceIndex | uint NonUniformResourceIndex(uint index) | ウェーブ内のレーンごとに値が違うインデックスで、リソースを引くことを、コンパイラーに伝える(バインドレスで必須)。 | 5.1
CheckAccessFullyMapped | bool CheckAccessFullyMapped(uint status) | タイルド リソースの読み取りの status を見て、すべてがマップ済みのメモリに当たったなら true。 | 5.0
and | T and(T x, T y) | 成分ごとの論理積(HLSL 2021 の関数形)。 | 6.0
or | T or(T x, T y) | 成分ごとの論理和(HLSL 2021 の関数形)。 | 6.0
InterlockedCompareStoreFloatBitwise | void InterlockedCompareStoreFloatBitwise(R dest, float compare_value, float value) | float をビットで比較して、等しければ value を書く(原子的)。 | 6.6
InterlockedCompareExchangeFloatBitwise | void InterlockedCompareExchangeFloatBitwise(R dest, float compare_value, float value, out float original_value) | float をビットで比較して、等しければ value を書き、元の値を返す(原子的)。 | 6.6
GetGroupWaveIndex | uint GetGroupWaveIndex() | スレッド グループの中での、このウェーブの番号。 | 6.10
GetGroupWaveCount | uint GetGroupWaveCount() | スレッド グループの中の、ウェーブの数。 | 6.10
DebugBreak | void DebugBreak() | デバッガーで、ここで止める。 | 6.10
ClusterID | uint ClusterID() | ヒットしたクラスターの ID(クラスター ジオメトリ)。 | 6.10
TriangleObjectPositions | float3x3 TriangleObjectPositions() | ヒットした三角形の 3 頂点の、オブジェクト空間での位置(行ごとに 1 頂点)。 | 6.10

# ---- バリア ----
AllMemoryBarrier | void AllMemoryBarrier() | すべてのメモリ アクセスが完了するまで待つ。 | 5.0
AllMemoryBarrierWithGroupSync | void AllMemoryBarrierWithGroupSync() | AllMemoryBarrier に加えて、スレッド グループ内の全スレッドの到達も待つ。 | 5.0
DeviceMemoryBarrier | void DeviceMemoryBarrier() | UAV とバッファ(デバイス メモリ)のアクセスが完了するまで待つ。 | 5.0
DeviceMemoryBarrierWithGroupSync | void DeviceMemoryBarrierWithGroupSync() | DeviceMemoryBarrier に加えて、グループ全体の同期も取る。 | 5.0
GroupMemoryBarrier | void GroupMemoryBarrier() | groupshared のアクセスが完了するまで待つ。 | 5.0
GroupMemoryBarrierWithGroupSync | void GroupMemoryBarrierWithGroupSync() | GroupMemoryBarrier に加えて、グループ全体の同期も取る。 | 5.0
Barrier | void Barrier(uint MemoryTypeFlags, uint SemanticFlags);;void Barrier(object target, uint SemanticFlags) | SM 6.8 の汎用バリア。メモリの種類と、スコープ・同期の指定を組み合わせる。 | 6.8
# ---- ピクセル シェーダー ----
EvaluateAttributeCentroid | T EvaluateAttributeCentroid(T attrib) | 補間された属性を、ピクセルの重心で評価し直す。 | 5.0
EvaluateAttributeAtSample | T EvaluateAttributeAtSample(T attrib, uint sampleIndex) | 補間された属性を、指定サンプルの位置で評価し直す。 | 5.0
EvaluateAttributeSnapped | T EvaluateAttributeSnapped(T attrib, int2 offset) | 補間された属性を、ピクセル中心から 1/16 ピクセル単位のオフセットで評価し直す。 | 5.0
GetAttributeAtVertex | T GetAttributeAtVertex(nointerpolation T attrib, uint vertexID) | 補間前の頂点属性を直接取り出す(0, 1, 2)。SV_Barycentrics と組み合わせる。 | 6.1
GetRenderTargetSampleCount | uint GetRenderTargetSampleCount() | レンダー ターゲットのサンプル数。 | 4.1
GetRenderTargetSamplePosition | float2 GetRenderTargetSamplePosition(int index) | サンプルのピクセル内の位置。 | 4.1
IsHelperLane | bool IsHelperLane() | 現在のレーンがヘルパー レーン(微分用の捨てレーン)なら true。 | 6.6
# ---- テッセレーション ----
Process2DQuadTessFactorsAvg | void Process2DQuadTessFactorsAvg(float4 RawEdgeFactors, float2 InsideScale, out float4 RoundedEdgeTessFactors, out float2 RoundedInsideTessFactors, out float2 UnroundedInsideTessFactors) | クアッドのテッセレーション係数を平均で丸める。 | 5.0
Process2DQuadTessFactorsMax | void Process2DQuadTessFactorsMax(float4 RawEdgeFactors, float2 InsideScale, out float4 RoundedEdgeTessFactors, out float2 RoundedInsideTessFactors, out float2 UnroundedInsideTessFactors) | クアッドのテッセレーション係数を最大値で丸める。 | 5.0
Process2DQuadTessFactorsMin | void Process2DQuadTessFactorsMin(float4 RawEdgeFactors, float2 InsideScale, out float4 RoundedEdgeTessFactors, out float2 RoundedInsideTessFactors, out float2 UnroundedInsideTessFactors) | クアッドのテッセレーション係数を最小値で丸める。 | 5.0
ProcessIsolineTessFactors | void ProcessIsolineTessFactors(float RawDetailFactor, float RawDensityFactor, out float RoundedDetailFactor, out float RoundedDensityFactor) | アイソラインのテッセレーション係数を丸める。 | 5.0
ProcessQuadTessFactorsAvg | void ProcessQuadTessFactorsAvg(float4 RawEdgeFactors, float InsideScale, out float4 RoundedEdgeTessFactors, out float2 RoundedInsideTessFactors, out float2 UnroundedInsideTessFactors) | クアッドのテッセレーション係数を平均で処理する。 | 5.0
ProcessQuadTessFactorsMax | void ProcessQuadTessFactorsMax(float4 RawEdgeFactors, float InsideScale, out float4 RoundedEdgeTessFactors, out float2 RoundedInsideTessFactors, out float2 UnroundedInsideTessFactors) | クアッドのテッセレーション係数を最大値で処理する。 | 5.0
ProcessQuadTessFactorsMin | void ProcessQuadTessFactorsMin(float4 RawEdgeFactors, float InsideScale, out float4 RoundedEdgeTessFactors, out float2 RoundedInsideTessFactors, out float2 UnroundedInsideTessFactors) | クアッドのテッセレーション係数を最小値で処理する。 | 5.0
ProcessTriTessFactorsAvg | void ProcessTriTessFactorsAvg(float3 RawEdgeFactors, float InsideScale, out float3 RoundedEdgeTessFactors, out float RoundedInsideTessFactor, out float UnroundedInsideTessFactor) | 三角形のテッセレーション係数を平均で処理する。 | 5.0
ProcessTriTessFactorsMax | void ProcessTriTessFactorsMax(float3 RawEdgeFactors, float InsideScale, out float3 RoundedEdgeTessFactors, out float RoundedInsideTessFactor, out float UnroundedInsideTessFactor) | 三角形のテッセレーション係数を最大値で処理する。 | 5.0
ProcessTriTessFactorsMin | void ProcessTriTessFactorsMin(float3 RawEdgeFactors, float InsideScale, out float3 RoundedEdgeTessFactors, out float RoundedInsideTessFactor, out float UnroundedInsideTessFactor) | 三角形のテッセレーション係数を最小値で処理する。 | 5.0
# ---- 古いテクスチャ関数(SM 3 まで) ----
tex1D | float4 tex1D(sampler1D s, float t) | 1D テクスチャをサンプリングする(旧 API)。 | 1.0
tex1Dbias | float4 tex1Dbias(sampler1D s, float4 t) | mip バイアス付きの 1D サンプリング(旧 API)。 | 1.0
tex1Dgrad | float4 tex1Dgrad(sampler1D s, float t, float ddx, float ddy) | 勾配指定の 1D サンプリング(旧 API)。 | 1.0
tex1Dlod | float4 tex1Dlod(sampler1D s, float4 t) | mip レベル指定の 1D サンプリング(旧 API)。 | 1.0
tex1Dproj | float4 tex1Dproj(sampler1D s, float4 t) | 射影つきの 1D サンプリング(旧 API)。 | 1.0
tex2D | float4 tex2D(sampler2D s, float2 t) | 2D テクスチャをサンプリングする(旧 API)。 | 1.0
tex2Dbias | float4 tex2Dbias(sampler2D s, float4 t) | mip バイアス付きの 2D サンプリング(旧 API)。 | 1.0
tex2Dgrad | float4 tex2Dgrad(sampler2D s, float2 t, float2 ddx, float2 ddy) | 勾配指定の 2D サンプリング(旧 API)。 | 1.0
tex2Dlod | float4 tex2Dlod(sampler2D s, float4 t) | mip レベル指定の 2D サンプリング(旧 API)。 | 1.0
tex2Dproj | float4 tex2Dproj(sampler2D s, float4 t) | 射影つきの 2D サンプリング(旧 API)。 | 1.0
tex3D | float4 tex3D(sampler3D s, float3 t) | 3D テクスチャをサンプリングする(旧 API)。 | 1.0
tex3Dbias | float4 tex3Dbias(sampler3D s, float4 t) | mip バイアス付きの 3D サンプリング(旧 API)。 | 1.0
tex3Dgrad | float4 tex3Dgrad(sampler3D s, float3 t, float3 ddx, float3 ddy) | 勾配指定の 3D サンプリング(旧 API)。 | 1.0
tex3Dlod | float4 tex3Dlod(sampler3D s, float4 t) | mip レベル指定の 3D サンプリング(旧 API)。 | 1.0
tex3Dproj | float4 tex3Dproj(sampler3D s, float4 t) | 射影つきの 3D サンプリング(旧 API)。 | 1.0
texCUBE | float4 texCUBE(samplerCUBE s, float3 t) | キューブ テクスチャをサンプリングする(旧 API)。 | 1.0
texCUBEbias | float4 texCUBEbias(samplerCUBE s, float4 t) | mip バイアス付きのキューブ サンプリング(旧 API)。 | 1.0
texCUBEgrad | float4 texCUBEgrad(samplerCUBE s, float3 t, float3 ddx, float3 ddy) | 勾配指定のキューブ サンプリング(旧 API)。 | 1.0
texCUBElod | float4 texCUBElod(samplerCUBE s, float4 t) | mip レベル指定のキューブ サンプリング(旧 API)。 | 1.0
texCUBEproj | float4 texCUBEproj(samplerCUBE s, float4 t) | 射影つきのキューブ サンプリング(旧 API)。 | 1.0
# ---- ウェーブ(SM 6.0) ----
WaveIsFirstLane | bool WaveIsFirstLane() | 現在のレーンが、ウェーブ内のアクティブな最初のレーンなら true。 | 6.0
WaveGetLaneIndex | uint WaveGetLaneIndex() | ウェーブ内でのレーン番号(0 始まり)。 | 6.0
WaveGetLaneCount | uint WaveGetLaneCount() | ウェーブのレーン数(通常 32 か 64)。 | 6.0
WaveActiveAnyTrue | bool WaveActiveAnyTrue(bool expr) | アクティブなレーンのどれかで expr が true なら true。 | 6.0
WaveActiveAllTrue | bool WaveActiveAllTrue(bool expr) | アクティブなレーンのすべてで expr が true なら true。 | 6.0
WaveActiveBallot | uint4 WaveActiveBallot(bool expr) | expr が true のレーンをビット マスクにして返す(uint4 の 128 ビット)。 | 6.0
WaveReadLaneAt | T WaveReadLaneAt(T expr, uint laneIndex) | 指定レーンの expr の値を読む。laneIndex は全レーンで同じ値にする。 | 6.0
WaveReadLaneFirst | T WaveReadLaneFirst(T expr) | アクティブな最初のレーンの値を全レーンに配る。 | 6.0
WaveActiveAllEqual | bool WaveActiveAllEqual(T expr) | アクティブな全レーンで値が等しければ true。 | 6.0
WaveActiveBitAnd | U WaveActiveBitAnd(U expr) | アクティブな全レーンの論理積。 | 6.0
WaveActiveBitOr | U WaveActiveBitOr(U expr) | アクティブな全レーンの論理和。 | 6.0
WaveActiveBitXor | U WaveActiveBitXor(U expr) | アクティブな全レーンの排他的論理和。 | 6.0
WaveActiveCountBits | uint WaveActiveCountBits(bool bBit) | bBit が true のレーンの数。 | 6.0
WaveActiveMax | T WaveActiveMax(T expr) | アクティブな全レーンの最大値。 | 6.0
WaveActiveMin | T WaveActiveMin(T expr) | アクティブな全レーンの最小値。 | 6.0
WaveActiveProduct | T WaveActiveProduct(T expr) | アクティブな全レーンの積。 | 6.0
WaveActiveSum | T WaveActiveSum(T expr) | アクティブな全レーンの和。 | 6.0
WavePrefixCountBits | uint WavePrefixCountBits(bool bBit) | 自分より前のレーンで bBit が true の数。 | 6.0
WavePrefixProduct | T WavePrefixProduct(T expr) | 自分より前のレーンの積(排他的)。 | 6.0
WavePrefixSum | T WavePrefixSum(T expr) | 自分より前のレーンの和(排他的)。 | 6.0
QuadReadLaneAt | T QuadReadLaneAt(T expr, uint quadLaneIndex) | クアッド(2x2)内の指定レーンの値を読む。 | 6.0
QuadReadAcrossX | T QuadReadAcrossX(T expr) | クアッド内で X 方向に隣のレーンの値を読む。 | 6.0
QuadReadAcrossY | T QuadReadAcrossY(T expr) | クアッド内で Y 方向に隣のレーンの値を読む。 | 6.0
QuadReadAcrossDiagonal | T QuadReadAcrossDiagonal(T expr) | クアッド内で対角のレーンの値を読む。 | 6.0
# ---- ウェーブ(SM 6.5 以降) ----
WaveMatch | uint4 WaveMatch(T expr) | expr が自分と同じ値のレーンをビット マスクで返す。 | 6.5
WaveMultiPrefixBitAnd | U WaveMultiPrefixBitAnd(U expr, uint4 mask) | mask で指定したグループ内の、自分より前のレーンの論理積。 | 6.5
WaveMultiPrefixBitOr | U WaveMultiPrefixBitOr(U expr, uint4 mask) | mask で指定したグループ内の、自分より前のレーンの論理和。 | 6.5
WaveMultiPrefixBitXor | U WaveMultiPrefixBitXor(U expr, uint4 mask) | mask で指定したグループ内の、自分より前のレーンの排他的論理和。 | 6.5
WaveMultiPrefixCountBits | uint WaveMultiPrefixCountBits(bool value, uint4 mask) | mask のグループ内で、自分より前に value が true のレーンの数。 | 6.5
WaveMultiPrefixProduct | T WaveMultiPrefixProduct(T value, uint4 mask) | mask のグループ内で、自分より前のレーンの積。 | 6.5
WaveMultiPrefixSum | T WaveMultiPrefixSum(T value, uint4 mask) | mask のグループ内で、自分より前のレーンの和。 | 6.5
QuadAny | bool QuadAny(bool expr) | クアッド内のどれかのレーンで expr が true なら true。 | 6.7
QuadAll | bool QuadAll(bool expr) | クアッド内のすべてのレーンで expr が true なら true。 | 6.7
# ---- メッシュ シェーダー(SM 6.5) ----
SetMeshOutputCounts | void SetMeshOutputCounts(uint numVertices, uint numPrimitives) | このグループが出力する頂点数とプリミティブ数を宣言する。出力を書く前に 1 回だけ、全スレッドで呼ぶ。 | 6.5
DispatchMesh | void DispatchMesh(uint ThreadGroupCountX, uint ThreadGroupCountY, uint ThreadGroupCountZ, groupshared payload_type payload) | 増幅シェーダーから、メッシュ シェーダーのグループを起動する。呼んだあとの処理は実行されない。 | 6.5
# ---- レイトレーシング(DXR) ----
TraceRay | void TraceRay(RaytracingAccelerationStructure AccelerationStructure, uint RayFlags, uint InstanceInclusionMask, uint RayContributionToHitGroupIndex, uint MultiplierForGeometryContributionToHitGroupIndex, uint MissShaderIndex, RayDesc Ray, inout payload_t Payload) | レイを飛ばして、最も近い交差を探す。 | 6.3
CallShader | void CallShader(uint ShaderIndex, inout callable_params_t Parameter) | Callable シェーダーを呼ぶ。 | 6.3
ReportHit | bool ReportHit(float THit, uint HitKind, attr_t Attributes) | 交差シェーダーから、交点を報告する。 | 6.3
IgnoreHit | void IgnoreHit() | Any-hit シェーダーで、この交点を無視する。以降の処理は実行されない。 | 6.3
AcceptHitAndEndSearch | void AcceptHitAndEndSearch() | Any-hit シェーダーで、この交点を採用して探索を終える。以降の処理は実行されない。 | 6.3
DispatchRaysIndex | uint3 DispatchRaysIndex() | DispatchRays の中での、現在のスレッドの 3 次元位置。 | 6.3
DispatchRaysDimensions | uint3 DispatchRaysDimensions() | DispatchRays の幅・高さ・深さ。 | 6.3
WorldRayOrigin | float3 WorldRayOrigin() | ワールド空間でのレイの始点。 | 6.3
WorldRayDirection | float3 WorldRayDirection() | ワールド空間でのレイの方向(正規化されていない)。 | 6.3
RayTMin | float RayTMin() | レイの最小 T。 | 6.3
RayTCurrent | float RayTCurrent() | 現在の最も近い交点までの T。ミスのときは TMax。 | 6.3
RayFlags | uint RayFlags() | TraceRay に渡された RayFlags。 | 6.3
InstanceIndex | uint InstanceIndex() | TLAS 内でのインスタンスの通し番号。 | 6.3
InstanceID | uint InstanceID() | インスタンスに設定された InstanceID(ユーザー値)。 | 6.3
GeometryIndex | uint GeometryIndex() | BLAS 内のジオメトリ番号。 | 6.5
PrimitiveIndex | uint PrimitiveIndex() | ジオメトリ内の三角形(プリミティブ)の番号。 | 6.3
ObjectRayOrigin | float3 ObjectRayOrigin() | オブジェクト空間でのレイの始点。 | 6.3
ObjectRayDirection | float3 ObjectRayDirection() | オブジェクト空間でのレイの方向。 | 6.3
ObjectToWorld3x4 | float3x4 ObjectToWorld3x4() | オブジェクト → ワールドの変換行列(3 行 4 列)。 | 6.3
ObjectToWorld4x3 | float4x3 ObjectToWorld4x3() | オブジェクト → ワールドの変換行列(4 行 3 列。mul(v, M) 向け)。 | 6.3
WorldToObject3x4 | float3x4 WorldToObject3x4() | ワールド → オブジェクトの変換行列(3 行 4 列)。 | 6.3
WorldToObject4x3 | float4x3 WorldToObject4x3() | ワールド → オブジェクトの変換行列(4 行 3 列)。 | 6.3
ObjectToWorld | float3x4 ObjectToWorld() | ObjectToWorld3x4 の古い名前。 | 6.3
WorldToObject | float3x4 WorldToObject() | WorldToObject3x4 の古い名前。 | 6.3
HitKind | uint HitKind() | 交点の種類(表面 / 裏面など)。 | 6.3
GetRemainingRecursionLevels | uint GetRemainingRecursionLevels() | 残りの再帰回数。ワーク グラフではノードの再帰レベル。 | 6.8
"""

# 特殊な名前空間つき(dx::)。名前は "dx::XXX" で持つ
RAW_DX = r"""
dx::MaybeReorderThread | void MaybeReorderThread(dx::HitObject hit);;void MaybeReorderThread(uint CoherenceHint, uint NumCoherenceHintBitsFromLSB);;void MaybeReorderThread(dx::HitObject hit, uint CoherenceHint, uint NumCoherenceHintBitsFromLSB) | Shader Execution Reordering。レイの結果が似たスレッドを、近くのウェーブに寄せ集める。 | 6.9
dx::IsDebuggingEnabled | bool IsDebuggingEnabled() | デバッグが有効なら true。 | 6.10
dx::HitObject | dx::HitObject | レイの探索結果(ヒット / ミス / NOP)を持つ型。TraceRay と Invoke を分けて呼ぶために使う。 | 6.9
"""
