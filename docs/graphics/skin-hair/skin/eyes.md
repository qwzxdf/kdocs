---
title: Eye Rendering
tags:
  - 描画
---

# Eye Rendering

**目は魂の窓**と言われるように、キャラクターの目が不自然だと、顔全体が死んで見えます。人間の目は、実は**複雑な光学系**で、角膜・虹彩・瞳孔・強膜（白目）・涙の膜と、さまざまな部分が、それぞれ別の光の振る舞いをします。このページでは、目の構造と、ゲームでの再現方法（角膜の屈折、虹彩の見え方、湿った反射、強膜の SSS）を説明します。

!!! tip "ポイント"
    - 目の表面は<strong>透明な角膜</strong>。その奥に<strong>虹彩</strong>（色の部分）と<strong>瞳孔</strong>がある。
    - **角膜の屈折（屈折率 約 1.376）**で、虹彩が**大きく・奥に**見える。**視線を動かすと、見え方が変わる**。
    - **湿った表面の反射**が「生きている目」の鍵。**涙の膜**がつやを作る。
    - **強膜**（白目）は、**SSS**と**血管の透け**で、白一色にしない。
    - **眼窩の影**（まぶたの影）と**環境光の映り込み**が、目の立体感を作る。

## 目の構造

目を、描画の観点で、手前から順に見ます。

最も手前が<strong>涙の膜</strong>です。薄い水の層が目の表面を覆い、つやを作ります。その下が<strong>角膜</strong>（cornea）で、透明なドーム状の膜です。屈折率が約 1.376 で、光を曲げます。角膜の奥には<strong>前房</strong>（水のような液体）があり、さらにその奥に<strong>虹彩</strong>（iris）があります。虹彩は、色のついた円盤で、中央に<strong>瞳孔</strong>（pupil）という穴が開いています。瞳孔は光の量に応じて広がったり狭まったりします。目の白い部分は<strong>強膜</strong>（sclera）で、光をよく散乱する不透明に近い層で、血管が見えます。

この構造のうち、描画で重要なのは、**角膜が透明なドームで、光を屈折させる**ことです。真正面から見ると、虹彩は、角膜の奥に見えます。角膜が凸レンズのように働くので、見える虹彩は、実際より**大きく、わずかに手前に**見えます。

<!-- fig:eye-refraction:begin -->

