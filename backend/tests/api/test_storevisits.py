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
                "product": {
                    "self": f"{store_url}/products/{product.ean}",
                    "store": store_url,
                    "ean": product.ean,
                    "name": product.name,
                    "price": float(product.price),
                },
                "quantity": product.quantity,
                "total_price": float(product.quantity * product.price),
            }
            for product in storevisit.cart
        ],
    }


def test_get_store_visit_not_found(testclient, faker):
    response = testclient.get(f"http://testserver/api/v1/storevisits/{faker.uuid4()}")
    assert response.status_code == fastapi.status.HTTP_404_NOT_FOUND


def test_post_store_visit(testclient, store, product, faker):
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
    storevisit_in_response = response.json()
    assert storevisit_in_response == {
        "self": storevisit_url,
        "id": storevisit_in_response["id"],
        "store": store_url,
        "cart": [
            {
                "product": {
                    "self": product_url,
                    "store": store_url,
                    "ean": product.ean,
                    "name": product.name,
                    "price": float(product.price),
                },
                "quantity": quantity,
                "total_price": float(product.price * quantity),
            }
        ],
    }


def test_post_store_visit_ean_lookup(testclient, store, product, faker):
    store_url = f"http://testserver/api/v1/stores/{store.id}"
    quantity = faker.pyint(min_value=1)
    response = testclient.post(
        "http://testserver/api/v1/storevisits",
        json={
            "store": store_url,
            "cart": [
                {
                    "product": product.ean,
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
                "product": {
                    "self": f"{store_url}/products/{product.ean}",
                    "store": store_url,
                    "ean": product.ean,
                    "name": product.name,
                    "price": float(product.price),
                },
                "quantity": quantity,
                "total_price": float(product.price * quantity),
            }
        ],
    }


def test_post_store_visit_unknown_store(testclient, faker):
    response = testclient.post(
        "http://testserver/api/v1/storevisits",
        json={
            "store": faker.uuid4(),
        },
    )
    assert response.status_code == fastapi.status.HTTP_400_BAD_REQUEST


def test_post_store_visit_duplicate_product(testclient, store, product, faker):
    response = testclient.post(
        "http://testserver/api/v1/storevisits",
        json={
            "store": str(store.id),
            "cart": [
                {
                    "product": product.ean,
                    "quantity": faker.pyint(min_value=1),
                },
                {
                    "product": product.ean,
                    "quantity": faker.pyint(min_value=1),
                },
            ],
        },
    )
    assert response.status_code == fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY


def test_post_store_visit_unknown_product(testclient, store, faker):
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


def test_put_store_visit(testclient, storevisit, store, product, faker):
    storevisit_url = f"http://testserver/api/v1/storevisits/{storevisit.id}"
    store_url = f"http://testserver/api/v1/stores/{store.id}"
    product_url = f"{store_url}/products/{product.ean}"
    quantity = faker.pyint(min_value=1)
    response = testclient.put(
        storevisit_url,
        json={
            "cart": [
                {
                    "product": product_url,
                    "quantity": quantity,
                }
            ],
        },
    )
    assert response.status_code == fastapi.status.HTTP_200_OK, response.text
    assert response.json() == {
        "self": storevisit_url,
        "id": str(storevisit.id),
        "store": store_url,
        "cart": [
            {
                "product": {
                    "self": f"{store_url}/products/{product.ean}",
                    "store": store_url,
                    "ean": product.ean,
                    "name": product.name,
                    "price": float(product.price),
                },
                "quantity": quantity,
                "total_price": float(product.price * quantity),
            }
        ],
    }


def test_put_store_visit_not_found(testclient, faker):
    response = testclient.put(
        f"http://testserver/api/v1/storevisits/{faker.uuid4()}", json={"cart": []}
    )
    assert response.status_code == fastapi.status.HTTP_404_NOT_FOUND


def test_patch_store_visit(testclient, storevisit, store, product, faker):
    storevisit_url = f"http://testserver/api/v1/storevisits/{storevisit.id}"
    store_url = f"http://testserver/api/v1/stores/{store.id}"
    product_url = f"{store_url}/products/{product.ean}"
    quantity = faker.pyint(min_value=1)
    response = testclient.patch(
        storevisit_url,
        headers={"Content-Type": "application/json-patch+json"},
        json=[
            {"op": "replace", "path": "/cart", "value": []},
            {
                "op": "add",
                "path": "/cart/0",
                "value": {"product": product_url, "quantity": quantity},
            },
        ],
    )
    assert response.status_code == fastapi.status.HTTP_200_OK, response.text
    assert response.json() == {
        "self": storevisit_url,
        "id": str(storevisit.id),
        "store": store_url,
        "cart": [
            {
                "product": {
                    "self": f"{store_url}/products/{product.ean}",
                    "store": store_url,
                    "ean": product.ean,
                    "name": product.name,
                    "price": float(product.price),
                },
                "quantity": quantity,
                "total_price": float(product.price * quantity),
            }
        ],
    }


def test_patch_store_visit_invalid_content_type(testclient, storevisit):
    response = testclient.patch(
        f"http://testserver/api/v1/storevisits/{storevisit.id}", json=[]
    )
    assert response.status_code == fastapi.status.HTTP_415_UNSUPPORTED_MEDIA_TYPE


def test_patch_store_visit_not_found(testclient, faker):
    response = testclient.patch(
        f"http://testserver/api/v1/storevisits/{faker.uuid4()}",
        headers={"Content-Type": "application/json-patch+json"},
        json=[],
    )
    assert response.status_code == fastapi.status.HTTP_404_NOT_FOUND


def test_patch_store_visit_failed_patch(testclient, storevisit):
    storevisit_url = f"http://testserver/api/v1/storevisits/{storevisit.id}"
    response = testclient.patch(
        storevisit_url,
        headers={"Content-Type": "application/json-patch+json"},
        json=[
            {
                "op": "test",
                "path": "/store",
                "value": "this is not a astore",
            },
        ],
    )
    assert response.status_code == fastapi.status.HTTP_409_CONFLICT


def test_patch_store_visit_invalid_model(testclient, storevisit):
    storevisit_url = f"http://testserver/api/v1/storevisits/{storevisit.id}"
    response = testclient.patch(
        storevisit_url,
        headers={"Content-Type": "application/json-patch+json"},
        json=[
            {
                "op": "add",
                "path": "/cart",
                "value": "this is not a cart",
            },
        ],
    )
    assert response.status_code == fastapi.status.HTTP_400_BAD_REQUEST
