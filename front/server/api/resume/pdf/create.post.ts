import { defineEventHandler, readBody, createError } from "h3";
import { $fetch } from "ofetch";

export default defineEventHandler(async (event) => {
  const runtimeConfig = useRuntimeConfig();
  const BASE_HOST = runtimeConfig.BASE_HOST;

  const body = await readRawBody(event, false);

  const clientHeaders = event.node.req.headers;

  return createApiHandler({
    url: `/resume_storage/api/v001/users/resume`,
    event,
    options: {
      method: "POST",
      body,
      headers: {
        ...(event.context.cookies && { cookie: event.context.cookies }),
        "content-type": clientHeaders["content-type"],
      },
    },
  });
});
