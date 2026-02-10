import unittest


from models import Product
from services.product_service import ProductService


class ProductServiceTests(unittest.TestCase):

    def test_create_product(self):

        producto = ProductService.create(
            name="Producto de prueba",
            family="Forniture",
            price="100"
        )
        ProductService.delete(producto.id)
        name = producto.name

        self.assertEqual(name, "Producto de prueba", "[+] Crear producto pasado")

    def test_get_by_id(self):
        producto = ProductService.create(
            name="Producto de prueba",
            family="Forniture",
            price="100"
        )

        name = ProductService.get_by_id(producto.id).name
        ProductService.delete(producto.id)

        self.assertEqual(name, "Producto de prueba")


    def test_get_by_name(self):

        producto = ProductService.create(
            name="Producto de prueba",
            family="Forniture",
            price="100"
        )

        family = ProductService.get_by_name("Producto de prueba").family

        ProductService.delete(producto.id)

        self.assertEqual(family, "Forniture")

    def test_update_product(self):

        producto = ProductService.create(
            name="Producto de prueba",
            family="Forniture",
            price="100"
        )

        ProductService.update(
            product_id = producto.id,
            family = "Electronics",
        )

        family = ProductService.get_by_name("Producto de prueba").family

        ProductService.delete(producto.id)

        self.assertEqual("Electronics", family)


    def test_delete_product(self):
        producto = ProductService.create(
            name="Producto de prueba",
            family="Forniture",
            price="100"
        )

        ProductService.delete(producto.id)

        producto = ProductService.get_by_id(producto.id)

        self.assertEqual(producto, None)



if __name__ == "__main__":
    unittest.main()