<svg class="fig illust motion" data-fig="eye-refraction" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-eye-refraction" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">目の屈折: 角膜(透明な丸いドーム)の中を光が曲がり、虹彩が、本当の位置からずれて見える</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">断面。角膜の屈折率 n = 1.376。斜めから見るほど、虹彩の見える位置が、横にずれる</text>
<rect x="30" y="96" width="900" height="330" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 目の断面(上 = 外、下 = 目の中)</text>
<line x1="271.0" y1="232.0" x2="689.0" y2="232.0" stroke="#38bdf8" stroke-width="5"/>
<text x="274.79999999999995" y="224.0" text-anchor="start" style="font-size:12px;font-weight:700;fill:#0284c7">角膜の表面</text>
<rect x="271.0" y="232.0" width="418.0" height="117.8" fill="#bae6fd" fill-opacity="0.35"/>
<line x1="271.0" y1="349.8" x2="689.0" y2="349.8" stroke="#7c3aed" stroke-width="5"/>
<text x="274.79999999999995" y="367.8" text-anchor="start" style="font-size:12px;font-weight:700;fill:#7c3aed">虹彩(色のついた円盤)</text>
<circle cx="480.0" cy="349.8" r="7" fill="#7c3aed"/>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2603;0.2605;1.0000" values="1;1;0;0"/><line x1="480.0" y1="232.0" x2="480.0" y2="118.0" stroke="#2ea043" stroke-width="3.5"/>
<line x1="480.0" y1="232.0" x2="480.0" y2="349.8" stroke="#e5484d" stroke-width="3.5"/>
<line x1="480.0" y1="232.0" x2="480.0" y2="349.8" stroke="#64748b" stroke-width="2.5" stroke-dasharray="6 5"/>
<circle cx="480.0" cy="349.8" r="8" fill="#e9d5ff" stroke="#7c3aed" stroke-width="2"/>
<text x="480.0" y="373.8" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">屈折を無視した位置</text>
<text x="50" y="130" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed">見る角度 0°</text>
<text x="50" y="156" text-anchor="start" style="font-size:14px;font-weight:500;fill:#1f2937">目の中での角度 0.0°(sin θ ÷ 1.376 から)</text>
<text x="50" y="178" text-anchor="start" style="font-size:16px;font-weight:700;fill:#e5484d">虹彩の位置のずれ: 0.00 mm</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2603;0.2605;0.4742;0.4744;1.0000" values="0;0;1;1;0;0"/><line x1="510.23" y1="232.0" x2="549.22" y2="124.88" stroke="#2ea043" stroke-width="3.5"/>
<line x1="510.23" y1="232.0" x2="480.0" y2="349.8" stroke="#e5484d" stroke-width="3.5"/>
<line x1="510.23" y1="232.0" x2="467.35" y2="349.8" stroke="#64748b" stroke-width="2.5" stroke-dasharray="6 5"/>
<circle cx="467.35" cy="349.8" r="8" fill="#e9d5ff" stroke="#7c3aed" stroke-width="2"/>
<text x="467.3535172820183" y="373.8" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">屈折を無視した位置</text>
<text x="50" y="130" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed">見る角度 20°</text>
<text x="50" y="156" text-anchor="start" style="font-size:14px;font-weight:500;fill:#1f2937">目の中での角度 14.4°(sin θ ÷ 1.376 から)</text>
<text x="50" y="178" text-anchor="start" style="font-size:16px;font-weight:700;fill:#e5484d">虹彩の位置のずれ: 0.33 mm</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4742;0.4744;0.6882;0.6884;1.0000" values="0;0;1;1;0;0"/><line x1="542.24" y1="232.0" x2="615.52" y2="144.67" stroke="#2ea043" stroke-width="3.5"/>
<line x1="542.24" y1="232.0" x2="480.0" y2="349.8" stroke="#e5484d" stroke-width="3.5"/>
<line x1="542.24" y1="232.0" x2="443.39" y2="349.8" stroke="#64748b" stroke-width="2.5" stroke-dasharray="6 5"/>
<circle cx="443.39" cy="349.8" r="8" fill="#e9d5ff" stroke="#7c3aed" stroke-width="2"/>
<text x="443.3916257789785" y="373.8" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">屈折を無視した位置</text>
<text x="50" y="130" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed">見る角度 40°</text>
<text x="50" y="156" text-anchor="start" style="font-size:14px;font-weight:500;fill:#1f2937">目の中での角度 27.8°(sin θ ÷ 1.376 から)</text>
<text x="50" y="178" text-anchor="start" style="font-size:16px;font-weight:700;fill:#e5484d">虹彩の位置のずれ: 0.96 mm</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6882;0.6884;1.0000" values="0;0;1;1"/><line x1="575.41" y1="232.0" x2="674.13" y2="175.0" stroke="#2ea043" stroke-width="3.5"/>
<line x1="575.41" y1="232.0" x2="480.0" y2="349.8" stroke="#e5484d" stroke-width="3.5"/>
<line x1="575.41" y1="232.0" x2="371.37" y2="349.8" stroke="#64748b" stroke-width="2.5" stroke-dasharray="6 5"/>
<circle cx="371.37" cy="349.8" r="8" fill="#e9d5ff" stroke="#7c3aed" stroke-width="2"/>
<text x="371.3716666638468" y="373.8" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">屈折を無視した位置</text>
<text x="50" y="130" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed">見る角度 60°</text>
<text x="50" y="156" text-anchor="start" style="font-size:14px;font-weight:500;fill:#1f2937">目の中での角度 39.0°(sin θ ÷ 1.376 から)</text>
<text x="50" y="178" text-anchor="start" style="font-size:16px;font-weight:700;fill:#e5484d">虹彩の位置のずれ: 2.86 mm</text>
</g>
<circle cx="56" cy="400" r="6" fill="#2ea043"/>
<text x="66" y="404" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">外から見る向き</text>
<circle cx="161.8" cy="400" r="6" fill="#e5484d"/>
<text x="171.8" y="404" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">目の中の光(曲がる)</text>
<circle cx="301.8" cy="400" r="6" fill="#64748b"/>
<text x="311.8" y="404" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">曲がらないと考えたとき</text>
<text x="40" y="452" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">ずれの大きさ:</text>
<text x="150" y="456" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0603;0.0605;1.0000" values="1;1;0;0"/></text>
<text x="150" y="456" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0603;0.0605;0.2742;0.2744;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="456" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">33<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2742;0.2744;0.4882;0.4884;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="456" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">96<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4882;0.4884;0.7021;0.7023;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="456" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">286<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.7021;0.7023;1.0000" values="0;0;1;1"/></text>
<text x="205" y="456" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">(0.01 mm 単位)</text>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.8789;0.8791;1.0000" values="0;0;1;1"/><rect x="340" y="436" width="590" height="80" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="356" y="460" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">正面から見ると、ずれ 0。斜めになるほど、虹彩が横にずれて見える</text>
<text x="356" y="483" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">ゲームでは、虹彩のテクスチャ座標を、この分だけずらす(視差オフセット)</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">角膜は透明なドーム。光は、その中で曲がる(屈折)<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0463;0.0465;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">斜めから見ると、虹彩の見える位置が、本当の位置から、横にずれる<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0463;0.0465;0.9021;0.9023;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">このずれを、テクスチャ座標の補正で作ると、目が「奥行きのある丸い物」に見える<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.9021;0.9023;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:eye-refraction:end -->

