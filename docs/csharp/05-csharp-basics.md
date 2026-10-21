---
title: 第 5 章 C++ を知っている人のための C# 入門
tags:
  - C#連携
---

# 第 5 章 C++ を知っている人のための C# 入門

この章から第 2 部に入ります。ここからは <strong>C# と WPF と Prism</strong> を学びながら、エディタの骨組みを作ります。まず、この章で、<strong>エディタを書くために必要な C# の言葉</strong>を、C++ との対応つきで学びます。C# のすべてを網羅するのではなく、<strong>この教材のコードを読み書きするのに足りる範囲</strong>に絞ります。

## この章の考え方

C++ を中級まで知っている人にとって、C# は「見た目がよく似ているのに、考え方が少し違う言語」です。`class` も `for` も `if` も、同じように書けます。違いは主に、次の 4 つです。

1. <strong>メモリを自分で解放しない。</strong>`new` で作ったオブジェクトは、使われなくなったら、ガベージ コレクター（GC）が自動で片付けます。`delete` も、デストラクターも、ほとんど要りません。
2. <strong>型が「値型」と「参照型」に分かれる。</strong>`class` は<strong>参照型</strong>（変数がオブジェクトを指す）、`struct` は<strong>値型</strong>（変数がオブジェクトそのもの）です。C++ では、`class` と `struct` の違いは、既定のアクセス権だけでしたが、C# では、コピーの意味が変わります。
3. <strong>ポインターを（ほぼ）使わない。</strong>参照型の変数は、すでに「指す」ものです。`*` も `->` も要りません。
4. <strong>ヘッダー ファイルがない。</strong>宣言と定義が、同じ場所にあります。他のファイルのクラスは、`using` と名前空間で、そのまま使えます。

この章は、C# のコードを<strong>自分で実験できる場所</strong>を作ってから、1 つずつ確かめます。

## 手順 1：実験用のコンソール プロジェクトを作る

エディタのプロジェクトに、いきなり実験コードを書くと散らかるので、<strong>捨ててよい</strong>プロジェクトを別に作ります。

1. Visual Studio で「新しいプロジェクトの作成」→ 言語 C# →「コンソール アプリ」（<strong>.NET Framework ではないほう</strong>）を選ぶ。
2. 名前を `CSharpPlayground`、場所は `MiniEngine` とは別のフォルダーにする。フレームワークは <strong>.NET 8.0</strong>。
3. 「最上位レベルのステートメントを使用しない」に<strong>チェックを入れて</strong>作成する（`Program` クラスと `Main` 関数が見えるようにするため）。

作られる `Program.cs` は、次の形です。

```csharp
namespace CSharpPlayground;

internal class Program
{
    static void Main(string[] args)
    {
        Console.WriteLine("Hello, World!");
    }
}
```

| 新しく出てきたもの | C++ では | 説明 |
| --- | --- | --- |
| `namespace CSharpPlayground;` | `namespace CSharpPlayground { … }` | 名前の置き場所。末尾が `;` の形は、<strong>このファイル全体</strong>が、その名前空間に入る（ファイルスコープ名前空間） |
| `internal class Program` | `class Program`（外に公開しない） | `internal` は、「同じプロジェクトの中だけで見える」というアクセス権（後で詳しく） |
| `static void Main(string[] args)` | `int main(int argc, char** argv)` | プログラムの入口。`static` は、オブジェクトを作らなくても呼べる。`string[] args` が、コマンドライン引数 |
| `Console.WriteLine(…)` | `std::println(…)` | 標準出力に 1 行書く。`Console` は、.NET の標準ライブラリのクラス |

`F5`（またはデバッグなしで `Ctrl + F5`）で実行すると、黒い画面に `Hello, World!` が出ます。以降のコードは、`Main` の中に書いて試します。

## 手順 2：型と変数

### 基本の型

```csharp
int hp = 100;
float speed = 2.5f;
double pi = 3.14159265358979;
bool alive = true;
char letter = 'A';
string name = "Player";
```

C++ とほぼ同じですが、<strong>サイズが決まっている</strong>点が違います。C# の `int` は、必ず 32 ビット、`long` は必ず 64 ビットです。

