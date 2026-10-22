using System.ComponentModel.Composition;
using Microsoft.VisualStudio.LanguageServer.Client;
using Microsoft.VisualStudio.Utilities;

namespace KHlsl.Vsix
{
    /// <summary>"hlsl" コンテンツ タイプと、拡張子の対応。</summary>
    internal static class KHlslContentType
    {
        // 他の HLSL 拡張や VS 標準も "hlsl" を使うので、同じ名前にそろえる。
        // 名前が違うと、同じ拡張子の割り当てが競合して、言語クライアントが起動しない。
        public const string Name = "hlsl";

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
}
