// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  components: [
    { path: "~/components/field", prefix: "" },
    { path: "~/components/", prefix: "" },
  ],

  css: ["~/assets/css/main.css"],

  compatibilityDate: "2024-11-01",
  devtools: { enabled: false },
  runtimeConfig: {
    BASE_HOST: process.env.BASE_HOST || "http://localhost:80",
    public: {},
  },
  app: {
    head: {
      title: "CV",
      htmlAttrs: {
        lang: "ru",
      },
      link: [{ rel: "icon", type: "image/x-icon", href: "/favicon.ico" }],
      charset: "utf-16",
      viewport: "width=device-width, initial-scale=1, maximum-scale=1",
    },
  },
  nitro: {
    routeRules: {
      "/api/**": {
        proxy: {
          to: "http://traefik:80/**",
        },
      },
    },
  },
});
