using System.Net;
using Microsoft.AspNetCore.Mvc.Testing;
using Xunit;

namespace SentinelBrief.WebApi.Tests;

/// <summary>Verifies the static demo page is served at the site root.</summary>
public class DemoPageTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly WebApplicationFactory<Program> _factory;

    public DemoPageTests(WebApplicationFactory<Program> factory)
    {
        _factory = factory;
    }

    [Fact]
    public async Task Root_ServesHtmlDemoPage()
    {
        var client = _factory.CreateClient();

        var response = await client.GetAsync("/");

        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        Assert.Equal("text/html", response.Content.Headers.ContentType?.MediaType);
        var html = await response.Content.ReadAsStringAsync();
        Assert.Contains("SentinelBrief", html);
    }
}
