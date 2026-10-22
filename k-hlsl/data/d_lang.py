# -*- coding: utf-8 -*-
"""型・メソッド・セマンティクス・属性・キーワード・定数・ディレクティブの表。"""

# ---- リソース型 -------------------------------------------------------
# 名前 | 説明 | 最低 SM | メソッド群(カンマ区切り)
RESOURCE_TYPES = r"""
Texture1D | 1D テクスチャ(読み取り専用)。 | 4.0 | tex,texlod
Texture1DArray | 1D テクスチャ配列。 | 4.0 | tex,texlod
Texture2D | 2D テクスチャ(読み取り専用)。 | 4.0 | tex,texlod,gather
Texture2DArray | 2D テクスチャ配列。 | 4.0 | tex,texlod,gather
Texture2DMS | マルチサンプル 2D テクスチャ。 | 4.0 | ms
Texture2DMSArray | マルチサンプル 2D テクスチャ配列。 | 4.0 | ms
Texture3D | 3D テクスチャ。 | 4.0 | tex,texlod
TextureCube | キューブ テクスチャ。 | 4.0 | tex,texlod,gather
TextureCubeArray | キューブ テクスチャ配列。 | 4.0 | tex,texlod,gather
RWTexture1D | 読み書きできる 1D テクスチャ(UAV)。 | 5.0 | rwtex
RWTexture1DArray | 読み書きできる 1D テクスチャ配列。 | 5.0 | rwtex
RWTexture2D | 読み書きできる 2D テクスチャ(UAV)。 | 5.0 | rwtex
RWTexture2DArray | 読み書きできる 2D テクスチャ配列。 | 5.0 | rwtex
RWTexture3D | 読み書きできる 3D テクスチャ。 | 5.0 | rwtex
RasterizerOrderedTexture1D | ラスタライザ順序付きの 1D テクスチャ(ROV)。 | 5.1 | rwtex
RasterizerOrderedTexture1DArray | ラスタライザ順序付きの 1D テクスチャ配列。 | 5.1 | rwtex
RasterizerOrderedTexture2D | ラスタライザ順序付きの 2D テクスチャ(ROV)。 | 5.1 | rwtex
RasterizerOrderedTexture2DArray | ラスタライザ順序付きの 2D テクスチャ配列。 | 5.1 | rwtex
RasterizerOrderedTexture3D | ラスタライザ順序付きの 3D テクスチャ。 | 5.1 | rwtex
FeedbackTexture2D | サンプラー フィードバック用の 2D テクスチャ。 | 6.5 | feedback
FeedbackTexture2DArray | サンプラー フィードバック用の 2D テクスチャ配列。 | 6.5 | feedback
Buffer | 型つきバッファ(読み取り専用)。 | 4.0 | buf
RWBuffer | 型つきバッファ(UAV)。 | 5.0 | buf
RasterizerOrderedBuffer | ラスタライザ順序付きの型つきバッファ。 | 5.1 | buf
StructuredBuffer | 構造体の配列バッファ(読み取り専用)。 | 4.0 | sbuf
RWStructuredBuffer | 構造体の配列バッファ(UAV)。カウンターつき。 | 5.0 | sbuf,sbufrw
RasterizerOrderedStructuredBuffer | ラスタライザ順序付きの構造体バッファ。 | 5.1 | sbuf
AppendStructuredBuffer | 追記専用の構造体バッファ。 | 5.0 | append
ConsumeStructuredBuffer | 取り出し専用の構造体バッファ。 | 5.0 | consume
ByteAddressBuffer | バイト アドレスで読むバッファ(読み取り専用)。 | 5.0 | bab
RWByteAddressBuffer | バイト アドレスで読み書きするバッファ(UAV)。 | 5.0 | bab,babrw
RasterizerOrderedByteAddressBuffer | ラスタライザ順序付きのバイト アドレス バッファ。 | 5.1 | bab,babrw
ConstantBuffer | 型つきの定数バッファ。 | 5.1 |
TextureBuffer | tbuffer を型つきで書く形式。 | 4.0 |
SamplerState | サンプラー。 | 4.0 |
SamplerComparisonState | 比較サンプラー(SampleCmp 用)。 | 4.0 |
RaytracingAccelerationStructure | レイトレーシングの加速構造(TLAS)。 | 6.3 |
RayQuery | インライン レイトレーシング(DXR 1.1)のレイ クエリ。 | 6.5 | rayquery
InputPatch | ハル シェーダーの入力パッチ。 | 5.0 | patch
OutputPatch | ドメイン シェーダーの入力パッチ。 | 5.0 | patch
PointStream | ジオメトリ シェーダーのポイント出力ストリーム。 | 4.0 | stream
LineStream | ジオメトリ シェーダーの線出力ストリーム。 | 4.0 | stream
TriangleStream | ジオメトリ シェーダーの三角形出力ストリーム。 | 4.0 | stream
NodeOutput | ワーク グラフのノード出力。 | 6.8 | nodeout
NodeOutputArray | ワーク グラフのノード出力配列。 | 6.8 | nodeout
EmptyNodeOutput | レコードを持たないノード出力。 | 6.8 | emptynodeout
EmptyNodeOutputArray | レコードを持たないノード出力の配列。 | 6.8 | emptynodeout
DispatchNodeInputRecord | ブロードキャスト ノードの入力レコード(読み取り専用)。 | 6.8 | noderec
RWDispatchNodeInputRecord | ブロードキャスト ノードの入力レコード(読み書き)。 | 6.8 | noderec
GroupNodeInputRecords | コアレッシング ノードの入力レコード群(読み取り専用)。 | 6.8 | noderecs
RWGroupNodeInputRecords | コアレッシング ノードの入力レコード群(読み書き)。 | 6.8 | noderecs
ThreadNodeInputRecord | スレッド ノードの入力レコード(読み取り専用)。 | 6.8 | noderec
RWThreadNodeInputRecord | スレッド ノードの入力レコード(読み書き)。 | 6.8 | noderec
EmptyNodeInput | レコードを持たない入力。 | 6.8 | emptynodein
NodeOutputRecord | ノードの出力レコード(GetThreadNodeOutputRecords など)。 | 6.8 | noderecs
ThreadNodeOutputRecords | スレッド単位の出力レコード群。 | 6.8 | noderecs
GroupNodeOutputRecords | グループ単位の出力レコード群。 | 6.8 | noderecs
"""

