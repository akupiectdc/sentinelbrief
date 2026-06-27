using Microsoft.AspNetCore.Diagnostics;
using SentinelBrief.WebApi.Models;
using SentinelBrief.WebApi.Services;

var builder = WebApplication.CreateBuilder(args);

// The ai-service URL is configuration-driven (env var AI_SERVICE_URL or the
// "AiService:Url" setting). It is never hardcoded in request-handling code.
var aiServiceUrl =
    builder.Configuration["AI_SERVICE_URL"]
    ?? builder.Configuration["AiService:Url"]
    ?? "http://localhost:8000";

builder.Services.AddHttpClient<AiServiceClient>(client =>
{
    client.BaseAddress = new Uri(aiServiceUrl);
});

var app = builder.Build();

// Translate a failed downstream (ai-service) call into 502 Bad Gateway.
app.UseExceptionHandler(handler => handler.Run(async context =>
{
    var error = context.Features.Get<IExceptionHandlerFeature>()?.Error;
    context.Response.StatusCode = error is HttpRequestException
        ? StatusCodes.Status502BadGateway
        : StatusCodes.Status500InternalServerError;
    await context.Response.WriteAsJsonAsync(new { error = "ai-service request failed" });
}));

// Serve the static demo page (wwwroot/index.html) at the site root.
app.UseDefaultFiles();
app.UseStaticFiles();

// Gateway health. Independent of the ai-service so it stays fast and dependency-free.
app.MapGet("/health", () => Results.Ok(new HealthResponse("ok", "web-api")));

// Forwards a health probe to the Python ai-service.
app.MapGet("/ai/health", async (AiServiceClient ai, CancellationToken ct) =>
{
    var reachable = await ai.IsHealthyAsync(ct);
    return Results.Ok(new AiHealthResponse(reachable));
});

// --- Forwarding endpoints. The gateway forwards AI work to the ai-service and
// implements no RAG logic itself. ---

app.MapPost("/documents", async (IngestRequest request, AiServiceClient ai, CancellationToken ct) =>
{
    var metadata = await ai.IngestDocumentAsync(request, ct);
    return Results.Created($"/documents/{metadata.DocumentId}", metadata);
});

app.MapGet("/documents", async (AiServiceClient ai, CancellationToken ct) =>
    Results.Ok(await ai.ListDocumentsAsync(ct)));

app.MapGet("/documents/{documentId}", async (string documentId, AiServiceClient ai, CancellationToken ct) =>
{
    var detail = await ai.GetDocumentAsync(documentId, ct);
    return detail is null ? Results.NotFound() : Results.Ok(detail);
});

app.MapPost("/search", async (SearchRequest request, AiServiceClient ai, CancellationToken ct) =>
    Results.Ok(await ai.SearchAsync(request, ct)));

app.MapPost("/ask", async (AskRequest request, AiServiceClient ai, CancellationToken ct) =>
    Results.Ok(await ai.AskAsync(request, ct)));

app.Run();

// Exposed so the test project can use WebApplicationFactory<Program>.
public partial class Program { }
