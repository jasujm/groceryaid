import fastapi


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


def test_get_product_not_found(testclient, faker):
    response = testclient.get(
        f"http://testserver/apiv1/stores/{faker.uuid4()}/products/{faker.ean()}"
    )
    assert response.status_code == fastapi.status.HTTP_404_NOT_FOUND