| C# の型 | 大きさ | C++ の対応 |
| --- | --- | --- |
| `byte` | 8 ビット、符号なし | `std::uint8_t` |
| `sbyte` | 8 ビット、符号あり | `std::int8_t` |
| `short` / `ushort` | 16 ビット | `std::int16_t` / `std::uint16_t` |
| `int` / `uint` | 32 ビット | `std::int32_t` / `std::uint32_t` |
| `long` / `ulong` | 64 ビット | `std::int64_t` / `std::uint64_t` |
| `float` | 32 ビット浮動小数 | `float` |
| `double` | 64 ビット浮動小数 | `double` |
| `bool` | 真偽 | `bool`（ただし C# は、整数を `if` に入れられない） |
| `char` | 16 ビットの UTF-16 の文字 | `char16_t`（`char` とは違う） |
| `string` | UTF-16 の文字列（<strong>変更できない</strong>） | `std::u16string` に近いが別物 |
| `nint` / `nuint` | ポインターの大きさの整数 | `std::intptr_t` / `std::uintptr_t` |

!!! warning "C# の `long` は 64 ビット"
    C++ の Windows では `long` は 32 ビットです。C# の `long` と C++ の `long` は<strong>違う型</strong>です。C++ と受け渡すときは、`int`（32 ビット）と `std::int32_t`、`long`（64 ビット）と `std::int64_t` のように、<strong>大きさで</strong>対応させます（第 13 章）。

### var（型推論）

```csharp
var count = 10;           // int と推論される
var names = new List<string>();   // List<string> と推論される
```

`var` は C++ の `auto` と同じです。右辺から型が決まり、<strong>後から別の型は入れられません</strong>（C++ の `auto` と同じで、動的型ではありません）。

### 変換

C# では、<strong>情報が失われる変換は、明示的に書く</strong>必要があります。

```csharp
int a = 10;
long b = a;            // 広がる変換は自動
int c = (int)b;        // 狭まる変換は、キャストを書く
float f = 3.7f;
int i = (int)f;        // 3（小数点以下は切り捨て）
```

C++ の暗黙の変換（`int x = 3.7;` が通ってしまう）は、C# では<strong>エラー</strong>になります。この点は、C# のほうが安全です。

### 文字列

```csharp
string name = "Player";
int hp = 100;
string text = $"{name} の HP は {hp} です";   // 補間文字列
string upper = name.ToUpper();
bool starts = name.StartsWith("Pl");
int length = name.Length;                      // 関数ではなく、プロパティ（() が要らない）
string[] parts = "a,b,c".Split(',');
```

| 新しく出てきたもの | C++ では | 説明 |
| --- | --- | --- |
| `$"…{式}…"` | `std::format("…{}…", 式)` | 補間文字列。`{}` の中に、変数や式をそのまま書ける。書式も指定できる（`{value:F2}` で小数 2 桁） |
| `string` は変更できない | `const std::u16string` に近い | `ToUpper()` などは、<strong>新しい文字列を返す</strong>。元は変わらない |
| `name.Length` | `name.size()` | 「長さ」は、プロパティ（後述）で、`()` を付けない |
| `Split(',')` | 標準にはない | 区切り文字で分けて、`string[]`（配列）を返す |

## 手順 3：値型と参照型

C# で最も大事な概念の 1 つです。

```csharp
struct PointStruct { public int X; public int Y; }
class  PointClass  { public int X; public int Y; }

var s1 = new PointStruct { X = 1, Y = 2 };
var s2 = s1;           // 値がコピーされる
s2.X = 99;
Console.WriteLine(s1.X);   // 1（s1 は変わらない）

var c1 = new PointClass { X = 1, Y = 2 };
var c2 = c1;           // 同じオブジェクトを指すだけ（コピーされない）
c2.X = 99;
Console.WriteLine(c1.X);   // 99（c1 も変わる）
```

