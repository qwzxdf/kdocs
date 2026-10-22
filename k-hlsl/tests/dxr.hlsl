// レイトレーシング(DXR 1.0 / 1.1 / SER)の API を、ひととおり使うシェーダー。
// DXC(lib_6_9)でコンパイルできて、K-HLSL がすべての API を認識することを確かめる。

RaytracingAccelerationStructure gScene : register(t0, space0);
RWTexture2D<float4> gOutput : register(u0);
ByteAddressBuffer gGeometry : register(t1);

struct [raypayload] Payload
{
    float4 color : read(caller) : write(closesthit, miss, caller);
    uint   depth : read(closesthit, miss, caller) : write(caller);
};

struct CallableData { float3 tint; };

cbuffer Camera : register(b0)
{
    float4x4 gInvViewProj;
    float3   gEye;
    uint     gFrame;
};

[shader("raygeneration")]
void RayGen()
{
    uint2 index = DispatchRaysIndex().xy;
    uint2 size = DispatchRaysDimensions().xy;
    float2 uv = (float2(index) + 0.5) / float2(size);

    RayDesc ray;
    ray.Origin = gEye;
    ray.Direction = normalize(float3(uv * 2.0 - 1.0, 1.0));
    ray.TMin = 0.001;
    ray.TMax = 1000.0;

    Payload payload;
    payload.color = 0;
    payload.depth = 0;
    TraceRay(gScene, RAY_FLAG_CULL_BACK_FACING_TRIANGLES | RAY_FLAG_FORCE_OPAQUE, 0xFF, 0, 1, 0, ray, payload);
    gOutput[index] = payload.color;
}

[shader("closesthit")]
void ClosestHit(inout Payload payload, in BuiltInTriangleIntersectionAttributes attr)
{
    float3 bary = float3(1.0 - attr.barycentrics.x - attr.barycentrics.y, attr.barycentrics.x, attr.barycentrics.y);
    float t = RayTCurrent();
    float3 worldPos = WorldRayOrigin() + WorldRayDirection() * t;
    float3x4 o2w = ObjectToWorld3x4();
    float4x3 w2o = WorldToObject4x3();
    float3 objOrigin = ObjectRayOrigin();
    float3 objDir = ObjectRayDirection();
    uint kind = HitKind();
    bool front = kind == HIT_KIND_TRIANGLE_FRONT_FACE;
    uint ids = InstanceIndex() + InstanceID() + PrimitiveIndex() + GeometryIndex() + RayFlags();
    float tmin = RayTMin();
    payload.color = float4(bary * (front ? 1.0 : 0.5) + worldPos * 0.0 + objOrigin * 0.0 + objDir * 0.0 + o2w[0].xyz * 0.0 + w2o[0] * 0.0, tmin + ids);

    CallableData data;
    data.tint = float3(1, 0, 0);
    CallShader(0, data);
    payload.color.rgb *= data.tint;
}

[shader("anyhit")]
void AnyHit(inout Payload payload, in BuiltInTriangleIntersectionAttributes attr)
{
    if (attr.barycentrics.x < 0.1) { IgnoreHit(); }
    if (attr.barycentrics.y > 0.9) { AcceptHitAndEndSearch(); }
}

[shader("miss")]
void Miss(inout Payload payload)
{
    payload.color = float4(0.1, 0.2, 0.4, 1.0);
}

struct SphereAttr { float2 uv; };

[shader("intersection")]
void Sphere()
{
    SphereAttr a;
    a.uv = float2(0.5, 0.5);
    ReportHit(RayTCurrent(), 0, a);
}

[shader("callable")]
void Tint(inout CallableData data)
{
    data.tint *= 0.5;
}

// DXR 1.1: インライン レイトレーシング(RayQuery)
[numthreads(8, 8, 1)]
void InlineRT(uint3 id : SV_DispatchThreadID)
{
    RayDesc ray;
    ray.Origin = gEye;
    ray.Direction = float3(0, 0, 1);
    ray.TMin = 0.0;
    ray.TMax = 100.0;

    RayQuery<RAY_FLAG_FORCE_OPAQUE | RAY_FLAG_SKIP_PROCEDURAL_PRIMITIVES> q;
    q.TraceRayInline(gScene, 0, 0xFF, ray);
    while (q.Proceed())
    {
        if (q.CandidateType() == CANDIDATE_NON_OPAQUE_TRIANGLE)
        {
            q.CommitNonOpaqueTriangleHit();
        }
        else if (q.CandidateType() == CANDIDATE_PROCEDURAL_PRIMITIVE)
        {
            q.CommitProceduralPrimitiveHit(q.CandidateTriangleRayT());
        }
    }
    float4 result = 0;
    if (q.CommittedStatus() == COMMITTED_TRIANGLE_HIT)
    {
        float2 b = q.CommittedTriangleBarycentrics();
        float3x4 m = q.CommittedObjectToWorld3x4();
        result = float4(b, q.CommittedRayT(), q.CommittedTriangleFrontFace() ? 1.0 : 0.0);
        result.x += q.CommittedInstanceID() + q.CommittedInstanceIndex() + q.CommittedGeometryIndex() + q.CommittedPrimitiveIndex() + m[0][0];
        result.y += q.CommittedInstanceContributionToHitGroupIndex();
        float3 o = q.CommittedObjectRayOrigin() + q.CommittedObjectRayDirection();
        result.xyz += o + q.WorldRayOrigin() + q.WorldRayDirection();
        result.w += q.RayFlags() + q.RayTMin();
    }
    q.Abort();
    gOutput[id.xy] = result;
}

// SM 6.9: Shader Execution Reordering
[shader("raygeneration")]
void SerRayGen()
{
    RayDesc ray;
    ray.Origin = gEye;
    ray.Direction = float3(0, 0, 1);
    ray.TMin = 0.0;
    ray.TMax = 100.0;

    Payload payload;
    payload.color = 0;
    payload.depth = 0;
    dx::HitObject hit = dx::HitObject::TraceRay(gScene, RAY_FLAG_NONE, 0xFF, 0, 1, 0, ray, payload);
    dx::MaybeReorderThread(hit);
    if (hit.IsHit())
    {
        uint table = hit.GetShaderTableIndex();
        float t = hit.GetRayTCurrent();
        payload.depth = table + (uint)t + hit.GetInstanceIndex() + hit.GetInstanceID() + hit.GetPrimitiveIndex() + hit.GetGeometryIndex() + hit.GetHitKind();
    }
    else if (hit.IsMiss())
    {
        payload.color = float4(0, 0, 0, 1);
    }
    dx::HitObject::Invoke(hit, payload);
    gOutput[DispatchRaysIndex().xy] = payload.color;
}
