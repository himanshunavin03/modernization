namespace Fixture.Inaccessible;

public class Secret
{
    private void Hidden() { }
}

public class Caller
{
    public void Test(Secret secret)
    {
        secret.Hidden();
    }
}