| | 値型（`struct`、`int`、`float` など） | 参照型（`class`、`string`、配列など） |
| --- | --- | --- |
| 変数の中身 | オブジェクトそのもの | オブジェクトへの<strong>参照</strong>（ポインターのようなもの） |
| `=` で代入すると | <strong>中身がコピー</strong>される | <strong>参照がコピー</strong>される（同じオブジェクトを指す） |
| 置き場所 | 持ち主の中（スタック、またはクラスの中） | ヒープ（GC が管理する） |
| 何も指さない状態（`null`） | 既定ではない | ある（`null`） |
| C++ で近いもの | 普通の変数（`Vec3 v;`） | `std::shared_ptr<T>`（コピーすると同じものを指す。ただし、参照カウントではなく GC） |

この違いは、<strong>エンジンとの受け渡し</strong>で重要になります。`Vector3`（位置）のような小さなデータは `struct`（値型）にして、C++ の構造体と同じ並びにすると、そのまま受け渡せます（第 13 章）。一方、シーンのオブジェクトやビューモデルは `class`（参照型）にして、複数の場所から同じものを参照します。

!!! note "C++ との違い：struct と class"
    C++ の `struct` と `class` は、アクセス権の既定値が違うだけで、どちらも値のように振る舞います。C# では、`struct` と `class` で<strong>コピーの意味</strong>が変わります。迷ったら、`class` にします。`struct` は、「小さく、不変で、値として扱いたいもの」に使います。

## 手順 4：クラス、メンバー、アクセス権

```csharp
public class Player
{
    // フィールド（メンバー変数）
    private int _hp = 100;

    // プロパティ（読み書きを関数のように制御できる変数）
    public int Hp
    {
        get { return _hp; }
        set { _hp = Math.Clamp(value, 0, 100); }
    }

    // 自動実装プロパティ（上の書き方を、短く書ける）
    public string Name { get; set; } = "Player";

    // 読み取り専用のプロパティ
    public bool IsDead => _hp <= 0;

    // コンストラクター
    public Player(string name)
    {
        Name = name;
    }

    // メソッド（メンバー関数）
    public void Damage(int amount)
    {
        Hp -= amount;
    }
}
```

使い方は、次のとおりです。

```csharp
var p = new Player("Alice");   // new で作る。delete は要らない
p.Damage(30);
Console.WriteLine(p.Hp);       // 70
p.Hp = 500;                    // set が呼ばれ、100 に切り詰められる
Console.WriteLine(p.IsDead);   // False
```

| 新しく出てきたもの | C++ では | 説明 |
| --- | --- | --- |
| フィールド | メンバー変数 | クラスの中の変数。慣習として、`private` なら `_hp` のように、先頭に `_` を付ける |
| <strong>プロパティ</strong> | `getter` / `setter` の組 | 外からは<strong>変数のように</strong>使えるが、中身は<strong>関数</strong>。読み書きのときに処理を挟める。<strong>WPF のデータ バインディングは、プロパティを対象にする</strong>ので、この教材で最も大事な概念の 1 つ |
| `get` / `set` | `GetHp()` / `SetHp(v)` | 読むとき / 書くときの処理。`set` の中の `value` は、代入された値 |
| 自動実装プロパティ `{ get; set; }` | 単純な getter / setter | 裏に隠れたフィールドが自動で作られる。処理を挟む必要がなければ、これで十分 |
| `=>`（式形式のメンバー） | `bool IsDead() const { return …; }` | 1 つの式だけで済むメンバーを短く書く。`get` だけのプロパティになる |
| `Math.Clamp` | `std::clamp` | 範囲に切り詰める |
| コンストラクター | コンストラクター | クラスと同じ名前の関数。書き方は C++ と同じ |
| デストラクター | デストラクター | C# にも書けるが、<strong>呼ばれる時点が決まらない</strong>（GC が決める）。普段は書かない（第 31 章で `IDisposable` を学ぶ） |

### アクセス権

| C# | 見える範囲 | C++ で近いもの |
| --- | --- | --- |
| `public` | どこからでも | `public` |
| `private` | そのクラスの中だけ（<strong>省略時の既定</strong>） | `private` |
| `protected` | そのクラスと、継承したクラス | `protected` |
| `internal` | <strong>同じプロジェクト（アセンブリ）の中</strong> | （近いものがない。DLL 内の非公開に近い） |
| `protected internal` | 同じプロジェクトの中、または継承したクラス | （なし） |

C# では、`internal` が重要です。プロジェクトの外には見せたくないが、プロジェクトの中では自由に使いたいもの、に付けます。

