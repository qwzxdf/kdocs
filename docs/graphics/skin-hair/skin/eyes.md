---
title: Eye Rendering
tags:
  - 描画
---

# Eye Rendering

<strong>目は魂の窓</strong>と言われるようにキャラクターの目が不自然だと顔全体が死んで見えます。人間の目は実は複雑な光学系で、角膜・虹彩・瞳孔・強膜（白目）・涙の膜とさまざまな部分がそれぞれ別の光の振る舞いをします。このページでは目の構造とゲームでの再現方法（角膜の屈折、虹彩の見え方、湿った反射、強膜の SSS）を説明します。

!!! tip "ポイント"
    - 目の表面は<strong>透明な角膜</strong>。その奥に<strong>虹彩</strong>（色の部分）と瞳孔がある。
    - 角膜の屈折（屈折率 約 1.376）で、虹彩が大きく・奥に見える。視線を動かすと見え方が変わる。
    - 湿った表面の反射が「生きている目」の鍵。涙の膜がつやを作る。
    - 強膜（白目）は SSSと血管の透けで、白一色にしない。
    - 眼窩の影（まぶたの影）と環境光の映り込みが、目の立体感を作る。

!!! info "このページを読む前に"
    - [Skin Overview](index.md)（このセクション全体の地図と、読む順番）

## 目の構造

目を描画の観点で手前から順に見ます。

最も手前が<strong>涙の膜</strong>です。薄い水の層が目の表面を覆いつやを作ります。その下が角膜（cornea）で、透明なドーム状の膜です。屈折率が約 1.376 で光を曲げます。角膜の奥には前房（水のような液体）がありさらにその奥に虹彩（iris）があります。虹彩は色のついた円盤で中央に瞳孔（pupil）という穴が開いています。瞳孔は光の量に応じて広がったり狭まったりします。目の白い部分は強膜（sclera）で、光をよく散乱する不透明に近い層で、血管が見えます。

この構造のうち描画で重要なのは、角膜が透明なドームで光を屈折させることです。真正面から見ると虹彩は角膜の奥に見えます。角膜が凸レンズのように働くので、見える虹彩は実際より大きく、わずかに手前に見えます。

<!-- fig:eye-refraction:begin -->

<svg class="fig illust motion" data-fig="eye-refraction" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-eye-refraction" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">目の屈折: 角膜(透明な丸いドーム)の中を光が曲がり、虹彩が本当の位置からずれて見える</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">断面。角膜の屈折率 n = 1.376。斜めから見るほど、虹彩の見える位置が横にずれる</text>
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
<text x="356" y="483" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">ゲームでは、虹彩のテクスチャ座標をこの分だけずらす(視差オフセット)</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">角膜は透明なドーム。光は、その中で曲がる(屈折)<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0463;0.0465;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">斜めから見ると、虹彩の見える位置が本当の位置から、横にずれる<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0463;0.0465;0.9021;0.9023;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">このずれをテクスチャ座標の補正で作ると、目が「奥行きのある丸い物」に見える<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.9021;0.9023;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:eye-refraction:end -->

## 角膜の屈折と虹彩の見え方

目を斜めから見ると虹彩が<strong>位置ずれ</strong>して見えます。角膜の屈折により視線が曲がるためです。この屈折を無視して虹彩を球体の表面に貼ったテクスチャとして描くと目が「絵」のように平坦に見えます。屈折を正しく扱うと見る角度によって虹彩の見え方が変わり 目の奥行きが出ます。

実装は 視線の屈折を計算して、虹彩の平面のどこを見ているかを求めます。

1. 目の表面（角膜）の点 P と視線ベクトル V から、屈折ベクトル R を計算します（`refract(-V, N, 1 / 1.376)`）。
2. 屈折した視線 R が虹彩の平面と交わる点を求めます。虹彩の平面は角膜から少し奥（約 2〜3 mm）にあります。
3. 交点の位置を虹彩のテクスチャの UV に変換して、色を引きます。

```hlsl
float3 EyeIrisColor(float3 world_pos, float3 view_dir, float3 eye_normal, float3 iris_center, float3 iris_forward) {
  float3 refracted = refract(-view_dir, eye_normal, 1.0 / 1.376);
  float distance_to_plane = dot(iris_center - world_pos, iris_forward) / dot(refracted, iris_forward);
  float3 hit = world_pos + refracted * distance_to_plane;
  float2 iris_uv = (float2(dot(hit - iris_center, iris_right), dot(hit - iris_center, iris_up)) / kIrisRadius) * 0.5 + 0.5;
  return iris_tex.Sample(linear_clamp, iris_uv).rgb;
}
```

実用的にはこの計算を簡略化することが多いです。パララックス マッピング（UV を視線方向にずらす）で、屈折による虹彩のずれを近似します。簡易な式は `uv_offset = view_tangent.xy * depth_of_iris` でこれだけでも見る角度による虹彩の位置のずれが出て、立体感が増します。

## 瞳孔の開閉

