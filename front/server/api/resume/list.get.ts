import { defineEventHandler, createError } from "h3";
import { $fetch } from "ofetch";

export default defineEventHandler(async (event) => {
  const runtimeConfig = useRuntimeConfig();
  const BASE_HOST = runtimeConfig.BASE_HOST;
  const NUXT_HOST = runtimeConfig.NUXT_HOST;
  let k = {
    ...(event.context.cookies && { cookie: event.context.cookies }),
  };
  console.log(k, "k");

  try {
    const response = await $fetch.raw(
      `${BASE_HOST}/resume_storage/api/v001/users/resume/list`,
      {
        headers: k,
      }
    );

    return response._data;
  } catch (error: any) {
    const res = await $fetch.raw(`${NUXT_HOST}/api/user/auth/refresh`, {
      headers: k,
    });
    const newCookies = res.headers.getSetCookie();

    // 3. Логируем для проверки
    console.log("Получены куки:", newCookies);

    newCookies.forEach((cookie) => {
      appendHeader(event, "Set-Cookie", cookie);
    });
    const response = await fetch(
      `${BASE_HOST}/resume_storage/api/v001/users/resume/list`,
      {
        headers: {
          cookie: newCookies.join("; "),
        },
      }
    );
    console.log(response, "response");

    return response;

    throw createError({
      statusCode: error.response?.status || 500,
      statusMessage: `Backend Error: ${
        error.response?.statusText || error.message
      }`,
      data: error.data || { message: error.message },
    });
  }
});
