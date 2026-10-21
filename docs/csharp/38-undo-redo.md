---
title: 第 38 章 Undo/Redo
tags:
  - C#連携
---

# 第 38 章 Undo/Redo

この章では、これまでの編集（作成、削除、親子づけ、名前、位置、回転、拡大、色）を、すべて<strong>元に戻せる／やり直せる</strong>ようにします。エディタでは、Undo/Redo は「あると便利な機能」ではなく、<strong>あって当たり前の土台</strong>です。後から足すと、全部の編集コードを書き直すことになるので、第 36 章で `ISceneEditor` という窓口を用意しておきました。ここで、その真価が出ます。

## この章の考え方

### Undo の 2 つの作り方

| 方式 | 内容 | 長所 | 短所 |
| --- | --- | --- | --- |
| <strong>スナップショット</strong> | 編集のたびに、シーン全体のコピーを保存する。Undo は、そのコピーに戻す | 実装が簡単。漏れがない | シーンが大きいと、メモリと時間が膨大。部分的な変更でも全体をコピー |
| <strong>コマンド</strong>（採用） | 編集を、「やること」と「戻すこと」のペアとして記録する | 小さい。必要な分だけ記録。変更の履歴（名前）が分かる | 編集ごとに、コマンドを書く必要がある。「戻すこと」の書き忘れが、バグになる |

<strong>コマンド パターン</strong>を使います。1 つの編集 ＝ 1 つのコマンド（オブジェクト）で、`Do()`（実行）と `Undo()`（元に戻す）を持ちます。

```text
履歴： [ 位置を変更 ] [ 色を変更 ] [ 物を追加 ] ← 今ここ
         ↑ Undo すると、「物を追加」の Undo() が呼ばれ、1 つ前に戻る
         Redo すると、Undo したコマンドの Do() が、もう一度呼ばれる
```

### Undo の 4 つの難しさ

| 難しさ | 例 | 対処 |
| --- | --- | --- |
| 連続した操作 | ギズモのドラッグは、1 秒間に 60 回の位置の更新。Undo が 60 回必要になる | <strong>まとめる</strong>（トランザクション、マージ） |
| 削除の復元 | 削除した物を戻すとき、子、色、並び順、ID を、すべて元通りにする | 削除の前に、<strong>スナップショット</strong>を取る |
| 参照が壊れる | 削除して復元すると、別のオブジェクトになる。古いコマンドが、古いオブジェクトを指したままになる | コマンドは、オブジェクトでなく <strong>ID</strong> を持つ |
| 履歴の分岐 | Undo してから、別の編集をすると、Redo できる履歴が消える | 新しい編集で、Redo の履歴を<strong>捨てる</strong> |

## この章のゴール

- すべての編集が、`Ctrl + Z` で戻り、`Ctrl + Y` でやり直せる。
- ギズモのドラッグや、スライダーの操作が、<strong>1 回の Undo</strong> で戻る。
- 削除した物（と子）を、同じ ID、名前、値で復元できる。
- メニューに、`元に戻す: 位置を変更` のように、操作の名前が出る。
- 未保存かどうか（ダーティ フラグ）を、履歴から判定できる。

## 手順 1：コマンドと履歴

`Services\Undo\IUndoCommand.cs`:

```csharp
namespace Editor.Services.Undo;

// 1 つの編集。Do で実行し、Undo で元に戻す。
public interface IUndoCommand
{
    string Name { get; }
    void Do();
    void Undo();

    // 直前のコマンドと「まとめられる」なら、next を自分に取り込んで true を返す
    // （next は、すでに実行済み）
    bool TryMerge(IUndoCommand next);
}
```

`Services\Undo\CompositeCommand.cs`（複数をまとめる）:

