export default defineEventHandler(async (event) => {
  const body = await readBody(event);
  const { BASE_HOST } = useRuntimeConfig();
  console.log("До");

  const response = await $fetch.raw(
    `${BASE_HOST}/user_service/api/v001/users/info`,
    {
      method: "DELETE",
      headers: {
        ...(event.context.cookies && { cookie: event.context.cookies }),
      },
      body,
    }
  );
  console.log(response._data);

  return response._data;
});
