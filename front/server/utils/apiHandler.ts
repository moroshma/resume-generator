import { H3Event } from "h3";
import { $fetch, FetchOptions } from "ofetch";

export const createApiHandler = <T>(config: {
  url: string;
  options?: FetchOptions;
  event: H3Event;
  enableAutoRefresh?: boolean;
}) => {
  const { url, options, event, enableAutoRefresh = true } = config;
  const { BASE_HOST, NUXT_HOST } = useRuntimeConfig();

  const executeRequest = async (retry = false): Promise<T> => {
    try {
      const response = await $fetch.raw(url, {
        baseURL: BASE_HOST,
        ...options,
        headers: {
          ...options?.headers,
          cookie: retry
            ? event.context.newCookies?.join("; ")
            : event.context.cookies || "",
        },
      });

      if (!retry) {
        event.context.originalCookies = event.context.cookies;
      }

      return response._data as T;
    } catch (error: any) {
      if (error.response?.status === 401 && enableAutoRefresh) {
        try {
          const refreshResponse = await $fetch.raw(
            `${NUXT_HOST}/api/user/auth/refresh`,
            {
              headers: {
                cookie:
                  event.context.originalCookies || event.context.cookies || "",
              },
            }
          );

          event.context.newCookies = refreshResponse.headers.getSetCookie();

          event.context.newCookies?.forEach((cookie: any) => {
            if (!event.node.res.headersSent) {
              appendHeader(event, "Set-Cookie", cookie);
            }
          });

          return executeRequest(true);
        } catch (refreshError) {
          appendHeader(
            event,
            "Set-Cookie",
            "session=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT"
          );
          event.node.res.statusCode = 301;
          event.node.res.setHeader("Location", "/auth");
          event.node.res.end();
          return {} as T;
        }
      }

      throw createError({
        statusCode: error.response?.status || 500,
        message: error.message,
        data: error.data,
      });
    }
  };

  return executeRequest();
};