### 初期化子

```csharp
var p = new Player("Bob") { Hp = 50 };   // 作ると同時に、プロパティを設定できる
```

### 静的メンバー

```csharp
public class Counter
{
    public static int Total;               // クラス全体で 1 つ
    public static void Reset() { Total = 0; }
}
Counter.Total++;                           // インスタンスなしで使う
```

`static` は C++ と同じ意味です。`Counter.Total` のように、クラス名を `.` でつないで使います（C++ の `::` ではない）。

## 手順 5：null と null 許容

参照型の変数は、`null`（何も指さない）にできます。`null` のオブジェクトにメンバーを呼ぶと、<strong>例外</strong>（`NullReferenceException`）が起きます。C++ のヌル ポインターの参照外しと同じですが、クラッシュではなく例外として捕まえられます。

```csharp
string? maybe = null;                  // ? を付けると「null かもしれない」と表明する
int length = maybe?.Length ?? 0;       // null のときは 0
if (maybe is not null)
{
    Console.WriteLine(maybe.Length);
}
int? number = null;                    // 値型でも ? を付けると null が入れられる
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `string?`（`T?`） | 「`null` を入れてよい」ことを表す型。付いていない `string` は「null にしない」という約束（コンパイラが警告で守ってくれる）。この仕組みを<strong>null 許容参照型</strong>と呼ぶ。新しいプロジェクトでは、既定で有効 |
| `?.`（null 条件演算子） | 左が `null` なら、右を実行せず、全体が `null` になる。`a?.b` は、`a != null ? a.b : null` |
| `??`（null 合体演算子） | 左が `null` のとき、右の値を使う。`a ?? b` |
| `is null` / `is not null` | `null` かどうかの判定 |
| `int?`（`Nullable<int>`） | 値型に、「値がない」状態を足したもの。C++ の `std::optional<int>` に近い |

## 手順 6：コレクションと繰り返し

```csharp
var numbers = new List<int> { 3, 1, 2 };   // std::vector<int>
numbers.Add(5);
numbers.Sort();
Console.WriteLine(numbers.Count);          // 4（size() ではなく Count）
foreach (var n in numbers)                 // 範囲 for 文
{
    Console.WriteLine(n);
}

var scores = new Dictionary<string, int>   // std::unordered_map<std::string, int>
{
    ["Alice"] = 90,
    ["Bob"] = 70,
};
if (scores.TryGetValue("Alice", out int score))
{
    Console.WriteLine(score);
}

int[] array = { 1, 2, 3 };                 // 配列（std::array / 生配列に近い）
```

| C# | C++ | 説明 |
| --- | --- | --- |
| `List<T>` | `std::vector<T>` | 伸び縮みする配列。`Add`、`Remove`、`Count`、`[i]` |
| `Dictionary<K, V>` | `std::unordered_map<K, V>` | キーで引く表。`dict[key]` は、キーがないと例外。`TryGetValue` なら、ないときも安全 |
| `HashSet<T>` | `std::unordered_set<T>` | 重複のない集合 |
| `T[]` | `T[N]` や `std::array`（ただし、大きさは実行時に決まる） | 固定長の配列 |
| `foreach (var x in 集まり)` | `for (auto& x : 集まり)` | 範囲 for 文。ループ中に集まりを変更すると例外になる |
| `out int score` | `int& score`（出力用の参照引数） | 呼ばれた関数が値を書き込む引数。呼ぶ側も `out` を書く |
| `<T>`（ジェネリクス） | `template <typename T>` | 型を後から指定する仕組み。ただし、C# は<strong>実行時</strong>に型が決まり、テンプレートより制約が強い |

### LINQ（データの絞り込み）

```csharp
using System.Linq;

