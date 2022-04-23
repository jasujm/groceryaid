import axios, { AxiosResponse } from "axios";
import { Store, StoreVisit, GroupedCart, Product } from "./types";

const HTTP_URL_RE = /^(http:|https:)/;

const apiOrigin = process.env.REACT_APP_GROCERYAID_API_ORIGIN ?? "";
const client = axios.create({
  baseURL: `${apiOrigin}/api/v1`,
  timeout: 1000,
});

interface ErrorMessage {
  detail: string;
}

export class ApiError extends Error {}

function throwApiError(err: unknown): never {
  if (axios.isAxiosError(err)) {
    if (err.response) {
      const errorMessage = err.response.data as ErrorMessage;
      throw new ApiError(errorMessage.detail);
    }
  }
  throw new ApiError((err as Error)?.message ?? "Unknown error");
}

async function respondWithErrorHandling<Data>(
  request: Promise<AxiosResponse<Data>>
) {
  try {
    const response = await request;
    return response.data as Data;
  } catch (err) {
    throwApiError(err);
  }
}

function getStoreUrl(idOrUrl: string) {
  return idOrUrl.match(HTTP_URL_RE) ? idOrUrl : `/stores/${idOrUrl}`;
}

function getStoreVisitUrl(idOrUrl: string) {
  return idOrUrl.match(HTTP_URL_RE) ? idOrUrl : `/storevisits/${idOrUrl}`;
}

export async function getStores() {
  return respondWithErrorHandling<Store[]>(client.get("/stores"));
}

export async function getProduct(store: string, ean: string) {
  const url = `${getStoreUrl(store)}/products/${ean}`;
  return await respondWithErrorHandling<Product>(client.get(url));
}

export async function createStoreVisit(store: string) {
  return await respondWithErrorHandling<StoreVisit>(
    client.post("/storevisits", { store })
  );
}

export async function getStoreVisit(storeVisit: string) {
  const url = getStoreVisitUrl(storeVisit);
  return await respondWithErrorHandling<StoreVisit>(client.get(url));
}

export async function updateStoreVisit(storeVisit: StoreVisit, patch: unknown) {
  return await respondWithErrorHandling<StoreVisit>(
    client.patch(storeVisit.self, patch, {
      headers: { "content-type": "application/json-patch+json" },
    })
  );
}

export async function getGroupedStoreVisitCart(storeVisit: string) {
  const url = `${getStoreVisitUrl(storeVisit)}/bins`;
  return await respondWithErrorHandling<GroupedCart>(client.get(url));
}
