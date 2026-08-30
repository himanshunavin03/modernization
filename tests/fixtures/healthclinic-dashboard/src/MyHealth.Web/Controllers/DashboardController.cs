using Microsoft.AspNet.Authorization;
public class DashboardController { [Authorize] public IActionResult Index() { return View(); } }
