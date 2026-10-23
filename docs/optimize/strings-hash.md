---
title: 文字列とハッシュの最適化
tags:
  - 最適化
---

# 文字列とハッシュの最適化

ゲームの中には、**文字列**がたくさん出てきます（アセット名、イベント名、オブジェクト名、ログ）。`std::string` は便利ですが、確保・コピー・比較が意外と重いのです。そこで実行中は文字列を使わず、整数（ID・ハッシュ値）で扱うのがゲームの定石です。このページは、`std::string` のコスト、`string_view`、文字列のハッシュ化、文字列 ID（インターン）、`unordered_map` での検索をまとめます。

!!! tip "ポイント"
    - <strong>`std::string` は、作る・コピーする・比べるのが整数より何十倍も遅い</strong>。<strong>毎フレーム使わない</strong>。
    - 引数は`std::string_view`（コピーなし・確保なし）。ただし、`\0` 終端でない点に注意。
    - 名前はハッシュ値（整数）にして、実行中は整数で比べる。コンパイル時にハッシュできる（`constexpr`）。
    - ハッシュは衝突する。64 ビットにして、開発中は衝突を検出する。
    - `unordered_map<std::string, T>` の検索で、`std::string` を作らない（C++20 の透過的検索）。
    - デバッグ用の名前は、製品ビルドで消せるようにする。

## std::string のコスト

| 操作 | コスト |
| --- | --- |
| <strong>作成（長い文字列）</strong> | ヒープ確保 + コピー |
| 作成（短い文字列） | SSO で確保なし（約 15 文字以下）。それでもコピーは必要 |
| 比較（`==`） | 長さ + 中身を、1 文字ずつ。長いほど遅い。整数の比較は、1 命令 |
| 連結（`+`） | 一時オブジェクトの作成・確保・コピー |
| `std::map<std::string, T>` | 比較が木の深さぶん。しかも文字列比較 |
| `std::unordered_map<std::string, T>` | ハッシュ計算（文字列の長さ）+ 比較 |

整数の `==` は 1 サイクル、文字列の `==` は数十〜数百サイクルが、目安です。

## string_view

**`std::string_view`** は、文字列の先頭と長さだけを持つ、読み取り専用の窓です。確保もコピーもしません。

```cpp
void Log(std::string_view message);

Log("hello");
Log(name);
Log(std::string("temp"));
```

| 項目 | 説明 |
| --- | --- |
| 使いどころ | 関数の引数。`const std::string&` より、リテラルでも確保しない |
| 寿命に注意 | 元の文字列が消えるとぶら下がる。保存しない（メンバに持たない） |
| `\0` 終端ではない | C の API（`printf`、Windows API）に渡すとき、`\0` がないかもしれない。`std::string` に変換するか、長さ付きの API を使う |
| 一時 `std::string` の `string_view` | `std::string_view sv = std::string("x");` はすぐ消えてぶら下がる |

詳しくは、[std::string_view](../stl/utilities/string_view.md) を見てください。

## 文字列をハッシュにする

**文字列を整数（ハッシュ値）に変換**して、実行中は整数だけで比べます。

```cpp
constexpr uint64_t Fnv1a(std::string_view s) {
  uint64_t hash = 14695981039346656037ull;
  for (char c : s) {
    hash ^= static_cast<uint8_t>(c);
    hash *= 1099511628211ull;
  }
  return hash;
}

constexpr uint64_t kPlayerHash = Fnv1a("player");
```

| 特徴 | 説明 |
| --- | --- |
| `constexpr` | コンパイル時に計算できる。`switch` の `case` にも使える |
| FNV-1a | 単純で速い。ゲームの名前によく使う（暗号用ではない） |
| 実行時のコスト | ハッシュ計算（文字列の長さ）が、1 回だけ。以後は整数 |

### 使い方

```cpp
struct StringId {
  uint64_t value;
  constexpr explicit StringId(std::string_view s) : value(Fnv1a(s)) {}
  constexpr bool operator==(const StringId&) const = default;
};

constexpr StringId kJump("jump");

void OnEvent(StringId id) {
  if (id == kJump) { ... }
}
```

