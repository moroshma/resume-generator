import { defineEventHandler, readBody, createError } from "h3";
import { $fetch } from "ofetch";

export default defineEventHandler(async (event) => {
  const runtimeConfig = useRuntimeConfig();
  const BASE_HOST = runtimeConfig.BASE_HOST;

  const body = await readRawBody(event, false);

  const clientHeaders = event.node.req.headers;

  try {
    const response = await $fetch.raw(
      `${BASE_HOST}/resume_storage/api/v001/users/resume`,
      {
        method: "POST",
        body: body,
        headers: {
          ...(event.context.cookies && { cookie: event.context.cookies }),
          "content-type": clientHeaders["content-type"],
        },
      }
    );

    return response._data;
  } catch (error: any) {
    console.error("Ошибка при запросе к бэкенду:", error.message);
    if (error.response) {
      console.error("Backend Status:", error.response.status);
      console.error("Backend Status Text:", error.response.statusText);
      console.error("Backend Response Data:", error.data);
    } else {
      console.error("Error details:", error);
    }

    throw createError({
      statusCode: error.response?.status || 500,
      statusMessage: `Backend Error: ${
        error.response?.statusText || error.message
      }`,
      data: error.data || { message: error.message },
    });
  }
});
