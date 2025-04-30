export default defineEventHandler(async (event) => {
  const { BASE_HOST } = useRuntimeConfig();
  const body = await readBody(event);

  const response = await $fetch.raw(
    `${BASE_HOST}/resume_storage/api/v001/users/resume`,
    {
      method: "POST",
      body,
      headers: {
        ...(event.context.cookies && { cookie: event.context.cookies }),
      },
    }
  );

  return response._data;
});