型にすることで普通の整数と間違えないようにします。

### 注意：衝突

異なる文字列が同じハッシュ値になることを、衝突といいます。

| ビット数 | 衝突の起こりやすさ |
| --- | --- |
| 32 ビット | 数万個の名前で衝突の可能性が出る（誕生日のパラドックス） |
| 64 ビット | 数十億個でもほぼ起きない |

| 対策 | 説明 |
| --- | --- |
| 64 ビットにする | 最も簡単 |
| 開発中は衝突を検出する | 登録時に同じハッシュで異なる文字列がないか、チェック（`assert`） |
| ハッシュだけに頼らない | 重要な所では元の文字列も比べる |

!!! warning "標準の `std::hash` は実装依存"
    `std::hash<std::string>` の値は、実装・実行ごとに変わるかもしれません。ファイルに保存したり、ネットワークで送るハッシュには、自作の固定アルゴリズム（FNV-1a など）を使います（[std::hash](../stl/utilities/hash.md)）。

## 文字列 ID とインターン

**同じ文字列を、1 つだけ保存**して、ID（番号）で参照する仕組みが文字列のインターンです。

```cpp
class StringTable {
 public:
  uint32_t Intern(std::string_view s) {
    auto it = map_.find(s);
    if (it != map_.end()) return it->second;
    uint32_t id = static_cast<uint32_t>(strings_.size());
    strings_.emplace_back(s);
    map_.emplace(strings_.back(), id);
    return id;
  }

  const std::string& Get(uint32_t id) const { return strings_[id]; }

 private:
  std::deque<std::string> strings_;
  std::unordered_map<std::string_view, uint32_t> map_;
};
```

| 項目 | ハッシュ | インターン |
| --- | --- | --- |
| 値 | ハッシュ値（64 ビット） | 連番（32 ビットで十分） |
| 衝突 | ある（まれに） | ない |
| 逆引き（ID → 文字列） | できない（別途テーブルが必要） | できる（デバッグに便利） |
| コンパイル時の計算 | できる | できない（実行時にテーブルに登録） |
| 保存・通信 | 固定アルゴリズムなら、そのまま使える | ID が実行ごとに変わる。保存には向かない |

ハッシュ + 開発用の逆引きテーブル（デバッグビルドだけ）が、実用的です。

## unordered_map の検索

```cpp
std::unordered_map<std::string, int> table;

table.find("player");
```

**`find("player")` は、`std::string` の一時オブジェクトを作る**ので、確保が起きることがあります。

### 透過的検索（C++20）

```cpp
struct StringHash {
  using is_transparent = void;
  size_t operator()(std::string_view s) const { return std::hash<std::string_view>{}(s); }
};

std::unordered_map<std::string, int, StringHash, std::equal_to<>> table;

table.find(std::string_view("player"));
```

`is_transparent` を付けたハッシュと、`std::equal_to<>`を使うと、**`string_view` や `const char*` のまま検索できます。一時 `std::string` が作られません**。

### そもそもキーを整数にする

```cpp
std::unordered_map<StringId, int, StringIdHash> table;
```

ID をキーにすれば、ハッシュ計算・比較が軽くなります。文字列のキーは、ロード時に ID にして、実行中は ID だけにします。

## 数値と文字列の変換

| やりたいこと | 速い方法 |
| --- | --- |
| **数値 → 文字列** | `std::to_chars`（バッファに書く。確保なし） |
| 文字列 → 数値 | `std::from_chars`（ロケール非依存・例外なし・速い） |
| 書式付きの文字列 | `std::format_to` / `std::format_to_n`（固定バッファへ） |

```cpp
char buffer[32];
auto [end, error] = std::to_chars(buffer, buffer + sizeof(buffer), value);
std::string_view result(buffer, end - buffer);
```

`std::to_string`、`std::stoi`、`sprintf`、`stringstream` は、ロケールの処理・確保があり、遅いです。

## 文字列を避ける設計

