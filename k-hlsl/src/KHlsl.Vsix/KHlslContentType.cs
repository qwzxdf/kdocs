using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel.Composition;
using System.IO;
using Microsoft.VisualStudio.LanguageServer.Client;
using Microsoft.VisualStudio.Text;
using Microsoft.VisualStudio.Text.Editor;
using Microsoft.VisualStudio.Utilities;

namespace KHlsl.Vsix
{
    /// <summary>"hlsl" コンテンツ タイプと、拡張子の対応。</summary>
    internal static class KHlslContentType
    {
        public const string Name = "khlsl";

        public static readonly HashSet<string> Extensions = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
        {
            ".hlsl", ".hlsli", ".fx", ".fxh", ".vsh", ".psh", ".gsh", ".hsh", ".dsh", ".csh", ".msh", ".ash",
            ".usf", ".ush", ".compute"
        };

        [Export]
        [Name(Name)]
        [BaseDefinition(CodeRemoteContentDefinition.CodeRemoteContentTypeName)]
        [BaseDefinition("code")]
        internal static ContentTypeDefinition Definition;

        [Export] [FileExtension(".hlsl")] [ContentType(Name)] internal static FileExtensionToContentTypeDefinition Hlsl;
        [Export] [FileExtension(".hlsli")] [ContentType(Name)] internal static FileExtensionToContentTypeDefinition Hlsli;
        [Export] [FileExtension(".fx")] [ContentType(Name)] internal static FileExtensionToContentTypeDefinition Fx;
        [Export] [FileExtension(".fxh")] [ContentType(Name)] internal static FileExtensionToContentTypeDefinition Fxh;
        [Export] [FileExtension(".vsh")] [ContentType(Name)] internal static FileExtensionToContentTypeDefinition Vsh;
        [Export] [FileExtension(".psh")] [ContentType(Name)] internal static FileExtensionToContentTypeDefinition Psh;
        [Export] [FileExtension(".gsh")] [ContentType(Name)] internal static FileExtensionToContentTypeDefinition Gsh;
        [Export] [FileExtension(".hsh")] [ContentType(Name)] internal static FileExtensionToContentTypeDefinition Hsh;
        [Export] [FileExtension(".dsh")] [ContentType(Name)] internal static FileExtensionToContentTypeDefinition Dsh;
        [Export] [FileExtension(".csh")] [ContentType(Name)] internal static FileExtensionToContentTypeDefinition Csh;
        [Export] [FileExtension(".msh")] [ContentType(Name)] internal static FileExtensionToContentTypeDefinition Msh;
        [Export] [FileExtension(".ash")] [ContentType(Name)] internal static FileExtensionToContentTypeDefinition Ash;
        [Export] [FileExtension(".usf")] [ContentType(Name)] internal static FileExtensionToContentTypeDefinition Usf;
        [Export] [FileExtension(".ush")] [ContentType(Name)] internal static FileExtensionToContentTypeDefinition Ush;
        [Export] [FileExtension(".compute")] [ContentType(Name)] internal static FileExtensionToContentTypeDefinition Compute;
    }

    /// <summary>
    /// 保険。VS の起動直後など、KHlslPackage が読み込まれる前に開かれたファイルは、
    /// ビューが作られるときに切り替える。
    /// </summary>
    [Export(typeof(IWpfTextViewConnectionListener))]
    [ContentType("text")]
    [TextViewRole(PredefinedTextViewRoles.Document)]
    internal sealed class KHlslContentTypeFallback : IWpfTextViewConnectionListener
    {
        [Import] internal IContentTypeRegistryService ContentTypes { get; set; }
        [Import] internal ITextDocumentFactoryService Documents { get; set; }

        public void SubjectBuffersConnected(IWpfTextView textView, ConnectionReason reason, Collection<ITextBuffer> subjectBuffers)
        {
            foreach (var buffer in subjectBuffers)
            {
                try
                {
                    if (buffer.ContentType.IsOfType(KHlslContentType.Name)) continue;
                    ITextDocument doc;
                    if (!Documents.TryGetTextDocument(buffer, out doc) || string.IsNullOrEmpty(doc.FilePath)) continue;
                    if (!KHlslContentType.Extensions.Contains(Path.GetExtension(doc.FilePath))) continue;
                    var ct = ContentTypes.GetContentType(KHlslContentType.Name);
                    if (ct != null) buffer.ChangeContentType(ct, null);
                }
                catch (Exception) { }
            }
        }

        public void SubjectBuffersDisconnected(IWpfTextView textView, ConnectionReason reason, Collection<ITextBuffer> subjectBuffers) { }
    }
}
