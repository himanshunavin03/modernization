using System.Security.Cryptography;
using System.Text.Json;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;

var options = ParseArguments(args);
var sourceRoot = Path.GetFullPath(Required(options, "--source-root"));
var projectId = Required(options, "--project-id");
var outputPath = Required(options, "--output");
var inputs = Directory.EnumerateFiles(sourceRoot, "*.cs", SearchOption.AllDirectories)
    .Select(path => new SourceInput(path, Path.GetRelativePath(sourceRoot, path).Replace('\\', '/'), File.ReadAllText(path)))
    .ToList();
var trees = inputs.Select(input => CSharpSyntaxTree.ParseText(input.Text, path: input.Path)).ToList();
var references = ((string?)AppContext.GetData("TRUSTED_PLATFORM_ASSEMBLIES"))?.Split(Path.PathSeparator).Select(MetadataReference.CreateFromFile).ToList() ?? [];
var compilation = CSharpCompilation.Create("PolarisSemantic", trees, references, new CSharpCompilationOptions(OutputKind.DynamicallyLinkedLibrary));
var facts = new List<Fact>();
var actionTypeIds = new HashSet<string>();

foreach (var input in inputs)
{
    var tree = trees.Single(tree => tree.FilePath == input.Path);
    var model = compilation.GetSemanticModel(tree);
    var root = tree.GetRoot();
    var context = new FileContext(projectId, input);
    foreach (var declaration in root.DescendantNodes().OfType<BaseNamespaceDeclarationSyntax>())
    {
        var symbol = model.GetDeclaredSymbol(declaration);
        facts.Add(context.CreateFact("namespace", symbol?.ToDisplayString() ?? declaration.Name.ToString(), declaration,
            new() { ["identity"] = symbol is null ? declaration.Name.ToString() : SymbolId(symbol) }, symbol is not null,
            symbol is null ? "Roslyn could not resolve the declared namespace symbol." : null));
    }

    foreach (var type in root.DescendantNodes().OfType<TypeDeclarationSyntax>())
    {
        var typeSymbol = model.GetDeclaredSymbol(type);
        if (typeSymbol is null)
        {
            facts.Add(context.CreateFact("type", type.Identifier.Text, type, new(), false, "Roslyn could not resolve the declared type symbol."));
            continue;
        }
        var typeId = SymbolId(typeSymbol);
        var isController = IsController(typeSymbol);
        var controllerRoutes = Attributes(type.AttributeLists, model).Where(attribute => attribute.Resolved && IsAttribute(attribute, "RouteAttribute"))
            .Select(attribute => StaticTemplate(attribute.Syntax)).Where(template => template is not null).Cast<string>().ToList();
        facts.Add(context.CreateFact(isController ? "controller" : "type", typeSymbol.Name, type,
            new() { ["identity"] = typeId, ["namespace"] = typeSymbol.ContainingNamespace.ToDisplayString(), ["type_kind"] = typeSymbol.TypeKind.ToString() }, true, null));
        foreach (var attribute in Attributes(type.AttributeLists, model).Where(IsAuthorizationAttribute))
            facts.Add(AuthorizationFact(context, attribute, typeSymbol, "controller"));

        foreach (var property in type.Members.OfType<PropertyDeclarationSyntax>())
        {
            var propertySymbol = model.GetDeclaredSymbol(property);
            var propertyType = model.GetTypeInfo(property.Type).Type;
            var resolved = propertySymbol is not null && propertyType is not null && propertyType.TypeKind != TypeKind.Error;
            facts.Add(context.CreateFact("property", propertySymbol?.Name ?? property.Identifier.Text, property,
                new() { ["identity"] = propertySymbol is null ? $"{typeId}.{property.Identifier.Text}" : SymbolId(propertySymbol), ["owner_identity"] = typeId,
                    ["type_identity"] = propertyType is null ? property.Type.ToString() : SymbolId(propertyType), ["type_name"] = propertyType?.ToDisplayString() ?? property.Type.ToString() },
                resolved, resolved ? null : "Roslyn could not resolve the property declaration or property type."));
        }

        foreach (var method in type.Members.OfType<MethodDeclarationSyntax>())
        {
            var methodSymbol = model.GetDeclaredSymbol(method);
            var returnType = model.GetTypeInfo(method.ReturnType).Type;
            var isAction = isController && methodSymbol is not null && methodSymbol.DeclaredAccessibility == Accessibility.Public && !methodSymbol.IsStatic;
            var methodId = methodSymbol is null ? $"{typeId}.{method.Identifier.Text}" : SymbolId(methodSymbol);
            var resolved = methodSymbol is not null && returnType is not null && returnType.TypeKind != TypeKind.Error;
            if (isAction && returnType is not null && returnType.TypeKind != TypeKind.Error) actionTypeIds.Add(SymbolId(returnType));
            foreach (var parameter in method.ParameterList.Parameters)
            {
                var parameterType = parameter.Type is null ? null : model.GetTypeInfo(parameter.Type).Type;
                if (isAction && parameterType is not null && parameterType.TypeKind != TypeKind.Error) actionTypeIds.Add(SymbolId(parameterType));
                facts.Add(context.CreateFact("type_reference", parameterType?.ToDisplayString() ?? parameter.Type?.ToString() ?? "unknown", parameter,
                    new() { ["owner_identity"] = methodId, ["identity"] = parameterType is null ? parameter.Type?.ToString() : SymbolId(parameterType), ["usage"] = "parameter" },
                    parameterType is not null && parameterType.TypeKind != TypeKind.Error, parameterType is null || parameterType.TypeKind == TypeKind.Error ? "Roslyn could not resolve the parameter type." : null));
            }
            facts.Add(context.CreateFact(isAction ? "action" : "method", methodSymbol?.Name ?? method.Identifier.Text, method,
                new() { ["identity"] = methodId, ["owner_identity"] = typeId, ["return_type_identity"] = returnType is null ? method.ReturnType.ToString() : SymbolId(returnType), ["return_type_name"] = returnType?.ToDisplayString() ?? method.ReturnType.ToString() },
                resolved, resolved ? null : "Roslyn could not resolve the method declaration or return type."));
            facts.Add(context.CreateFact("type_reference", returnType?.ToDisplayString() ?? method.ReturnType.ToString(), method.ReturnType,
                new() { ["owner_identity"] = methodId, ["identity"] = returnType is null ? method.ReturnType.ToString() : SymbolId(returnType), ["usage"] = "return" },
                returnType is not null && returnType.TypeKind != TypeKind.Error, returnType is null || returnType.TypeKind == TypeKind.Error ? "Roslyn could not resolve the return type." : null));
            if (isAction)
            {
                foreach (var attribute in Attributes(method.AttributeLists, model))
                {
                    if (IsAuthorizationAttribute(attribute)) facts.Add(AuthorizationFact(context, attribute, methodSymbol!, "action"));
                }
                foreach (var attribute in Attributes(method.AttributeLists, model).Where(attribute => attribute.Resolved && IsEndpointAttribute(attribute)))
                {
                    var actionTemplate = StaticTemplate(attribute.Syntax);
                    var controllerTemplate = controllerRoutes.Count == 1 ? controllerRoutes[0] : null;
                    var combined = controllerTemplate is not null && actionTemplate is not null ? CombineRoute(controllerTemplate, actionTemplate) : null;
                    var verb = HttpVerb(attribute);
                    facts.Add(context.CreateFact("endpoint", $"{methodSymbol!.Name} {verb ?? "ROUTE"}", attribute.Syntax,
                        new() { ["identity"] = $"{methodId}:{verb ?? "ROUTE"}:{combined ?? actionTemplate ?? string.Empty}", ["owner_identity"] = methodId,
                            ["verb"] = verb, ["action_route_template"] = actionTemplate, ["controller_route_template"] = controllerTemplate, ["route_template"] = combined ?? actionTemplate }, true, null));
                }
            }
            foreach (var invocation in method.DescendantNodes().OfType<InvocationExpressionSyntax>())
            {
                var target = model.GetSymbolInfo(invocation).Symbol as IMethodSymbol;
                facts.Add(context.CreateFact("invocation", target?.Name ?? invocation.Expression.ToString(), invocation,
                    new() { ["owner_identity"] = methodId, ["target_identity"] = target is null ? invocation.Expression.ToString() : SymbolId(target), ["target_name"] = target?.ToDisplayString() ?? invocation.Expression.ToString() },
                    target is not null, target is null ? "Roslyn could not resolve the invocation target." : null));
            }
        }
    }
}

