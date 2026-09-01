[RoutePrefix("api/orders")]
public class OrdersController {
    [HttpGet]
    [Route("{id}")]
    public OrderDto Get(int id) { return null; }

    [HttpPost]
    public OrderDto Create(CreateOrder request) { return null; }
}
