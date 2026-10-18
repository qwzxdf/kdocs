---
title: データ指向設計
tags:
  - 設計
  - パフォーマンス
---

# データ指向設計

**データ指向設計**（Data-Oriented Design、DOD）は、<strong>「オブジェクトが何をするか」ではなく「データがどう並び、どう流れるか」から設計する</strong>考え方です。普通のオブジェクト指向では「敵というオブジェクトが自分を更新する」と考えますが、データ指向では「全部の敵の位置の配列に、全部の敵の速度を足す」と考えます。CPU のキャッシュを無駄なく使えるので、大量のオブジェクトを扱うゲームで何倍も速くなることがあります。[ECS](ecs.md) はこの考え方から生まれた設計です。

!!! tip "ポイント"
    - **同じ処理をたくさんのデータに対して行う**なら、そのデータを連続した配列に並べる。
    - 1 つずつ仮想関数を呼ぶより、**種類ごとにまとめて**普通の関数で処理する。
    - 一緒に使うデータは近くに、使わないデータは別の場所に（ホット / コールドの分離）。
    - オブジェクトが数百程度なら気にしなくていい。**測ってから**適用する。

!!! info "このページを読む前に"
    [キャッシュ効率](../../basics/cache.md) を先に読んでください。

## オブジェクト指向とデータ指向

=== "オブジェクト指向的"

    ```cpp
    class GameObject {
     public:
      virtual void Update(float dt) = 0;  // 1 つずつ仮想関数
    };

    std::vector<std::unique_ptr<GameObject>> objects;  // 本体はバラバラ
    for (auto& obj : objects) {
      obj->Update(dt);
    }
    ```

=== "データ指向的"

    ```cpp
    struct Particles {
      std::vector<float> x, y;    // 位置だけが並んだ配列
      std::vector<float> vx, vy;  // 速度だけが並んだ配列
    };

    void UpdatePositions(Particles& p, float dt) {  // 全部まとめて 1 回で
      for (std::size_t i = 0; i < p.x.size(); ++i) {
        p.x[i] += p.vx[i] * dt;
        p.y[i] += p.vy[i] * dt;
      }
    }
    ```

| | オブジェクト指向的 | データ指向的 |
| --- | --- | --- |
| 考え方の中心 | 1 つのオブジェクト | データの配列と、それへの処理 |
| メモリ | オブジェクトごとにバラバラ | 種類ごとに連続 |
| 処理の呼び方 | 1 つずつ（仮想関数） | まとめて（普通のループ） |
| 得意 | 種類が多く、数が少ないもの（UI、ボス） | 種類が少なく、数が多いもの（弾、パーティクル、群衆） |

<!-- fig:aos-vs-soa:begin -->

