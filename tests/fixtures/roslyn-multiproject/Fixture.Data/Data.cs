namespace Fixture.Data;
public interface IStore { string Read(int id); }
public class Store : IStore { public string Read(int id) => id.ToString(); }
public static class StoreExtensions { public static T Identity<T>(this T value) => value; }
