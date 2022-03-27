"""Test store visit API"""

import fastapi
import pytest


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


@pytest.mark.asyncio
async def test_post_store_visit(testclient, store, product, faker):
    store_url = f"http://testserver/api/v1/stores/{store.id}"
    product_url = f"{store_url}/products/{product.ean}"
    quantity = faker.pyint(min_value=1)
    response = testclient.post(
        "http://testserver/api/v1/storevisits",
        json={
            "store": store_url,
            "cart": [
                {
                    "product": product_url,
                    "quantity": quantity,
                }
            ],
        },
    )
    assert response.status_code == fastapi.status.HTTP_201_CREATED, response.text
    storevisit_url = response.headers["Location"]
    expected_storevisit_id = storevisit_url.split("/")[-1]
    response = testclient.get(storevisit_url)
    assert response.json() == {
        "self": storevisit_url,
        "id": expected_storevisit_id,
        "store": store_url,
        "cart": [
            {
                "product": product_url,
                "quantity": quantity,
            }
        ],
    }


@pytest.mark.asyncio
async def test_post_store_visit_ean_lookup(testclient, store, product, faker):
    store_url = f"http://testserver/api/v1/stores/{store.id}"
    quantity = faker.pyint(min_value=1)
    response = testclient.post(
        "http://testserver/api/v1/storevisits",
        json={
            "store": store_url,
            "cart": [
                {
                    "ean": product.ean,
                    "quantity": quantity,
                }
            ],
        },
    )
    assert response.status_code == fastapi.status.HTTP_201_CREATED, response.text
    storevisit_url = response.headers["Location"]
    expected_storevisit_id = storevisit_url.split("/")[-1]
    response = testclient.get(storevisit_url)
    assert response.json() == {
        "self": storevisit_url,
        "id": expected_storevisit_id,
        "store": store_url,
        "cart": [
            {
                "product": f"{store_url}/products/{product.ean}",
                "quantity": quantity,
            }
        ],
    }


@pytest.mark.asyncio
async def test_post_store_visit_unknown_store(testclient, faker):
    store_url = f"http://testserver/api/v1/stores/{faker.uuid4()}"
    response = testclient.post(
        "http://testserver/api/v1/storevisits",
        json={
            "store": store_url,
        },
    )
    assert response.status_code == fastapi.status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_post_store_visit_unknown_product(testclient, store, faker):
    store_url = f"http://testserver/api/v1/stores/{store.id}"
    product_url = f"{store_url}/products/{faker.ean()}"
    response = testclient.post(
        "http://testserver/api/v1/storevisits",
        json={
            "store": store_url,
            "cart": [
                {
                    "product": product_url,
                    "quantity": 1,
                }
            ],
        },
    )
    assert response.status_code == fastapi.status.HTTP_400_BAD_REQUEST