# ---- メソッド群 -------------------------------------------------------
# 群 | 名前 | シグネチャ(;; 区切り) | 説明 | SM
METHODS = r"""
tex | Sample | T Sample(SamplerState s, float location [, int offset [, float clamp [, out uint status]]]) | サンプラーでテクスチャを読む。暗黙の微分から mip レベルを決める。 | 4.0
tex | SampleBias | T SampleBias(SamplerState s, float location, float bias [, int offset [, float clamp [, out uint status]]]) | mip レベルにバイアスを足してサンプリングする。 | 4.0
tex | SampleCmp | float SampleCmp(SamplerComparisonState s, float location, float compareValue [, int offset [, float clamp [, out uint status]]]) | 比較サンプリング(シャドウ マップ用)。 | 4.1
tex | SampleCmpBias | float SampleCmpBias(SamplerComparisonState s, float location, float compareValue, float bias [, int offset [, float clamp [, out uint status]]]) | バイアス付きの比較サンプリング。 | 6.8
tex | SampleCmpGrad | float SampleCmpGrad(SamplerComparisonState s, float location, float compareValue, float ddx, float ddy [, int offset [, float clamp [, out uint status]]]) | 勾配を指定した比較サンプリング。 | 6.8
tex | SampleCmpLevel | float SampleCmpLevel(SamplerComparisonState s, float location, float compareValue, float lod [, int offset [, out uint status]]) | mip レベルを指定した比較サンプリング。 | 6.7
tex | SampleCmpLevelZero | float SampleCmpLevelZero(SamplerComparisonState s, float location, float compareValue [, int offset [, out uint status]]) | mip レベル 0 での比較サンプリング。 | 4.1
tex | SampleGrad | T SampleGrad(SamplerState s, float location, float ddx, float ddy [, int offset [, float clamp [, out uint status]]]) | 勾配を指定してサンプリングする。 | 4.0
tex | SampleLevel | T SampleLevel(SamplerState s, float location, float lod [, int offset [, out uint status]]) | mip レベルを指定してサンプリングする。微分が要らないので、どのシェーダー ステージでも使える。 | 4.0
tex | Load | T Load(int location [, int offset [, out uint status]]) | サンプラーを使わずに、テクセルを整数座標で読む。最後の成分が mip レベル。 | 4.0
tex | GetDimensions | void GetDimensions([uint mipLevel,] out uint width [, out uint height [, out uint depth]], out uint numberOfLevels) | テクスチャの大きさと mip 数を取る。 | 4.0
tex | CalculateLevelOfDetail | float CalculateLevelOfDetail(SamplerState s, float location) | mip レベルを計算する(クランプ後)。ピクセル シェーダー、SM 6.6 以降は CS / MS / AS も。 | 4.1
tex | CalculateLevelOfDetailUnclamped | float CalculateLevelOfDetailUnclamped(SamplerState s, float location) | mip レベルを計算する(クランプ前)。 | 4.1
texlod | mips | mips[mipLevel][pos] | mip レベルを指定して、配列の添字のようにテクセルを読む。 | 4.0
gather | Gather | T Gather(SamplerState s, float location [, int offset]) | 4 テクセルの赤成分を集める。 | 4.1
gather | GatherRed | T GatherRed(SamplerState s, float location [, int offset [, out uint status]]) | 4 テクセルの赤成分を集める。 | 5.0
gather | GatherGreen | T GatherGreen(SamplerState s, float location [, int offset [, out uint status]]) | 4 テクセルの緑成分を集める。 | 5.0
gather | GatherBlue | T GatherBlue(SamplerState s, float location [, int offset [, out uint status]]) | 4 テクセルの青成分を集める。 | 5.0
gather | GatherAlpha | T GatherAlpha(SamplerState s, float location [, int offset [, out uint status]]) | 4 テクセルのアルファ成分を集める。 | 5.0
gather | GatherCmp | float4 GatherCmp(SamplerComparisonState s, float location, float compareValue [, int offset]) | 4 テクセルを比較して、結果(0 / 1)を集める。 | 4.1
gather | GatherCmpRed | float4 GatherCmpRed(SamplerComparisonState s, float location, float compareValue [, int offset [, out uint status]]) | 赤成分を 4 テクセル比較して集める。 | 5.0
gather | GatherCmpGreen | float4 GatherCmpGreen(SamplerComparisonState s, float location, float compareValue [, int offset [, out uint status]]) | 緑成分を 4 テクセル比較して集める。 | 5.0
gather | GatherCmpBlue | float4 GatherCmpBlue(SamplerComparisonState s, float location, float compareValue [, int offset [, out uint status]]) | 青成分を 4 テクセル比較して集める。 | 5.0
gather | GatherCmpAlpha | float4 GatherCmpAlpha(SamplerComparisonState s, float location, float compareValue [, int offset [, out uint status]]) | アルファ成分を 4 テクセル比較して集める。 | 5.0
gather | GatherRaw | uint4 GatherRaw(SamplerState s, float location [, int offset]) | 4 テクセルの生のビット(整数)を集める。 | 6.7
ms | Load | T Load(int2 location, int sampleIndex [, int2 offset [, out uint status]]) | マルチサンプル テクスチャの、指定サンプルを読む。 | 4.0
ms | GetSamplePosition | float2 GetSamplePosition(int sampleIndex) | サンプルのピクセル内の位置。 | 4.0
ms | GetDimensions | void GetDimensions(out uint width, out uint height [, out uint elements], out uint numberOfSamples) | 大きさとサンプル数を取る。 | 4.0
ms | sample | sample[sampleIndex][pos] | サンプルを指定して、配列の添字のようにテクセルを読む。 | 4.0
rwtex | Load | T Load(int location [, out uint status]) | UAV のテクセルを読む。 | 5.0
rwtex | GetDimensions | void GetDimensions(out uint width [, out uint height [, out uint depth]]) | 大きさを取る。 | 5.0
buf | Load | T Load(int location [, out uint status]) | 要素を読む。 | 4.0
buf | GetDimensions | void GetDimensions(out uint numStructs) | 要素数を取る。 | 4.0
sbuf | Load | T Load(int location [, out uint status]) | 要素を読む。 | 4.0
sbuf | GetDimensions | void GetDimensions(out uint numStructs, out uint stride) | 要素数とストライドを取る。 | 4.0
sbufrw | IncrementCounter | uint IncrementCounter() | 隠しカウンターを 1 増やして、増やす前の値を返す。 | 5.0
sbufrw | DecrementCounter | uint DecrementCounter() | 隠しカウンターを 1 減らして、減らした後の値を返す。 | 5.0
append | Append | void Append(T value) | 末尾に 1 要素を追加する。 | 5.0
append | GetDimensions | void GetDimensions(out uint numStructs, out uint stride) | 要素数とストライドを取る。 | 5.0
consume | Consume | T Consume() | 末尾から 1 要素を取り出す。 | 5.0
consume | GetDimensions | void GetDimensions(out uint numStructs, out uint stride) | 要素数とストライドを取る。 | 5.0
bab | Load | uint Load(uint byteOffset [, out uint status]) | バイト オフセットから 1 つの uint を読む。 | 5.0
bab | Load2 | uint2 Load2(uint byteOffset [, out uint status]) | 2 つの uint を読む。 | 5.0
bab | Load3 | uint3 Load3(uint byteOffset [, out uint status]) | 3 つの uint を読む。 | 5.0
bab | Load4 | uint4 Load4(uint byteOffset [, out uint status]) | 4 つの uint を読む。 | 5.0
bab | Load | T Load<T>(uint byteOffset) | 任意の型 T を読む。HLSL 2018 以降、SM 6.2 以降。 | 6.2
bab | GetDimensions | void GetDimensions(out uint dim) | バッファのバイト数を取る。 | 5.0
babrw | Store | void Store(uint byteOffset, uint value) | 1 つの uint を書く。 | 5.0
babrw | Store2 | void Store2(uint byteOffset, uint2 value) | 2 つの uint を書く。 | 5.0
babrw | Store3 | void Store3(uint byteOffset, uint3 value) | 3 つの uint を書く。 | 5.0
babrw | Store4 | void Store4(uint byteOffset, uint4 value) | 4 つの uint を書く。 | 5.0
babrw | Store | void Store<T>(uint byteOffset, T value) | 任意の型 T を書く。SM 6.2 以降。 | 6.2
babrw | InterlockedAdd | void InterlockedAdd(uint byteOffset, uint value [, out uint original]) | 原子的に加算する。 | 5.0
babrw | InterlockedAdd64 | void InterlockedAdd64(uint byteOffset, uint64_t value [, out uint64_t original]) | 64 ビットの原子的な加算。 | 6.6
babrw | InterlockedAnd | void InterlockedAnd(uint byteOffset, uint value [, out uint original]) | 原子的に論理積を取る。 | 5.0
babrw | InterlockedAnd64 | void InterlockedAnd64(uint byteOffset, uint64_t value [, out uint64_t original]) | 64 ビットの原子的な論理積。 | 6.6
babrw | InterlockedCompareExchange | void InterlockedCompareExchange(uint byteOffset, uint compare, uint value, out uint original) | 比較して等しければ交換する。 | 5.0
babrw | InterlockedCompareExchange64 | void InterlockedCompareExchange64(uint byteOffset, uint64_t compare, uint64_t value, out uint64_t original) | 64 ビットの比較交換。 | 6.6
babrw | InterlockedCompareStore | void InterlockedCompareStore(uint byteOffset, uint compare, uint value) | 比較して等しければ書く。 | 5.0
babrw | InterlockedCompareStore64 | void InterlockedCompareStore64(uint byteOffset, uint64_t compare, uint64_t value) | 64 ビットの比較書き込み。 | 6.6
babrw | InterlockedExchange | void InterlockedExchange(uint byteOffset, uint value, out uint original) | 原子的に入れ替える。 | 5.0
babrw | InterlockedExchange64 | void InterlockedExchange64(uint byteOffset, uint64_t value, out uint64_t original) | 64 ビットの原子的な入れ替え。 | 6.6
babrw | InterlockedMax | void InterlockedMax(uint byteOffset, uint value [, out uint original]) | 原子的に最大値を書く。 | 5.0
babrw | InterlockedMax64 | void InterlockedMax64(uint byteOffset, uint64_t value [, out uint64_t original]) | 64 ビットの原子的な最大値。 | 6.6
babrw | InterlockedMin | void InterlockedMin(uint byteOffset, uint value [, out uint original]) | 原子的に最小値を書く。 | 5.0
babrw | InterlockedMin64 | void InterlockedMin64(uint byteOffset, uint64_t value [, out uint64_t original]) | 64 ビットの原子的な最小値。 | 6.6
babrw | InterlockedOr | void InterlockedOr(uint byteOffset, uint value [, out uint original]) | 原子的に論理和を取る。 | 5.0
babrw | InterlockedOr64 | void InterlockedOr64(uint byteOffset, uint64_t value [, out uint64_t original]) | 64 ビットの原子的な論理和。 | 6.6
babrw | InterlockedXor | void InterlockedXor(uint byteOffset, uint value [, out uint original]) | 原子的に排他的論理和を取る。 | 5.0
babrw | InterlockedXor64 | void InterlockedXor64(uint byteOffset, uint64_t value [, out uint64_t original]) | 64 ビットの原子的な排他的論理和。 | 6.6
babrw | InterlockedCompareExchangeFloatBitwise | void InterlockedCompareExchangeFloatBitwise(uint byteOffset, float compare, float value, out float original) | float をビット比較して交換する。 | 6.6
babrw | InterlockedCompareStoreFloatBitwise | void InterlockedCompareStoreFloatBitwise(uint byteOffset, float compare, float value) | float をビット比較して書く。 | 6.6
stream | Append | void Append(T vertex) | 頂点を出力ストリームに追加する。 | 4.0
stream | RestartStrip | void RestartStrip() | 現在のストリップを終えて、次のストリップを始める。 | 4.0
patch | Length | uint Length | パッチの制御点の数。 | 5.0
feedback | WriteSamplerFeedback | void WriteSamplerFeedback(Texture2D tex, SamplerState s, float2 location [, float clamp]) | サンプラー フィードバックを書く。 | 6.5
feedback | WriteSamplerFeedbackBias | void WriteSamplerFeedbackBias(Texture2D tex, SamplerState s, float2 location, float bias [, float clamp]) | バイアス付きで書く。 | 6.5
feedback | WriteSamplerFeedbackGrad | void WriteSamplerFeedbackGrad(Texture2D tex, SamplerState s, float2 location, float2 ddx, float2 ddy [, float clamp]) | 勾配を指定して書く。 | 6.5
feedback | WriteSamplerFeedbackLevel | void WriteSamplerFeedbackLevel(Texture2D tex, SamplerState s, float2 location, float lod) | mip レベルを指定して書く。 | 6.5
rayquery | TraceRayInline | void TraceRayInline(RaytracingAccelerationStructure accel, uint rayFlags, uint instanceInclusionMask, RayDesc ray) | インライン レイトレーシングを始める。 | 6.5
rayquery | Proceed | bool Proceed() | 次の候補へ進む。まだ続くなら true。 | 6.5
rayquery | Abort | void Abort() | クエリを打ち切る。 | 6.5
rayquery | CommitNonOpaqueTriangleHit | void CommitNonOpaqueTriangleHit() | 不透明でない三角形の候補を確定する。 | 6.5
rayquery | CommitProceduralPrimitiveHit | void CommitProceduralPrimitiveHit(float t) | プロシージャル プリミティブの候補を確定する。 | 6.5
rayquery | CommittedStatus | COMMITTED_STATUS CommittedStatus() | 確定した交点の種類。 | 6.5
rayquery | CandidateType | CANDIDATE_TYPE CandidateType() | 現在の候補の種類。 | 6.5
rayquery | CandidateTriangleBarycentrics | float2 CandidateTriangleBarycentrics() | 候補三角形の重心座標。 | 6.5
rayquery | CandidateTriangleFrontFace | bool CandidateTriangleFrontFace() | 候補三角形が表向きなら true。 | 6.5
rayquery | CandidateTriangleRayT | float CandidateTriangleRayT() | 候補三角形への T。 | 6.5
rayquery | CandidateProceduralPrimitiveNonOpaque | bool CandidateProceduralPrimitiveNonOpaque() | 候補プロシージャル プリミティブが不透明でなければ true。 | 6.5
rayquery | CandidateInstanceIndex | uint CandidateInstanceIndex() | 候補のインスタンス番号。 | 6.5
rayquery | CandidateInstanceID | uint CandidateInstanceID() | 候補の InstanceID。 | 6.5
rayquery | CandidateInstanceContributionToHitGroupIndex | uint CandidateInstanceContributionToHitGroupIndex() | 候補のヒット グループ オフセット。 | 6.5
rayquery | CandidateGeometryIndex | uint CandidateGeometryIndex() | 候補のジオメトリ番号。 | 6.5
rayquery | CandidatePrimitiveIndex | uint CandidatePrimitiveIndex() | 候補のプリミティブ番号。 | 6.5
rayquery | CandidateObjectRayOrigin | float3 CandidateObjectRayOrigin() | 候補のオブジェクト空間でのレイ始点。 | 6.5
rayquery | CandidateObjectRayDirection | float3 CandidateObjectRayDirection() | 候補のオブジェクト空間でのレイ方向。 | 6.5
rayquery | CandidateObjectToWorld3x4 | float3x4 CandidateObjectToWorld3x4() | 候補のオブジェクト → ワールド行列。 | 6.5
rayquery | CandidateObjectToWorld4x3 | float4x3 CandidateObjectToWorld4x3() | 候補のオブジェクト → ワールド行列(4x3)。 | 6.5
rayquery | CandidateWorldToObject3x4 | float3x4 CandidateWorldToObject3x4() | 候補のワールド → オブジェクト行列。 | 6.5
rayquery | CandidateWorldToObject4x3 | float4x3 CandidateWorldToObject4x3() | 候補のワールド → オブジェクト行列(4x3)。 | 6.5
rayquery | CommittedRayT | float CommittedRayT() | 確定した交点への T。 | 6.5
rayquery | CommittedTriangleBarycentrics | float2 CommittedTriangleBarycentrics() | 確定した三角形の重心座標。 | 6.5
rayquery | CommittedTriangleFrontFace | bool CommittedTriangleFrontFace() | 確定した三角形が表向きなら true。 | 6.5
rayquery | CommittedInstanceIndex | uint CommittedInstanceIndex() | 確定したインスタンス番号。 | 6.5
rayquery | CommittedInstanceID | uint CommittedInstanceID() | 確定した InstanceID。 | 6.5
rayquery | CommittedInstanceContributionToHitGroupIndex | uint CommittedInstanceContributionToHitGroupIndex() | 確定したヒット グループ オフセット。 | 6.5
rayquery | CommittedGeometryIndex | uint CommittedGeometryIndex() | 確定したジオメトリ番号。 | 6.5
rayquery | CommittedPrimitiveIndex | uint CommittedPrimitiveIndex() | 確定したプリミティブ番号。 | 6.5
rayquery | CommittedObjectRayOrigin | float3 CommittedObjectRayOrigin() | 確定した交点でのオブジェクト空間のレイ始点。 | 6.5
rayquery | CommittedObjectRayDirection | float3 CommittedObjectRayDirection() | 確定した交点でのオブジェクト空間のレイ方向。 | 6.5
rayquery | CommittedObjectToWorld3x4 | float3x4 CommittedObjectToWorld3x4() | 確定した オブジェクト → ワールド行列。 | 6.5
rayquery | CommittedObjectToWorld4x3 | float4x3 CommittedObjectToWorld4x3() | 確定した オブジェクト → ワールド行列(4x3)。 | 6.5
rayquery | CommittedWorldToObject3x4 | float3x4 CommittedWorldToObject3x4() | 確定した ワールド → オブジェクト行列。 | 6.5
rayquery | CommittedWorldToObject4x3 | float4x3 CommittedWorldToObject4x3() | 確定した ワールド → オブジェクト行列(4x3)。 | 6.5
rayquery | RayFlags | uint RayFlags() | TraceRayInline に渡した RayFlags。 | 6.5
rayquery | WorldRayOrigin | float3 WorldRayOrigin() | ワールド空間のレイ始点。 | 6.5
rayquery | WorldRayDirection | float3 WorldRayDirection() | ワールド空間のレイ方向。 | 6.5
rayquery | RayTMin | float RayTMin() | レイの最小 T。 | 6.5
nodeout | GetThreadNodeOutputRecords | ThreadNodeOutputRecords<T> GetThreadNodeOutputRecords(uint numRecords) | スレッドごとに出力レコードを確保する。 | 6.8
nodeout | GetGroupNodeOutputRecords | GroupNodeOutputRecords<T> GetGroupNodeOutputRecords(uint numRecords) | グループで共有する出力レコードを確保する。 | 6.8
nodeout | IsValid | bool IsValid() | この出力先が接続されていれば true。 | 6.8
nodeout | OutputComplete | void OutputComplete() | 出力をすべて終えたことを伝える。 | 6.8
nodeout | ThreadIncrementOutputCount | void ThreadIncrementOutputCount(uint count) | スレッド単位で、出力数を増やす(Empty 出力用)。 | 6.8
nodeout | GroupIncrementOutputCount | void GroupIncrementOutputCount(uint count) | グループ単位で、出力数を増やす(Empty 出力用)。 | 6.8
emptynodeout | IsValid | bool IsValid() | この出力先が接続されていれば true。 | 6.8
emptynodeout | ThreadIncrementOutputCount | void ThreadIncrementOutputCount(uint count) | スレッド単位で、出力数を増やす。 | 6.8
emptynodeout | GroupIncrementOutputCount | void GroupIncrementOutputCount(uint count) | グループ単位で、出力数を増やす。 | 6.8
noderec | Get | T Get() | レコードの中身を取る(参照)。 | 6.8
noderec | FinishedCrossGroupSharing | bool FinishedCrossGroupSharing() | グループをまたぐ共有の最後のグループなら true。RWDispatchNodeInputRecord 用。 | 6.8
noderecs | Get | T Get(uint index) | index 番目のレコードを取る。 | 6.8
noderecs | Count | uint Count() | レコードの数。 | 6.8
emptynodein | Count | uint Count() | 空レコードの数。 | 6.8
"""