<svg class="fig illust motion" data-fig="aos-vs-soa" viewBox="0 0 780 460" role="img"><rect x="0" y="0" width="780" height="460" rx="14" fill="#ffffff"/>
<defs><marker id="arr-aos-vs-soa" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">x だけ読むとき: 構造体の配列(AoS)は 4 ライン、成分ごとの配列(SoA)は 1 ライン</text>
<text x="40" y="80" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d">AoS（1 体ずつ x y z hp が並ぶ）</text>
<text x="140" y="113" text-anchor="end" style="font-size:11px;font-weight:700;fill:#64748b">ライン 1</text>
<rect x="150" y="95" width="24" height="28" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<text x="162.0" y="114" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">x</text>
<rect x="176" y="95" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="188.0" y="114" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">y</text>
<rect x="202" y="95" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="214.0" y="114" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">z</text>
<rect x="228" y="95" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="240.0" y="114" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">hp</text>
<rect x="254" y="95" width="24" height="28" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<text x="266.0" y="114" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">x</text>
<rect x="280" y="95" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="292.0" y="114" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">y</text>
<rect x="306" y="95" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="318.0" y="114" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">z</text>
<rect x="332" y="95" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="344.0" y="114" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">hp</text>
<rect x="358" y="95" width="24" height="28" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<text x="370.0" y="114" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">x</text>
<rect x="384" y="95" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="396.0" y="114" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">y</text>
<rect x="410" y="95" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="422.0" y="114" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">z</text>
<rect x="436" y="95" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="448.0" y="114" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">hp</text>
<rect x="462" y="95" width="24" height="28" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<text x="474.0" y="114" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">x</text>
<rect x="488" y="95" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="500.0" y="114" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">y</text>
<rect x="514" y="95" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="526.0" y="114" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">z</text>
<rect x="540" y="95" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="552.0" y="114" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">hp</text>
<rect x="147" y="93" width="420" height="32" fill="none" stroke="#e5aa28" stroke-width="4" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="0;0;1;1"/></rect>
<text x="140" y="147" text-anchor="end" style="font-size:11px;font-weight:700;fill:#64748b">ライン 2</text>
<rect x="150" y="129" width="24" height="28" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<text x="162.0" y="148" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">x</text>
<rect x="176" y="129" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="188.0" y="148" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">y</text>
<rect x="202" y="129" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="214.0" y="148" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">z</text>
<rect x="228" y="129" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="240.0" y="148" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">hp</text>
<rect x="254" y="129" width="24" height="28" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<text x="266.0" y="148" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">x</text>
<rect x="280" y="129" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="292.0" y="148" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">y</text>
<rect x="306" y="129" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="318.0" y="148" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">z</text>
<rect x="332" y="129" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="344.0" y="148" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">hp</text>
<rect x="358" y="129" width="24" height="28" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<text x="370.0" y="148" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">x</text>
<rect x="384" y="129" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="396.0" y="148" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">y</text>
<rect x="410" y="129" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="422.0" y="148" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">z</text>
<rect x="436" y="129" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="448.0" y="148" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">hp</text>
<rect x="462" y="129" width="24" height="28" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<text x="474.0" y="148" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">x</text>
<rect x="488" y="129" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="500.0" y="148" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">y</text>
<rect x="514" y="129" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="526.0" y="148" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">z</text>
<rect x="540" y="129" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="552.0" y="148" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">hp</text>
<rect x="147" y="127" width="420" height="32" fill="none" stroke="#e5aa28" stroke-width="4" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1417;0.1419;1.0000" values="0;0;1;1"/></rect>
<text x="140" y="181" text-anchor="end" style="font-size:11px;font-weight:700;fill:#64748b">ライン 3</text>
<rect x="150" y="163" width="24" height="28" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<text x="162.0" y="182" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">x</text>
<rect x="176" y="163" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="188.0" y="182" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">y</text>
<rect x="202" y="163" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="214.0" y="182" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">z</text>
<rect x="228" y="163" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="240.0" y="182" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">hp</text>
<rect x="254" y="163" width="24" height="28" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<text x="266.0" y="182" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">x</text>
<rect x="280" y="163" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="292.0" y="182" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">y</text>
<rect x="306" y="163" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="318.0" y="182" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">z</text>
<rect x="332" y="163" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="344.0" y="182" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">hp</text>
<rect x="358" y="163" width="24" height="28" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<text x="370.0" y="182" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">x</text>
<rect x="384" y="163" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="396.0" y="182" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">y</text>
<rect x="410" y="163" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="422.0" y="182" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">z</text>
<rect x="436" y="163" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="448.0" y="182" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">hp</text>
<rect x="462" y="163" width="24" height="28" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<text x="474.0" y="182" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">x</text>
<rect x="488" y="163" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="500.0" y="182" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">y</text>
<rect x="514" y="163" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="526.0" y="182" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">z</text>
<rect x="540" y="163" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="552.0" y="182" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">hp</text>
<rect x="147" y="161" width="420" height="32" fill="none" stroke="#e5aa28" stroke-width="4" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2191;0.2194;1.0000" values="0;0;1;1"/></rect>
<text x="140" y="215" text-anchor="end" style="font-size:11px;font-weight:700;fill:#64748b">ライン 4</text>
<rect x="150" y="197" width="24" height="28" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<text x="162.0" y="216" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">x</text>
<rect x="176" y="197" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="188.0" y="216" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">y</text>
<rect x="202" y="197" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="214.0" y="216" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">z</text>
<rect x="228" y="197" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="240.0" y="216" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">hp</text>
<rect x="254" y="197" width="24" height="28" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<text x="266.0" y="216" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">x</text>
<rect x="280" y="197" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="292.0" y="216" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">y</text>
<rect x="306" y="197" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="318.0" y="216" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">z</text>
<rect x="332" y="197" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="344.0" y="216" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">hp</text>
<rect x="358" y="197" width="24" height="28" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<text x="370.0" y="216" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">x</text>
<rect x="384" y="197" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="396.0" y="216" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">y</text>
<rect x="410" y="197" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="422.0" y="216" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">z</text>
<rect x="436" y="197" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="448.0" y="216" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">hp</text>
<rect x="462" y="197" width="24" height="28" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<text x="474.0" y="216" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">x</text>
<rect x="488" y="197" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="500.0" y="216" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">y</text>
<rect x="514" y="197" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="526.0" y="216" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">z</text>
<rect x="540" y="197" width="24" height="28" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="552.0" y="216" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#64748b">hp</text>
<rect x="147" y="195" width="420" height="32" fill="none" stroke="#e5aa28" stroke-width="4" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2965;0.2968;1.0000" values="0;0;1;1"/></rect>
<text x="40" y="270" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">SoA（x だけ、y だけ…と別の配列）</text>
<text x="140" y="288" text-anchor="end" style="font-size:11px;font-weight:700;fill:#64748b">ライン 1</text>
<rect x="150" y="276" width="24" height="28" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<text x="162.0" y="295" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">x</text>
<rect x="176" y="276" width="24" height="28" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<text x="188.0" y="295" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">x</text>
<rect x="202" y="276" width="24" height="28" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<text x="214.0" y="295" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">x</text>
<rect x="228" y="276" width="24" height="28" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<text x="240.0" y="295" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">x</text>
<rect x="254" y="276" width="24" height="28" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<text x="266.0" y="295" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">x</text>
<rect x="280" y="276" width="24" height="28" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<text x="292.0" y="295" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">x</text>
<rect x="306" y="276" width="24" height="28" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<text x="318.0" y="295" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">x</text>
<rect x="332" y="276" width="24" height="28" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<text x="344.0" y="295" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">x</text>
<rect x="358" y="276" width="24" height="28" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<text x="370.0" y="295" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">x</text>
<rect x="384" y="276" width="24" height="28" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<text x="396.0" y="295" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">x</text>
<rect x="410" y="276" width="24" height="28" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<text x="422.0" y="295" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">x</text>
<rect x="436" y="276" width="24" height="28" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<text x="448.0" y="295" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">x</text>
<rect x="462" y="276" width="24" height="28" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<text x="474.0" y="295" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">x</text>
<rect x="488" y="276" width="24" height="28" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<text x="500.0" y="295" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">x</text>
<rect x="514" y="276" width="24" height="28" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<text x="526.0" y="295" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">x</text>
<rect x="540" y="276" width="24" height="28" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<text x="552.0" y="295" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">x</text>
<rect x="147" y="272" width="420" height="32" fill="none" stroke="#e5aa28" stroke-width="4" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4514;0.4516;1.0000" values="0;0;1;1"/></rect>
<text x="390" y="340" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">16 体 × 4 成分 × 4 バイト = 256 バイト = 4 ライン。x だけなら 64 バイト = 1 ライン</text>
<text x="390" y="390" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">青 = 読みたい x。1 ライン(橙の枠) = 一度に運ばれる 64 バイト<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="1;1;0;0"/></text>
<text x="390" y="390" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">AoS: 4 ライン運んで、使うのは 4 分の 1(25%)<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3868;0.3871;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="390" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">SoA: 1 ライン運んで、全部使う(100%)。データ指向が速い理由<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3868;0.3871;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:aos-vs-soa:end -->

