import { Link } from "react-router-dom";
import { ShoppingCart, Package, LogOut, User } from "lucide-react";
import { useSelector } from "react-redux";
import type { RootState } from "../../core/store/store";
import { useAuth } from "../../auth/hooks/useAuth";

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuth();
  const itemCount = useSelector((s: RootState) => s.cart.itemCount);

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">

        {/* Logo */}
        <Link to="/" className="text-xl font-bold text-blue-600">
          ShopApp
        </Link>

        {/* Nav Links */}
        <div className="flex items-center gap-6">
          <Link
            to="/products"
            className="text-sm text-gray-600 hover:text-blue-600 transition-colors"
          >
            Products
          </Link>

          {isAuthenticated && (
            <>
              <Link to="/orders" className="flex items-center gap-1
                text-sm text-gray-600 hover:text-blue-600">
                <Package size={16} /> Orders
              </Link>

              {/* Cart icon with badge */}
              <Link to="/cart" className="relative">
                <ShoppingCart size={20} className="text-gray-600 hover:text-blue-600" />
                {itemCount > 0 && (
                  <span className="absolute -top-2 -right-2 bg-blue-600
                    text-white text-xs rounded-full h-5 w-5
                    flex items-center justify-center font-medium">
                    {itemCount}
                  </span>
                )}
              </Link>

              <div className="flex items-center gap-2 text-sm text-gray-600">
                <User size={16} />
                <span>{user?.username}</span>
              </div>

              <button
                onClick={logout}
                className="flex items-center gap-1 text-sm
                  text-red-500 hover:text-red-700 transition-colors"
              >
                <LogOut size={16} /> Logout
              </button>
            </>
          )}

          {!isAuthenticated && (
            <div className="flex gap-3">
              <Link to="/login"
                className="text-sm text-gray-600 hover:text-blue-600">
                Login
              </Link>
              <Link to="/register"
                className="text-sm bg-blue-600 text-white px-4 py-1.5
                  rounded-lg hover:bg-blue-700">
                Sign Up
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}