# 型つきの dx:: 系(SM 6.9)
DX_TYPES = r"""
dx::HitObject | レイの探索結果を持つ型。TraceRay と Invoke を分けて呼べる。SM 6.9 の Shader Execution Reordering。 | 6.9
"""
HITOBJECT_METHODS = r"""
dx::HitObject::TraceRay | static dx::HitObject TraceRay(RaytracingAccelerationStructure accel, uint rayFlags, uint instanceInclusionMask, uint rayContributionToHitGroupIndex, uint multiplierForGeometryContributionToHitGroupIndex, uint missShaderIndex, RayDesc ray, inout payload_t payload) | レイを飛ばして、結果を HitObject として受け取る(シェーダーは呼ばない)。 | 6.9
dx::HitObject::FromRayQuery | static dx::HitObject FromRayQuery(RayQuery<flags> query [, uint hitKind, attr_t attributes]) | RayQuery の結果から HitObject を作る。 | 6.9
dx::HitObject::MakeMiss | static dx::HitObject MakeMiss(uint rayFlags, uint missShaderIndex, RayDesc ray) | ミスの HitObject を作る。 | 6.9
dx::HitObject::MakeNop | static dx::HitObject MakeNop() | 何も起こさない HitObject を作る。 | 6.9
dx::HitObject::Invoke | static void Invoke(dx::HitObject hit, inout payload_t payload) | HitObject に対応するシェーダー(closest hit / miss)を実行する。 | 6.9
dx::HitObject::IsHit | bool IsHit() | ヒットなら true。 | 6.9
dx::HitObject::IsMiss | bool IsMiss() | ミスなら true。 | 6.9
dx::HitObject::IsNop | bool IsNop() | NOP なら true。 | 6.9
dx::HitObject::GetShaderTableIndex | uint GetShaderTableIndex() | シェーダー テーブルの番号を取る。 | 6.9
dx::HitObject::SetShaderTableIndex | void SetShaderTableIndex(uint recordIndex) | シェーダー テーブルの番号を上書きする。 | 6.9
dx::HitObject::LoadLocalRootTableConstant | uint LoadLocalRootTableConstant(uint offset) | ローカル ルート テーブルの定数を読む。 | 6.9
dx::HitObject::GetRayFlags | uint GetRayFlags() | RayFlags を取る。 | 6.9
dx::HitObject::GetRayTMin | float GetRayTMin() | レイの TMin を取る。 | 6.9
dx::HitObject::GetRayTCurrent | float GetRayTCurrent() | ヒット位置までの T を取る。 | 6.9
dx::HitObject::GetWorldRayOrigin | float3 GetWorldRayOrigin() | ワールド空間のレイ始点。 | 6.9
dx::HitObject::GetWorldRayDirection | float3 GetWorldRayDirection() | ワールド空間のレイ方向。 | 6.9
dx::HitObject::GetObjectRayOrigin | float3 GetObjectRayOrigin() | オブジェクト空間のレイ始点。 | 6.9
dx::HitObject::GetObjectRayDirection | float3 GetObjectRayDirection() | オブジェクト空間のレイ方向。 | 6.9
dx::HitObject::GetObjectToWorld3x4 | float3x4 GetObjectToWorld3x4() | オブジェクト → ワールド行列。 | 6.9
dx::HitObject::GetWorldToObject3x4 | float3x4 GetWorldToObject3x4() | ワールド → オブジェクト行列。 | 6.9
dx::HitObject::GetInstanceIndex | uint GetInstanceIndex() | インスタンス番号。 | 6.9
dx::HitObject::GetInstanceID | uint GetInstanceID() | InstanceID。 | 6.9
dx::HitObject::GetGeometryIndex | uint GetGeometryIndex() | ジオメトリ番号。 | 6.9
dx::HitObject::GetPrimitiveIndex | uint GetPrimitiveIndex() | プリミティブ番号。 | 6.9
dx::HitObject::GetHitKind | uint GetHitKind() | ヒットの種類。 | 6.9
dx::HitObject::GetAttributes | void GetAttributes(out attr_t attributes) | ヒット属性を取り出す。 | 6.9
"""

