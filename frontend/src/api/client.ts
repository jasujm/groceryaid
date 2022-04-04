import axios from "axios";
import { Store, StoreVisit } from "./types";

const HTTP_URL_RE = /^(http:|https:)/;

const apiOrigin =
  process.env.REACT_APP_GROCERYAID_API_ORIGIN ?? "http://localhost";
const client = axios.create({
  baseURL: `${apiOrigin}/api/v1`,
  timeout: 1000,
});

export async function getStores() {
  const response = await client.get("/stores");
  return response.data as Store[];
}

export async function createStoreVisit(store: string) {
  const response = await client.post("/storevisits", { store });
  return response.data as StoreVisit;
}

export async function getStoreVisit(storeVisit: string) {
  const url = storeVisit.match(HTTP_URL_RE)
    ? storeVisit
    : `/storevisits/${storeVisit}`;
  const response = await client.get(url);
  return response.data as StoreVisit;
}
