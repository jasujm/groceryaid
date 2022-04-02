import axios from "axios";

export interface Store {
  self: string;
  id: string;
  name: string;
}

const apiOrigin = process.env.REACT_APP_GROCERYAID_API_ORIGIN ?? "";
const client = axios.create({
  baseURL: `${apiOrigin}/api/v1`,
  timeout: 1000,
});

export async function getStores() {
  const response = await client.get("/stores");
  return response.data as Store[];
}