# ---- セマンティクス ----------------------------------------------------
SEMANTICS = r"""
SV_Position | 頂点シェーダーの出力ではクリップ空間の位置、ピクセル シェーダーの入力ではスクリーン座標(ピクセル中心は .5)。
SV_Target | ピクセル シェーダーの出力先レンダー ターゲット。SV_Target0〜7。
SV_Depth | ピクセル シェーダーが書き換える深度。
SV_DepthGreaterEqual | 深度を、元の値以上にだけ書き換える(Early-Z を保てる)。
SV_DepthLessEqual | 深度を、元の値以下にだけ書き換える(Early-Z を保てる)。
SV_Coverage | MSAA のカバレッジ マスク。出力にも入力にも使える。
SV_InnerCoverage | 保守的ラスタライズでの、内側カバレッジ。
SV_SampleIndex | 現在のサンプルの番号。これを入力にすると、サンプル単位で実行される。
SV_IsFrontFace | 表向きの三角形なら true。
SV_VertexID | 頂点番号(インデックスの値)。
SV_InstanceID | インスタンス番号。
SV_PrimitiveID | プリミティブの通し番号。
SV_GSInstanceID | ジオメトリ シェーダーのインスタンス番号。
SV_DispatchThreadID | Dispatch 全体での、スレッドの 3 次元位置。
SV_GroupID | スレッド グループの 3 次元位置。
SV_GroupThreadID | グループ内でのスレッドの 3 次元位置。
SV_GroupIndex | グループ内でのスレッドの 1 次元番号。
SV_DomainLocation | テッセレーションされた点の位置(ドメイン シェーダー)。
SV_InsideTessFactor | テッセレーションの内側係数。
SV_TessFactor | テッセレーションの辺の係数。
SV_OutputControlPointID | ハル シェーダーの、出力制御点の番号。
SV_ClipDistance | クリップ距離。負の側が切り取られる。SV_ClipDistance0 など。
SV_CullDistance | カリング距離。全頂点で負なら描かれない。
SV_RenderTargetArrayIndex | 描画先のスライス番号(レンダー ターゲット配列)。
SV_ViewportArrayIndex | 使うビューポートの番号。
SV_StencilRef | ピクセル シェーダーが書き換えるステンシル参照値。
SV_ShadingRate | 可変レート シェーディング(VRS)のレート。
SV_ViewID | マルチビュー レンダリングのビュー番号。
SV_Barycentrics | 重心座標(SM 6.1)。GetAttributeAtVertex と組み合わせる。
SV_CullPrimitive | メッシュ シェーダーで、そのプリミティブを捨てるかどうか。
SV_StartVertexLocation | DrawInstanced の StartVertexLocation(SM 6.8)。
SV_StartInstanceLocation | DrawInstanced の StartInstanceLocation(SM 6.8)。
SV_DispatchGrid | ワーク グラフの、ブロードキャスト ノードのディスパッチ グリッド(SM 6.8)。
SV_RayPayload | (予約)。
POSITION | 頂点位置(旧来のセマンティクス)。
POSITIONT | 変換済みの頂点位置(旧)。
NORMAL | 法線。
TANGENT | 接線。
BINORMAL | 従法線。
TEXCOORD | テクスチャ座標。TEXCOORD0, TEXCOORD1 …。
COLOR | 頂点色。
BLENDINDICES | スキニングの骨番号。
BLENDWEIGHT | スキニングの重み。
PSIZE | ポイント サイズ。
FOG | フォグ係数。
TESSFACTOR | テッセレーション係数(旧)。
DEPTH | 深度(旧)。
VPOS | スクリーン位置(SM 3)。
VFACE | 面の向き(SM 3)。
"""