```csharp
namespace Editor.Services.Undo;

// 複数のコマンドを、1 つの Undo の単位にまとめる。
public sealed class CompositeCommand : IUndoCommand
{
    private readonly List<IUndoCommand> _commands = new();

    public CompositeCommand(string name) => Name = name;

    public string Name { get; }
    public bool IsEmpty => _commands.Count == 0;

    // 追加と同時に実行する。直前のコマンドと合体できれば、合体する（ドラッグの連続した更新が 1 つになる）。
    public void AddAndDo(IUndoCommand command)
    {
        command.Do();
        if (_commands.Count > 0 && _commands[^1].TryMerge(command)) return;
        _commands.Add(command);
    }

    public void Do()
    {
        foreach (var c in _commands) c.Do();                  // Redo のとき、順番に
    }

    public void Undo()
    {
        for (int i = _commands.Count - 1; i >= 0; --i) _commands[i].Undo();   // 逆順に戻す
    }

    public bool TryMerge(IUndoCommand next) => false;
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `_commands[^1]` | 末尾の要素。`^1` は、「末尾から数えて 1 番目」を表す<strong>インデックス演算子</strong> |
| `public CompositeCommand(string name) => Name = name;` | 式形式のコンストラクター |
| 逆順で Undo | 「A してから B した」を戻すなら、<strong>B を戻してから A を戻す</strong>（スタックの順序） |
| `TryMerge` | 合体できるとき、`next` の「新しい値」を自分に移す。`next` を履歴には積まない |

`Services\Undo\IHistoryService.cs`:

```csharp
namespace Editor.Services.Undo;

public interface IHistoryService
{
    bool CanUndo { get; }
    bool CanRedo { get; }
    string? UndoName { get; }
    string? RedoName { get; }
    bool IsDirty { get; }                // 保存の後で、変更があるか

    void Execute(IUndoCommand command);  // 実行して、履歴に積む
    void Undo();
    void Redo();

    // 複数の操作を 1 つにまとめる（ギズモのドラッグなど）
    void BeginTransaction(string name);
    void CommitTransaction();

    void Clear();                        // シーンを開き直したとき
    void MarkSaved();                    // 保存したとき

    event Action? Changed;
}
```

### 履歴の実装

`Services\Undo\HistoryService.cs`:

```csharp
using System.Diagnostics;

namespace Editor.Services.Undo;

public sealed class HistoryService : IHistoryService
{
    private const int MaxHistory = 200;
    private static readonly long MergeWindowTicks = Stopwatch.Frequency * 7 / 10;   // 0.7 秒

    private readonly List<IUndoCommand> _done = new();
    private readonly Stack<IUndoCommand> _undone = new();
    private CompositeCommand? _transaction;
    private long _lastExecuteTicks;

    private IUndoCommand? _savePoint;            // 保存した時点の、先頭のコマンド
    private bool _savePointBroken;               // 保存点が、合体や削除で失われた

    public event Action? Changed;

