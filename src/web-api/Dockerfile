# C# web-api gateway image.
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

COPY SentinelBrief.WebApi/SentinelBrief.WebApi.csproj SentinelBrief.WebApi/
RUN dotnet restore SentinelBrief.WebApi/SentinelBrief.WebApi.csproj

COPY SentinelBrief.WebApi/ SentinelBrief.WebApi/
RUN dotnet publish SentinelBrief.WebApi/SentinelBrief.WebApi.csproj -c Release -o /app/publish

FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
COPY --from=build /app/publish .
EXPOSE 5000
ENV ASPNETCORE_URLS=http://0.0.0.0:5000
ENTRYPOINT ["dotnet", "SentinelBrief.WebApi.dll"]