## 角膜の屈折と虹彩の見え方

目を斜めから見ると、虹彩が**位置ずれ**して見えます。角膜の屈折により、視線が曲がるためです。この屈折を無視して、虹彩を球体の表面に貼ったテクスチャとして描くと、目が「絵」のように平坦に見えます。屈折を正しく扱うと、見る角度によって虹彩の見え方が変わり、**目の奥行き**が出ます。

実装は、**視線の屈折**を計算して、虹彩の平面のどこを見ているかを求めます。

1. 目の表面（角膜）の点 P と、視線ベクトル V から、屈折ベクトル R を計算します（`refract(-V, N, 1 / 1.376)`）。
2. 屈折した視線 R が、**虹彩の平面**と交わる点を求めます。虹彩の平面は、角膜から少し奥（約 2〜3 mm）にあります。
3. 交点の位置を、虹彩のテクスチャの UV に変換して、色を引きます。

```hlsl
float3 EyeIrisColor(float3 world_pos, float3 view_dir, float3 eye_normal, float3 iris_center, float3 iris_forward) {
  float3 refracted = refract(-view_dir, eye_normal, 1.0 / 1.376);
  float distance_to_plane = dot(iris_center - world_pos, iris_forward) / dot(refracted, iris_forward);
  float3 hit = world_pos + refracted * distance_to_plane;
  float2 iris_uv = (float2(dot(hit - iris_center, iris_right), dot(hit - iris_center, iris_up)) / kIrisRadius) * 0.5 + 0.5;
  return iris_tex.Sample(linear_clamp, iris_uv).rgb;
}
```

実用的には、この計算を、簡略化することが多いです。**パララックス マッピング**（UV を視線方向にずらす）で、屈折による虹彩のずれを近似します。簡易な式は、`uv_offset = view_tangent.xy * depth_of_iris` で、これだけでも、見る角度による虹彩の位置のずれが出て、立体感が増します。

## 瞳孔の開閉

瞳孔の大きさは、環境の明るさで変わります。明るい所では小さく、暗い所では大きくなります。感情でも変わります（驚くと開く）。瞳孔の大きさは、虹彩のテクスチャの UV を、中心を基準に拡大縮小して表します。瞳孔の境界は、**ぼかさず**に滑らかに切り替えます。

```hlsl
float2 iris_uv = (uv - 0.5) / pupil_scale + 0.5;
```

`pupil_scale` が小さいと、虹彩の内側（瞳孔の黒い部分）が広がり、大きいと狭まります。環境の明るさ（自動露出の値など）に連動させると、明るいシーンに移ったときに瞳孔が縮む演出ができます。

## 湿った表面の反射

目の生命感は、**表面の反射**で決まります。涙の膜と角膜は、とてもなめらかな球面で、周りの光景を鏡のように映します。**窓の形の映り込み**や、ライトのハイライトが目に入っているかどうかで、顔の印象が大きく変わります。