    public bool CanUndo => _done.Count > 0;
    public bool CanRedo => _undone.Count > 0;
    public string? UndoName => CanUndo ? _done[^1].Name : null;
    public string? RedoName => CanRedo ? _undone.Peek().Name : null;
    public bool IsDirty => _savePointBroken || (_done.Count > 0 ? _done[^1] : null) != _savePoint;
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `Stack<T>` | 後入れ先出しの入れ物（C++ の `std::stack`）。`Push`、`Pop`、`Peek`（先頭を見る） |
| `Stopwatch.Frequency` | 1 秒あたりのティック数。時間を整数で比べるときの単位 |
| `static readonly` | 一度だけ計算して、変えない値 |
| `IsDirty` | 保存点（保存したときの先頭のコマンド）と、今の先頭が違えば、「未保存の変更がある」 |

```csharp
    public void Execute(IUndoCommand command)
    {
        // トランザクション中は、まとめる入れ物に入れる（履歴にはまだ積まない）
        if (_transaction != null)
        {
            _transaction.AddAndDo(command);
            return;
        }

        command.Do();

        long now = Stopwatch.GetTimestamp();
        bool canMerge = _done.Count > 0 && now - _lastExecuteTicks < MergeWindowTicks && _done[^1].TryMerge(command);
        _lastExecuteTicks = now;

        if (canMerge)
        {
            if (ReferenceEquals(_done[^1], _savePoint)) _savePointBroken = true;    // 保存点の中身が変わった
        }
        else
        {
            _done.Add(command);
        }

        _undone.Clear();                         // 新しい編集で、Redo の履歴は捨てる
        TrimHistory();
        Changed?.Invoke();
    }

    public void Undo()
    {
        if (!CanUndo) return;
        var command = _done[^1];
        _done.RemoveAt(_done.Count - 1);
        command.Undo();
        _undone.Push(command);
        _lastExecuteTicks = 0;                   // Undo のあとは、直前のコマンドと合体させない
        Changed?.Invoke();
    }

    public void Redo()
    {
        if (!CanRedo) return;
        var command = _undone.Pop();
        command.Do();
        _done.Add(command);
        _lastExecuteTicks = 0;
        Changed?.Invoke();
    }

    public void BeginTransaction(string name)
    {
        if (_transaction != null) throw new InvalidOperationException("トランザクションの入れ子はできません");
        _transaction = new CompositeCommand(name);
    }

    public void CommitTransaction()
    {
        var transaction = _transaction ?? throw new InvalidOperationException("トランザクションが始まっていません");
        _transaction = null;
        if (transaction.IsEmpty) return;         // 何も起きなかった（クリックしただけのドラッグ）
        _done.Add(transaction);                  // すでに実行済みなので、Do は呼ばない
        _undone.Clear();
        TrimHistory();
        Changed?.Invoke();
    }

    public void Clear()
    {
        _done.Clear();
        _undone.Clear();
        _transaction = null;
        _savePoint = null;
        _savePointBroken = false;
        Changed?.Invoke();
    }

    public void MarkSaved()
    {
        _savePoint = _done.Count > 0 ? _done[^1] : null;
        _savePointBroken = false;
        Changed?.Invoke();
    }

    private void TrimHistory()
    {
        while (_done.Count > MaxHistory)
        {
            if (ReferenceEquals(_done[0], _savePoint)) _savePointBroken = true;
            _done.RemoveAt(0);
        }
    }
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `Stopwatch.GetTimestamp()` | 高精度のタイムスタンプ（ティック） |
| 時間による合体 | 0.7 秒以内の、<strong>同じ対象・同じプロパティ</strong>の編集は、1 つにまとめる（スライダーを動かし続ける間など）。条件は、`TryMerge` が判定する |
| `ReferenceEquals(a, b)` | 参照が同じか（`==` が演算子オーバーロードされていても、確実に同一かどうかを調べる） |
| トランザクション | 開始から確定までの全コマンドを、1 つの `CompositeCommand` にまとめ、確定時に履歴へ積む |
| `?? throw …` | `null` なら例外を投げる式（第 27 章） |
| 上限 `MaxHistory` | 無限に溜めない。古いものから捨てる |

## 手順 2：ドキュメントを、復元しやすくする

Undo で物を復元するには、<strong>元の場所（兄弟の中の順番）に戻す</strong>必要があります。`SceneDocument` の `Create` と `Reparent` に、`index` を足します。

```csharp
public SceneObject Create(string name, SceneObject? parent = null, uint? id = null, int index = -1)
{
    // …（第 34 章と同じ）
    var siblings = parent?.Children ?? Roots;
    if (index < 0 || index > siblings.Count) siblings.Add(obj);
    else siblings.Insert(index, obj);
    Changed?.Invoke(new SceneChange(SceneChangeKind.Created, obj));
    return obj;
}

public void Reparent(SceneObject obj, SceneObject? newParent, int index = -1)
{
    // …（輪の検査は、第 34 章と同じ）
    (obj.Parent?.Children ?? Roots).Remove(obj);
    obj.Parent = newParent;
    var siblings = newParent?.Children ?? Roots;
    if (index < 0 || index > siblings.Count) siblings.Add(obj);
    else siblings.Insert(index, obj);
    Changed?.Invoke(new SceneChange(SceneChangeKind.Reparented, obj));
}

public int IndexOf(SceneObject obj) => (obj.Parent?.Children ?? Roots).IndexOf(obj);
```

### スナップショット

削除する物の「全部の情報」を、木ごと保存します。

`Services\Undo\Snapshots.cs`:

```csharp
using System.Numerics;
using Editor.Models;

namespace Editor.Services.Undo;

// 物 1 つ分（子を含む）の、保存された状態
public sealed record ObjectSnapshot(
    uint Id, string Name, Vector3 Position, Vector3 RotationDegrees, Vector3 Scale, Vector4 Color,
    IReadOnlyList<ObjectSnapshot> Children)
{
    public static ObjectSnapshot Take(SceneObject o) => new(
        o.Id, o.Name, o.Position, o.RotationDegrees, o.Scale, o.Color,
        o.Children.Select(Take).ToList());

    // 復元する。parent の下の index の位置に、同じ ID で再作成する
    public SceneObject Restore(SceneDocument document, SceneObject? parent, int index)
    {
        var obj = document.Create(Name, parent, Id, index);
        obj.Position = Position;
        obj.RotationDegrees = RotationDegrees;
        obj.Scale = Scale;
        obj.Color = Color;
        document.NotifyChanged(SceneChangeKind.TransformChanged, obj);
        document.NotifyChanged(SceneChangeKind.ColorChanged, obj);
        foreach (var child in Children) child.Restore(document, obj, -1);
        return obj;
    }
}

// 削除のとき、親と並び順も一緒に覚える
public sealed record RemovedObject(ObjectSnapshot Snapshot, uint ParentId, int Index);
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `record ObjectSnapshot(…)` | 値を運ぶだけの入れ物。コンストラクターとプロパティが、自動で作られる。<strong>作った後は変わらない</strong>ので、履歴に安全に保存できる |
| `o.Children.Select(Take).ToList()` | 子を再帰的に `Take` する。メソッド名をそのまま渡せる（メソッド グループ） |
| `Take` と `Restore` | 保存と復元の対。<strong>項目を足したら、両方に足す</strong> |
| `Restore` の中の `NotifyChanged` | 復元したとき、エンジンにも変換・色を送る（`Created` は、既定の値で作るので） |

## 手順 3：具体的なコマンド

### 値の変更

`Services\Undo\SetValueCommand.cs`:

```csharp
namespace Editor.Services.Undo;

// 物の 1 つのプロパティを変える。物は、ID で覚える（復元で別のオブジェクトになっても、辿れる）。
public sealed class SetValueCommand<T> : IUndoCommand
{
    private readonly uint _id;
    private readonly string _property;
    private readonly Action<uint, T> _apply;
    private readonly T _oldValue;
    private T _newValue;

    public SetValueCommand(string name, uint id, string property, T oldValue, T newValue, Action<uint, T> apply)
    {
        Name = name;
        _id = id;
        _property = property;
        _oldValue = oldValue;
        _newValue = newValue;
        _apply = apply;
    }

    public string Name { get; }

    public void Do() => _apply(_id, _newValue);
    public void Undo() => _apply(_id, _oldValue);

    public bool TryMerge(IUndoCommand next)
    {
        if (next is SetValueCommand<T> other && other._id == _id && other._property == _property)
        {
            _newValue = other._newValue;       // 古い値は保ち、新しい値だけを更新する
            return true;
        }
        return false;
    }
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `SetValueCommand<T>` | ジェネリックなクラス。`Vector3` にも `Vector4` にも `string` にも使える |
| `Action<uint, T> apply` | 「ID の物に、値を設定する」関数。<strong>どう設定するか</strong>は、外から渡す |
| `next is SetValueCommand<T> other && …` | 型の判定と取り出し。同じ ID・同じプロパティなら合体 |
| 古い値を保つ | 合体しても `_oldValue` は最初のまま。Undo すると、<strong>ドラッグ前の値</strong>に戻る |

### 作成、削除、親子づけ

`Services\Undo\StructureCommands.cs`:

```csharp
using Editor.Models;

namespace Editor.Services.Undo;

public sealed class CreateObjectCommand : IUndoCommand
{
    private readonly SceneDocument _document;
    private readonly string _objectName;
    private readonly uint _parentId;
    private readonly uint _id;
    private readonly Action<SceneObject>? _initialize;

