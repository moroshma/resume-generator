export default defineEventHandler(async (event) => {
  const { BASE_HOST } = useRuntimeConfig();
  const response = await $fetch.raw(
    `${BASE_HOST}/user_service/api/v001/users/info`,
    {
      headers: {
        ...(event.context.cookies && { cookie: event.context.cookies }),
      },
    }
  );

  return response._data;
});
