using System.Net;
using System.Net.Http.Json;
using System.Text;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.AspNetCore.TestHost;
using Microsoft.Extensions.DependencyInjection;
using SentinelBrief.WebApi.Models;
using SentinelBrief.WebApi.Services;
using Xunit;

namespace SentinelBrief.WebApi.Tests;

/// <summary>
/// Tests the gateway's forwarding endpoints. The downstream ai-service HttpClient
/// is replaced with a stub handler, so no real Ollama/Qdrant/ai-service is needed.
/// The stub responds with snake_case JSON, like the Python service.
/// </summary>
public class GatewayEndpointTests : IClassFixture<GatewayEndpointTests.StubFactory>
{
    private readonly StubFactory _factory;

    public GatewayEndpointTests(StubFactory factory)
    {
        _factory = factory;
    }

    [Fact]
    public async Task Ask_ForwardsAndReturnsGroundedAnswerWithCitations()
    {
        var client = _factory.CreateClient();

        var response = await client.PostAsJsonAsync("/ask", new { question = "How are incidents reported?" });

        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        var body = await response.Content.ReadFromJsonAsync<AnswerResponse>();
        Assert.NotNull(body);
        Assert.False(body!.Refused);
        Assert.Contains("SOC", body.Answer);
        Assert.Equal("Incident Response Policy", body.Citations[0].SourceTitle);
        Assert.Equal("Incident Response Policy", body.RetrievedTitles[0]);
    }

    [Fact]
    public async Task Search_ForwardsAndReturnsResults()
    {
        var client = _factory.CreateClient();

        var response = await client.PostAsJsonAsync("/search", new { query = "incidents" });

        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        var body = await response.Content.ReadFromJsonAsync<SearchResponse>();
        Assert.NotNull(body);
        Assert.Equal(1, body!.Count);
        Assert.Equal("doc-1::chunk-0", body.Results[0].ChunkId);
    }

    [Fact]
    public async Task IngestDocument_ForwardsAndReturnsCreated()
    {
        var client = _factory.CreateClient();

        var response = await client.PostAsJsonAsync(
            "/documents", new { title = "T", text = "body", source_type = "synthetic" });

        Assert.Equal(HttpStatusCode.Created, response.StatusCode);
        var body = await response.Content.ReadFromJsonAsync<DocumentMetadata>();
        Assert.NotNull(body);
        Assert.Equal(3, body!.ChunkCount);
    }

    [Fact]
    public async Task GetDocument_Unknown_Returns404()
    {
        var client = _factory.CreateClient();

        var response = await client.GetAsync("/documents/missing");

        Assert.Equal(HttpStatusCode.NotFound, response.StatusCode);
    }

    [Fact]
    public async Task Ask_WhenAiServiceFails_Returns502()
    {
        var client = _factory.CreateClient();

        // The special question makes the stub return 500, simulating a downstream failure.
        var response = await client.PostAsJsonAsync("/ask", new { question = "boom" });

        Assert.Equal(HttpStatusCode.BadGateway, response.StatusCode);
    }

    /// <summary>Factory that swaps the ai-service client's handler for a stub.</summary>
    public class StubFactory : WebApplicationFactory<Program>
    {
        protected override void ConfigureWebHost(IWebHostBuilder builder)
        {
            builder.ConfigureTestServices(services =>
            {
                services.AddHttpClient<AiServiceClient>(c => c.BaseAddress = new Uri("http://ai-service.test"))
                    .ConfigurePrimaryHttpMessageHandler(() => new StubAiHandler());
            });
        }
    }

    private sealed class StubAiHandler : HttpMessageHandler
    {
        protected override async Task<HttpResponseMessage> SendAsync(
            HttpRequestMessage request, CancellationToken cancellationToken)
        {
            var path = request.RequestUri!.AbsolutePath;
            var method = request.Method;

            if (method == HttpMethod.Post && path == "/ask")
            {
                var content = request.Content is null
                    ? string.Empty
                    : await request.Content.ReadAsStringAsync(cancellationToken);
                if (content.Contains("boom"))
                {
                    return Json("{\"detail\":\"local model error\"}", HttpStatusCode.InternalServerError);
                }

                return Json(
                    """
                    {"answer":"Report incidents to the SOC without delay [Incident Response Policy].",
                     "citations":[{"source_title":"Incident Response Policy","chunk_id":"doc-1::chunk-0","score":0.82,"page_number":null}],
                     "retrieved_titles":["Incident Response Policy"],"refused":false}
                    """);
            }

            if (method == HttpMethod.Post && path == "/search")
            {
                return Json(
                    """
                    {"query":"incidents","count":1,"results":[
                      {"chunk_id":"doc-1::chunk-0","document_id":"doc-1","source_title":"Incident Response Policy",
                       "source_type":"synthetic","text":"Report incidents to the SOC.","score":0.82,"page_number":null}]}
                    """);
            }

            if (method == HttpMethod.Post && path == "/documents")
            {
                return Json(
                    """
                    {"document_id":"doc-1","title":"T","source_type":"synthetic","language":"en",
                     "filename":null,"url":null,"ingested_at":"2026-06-27T10:00:00Z","chunk_count":3}
                    """,
                    HttpStatusCode.Created);
            }

            if (method == HttpMethod.Get && path == "/documents")
            {
                return Json("""{"documents":[],"count":0}""");
            }

            if (method == HttpMethod.Get && path.StartsWith("/documents/"))
            {
                return Json(string.Empty, HttpStatusCode.NotFound);
            }

            return Json("{}", HttpStatusCode.NotFound);
        }

        private static HttpResponseMessage Json(string body, HttpStatusCode status = HttpStatusCode.OK)
            => new(status)
            {
                Content = new StringContent(body, Encoding.UTF8, "application/json"),
            };
    }
}
