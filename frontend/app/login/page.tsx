"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import Link from "next/link";
import api from "@/lib/api";
import { getDefaultRouteForRole } from "@/lib/auth";
import { useAuthStore } from "@/lib/store";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import { useState } from "react";

const loginSchema = z.object({
  username: z.string().min(1, "Username is required"),
  password: z.string().min(1, "Password is required"),
});

type LoginForm = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const { setAuth } = useAuthStore();
  const [errorMsg, setErrorMsg] = useState("");

  const { register, handleSubmit, formState: { errors } } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  });

  const mutation = useMutation({
    mutationFn: async (data: LoginForm) => {
      const res = await api.post("/auth/login", data);
      return res.data;
    },
    onSuccess: (data) => {
      setAuth(data.user, data.access);
      router.push(getDefaultRouteForRole(data.user?.role));
    },
    onError: (error: any) => {
      setErrorMsg(error.response?.data?.detail || "Invalid credentials");
    },
  });

  const onSubmit = (data: LoginForm) => {
    setErrorMsg("");
    mutation.mutate(data);
  };

  return (
    <div className="flex-center mt-12">
      <Card className="w-[400px]">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">Login</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="gap-4 flex flex-col">
            <div className="space-y-1">
              <label className="text-sm font-medium">Username</label>
              <Input {...register("username")} placeholder="johndoe" />
              {errors.username && <p className="text-xs text-destructive">{errors.username.message}</p>}
            </div>
            
            <div className="space-y-1">
              <label className="text-sm font-medium">Password</label>
              <Input type="password" {...register("password")} placeholder="••••••••" />
              {errors.password && <p className="text-xs text-destructive">{errors.password.message}</p>}
            </div>

            {errorMsg && <p className="text-sm text-destructive font-medium">{errorMsg}</p>}

            <Button type="submit" className="w-full" disabled={mutation.isPending}>
              {mutation.isPending ? "Logging in..." : "Login"}
            </Button>
          </form>
        </CardContent>
        <CardFooter className="flex justify-center text-sm">
          <p className="text-muted-foreground">
            Don&apos;t have an account?{" "}
            <Link href="/register" className="text-primary hover:underline font-medium">
              Register here
            </Link>
          </p>
        </CardFooter>
      </Card>
    </div>
  );
}
