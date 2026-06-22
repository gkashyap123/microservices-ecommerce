import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Provider } from "react-redux";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "react-hot-toast";
import "./App.css";
import { store } from "./app/core/store/store";
import { queryClient } from "./app/core/queryClient";
import Navbar from "./app/shared/components/Navbar";
import ProtectedRoute from "./app/shared/components/ProtectedRoute";
import LoginPage from "./app/auth/pages/LoginPage";
import RegisterPage from "./app/auth/pages/RegisterPage";
import ProductsPage from "./app/products/pages/ProductsPage";
import CartPage from "./app/cart/pages/CartPage";
import OrdersPage from "./app/orders/pages/OrdersPage";

export default function App() {
  return (
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Navbar />
          <Routes>
            {/* Public */}
            <Route path="/"         element={<Navigate to="/products" replace />} />
            <Route path="/login"    element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/products" element={<ProductsPage />} />

            {/* Protected */}
            <Route element={<ProtectedRoute />}>
              <Route path="/cart"   element={<CartPage />} />
              <Route path="/orders" element={<OrdersPage />} />
            </Route>
          </Routes>
          <Toaster position="top-right" />
        </BrowserRouter>
      </QueryClientProvider>
    </Provider>
  );
}