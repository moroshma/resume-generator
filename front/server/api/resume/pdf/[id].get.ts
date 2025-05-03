export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, "id");

  return createApiHandler({
    url: `/resume_storage/api/v001/users/resume/${id}`,
    event,
    options: {
      method: "GET",
      headers: {
        ...(event.context.cookies && { cookie: event.context.cookies }),
      },
    },
  });
});