var names = new List<string> { "Alice", "Bob", "Charlie" };
var longNames = names.Where(n => n.Length > 3).ToList();   // 4 文字より長いもの
var upper = names.Select(n => n.ToUpper());                // 全部大文字にした列
bool any = names.Any(n => n.StartsWith("B"));
string first = names.First();
```

`Where`、`Select`、`Any` は、C++ の `std::ranges::views::filter`、`transform`、`std::ranges::any_of` に近い関数です。`n => n.Length > 3` は<strong>ラムダ式</strong>で、C++ の `[](auto n) { return n.Length() > 3; }` と同じです。

## 手順 7：ラムダ式、デリゲート、イベント

C# には、「関数を値として渡す」ための型として、<strong>デリゲート</strong>があります。

```csharp
// 汎用のデリゲート型
Action<string> log = message => Console.WriteLine(message);   // 戻り値なし（void）
Func<int, int, int> add = (a, b) => a + b;                    // 戻り値あり（最後の型が戻り値）
log("hello");
Console.WriteLine(add(2, 3));    // 5
```

| 新しく出てきたもの | C++ では | 説明 |
| --- | --- | --- |
| `Action<T…>` | `std::function<void(T…)>` | 戻り値のない関数を表す型 |
| `Func<T…, R>` | `std::function<R(T…)>` | 戻り値のある関数を表す型。最後の型引数が戻り値 |
| ラムダ式 `(a, b) => a + b` | `[](auto a, auto b) { return a + b; }` | 名前のない関数。`=>` の右が本体。外の変数は、<strong>自動で捕まえる</strong>（キャプチャの書き方は要らない） |
| `delegate` | 関数ポインター / `std::function` | デリゲート型の宣言に使うキーワード。普段は、`Action`、`Func` で足りる |

### イベント

```csharp
public class Player
{
    // 「HP が変わった」ことを知らせるイベント
    public event Action<int>? HpChanged;

    private int _hp;
    public int Hp
    {
        get => _hp;
        set
        {
            _hp = value;
            HpChanged?.Invoke(_hp);    // 登録者がいれば、全員に知らせる
        }
    }
}

var p = new Player();
p.HpChanged += hp => Console.WriteLine($"HP が {hp} になった");   // 登録
p.Hp = 50;                                                         // "HP が 50 になった"
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `event` | デリゲートを<strong>外から呼べなく</strong>して、登録（`+=`）と解除（`-=`）だけを許す。通知の仕組み（オブザーバー パターン）を、言語が支える |
| `+=` / `-=` | 登録 / 解除。解除し忘れると、登録された側が、GC で片付かない（メモリ リーク）。第 31 章で扱う |
| `?.Invoke(…)` | 登録者がいなければ（`null`）何もしない |

WPF は、<strong>イベント</strong>（ボタンが押された）と<strong>プロパティ変更通知</strong>（`INotifyPropertyChanged`）で動きます。この仕組みの土台がこれです。

## 手順 8：継承とインターフェース

```csharp
public interface IDamageable                 // 約束だけを書く（C++ の純粋仮想クラスに近い）
{
    void Damage(int amount);
    bool IsDead { get; }
}

public abstract class Entity { public string Name { get; set; } = ""; }

public class Enemy : Entity, IDamageable     // 継承は 1 つ、インターフェースは複数
{
    private int _hp = 10;
    public void Damage(int amount) { _hp -= amount; }
    public bool IsDead => _hp <= 0;
}
```

| 新しく出てきたもの | C++ では | 説明 |
| --- | --- | --- |
| `interface` | 純粋仮想関数だけを持つクラス | メンバーの宣言だけを持つ約束。<strong>名前は慣習として `I` で始める</strong>（`IDamageable`） |
| `: Entity, IDamageable` | `class Enemy : public Entity, public IDamageable` | `:` の後ろに、基底クラス（1 つだけ）とインターフェース（いくつでも）を並べる。`public` は書かない |
| `abstract` | 純粋仮想関数を持つ | 直接 `new` できないクラス |
| `virtual` / `override` | `virtual` / `override` | C++ と同じ。C# は、<strong>既定で仮想関数ではない</strong>ので、`virtual` を書く。派生側では必ず `override` を書く |
| `sealed` | `final` | これ以上継承できない |
| `is` / `as` | `dynamic_cast` | 型の判定 / 変換。`obj is Enemy e`、`obj as Enemy`（失敗すると `null`） |

## 手順 9：例外