    public CreateObjectCommand(SceneDocument document, string name, uint parentId, uint id, Action<SceneObject>? initialize)
    {
        _document = document;
        _objectName = name;
        _parentId = parentId;
        _id = id;
        _initialize = initialize;
    }

    public string Name => $"{_objectName} を作成";

    public void Do()
    {
        var parent = _parentId == 0 ? null : _document.Find(_parentId);
        var obj = _document.Create(_objectName, parent, _id);
        _initialize?.Invoke(obj);
    }

    public void Undo()
    {
        var obj = _document.Find(_id);
        if (obj != null) _document.Destroy(obj);
    }

    public bool TryMerge(IUndoCommand next) => false;
}

public sealed class DestroyObjectsCommand : IUndoCommand
{
    private readonly SceneDocument _document;
    private readonly List<RemovedObject> _removed = new();

    // 選択された物のうち、「親も選ばれている物」は除く（親が消えれば、子も消えるので）
    public DestroyObjectsCommand(SceneDocument document, IEnumerable<SceneObject> targets)
    {
        _document = document;
        var set = targets.ToHashSet();
        foreach (var o in targets)
        {
            bool ancestorIncluded = false;
            for (var p = o.Parent; p != null; p = p.Parent) if (set.Contains(p)) { ancestorIncluded = true; break; }
            if (ancestorIncluded) continue;
            _removed.Add(new RemovedObject(ObjectSnapshot.Take(o), o.Parent?.Id ?? 0, document.IndexOf(o)));
        }
    }