## 実践のテクニック

### 1. 種類ごとに配列を分ける

```cpp
#include <print>
#include <vector>

struct Bullet {
  float x;
  float y;
  float vy;
};
struct Missile {
  float x;
  float y;
  float speed;
  int target;
};

struct Projectiles {
  std::vector<Bullet> bullets;    // 種類ごとに vector
  std::vector<Missile> missiles;
};

void Update(Projectiles& p, float dt) {
  for (auto& b : p.bullets) {     // 仮想関数を使わず、型ごとにまとめて回す
    b.y += b.vy * dt;
  }
  for (auto& m : p.missiles) {
    m.x += m.speed * dt;
  }
}

int main() {
  Projectiles p;
  p.bullets.push_back({0, 0, 10});
  p.missiles.push_back({0, 0, 5, 1});
  Update(p, 0.5f);
  std::println("{} {}", p.bullets[0].y, p.missiles[0].x);
}
```

```text title="実行結果"
5 2.5
```

### 2. ホットとコールドを分ける

```cpp
struct EnemyMotion {  // 毎フレーム使う（ホット）
  float x, y, vx, vy;
};
struct EnemyInfo {    // たまにしか使わない（コールド）
  std::string name;
  std::string description;
  int drop_table_id;
};

std::vector<EnemyMotion> motions;  // 毎フレームはこれだけを回す
std::vector<EnemyInfo> infos;      // 同じ添字で対応
```

