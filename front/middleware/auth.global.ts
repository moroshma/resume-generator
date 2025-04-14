import { useAuth } from "~/composables/auth/useAuth";

export default defineNuxtRouteMiddleware(async (to) => {
  const routeMeta = to.meta;

  if (routeMeta.private && import.meta.client) {
    const { isAuthenticated, checkAuth } = useAuth();

    await checkAuth();

    if (!isAuthenticated.value) return navigateTo("/auth");
  }
});
