import {
  TypedUseSelectorHook,
  useDispatch as baseUseDispatch,
  useSelector as baseUseSelector,
} from "react-redux";
import type { RootState, AppDispatch } from "./store";

export const useDispatch = () => baseUseDispatch<AppDispatch>();
export const useSelector: TypedUseSelectorHook<RootState> = baseUseSelector;
