using Fixture.Business;
using Fixture.Data;
namespace Fixture.Web;
public class Runner { public string Run(int id) => new Service(new Store()).Load(id); }
