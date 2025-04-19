export const useAuth = () => {
  const isAuthenticated = ref(false);

  async function checkAuth() {
    try {
      const response = await $fetch("/api/user/auth/check", {
        credentials: "include",
      });
      if (response !== 204) throw new Error("Unauthorized");

      isAuthenticated.value = true;
    } catch (error) {
      isAuthenticated.value = false;
    }
  }

  async function register(login: string, password: string) {
    const response = await $fetch.raw("/api/user/auth/register", {
      method: "POST",
      body: {
        login,
        password,
      },
      credentials: "include",
    });

    return response;
  }

  async function login(login: string, password: string) {
    const response = await $fetch.raw("/api/user/auth/login", {
      method: "POST",
      body: {
        login,
        password,
      },
      credentials: "include",
    });

    return response;
  }

  async function logout() {
    const response = await $fetch.raw("/api/user/auth/logout", {
      method: "DELETE",
      credentials: "include",
    });

    return response;
  }

  return { register, login, isAuthenticated, checkAuth, logout };
};