    public string Name => _removed.Count == 1 ? $"{_removed[0].Snapshot.Name} を削除" : $"{_removed.Count} 個を削除";

    public void Do()
    {
        foreach (var r in _removed)
        {
            var obj = _document.Find(r.Snapshot.Id);
            if (obj != null) _document.Destroy(obj);
        }
    }

    public void Undo()
    {
        // 削除した順の逆に復元すると、並び順（Index）が元通りになる
        for (int i = _removed.Count - 1; i >= 0; --i)
        {
            var r = _removed[i];
            var parent = r.ParentId == 0 ? null : _document.Find(r.ParentId);
            r.Snapshot.Restore(_document, parent, r.Index);
        }
    }

    public bool TryMerge(IUndoCommand next) => false;
}

public sealed class ReparentCommand : IUndoCommand
{
    private readonly SceneDocument _document;
    private readonly uint _id;
    private readonly uint _oldParentId, _newParentId;
    private readonly int _oldIndex;

    public ReparentCommand(SceneDocument document, SceneObject obj, SceneObject? newParent)
    {
        _document = document;
        _id = obj.Id;
        _oldParentId = obj.Parent?.Id ?? 0;
        _oldIndex = document.IndexOf(obj);
        _newParentId = newParent?.Id ?? 0;
    }

    public string Name => "親を変更";

    public void Do() => Move(_newParentId, -1);
    public void Undo() => Move(_oldParentId, _oldIndex);

    private void Move(uint parentId, int index)
    {
        var obj = _document.Find(_id);
        if (obj == null) return;
        var parent = parentId == 0 ? null : _document.Find(parentId);
        _document.Reparent(obj, parent, index);
    }