* **鏡面反射は低粗さ**（0.05 以下）で、ハイライトを鋭くします。
* **F0 は約 0.025**（水に近い）。斜めから見ると強く映ります。
* **環境の反射**は、環境マップ（IBL）と、SSR や平面反射で映します。目は小さい物体なので、ふつうは環境マップで十分です。
* ライトの**ハイライトの位置**は、アーティストが調整できるように、目の専用ライトを足すこともあります（キャッチライト）。

重要な注意は、**角膜のドームは、虹彩の上に浮いている**ことです。目の描画は、虹彩を描く面と、角膜を描く面（反射を担当する透明な面）の、**2 枚のメッシュ**に分けると、扱いやすくなります。虹彩の面は不透明で拡散、角膜の面は透明で鏡面反射だけを持ちます。

## 強膜（白目）

白目は、真っ白ではありません。**強膜**は、SSS が強く、血管が透けて見える、わずかに赤みがかった不透明な層です。白目の色を、アルベドの白一色にすると、目が不自然に硬く見えます。

* アルベドは、わずかに**クリームがかった白**にします。
* **血管**のテクスチャを重ねます。目頭と目尻に多く、中央は少なくします。疲れた目や、感情が高ぶったときに、血管を濃くする演出もできます。
* **SSS**で、まぶたの縁や、涙丘（目頭の赤い部分）の周りに、柔らかな赤みを出します。
* **眼窩の影**で、目の周りが暗くなります。AO や、まぶたの落とす影で表します。

## まぶたと涙

目の周りの、まぶたの縁には、**涙の溜まり**（涙液メニスカス）があります。まぶたと眼球の境目に、細く光る水の線が見えます。この線が、目を濡れて見せる、重要なディテールです。これは、まぶたの縁に沿って、**半透明の細いメッシュ**を置き、鏡面反射だけを描く方法で表せます。

**まばたき**は、まぶたのメッシュの動きだけでなく、眼球の濡れ方にも影響します。まぶたが目を覆うとき、目の表面が一瞬、新しい涙で濡れ直されるので、反射が強まります。目を開けてしばらくすると、涙が蒸発して、反射が弱まる（乾く）演出も、リアリティを増します。

## 目の周りの SSS の処理

目の周りの皮膚（まぶた）は、とても薄く、透光性が高いので、SSS の影響が大きい部位です。薄いまぶたの裏側から、目の光が透けて見えます。まぶたの SSS を強める（マスクで強度を上げる）ことと、[Thin Translucency](thin-translucency.md) の透過を足すことで、自然な見た目になります。

画面空間の SSS を使うときは、**目の部分をステンシルから除外する**ことに注意します。角膜や虹彩に SSS のぼかしを掛けると、虹彩の模様がぼけます。目は、肌のぼかしの対象外にします。

## よくあるミス

??? failure "目が平面的で、絵のように見える"
    **角膜の屈折（またはパララックス）**で、虹彩を奥に見せる。

??? failure "目に反射がなく、死んだ目に見える"
    **低粗さの鏡面**と**環境の映り込み**を足す。**キャッチライト**を入れる。

??? failure "虹彩の模様が、SSS のぼかしでぼける"
    目を、**SSS の対象（ステンシル）から外す**。

??? failure "白目が真っ白で、のっぺりしている"
    **血管のテクスチャ**と**クリーム色のアルベド**、**眼窩の影**を足す。

??? failure "瞳孔の大きさが一定で、明暗の変化に反応しない"
    **環境の明るさ**に応じて、`pupil_scale` を変える。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 目は<strong>角膜（透明なドーム）／虹彩／瞳孔／強膜／涙の膜</strong>の組み合わせ
    - [x] **角膜の屈折（n = 1.376）**で虹彩の見え方が変わる。**簡易にはパララックス**
    - [x] **湿った低粗さの反射**で目が生きる
    - [x] **白目は血管と SSS**。**目は肌の SSS から除外**する

## 参考

- Jimenez, Danvoye, "Next Generation Character Rendering"（GDC 2013）
- Francois, Gautron, Breton, Bouatouch, "Image-based Modeling of the Human Eye"（IEEE TVCG, 2009）

## 関連ページ

- [Skin Overview](index.md)
- [Thin Translucency](thin-translucency.md)
- [Skin Specular](specular.md)
- [Refraction](../../translucency/refraction/index.md)
