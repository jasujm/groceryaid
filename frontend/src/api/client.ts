import axios from "axios";
import { Store, StoreVisit, GroupedCart } from "./types";

const HTTP_URL_RE = /^(http:|https:)/;

const apiOrigin =
  process.env.REACT_APP_GROCERYAID_API_ORIGIN ?? "http://localhost";
const client = axios.create({
  baseURL: `${apiOrigin}/api/v1`,
  timeout: 1000,
});

function getStoreVisitUrl(idOrUrl: string) {
  return idOrUrl.match(HTTP_URL_RE) ? idOrUrl : `/storevisits/${idOrUrl}`;
}

export async function getStores() {
  const response = await client.get("/stores");
  return response.data as Store[];
}

export async function createStoreVisit(store: string) {
  const response = await client.post("/storevisits", { store });
  return response.data as StoreVisit;
}

export async function getStoreVisit(storeVisit: string) {
  const url = getStoreVisitUrl(storeVisit);
  const response = await client.get(url);
  return response.data as StoreVisit;
}

export async function updateStoreVisit(storeVisit: StoreVisit, patch: unknown) {
  const response = await client.patch(storeVisit.self, patch, {
    headers: { "content-type": "application/json-patch+json" },
  });
  return response.data as StoreVisit;
}

export async function getGroupedStoreVisitCart(storeVisit: string) {
  const url = `${getStoreVisitUrl(storeVisit)}/bins`;
  const response = await client.get(url);
  return response.data as GroupedCart;
}
