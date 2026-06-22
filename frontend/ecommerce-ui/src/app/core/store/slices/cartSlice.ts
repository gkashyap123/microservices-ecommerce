import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type { Cart } from "../../../shared/types";

interface CartState {
  cart: Cart | null;
  itemCount: number;
}

const initialState: CartState = {
  cart:      null,
  itemCount: 0,
};

const cartSlice = createSlice({
  name: "cart",
  initialState,
  reducers: {
    setCart(state, action: PayloadAction<Cart>) {
      state.cart      = action.payload;
      state.itemCount = action.payload.total_items;
    },
    clearCart(state) {
      state.cart      = null;
      state.itemCount = 0;
    },
  },
});

export const { setCart, clearCart } = cartSlice.actions;
export default cartSlice.reducer;