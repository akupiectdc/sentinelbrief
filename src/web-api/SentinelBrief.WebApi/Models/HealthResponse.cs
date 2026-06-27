namespace SentinelBrief.WebApi.Models;

/// <summary>Gateway health response.</summary>
public record HealthResponse(string Status, string Service);

/// <summary>Result of probing the downstream ai-service.</summary>
public record AiHealthResponse(bool AiServiceReachable);
