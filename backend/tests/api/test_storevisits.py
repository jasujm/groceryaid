"""Test store visit API"""

import decimal

import fastapi


def test_get_store_visit(testclient, storevisit):
    store_visit_url = f"http://testserver/api/v1/storevisits/{storevisit.id}"
    response = testclient.get(store_visit_url)
    store_url = f"http://testserver/api/v1/stores/{storevisit.store_id}"
    assert response.status_code == fastapi.status.HTTP_200_OK
    response_json = response.json()
    assert response_json == {
        "self": store_visit_url,
        "id": str(storevisit.id),
        "store": store_url,
        "cart": {
            "items": [
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
            "total_price": response_json["cart"]["total_price"],
        },
    }


def test_get_store_visit_not_found(testclient, faker):
    response = testclient.get(f"http://testserver/api/v1/storevisits/{faker.uuid4()}")
    assert response.status_code == fastapi.status.HTTP_404_NOT_FOUND


def test_post_store_visit(testclient, store, product, faker):
    store_url = f"http://testserver/api/v1/stores/{store.id}"
    product_url = f"{store_url}/products/{product.ean}"
    quantity = faker.pyint(min_value=1, max_value=999)
    response = testclient.post(
        "http://testserver/api/v1/storevisits",
        json={
            "store": store_url,
            "cart": {
                "items": [
                    {
                        "product": product_url,
                        "quantity": quantity,
                    }
                ],
            },
        },
    )
    assert response.status_code == fastapi.status.HTTP_201_CREATED, response.text
    storevisit_url = response.headers["Location"]
    storevisit_in_response = response.json()
    assert storevisit_in_response == {
        "self": storevisit_url,
        "id": storevisit_in_response["id"],
        "store": store_url,
        "cart": {
            "items": [
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
            "total_price": storevisit_in_response["cart"]["total_price"],
        },
    }


def test_post_store_visit_ean_lookup(testclient, store, product, faker):
    store_url = f"http://testserver/api/v1/stores/{store.id}"
    quantity = faker.pyint(min_value=1, max_value=999)
    response = testclient.post(
        "http://testserver/api/v1/storevisits",
        json={
            "store": store_url,
            "cart": {
                "items": [
                    {
                        "product": product.ean,
                        "quantity": quantity,
                    }
                ],
            },
        },
    )
    assert response.status_code == fastapi.status.HTTP_201_CREATED, response.text
    storevisit_url = response.headers["Location"]
    expected_storevisit_id = storevisit_url.split("/")[-1]
    response = testclient.get(storevisit_url)
    response_json = response.json()
    assert response_json == {
        "self": storevisit_url,
        "id": expected_storevisit_id,
        "store": store_url,
        "cart": {
            "items": [
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
            "total_price": response_json["cart"]["total_price"],
        },
    }


def test_post_store_visit_variable_price_ean_lookup(
    testclient, store, variable_price_product
):
    store_url = f"http://testserver/api/v1/stores/{store.id}"
    variable_price = decimal.Decimal("12.34")
    variable_price_ean = variable_price_product.ean.get_ean_with_price(variable_price)
    response = testclient.post(
        "http://testserver/api/v1/storevisits",
        json={
            "store": store_url,
            "cart": {
                "items": [{"product": variable_price_ean}],
            },
        },
    )
    assert response.status_code == fastapi.status.HTTP_201_CREATED, response.text
    storevisit_url = response.headers["Location"]
    expected_storevisit_id = storevisit_url.split("/")[-1]
    response = testclient.get(storevisit_url)
    response_json = response.json()
    assert response_json == {
        "self": storevisit_url,
        "id": expected_storevisit_id,
        "store": store_url,
        "cart": {
            "items": [
                {
                    "product": {
                        "self": f"{store_url}/products/{variable_price_product.ean}",
                        "store": store_url,
                        "ean": variable_price_product.ean,
                        "name": variable_price_product.name,
                        "price": float(variable_price),
                    },
                    "quantity": None,
                    "total_price": float(variable_price),
                }
            ],
            "total_price": response_json["cart"]["total_price"],
        },
    }


def test_post_store_visit_unknown_store(testclient, faker):
    response = testclient.post(
        "http://testserver/api/v1/storevisits",
        json={
            "store": faker.uuid4(),
        },
    )
    assert response.status_code == fastapi.status.HTTP_400_BAD_REQUEST


def test_post_store_visit_unknown_product(testclient, store, faker):
    store_url = f"http://testserver/api/v1/stores/{store.id}"
    product_url = f"{store_url}/products/{faker.ean()}"
    response = testclient.post(
        "http://testserver/api/v1/storevisits",
        json={
            "store": store_url,
            "cart": {
                "items": [
                    {
                        "product": product_url,
                        "quantity": 1,
                    }
                ],
            },
        },
    )
    assert response.status_code == fastapi.status.HTTP_400_BAD_REQUEST


def test_post_store_visit_variable_price_with_quantity(
    testclient, store, variable_price_product
):
    store_url = f"http://testserver/api/v1/stores/{store.id}"
    response = testclient.post(
        "http://testserver/api/v1/storevisits",
        json={
            "store": store_url,
            "cart": {
                "items": [{"product": variable_price_product.ean, "quantity": 1}],
            },
        },
    )
    assert (
        response.status_code == fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY
    ), response.text


def test_put_store_visit(testclient, storevisit, store, product, faker):
    storevisit_url = f"http://testserver/api/v1/storevisits/{storevisit.id}"
    store_url = f"http://testserver/api/v1/stores/{store.id}"
    product_url = f"{store_url}/products/{product.ean}"
    quantity = faker.pyint(min_value=1, max_value=999)
    response = testclient.put(
        storevisit_url,
        json={
            "cart": {
                "items": [
                    {
                        "product": product_url,
                        "quantity": quantity,
                    }
                ],
            }
        },
    )
    assert response.status_code == fastapi.status.HTTP_200_OK, response.text
    response_json = response.json()
    assert response_json == {
        "self": storevisit_url,
        "id": str(storevisit.id),
        "store": store_url,
        "cart": {
            "items": [
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
            "total_price": response_json["cart"]["total_price"],
        },
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
    quantity = faker.pyint(min_value=1, max_value=999)
    response = testclient.patch(
        storevisit_url,
        headers={"Content-Type": "application/json-patch+json"},
        json=[
            {"op": "replace", "path": "/cart/items", "value": []},
            {
                "op": "add",
                "path": "/cart/items/0",
                "value": {"product": product_url, "quantity": quantity},
            },
        ],
    )
    assert response.status_code == fastapi.status.HTTP_200_OK, response.text
    response_json = response.json()
    assert response_json == {
        "self": storevisit_url,
        "id": str(storevisit.id),
        "store": store_url,
        "cart": {
            "items": [
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
            "total_price": response_json["cart"]["total_price"],
        },
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


def test_get_grouped_store_visit_cart(testclient, storevisit):
    store_visit_url = f"http://testserver/api/v1/storevisits/{storevisit.id}"
    response = testclient.get(f"{store_visit_url}/bins")
    assert response.status_code == fastapi.status.HTTP_200_OK
    response_json = response.json()
    assert response_json["store_visit"] == store_visit_url
    # The bin packing isn't deterministic, so just check that the products are present
    eans_in_response = set(
        item["product"]["ean"]
        for cart in response_json["binned_cart"]
        for item in cart["items"]
    )
    expected_eans = set(cartproduct.ean for cartproduct in storevisit.cart)
    assert eans_in_response == expected_eans