瞳孔の大きさは環境の明るさで変わります。明るい所では小さく暗い所では大きくなります。感情でも変わります（驚くと開く）。瞳孔の大きさは虹彩のテクスチャの UV を中心を基準に拡大縮小して表します。瞳孔の境界は <strong>ぼかさず</strong>に滑らかに切り替えます。

```hlsl
float2 iris_uv = (uv - 0.5) / pupil_scale + 0.5;
```

`pupil_scale` が小さいと虹彩の内側（瞳孔の黒い部分）が広がり大きいと狭まります。環境の明るさ（自動露出の値など）に連動させると、明るいシーンに移ったときに瞳孔が縮む演出ができます。

## 湿った表面の反射

目の生命感は <strong>表面の反射</strong>で決まります。涙の膜と角膜はとてもなめらかな球面で、周りの光景を鏡のように映します。窓の形の映り込みやライトのハイライトが目に入っているかどうかで、顔の印象が大きく変わります。

* 鏡面反射は低粗さ（0.05 以下）で、ハイライトを鋭くします。
* F0 は約 0.025（水に近い）。斜めから見ると強く映ります。
* 環境の反射は環境マップ（IBL）と SSR や平面反射で映します。目は小さい物体なのでふつうは環境マップで十分です。
* ライトのハイライトの位置はアーティストが調整できるように目の専用ライトを足すこともあります（キャッチライト）。

重要な注意は 角膜のドームは虹彩の上に浮いていることです。目の描画は虹彩を描く面と角膜を描く面（反射を担当する透明な面）の 2 枚のメッシュに分けると、扱いやすくなります。虹彩の面は不透明で拡散、角膜の面は透明で鏡面反射だけを持ちます。

## 強膜（白目）

白目は真っ白ではありません。<strong>強膜</strong>は SSS が強く血管が透けて見えるわずかに赤みがかった不透明な層です。白目の色をアルベドの白一色にすると、目が不自然に硬く見えます。

* アルベドはわずかにクリームがかった白にします。
* 血管のテクスチャを重ねます。目頭と目尻に多く中央は少なくします。疲れた目や感情が高ぶったときに血管を濃くする演出もできます。
* SSSでまぶたの縁や涙丘（目頭の赤い部分）の周りに柔らかな赤みを出します。
* 眼窩の影で目の周りが暗くなります。AO やまぶたの落とす影で表します。

## まぶたと涙

目の周りのまぶたの縁には <strong>涙の溜まり</strong>（涙液メニスカス）があります。まぶたと眼球の境目に細く光る水の線が見えます。この線が目を濡れて見せる重要なディテールです。これはまぶたの縁に沿って 半透明の細いメッシュを置き鏡面反射だけを描く方法で表せます。

まばたきはまぶたのメッシュの動きだけでなく、眼球の濡れ方にも影響します。まぶたが目を覆うとき目の表面が一瞬、新しい涙で濡れ直されるので反射が強まります。目を開けてしばらくすると涙が蒸発して、反射が弱まる（乾く）演出もリアリティを増します。

## 目の周りの SSS の処理

目の周りの皮膚（まぶた）はとても薄く、透光性が高いので SSS の影響が大きい部位です。薄いまぶたの裏側から目の光が透けて見えます。まぶたの SSS を強める（マスクで強度を上げる）ことと[Thin Translucency](thin-translucency.md) の透過を足すことで、自然な見た目になります。

画面空間の SSS を使うときは <strong>目の部分をステンシルから除外する</strong>ことに注意します。角膜や虹彩に SSS のぼかしを掛けると、虹彩の模様がぼけます。目は肌のぼかしの対象外にします。

## よくあるミス

??? failure "目が平面的で、絵のように見える"
    <strong>角膜の屈折（またはパララックス）</strong>で、虹彩を奥に見せる。

??? failure "目に反射がなく、死んだ目に見える"
    低粗さの鏡面と環境の映り込みを足す。キャッチライトを入れる。

??? failure "虹彩の模様が SSS のぼかしでぼける"
    目を SSS の対象（ステンシル）から外す。

??? failure "白目が真っ白で、のっぺりしている"
    血管のテクスチャとクリーム色のアルベド、眼窩の影を足す。

??? failure "瞳孔の大きさが一定で、明暗の変化に反応しない"
    環境の明るさに応じて、`pupil_scale` を変える。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 目は<strong>角膜（透明なドーム）／虹彩／瞳孔／強膜／涙の膜</strong>の組み合わせ
    - [x] 角膜の屈折（n = 1.376）で虹彩の見え方が変わる。簡易にはパララックス
    - [x] 湿った低粗さの反射で目が生きる
    - [x] 白目は血管と SSS。目は肌の SSS から除外する

## 参考

- Jimenez, Danvoye, "Next Generation Character Rendering"（GDC 2013）
- Francois, Gautron, Breton, Bouatouch, "Image-based Modeling of the Human Eye"（IEEE TVCG, 2009）

## 関連ページ

- [Skin Overview](index.md)
- [Thin Translucency](thin-translucency.md)
- [Skin Specular](specular.md)
- [Refraction](../../translucency/refraction/index.md)