foreach (var fact in facts.Where(fact => fact.Kind == "type" && fact.Properties.TryGetValue("identity", out var identity) && identity is string typeId && actionTypeIds.Contains(typeId))) fact.Kind = "dto";

Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(outputPath))!);
File.WriteAllText(outputPath, JsonSerializer.Serialize(new { project_id = projectId, facts, warnings = Array.Empty<object>() }, new JsonSerializerOptions { WriteIndented = true, PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower }));

static Dictionary<string, string> ParseArguments(string[] args) => Enumerable.Range(0, args.Length / 2).ToDictionary(index => args[index * 2], index => args[index * 2 + 1]);
static string Required(Dictionary<string, string> values, string key) => values.TryGetValue(key, out var value) ? value : throw new ArgumentException($"Missing {key}.");
static string SymbolId(ISymbol symbol) => symbol.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat);
static bool IsController(INamedTypeSymbol symbol) => symbol.Name.EndsWith("Controller", StringComparison.Ordinal) || InheritsController(symbol);
static bool InheritsController(INamedTypeSymbol symbol) => symbol.BaseType is not null && (symbol.BaseType.Name.EndsWith("Controller", StringComparison.Ordinal) || InheritsController(symbol.BaseType));
static bool IsAttribute(AttributeInfo attribute, string name) => attribute.Symbol?.ContainingType.Name.Equals(name, StringComparison.Ordinal) == true;
static bool IsAuthorizationAttribute(AttributeInfo attribute) => attribute.Symbol?.ContainingType.Name.Contains("Authorize", StringComparison.Ordinal) == true;
static bool IsEndpointAttribute(AttributeInfo attribute) => IsAttribute(attribute, "RouteAttribute") || HttpVerb(attribute) is not null;
static string? HttpVerb(AttributeInfo attribute) => attribute.Symbol?.ContainingType.Name switch { "HttpGetAttribute" => "GET", "HttpPostAttribute" => "POST", "HttpPutAttribute" => "PUT", "HttpDeleteAttribute" => "DELETE", "HttpPatchAttribute" => "PATCH", _ => null };
static string? StaticTemplate(AttributeSyntax attribute) => attribute.ArgumentList?.Arguments.FirstOrDefault(argument => argument.NameEquals is null)?.Expression is LiteralExpressionSyntax literal && literal.IsKind(SyntaxKind.StringLiteralExpression) ? literal.Token.ValueText : null;
static string CombineRoute(string controller, string action) => $"{controller.TrimEnd('/')}/{action.TrimStart('/')}";
static IEnumerable<AttributeInfo> Attributes(SyntaxList<AttributeListSyntax> lists, SemanticModel model) => lists.SelectMany(list => list.Attributes).Select(attribute => new AttributeInfo(attribute, model.GetSymbolInfo(attribute).Symbol, model.GetSymbolInfo(attribute).Symbol is not null));
static Fact AuthorizationFact(FileContext context, AttributeInfo attribute, ISymbol owner, string ownerKind) => context.CreateFact("authorization_policy", attribute.Symbol?.ContainingType.Name ?? attribute.Syntax.Name.ToString(), attribute.Syntax,
    new() { ["identity"] = $"{SymbolId(owner)}:{attribute.Syntax}", ["owner_identity"] = SymbolId(owner), ["owner_kind"] = ownerKind, ["policy"] = NamedString(attribute.Syntax, "Policy"), ["roles"] = NamedString(attribute.Syntax, "Roles") }, attribute.Resolved, attribute.Resolved ? null : "Roslyn could not resolve the authorization attribute.");
