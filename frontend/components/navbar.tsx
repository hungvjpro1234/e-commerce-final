"use client";

import Link from "next/link";
import { ShoppingCart, LogOut, Package } from "lucide-react";
import { useAuthStore } from "@/lib/store";
import { ROLE_ADMIN, ROLE_CUSTOMER, ROLE_STAFF } from "@/lib/auth";
import { Button } from "./ui/button";
import { useRouter } from "next/navigation";

export function Navbar() {
  const { user, logout } = useAuthStore();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between">
        <div className="flex gap-6 md:gap-10">
          <Link href="/" className="flex items-center space-x-2">
            <Package className="h-6 w-6 text-primary" />
            <span className="inline-block font-bold">Nexus Shop</span>
          </Link>
          <nav className="hidden md:flex gap-6">
            <Link href="/" className="flex items-center text-sm font-medium text-muted-foreground hover:text-foreground">
              Products
            </Link>
            {user?.role === ROLE_CUSTOMER && (
              <Link href="/orders" className="flex items-center text-sm font-medium text-muted-foreground hover:text-foreground">
                Orders
              </Link>
            )}
            {user?.role === ROLE_ADMIN && (
              <Link href="/admin" className="flex items-center text-sm font-medium text-muted-foreground hover:text-foreground">
                Admin
              </Link>
            )}
            {user?.role === ROLE_STAFF && (
              <Link href="/staff" className="flex items-center text-sm font-medium text-muted-foreground hover:text-foreground">
                Staff
              </Link>
            )}
          </nav>
        </div>

        <div className="flex items-center gap-4">
          {user?.role === ROLE_CUSTOMER && (
            <Link href="/cart">
              <Button variant="ghost" size="icon" className="relative cursor-pointer">
                <ShoppingCart className="h-5 w-5" />
              </Button>
            </Link>
          )}

          {user ? (
            <div className="flex items-center gap-4">
              <span className="text-sm font-medium hidden md:inline-block">Hi, {user.first_name || user.username}</span>
              <Button variant="outline" size="sm" onClick={handleLogout}>
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </Button>
            </div>
          ) : (
            <div className="flex gap-2">
              <Link href="/login">
                <Button variant="ghost" size="sm">Login</Button>
              </Link>
              <Link href="/register">
                <Button size="sm">Register</Button>
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