| 場面 | 文字列を使わない方法 |
| --- | --- |
| **イベント名** | `enum class`、`StringId`（ハッシュ） |
| アセットのパス | ロード時にハッシュ化 → ハンドル（[ハンドル](../engine/handle.md)） |
| オブジェクト名 | エディター・デバッグ用だけ。実行は ID |
| アニメーション名・状態名 | `enum`、またはロード時に番号へ変換 |
| ログ | 書式文字列はログのレベルを確認してから作る |
| 設定のキー | ロード時に解決して、実行中はキーで検索しない |

文字列の比較が必要なのは、「人間が読む・書く」境界だけです（ファイル、UI、コンソール）。中に入れたら、すぐ ID にします。

## デバッグ名を製品で消す

```cpp
struct Entity {
  StringId id;
#ifdef _DEBUG
  std::string debug_name;
#endif
};
```

**デバッグ用の名前**は、開発中だけ持てば十分です。製品ではメモリも文字列も消せます（[プリプロセッサマクロ](../vs/preprocessor.md)）。

<!-- fig:hash-buckets:begin -->

<svg class="fig illust motion" data-fig="hash-buckets" viewBox="0 0 780 460" role="img"><rect x="0" y="0" width="780" height="460" rx="14" fill="#ffffff"/>
<defs><marker id="arr-hash-buckets" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">ハッシュ表: キーを数値に変え、その番号のバケツへ入れる(衝突は同じバケツに並ぶ)</text>
<text x="110" y="112" text-anchor="end" style="font-size:12px;font-weight:700;fill:#64748b">バケツ 0</text>
<rect x="120" y="90" width="60" height="30" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="110" y="150" text-anchor="end" style="font-size:12px;font-weight:700;fill:#64748b">バケツ 1</text>
<rect x="120" y="128" width="60" height="30" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="110" y="188" text-anchor="end" style="font-size:12px;font-weight:700;fill:#64748b">バケツ 2</text>
<rect x="120" y="166" width="60" height="30" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="110" y="226" text-anchor="end" style="font-size:12px;font-weight:700;fill:#64748b">バケツ 3</text>
<rect x="120" y="204" width="60" height="30" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="110" y="264" text-anchor="end" style="font-size:12px;font-weight:700;fill:#64748b">バケツ 4</text>
<rect x="120" y="242" width="60" height="30" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="110" y="302" text-anchor="end" style="font-size:12px;font-weight:700;fill:#64748b">バケツ 5</text>
<rect x="120" y="280" width="60" height="30" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="110" y="340" text-anchor="end" style="font-size:12px;font-weight:700;fill:#64748b">バケツ 6</text>
<rect x="120" y="318" width="60" height="30" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="110" y="378" text-anchor="end" style="font-size:12px;font-weight:700;fill:#64748b">バケツ 7</text>
<rect x="120" y="356" width="60" height="30" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.0809;0.0811;1.0000" values="0;0;1;1"/><rect x="190" y="280" width="90" height="30" fill="#2563eb" opacity="0.9"/>
<text x="235" y="301" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">hp</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.1619;0.1622;1.0000" values="0;0;1;1"/><rect x="190" y="90" width="90" height="30" fill="#2563eb" opacity="0.9"/>
<text x="235" y="111" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">mp</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.2430;0.2432;1.0000" values="0;0;1;1"/><rect x="190" y="128" width="90" height="30" fill="#2563eb" opacity="0.9"/>
<text x="235" y="149" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">atk</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.3241;0.3243;1.0000" values="0;0;1;1"/><rect x="190" y="242" width="90" height="30" fill="#2563eb" opacity="0.9"/>
<text x="235" y="263" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">def</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.4052;0.4054;1.0000" values="0;0;1;1"/><rect x="190" y="318" width="90" height="30" fill="#2563eb" opacity="0.9"/>
<text x="235" y="339" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">spd</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.4863;0.4865;1.0000" values="0;0;1;1"/><rect x="190" y="204" width="90" height="30" fill="#2563eb" opacity="0.9"/>
<text x="235" y="225" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">luk</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.5674;0.5676;1.0000" values="0;0;1;1"/><rect x="290" y="90" width="90" height="30" fill="#e5484d" opacity="0.9"/>
<text x="335" y="111" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">exp</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.6484;0.6486;1.0000" values="0;0;1;1"/><rect x="290" y="204" width="90" height="30" fill="#e5484d" opacity="0.9"/>
<text x="335" y="225" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">gold</text>
</g>
<text x="600" y="250" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">キーを FNV-1a でハッシュ → 8 で割った余りがバケツ番号<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.0809;0.0811;1.0000" values="1;1;0;0"/></text>
<text x="600" y="250" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">"hp" → バケツ 5<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.0809;0.0811;0.1619;0.1622;1.0000" values="0;0;1;1;0;0"/></text>
<text x="600" y="250" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">"mp" → バケツ 0<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.1619;0.1622;0.2430;0.2432;1.0000" values="0;0;1;1;0;0"/></text>
<text x="600" y="250" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">"atk" → バケツ 1<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.2430;0.2432;0.3241;0.3243;1.0000" values="0;0;1;1;0;0"/></text>
<text x="600" y="250" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">"def" → バケツ 4<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.3241;0.3243;0.4052;0.4054;1.0000" values="0;0;1;1;0;0"/></text>
<text x="600" y="250" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">"spd" → バケツ 6<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.4052;0.4054;0.4863;0.4865;1.0000" values="0;0;1;1;0;0"/></text>
<text x="600" y="250" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">"luk" → バケツ 3<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.4863;0.4865;0.5674;0.5676;1.0000" values="0;0;1;1;0;0"/></text>
<text x="600" y="250" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">"exp" → バケツ 0（先客あり: 衝突。同じバケツに連ねる）<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.5674;0.5676;0.6484;0.6486;1.0000" values="0;0;1;1;0;0"/></text>
<text x="600" y="250" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">"gold" → バケツ 3（先客あり: 衝突。同じバケツに連ねる）<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.6484;0.6486;0.7295;0.7297;1.0000" values="0;0;1;1;0;0"/></text>
<text x="600" y="250" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">8 個を入れて、衝突が 2 回。多いと検索が遅くなる<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.7295;0.7297;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:hash-buckets:end -->