```csharp
try
{
    var text = File.ReadAllText("settings.json");
    Console.WriteLine(text.Length);
}
catch (FileNotFoundException e)
{
    Console.WriteLine($"ファイルがありません: {e.Message}");
}
catch (Exception e)
{
    Console.WriteLine($"想定外のエラー: {e}");
}
finally
{
    Console.WriteLine("最後に必ず実行される");
}
```

| 新しく出てきたもの | C++ では | 説明 |
| --- | --- | --- |
| `try` / `catch` / `finally` | `try` / `catch`（`finally` は無い） | `finally` は、成功しても失敗しても必ず実行される後始末の場所（C++ では、デストラクターで行う） |
| `Exception` | `std::exception` | すべての例外の基底クラス。`Message`（理由）と `StackTrace` を持つ |
| `File.ReadAllText` | `std::ifstream` で読む | ファイルを丸ごと文字列で読む。`System.IO` 名前空間 |
| `throw new ArgumentException("…")` | `throw std::invalid_argument("…")` | 例外を投げる |

C# の例外は、<strong>すべて `Exception` を継承したクラスのオブジェクト</strong>です。`catch (Exception e)` で、ほぼ全部を捕まえられます。

## 手順 10：using（名前空間の導入、後始末）

`using` には、2 つの意味があります。

```csharp
using System.Collections.Generic;       // ① 名前空間の導入（C++ の using namespace に近い）

using (var stream = File.OpenRead("a.bin"))   // ② 後始末（スコープを出たら Dispose が呼ばれる）
{
    // stream を使う
}                                       // ここで自動的に閉じられる

using var writer = new StreamWriter("log.txt");   // ③ 新しい書き方：このブロックの終わりで閉じる
```

| 書き方 | 説明 |
| --- | --- |
| ① ファイルの先頭の `using 名前空間;` | その名前空間のクラスを、名前だけで書けるようにする。.NET 6 以降は、よく使うものが<strong>暗黙で</strong>入る（`ImplicitUsings`）。`System`、`System.Collections.Generic`、`System.IO`、`System.Linq` など |
| ② `using (…) { … }` | `IDisposable` を実装した物を、ブロックを出るときに<strong>必ず</strong>後始末（`Dispose`）する。C++ の RAII（デストラクターで自動解放）に相当する仕組み |
| ③ `using var x = …;` | 現在のブロックの終わりで `Dispose` を呼ぶ。② の短い書き方 |

!!! note "C++ の RAII が、そのままは使えない"
    C++ では、オブジェクトが範囲を出ると、デストラクターが<strong>必ず</strong>呼ばれます。C# の GC は、いつ片付けるかが決まりません。そのため、ファイルやネイティブのハンドルのように、<strong>確実に閉じたいもの</strong>は、`IDisposable` と `using` で明示的に閉じます。エンジンのハンドルを扱うときに、特に重要になります（第 13 章、第 31 章）。

## 手順 11：非同期（async / await）の入口

ファイルの読み込みなど、時間のかかる処理を、画面を止めずに行うための仕組みです。

```csharp
static async Task Main(string[] args)
{
    string text = await File.ReadAllTextAsync("big.txt");   // 待つ間、スレッドを占有しない
    Console.WriteLine(text.Length);
}
```

| 新しく出てきたもの | C++ では | 説明 |
| --- | --- | --- |
| `async` | コルーチンに近い | この関数の中で `await` を使うと宣言する。戻り値は `Task`（値があるなら `Task<T>`） |
| `await` | `co_await` | 結果が出るまで、この関数を<strong>中断</strong>し、呼び出し元に制御を返す。終わったら、続きから再開する |
| `Task` / `Task<T>` | `std::future<T>` に近い | 「いずれ終わる仕事」を表す型 |

WPF では、画面を操作できる<strong>スレッド</strong>は、UI スレッド 1 本だけです。時間のかかる処理でこのスレッドを止めると、画面が固まります。`async`/`await` は、これを避ける標準的な方法です。詳しくは、必要になる章（第 25、26 章）で扱います。

## 手順 12：その他、よく見る書き方

