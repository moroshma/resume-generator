import { defineEventHandler, createError } from "h3";
import { $fetch } from "ofetch";
import { createApiHandler } from "~/server/utils/apiHandler";

export default defineEventHandler(async (event) => {
  return createApiHandler({
    url: "/resume_storage/api/v001/users/resume/list",
    event,
    options: {
      method: "GET",
    },
  });
});