## よくあるミス

??? failure "毎フレーム、`std::string` で名前を比較している"
    **ハッシュ（ID）にして**、整数で比べます。

??? failure "`const std::string&` の引数に、リテラルを渡して、毎回確保している"
    `std::string_view` で受け取ります。

??? failure "`string_view` をメンバに保存して、元の文字列が消えた"
    ぶら下がりです。保存するなら、`std::string` か、寿命が確かなもの（リテラル）だけにします。

??? failure "32 ビットのハッシュで、名前が衝突した"
    64 ビットにして、開発中に衝突を検出します。

??? failure "`std::hash` の値をファイルに保存した"
    実装・実行で変わります。固定アルゴリズム（FNV-1a）を使います。

??? failure "`unordered_map<string, T>` の検索で、毎回 `std::string` を作っている"
    透過的検索にするか、キーを ID にします。

??? failure "`std::to_string` や `stringstream` を、毎フレーム使う"
    `to_chars`・`format_to` で、固定バッファに書きます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::string` は、確保・コピー・比較が重い。実行中は使わず、整数（ID）で扱う
    - [x] 引数は`string_view`。保存しない（ぶら下がり）。`\0` 終端ではない
    - [x] 名前は`constexpr` なハッシュ（FNV-1a）で ID 化。64 ビット + 衝突の検出
    - [x] 保存・通信するハッシュは、固定アルゴリズム（`std::hash` は不可）
    - [x] `unordered_map` は透過的検索、またはID をキーに。変換は`to_chars` / `from_chars`

## 関連ページ

- [最適化の進め方](index.md)
- [毎フレームのヒープ確保を避ける](frame-allocation.md)
- [std::string_view](../stl/utilities/string_view.md)
- [std::hash](../stl/utilities/hash.md)
- [std::unordered_map](../stl/containers/unordered_map.md)
- [ハンドル](../engine/handle.md)
