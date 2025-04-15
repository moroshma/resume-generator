export default defineEventHandler(async (event) => {
  const body = await readBody(event);
  const { BASE_HOST } = useRuntimeConfig();
  const response = await $fetch.raw(
    `${BASE_HOST}/user_service/api/v001/users/info`,
    {
      method: "PUT",
      headers: {
        ...(event.context.cookies && { cookie: event.context.cookies }),
      },
      body,
    }
  );

  return response._data;
});
