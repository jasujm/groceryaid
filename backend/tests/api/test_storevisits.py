"""Test store visit API"""

import fastapi


def test_get_store_visit(testclient, storevisit):
    store_visit_url = f"http://testserver/api/v1/storevisits/{storevisit.id}"
    response = testclient.get(store_visit_url)
    store_url = f"http://testserver/api/v1/stores/{storevisit.store_id}"
    assert response.status_code == fastapi.status.HTTP_200_OK
    assert response.json() == {
        "self": store_visit_url,
        "id": str(storevisit.id),
        "store": store_url,
        "cart": [
            {
                "product": f"{store_url}/products/{product.ean}",
                "quantity": product.quantity,
            }
            for product in storevisit.cart
        ],
    }


def test_get_store_visit_not_found(testclient, faker):
    response = testclient.get(f"http://testserver/api/v1/storevisits/{faker.uuid4()}")
    assert response.status_code == fastapi.status.HTTP_404_NOT_FOUND