# ---- 属性 --------------------------------------------------------------
# 名前 | 書式 | 説明 | SM
ATTRIBUTES = r"""
numthreads | numthreads(x, y, z) | スレッド グループの大きさ(コンピュート / メッシュ / 増幅 / ノード)。 | 5.0
domain | domain("tri" | "quad" | "isoline") | テッセレーションのドメイン。 | 5.0
partitioning | partitioning("integer" | "fractional_even" | "fractional_odd" | "pow2") | テッセレーションの分割方式。 | 5.0
outputtopology | outputtopology("point" | "line" | "triangle" | "triangle_cw" | "triangle_ccw") | テッセレーション / メッシュ シェーダーの出力トポロジー。 | 5.0
outputcontrolpoints | outputcontrolpoints(n) | ハル シェーダーの出力制御点の数。 | 5.0
patchconstantfunc | patchconstantfunc("name") | パッチ定数関数の名前。 | 5.0
maxtessfactor | maxtessfactor(n) | テッセレーション係数の最大値(ヒント)。 | 5.0
instance | instance(n) | ジオメトリ シェーダーのインスタンス数。 | 5.0
maxvertexcount | maxvertexcount(n) | ジオメトリ シェーダーが出力する頂点の最大数。 | 4.0
earlydepthstencil | earlydepthstencil | ピクセル シェーダーの前に、深度 / ステンシル テストを強制する。 | 5.0
RootSignature | RootSignature("...") | ルート シグネチャを文字列で書く。 | 5.1
unroll | unroll or unroll(n) | ループを展開する。 | 1.0
loop | loop | ループを展開しない(本物のループにする)。 | 1.0
fastopt | fastopt | ループの最適化を促す。 | 1.0
allow_uav_condition | allow_uav_condition | UAV に依存するループを許す。 | 5.0
branch | branch | if を分岐命令にする。 | 1.0
flatten | flatten | if を、両方の側を実行して選ぶ形にする。 | 1.0
forcecase | forcecase | switch を強制的に case 命令にする。 | 1.0
call | call | switch をサブルーチン呼び出しにする。 | 1.0
WaveSize | WaveSize(n) / WaveSize(min, max [, preferred]) | ウェーブのサイズを指定する(SM 6.6)。範囲指定は SM 6.8。 | 6.6
shader | shader("compute" | "vertex" | "pixel" | "geometry" | "hull" | "domain" | "mesh" | "amplification" | "node" | "raygeneration" | "closesthit" | "anyhit" | "miss" | "intersection" | "callable") | ライブラリ内のエントリ ポイントのステージを指定する。 | 6.3
experimental | experimental("...") | 試験的な機能の指定。 | 6.0
clipplanes | clipplanes(plane0, plane1, ...) | ユーザー クリップ平面(旧)。 | 4.0
noinline | noinline | インライン展開しない。 | 6.0
export | export | ライブラリから公開する関数(キーワード)。 | 6.1
raypayload | raypayload | レイ ペイロードの構造体(SM 6.7 のアクセス修飾子つき)。 | 6.7
Shader | Shader("node") | ワーク グラフのノード シェーダー。 | 6.8
NodeLaunch | NodeLaunch("broadcasting" | "coalescing" | "thread") | ノードの起動方式。 | 6.8
NodeIsProgramEntry | NodeIsProgramEntry | このノードをワーク グラフの入口にする。 | 6.8
NodeID | NodeID("name" [, arrayIndex]) | ノードの名前と配列番号。 | 6.8
NodeLocalRootArgumentsTableIndex | NodeLocalRootArgumentsTableIndex(n) | ローカル ルート引数テーブルの番号。 | 6.8
NodeShareInputOf | NodeShareInputOf("name" [, arrayIndex]) | 別のノードと入力を共有する。 | 6.8
NodeDispatchGrid | NodeDispatchGrid(x, y, z) | ブロードキャスト ノードの固定ディスパッチ グリッド。 | 6.8
NodeMaxDispatchGrid | NodeMaxDispatchGrid(x, y, z) | ブロードキャスト ノードのディスパッチ グリッドの上限。SV_DispatchGrid と組み合わせる。 | 6.8
NodeMaxRecursionDepth | NodeMaxRecursionDepth(n) | 再帰の最大深さ。 | 6.8
NodeTrackRWInputSharing | NodeTrackRWInputSharing | RW 入力の共有状況を追跡する。 | 6.8
MaxRecords | MaxRecords(n) | 出力 / 入力で扱うレコードの最大数。 | 6.8
MaxRecordsSharedWith | MaxRecordsSharedWith(param) | 別の出力と、レコード数の上限を共有する。 | 6.8
AllowSparseNodes | AllowSparseNodes | 出力先の配列に、欠番を許す。 | 6.8
NodeArraySize | NodeArraySize(n) | 出力配列の大きさ。 | 6.8
UnboundedSparseNodes | UnboundedSparseNodes | 出力配列の大きさを決めない。 | 6.8
vk::binding | vk::binding(binding [, set]) | SPIR-V: バインディングとセット番号。 | 0
vk::location | vk::location(n) | SPIR-V: 入出力のロケーション。 | 0
vk::push_constant | vk::push_constant | SPIR-V: プッシュ定数。 | 0
vk::constant_id | vk::constant_id(id) | SPIR-V: 特殊化定数の ID。 | 0
vk::builtin | vk::builtin("...") | SPIR-V: ビルトイン変数の指定。 | 0
vk::input_attachment_index | vk::input_attachment_index(n) | SPIR-V: 入力アタッチメントの番号。 | 0
vk::offset | vk::offset(n) | SPIR-V: メンバーのオフセット。 | 0
vk::index | vk::index(n) | SPIR-V: デュアル ソース ブレンドの出力インデックス。 | 0
vk::image_format | vk::image_format("...") | SPIR-V: 画像のフォーマット。 | 0
vk::counter_binding | vk::counter_binding(n) | SPIR-V: カウンター バッファのバインディング。 | 0
"""

