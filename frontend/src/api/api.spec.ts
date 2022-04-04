import nock from "nock";

import { storeFactory, storeVisitFactory } from "../test/factories";

import { getStores, createStoreVisit, getStoreVisit } from "./client";

const stores = storeFactory.buildList(3);
const storeVisit = storeVisitFactory.build();

describe("api", () => {
  let scope: nock.Scope;

  beforeEach(() => {
    scope = nock("http://localhost");
  });

  afterEach(() => {
    nock.cleanAll();
  });

  describe("getStores", () => {
    it("returns stores", async () => {
      scope.get("/api/v1/stores").reply(200, stores);
      expect(await getStores()).toEqual(stores);
    });
  });

  describe("createStoreVisit", () => {
    it("creates store visit", async () => {
      const store = storeVisit.store;
      scope
        .post("/api/v1/storevisits", { store: store })
        .reply(201, storeVisit);
      expect(await createStoreVisit(store)).toEqual(storeVisit);
    });
  });

  describe("getStoreVisit", () => {
    beforeEach(() => {
      scope.get(`/api/v1/storevisits/${storeVisit.id}`).reply(200, storeVisit);
    });

    it("returns store visit by id", async () => {
      expect(await getStoreVisit(storeVisit.id)).toEqual(storeVisit);
    });

    it("returns store visit by url", async () => {
      expect(await getStoreVisit(storeVisit.self)).toEqual(storeVisit);
    });
  });
});
