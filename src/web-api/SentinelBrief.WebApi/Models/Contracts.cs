namespace SentinelBrief.WebApi.Models;

// DTOs mirroring the Python ai-service contract. The gateway forwards these
// through verbatim; it adds no RAG logic. JSON snake_case <-> PascalCase mapping
// is handled by the serializer options in AiServiceClient.

public record IngestRequest(
    string Title,
    string Text,
    string SourceType = "user",
    string Language = "en",
    string? Filename = null,
    string? Url = null);

public record DocumentMetadata(
    string DocumentId,
    string Title,
    string SourceType,
    string Language,
    string? Filename,
    string? Url,
    DateTimeOffset IngestedAt,
    int ChunkCount);

public record Chunk(
    string DocumentId,
    string ChunkId,
    string SourceTitle,
    string SourceType,
    string Text,
    int CharacterStart,
    int CharacterEnd,
    int? PageNumber);

public record DocumentDetail(DocumentMetadata Document, IReadOnlyList<Chunk> Chunks);

public record DocumentList(IReadOnlyList<DocumentMetadata> Documents, int Count);

public record SearchRequest(string Query, int? TopK = null);

public record RetrievedChunkResult(
    string ChunkId,
    string DocumentId,
    string SourceTitle,
    string SourceType,
    string Text,
    double Score,
    int? PageNumber);

public record SearchResponse(string Query, int Count, IReadOnlyList<RetrievedChunkResult> Results);

public record AskRequest(string Question, int? TopK = null);

public record Citation(string SourceTitle, string ChunkId, double? Score, int? PageNumber);

public record AnswerResponse(
    string Answer,
    IReadOnlyList<Citation> Citations,
    IReadOnlyList<string> RetrievedTitles,
    bool Refused);
