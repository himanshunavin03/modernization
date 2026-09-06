using System.Threading.Tasks;

namespace Alpha
{
    class CatalogWorker
    {
        async Task LoadByCategoryAsync(Category category)
        {
            await Task.Delay(1);
        }

        void Reconcile()
        {
        }

        void Reconcile(string value)
        {
        }

        void Reconcile<T>(T value)
        {
        }
    }
}

namespace Beta
{
    class CatalogWorker
    {
        void Reconcile()
        {
        }

        void PreserveTailMethod()
        {
        }
    }
}
