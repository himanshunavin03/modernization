using Fixture.Data;
namespace Fixture.Business;
public class BaseService { public virtual string Format(string value) => value; }
public class Service : BaseService {
  private readonly IStore store;
  public Service(IStore store) { this.store = store; }
  public string Load(int id) => Format(store.Read(id).Identity());
  public string Load(string id) => Load(int.Parse(id));
}
