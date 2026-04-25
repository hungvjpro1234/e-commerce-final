"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import Link from "next/link";
import api from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import { useState } from "react";

const registerSchema = z.object({
  username: z.string().min(3, "Username must be at least 3 characters"),
  email: z.string().email("Invalid email address"),
  password: z.string().min(6, "Password must be at least 6 characters"),
  first_name: z.string().min(1, "First name is required"),
  last_name: z.string().min(1, "Last name is required"),
});

type RegisterForm = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const router = useRouter();
  const [errorMsg, setErrorMsg] = useState("");

  const { register, handleSubmit, formState: { errors } } = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
  });

  const mutation = useMutation({
    mutationFn: async (data: RegisterForm) => {
      const payload = { ...data, role: "customer" };
      const res = await api.post("/auth/register", payload);
      return res.data;
    },
    onSuccess: () => {
      router.push("/login?registered=true");
    },
    onError: (error: any) => {
      setErrorMsg(error.response?.data?.detail || "Failed to register. Username might exist.");
    },
  });

  const onSubmit = (data: RegisterForm) => {
    setErrorMsg("");
    mutation.mutate(data);
  };

  return (
    <div className="flex-center mt-12 mb-12">
      <Card className="w-[450px]">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">Create an Account</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="gap-4 flex flex-col">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="text-sm font-medium">First Name</label>
                <Input {...register("first_name")} />
                {errors.first_name && <p className="text-xs text-destructive">{errors.first_name.message}</p>}
              </div>
              <div className="space-y-1">
                <label className="text-sm font-medium">Last Name</label>
                <Input {...register("last_name")} />
                {errors.last_name && <p className="text-xs text-destructive">{errors.last_name.message}</p>}
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-sm font-medium">Username</label>
              <Input {...register("username")} />
              {errors.username && <p className="text-xs text-destructive">{errors.username.message}</p>}
            </div>

            <div className="space-y-1">
              <label className="text-sm font-medium">Email</label>
              <Input type="email" {...register("email")} />
              {errors.email && <p className="text-xs text-destructive">{errors.email.message}</p>}
            </div>
            
            <div className="space-y-1">
              <label className="text-sm font-medium">Password</label>
              <Input type="password" {...register("password")} placeholder="••••••••" />
              {errors.password && <p className="text-xs text-destructive">{errors.password.message}</p>}
            </div>

            {errorMsg && <p className="text-sm text-destructive font-medium">{errorMsg}</p>}

            <Button type="submit" className="w-full" disabled={mutation.isPending}>
              {mutation.isPending ? "Creating account..." : "Register"}
            </Button>
          </form>
        </CardContent>
        <CardFooter className="flex justify-center text-sm">
          <p className="text-muted-foreground">
            Already have an account?{" "}
            <Link href="/login" className="text-primary hover:underline font-medium">
              Log in
            </Link>
          </p>
        </CardFooter>
      </Card>
    </div>
  );
}
