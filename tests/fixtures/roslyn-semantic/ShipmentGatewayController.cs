using System;

namespace Sample.Shipments;

public class ControllerBase { }

[AttributeUsage(AttributeTargets.Class | AttributeTargets.Method)]
public sealed class RouteAttribute(string template) : Attribute { }

[AttributeUsage(AttributeTargets.Method)]
public sealed class HttpGetAttribute(string template) : Attribute { }

[AttributeUsage(AttributeTargets.Class | AttributeTargets.Method)]
public sealed class AuthorizeAttribute : Attribute
{
    public string? Policy { get; set; }
    public string? Roles { get; set; }
}

[Route("api/shipments")]
public class ShipmentGatewayController : ControllerBase
{
    [Authorize(Policy = "shipments.read")]
    [HttpGet("{trackingCode}")]
    public ShipmentSummary Fetch(string trackingCode) => BuildSummary(trackingCode);

    private ShipmentSummary BuildSummary(string trackingCode) => new() { TrackingCode = trackingCode, Status = "ready" };
}

public class ShipmentSummary
{
    public string TrackingCode { get; set; } = "";
    public string Status { get; set; } = "";
}