# ---- キーワード --------------------------------------------------------
KEYWORDS_CONTROL = "break case continue default discard do else for if return switch while goto".split()
KEYWORDS_STORAGE = ("const static extern uniform volatile shared groupshared inline in out inout "
                    "nointerpolation linear centroid noperspective sample precise row_major column_major "
                    "globallycoherent reordercoherent snorm unorm unsigned export "
                    "perprimitive pervertex indices vertices primitives payload "
                    "triangle line point lineadj triangleadj").split()
KEYWORDS_DECL = ("struct class interface cbuffer tbuffer namespace typedef enum template typename using "
                 "operator this private public protected register packoffset static_assert sizeof "
                 "compile compile_fragment technique pass Technique Pass").split()
KEYWORD_DOCS = {
    "groupshared": "スレッド グループ内で共有するメモリ。GroupMemoryBarrierWithGroupSync で同期する。",
    "nointerpolation": "補間しない(プロビング頂点の値をそのまま渡す)。整数の入出力に必須。",
    "centroid": "重心で補間する(MSAA で、プリミティブの外を見ないようにする)。",
    "noperspective": "透視補正をしない線形補間。",
    "precise": "式の再結合を禁止して、結果を厳密にそろえる。",
    "row_major": "行列を行優先でメモリに置く。",
    "column_major": "行列を列優先でメモリに置く(既定)。",
    "globallycoherent": "UAV へのアクセスを、グループをまたいで一貫させる。",
    "reordercoherent": "UAV へのアクセスを、SER(スレッドの並べ替え)をまたいで一貫させる。",
    "cbuffer": "定数バッファを宣言する。register(bN, spaceM) で場所を指定する。",
    "discard": "ピクセルを破棄する(ピクセル シェーダー)。",
    "register": "レジスタ(t / s / u / b)と space を指定する。例: register(t0, space1)。",
    "packoffset": "定数バッファの中での位置を指定する。例: packoffset(c0.y)。",
    "perprimitive": "メッシュ シェーダーのプリミティブ単位の出力。",
    "vertices": "メッシュ シェーダーの頂点出力配列の修飾子。",
    "primitives": "メッシュ シェーダーのプリミティブ出力配列の修飾子。",
    "indices": "メッシュ シェーダーのインデックス出力配列の修飾子。",
    "payload": "増幅シェーダーからメッシュ シェーダーに渡すペイロード。",
    "export": "ライブラリから外へ公開する関数。",
    "static_assert": "コンパイル時のアサート(DXC)。",
}