```csharp
// switch 式
string label = hp switch
{
    <= 0 => "死亡",
    < 30 => "ピンチ",
    _    => "元気",
};

// タプル
(int x, int y) = (3, 4);
var (min, max) = GetRange();

// record（値のように比較される、変更しにくいデータ）
public record SceneInfo(string Name, int ObjectCount);

// 名前付き引数と既定値
void Log(string message, int level = 0) { }
Log("hello", level: 2);

// 拡張メソッド（既存の型に、メソッドを足したように見せる）
public static class StringExtensions
{
    public static bool IsBlank(this string s) => string.IsNullOrWhiteSpace(s);
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `switch` 式 | 値を返す `switch`。`_` は、それ以外 |
| タプル `(int, int)` | 複数の値をまとめて返す。`std::pair` / `std::tuple` に近い |
| `record` | データを運ぶための型。中身が等しければ「等しい」と判定される。プロパティが自動で作られる |
| 名前付き引数 | 引数名を指定して呼ぶ。順番を気にしなくてよい |
| 拡張メソッド | `this` を付けた最初の引数の型に、メソッドを足したように呼べる。LINQ はこれで作られている |

## C# と C++ の対応のまとめ

| 目的 | C++ | C# |
| --- | --- | --- |
| メモリの解放 | `delete`、スマート ポインター | GC が自動で行う。ネイティブの資源は `IDisposable` と `using` |
| 参照 | `T&` | 参照型は、すでに参照。`ref` と `out` で、値型も参照渡しにできる |
| ポインター | `T*` | 通常は使わない（`unsafe` 内だけ）。ネイティブとの境界では `IntPtr` / `nint` |
| 名前の探し方 | `#include` と `namespace` | `using` と `namespace`（ヘッダーなし） |
| テンプレート | `template` | ジェネリクス `<T>` |
| 継承 | 多重継承可 | クラスは単一継承、インターフェースは複数 |
| 定数 | `constexpr` / `const` | `const`（コンパイル時定数）、`readonly`（実行時に一度だけ設定） |
| 文字列 | `std::string`（UTF-8 が主） | `string`（UTF-16、不変） |
| 配列 | `std::vector` / `std::array` | `List<T>` / `T[]` |
| 列挙型 | `enum class` | `enum`（名前の前に型名が必要。`Color.Red`） |

## よくあるミス

??? failure "`CS0103: 現在のコンテキストに '〜' という名前は存在しません`"
    変数名のタイプミス、または、`using` が足りない。クラス名にカーソルを置いて `Ctrl + .` を押すと、必要な `using` を足す候補が出る。

??? failure "`CS8600`／`CS8602`（null の可能性）の警告"
    null 許容参照型の警告。`null` になりうる値に `?` を付けて、`?.` や `is not null` で確かめてから使う。警告を無視すると、実行時に `NullReferenceException` が起きる。

??? failure "`foreach` の中で `List` を変更して例外になる"
    `InvalidOperationException: Collection was modified`。ループ中に、要素の追加・削除はできない。`ToList()` でコピーしてから回すか、別の変数に結果を貯めて、あとで反映する。

??? failure "`struct` を `List` から取り出して変更しても、元が変わらない"
    値型は<strong>コピー</strong>されるので、`list[0].X = 5;` は、コピーを変更しようとして、コンパイル エラーになる（または、無効な変更になる）。変更したいデータは `class` にする。

??? failure "文字列を `==` で比べて、期待通りにならない"
    C# の `string` の `==` は、<strong>中身</strong>を比べる（C++ の `std::string` と同じ）。ただし、大文字小文字を区別する。区別しない比較は、`string.Equals(a, b, StringComparison.OrdinalIgnoreCase)`。

## この章のまとめ

- C# はメモリ解放が自動（GC）。ただし、ネイティブの資源は `IDisposable` と `using` で閉じる。
- `class` は参照型、`struct` は値型。コピーの意味が違う。
- <strong>プロパティ</strong>は、変数のように見える関数。WPF のデータ バインディングの対象はプロパティ。
- <strong>イベント</strong>と<strong>デリゲート</strong>が、通知の土台。
- `?` と `?.` と `??` で、`null` を安全に扱う。

## 次の章へ

次の章（[第 6 章 WPF プロジェクトと XAML](06-wpf-xaml.md)）では、第 1 章で作った `Editor` プロジェクトを開いて、WPF のプロジェクトの中身を読み、XAML で画面を作ります。
