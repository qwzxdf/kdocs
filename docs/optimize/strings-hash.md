---
title: 文字列とハッシュの最適化
tags:
  - 最適化
---

# 文字列とハッシュの最適化

ゲームの中には、**文字列**がたくさん出てきます（アセット名、イベント名、オブジェクト名、ログ）。`std::string` は便利ですが、**確保・コピー・比較**が、意外と重いのです。そこで、**実行中は文字列を使わず、整数（ID・ハッシュ値）で扱う**のが、ゲームの定石です。このページは、`std::string` のコスト、**`string_view`**、**文字列のハッシュ化**、<strong>文字列 ID（インターン）</strong>、`unordered_map` での検索をまとめます。

!!! tip "ポイント"
    - <strong>`std::string` は、作る・コピーする・比べるのが、整数より何十倍も遅い</strong>。<strong>毎フレーム使わない</strong>。
    - 引数は<strong>`std::string_view`</strong>（コピーなし・確保なし）。ただし、<strong>`\0` 終端でない</strong>点に注意。
    - 名前は<strong>ハッシュ値（整数）にして</strong>、実行中は<strong>整数で比べる</strong>。<strong>コンパイル時にハッシュ</strong>できる（`constexpr`）。
    - <strong>ハッシュは衝突する</strong>。<strong>64 ビット</strong>にして、<strong>開発中は衝突を検出</strong>する。
    - <strong>`unordered_map<std::string, T>` の検索で、`std::string` を作らない</strong>（C++20 の透過的検索）。
    - <strong>デバッグ用の名前</strong>は、製品ビルドで消せるようにする。

## std::string のコスト

| 操作 | コスト |
| --- | --- |
| <strong>作成（長い文字列）</strong> | ヒープ確保 + コピー |
| <strong>作成（短い文字列）</strong> | SSO で確保なし（約 15 文字以下）。それでもコピーは必要 |
| <strong>比較（`==`）</strong> | **長さ + 中身を、1 文字ずつ**。長いほど遅い。整数の比較は、1 命令 |
| <strong>連結（`+`）</strong> | 一時オブジェクトの作成・確保・コピー |
| **`std::map<std::string, T>`** | **比較が、木の深さぶん**。しかも、文字列比較 |
| **`std::unordered_map<std::string, T>`** | **ハッシュ計算（文字列の長さ）+ 比較** |

**整数の `==` は 1 サイクル**、**文字列の `==` は数十〜数百サイクル**が、目安です。

## string_view

**`std::string_view`** は、**文字列の先頭と長さ**だけを持つ、**読み取り専用の窓**です。**確保もコピーもしません**。

```cpp
void Log(std::string_view message);

Log("hello");
Log(name);
Log(std::string("temp"));
```

| 項目 | 説明 |
| --- | --- |
| **使いどころ** | **関数の引数**。`const std::string&` より、**リテラルでも確保しない** |
| **寿命に注意** | **元の文字列が消えると、ぶら下がる**。**保存しない**（メンバに持たない） |
| **`\0` 終端ではない** | C の API（`printf`、Windows API）に渡すとき、**`\0` がない**かもしれない。**`std::string` に変換**するか、**長さ付き**の API を使う |
| **一時 `std::string` の `string_view`** | `std::string_view sv = std::string("x");` は、**すぐ消えて**ぶら下がる |

詳しくは、[std::string_view](../stl/utilities/string_view.md) を見てください。

## 文字列をハッシュにする

**文字列を、整数（ハッシュ値）に変換**して、**実行中は整数だけで比べます**。

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
| **`constexpr`** | **コンパイル時に計算**できる。`switch` の `case` にも使える |
| **FNV-1a** | **単純で、速い**。ゲームの名前に、よく使う（暗号用ではない） |
| **実行時のコスト** | ハッシュ計算（文字列の長さ）が、**1 回だけ**。以後は、整数 |

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

**型にする**ことで、**普通の整数と間違えない**ようにします。

### 注意：衝突

**異なる文字列が、同じハッシュ値**になることを、**衝突**といいます。

| ビット数 | 衝突の起こりやすさ |
| --- | --- |
| 32 ビット | **数万個の名前**で、**衝突の可能性**が出る（誕生日のパラドックス） |
| **64 ビット** | **数十億個**でも、ほぼ起きない |

| 対策 | 説明 |
| --- | --- |
| **64 ビットにする** | 最も簡単 |
| **開発中は、衝突を検出する** | 登録時に、**同じハッシュで、異なる文字列**がないか、チェック（`assert`） |
| **ハッシュだけに頼らない** | 重要な所では、元の文字列も比べる |

!!! warning "標準の `std::hash` は、実装依存"
    **`std::hash<std::string>` の値は、実装・実行ごとに変わる**かもしれません。**ファイルに保存したり、ネットワークで送る**ハッシュには、**自作の固定アルゴリズム**（FNV-1a など）を使います（[std::hash](../stl/utilities/hash.md)）。

## 文字列 ID とインターン

**同じ文字列を、1 つだけ保存**して、**ID（番号）で参照**する仕組みが、**文字列のインターン**です。

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
| 値 | ハッシュ値（64 ビット） | **連番**（32 ビットで十分） |
| **衝突** | **ある**（まれに） | **ない** |
| <strong>逆引き（ID → 文字列）</strong> | できない（別途テーブルが必要） | **できる**（デバッグに便利） |
| コンパイル時の計算 | **できる** | できない（実行時に、テーブルに登録） |
| 保存・通信 | 固定アルゴリズムなら、そのまま使える | **ID が実行ごとに変わる**。保存には向かない |