    public bool TryMerge(IUndoCommand next) => false;
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| 作成コマンドが ID を覚える | 最初の作成で決まった ID を、`Do`（Redo）でも使う。Redo で別の ID になると、後ろの履歴が壊れる |
| `ToHashSet()` | 集合（`HashSet<T>`）に変える。`Contains` が速い |
| 親が選ばれている物を除く | 親と子の両方を削除対象にすると、子が二重に復元される |
| 逆順で復元 | 削除したときの並びの位置（`Index`）を使うので、後ろから戻す |
| 「<strong>ID</strong>で探す」 | コマンドは、`SceneObject` の参照を持たず、`_document.Find(_id)` で毎回探す。削除と復元で別のオブジェクトになっても、同じ ID なら見つかる |

## 手順 4：ISceneEditor を拡張して、Undo 対応版を作る

`ISceneEditor` に、構造の操作を足します。

```csharp
SceneObject CreateObject(string name, SceneObject? parent, Vector3? position = null);
void DestroyObjects(IReadOnlyList<SceneObject> objects);
void Reparent(SceneObject obj, SceneObject? newParent);
```

第 36 章の `SceneEditor` は、「<strong>値を直接変える</strong>」実装でした。これを、そのまま「内側の実装」として残し、<strong>履歴を記録する外側の実装</strong>を、新しく作ります。

`Services\UndoableSceneEditor.cs`:

```csharp
using System.Numerics;
using Editor.Models;
using Editor.Services.Undo;

namespace Editor.Services;

// 編集を、Undo 可能なコマンドにして、履歴に積む。実際の変更は、内側の SceneEditor が行う。
public sealed class UndoableSceneEditor : ISceneEditor
{
    private readonly SceneDocument _document;
    private readonly SceneEditor _inner;
    private readonly IHistoryService _history;

    public UndoableSceneEditor(SceneDocument document, SceneEditor inner, IHistoryService history)
    {
        _document = document;
        _inner = inner;
        _history = history;
    }

    public void SetName(SceneObject obj, string name)
    {
        if (obj.Name == name) return;
        _history.Execute(new SetValueCommand<string>("名前を変更", obj.Id, "Name", obj.Name, name,
            (id, v) => { if (_document.Find(id) is { } o) _inner.SetName(o, v); }));
    }

    public void SetPosition(SceneObject obj, Vector3 value)
    {
        if (obj.Position == value) return;
        _history.Execute(new SetValueCommand<Vector3>("位置を変更", obj.Id, "Position", obj.Position, value,
            (id, v) => { if (_document.Find(id) is { } o) _inner.SetPosition(o, v); }));
    }

    public void SetRotationDegrees(SceneObject obj, Vector3 value)
    {
        if (obj.RotationDegrees == value) return;
        _history.Execute(new SetValueCommand<Vector3>("回転を変更", obj.Id, "Rotation", obj.RotationDegrees, value,
            (id, v) => { if (_document.Find(id) is { } o) _inner.SetRotationDegrees(o, v); }));
    }

    public void SetScale(SceneObject obj, Vector3 value)
    {
        if (obj.Scale == value) return;
        _history.Execute(new SetValueCommand<Vector3>("拡大を変更", obj.Id, "Scale", obj.Scale, value,
            (id, v) => { if (_document.Find(id) is { } o) _inner.SetScale(o, v); }));
    }

    public void SetColor(SceneObject obj, Vector4 value)
    {
        if (obj.Color == value) return;
        _history.Execute(new SetValueCommand<Vector4>("色を変更", obj.Id, "Color", obj.Color, value,
            (id, v) => { if (_document.Find(id) is { } o) _inner.SetColor(o, v); }));
    }

    public SceneObject CreateObject(string name, SceneObject? parent, Vector3? position = null)
    {
        uint id = _document.AllocateId();
        _history.Execute(new CreateObjectCommand(_document, name, parent?.Id ?? 0, id,
            o => { if (position is { } p) _inner.SetPosition(o, p); }));
        return _document.Find(id)!;
    }

    public void DestroyObjects(IReadOnlyList<SceneObject> objects)
    {
        if (objects.Count == 0) return;
        _history.Execute(new DestroyObjectsCommand(_document, objects));
    }

    public void Reparent(SceneObject obj, SceneObject? newParent)
    {
        if (obj.Parent == newParent) return;
        _history.Execute(new ReparentCommand(_document, obj, newParent));
    }
}
```

`SceneEditor`（内側の実装）にも、同じ 3 つのメソッドを足します。ただし、内側が実際に行うのは、プロパティの設定だけなので、`CreateObject` などは、`NotSupportedException` にするか、`ISceneEditor` を分けて、内側は値の設定だけを持つようにします。ここでは、<strong>値の設定用の小さなインターフェース</strong>に分けます。

```csharp
// 値を直接設定する（Undo なし）。内側の実装が、これを実装する。
public interface IRawSceneEditor
{
    void SetName(SceneObject obj, string name);
    void SetPosition(SceneObject obj, Vector3 value);
    void SetRotationDegrees(SceneObject obj, Vector3 value);
    void SetScale(SceneObject obj, Vector3 value);
    void SetColor(SceneObject obj, Vector4 value);
}
```

`SceneEditor : IRawSceneEditor`（第 36 章の中身はそのまま）にし、`UndoableSceneEditor` は `IRawSceneEditor _inner` を受け取ります。登録は、次のとおりです。

```csharp
containerRegistry.RegisterSingleton<IHistoryService, HistoryService>();
containerRegistry.RegisterSingleton<IRawSceneEditor, SceneEditor>();
containerRegistry.RegisterSingleton<ISceneEditor, UndoableSceneEditor>();
```

<strong>`PropertyViewModel` は、1 行も変えずに、Undo に対応しました。</strong> `ISceneEditor` の窓口を通していたからです。

## 手順 5：呼び出し側を窓口に切り替える

### シーン ツリー

`SceneTreeViewModel` の `_document.Create` / `Destroy` / `Reparent` を、`ISceneEditor` の呼び出しに変えます。

```csharp
private void AddEmpty()
{
    var obj = _editor.CreateObject($"Object {_document.AllocateId()}", null);
    _selection.Select(obj);
}

private void AddChild()
{
    var parent = _selection.Primary;
    if (parent == null) return;
    var obj = _editor.CreateObject($"Object {_document.AllocateId()}", parent, new Vector3(0, 1, 0));
    _selection.Select(obj);
}

private void Delete() => _editor.DestroyObjects(_selection.Selection.ToList());

public void Reparent(SceneObject dragged, SceneObject? newParent) => _editor.Reparent(dragged, newParent);
```

### ギズモのドラッグ

ドラッグの開始から終わりまでを<strong>トランザクション</strong>にします。

```csharp
// GizmoController
public bool TryBeginDrag(float px, float py)
{
    // …（当たり判定）
    _history.BeginTransaction("移動");
    // …
}

public void EndDrag()
{
    _history.CommitTransaction();       // ドラッグ中の何百回もの SetPosition が、1 つの Undo になる
    _dragAxis = -1;
    // …
}
```

トランザクション中は、`Execute` が `CompositeCommand.AddAndDo` を通ります。連続した `SetValueCommand<Vector3>`（同じ ID・同じプロパティ）は、<strong>合体</strong>されて 1 つになります。ドラッグ中の位置の移動は、結局 1 つの `SetValueCommand` に収まります。

## 手順 6：メニューとキー

`MainWindowViewModel`:

```csharp
public MainWindowViewModel(IHistoryService history /* ほか */)
{
    _history = history;
    UndoCommand = new DelegateCommand(_history.Undo, () => _history.CanUndo);
    RedoCommand = new DelegateCommand(_history.Redo, () => _history.CanRedo);

    _history.Changed += () =>
    {
        UndoCommand.RaiseCanExecuteChanged();
        RedoCommand.RaiseCanExecuteChanged();
        RaisePropertyChanged(nameof(UndoHeader));
        RaisePropertyChanged(nameof(RedoHeader));
    };
}

public DelegateCommand UndoCommand { get; }
public DelegateCommand RedoCommand { get; }
public string UndoHeader => _history.UndoName is { } n ? $"元に戻す: {n}(_U)" : "元に戻す(_U)";
public string RedoHeader => _history.RedoName is { } n ? $"やり直し: {n}(_R)" : "やり直し(_R)";
```

`MainWindow.xaml`:

```xml
<Window.InputBindings>
    <KeyBinding Key="Z" Modifiers="Control" Command="{Binding UndoCommand}" />
    <KeyBinding Key="Y" Modifiers="Control" Command="{Binding RedoCommand}" />
    <KeyBinding Key="Z" Modifiers="Control+Shift" Command="{Binding RedoCommand}" />
</Window.InputBindings>
<!-- … -->
<MenuItem Header="{Binding UndoHeader}" Command="{Binding UndoCommand}" InputGestureText="Ctrl+Z" />
<MenuItem Header="{Binding RedoHeader}" Command="{Binding RedoCommand}" InputGestureText="Ctrl+Y" />
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `Window.InputBindings` | ウィンドウ全体で効くキー操作 |
| `Modifiers="Control+Shift"` | 修飾キーの組み合わせ |
| `InputGestureText` | メニューに出す、ショートカットの表示（飾りだけで、機能はしない。機能は `KeyBinding`） |
| `TextBox` の中の `Ctrl+Z` | `TextBox` は自分の文字入力の Undo を持っていて、優先される。入力欄にフォーカスがあるときは、その入力の中だけで元に戻る。これは、<strong>期待される動作</strong>（確定前の入力の取り消し） |

## 手順 7：ダーティ フラグ

`IHistoryService.IsDirty` を使って、ウィンドウのタイトルに `*` を付けます（保存は、第 39 章）。

```csharp
public string Title => _history.IsDirty ? "MiniEngine Editor *" : "MiniEngine Editor";
// _history.Changed で RaisePropertyChanged(nameof(Title)) を呼ぶ
```

## 動作確認

| 操作 | 期待する結果 |
| --- | --- |
| 「＋ 追加」→ `Ctrl+Z` | 物が消える。`Ctrl+Y` で復活（同じ名前、同じ場所） |
| 位置を変更 → `Ctrl+Z` | 元の位置に戻る。メニューに「元に戻す: 位置を変更」が出る |
| ギズモで長くドラッグ → `Ctrl+Z` | 1 回の Undo で、ドラッグ前の位置に戻る |
| 色のスライダーを動かす → `Ctrl+Z` | 1 回で、動かす前の色に戻る |
| 親を持つ物を削除 → `Ctrl+Z` | 子も含めて、元通りに復活。並び順も同じ |
| Undo → 別の編集 | Redo ができなくなる（メニューが灰色） |
| 削除 → 復元 → その前の編集を Undo | クラッシュしない（ID で探すので） |
| 保存の後で編集 | タイトルに `*` が付く。Undo で保存時点に戻ると消える |

## よくあるミス

??? failure "Undo すると例外が出る（オブジェクトが見つからない）"
    コマンドが `SceneObject` の参照を持っている。ID を覚えて、実行時に `document.Find(id)` で探す。

??? failure "ドラッグが 1 回の Undo にならない"
    トランザクションを使っていない。または、`TryMerge` の条件（同じ ID、同じプロパティ）が合っていない。

??? failure "Undo で復活した物の子が、消えている"
    スナップショットの `Children` を再帰的に `Restore` していない。または、`DestroyObjectsCommand` が、子を選択に含めて、二重に扱っている。

??? failure "Redo すると、ID が変わる"
    `CreateObjectCommand` が、`Do` のたびに新しい ID を採番している。最初の ID を覚えて、使い回す。

??? failure "Undo のあとにスライダーを動かすと、直前のコマンドと合体してしまう"
    時間による合体の判定が、Undo の後もそのまま。`Undo` と `Redo` で `_lastExecuteTicks = 0` にして、合体の対象にしない。

??? failure "Undo/Redo の途中で、また編集コマンドが積まれて、履歴が壊れる"
    Undo 中の `Do/Undo` の中で、`ISceneEditor` ではなく<strong>内側の `IRawSceneEditor`</strong> を呼んでいるか確認する。窓口（`UndoableSceneEditor`）を呼ぶと、履歴に二重に積まれる。

## この章のまとめ

- 編集を、`Do()` と `Undo()` を持つ<strong>コマンド</strong>にする。
- 連続した操作は、<strong>トランザクション</strong>と<strong>合体（`TryMerge`）</strong>で 1 つにまとめる。
- コマンドは、オブジェクトの参照ではなく <strong>ID</strong> を覚える。削除は、<strong>スナップショット</strong>で復元する。
- `ISceneEditor` という窓口を作っておいたので、<strong>呼び出し側を変えずに</strong> Undo に対応できた。

## 次の章へ

次の章（[第 39 章 保存と読み込み](39-save-load.md)）では、シーンを JSON のファイルに保存し、読み込み直せるようにします。`System.Text.Json`、ファイル ダイアログ、非同期の入出力、ダーティ時の確認ダイアログを扱います。
