"""Test stores API"""

import fastapi


def test_get_stores(testclient, store):
    response = testclient.get("http://testserver/api/v1/stores")
    assert response.status_code == fastapi.status.HTTP_200_OK
    assert response.json() == [
        {
            "self": f"http://testserver/api/v1/stores/{store.id}",
            "id": str(store.id),
            "chain": store.chain.value,
            "name": store.name,
        }
    ]


def test_get_store(testclient, store):
    store_url = f"http://testserver/api/v1/stores/{store.id}"
    response = testclient.get(store_url)
    assert response.status_code == fastapi.status.HTTP_200_OK
    assert response.json() == {
        "self": store_url,
        "id": str(store.id),
        "chain": store.chain.value,
        "name": store.name,
    }


def test_get_store_not_found(testclient, faker):
    response = testclient.get(f"http://testserver/apiv1/stores/{faker.uuid4()}")
    assert response.status_code == fastapi.status.HTTP_404_NOT_FOUND


def test_get_product(testclient, product):
    product_url = (
        f"http://testserver/api/v1/stores/{product.store_id}/products/{product.ean}"
    )
    response = testclient.get(product_url)
    assert response.status_code == fastapi.status.HTTP_200_OK
    assert response.json() == {
        "self": product_url,
        "store": f"http://testserver/api/v1/stores/{product.store_id}",
        "ean": product.ean,
        "name": product.name,
        "price": float(product.price),
    }


def test_get_product_variable_price(testclient, variable_price_product, faker):
    price = faker.pydecimal(positive=True, max_value=10, right_digits=2)
    ean = variable_price_product.ean.get_ean_with_price(price)
    store_url = f"http://testserver/api/v1/stores/{variable_price_product.store_id}"
    response = testclient.get(f"{store_url}/products/{ean}")
    assert response.status_code == fastapi.status.HTTP_200_OK, response.text
    assert response.json() == {
        "self": f"{store_url}/products/{variable_price_product.ean}",
        "store": f"http://testserver/api/v1/stores/{variable_price_product.store_id}",
        "ean": variable_price_product.ean,
        "name": variable_price_product.name,
        "price": float(variable_price_product.price),
    }


def test_get_product_not_found(testclient, faker):
    response = testclient.get(
        f"http://testserver/apiv1/stores/{faker.uuid4()}/products/{faker.ean()}"
    )
    assert response.status_code == fastapi.status.HTTP_404_NOT_FOUND