**ハッシュ + 開発用の逆引きテーブル**（デバッグビルドだけ）が、実用的です。

## unordered_map の検索

```cpp
std::unordered_map<std::string, int> table;

table.find("player");
```

**`find("player")` は、`std::string` の一時オブジェクトを作る**ので、**確保**が起きることがあります。

### 透過的検索（C++20）

```cpp
struct StringHash {
  using is_transparent = void;
  size_t operator()(std::string_view s) const { return std::hash<std::string_view>{}(s); }
};

std::unordered_map<std::string, int, StringHash, std::equal_to<>> table;

table.find(std::string_view("player"));
```

**`is_transparent`** を付けた**ハッシュ**と、**`std::equal_to<>`**を使うと、**`string_view` や `const char*` のまま<strong>検索できます。</strong>一時 `std::string` が作られません**。

### そもそも、キーを整数にする

```cpp
std::unordered_map<StringId, int, StringIdHash> table;
```

**ID をキー**にすれば、**ハッシュ計算・比較が軽く**なります。**文字列のキーは、ロード時に ID にして、実行中は ID だけ**にします。

## 数値と文字列の変換

| やりたいこと | 速い方法 |
| --- | --- |
| **数値 → 文字列** | `std::to_chars`（バッファに書く。確保なし） |
| **文字列 → 数値** | `std::from_chars`（ロケール非依存・例外なし・速い） |
| 書式付きの文字列 | `std::format_to` / `std::format_to_n`（固定バッファへ） |

```cpp
char buffer[32];
auto [end, error] = std::to_chars(buffer, buffer + sizeof(buffer), value);
std::string_view result(buffer, end - buffer);
```

`std::to_string`、`std::stoi`、`sprintf`、`stringstream` は、**ロケールの処理・確保**があり、**遅い**です。

## 文字列を避ける設計

| 場面 | 文字列を使わない方法 |
| --- | --- |
| **イベント名** | `enum class`、`StringId`（ハッシュ） |
| **アセットのパス** | ロード時にハッシュ化 → ハンドル（[ハンドル](../engine/handle.md)） |
| **オブジェクト名** | エディター・デバッグ用だけ。実行は ID |
| **アニメーション名・状態名** | `enum`、または、ロード時に、番号へ変換 |
| **ログ** | 書式文字列は、**ログのレベルを確認してから**作る |
| **設定のキー** | ロード時に解決して、**実行中は、キーで検索しない** |

**文字列の比較が必要なのは、「人間が読む・書く」境界だけ**です（ファイル、UI、コンソール）。**中に入れたら、すぐ ID にします**。

## デバッグ名を製品で消す

```cpp
struct Entity {
  StringId id;
#ifdef _DEBUG
  std::string debug_name;
#endif
};
```

**デバッグ用の名前**は、**開発中だけ**持てば十分です。製品では、**メモリも、文字列も、消せます**（[プリプロセッサマクロ](../vs/preprocessor.md)）。

## よくあるミス

??? failure "毎フレーム、`std::string` で、名前を比較している"
    **ハッシュ（ID）にして**、整数で比べます。

??? failure "`const std::string&` の引数に、リテラルを渡して、毎回確保している"
    `std::string_view` で受け取ります。

??? failure "`string_view` をメンバに保存して、元の文字列が消えた"
    **ぶら下がり**です。保存するなら、`std::string` か、**寿命が確かなもの**（リテラル）だけにします。

??? failure "32 ビットのハッシュで、名前が衝突した"
    **64 ビットにして**、開発中に**衝突を検出**します。

??? failure "`std::hash` の値を、ファイルに保存した"
    実装・実行で変わります。**固定アルゴリズム**（FNV-1a）を使います。

??? failure "`unordered_map<string, T>` の検索で、毎回 `std::string` を作っている"
    **透過的検索**にするか、キーを ID にします。

??? failure "`std::to_string` や `stringstream` を、毎フレーム使う"
    `to_chars`・`format_to` で、**固定バッファ**に書きます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>`std::string` は、確保・コピー・比較が重い</strong>。<strong>実行中は使わず、整数（ID）で扱う</strong>
    - [x] 引数は<strong>`string_view`</strong>。<strong>保存しない</strong>（ぶら下がり）。<strong>`\0` 終端ではない</strong>
    - [x] 名前は<strong>`constexpr` なハッシュ（FNV-1a）で ID 化</strong>。<strong>64 ビット + 衝突の検出</strong>
    - [x] 保存・通信するハッシュは、<strong>固定アルゴリズム</strong>（`std::hash` は不可）
    - [x] `unordered_map` は<strong>透過的検索</strong>、または<strong>ID をキー</strong>に。変換は<strong>`to_chars` / `from_chars`</strong>

## 関連ページ

- [最適化の進め方](index.md)
- [毎フレームのヒープ確保を避ける](frame-allocation.md)
- [std::string_view](../stl/utilities/string_view.md)
- [std::hash](../stl/utilities/hash.md)
- [std::unordered_map](../stl/containers/unordered_map.md)
- [ハンドル](../engine/handle.md)