# ---- 定数(列挙値・フラグ) --------------------------------------------
# 群 | 名前 | 説明
CONSTANTS = r"""
ray | RAY_FLAG_NONE | フラグなし。
ray | RAY_FLAG_FORCE_OPAQUE | すべてを不透明として扱う(any-hit を呼ばない)。
ray | RAY_FLAG_FORCE_NON_OPAQUE | すべてを不透明でないものとして扱う(any-hit を必ず呼ぶ)。
ray | RAY_FLAG_ACCEPT_FIRST_HIT_AND_END_SEARCH | 最初のヒットで探索を終える(影の判定向き)。
ray | RAY_FLAG_SKIP_CLOSEST_HIT_SHADER | closest-hit シェーダーを呼ばない。
ray | RAY_FLAG_CULL_BACK_FACING_TRIANGLES | 裏向きの三角形を無視する。
ray | RAY_FLAG_CULL_FRONT_FACING_TRIANGLES | 表向きの三角形を無視する。
ray | RAY_FLAG_CULL_OPAQUE | 不透明なものを無視する。
ray | RAY_FLAG_CULL_NON_OPAQUE | 不透明でないものを無視する。
ray | RAY_FLAG_SKIP_TRIANGLES | 三角形を無視する。
ray | RAY_FLAG_SKIP_PROCEDURAL_PRIMITIVES | プロシージャル プリミティブを無視する。
ray | RAY_FLAG_FORCE_OMM_2_STATE | Opacity Micromap を 2 状態として扱う(SM 6.9)。
hit | HIT_KIND_TRIANGLE_FRONT_FACE | 三角形の表側に当たった。
hit | HIT_KIND_TRIANGLE_BACK_FACE | 三角形の裏側に当たった。
rq | COMMITTED_NOTHING | 確定した交点がない。
rq | COMMITTED_TRIANGLE_HIT | 確定した交点は三角形。
rq | COMMITTED_PROCEDURAL_PRIMITIVE_HIT | 確定した交点はプロシージャル プリミティブ。
rq | CANDIDATE_NON_OPAQUE_TRIANGLE | 候補は不透明でない三角形。
rq | CANDIDATE_PROCEDURAL_PRIMITIVE | 候補はプロシージャル プリミティブ。
rq | COMMITTED_STATUS | CommittedStatus() の戻り値の型。
rq | CANDIDATE_TYPE | CandidateType() の戻り値の型。
pipe | RAYTRACING_PIPELINE_FLAG_NONE | フラグなし。
pipe | RAYTRACING_PIPELINE_FLAG_SKIP_TRIANGLES | パイプライン全体で三角形を無視する。
pipe | RAYTRACING_PIPELINE_FLAG_SKIP_PROCEDURAL_PRIMITIVES | パイプライン全体でプロシージャル プリミティブを無視する。
bar | UAV_MEMORY | Barrier: UAV のメモリ。
bar | GROUP_SHARED_MEMORY | Barrier: groupshared メモリ。
bar | NODE_INPUT_MEMORY | Barrier: ノードの入力メモリ。
bar | NODE_OUTPUT_MEMORY | Barrier: ノードの出力メモリ。
bar | ALL_MEMORY | Barrier: すべてのメモリ。
bar | GROUP_SYNC | Barrier: グループ内で同期する。
bar | GROUP_SCOPE | Barrier: グループの範囲で可視にする。
bar | DEVICE_SCOPE | Barrier: デバイス全体で可視にする。
bar | REORDER_SCOPE | Barrier: 並べ替えの範囲で可視にする。
sampler | SAMPLER_FEEDBACK_MIN_MIP | サンプラー フィードバックの種類: 最小 mip。
sampler | SAMPLER_FEEDBACK_MIP_REGION_USED | サンプラー フィードバックの種類: 使った mip 領域。
lang | true | 真。
lang | false | 偽。
lang | NULL | (HLSL にはない。DXC では未定義)。
"""

