import {
  createBrowserRouter,
  Link,
  Outlet,
  RouterProvider,
  useNavigate,
  useRouteError,
  isRouteErrorResponse,
} from "react-router";

import { useEffect } from "react";

import HomePage from "./index";
import Community from "./community.index";
import PostPage from "./community.$id";
import Contribute from "./contribute";
import LoginPage from "./auth.login";
import RegisterPage from "./auth.register";
import SearchPage from "./search";
import NewProduct from "./products.new";
import ProductPage from "./product.$id";
import ProfilePage from "./profile";

import { reportError } from "../lib/error-reporting";
import { AuthProvider } from "../lib/auth";
import { SiteLayout } from "../components/layout";

function NotFoundComponent() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="max-w-md text-center">
        <h1 className="text-7xl font-bold text-foreground">404</h1>
        <h2 className="mt-4 text-xl font-semibold text-foreground">
          Page not found
        </h2>
        <p className="mt-2 text-sm text-muted-foreground">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <div className="mt-6">
          <Link
            to="/"
            className="inline-flex rounded-full bg-primary px-4 py-2 text-sm font-medium text-primary-foreground"
          >
            Go home
          </Link>
        </div>
      </div>
    </div>
  );
}

function ErrorComponent() {
  const error = useRouteError();
  const navigate = useNavigate();

  useEffect(() => {
    console.error(error);

    reportError(error, {
      boundary: "react_router_root_error_boundary",
    });
  }, [error]);

  const errorMessage = isRouteErrorResponse(error)
    ? `${error.status} ${error.statusText}`
    : "An unexpected error occurred.";

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="max-w-md text-center">
        <h1 className="text-xl font-semibold text-foreground">
          This page didn't load
        </h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Something went wrong on our end. You can try refreshing or head back
          home.
        </p>
        {isRouteErrorResponse(error) && (
          <p className="mt-2 text-xs text-muted-foreground">
            {errorMessage}
          </p>
        )}
        <div className="mt-6 flex justify-center gap-2">
          <button
            onClick={() => navigate(0)}
            className="rounded-full bg-primary px-4 py-2 text-sm font-medium text-primary-foreground"
          >
            Try again
          </button>
          <Link
            to="/"
            className="rounded-full border px-4 py-2 text-sm font-medium"
          >
            Go home
          </Link>
        </div>
      </div>
    </div>
  );
}

function RootComponent() {
  return (
    <AuthProvider>
      <SiteLayout>
        <Outlet />
      </SiteLayout>
    </AuthProvider>
  );
}

export const router = createBrowserRouter([
  {
    path: "/",
    element: <RootComponent />,
    errorElement: <ErrorComponent />,
    children: [
      {
        index: true,
        element: <HomePage />,
      },
      {
        path: "auth/register",
        element: <RegisterPage />,
      },
      {
        path: "auth/login",
        element: <LoginPage />,
      },
      {
        path: "community",
        element: <Community />,
      },
      {
        path: "community/:id",
        element: <PostPage />,
      },
      {
        path: "products/new",
        element: <NewProduct />,
      },
      {
        path: "product/:id",
        element: <ProductPage />,
      },
      {
        path: "search",
        element: <SearchPage />,
      },
      {
        path: "contribute",
        element: <Contribute />,
      },
      {
        path: "profile",
        element: <ProfilePage />,
     },
      {
        path: "*",
        element: <NotFoundComponent />,
      },
    ],
  },
]);

export default function App() {
  return <RouterProvider router={router} />;
}