static string? NamedString(AttributeSyntax attribute, string name) => attribute.ArgumentList?.Arguments.FirstOrDefault(argument => argument.NameEquals?.Name.Identifier.Text == name)?.Expression is LiteralExpressionSyntax literal && literal.IsKind(SyntaxKind.StringLiteralExpression) ? literal.Token.ValueText : null;

sealed record SourceInput(string Path, string Relative, string Text);
sealed record AttributeInfo(AttributeSyntax Syntax, ISymbol? Symbol, bool Resolved);
sealed class Fact(string kind, string name, string projectId, Evidence evidence, Dictionary<string, object?> properties)
{
    public string Kind { get; set; } = kind;
    public string Name { get; } = name;
    public string ProjectId { get; } = projectId;
    public Evidence Evidence { get; } = evidence;
    public Dictionary<string, object?> Properties { get; } = properties;
}
sealed record Evidence(string ProjectId, string SourcePath, int LineStart, int LineEnd, int ColumnStart, int ColumnEnd, string SourceHash, string Extractor, double Confidence, string ResolutionStatus, string? Diagnostic);
sealed class FileContext(string projectId, SourceInput input)
{
    private readonly string _hash = Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(input.Path))).ToLowerInvariant();
    public Fact CreateFact(string kind, string name, SyntaxNode node, Dictionary<string, object?> properties, bool resolved, string? diagnostic)
    {
        var span = node.GetLocation().GetLineSpan();
        var evidence = new Evidence(projectId, input.Relative, span.StartLinePosition.Line + 1, span.EndLinePosition.Line + 1, span.StartLinePosition.Character + 1, span.EndLinePosition.Character + 1, _hash, "roslyn", resolved ? 1.0 : 0.0, resolved ? "proven" : "unresolved", diagnostic);
        return new Fact(kind, name, projectId, evidence, properties);
    }
}
