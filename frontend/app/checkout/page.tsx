"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import { useAuthStore } from "@/lib/store";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { useState } from "react";
import { Cart } from "@/types";
import { ArrowRight, Lock } from "lucide-react";

const checkoutSchema = z.object({
  address: z.string().min(5, "Address must be at least 5 characters"),
  simulate_payment_failure: z.boolean().default(false),
});

type CheckoutForm = z.infer<typeof checkoutSchema>;
type CheckoutFormInput = z.input<typeof checkoutSchema>;

export default function CheckoutPage() {
  const router = useRouter();
  const { user } = useAuthStore();
  const queryClient = useQueryClient();
  const [errorMsg, setErrorMsg] = useState("");

  const { data: cart, isLoading } = useQuery<Cart>({
    queryKey: ["cart", user?.id],
    queryFn: async () => {
      if (!user) return { id: 0, user_id: 0, items: [] };
      const res = await api.get("/cart/");
      return res.data;
    },
    enabled: !!user,
  });

  const { register, handleSubmit, formState: { errors } } = useForm<CheckoutFormInput, any, CheckoutForm>({
    resolver: zodResolver(checkoutSchema),
    defaultValues: { simulate_payment_failure: false }
  });

  const mutation = useMutation({
    mutationFn: async (data: CheckoutForm) => {
      if (!user) throw new Error("Must be logged in");
      const res = await api.post("/orders", data);
      return res.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["cart", user?.id] });
      router.push(`/orders/${data.id}`);
    },
    onError: (error: any) => {
      const msg = error.response?.data?.detail;
      setErrorMsg(msg || "Payment failed or out of stock.");
    },
  });

  const onSubmit = (data: CheckoutForm) => {
    setErrorMsg("");
    mutation.mutate(data);
  };

  if (!user) return null;

  if (isLoading || !cart) {
    return <div className="max-w-xl mx-auto mt-12 p-12 text-center text-muted-foreground animate-pulse border rounded-xl">Loading checkout...</div>;
  }

  const items = cart.items || [];
  if (items.length === 0) {
    return (
      <div className="max-w-xl mx-auto mt-12 text-center space-y-4 py-20 border rounded-xl bg-muted/20">
        <h2 className="text-2xl font-bold">Your cart is empty</h2>
        <Button onClick={() => router.push("/")}>Return to Shop</Button>
      </div>
    );
  }

  return (
    <div className="max-w-xl mx-auto mt-6">
      <Card>
        <CardHeader className="text-center pb-4 border-b">
          <CardTitle className="text-2xl flex items-center justify-center gap-2">
            <Lock className="w-5 h-5 text-muted-foreground" />
            Secure Checkout
          </CardTitle>
          <p className="text-sm text-muted-foreground">Order total will be processed immediately</p>
        </CardHeader>
        <CardContent className="pt-6">
          <form onSubmit={handleSubmit(onSubmit)} className="gap-6 flex flex-col">
            <div className="space-y-2">
              <label className="text-sm font-semibold">Shipping Address</label>
              <Input {...register("address")} placeholder="123 Main St, City, Country" className="h-11" />
              {errors.address && <p className="text-xs text-destructive">{errors.address.message}</p>}
            </div>
            
            <div className="border bg-amber-500/10 border-amber-500/20 p-4 rounded-md space-y-2 relative">
              <div className="flex items-start gap-2">
                <input 
                  type="checkbox" 
                  {...register("simulate_payment_failure")} 
                  id="simulate"
                  className="mt-1"
                />
                <label htmlFor="simulate" className="text-sm font-medium text-amber-800 dark:text-amber-400 cursor-pointer">
                  Simulate Payment Failure
                </label>
              </div>
              <p className="text-xs text-amber-700/80 dark:text-amber-500/80 pl-5">
                Check this box to intentionally cause the payment to fail (for MVP testing).
              </p>
            </div>

            {errorMsg && (
              <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-md text-sm text-destructive font-semibold">
                {errorMsg}
              </div>
            )}

            <Button type="submit" size="lg" className="w-full h-12 text-base mt-2" disabled={mutation.isPending}>
              {mutation.isPending ? "Processing Order..." : `Pay & Place Order (${items.length} items)`}
              {!mutation.isPending && <ArrowRight className="w-5 h-5 ml-2" />}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