### 3. 「生きているもの」だけを詰めておく

`if (!alive) continue;` で飛ばしながら回すより、生きているものだけを配列の前に詰めておく（死んだら swap して pop_back）ほうが、分岐もなくなり速くなります（[vector](../../stl/containers/vector.md#順番がどうでもいいならswap-して-pop_back)）。

### 4. まとめて処理する（バッチ）

| 1 つずつ | まとめて |
| --- | --- |
| 敵 1 体ごとに `DrawSprite()` | 同じ画像の敵を全部集めて 1 回で描く |
| 弾 1 発ごとに当たり判定の関数を呼ぶ | 全弾の位置の配列を一度に調べる |
| オブジェクトごとにファイルを読む | 起動時に全部まとめて読む |

## いつ使うか

| 使う | 使わない |
| --- | --- |
| 弾、パーティクル、群衆など数千〜数万 | プレイヤー、ボス、UI など数が少ないもの |
| 毎フレーム同じ処理をする | たまにしか動かない処理 |
| 実際に測って遅かった | 遅いかどうか分からない（まず測る） |

データ指向とオブジェクト指向は「どちらか一方」ではなく、**数が多くて重いところだけデータ指向にする**のが現実的です。

## よくある失敗

??? failure "全部をデータ指向で書こうとする"
    数が少ないものまで配列の構造体にすると、コードが読みにくくなるだけで速くもなりません。

??? failure "測らずに最適化する"
    遅い原因は描画やファイル読み込みだった、ということもよくあります。プロファイラで測ってから直します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 数が多いものは、データを配列に並べてまとめて処理する
    - [x] 種類ごとに分ける、ホットとコールドを分ける
    - [x] 数が少ないものはオブジェクト指向のままでいい
    - [x] 測ってから適用する

## 関連ページ

- [キャッシュ効率](../../basics/cache.md)
- [ECS](ecs.md)
- [Data-Oriented Design（Richard Fabian）](https://www.dataorienteddesign.com/dodbook/)
- [メモリとキャッシュ（最適化）](../../optimize/memory-cache.md)
- [計測（最適化）](../../optimize/measure.md)