# ---- プリプロセッサ ----------------------------------------------------
DIRECTIVES = r"""
define | #define NAME value | マクロを定義する。
undef | #undef NAME | マクロの定義を消す。
include | #include "file" / #include <file> | ファイルを取り込む。
if | #if expr | 条件付きコンパイル。
ifdef | #ifdef NAME | マクロが定義されていれば有効。
ifndef | #ifndef NAME | マクロが定義されていなければ有効。
elif | #elif expr | 前の条件が偽のときの条件。
else | #else | 前の条件が偽のとき有効。
endif | #endif | 条件付きコンパイルの終わり。
pragma | #pragma ... | コンパイラへの指示。once / pack_matrix(row_major) / warning など。
error | #error message | コンパイルをエラーで止める。
warning | #warning message | 警告を出す。
line | #line number | 行番号を書き換える。
"""

MACROS = r"""
__HLSL_VERSION | HLSL の言語バージョン(2016 / 2017 / 2018 / 2021 / 202x)。
__SHADER_TARGET_MAJOR | ターゲット シェーダー モデルのメジャー番号。
__SHADER_TARGET_MINOR | ターゲット シェーダー モデルのマイナー番号。
__SHADER_TARGET_STAGE | ターゲットのステージ(__SHADER_STAGE_VERTEX などと比べる)。
__SHADER_STAGE_VERTEX | ステージ番号: 頂点。
__SHADER_STAGE_PIXEL | ステージ番号: ピクセル。
__SHADER_STAGE_GEOMETRY | ステージ番号: ジオメトリ。
__SHADER_STAGE_HULL | ステージ番号: ハル。
__SHADER_STAGE_DOMAIN | ステージ番号: ドメイン。
__SHADER_STAGE_COMPUTE | ステージ番号: コンピュート。
__SHADER_STAGE_AMPLIFICATION | ステージ番号: 増幅。
__SHADER_STAGE_MESH | ステージ番号: メッシュ。
__SHADER_STAGE_LIBRARY | ステージ番号: ライブラリ。
__DXC_VERSION_MAJOR | DXC のメジャー バージョン。
__DXC_VERSION_MINOR | DXC のマイナー バージョン。
__DXC_VERSION_RELEASE | DXC のリリース番号。
__DXC_VERSION_COMMITS | DXC のコミット数。
__spirv__ | SPIR-V 出力のとき定義される。
__FILE__ | 現在のファイル名。
__LINE__ | 現在の行番号。
__DATE__ | コンパイル日。
__TIME__ | コンパイル時刻。
"""

SCALAR_TYPES = ("bool int uint dword half float double min16float min10float min16int min12int min16uint "
                "int16_t uint16_t float16_t int32_t uint32_t float32_t int64_t uint64_t float64_t "
                "int8_t4_packed uint8_t4_packed string void vector matrix sampler sampler1D sampler2D "
                "sampler3D samplerCUBE sampler_state texture Texture").split()
SCALAR_DOCS = {
    "half": "16 ビット(min16float)か 32 ビットの浮動小数点。-enable-16bit-types を付けると本当の 16 ビット。",
    "dword": "uint の別名。",
    "min16float": "最低 16 ビットの浮動小数点(実際の精度は実装次第)。",
    "uint8_t4_packed": "8 ビット × 4 を 1 つの uint に詰めた型(SM 6.6)。pack_u8 / unpack_u8u32 で操作する。",
    "int8_t4_packed": "符号付き 8 ビット × 4 を 1 つの uint に詰めた型(SM 6.6)。",
    "vector": "vector<T, N>。HLSL 2021 のテンプレート形式。SM 6.9 では N が最大 1024 まで(ロング ベクター)。",
    "matrix": "matrix<T, R, C>。HLSL 2021 のテンプレート形式。",
    "string": "printf などの書式文字列用。変数には持てない。",
    "int16_t": "16 ビット符号付き整数(-enable-16bit-types)。",
    "uint16_t": "16 ビット符号なし整数(-enable-16bit-types)。",
    "float16_t": "16 ビット浮動小数点(-enable-16bit-types)。",
    "int64_t": "64 ビット符号付き整数(SM 6.0 以降。アトミックは SM 6.6)。",
    "uint64_t": "64 ビット符号なし整数。",
}

SPECIAL_OBJECTS = {
    "ResourceDescriptorHeap": "SM 6.6 以降。リソース ディスクリプタ ヒープ全体を、配列のように添字で引く。例: Texture2D t = ResourceDescriptorHeap[index];。ルート シグネチャに CBV_SRV_UAV_HEAP_DIRECTLY_INDEXED が必要。",
    "SamplerDescriptorHeap": "SM 6.6 以降。サンプラー ヒープ全体を添字で引く。例: SamplerState s = SamplerDescriptorHeap[index];。ルート シグネチャに SAMPLER_HEAP_DIRECTLY_INDEXED が必要。",
}
