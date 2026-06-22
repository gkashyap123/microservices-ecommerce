import { useForm } from "react-hook-form";
import { Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import Input from "../../shared/components/Input";
import Button from "../../shared/components/Button";
import type { RegisterRequest } from "../../shared/types";

export default function RegisterPage() {
  const { register: registerUser, isRegistering } = useAuth();
  const { register, handleSubmit, formState: { errors } } =
    useForm<RegisterRequest>();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-sm
        border border-gray-200 p-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Create account</h1>

        <form onSubmit={handleSubmit((data) => registerUser(data))}
          className="flex flex-col gap-4">
          <Input
            label="Username"
            placeholder="gaurav"
            error={errors.username?.message}
            {...register("username", { required: "Username is required" })}
          />
          <Input
            label="Email"
            type="email"
            placeholder="you@example.com"
            error={errors.email?.message}
            {...register("email", { required: "Email is required" })}
          />
          <Input
            label="Password"
            type="password"
            placeholder="••••••••"
            error={errors.password?.message}
            {...register("password", {
              required: "Password is required",
              minLength: { value: 6, message: "Min 6 characters" },
            })}
          />
          <Button type="submit" isLoading={isRegistering} fullWidth>
            Create Account
          </Button>
        </form>

        <p className="text-sm text-center text-gray-500 mt-6">
          Already have an account?{" "}
          <Link to="/login" className="text-blue-600 hover:underline">
            Login
          </Link>
        </p>
      </div>
    </div>
  );
}