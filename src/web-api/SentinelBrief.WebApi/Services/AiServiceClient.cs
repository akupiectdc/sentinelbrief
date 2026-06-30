using System.Net;
using System.Net.Http.Json;
using System.Text.Json;
using System.Text.Json.Serialization;
using SentinelBrief.WebApi.Models;

namespace SentinelBrief.WebApi.Services;

/// <summary>
/// Typed HttpClient for the Python ai-service. The gateway forwards AI-related
/// work here and implements no RAG logic itself.
/// </summary>
public class AiServiceClient
{
    // The ai-service speaks snake_case (Pydantic). Map to/from PascalCase DTOs.
    private static readonly JsonSerializerOptions JsonOptions = new(JsonSerializerDefaults.Web)
    {
        PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
        DictionaryKeyPolicy = JsonNamingPolicy.SnakeCaseLower,
        DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
    };

    private readonly HttpClient _httpClient;

    public AiServiceClient(HttpClient httpClient)
    {
        _httpClient = httpClient;
    }

    /// <summary>Returns the ai-service's non-secret runtime configuration.</summary>
    public async Task<InfoResponse> GetInfoAsync(CancellationToken cancellationToken = default)
    {
        return (await _httpClient.GetFromJsonAsync<InfoResponse>(
            "/info", JsonOptions, cancellationToken))!;
    }

    /// <summary>Returns true if the ai-service health endpoint responds successfully.</summary>
    public async Task<bool> IsHealthyAsync(CancellationToken cancellationToken = default)
    {
        try
        {
            using var response = await _httpClient.GetAsync("/health", cancellationToken);
            return response.IsSuccessStatusCode;
        }
        catch (HttpRequestException)
        {
            return false;
        }
        catch (TaskCanceledException)
        {
            return false;
        }
    }

    public async Task<DocumentMetadata> IngestDocumentAsync(
        IngestRequest request, CancellationToken cancellationToken = default)
    {
        using var response = await _httpClient.PostAsJsonAsync(
            "/documents", request, JsonOptions, cancellationToken);
        response.EnsureSuccessStatusCode();
        return (await response.Content.ReadFromJsonAsync<DocumentMetadata>(
            JsonOptions, cancellationToken))!;
    }

    public async Task<DocumentList> ListDocumentsAsync(CancellationToken cancellationToken = default)
    {
        return (await _httpClient.GetFromJsonAsync<DocumentList>(
            "/documents", JsonOptions, cancellationToken))!;
    }

    /// <summary>Returns the document, or null if the ai-service reports 404.</summary>
    public async Task<DocumentDetail?> GetDocumentAsync(
        string documentId, CancellationToken cancellationToken = default)
    {
        using var response = await _httpClient.GetAsync(
            $"/documents/{Uri.EscapeDataString(documentId)}", cancellationToken);
        if (response.StatusCode == HttpStatusCode.NotFound)
        {
            return null;
        }
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<DocumentDetail>(
            JsonOptions, cancellationToken);
    }

    public async Task<SearchResponse> SearchAsync(
        SearchRequest request, CancellationToken cancellationToken = default)
    {
        using var response = await _httpClient.PostAsJsonAsync(
            "/search", request, JsonOptions, cancellationToken);
        response.EnsureSuccessStatusCode();
        return (await response.Content.ReadFromJsonAsync<SearchResponse>(
            JsonOptions, cancellationToken))!;
    }

    public async Task<AnswerResponse> AskAsync(
        AskRequest request, CancellationToken cancellationToken = default)
    {
        using var response = await _httpClient.PostAsJsonAsync(
            "/ask", request, JsonOptions, cancellationToken);
        response.EnsureSuccessStatusCode();
        return (await response.Content.ReadFromJsonAsync<AnswerResponse>(
            JsonOptions, cancellationToken))!;
    }
}
